#!/usr/bin/env python

"""Tests for `sentimentbot` package."""

import pytest

from click.testing import CliRunner

from sentimentbot.feeds import FinvizNewsFeed, MotleyFoolNewsFeed
from sentimentbot.analyzer import SentimentAnalyzer


@pytest.fixture
def finviznewsfeed():
    """
    Test-fixture for NewsFeed
    """
    feed = FinvizNewsFeed("SHOP")
    return feed


@pytest.fixture
def sentimentanalyzer():
    """
    Test-fixture for NewsFeed
    """
    analyzer = SentimentAnalyzer("SHOP")
    return analyzer


@pytest.fixture
def motleyfoolfeed():
    return MotleyFoolNewsFeed(
        "https://www.fool.com/investing/2020/08/25/bigcommerce-introduces-instagram-checkout-tiptoein/"
    )


class TestFinvizNewsFeed(object):
    """ unittests for the FinvizNewsFeed """

    def test_creation(self):
        """ tests the constructor """
        feed = FinvizNewsFeed("SHOP")
        assert feed.ticker == "SHOP"
        assert feed._uri == "https://finviz.com/quote.ashx?t=SHOP"

    def test_get_html(self, finviznewsfeed):
        """ test to get HTLM """
        response = finviznewsfeed._get_html()
        assert len(response) > 0

    def test_parser(self, finviznewsfeed):
        """ testing to parse the data """
        news = finviznewsfeed.read()
        print("\n")
        print(news.head(5))


class TestMotleyFool(object):
    """ unittest for motley fool """

    def test_creation(self, motleyfoolfeed):
        """ testing constructor """
        text = motleyfoolfeed.read()
        print(text)


class TestSentimentAnalyzer(object):
    """ collects all the Source-tests in one place """

    def test_sentiment_analyzer(self, sentimentanalyzer):
        """ testing the sentiment analyzer """
        scores = sentimentanalyzer.analyze()
        print("\n")
        print(scores.head())
        print(scores.describe())
