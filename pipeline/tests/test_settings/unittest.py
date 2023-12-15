import os
from pathlib import Path

from common import const
from configurations import Configuration


class UnittestConfig(Configuration):
    DEBUG = True

    # Paths
    BASE_DIR = Path(__file__).parents[3]
    PROJECT_DIR = BASE_DIR / const.PIPELINE
    CONFIG_FILE = BASE_DIR / "tests" / "test_configs" / "pipeline.yml"
    DATA_DIR = PROJECT_DIR / "tests" / "test_data"

    LOAD_BATCH_SIZE = 1_000
    READ_CHUNK_SIZE = 1_000

    # ENVIRONMENT
    ENV = os.getenv("ENV", None)

    INSTALLED_APPS = (
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "tax_credit",
        "tests",
    )

    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "NAME": os.getenv("POSTGRES_DB", None),
            "USER": os.getenv("POSTGRES_USER", None),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", None),
            "HOST": os.getenv("POSTGRES_HOST", None),
            "PORT": int(os.getenv("POSTGRES_PORT", None)),
            "CONN_MAX_AGE": int(os.getenv("POSTGRES_CONN_MAX_AGE", None)),
            "DISABLE_SERVER_SIDE_CURSORS": False,
        }
    }
