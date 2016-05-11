from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
import jwt

import sys
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'xchat_site.settings')
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
django.setup()

from django.conf import settings


class AuthenticatorSession(ApplicationSession):
    @inlineCallbacks
    def onJoin(self, details):

        def authenticate(realm, authid, details):
            token = details['ticket']
            try:
                _ = jwt.decode(token, settings.USER_KEY)
            except Exception as e:
                raise ApplicationError(e)
            return "user"

        yield self.register(authenticate, 'cm.authenticate')

