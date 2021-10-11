#!/bin/bash
set -Eeux

cd /scrapy
scrapy runspider -L WARNING meteo/spiders/smn.py
