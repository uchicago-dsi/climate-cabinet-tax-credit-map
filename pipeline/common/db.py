"""Provides functions for common database operations not provided by the Django ORM.
"""

# Standard library imports
import logging
from datetime import datetime, timedelta
from itertools import islice
from math import ceil
from typing import Generator

# Third-party imports
from django.conf import settings
from django.db import models
from django.db.utils import ProgrammingError, IntegrityError


def dynamic_bulk_insert(
    objs: Generator[models.Model, None, None],
    manager: models.Manager,
    logger: logging.Logger,
    smoothing_factor: float = settings.EXPONENTIAL_SMOOTHING_FACTOR,
    target_seconds_per_batch: int = settings.TARGET_SECONDS_PER_BATCH,
) -> None:
    """Bulk inserts records into a database table in batches. Uses
    exponential smoothing to dynamically choose the batch size
    based on previous database server processing times.

    References:
    - ["Exponential Smoothing | Wikipedia"\
        ](https://en.wikipedia.org/wiki/Exponential_smoothing)
    - ["QuerySet API Reference | Django Documentation | Django"\
        ](https://docs.djangoproject.com/en/5.0/ref/models/querysets/#bulk-create)

    Args:
        objs (`generator` of `django.db.models.Model`): A generator
            yielding Django Model instances.

        logger (`logging.Logger`): A standard logger instance.

        smoothing_factor (`float`): A number between 0 and 1, inclusive.
            If close to zero, more weight is given to observations
            (i.e., database processing times) from the past when 
            determining the batch size.  If close to one, more weight is
            given to recent observations. Defaults to the value defined
            in configuration settings.

        target_seconds_per_batch (`int`): The ideal maximum number
            of seconds by which a batch should be inserted, which
            affects the size of the batch. Defaults to the value
            defined in configuration settings.

    Returns:
        `None`
    """
    # Initialize starting variables for batch insert
    batch_ct = 0
    batch_size = 1
    target_time = timedelta(seconds=target_seconds_per_batch)
    avg_record_proc_time = timedelta(seconds=0)
    num_inserted = 0

    # Begin database load
    try:
        logger.info(
            "Starting batch inserts to load record(s) "
            f'into "{manager.model.__name__}" table.'
        )

        while True:

            # Assign batch name
            batch_name = f"Batch {batch_ct + 1:,}, Size {batch_size:,}"

            # Pull batch of records to insert from list
            logger.info(f"{batch_name} - Pulling batch of records from list.")
            batch = list(islice(objs, batch_size))
            if not batch:
                logger.info("No more records left to insert. Database load complete.")
                break

            # Bulk insert records
            logger.info(f"{batch_name} - Bulk inserting records.")
            start_time = datetime.now()
            manager.bulk_create(batch, ignore_conflicts=True)
            end_time = datetime.now()
            processing_time = end_time - start_time
            num_inserted += len(batch)
            logger.debug(f"{batch_name} - Operation completed in {processing_time}.")

            # Calibrate proper size of next batch based on latest processing time
            logger.info(f"{batch_name} - Calculating best size for next batch.")
            avg_record_proc_time = (
                (1 - smoothing_factor) * avg_record_proc_time
                + smoothing_factor * processing_time / batch_size
            )
            if batch_ct < 5:
                batch_size = min(
                    ceil(target_time / avg_record_proc_time),
                    ceil(batch_size * 2),
                )
            else:
                batch_size = ceil(target_time / avg_record_proc_time)

            # Iterate batch count
            batch_ct += 1

    except (ProgrammingError, IntegrityError):
        logger.error("Database insert failed.")
        raise

    return num_inserted
