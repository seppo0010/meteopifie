FROM ubuntu:20.04

RUN apt-get update && apt-get install -y pipenv && rm -rf /var/lib/apt/lists/*
COPY Pipfile* /windguru-server/
RUN pip install pipenv && cd /windguru-server && pipenv install --system --deploy --ignore-pipfile
COPY . /windguru-server
CMD cd /windguru-server && ./run.sh
