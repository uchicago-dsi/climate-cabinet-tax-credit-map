from common.logger import LoggerFactory
from django.contrib.gis.db.backends.postgis.base import (
    DatabaseWrapper as PostgisDatabaseWrapper,
)

logger = LoggerFactory.get(__name__)


class DatabaseWrapper(PostgisDatabaseWrapper):
    def __init__(self, *args, **kwargs):
        logger.info("Creating DB wrapper...")
        super().__init__(*args, **kwargs)

    def get_new_connection(self, conn_params):
        logger.info("Creating new connection...")
        return super().get_new_connection(conn_params)
