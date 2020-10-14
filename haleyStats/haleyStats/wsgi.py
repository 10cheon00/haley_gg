"""
WSGI config for haleyStats project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

"""DJANGO_SETTINGS_MODULE set local setting. It must changed when you have
        other purpost like publish products or test this project..etc. """
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haleyStats.settings.local')

application = get_wsgi_application()
