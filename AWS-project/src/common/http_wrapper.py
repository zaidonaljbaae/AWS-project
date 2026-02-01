#Libs
import requests

def get(url, headers={}, json=True):
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json() if json else r.text


def post(url, headers={}, data={}, json=True):
    r = requests.post(url, headers=headers, data=data)
    r.raise_for_status()
    return r.json() if json else r.text