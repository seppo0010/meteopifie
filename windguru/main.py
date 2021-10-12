import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

def get_meteo_db():
    pg_user = os.getenv("POSTGRES_USER")
    pg_host = 'database'
    pg_db = os.getenv("POSTGRES_DB")
    with open('/run/secrets/postgres-password', 'r') as fp:
        pg_password = fp.read().strip()
    dsn = f'postgres://{pg_user}:{urllib.parse.quote(pg_password)}@{pg_host}/{pg_db}'

    return psycopg2.connect(dsn)

class MyServer(BaseHTTPRequestHandler):
    def do_POST(self):
        db = get_meteo_db()
        cur = db.cursor()
        now = datetime.now()
        content_length = self.headers['content-length']
        length = int(content_length) if content_length else 0
        r = self.rfile.read(length)
        req = json.loads(r)
        for dt, value in req.items():
            cur.execute(f'''INSERT INTO forecast_wg (read_at, forecast_date, temperature) VALUES (%s, %s)''', [
                now,
                dt,
                value,
            ])

        db.commit()
        self.send_response(200)
        self.end_headers()
        sys.exit(0)

if __name__ == "__main__":
    webServer = HTTPServer(('0.0.0.0', 8000), MyServer)

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
