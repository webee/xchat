from datetime import datetime, timedelta
from django.conf import settings
import jwt


def gen_token(user, ns='', expire=timedelta(hours=1), is_admin=False):
    payload = {
        'ns': ns,
        'user': user,
        'exp': datetime.utcnow() + expire
    }

    if is_admin:
        payload['is_admin'] = True

    return jwt.encode(payload, settings.NS_USER_KEYS[ns], 'HS256').decode('utf-8')
