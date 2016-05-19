from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import exceptions


class VirtualUser(object):
    def __init__(self, is_admin=False):
        self.is_staff = is_admin

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
        return VirtualUser(is_admin=is_admin)
