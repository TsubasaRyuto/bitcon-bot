# Import files
from config.secret import BITFLYER_KEY
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

class Position:
    path = '/v1/me/getpositions?product_code=FX_BTC_JPY'
    method = 'GET'
    def get_position_info(self):
        timestamp = str(time.time())
        text = timestamp + self.method + self.path
        sign = hmac.new(bytes(BITFLYER_KEY['api_secret'], 'ascii'), bytes(text, 'ascii'), hashlib.sha256).hexdigest()
        for _ in range(3):
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
                logger.error('Error mssage: {0}'.format(str(e)))
            else:
                break
        else:
            return None
        return acquired_data
