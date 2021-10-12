#!/bin/bash
set -Eeux

while true; do
  /windguru-scraper/run-once.sh
  sleep 3600
done
