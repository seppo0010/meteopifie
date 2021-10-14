from datetime import datetime, timedelta
import json
import io
import os
from datetime import datetime
import logging
import urllib
import pytz

import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from telethon import TelegramClient

TZ = 'America/Buenos_Aires'
RAINSCALE = [
    ([
     'Despejado',
     ],
     'Despejado'
    ),
    ([
     'Algo nublado',
     'Parcialmente nublado',
     'Ligeramente nublado',
     ],
     'Parcialmente nublado'
    ),
    ([
     'Nublado',
     ],
     'Nublado'
    ),
    (
     [
     'Mayormente nublado',
     'Cubierto',
     'Neblina',
     'Cubierto con neblina',
     'Mayormente nublado con neblina',
     'Niebla',
     'Nublado con neblina',
     ],
     'Mayormente nublado'
    ),
    ([
     'Lluvias aisladas',
     'Cubierto con llovizna en la hora anterior',
     'Cubierto con llovizna',
     'Lloviznas',
     'Chaparrones',
     'Nublado con lluvia débil',
    ],
     'Lluvias aisladas'
    ),
    ([
     'Lluvias',
     'Nublado con lluvia en la hora anterior',
     ],
     'Lluvias'
    ),
    ([
     'Tormentas aisladas',
    ],
     'Tormentas aisladas'
    ),
]



def get_module_logger(mod_name):
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel({
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'DEBUG': logging.DEBUG,
    }[os.getenv('LOG_LEVEL', 'WARNING')])
    return logger
logger = get_module_logger(__name__)

def get_db_conn():
    pg_user = os.getenv("POSTGRES_USER")
    pg_host = 'database'
    pg_db = os.getenv("POSTGRES_DB")
    with open('/run/secrets/postgres-password', 'r') as fp:
        pg_password = fp.read().strip()
    dsn = f'postgres://{pg_user}:{urllib.parse.quote(pg_password)}@{pg_host}/{pg_db}'
    return psycopg2.connect(dsn)

def get_telegram_client():
    with open('/run/secrets/telegram-api-token', 'r') as fp:
        api_token = fp.read().strip()
    with open('/run/secrets/telegram-bot-token', 'r') as fp:
        bot_token = fp.read().strip()
    api_id, api_hash = api_token.split(':')
    return TelegramClient(
        'bot',
        api_id=int(api_id),
        api_hash=api_hash,
    ).start(bot_token=bot_token)

def get_last_period():
    now = datetime.now()
    h = ((now.hour - 2) // 6) * 6 + 2
    if h < 0:
        d = datetime(now.year, now.month, now.day, h + 24, 0, 0) - timedelta(days=1)
    else:
        d = datetime(now.year, now.month, now.day, h, 0, 0)
    d.replace(tzinfo=pytz.timezone(TZ))
    return d

def get_weather(d, pg_connection):
    return pd.read_sql('''
    SELECT * FROM weather WHERE read_at BETWEEN %s AND %s ORDER BY read_at DESC
    ''', pg_connection, params=[d - timedelta(hours=6), d])

def get_forecasts(d, pg_connection):
    forecasts = pd.read_sql('''
    SELECT * FROM forecast_timeofday WHERE date = %s AND tod = %s ORDER BY read_at DESC
    ''', pg_connection, params=[(d - timedelta(hours=6)).date(), {
        2: 'night',
        8: 'early_morning',
        14: 'morning',
        20: 'afternoon',
    }[d.hour]])
    forecasts.loc[:, 'read_at'] = pd.to_datetime(forecasts['read_at'])
    return forecasts

def get_predictions(d, forecasts):
    predictions = pd.DataFrame()
    for time in range(0, 14):
        t = (d - timedelta(hours=12 * time))
        closest = forecasts.loc[(forecasts['read_at'] - t).apply(lambda x: abs(x)).idxmin()]
        if abs(closest['read_at'] - t) < timedelta(hours=12):
            predictions = predictions.append(closest)
    return predictions

def get_rain(x):
    try:
        return [i for i, arr in enumerate(RAINSCALE) if x in arr[0]][0]
    except:
        logger.warning('unknown rain value: ' + x)
        return -1

def draw_chart(d, weather, predictions):
    plt.figure(figsize=(12, 10))
    plt.suptitle('Pronosticos para el ' + d.strftime('%d/%m') + ' por ' + {
        2: 'la noche',
        8: 'la mañana temprana',
        14: 'la mañana',
        20: 'la tarde',
    }[d.hour])
    ax = plt.subplot(2,1,1)
    ax.plot(predictions['read_at'], predictions['temperature'], color='red', linestyle='dashed')
    ax.legend([Line2D([0], [0], color='red', linestyle='dashed'), Line2D([0], [0])],
          ['Estimado', 'Real'],
          loc='upper center',
          bbox_to_anchor=(0.5, 1.2))

    xlim = ax.get_xlim()
    ax.hlines(weather['temperature'].min(), xlim[0], xlim[1])
    ax.hlines(weather['temperature'].max(), xlim[0], xlim[1])
    ax.set_xticks([predictions['read_at'].min(), predictions['read_at'].max()])

    ax.set_ylim(0, 30)

    ax = plt.subplot(2,1,2)
    ax.plot(predictions['read_at'], predictions['rain'], color='red', linestyle='dashed')
    xlim = ax.get_xlim()
    ax.hlines(weather['rain'].max(), *xlim)
    ax.hlines(weather['rain'].min(), *xlim)
    ax.set_xticks([predictions['read_at'].min(), predictions['read_at'].max()])
    ax.set_yticks(range(0, len(RAINSCALE)))
    ax.set_yticklabels([arr[1] for arr in (RAINSCALE)])

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

async def do_publish(telegram_client, chart):
    await telegram_client.get_entity(os.getenv('TELEGRAM_CHANNEL')) # idk why this is necessary
    await telegram_client.send_file(os.getenv('TELEGRAM_CHANNEL'), chart)

async def main(telegram_client):
    db = get_db_conn()
    d = get_last_period()
    weather = get_weather(d, db)
    forecasts = get_forecasts(d, db)
    predictions = get_predictions(d, forecasts)
    predictions.loc[:, 'rain'] = predictions['description'].apply(get_rain)
    weather.loc[:, 'rain'] = weather['description'].apply(get_rain)
    chart = draw_chart(d, weather, predictions)
    await do_publish(telegram_client, chart)

if __name__ == '__main__':
    telegram_client = get_telegram_client()
    with telegram_client:
        telegram_client.loop.run_until_complete(main(telegram_client))
