"""Main module."""


from nltk.sentiment.vader import SentimentIntensityAnalyzer

import pandas as pd

from sentimentbot.feeds import FinvizNewsFeed


class SentimentAnalyzer(object):
    """ wrapper for the sentiment analyzer """

    _analyzer = SentimentIntensityAnalyzer()

    def __init__(self, ticker):
        self._ticker = ticker
        self._newsfeed = FinvizNewsFeed(ticker)
        self._data = self._newsfeed.read()

    def _analyze_rows(self, data):
        sentiment = data["message_text"].apply(self._analyzer.polarity_scores)
        return pd.DataFrame(sentiment.tolist())

    def analyze(self):
        sentiment_data = self._data.pipe(self._analyze_rows).rename(
            columns={"neg": "negative", "neu": "neutral", "pos": "positive"}
        )
        assert (
            sentiment_data.shape[0] == self._data.shape[0]
        ), "Mismatch in rows after analyzing."

        data = self._data.join(sentiment_data)
        return data
