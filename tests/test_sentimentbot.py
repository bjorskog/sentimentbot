#!/usr/bin/env python

"""Tests for `sentimentbot` package."""

import pytest

from click.testing import CliRunner

from sentimentbot import sentimentbot


@pytest.fixture
def newsfeed():
    """
    Test-fixture for NewsFeed
    """
    feed = sentimentbot.NewsFeed("SHOP")
    return feed


@pytest.fixture
def sentimentanalyzer():
    """
    Test-fixture for NewsFeed
    """
    analyzer = sentimentbot.SentimentAnalyzer("SHOP")
    return analyzer


class TestSource(object):
    """ collects all the Source-tests in one place """

    def test_creation(self):
        """ tests the constructor """
        feed = sentimentbot.NewsFeed("SHOP")
        assert feed.ticker == "SHOP"
        assert feed._uri == "https://finviz.com/quote.ashx?t=SHOP"

    def test_get_html(self, newsfeed):
        """ test to get HTLM """
        response = newsfeed._get_html()
        assert len(response) > 0

    def test_parser(self, newsfeed):
        """ testing to parse the data """
        news = newsfeed.read_news()
        print("\n")
        print(news.head(5))

    def test_sentiment_analyzer(self, sentimentanalyzer):
        """ testing the sentiment analyzer """
        scores = sentimentanalyzer.analyze()
        print("\n")
        print(scores.head())
        print(scores.describe())
