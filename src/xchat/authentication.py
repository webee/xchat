import jwt
from rest_framework_jwt.settings import api_settings
from pytoolbox.jwt import encode_ns_user, decode_ns_user, encode_ns_token, parse_ns_token
from pytoolbox.jwt import handle_jwt_decode, handle_jwt_encode


def jwt_decode_handler(token):
    return handle_jwt_decode(token, api_settings)


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
        return jwt or request.query_params.get('jwt')

    def authenticate_credentials(self, payload):
        is_admin = payload.get("is_admin", False)
        ns = payload.get("ns", "")
        return VirtualUser(is_admin=is_admin, ns=ns)
