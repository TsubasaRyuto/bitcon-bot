"""
==========================================================================

    Packages

==========================================================================
"""
import json
import datetime
from time import sleep
import numpy as np
import dateutil.parser

"""
==========================================================================

   Global variables

==========================================================================
"""
PERIOD = 5 # データの期間（10秒: 10, 1分: 60)

class ClosingPriceList:
    def __init__(self):
        self.closing_price_list = []
        self.next_time = 0
        self.first_time = datetime.datetime.now()

    def begin_generate(self, acquired_data):
        exec_date = self.__toDatetime(acquired_data['timestamp']) + datetime.timedelta(hours=9) # change to JTC
        if (self.__get_date_seconds_excluded(self.first_time) == self.__get_date_seconds_excluded(exec_date)):
            return

        if not self.next_time:
            self.next_time = self.__get_date_seconds_excluded(self.first_time) + 60 + PERIOD
        elif self.__is_next_candlestick(exec_date):
            self.closing_price_list.insert(0, int(acquired_data['ltp']))
            if len(self.closing_price_list) == 16: self.closing_price_list.pop()
            self.next_time += PERIOD

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
