import twstock
import os
import datetime
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY, date2num

MyColumns = ['date', 'open', 'high', 'close', 'low', 'volume', 'ma5', 'ma10', 'ma20', 'mv5', 'mv10', 'mv20']
#Mycolumns = ['date', 'open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change', 'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20', 'turnover']

class MyStock:
    def __init__(self, twstock_id, start):
        self.stock = twstock.Stock(twstock_id)
        self.stock.fetch_from(start.year, start.month - 3)
        self.ID = twstock_id
        self.Name = twstock.codes[twstock_id].name
        self.RawData = None
        self.DataFrame = None
        self.PNGFilename = '['+ datetime.date.today().strftime("%Y.%m.%d") + '][' + twstock_id + '] Result.png'
        self.Result = None

    def InitialData(self):
        # ma
        ma5 = self.stock.moving_average(self.stock.price, 5)
        ma10 = self.stock.moving_average(self.stock.price, 10)
        ma20 = self.stock.moving_average(self.stock.price, 20)

        # mv
        mv5 = self.stock.moving_average(self.stock.capacity, 5)
        mv10 = self.stock.moving_average(self.stock.capacity, 10)
        mv20 = self.stock.moving_average(self.stock.capacity, 20)

        for item in self.stock.data:
            tmp = []

            # date
            tmp.append(item[0])

            # open
            tmp.append(item[3])

            # high
            tmp.append(item[4])

            # close
            tmp.append(item[6])

            # low
            tmp.append(item[5])

            # volume
            tmp.append(item[1])

            # price_change
            # p_change

            # ma5
            index = self.stock.data.index(item)
            if index >= 4: tmp.append(ma5[index - 4])
            else: tmp.append(None)

            # ma10
            if index >= 9: tmp.append(ma10[index - 9])
            else: tmp.append(None)

            # ma20
            if index >= 19: tmp.append(ma20[index - 19])
            else: tmp.append(None)

            # mv5
            if index >= 4: tmp.append(mv5[index - 4])
            else: tmp.append(None)

            # mv10
            if index >= 9: tmp.append(mv10[index - 9])
            else: tmp.append(None)

            # mv20
            if index >= 19: tmp.append(mv20[index - 19])
            else: tmp.append(None)

            # turnover

            if self.RawData is None: self.RawData = [tmp]
            else: self.RawData.append(tmp)

        self.DataFrame = pd.DataFrame(self.RawData, columns = MyColumns)
        return

    def PandasCandlestickOHLC(self, MAList = None, MVList = None):
        mondays = WeekdayLocator(MONDAY)
        alldays = DayLocator()
        weekFormatter = DateFormatter('%Y %b %d')

        fig, (axOHLC, axTV) = plt.subplots(2, 1, sharex = True)
        fig.subplots_adjust(bottom = 0.2)
        plt.ticklabel_format(style='plain')

        # OHLC
        axOHLC.set_title(self.ID + '\nOHLC')
        axOHLC.xaxis.set_major_locator(mondays)
        axOHLC.xaxis.set_minor_locator(alldays)
        axOHLC.xaxis.set_major_formatter(weekFormatter)
        axOHLC.grid(True)

        # Create Candlestick
        stock_array = np.array(self.DataFrame.reset_index()[['date', 'open', 'high', 'low', 'close']])
        stock_array[:,0] = date2num(stock_array[:,0])
        candlestick_ohlc(axOHLC, stock_array, colorup = "red", colordown = "green", width = 0.4)

        # OHLC line chart
        if MAList is not None:
            for each in MAList:
                axOHLC.plot(self.DataFrame['date'], self.DataFrame[each], label=each)

        # Trading Volume
        axTV.set_title('Trading Volume')
        axTV.grid(True)
        axTV.bar(stock_array[:,0], self.DataFrame['volume'], align='center', color="red")

        # Trading Volume line chart
        if MVList is not None:
            for each in MVList:
                axTV.plot(self.DataFrame['date'], self.DataFrame[each], label=each)

        axTV.xaxis_date()
        axTV.autoscale_view()

        plt.setp(plt.gca().get_xticklabels(), rotation = 45, horizontalalignment = 'right')
        plt.savefig(self.PNGFilename)

    def BestFourPoint(self):
        bfp = twstock.BestFourPoint(self.stock)
        self.Result = [bfp.best_four_point_to_buy()]
        self.Result.append(bfp.best_four_point_to_sell())
        self.Result.append(bfp.best_four_point())
        
    def DailyResult(self, FilePath):
        file = open(FilePath, 'w+')
        file.write("#!/bin/bash\n")
        file.write("STOCK_ID=" + self.ID + "\n")
        file.write("STOCK_NAME=" + self.Name + "\n")
        file.write("STOCK_BFPB=" + str(self.Result[0]) + "\n")
        file.write("STOCK_BFPS=" + str(self.Result[1]) + "\n")
        file.write("STOCK_BFP=" + str(self.Result[2]) + "\n")
        file.close()
