"""Waits for a PostgreSQL database server to start up and allow conncections.
"""

import logging
import os
import psycopg2
from time import time, sleep

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

# Fetch database settings
check_timeout = int(os.getenv("POSTGRES_CHECK_TIMEOUT", 30))
check_interval = int(os.getenv("POSTGRES_CHECK_INTERVAL", 1))
settings = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
}

# Attempt database connection until success or timeout
start_time = time()
while time() - start_time < check_timeout:
    try:
        conn = psycopg2.connect(**settings)
        logger.info("Postgres is ready! ✨ 💅")
        conn.close()
        exit(0)
    except psycopg2.OperationalError:
        logger.info(
            "Postgres isn't ready. Waiting for " f"{check_interval} second(s)..."
        )
        sleep(check_interval)

logger.error("We could not connect to Postgres " f"within {check_timeout} second(s).")
exit(1)
