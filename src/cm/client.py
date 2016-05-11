from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
from autobahn.twisted.wamp import ApplicationSession


class ClientSession(ApplicationSession):
    def onConnect(self):
        realm = self.config.realm
        authid = self.config.extra[u'authid']
        print("ClientSession connected. Joining realm <{}> under authid <{}>".format(realm if realm else 'not provided', authid))
        self.join(realm, ['ticket'], authid)

    def onChallenge(self, challenge):
        print("ClientSession challenge received: {}".format(challenge))
        if challenge.method == 'ticket':
            return self.config.extra['jwt']
        else:
            raise Exception("Invalid authmethod {}".format(challenge.method))

    @inlineCallbacks
    def onJoin(self, details):
        print("ClientSession joined: {}".format(details))
        res = yield self.call("xchat.test.add", 3, 4)
        print("add() called with result: {result}".format(result=res))
        res = yield self.call("xchat.test.mul", 1, 2)
        print("mul() called with result: {result}".format(result=res))
        self.leave()

    def onLeave(self, details):
        print("ClientSession left: {}".format(details))
        self.disconnect()

    def onDisconnect(self):
        print("ClientSession disconnected")
        reactor.stop()


if __name__ == '__main__':
    from autobahn.twisted.wamp import ApplicationRunner

    extra = {
        'authid': "test",
        'jwt': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3QiLCJ1c2VyIjoidGVzdCIsImV4cCI6MTQ2MzA3NTUzNSwib3JpZ19pYXQiOjE0NjI5NDU5MzV9.podYXap_JEGl7ziB_K0C60Nsd0ZrISzFdeMcuSNf5cc"
    }
    runner = ApplicationRunner(url="ws://localhost:48080/ws", realm="xchat", extra=extra)
    runner.run(ClientSession)
