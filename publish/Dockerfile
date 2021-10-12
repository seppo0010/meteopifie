FROM ubuntu:20.04

RUN apt-get update && apt-get -y install cron pipenv
COPY Pipfile* /publish/
RUN pip install pipenv && cd /publish && pipenv install --system --deploy --ignore-pipfile

COPY cron /etc/cron.d/publish
RUN chmod 0644 /etc/cron.d/publish
RUN crontab /etc/cron.d/publish
RUN touch /var/log/cron.log

COPY . /publish/
 
CMD ["cron", "-f"]
