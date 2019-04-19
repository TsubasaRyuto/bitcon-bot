"""
==========================================================================

    Classes

==========================================================================
"""
from helper.generate_ohlc import GenerateOHLC
from helper.logic import Logic
from action.order import Order
from action.position import Position
from indicator.cci import CCI
generate_ohlc = GenerateOHLC()
logic = Logic()
order = Order()
position = Position()
cci = CCI()

"""
==========================================================================

    Packages

==========================================================================
"""
import json
import websocket
import datetime
import time
from time import sleep
import numpy as np
import threading
import signal

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

   Global variables

==========================================================================
"""
SYMBOL_BTC_FX = 'FX_BTC_JPY'
WS_URL = 'wss://ws.lightstream.bitflyer.com/json-rpc'
CHANNEL_NAME = 'lightning_ticker_FX_BTC_JPY'
CCI_PERIOD = 50
BASE_POSITION_SIZE = 0.1
active_positions = 0
now_cci = None
previous_cci = None
has_long_position = False
has_short_position = False

"""
==========================================================================

  functions

==========================================================================
"""
# 引数はシグナル番号、および現在のスタックフレーム
def exec_trading(signal_id, frame):
    global active_positions, previous_cci, now_cci, has_short_position, has_long_position
    ohlc_list = generate_ohlc.ohlc_list
    if len(ohlc_list) == CCI_PERIOD:
        logger.info('---------- Trading decide---------')
        previous_cci = now_cci
        now_cci = cci.cci_calculater(ohlc_list, CCI_PERIOD)
        logger.info('Previous CCI: {0}  |  Now CCI: {1}'.format(str(previous_cci), str(now_cci)))
        price = ohlc_list[0]['close']
        if logic.is_buy_signal(now_cci, previous_cci):
            if has_short_position:
                # Exit
                logger.info('Exit short position. ActivePosition: {0} Price: {1}'.format(str(active_positions), price))
                order.market_order('BUY', active_positions)
                has_short_position = False
            # Entry
            logger.info('Long entry: Lot: {0}  Price: {1}'.format(str(BASE_POSITION_SIZE), price))
            order.limit_order('BUY', BASE_POSITION_SIZE, price)
            has_long_position = True
        elif logic.is_sell_signal(now_cci, previous_cci):
            if has_long_position:
                # Exit
                logger.info('Exit Long position. ActivePosition: {0} Price: {1}'.format(str(active_positions), price))
                #order.market_order('SELL', active_positions)
                has_long_position = False
            # Entry
            logger.info('Short entry. Lot: {0}, Price: {1}'.format(str(BASE_POSITION_SIZE), price))
            order.limit_order('SELL', BASE_POSITION_SIZE, price)
            has_short_position = True
        else:
            logger.info('Nothing trading')

        time.sleep(8)

        active_positions = 0
        position_list = position.get_position_info()
        if position_list:
            position_size_list = [float(position.get('size')) for position in position_list]
            active_positions = round(sum(position_size_list), 3)
        else:
            active_positions = 0
            has_long_position = 0
            has_short_position = 0
        order.cancel_orders()

def start_program():
    while len(generate_ohlc.ohlc_list) != CCI_PERIOD:
        logger.info('OHLCデータ収集中........')
        time.sleep(1)
    signal.signal(signal.SIGALRM, exec_trading)
    signal.setitimer(signal.ITIMER_REAL, 1, 10)

def run_websocket():
    ws.keep_running = True
    ws.run_forever()

"""
Below are callback functions of websocket.
"""
# when get message
def on_message(self, message):
    acquired_data = json.loads(message)
    generate_ohlc.begin_generate(acquired_data['params']['message'], CCI_PERIOD)

# when error occurs
def on_error(self, error):
    logger.error(error)

# when websocket closed.
def on_close(self):
    logger.info('Disconnected websocket')

# when websocket opened.
def on_open(self):
    logger.info('Connected websocket')
    ws.send(json.dumps({ 'method': 'subscribe', 'params': { 'channel': CHANNEL_NAME } }))


if __name__ == '__main__':
    logger.info('---------- Welcome to HFT bot ----------')
    logger.info('BOT TYPE : HFT @ bitFlyer')
    logger.info('LOT      : ' + str(BASE_POSITION_SIZE))
    logger.info('========================================')

    ws = websocket.WebSocketApp(WS_URL, on_open = on_open, on_message = on_message, on_error = on_error, on_close = on_close)
    t1 = threading.Thread(target = run_websocket)

    t1.start()
    start_program()
