#!/bin/bash
set -Eeux

echo "[DEFAULT]
batch_mode = on
database = postgresql://${POSTGRES_USER}:$(cat /run/secrets/postgres-password)@database/${POSTGRES_DB}
sources = /windguru-server/migrations" > /tmp/config
yoyo apply --config /tmp/config

while true; do
    /windguru-server/run-once.sh
done
