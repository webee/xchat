import datetime
from pytoolbox.util.pmc_config import get_project_root, load_yaml, read_string

proj_root = get_project_root()
DEBUG = False
ALLOWED_HOSTS = ['l.xchat.com', 'xchat.qinqinxiaobao.com', '127.0.0.1', 'localhost']

XCHAT_API_ROOT_URL = 'http://xchat.qinqinxiaobao.com'
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = read_string('conf/xchat/secret_key.txt', root=proj_root)
USER_KEY = read_string('conf/xchat/user_key.txt', root=proj_root)
TEST_USER_KEY = read_string('conf/xchat/test_user_key.txt', root=proj_root)
CS_USER_KEY = read_string('conf/xchat/cs_user_key.txt', root=proj_root)
NS_USER_KEYS = {'': USER_KEY, 'test': TEST_USER_KEY, 'cs': CS_USER_KEY}


DATABASES = load_yaml('conf/xchat/databases.yaml', root=proj_root)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'


JWT_AUTH = {
    'JWT_SECRET_KEY': NS_USER_KEYS,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 10,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=36),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,
    'JWT_DECODE_HANDLER': 'xchat.authentication.jwt_decode_handler',

    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(hours=23),

    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        },
        'requests': {
            'level': 'INFO'
        }
    },
}
