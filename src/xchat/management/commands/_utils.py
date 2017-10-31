from datetime import datetime, timedelta
from django.conf import settings
import jwt


def gen_token(user=None, ns=None, expire=timedelta(hours=1), is_admin=False):
    payload = {
        'exp': datetime.utcnow() + expire
    }

    if is_admin:
        payload['ns'] = ns
        payload['is_admin'] = True
    else:
        payload.update({
            'ns': ns,
            'user': user
        })

    return jwt.encode(payload, settings.NS_USER_KEYS[ns], 'HS256').decode('utf-8')
