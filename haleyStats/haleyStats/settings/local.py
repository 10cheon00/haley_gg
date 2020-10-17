from .base import *


DEBUG = True

ALLOWED_HOSTS += ['*']

INSTALLED_APPS += ['Users.apps.UsersConfig']

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

STATIC_URL = '/static/'