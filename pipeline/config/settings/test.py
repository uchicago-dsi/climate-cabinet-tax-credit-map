"""Settings used for unit and integration testing.
"""

# Standard library imports
import os

# Application imports
from .base import BaseConfig


class TestConfig(BaseConfig):
    """Defines configuration settings used for testing."""

    # Set debugging flag
    DEBUG = True

    # Environment
    ENV = os.getenv("ENV", "TEST")

    # Define file paths
    DATA_DIR = BaseConfig.BASE_DIR / "data"
