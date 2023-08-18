"""Settings to use when running the Django project in production.
"""

import os
from .base import BaseConfig
from corsheaders.defaults import default_headers


class ProductionConfig(BaseConfig):
    """Defines configuration settings for production environments.
    """

    # General
    INSTALLED_APPS = BaseConfig.INSTALLED_APPS
    WSGI_APPLICATION = 'config.wsgi.application'

    # Server
    INSTALLED_APPS += ("gunicorn", )

    # Cross-origin requests
    # https://github.com/adamchainz/django-cors-headers
    CORS_ALLOW_HEADERS = list(default_headers) + [
        'Access-Control-Allow-Origin',
    ]
    CORS_ALLOWED_ORIGINS = []

    # HTTP security settings
    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = [] 
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = False

    # Google Cloud Storage
    STORAGE_BUCKET = os.getenv("CLOUD_STORAGE_BUCKET", "")

    # If the flag has been set, configure to use proxy
    # https://cloud.google.com/python/django/run
    if os.getenv("USE_CLOUD_SQL_AUTH_PROXY", None):
        BaseConfig.DATABASES["default"]["HOST"] = "127.0.0.1"
        BaseConfig.DATABASES["default"]["PORT"] = 5432
        ALLOWED_HOSTS += ('0.0.0.0',)
        DEBUG = True
        SECURE_PROXY_SSL_HEADER = None
        SECURE_SSL_REDIRECT = False

