import jwt
from rest_framework_jwt.settings import api_settings


def encode_ns_user(ns, user):
    if ns:
        return ns + ':' + user
    return user


def decode_ns_user(user):
    parts = user.split(':', 1)
    if len(parts) == 1:
        return '', user
    return parts[0], parts[1]


def parse_ns_token(token):
    parts = token.split(':', 1)
    if len(parts) == 1:
        return '', token
    return parts[0], parts[1]


def jwt_decode_handler(token):
    ns, token = parse_ns_token(token.decode())
    options = {
        'verify_exp': api_settings.JWT_VERIFY_EXPIRATION,
    }

    payload = jwt.decode(
            token,
            api_settings.JWT_SECRET_KEY[ns],
            api_settings.JWT_VERIFY,
            options=options,
            leeway=api_settings.JWT_LEEWAY,
            audience=api_settings.JWT_AUDIENCE,
            issuer=api_settings.JWT_ISSUER,
            algorithms=[api_settings.JWT_ALGORITHM]
    )
    payload['ns'] = ns
    return payload


from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import exceptions


class VirtualUser(object):
    def __init__(self, is_admin=False, ns=""):
        self.is_staff = is_admin
        self.ns = ns

    def __str__(self):
        return 'VirtualUser'

    def is_authenticated(self):
        return True


class JWTAuthentication(JSONWebTokenAuthentication):
    def get_jwt_value(self, request):
        jwt = super(JWTAuthentication, self).get_jwt_value(request)
        return jwt or request.query_params.get('jwt').encode()

    def authenticate_credentials(self, payload):
        is_admin = payload.get("is_admin", False)
        ns = payload.get("ns", "")
        return VirtualUser(is_admin=is_admin, ns=ns)
