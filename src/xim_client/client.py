from collections import namedtuple
import requests
import logging

logger = logging.getLogger(__name__)


Result = namedtuple('Result', ['status_code', 'data'])


def is_success_result(result):
    return result is not None and 200 <= result.status_code < 300


class RestClient(object):
    def __init__(self, host_url):
        self._host_url = host_url

    def set_host_url(self, host_url):
        self._host_url = host_url

    def get_token(self):
        if hasattr(self, 'token'):
            return self.token

    def request(self, method, url, data=None, json=None, *, params=None, headers=None, without_auth=False, **kwargs):
        params = params or {}
        data = data or {}
        json = json or {}
        headers = headers or {}
        if not without_auth and self.get_token() is not None:
            headers['Authorization'] = 'Bearer ' + self.get_token()
        logger.debug("request: %s %s, %s, %s, %s", method, url, data, json, params)
        req = requests.request(method, self._host_url + url, data=data, json=json, params=params, headers=headers)
        try:
            status_code, data = req.status_code, req.json()
            logger.debug("response: %s %s, %s, %s", method, url, status_code, data)
            return Result(req.status_code, data)
        except Exception as e:
            logger.error(e)

    def get(self, url, params=None, **kwargs):
        return self.request('GET', url, params=params, **kwargs)

    def post(self, url, data=None, json=None, *, params=None, **kwargs):
        return self.request('POST', url, data=data, json=json, params=params, **kwargs)

    def put(self, url, data=None, json=None, *, params=None, **kwargs):
        return self.request('PUT', url, data=data, json=json, params=params, **kwargs)

    def delete(self, url, data=None, json=None, *, params=None, **kwargs):
        return self.request('DELETE', url, data=data, json=json, params=params)

