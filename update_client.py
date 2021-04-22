import time

import requests

while True:
    try:
        response = requests.get('http://localhost:8000/update', timeout=10)
        print('server response code: {}'.format(response.status_code))
    except Exception as E:
        print('no response from server...')
    time.sleep(3)
