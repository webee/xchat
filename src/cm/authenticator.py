from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
from twisted.logger import Logger
import jwt
import sys
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xchat_site.settings')
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
django.setup()


class JWTAuthenticatorSession(ApplicationSession):
    logger = Logger()

    @inlineCallbacks
    def onJoin(self, details):
        print("JWTAuthenticator Joined.")

        try:
            yield self.register(JWTAuthenticatorSession.authenticate, 'xchat.authenticate.jwt')
            print("[xchat.authenticate.jwt] registered.")
        except Exception as e:
            print("[xchat.authenticate.jwt] register failed: {}".format(e))

    @staticmethod
    def authenticate(realm, authid, details):
        print("authenticate: realm ", realm)
        print("authenticate: authid ", authid)
        print("authenticate: details ", details)
        token = details['ticket']
        try:
            data = jwt.decode(token, settings.USER_KEY)
        except Exception as e:
            print(e)
            raise ApplicationError('xchat.authenticate.jwt')
        if data['user'] == authid:
            return "user"
        raise ApplicationError('xchat.authenticate.jwt')
