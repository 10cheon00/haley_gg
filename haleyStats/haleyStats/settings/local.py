from .base import *

DEBUG = True

ALLOWED_HOSTS += ['*']

INSTALLED_APPS += [
    'haleyStats.Apps.Users.apps.UsersConfig',
    'haleyStats.Apps.Maps.apps.MapsConfig',
]

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

STATIC_URL = '/static/'

MEDIA_URL = '/media/'
