import sys
import logging
import datetime
from stock import MyStock

# logger config
logger = logging.getLogger('MASTER')
ch = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s][%(filename)s][%(levelname)s][%(lineno)d]: %(message)s', '%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print('Number of Parameters is incorrect.')
        exit()
    mStock = MyStock(str(sys.argv[1]), datetime.date.today())
    mStock.InitialData()
    mStock.PandasCandlestickOHLC(MAList = ['ma5', 'ma10', 'ma20'], MVList = ['mv5', 'mv10', 'mv20'])
    mStock.BestFourPoint()
    mStock.DailyResult(sys.argv[2])
