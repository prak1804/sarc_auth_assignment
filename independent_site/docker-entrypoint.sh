#!/bin/sh
set -e

python - <<'PY'
import os
import time
import psycopg2

host = os.environ.get("INDIE_DB_HOST", "localhost")
port = int(os.environ.get("INDIE_DB_PORT", "5432"))
dbname = os.environ.get("INDIE_DB_NAME", "postgres")
user = os.environ.get("INDIE_DB_USER", "postgres")
password = os.environ.get("INDIE_DB_PASSWORD", "postgres")

for _ in range(30):
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
        )
        conn.close()
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("Indie DB not ready after 30s")
PY

python manage.py migrate
python manage.py runserver 0.0.0.0:8001
