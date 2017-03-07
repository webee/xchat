import os

DEBUG = False
ALLOWED_HOSTS = ['localhost', 't.xchat.engdd.com']

STATIC_ROOT = os.path.join('/data/xchat', 'static')

XCHAT_API_ROOT_URL = 'http://t.xchat.engdd.com'

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
            'level': 'DEBUG',
            'propagate': True
        },
        'requests': {
            'level': 'ERROR'
        }
    },
}
