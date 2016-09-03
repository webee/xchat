from datetime import datetime, timedelta
from django.conf import settings
from xchat.authentication import encode_ns_token
import jwt


def gen_token(user, ns='', expire=timedelta(hours=1), is_admin=False):
    payload = {
        'ns': ns,
        'user': user,
        'exp': datetime.utcnow() + expire
    }

    if is_admin:
        payload['is_admin'] = True

    token = jwt.encode(payload, settings.NS_USER_KEYS[ns], 'HS256').decode('utf-8')
    return encode_ns_token(ns, token)
