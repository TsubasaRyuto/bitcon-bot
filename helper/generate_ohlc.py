"""
==========================================================================

    Packages

==========================================================================
"""
import json
import datetime
from time import sleep
import dateutil.parser

"""
==========================================================================

   Global variables

==========================================================================
"""
class GenerateOHLC:
    def __init__(self, period):
        self.ohlc = { 'open': '', 'high': '', 'low': '', 'close': '' }
        self.ohlc_list = []
        self.next_time = 0
        self.first_time = datetime.datetime.now()
        self.period = period

    def begin_generate(self, acquired_data, indicator_period):
        exec_date = self.__toDatetime(acquired_data['timestamp']) + datetime.timedelta(hours=9) # change to JTC
        price = float(acquired_data['ltp'])

        if (self.__get_date_seconds_excluded(self.first_time) == self.__get_date_seconds_excluded(exec_date)):
            return

        if not self.next_time:
            self.next_time = self.__get_date_seconds_excluded(self.first_time) + 60 + self.period
            self.__initialize_ohlc(price)
        elif self.__is_next_candlestick(exec_date):
            self.ohlc_list.insert(0, { 'open': self.ohlc['open'],
                                        'high': self.ohlc['high'],
                                        'low': self.ohlc['low'],
                                        'close': self.ohlc['close'] })
            if len(self.ohlc_list) == indicator_period + 1: self.ohlc_list.pop()
            self.__initialize_ohlc(price)
            self.next_time += self.period
        else:
            self.__update_ohlc(price)

    # Use to skip the bad timing
    def __get_date_seconds_excluded(self, datetime):
        base_date = datetime.replace(second=0, microsecond=0)
        return base_date.timestamp()

    # Use to judge next candlestick
    def __get_date_millseconds_eccluded(self, datetime):
        base_date = datetime.replace(microsecond=0)
        return base_date.timestamp()

    def __is_next_candlestick(self, exec_date):
        return self.next_time <= self.__get_date_millseconds_eccluded(exec_date)

    def __toDatetime(self, date):
        datetime = date.replace('T', ' ')[:-1]
        return dateutil.parser.parse(datetime)

    def __initialize_ohlc(self, price):
        self.ohlc['open'] = price
        self.ohlc['high'] = price
        self.ohlc['low'] = price
        self.ohlc['close'] = price

    def __update_ohlc(self, price):
        self.ohlc['high'] = max(self.ohlc['high'], price)
        self.ohlc['low'] = min(self.ohlc['low'], price)
        self.ohlc['close'] = price
