"""
==========================================================================

    Classes

==========================================================================
"""
from helper.generate_ohlc import GenerateOHLC
from helper.logic import Logic
from action.order import Order
from action.position import Position
from action.collateral import Collateral
from indicator.cci import CCI

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
import requests
from decimal import *
import sys

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
PERIOD = 60
LEVERAGE = 15
active_positions = 0
base_position_size = 0
provisional_positions = 0
now_cci = None
previous_cci = None
has_long_position = False
has_short_position = False
# class instance
generate_ohlc = GenerateOHLC(PERIOD)
logic = Logic()
order = Order()
position = Position()
collateral = Collateral()
cci = CCI()

"""
==========================================================================

  functions

==========================================================================
"""
# 引数はシグナル番号、および現在のスタックフレーム
def exec_trading(signal_id, frame):
    global active_positions, previous_cci, now_cci, has_short_position, has_long_position, provisional_positions
    ohlc_list = generate_ohlc.ohlc_list
    if len(ohlc_list) == CCI_PERIOD:
        logger.info('---------- Trading decide---------')
        previous_cci = now_cci
        now_cci = cci.cci_calculater(ohlc_list, CCI_PERIOD)
        logger.info('Previous CCI: {0}  |  Now CCI: {1}'.format(str(previous_cci), str(now_cci)))
        price = ohlc_list[0]['close']
        if logic.is_buy_signal(now_cci, previous_cci):
            if active_positions > base_position_size * 6 and has_long_position:
                # Force exit
                logger.info('Forc exit Long position. ActivePosition: {0} Price: {1}'.format(str(active_positions), price))
                order.market_order('SELL', active_positions)
                has_long_position = False
                provisional_positions = 0
            else:
                if has_short_position:
                    # Exit
                    logger.info('Exit short position. Active positions: {0} Price: {1}'.format(str(active_positions), price))
                    order.market_order('BUY', active_positions)
                    has_short_position = False
                    provisional_positions = 0
                # Entry
                logger.info('Long entry: Lot: {0}  Price: {1}'.format(str(base_position_size), price))
                order.limit_order('BUY', base_position_size, price)
                has_long_position = True
                provisional_positions += base_position_size
        elif logic.is_sell_signal(now_cci, previous_cci):
            if active_positions > base_position_size * 6 and has_short_position:
                # Force exit
                logger.info('Forc exit short position. Active positions: {0} Price: {1}'.format(str(active_positions), price))
                order.market_order('BUY', active_positions)
                has_short_position = False
                provisional_positions = 0
            else:
                if has_long_position:
                    # Exit
                    logger.info('Exit Long position. ActivePosition: {0} Price: {1}'.format(str(active_positions), price))
                    order.market_order('SELL', active_positions)
                    has_long_position = False
                    provisional_positions = 0
                # Entry
                logger.info('Short entry. Lot: {0}, Price: {1}'.format(str(base_position_size), price))
                order.limit_order('SELL', base_position_size, price)
                has_short_position = True
                provisional_positions += base_position_size
        else:
            logger.info('Nothing trading')

        time.sleep(30)

        active_positions = 0
        position_list = position.get_position_info()
        if position_list is not None and position_list:
            position_size_list = [Decimal(str(position.get('size'))) for position in position_list]
            active_positions = sum(position_size_list)
        else:
            active_positions = 0
            provisional_position_size = 0
            has_long_position = 0
            has_short_position = 0
        order.cancel_orders()

def start_program():
    while len(generate_ohlc.ohlc_list) != CCI_PERIOD:
        logger.info('OHLCデータ収集中........')
        time.sleep(1)
    signal.signal(signal.SIGALRM, exec_trading)
    signal.setitimer(signal.ITIMER_REAL, 1, PERIOD)

def run_websocket(ws):
    while True:
        try:
            ws.keep_running = True
            ws.run_forever()
        except Exception as e:
            logger.error(e)
        time.sleep(1)

def get_current_price():
    path = '/v1/ticker?product_code=FX_BTC_JPY'
    url = 'https://api.bitflyer.com' + path
    for _ in range(3):
        try:
            request_data = requests.get(url)
        except Exception as e:
            logger.error(e)
        else:
            break
    else:
        logger.error('Failed to get current price')
        sys.exit(1)
    return request_data.json()['ltp']

def calculate_base_position_size(current_price):
    collateral_info = collateral.get_collateral_info()
    calc_result = ((collateral_info['collateral'] * LEVERAGE) / current_price) / 11
    return round(calc_result, 2)

"""
Below are callback functions of websocket.
"""
# when get message
def on_message(ws, message):
    acquired_data = json.loads(message)
    generate_ohlc.begin_generate(acquired_data['params']['message'], CCI_PERIOD)

# when error occurs
def on_error(ws, error):
    logger.error(error)

# when websocket closed.
def on_close(ws):
    logger.info('Disconnected websocket')

# when websocket opened.
def on_open(ws):
    logger.info('Connected websocket')
    ws.send(json.dumps({ 'method': 'subscribe', 'params': { 'channel': CHANNEL_NAME } }))


if __name__ == '__main__':
    current_price = get_current_price()
    base_position_size = calculate_base_position_size(current_price)
    base_position_size = Decimal(str(base_position_size))
    logger.info('---------- Welcome to HFT bot ----------')
    logger.info('BOT TYPE : HFT @ bitFlyer')
    logger.info('LOT      : ' + str(base_position_size))
    logger.info('========================================')

    ws = websocket.WebSocketApp(WS_URL, on_message = on_message, on_error = on_error, on_close = on_close)
    ws.on_open = on_open
    t1 = threading.Thread(target=run_websocket, args=(ws,))

    t1.start()
    start_program()
    #except KeyboardInterrupt:
    #    active_positions = 0
    #    position_list = position.get_position_info()
    #    if position_list:
    #        position_size_list = [Decimal(str(position.get('size'))) for position in position_list]
    #        active_positions = sum(position_size_list)
    #        position_side = position_list[0]['side']
    #        if position_list == 'BUY':
    #            order.market_order('SELL', active_positions)
    #        else:
    #            order.market_order('BUY', active_positions)
    #        logger.info('---------- Settlement all position ----------')
    #    logger.info('---------- Stop HFT bot ----------')

