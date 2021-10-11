#!/bin/bash
set -Eeux

echo "[DEFAULT]
batch_mode = on
database = postgresql://${POSTGRES_USER}:$(cat /run/secrets/postgres-password)@database/${POSTGRES_DB}
sources = /scrapy/migrations" > /tmp/config
yoyo apply --config /tmp/config

while true; do
    /scrapy/run-once.sh
    sleep 3600
done
