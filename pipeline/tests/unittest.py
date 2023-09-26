"""Contains project settings for running test cases."""
from pathlib import Path

from config.settings.base import BaseConfig


class UnittestConfig(BaseConfig):
    BASE_DIR = Path(BaseConfig.BASE_DIR)

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
