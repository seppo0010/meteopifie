#!/bin/bash
set -Eeux

cd /meteo
scrapy runspider -L WARNING meteo/spiders/smn.py
