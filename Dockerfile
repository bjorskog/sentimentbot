
FROM python:3.7-slim

MAINTAINER Bjørn Skogtrø

COPY . /opt/sentimentbot
WORKDIR /opt/sentimentbot

RUN pip install /opt/sentimentbot

EXPOSE 8080
ENTRYPOINT [ "sentimentbot" ]
