import urllib
import os
import re
from datetime import datetime

import psycopg2
import scrapy

def get_meteo_db():
    pg_user = os.getenv("POSTGRES_USER")
    pg_host = 'database'
    pg_db = os.getenv("POSTGRES_DB")
    with open('/run/secrets/postgres-password', 'r') as fp:
        pg_password = fp.read().strip()
    dsn = f'postgres://{pg_user}:{urllib.parse.quote(pg_password)}@{pg_host}/{pg_db}'

    return psycopg2.connect(dsn)

class SmnSpider(scrapy.Spider):
    name = 'smn'
    allowed_domains = ['www.smn.gob.ar', 'ws1.smn.gob.ar']
    start_urls = ['http://www.smn.gob.ar/']

    def parse(self, response):
        js = response.css('.pane-smn-mapas-pimet-smn-mapas-pimet .pane-content script::text').get('')
        token = re.search(r"localStorage.setItem\('token', '(.+)'\);", js).group(1)
        yield scrapy.http.Request('https://ws1.smn.gob.ar/v1/weather/location/4864', headers={
            'Accept': 'application/json',
            'Authorization': 'JWT ' + token,
        }, callback=self.parse_weather)
        yield scrapy.http.Request('https://ws1.smn.gob.ar/v1/forecast/location/4864', headers={
            'Accept': 'application/json',
            'Authorization': 'JWT ' + token,
        }, callback=self.parse_forecast)

    def parse_weather(self, response):
        res = response.json()
        db = get_meteo_db()
        cur = db.cursor()
        now = datetime.now()
        cur.execute(f'''INSERT INTO weather (read_at, humidity, temperature, description) VALUES (%s, %s, %s, %s)''', [
            now,
            res['humidity'],
            res['temperature'],
            res['weather']['description'],
        ])
        db.commit()

    def parse_forecast(self, response):
        db = get_meteo_db()
        cur = db.cursor()
        now = datetime.now()
        for forecast in response.json()['forecast']:
            cur.execute(f'''INSERT INTO forecast_date (read_at, date, tempmin, tempmax, hummin, hummax) VALUES (%s, %s, %s, %s, %s ,%s)''', [
                now,
                forecast['date'],
                forecast['temp_min'],
                forecast['temp_max'],
                forecast['humidity_min'],
                forecast['humidity_max']
            ])
            for tod in ('early_morning', 'morning', 'afternoon', 'night'):
                if forecast.get(tod, None) is not None:
                    cur.execute(f'''INSERT INTO forecast_timeofday (read_at, date, tod, temperature, humidity, description) VALUES (%s, %s, %s, %s, %s ,%s)''', [
                        now,
                        forecast['date'],
                        tod,
                        forecast[tod]['temperature'],
                        forecast[tod]['humidity'],
                        forecast[tod]['weather']['description']
                    ])
        db.commit()
