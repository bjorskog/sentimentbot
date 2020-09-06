import abc
import requests
import collections

import pandas as pd

from bs4 import BeautifulSoup


__all__ = ["FinvizNewsFeed"]


News = collections.namedtuple(
    "News", ["ticker", "date", "source", "time", "message_text", "link"]
)


class AbstractParser(abc.ABC):
    @abc.abstractmethod
    def parse(self, *args, **kwargs):
        pass

    def _get_soup(self, response):
        return BeautifulSoup(response, "html.parser")


class FinvizNewsParser(AbstractParser):
    """ handling all parsing of the feed """

    _id = "news-table"
    _news = []

    def __init__(self, ticker):
        self._ticker = ticker

    def parse(self, response):
        html = self._get_soup(response)
        news = html.find(id=self._id)
        rows = news.findAll("tr")
        for row in rows:
            self._parse_row(row)
        return self._news

    def _parse_row(self, row):

        text = row.a.get_text()
        link = row.a.get("href")
        tag_list = row.td.text.split()
        source = row.find("div", "news-link-right").text.strip()

        last_date = None

        if len(tag_list) > 1:
            date = last_date = tag_list[0]
            time = tag_list[1]
        else:
            time = tag_list[0]
            date = last_date

        self._news.append(News(self._ticker, date, source, time, text, link))


class AbstractNewsFeed(abc.ABC):

    _headers = {"user-agent": "my-app/0.0.1"}

    def __init__(self, uri):
        self._uri = uri

    @abc.abstractmethod
    def read(self):
        pass

    def _get_html(self):
        response = requests.get(self.uri, headers=self._headers)
        return response.content

    @property
    def uri(self):
        return self._uri


class FinvizNewsFeed(AbstractNewsFeed):
    """ Finviz news feed """

    _uri_template = "https://finviz.com/quote.ashx?t={ticker}"

    @property
    def ticker(self):
        return self._ticker

    def __init__(self, ticker):
        self._ticker = ticker
        self._uri = self._uri_template.format(ticker=ticker)
        super().__init__(self._uri)
        self._parser = FinvizNewsParser(ticker)

    def read(self):
        columns = ["date_time", "ticker", "source", "message_text", "link"]

        content = self._get_html()
        news = self._parser.parse(content)
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
            .pipe(lambda df: df[columns])
        )
        return data


class MotleyFoolParser(AbstractParser):
    """ parser for motley fool """

    def parse(self, response):
        soup = self._get_soup(response)
        paragraphs = soup.find("span", attrs={"class": "article-content"}).find_all("p")

        text_strings = []

        for p in paragraphs:
            text_strings.append(p.text)

        text = " ".join(text_strings)
        return text


class MotleyFoolNewsFeed(AbstractNewsFeed):
    """ motley-fool stock banter """

    def __init__(self, uri):
        super().__init__(uri)
        self._parser = MotleyFoolParser()

    def read(self):
        content = self._get_html()
        text = self._parser.parse(content)
        return text
