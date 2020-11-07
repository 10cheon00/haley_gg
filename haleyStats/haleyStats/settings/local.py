from .base import *

DEBUG = True

ALLOWED_HOSTS += ['*']

INSTALLED_APPS += [
    'haleyStats.Apps.haley_gg.apps.HaleyGgConfig',
    'bootstrap4',
]

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

STATIC_URL = '/static/'

MEDIA_URL = '/media/'
