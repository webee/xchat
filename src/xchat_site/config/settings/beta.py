XCHAT_API_ROOT_URL = 'http://b.xchat.qinqinxiaobao.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'xchat_beta',
        'USER': 'xchat_dev',
        'PASSWORD': 'xchat1234',
        'HOST': 'localhost',
        'PORT': '5432',
        #'CONN_MAX_AGE': 7,
    }
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
            'level': 'DEBUG',
            'propagate': True
        },
        'requests': {
            'level': 'ERROR'
        }
    },
}
