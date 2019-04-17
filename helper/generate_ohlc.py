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

   Global valiables

==========================================================================
"""
OHLC_PERIOD = 10 # OHLCデータの期間（10秒: 10, 1分: 60)

class GenerateOHLC:
    def __init__(self):
        self.ohlc = { 'open_time': '', 'timestamp': '', 'open': '', 'high': '', 'low': '', 'close': '' }
        self.ohlcs_data = []
        self.first_time = datetime.datetime.now()

    def begin_generate(self, acquired_data):
        exec_date = self.__toDatetime(acquired_data['timestamp']) + datetime.timedelta(hours=9) # change to JTC
        contract_data = {
            'exec_date': exec_date,
            'price': acquired_data['ltp']
        }
        if (self.__get_date_seconds_excluded(self.first_time) == self.__get_date_seconds_excluded(exec_date)):
            return
        if (self.ohlc['timestamp'] == ''):
            self.__initialize_ohlc(contract_data)
        elif (self.__is_next_candlestick(exec_date)):
            self.ohlcs_data.insert(0, { 'open_time': self.ohlc['open_time'],
                                        'timestamp': self.ohlc['timestamp'],
                                        'open': self.ohlc['open'],
                                        'high': self.ohlc['high'],
                                        'low': self.ohlc['low'],
                                        'close': self.ohlc['close'] })
            if len(self.ohlcs_data) == 16: self.ohlcs_data.pop()
            self.__initialize_ohlc(contract_data)
        else:
            self.__update_ohlc(contract_data)

    # Use to skip the bad timing
    def __get_date_seconds_excluded(self, datetime):
        base_date = datetime.replace(second=0, microsecond=0)
        return base_date.timestamp()

    # Use to judge next candlestick
    def __get_date_millseconds_eccluded(self, datetime):
        base_date = datetime.replace(microsecond=0)
        return base_date.timestamp()

    def __is_next_candlestick(self, exec_date):
        return self.__get_date_millseconds_eccluded(exec_date) - self.__get_date_millseconds_eccluded(self.ohlc['open_time']) == OHLC_PERIOD

    def __initialize_ohlc(self, contract_data):
        price = float(contract_data['price'])
        exec_date = contract_data['exec_date']
        self.ohlc['open_time'] = exec_date
        self.ohlc['timestamp'] = exec_date
        self.ohlc['open'] = price
        self.ohlc['high'] = price
        self.ohlc['low'] = price
        self.ohlc['close'] = price

    def __update_ohlc(self, contract_data):
        price = float(contract_data['price'])
        exec_date = contract_data['exec_date']
        self.ohlc['timestamp'] = exec_date
        self.ohlc['high'] = max(self.ohlc['high'], price)
        self.ohlc['low'] = min(self.ohlc['low'], price)
        self.ohlc['close'] = price

    def __toDatetime(self, date):
        datetime = date.replace('T', ' ')[:-1]
        return dateutil.parser.parse(datetime)
