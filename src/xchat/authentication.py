from rest_framework_jwt.settings import api_settings
from pytoolbox.jwt import handle_jwt_decode


def jwt_decode_handler(token):
    return handle_jwt_decode(token, api_settings)


class VirtualUser(object):
    def __init__(self, is_admin=False, ns=""):
        self.is_staff = is_admin
        self.ns = ns

    def __str__(self):
        return 'VirtualUser'

    def is_authenticated(self):
        return True


from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class JWTAuthentication(JSONWebTokenAuthentication):
    def get_jwt_value(self, request):
        jwt = super(JWTAuthentication, self).get_jwt_value(request)
        if jwt:
            jwt = jwt.decode('utf-8')
        return jwt or request.query_params.get('jwt')

    def authenticate_credentials(self, payload):
        is_admin = payload.get("is_admin", False)
        ns = payload.get("ns", "")
        return VirtualUser(is_admin=is_admin, ns=ns)
