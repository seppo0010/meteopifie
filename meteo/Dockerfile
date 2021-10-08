FROM ubuntu:20.04

RUN apt-get update && apt-get install -y pipenv && rm -rf /var/lib/apt/lists/*
COPY Pipfile* /meteo/
RUN pip install pipenv && cd /meteo && pipenv install --system --deploy --ignore-pipfile
COPY . /meteo
CMD cd /meteo && ./run.sh
