""" 

Adding entry-point for collecting the feed by
batch, implemented using luigi.

"""


import luigi
import pathlib
import datetime

from sentimentbot.feeds import FinvizNewsFeed

_OUTPATH = pathlib.Path().home().joinpath("data")


class ReadFinviz(luigi.ExternalTask):
    """ reads data from the interweb """

    ticker = luigi.Parameter()
    date_time = luigi.DateHourParameter(default=datetime.datetime.now())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._feed = FinvizNewsFeed(self.ticker)
        self._out_file = _OUTPATH.joinpath(
            f"finviz_news_{self.ticker.lower()}_{self.date_time}.csv"
        )

    def run(self):
        data = self._feed.read()
        with self.output().open("w") as out:
            data.to_csv(out, index=False)

    def output(self):
        return luigi.LocalTarget(self._out_file)

