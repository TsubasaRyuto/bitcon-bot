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

class Collateral:
    path = '/v1/me/getcollateral'
    method = 'GET'
    def get_collateral_info(self):
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
            logger.error('Error mssage: {0}'.format(str(e)))
        else:
            return acquired_data
