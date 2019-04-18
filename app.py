"""
==========================================================================

    Classes

==========================================================================
"""
from helper.closing_price_list import ClosingPriceList
from helper.logic import Logic
from action.order import Order
from action.position import Position
from indicator.rsi import RSI
closing_price_list = ClosingPriceList()
logic = Logic()
order = Order()
position = Position()
rsi = RSI()

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

   Global valiables

==========================================================================
"""
SYMBOL_BTC_FX = 'FX_BTC_JPY'
WS_URL = 'wss://ws.lightstream.bitflyer.com/json-rpc'
CHANNEL_NAME = 'lightning_ticker_FX_BTC_JPY'
RSI_PERIOD = 14
BASE_POSITION_SIZE = 0.1
active_positions = 0
now_rsi = None
previous_rsi = None
has_long_position = False
has_short_position = False

"""
==========================================================================

  functions

==========================================================================
"""
# 引数はシグナル番号、および現在のスタックフレーム
def exec_trading(signal_id, frame):
    global active_positions, previous_rsi, now_rsi, has_short_position, has_long_position
    cpl = closing_price_list.closing_price_list
    if len(cpl) == 15:
        logger.info('---------- Trading decide---------')
        previous_rsi = now_rsi
        now_rsi = rsi.rsi_calculater(cpl, RSI_PERIOD)
        logger.info('Previous RSI: {0}  |  Now RSI: {1}'.format(str(previous_rsi), str(now_rsi)))
        price = cpl[0]
        if logic.is_buy_signal(now_rsi, previous_rsi):
            if has_short_position:
                # Exit
                logger.info('Exit short position. ActivePosition: {0} Price: {1}'.format(str(active_positions), price))
                order.market_order('BUY', active_positions)
                has_short_position = False
            # Entry
            logger.info('Long entry: Lot: {0}  Price: {1}'.format(str(BASE_POSITION_SIZE), price))
            order.limit_order('BUY', BASE_POSITION_SIZE, price)
            has_long_position = True
        elif logic.is_sell_signal(now_rsi, previous_rsi):
            if has_long_position:
                # Exit
                logger.info('Exit Long position. ActivePosition: {0} Price: {1}'.format(str(active_positions), price))
                order.market_order('SELL', active_positions)
                has_long_position = False
            # Entry
            logger.info('Short entry. Lot: {0}, Price: {1}'.format(str(BASE_POSITION_SIZE), price))
            order.limit_order('SELL', BASE_POSITION_SIZE, price)
            has_short_position = True
        else:
            logger.info('Nothing trading')

        time.sleep(3)

        active_positions = 0
        position_list = position.get_position_info()
        if position_list:
            position_size_list = [float(position.get('size')) for position in position_list]
            active_positions = sum(position_size_list)
        else:
            active_positions = 0
            has_long_position = 0
            has_short_position = 0
        order.cancel_orders()

def start_program():
    while len(closing_price_list.closing_price_list) != 15:
        logger.info('OHLCデータ収集中........')
        time.sleep(1)
    signal.signal(signal.SIGALRM, exec_trading)
    signal.setitimer(signal.ITIMER_REAL, 1, 5)

def run_websocket():
    ws.keep_running = True
    ws.run_forever()

"""
Below are callback functions of websocket.
"""
# when get message
def on_message(self, message):
    acquired_data = json.loads(message)
    closing_price_list.begin_generate(acquired_data = acquired_data['params']['message'])

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
