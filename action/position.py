# Import files
from config.secret import BITFLYER_KEY
import json
import time
import requests
import hmac
import hashlib

class Position:
    path = '/v1/me/getpositions?product_code=FX_BTC_JPY'
    method = 'GET'
    def get_position_info(self):
        results = None
        position_size = 0
        timestamp = str(time.time())
        text = timestamp + self.method + self.path
        sign = hmac.new(bytes(BITFLYER_KEY['api_secret'], 'ascii'), bytes(text, 'ascii'), hashlib.sha256).hexdigest()
        try:
            request_data = requests.get(
                'https://api.bitflyer.com' + self.path,
                headers = {
                    'ACCESS-KEY': BITFLYER_KEY['api_key'],
                    'ACCESS-TIMESTAMP': timestamp,
                    'ACCESS-SIGN': sign,
                    'Content-Type': 'application/json'
                },
            )
            acquired_data = request_data.json()
        except Exception as e:
            return 'Error mssage: {0}'.format(str(e))
        else:
            return acquired_data
