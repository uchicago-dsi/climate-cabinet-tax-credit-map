import os

env = os.getenv("ENV", "DEV")

if env == "DEV":
    from .local import LocalConfig  # noqa: F401
elif env == "TEST":
    from .test import TestConfig  # noqa: F401
elif env == "PROD":
    from .production import ProductionConfig  # noqa: F401
else:
    raise ValueError(f'Received an unexpected value for ENV: "{env}".')
