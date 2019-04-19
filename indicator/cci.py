import numpy as np
class CCI:
    def cci_calculater(self, ohlcs, period):
        sma = self.__sma_calculater(ohlcs, period)
        constant = 0.015
        previous_high_price = ohlcs[0]['high']
        previous_low_price = ohlcs[0]['low']
        previous_close_price = ohlcs[0]['close']
        # Last Typical Price
        ltp = round(self.__tp_calculater(previous_high_price, previous_low_price, previous_close_price))
        # Mean Deviation
        md_molecule_list = [abs(self.__tp_calculater(ohlc['high'], ohlc['low'], ohlc['close']) - sma) for ohlc in ohlcs]
        sum = np.sum(np.array(md_molecule_list))
        md = sum / period
        return int((ltp - sma) / (constant * md))

    def __sma_calculater(self, ohlcs, period):
        tp_list = [self.__tp_calculater(ohlc['high'], ohlc['low'], ohlc['close']) for ohlc in ohlcs]
        sum = np.sum(np.array(tp_list))
        return round(sum / period);

    def __tp_calculater(self, high, low, close):
        return (high + low + close) / 3

