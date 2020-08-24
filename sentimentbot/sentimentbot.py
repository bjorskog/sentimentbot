"""Main module."""


import requests
import pendulum
import collections

import pandas as pd

from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer


__all__ = ["NewsFeed"]


_URI_TEMPLATE = "https://finviz.com/quote.ashx?t={ticker}"


News = collections.namedtuple("News", ["ticker", "date", "time", "message_text"])


class FeedParser(object):
    """ handling all parsing of the feed """

    _id = "news-table"
    _news = []

    def __init__(self, ticker):
        self._ticker = ticker

    def parse_html(self, response):
        html = BeautifulSoup(response)
        news = html.find(id=self._id)
        rows = news.findAll("tr")
        for row in rows:
            self._parse_row(row)
        return self._news

    def _parse_row(self, row):

        text = row.a.get_text()
        tag_list = row.td.text.split()

        last_date = None

        if len(tag_list) > 1:
            date = last_date = tag_list[0]
            time = tag_list[1]
        else:
            time = tag_list[0]
            date = last_date

        self._news.append(News(self._ticker, date, time, text))


class NewsFeed(object):
    """ News-source """

    _headers = {"user-agent": "my-app/0.0.1"}

    def __init__(self, ticker):
        self._ticker = ticker
        self._uri = _URI_TEMPLATE.format(ticker=ticker)
        self._parser = FeedParser(ticker)

    @property
    def ticker(self):
        return self._ticker

    @property
    def uri(self):
        return self._uri

    def read_news(self):
        content = self._get_html()
        news = self._parser.parse_html(content)
        data = (
            pd.DataFrame(data=news)
            .assign(date=lambda df: df["date"].fillna(method="pad"))
            .assign(date_time=lambda df: df["date"] + " " + df["time"])
            .assign(
                date_time=lambda df: pd.to_datetime(
                    df["date_time"], format="%b-%d-%y %H:%M%p"
                )
            )
            .assign(date=lambda df: pd.to_datetime(df["date"], format="%b-%d-%y"))
            .drop(columns=["date", "time"])
        )
        return data

    def _get_html(self):
        response = requests.get(self._uri, headers=self._headers)
        return response.content


class SentimentAnalyzer(object):
    """ wrapper for the sentiment analyzer """

    _analyzer = SentimentIntensityAnalyzer()

    def __init__(self, ticker):
        self._ticker = ticker
        self._newsfeed = NewsFeed(ticker)
        self._data = self._newsfeed.read_news()

    def _analyze_rows(self, data):
        sentiment = data["message_text"].apply(self._analyzer.polarity_scores)
        return pd.DataFrame(sentiment.tolist())

    def analyze(self):
        sentiment_data = self._data.pipe(self._analyze_rows).rename(
            columns={"neg": "negative", "neu": "neutral", "pos": "positive"}
        )
        assert (
            sentiment_data.shape[0] == self._data.shape[0]
        ), "Mismatch after analyzing."

        data = self._data.join(sentiment_data)
        return data
