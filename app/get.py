from typing import Union

try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request


def _urlopen(obj):
    try:
        resp = urlopen(obj)
    except HTTPError as e:
        return "App not found"

    return resp.read().decode("UTF-8")


def post(url, data, headers):
    # type: (str, Union[str, bytes], dict) -> str

    return _urlopen(Request(url, data=data, headers=headers))


def get(url):
    # type: (str) -> str

    return _urlopen(url)