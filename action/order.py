# Import files
from config.secret import BITFLYER_KEY

# Packages
import json
import time
import requests
import hmac
import hashlib

# -------------------------------- Setting log ---------------------------------
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False
# ------------------------------------------------------------------------------

class Order:
    product_code = 'FX_BTC_JPY'
    base_url = 'https://api.bitflyer.jp'
    method = 'POST'

    def market_order(self, order_side, size):
        path = '/v1/me/sendchildorder'
        params = {
            'product_code': self.product_code,
            'child_order_type': 'MARKET',
            'side': order_side,
            'size': float(size),
        };
        body = json.dumps(params)
        timestamp = str(time.time())
        text = timestamp + self.method + path + body
        sign = hmac.new(bytes(BITFLYER_KEY['api_secret'], 'ascii'), bytes(text, 'ascii'), hashlib.sha256).hexdigest()
        try:
            request_data = requests.post(
                self.base_url + path,
                data = body,
                headers = {
                    'ACCESS-KEY': BITFLYER_KEY['api_key'],
                    'ACCESS-TIMESTAMP': timestamp,
                    'ACCESS-SIGN': sign,
                    'Content-Type': 'application/json'
                }
            )
            acquired_data = request_data.json()
        except Exception as e:
            logger.error('Error mssage: {0}'.format(str(e)))
        else:
            return acquired_data

    def limit_order(self, order_side, size, price):
        path = '/v1/me/sendchildorder'
        params = {
            'product_code': self.product_code,
            "child_order_type": "LIMIT",
            'side': order_side,
            "price": int(price),
            'size': float(size),
        }
        body = json.dumps(params)
        timestamp = str(time.time())
        text = timestamp + self.method + path + body
        sign = hmac.new(bytes(BITFLYER_KEY['api_secret'], 'ascii'), bytes(text, 'ascii'), hashlib.sha256).hexdigest()
        try:
            request_data = requests.post(
                self.base_url + path,
                data = body,
                headers = {
                    'ACCESS-KEY': BITFLYER_KEY['api_key'],
                    'ACCESS-TIMESTAMP': timestamp,
                    'ACCESS-SIGN': sign,
                    'Content-Type': 'application/json'
                }
            )
            acquired_data = request_data.json()
        except Exception as e:
            logger.error('Error mssage: {0}'.format(str(e)))
        else:
            return acquired_data

    def cancel_orders(self):
        path = '/v1/me/cancelallchildorders'
        params = {
            'product_code': self.product_code,
        }
        body = json.dumps(params)
        timestamp = str(time.time())
        text = timestamp + self.method + path + body
        sign = hmac.new(bytes(BITFLYER_KEY['api_secret'], 'ascii'), bytes(text, 'ascii'), hashlib.sha256).hexdigest()
        try:
            request_data = requests.post(
                self.base_url + path,
                data = body,
                headers = {
                    'ACCESS-KEY': BITFLYER_KEY['api_key'],
                    'ACCESS-TIMESTAMP': timestamp,
                    'ACCESS-SIGN': sign,
                    'Content-Type': 'application/json'
                }
            )
        except Exception as e:
            logger.error('Error mssage: {0}'.format(str(e)))
        else:
            return request_data
