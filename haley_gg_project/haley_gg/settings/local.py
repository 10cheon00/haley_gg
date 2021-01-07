from .base import *

DEBUG = True

ALLOWED_HOSTS += ['*']

INSTALLED_APPS += [
    'haley_gg.apps.stats',
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

INTERNAL_IPS = [
    # '0.0.0.0',
    '172.17.0.1'
]
