FROM python:3.11
WORKDIR /
COPY . .
RUN pip3 install -r requirements.txt
#CMD [ "scrapy", "crawl", "telegram", "-a", "channels_file=channels.json", "-a", "fetch_times=crawler/fetch_times.json", "-a", "hours=24"]
ENTRYPOINT /crawl.sh
