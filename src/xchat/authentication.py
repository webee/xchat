from calendar import timegm
from datetime import datetime
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.compat import get_username, get_username_field


class JWTAuthentication(JSONWebTokenAuthentication):
    def get_jwt_value(self, request):
        jwt = super(JWTAuthentication, self).get_jwt_value(request)
        return jwt or request.query_params.get('jwt')


def jwt_payload_handler(user):
    username_field = get_username_field()
    username = get_username(user)

    payload = {
        'app': username,
        username_field: username,
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
    }

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
                datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload
