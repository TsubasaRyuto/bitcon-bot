import json
import websocket
import datetime
from time import sleep
import numpy as np

# -------------------------------- Setting log ---------------------------------
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False
# ------------------------------------------------------------------------------

"""
==========================================================================

   Global valiables

==========================================================================
"""
SYMBOL_BTC_FX = 'FX_BTC_JPY'
WS_URL = 'wss://ws.lightstream.bitflyer.com/json-rpc'
CHANNEL_NAME = 'lightning_ticker_FX_BTC_JPY'
#OHLC_PERIOD = 10
#INDICATOR_PERIOD = 14
#BASIC_POSITION_SIZE = 0.05
#first_time
#now_rsi
#previous_rsi
#has_long_position = false
#has_short_position = false
#ohlcs_data = []
#ohlc = { open_time: '', timestamp: '', open: '', high: '', low: '', close: '' }

TICK_RES = 60 # OHLCV データの解像度(1分足 : 60, 5分足 : 300, 10分足 : 600, ...)
OHLCV_LEN = 5 # OHLCV データの保持数、指定数+1 を管理(0番目は最新データ(随時更新)、1番目以降が確定データ)
IDX_DATE = 0
IDX_OPEN = 1
IDX_HIGH = 2
IDX_LOW = 3
IDX_CLOSE = 4
IDX_VOLUME = 5
ITV_SLEEP_WSS_RECONNECT = 1

"""
==========================================================================

  functions

==========================================================================
"""

class RealtimeOHLCV(object):
    def __init__(self):
        self.ws = websocket.WebSocketApp(WS_URL, header=None, on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        websocket.enableTrace(True)

    def run(self):
        self.ws.run_forever()

    """
    Below are callback functions of websocket.
    """
    # when we get message
    def on_message(self, message):
        acquired_data = json.loads(message)['params']['message']
        logger.info(acquired_data);

    # when error occurs
    def on_error(self, error):
        logger.error(error)

    # when websocket closed.
    def on_close(self):
        logger.info('Disconnected websocket')

    # when websocket opened.
    def on_open(self):
        logger.info('Connected websocket')
        self.ws.send(json.dumps({ 'method': 'subscribe', 'params': { 'channel': CHANNEL_NAME } }))

if __name__ == '__main__':
    rtOHLCV = RealtimeOHLCV()
    rtOHLCV.run()

