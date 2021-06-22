"""
WSGI config for big_screen project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "big_screen.settings_dev")

application = get_wsgi_application()
# DJANGO_SETTINGS_MODULE = ''
# WEBSOCKET_FACTORY_CLASS = "dwebsocket.backends.uwsgi.factory.uWsgiWebSocketFactory"
