import threading
import time
from utils import pmc_config
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
        通过app和password得到访问token.
        Returns: app access token.
        """
        result = self.post(self.config.APP_NEW_TOKEN_URL,
                           {'username': self.xim_app, 'password': self.xim_password},
                           without_auth=True)
        if is_success_result(result):
            return result.data['token']

    def new_user_token(self, user, expire_seconds=None):
        """
        获取用户访问token.
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

    def create_channel(self, publishers=None, subscribers=None, tag=None):
        """
        创建包含成员members和tag的channel.
        Args:
            publishers: 发布者列表[user1, user2,...]
            subscribers: 订阅者列表[user1, user2,...]
            tag: tag

        Returns:
        """
        json = {}
        if publishers is not None:
            json['pubs'] = publishers
        if subscribers is not None:
            json['subs'] = subscribers
        if tag is not None:
            json['tag'] = tag
        result = self.post(self.config.APP_CREATE_CHANNEL_URL, json=json)
        if is_success_result(result):
            return result.data['channel']

    def close_channel(self, channel):
        url = self.config.APP_CHANNEL_URL.format(channel=channel)
        result = self.delete(url)
        if is_success_result(result):
            return result.data

    def open_channel(self, channel):
        url = self.config.APP_CHANNEL_URL.format(channel=channel)
        result = self.put(url)
        if is_success_result(result):
            return result.data

    def get_channel(self, channel):
        """
        获取channel信息
        Args:
            channel: channel id
        Returns:
        """
        url = self.config.APP_CHANNEL_URL.format(channel=channel)
        result = self.get(url)
        if is_success_result(result):
            return result.data

    def add_channel_pub_subs(self, channel, publishers=None, subscribers=None):
        """
        增加channel发布者和订阅者
        Args:
            channel:
            publishers:
            subscribers:

        Returns:

        """
        json = {}
        if publishers is not None:
            json['pubs'] = publishers
        if subscribers is not None:
            json['subs'] = subscribers
        url = self.config.APP_CHANNEL_PUBSUBS_URL.format(channel=channel)
        result = self.post(url, json=json)
        if is_success_result(result):
            return result.data

    def remove_channel_pub_subs(self, channel, publishers=None, subscribers=None):
        """
        删除channel发布者和订阅者
        Args:
            channel:
            publishers:
            subscribers:

        Returns:

        """
        json = {}
        if publishers is not None:
            json['pubs'] = publishers
        if subscribers is not None:
            json['subs'] = subscribers
        url = self.config.APP_CHANNEL_PUBSUBS_URL.format(channel=channel)
        result = self.delete(url, json=json)
        if is_success_result(result):
            return result.data

    def add_channel_publishers(self, channel, users):
        """
        向channel中增加发布者
        Args:
            channel: channel id
            users: [user1, user2,...]
        Returns:
        """
        url = self.config.APP_CHANNEL_PUBLISHERS_URL.format(channel=channel)
        json = {'pubs': users}

        result = self.post(url, json=json)
        if is_success_result(result):
            return result.data

    def remove_channel_publishers(self, channel, users):
        """
        从channel中删除发布者.
        Args:
            channel: channel id
            users: [user1, user2,...]

        Returns:
        """
        url = self.config.APP_CHANNEL_PUBLISHERS_URL.format(channel=channel)
        json = {'pubs': users}

        result = self.delete(url, json=json)
        if is_success_result(result):
            return result.data

    def add_channel_subscribers(self, channel, users):
        """
        向channel中增加订阅者
        Args:
            channel: channel id
            users: [user1, user2,...]
        Returns:
        """
        url = self.config.APP_CHANNEL_SUBSCRIBERS_URL.format(channel=channel)
        json = {'subs': users}

        result = self.post(url, json=json)
        if is_success_result(result):
            return result.data

    def remove_channel_subscribers(self, channel, users):
        """
        从channel中删除订阅者.
        Args:
            channel: channel id
            users: [user1, user2,...]

        Returns:
        """
        url = self.config.APP_CHANNEL_SUBSCRIBERS_URL.format(channel=channel)
        json = {'subs': users}

        result = self.delete(url, json=json)
        if is_success_result(result):
            return result.data

    def get_channel_pubsubs(self, channel):
        """
        获取channel发布者和订阅者列表
        Args:
            channel: channel id
        Returns:
        """
        url = self.config.APP_CHANNEL_PUBSUBS_URL.format(channel=channel)

        result = self.get(url)
        if is_success_result(result):
            return result.data

    def get_channel_publishers(self, channel):
        """
        获取channel发布者列表
        Args:
            channel: channel id
        Returns:
        """
        url = self.config.APP_CHANNEL_PUBLISHERS_URL.format(channel=channel)

        result = self.get(url)
        if is_success_result(result):
            return result.data

    def get_channel_subscribers(self, channel):
        """
        获取channel订阅者列表
        Args:
            channel: channel id
        Returns:
        """
        url = self.config.APP_CHANNEL_PUBLISHERS_URL.format(channel=channel)

        result = self.get(url)
        if is_success_result(result):
            return result.data
