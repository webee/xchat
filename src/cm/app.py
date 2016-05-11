from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.types import SubscribeOptions, RegisterOptions
import time


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

    @inlineCallbacks
    def onLeave(self, details):
        print("session left", details)

    @inlineCallbacks
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
        yield
        returnValue(x + y)

    @inlineCallbacks
    def mul(self, x, y, details=None):
        caller = details.caller
        profile = self.profiles.setdefault(caller, {})
        profile.setdefault('mul', 0)
        profile['mul'] += 1

        yield sleep(10)
        returnValue(x * y)

    @inlineCallbacks
    def online(self, details=None):
        caller = details.caller
        profile = self.profiles.setdefault(caller, {})
        if profile.setdefault('offline', None) is None:
            registration = yield self.register(self.offline, 'xchat.user.{}.offline'.format(caller), options=RegisterOptions(details_arg='details'))
            profile['offline'] = registration

        returnValue({'ok': True})

    def offline(self, details=None):
        caller = details.caller
        profile = self.profiles.setdefault(caller, {})
        offline = profile.get('offline')
        if offline is not None:
            offline.unregister()
        return {'ok': True}

    def send_msg(self):
        pass