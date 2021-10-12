FROM cypress/included:8.6.0

COPY yarn.lock package.json /windguru-scraper/
RUN cd /windguru-scraper && yarn
COPY . /windguru-scraper/

ENTRYPOINT cd /windguru-scraper && ./run.sh
