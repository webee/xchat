import threading
import time
from utils import pmc_config
from collections import namedtuple
import jwt
import logging
from .client import RestClient, is_success_result
from .config import XIMClientConfig
# from .sync import RWLock

logger = logging.getLogger(__name__)


class ClientInstance(object):
    def __init__(self):
        self.client = None

    def set_client(self, client):
        self.client = client


__clientInstance = ClientInstance()


def get_client():
    return __clientInstance.client


def init(xim_app, xim_password, env_config):
    __clientInstance.set_client(XIMClient(xim_app, xim_password, env_config))


Member = namedtuple('Member', ['user', 'can_pub', 'can_sub'])


class XIMClient(RestClient):
    def __init__(self, xim_app, xim_password, env_config=None):
        self._lock = threading.Lock()
        # self._rwlock = RWLock()
        self.config = XIMClientConfig()
        if config is not None:
            pmc_config.merge_config(self.config, env_config)
        super(XIMClient, self).__init__(self.config.HOST_URL)

        self.xim_app = xim_app
        self.xim_password = xim_password
        self._token = None
        self._token_exp = 0

    def __is_current_token_invalid(self):
        t = time.time()
        # with self._rwlock.rlock:
        return self._token is None or t > self._token_exp

    @property
    def token(self):
        if self.__is_current_token_invalid():
            with self._lock:
                if self.__is_current_token_invalid():
                    self._token = self.new_token()
                    try:
                        payload = jwt.decode(self._token, verify=False)
                        self._token_exp = payload['exp']
                    except Exception as e:
                        logger.error(e)
                        self._token = None
        return self._token

    def new_token(self):
        """
        Returns: app access token.
        """
        result = self.post(self.config.APP_NEW_TOKEN_URL,
                           {'username': self.xim_app, 'password': self.xim_password},
                           without_auth=True)
        if is_success_result(result):
            return result.data['token']

    def new_user_token(self, user, expire_seconds=None):
        """
        Args:
            user: 用户名
            expire_seconds: 过期时间

        Returns: user access token.

        """
        data = {
            'user': user
        }
        if expire_seconds is not None:
            data['expire'] = expire_seconds

        result = self.post(self.config.APP_NEW_USER_TOKEN_URL, data)
        if is_success_result(result):
            return result.data['token']

    def create_channel(self, members=None, tag=None):
        members = members or None
        json = {'members': [{'user': m.user, 'can_pub': m.can_pub, 'can_sub': m.can_sub} for m in members]}
        if tag is not None:
            json['tag'] = tag
        result = self.post(self.config.APP_CREATE_CHANNEL_URL, json=json)
        if is_success_result(result):
            return result.data['channel']
