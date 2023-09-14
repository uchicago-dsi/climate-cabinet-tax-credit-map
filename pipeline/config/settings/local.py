"""Settings to use when running the Django project locally.
"""

import os
from pathlib import Path

from .base import BaseConfig

SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.dirname(SETTINGS_DIR)
PROJECT_DIR = os.path.dirname(CONFIG_DIR)


class LocalConfig(BaseConfig):
    """Defines configuration settings for local development environments."""

    # File paths
    DATA_DIR = Path(BaseConfig.BASE_DIR) / "data"

    # General
    DEBUG = True
    INSTALLED_APPS = BaseConfig.INSTALLED_APPS

    # Mail
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # Allowed Hosts
    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ["*"]

    # Cross-origin requests
    # https://github.com/adamchainz/django-cors-headers
    CORS_ORIGIN_ALLOW_ALL = True
