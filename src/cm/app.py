from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.types import SubscribeOptions, RegisterOptions
import time
from crochet import run_in_reactor


@inlineCallbacks
def ticker():
    while True:
        yield sleep(2)
        print("tick!!")


class AppSession(ApplicationSession):
    def __init__(self, config=None):
        ApplicationSession.__init__(self, config)
        print("component created", config)
        self.profiles = {}
        ticker()

    def onLeave(self, details):
        print("session left", details)

    def onDisconnect(self):
        print("transport disconnected")

    @inlineCallbacks
    def onJoin(self, details):
        print("joined", details)

        yield self.register(self.add, 'xchat.test.add', options=RegisterOptions(details_arg='details'))
        yield self.register(self.mul, 'xchat.test.mul', options=RegisterOptions(details_arg='details'))

        yield self.register(self.online, 'xchat.user.online', options=RegisterOptions(details_arg='details'))

    @inlineCallbacks
    def add(self, x, y, details=None):
        caller = details.caller
        authid = details.caller_authid
        profile = self.profiles.setdefault(caller, {})
        profile.setdefault('add', 0)
        profile['add'] += 1

        print(details)
        print("{authid}<{caller}> #{count} called add() with {x} and {y}.".format(count=profile['add'], caller=caller, authid=authid, x=x, y=y))
        if profile.get('is_online'):
            yield self.publish('xchat.user.{}.msg'.format(caller), x + y)
        returnValue(x + y)

    @run_in_reactor
    def sleep(self, n):
        time.sleep(n)

    @inlineCallbacks
    def mul(self, x, y, details=None):
        caller = details.caller
        profile = self.profiles.setdefault(caller, {})
        profile.setdefault('mul', 0)
        profile['mul'] += 1

        yield self.sleep(20)
        yield sleep(5)
        returnValue(x * y)

    @inlineCallbacks
    def online(self, details=None):
        caller = details.caller
        profile = self.profiles.setdefault(caller, {})
        if profile.setdefault('offline', None) is None:
            registration = yield self.register(self.offline, 'xchat.user.{}.offline'.format(caller), options=RegisterOptions(details_arg='details'))
            profile['offline'] = registration
            profile['is_online'] = True

        returnValue({'ok': True})

    def offline(self, details=None):
        caller = details.caller
        profile = self.profiles.setdefault(caller, {})
        offline = profile.get('offline')
        if offline is not None:
            del profile['offline']
            offline.unregister()
            del profile['is_online']
        return {'ok': True}

    def send_msg(self, chat_id, msg, details=None):
        caller = details.caller
        user = details.caller_authid
        pass

    def create_chat(self, details=None):
        """
        创建单聊
        """
        user = details.caller_authid
        pass

    def create_group_chat(self, details=None):
        """
        创建群聊
        """
        user = details.caller_authid
