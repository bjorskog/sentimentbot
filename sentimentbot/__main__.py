""" 
Entry-point for the sentiment-reader.

"""

import luigi


from sentimentbot.tasks import ReadFinviz


def main():
    task = ReadFinviz(ticker="SHOP")
    luigi.build([task], local_scheduler=True, workers=1)


if __name__ == "__main__":
    main()
