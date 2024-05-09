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
from django.db import connections, models
from django.db.utils import ProgrammingError, IntegrityError


def dynamic_bulk_insert(
    objs: Generator[models.Model, None, None],
    manager: models.Manager,
    logger: logging.Logger,
    smoothing_factor: float = settings.EXPONENTIAL_SMOOTHING_FACTOR,
    target_seconds_per_batch: int = settings.TARGET_SECONDS_PER_BATCH,
    db_alias: str = "default",
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

        manager (`models.Manager`): The Django Manager for the table (i.e.,
            the interface through which database query operations for the
            table are exposed).

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

        db_alias (`str`): The alias of the database to use for inserts.
            Defaults to "default".

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
            manager.using(db_alias).bulk_create(batch, ignore_conflicts=True)
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


def get_db_size(db_alias: str) -> str:
    """Reports the size of the given PostgreSQL database in megabytes (MB).

    Args:
        db_alias (`str`): The alias for the database (e.g., "default").

        logger (`logging.Logger`): A standard logger instance.

    Returns:
        (`str`): The size of the database with the units displayed
            (e.g., "147 MB").
    """
    try:
        conn = connections[db_alias]
        db_name = conn.settings_dict["NAME"]
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT pg_size_pretty(pg_database_size(%s))",
                [db_name],
            )
            return cursor.fetchone()[0]
    except KeyError as e:
        raise ValueError(
            "Failed to retrieve size of database. Could not locate "
            f'database "{db_name}" with alias "{db_alias}".'
        )
    except Exception as e:
        raise RuntimeError(f'Failed to retrieve size of database "{db_alias}". {e}')


def replicate_db_table(
    manager: models.Manager,
    from_db: str,
    to_db: str,
    logger: logging.Logger,
    batch_size: int = settings.DB_REPLICATION_CHUNK_SIZE,
) -> int:
    """Copies data from the given source database table
    to an identical table within the target database.

    Args:
        manager (`models.Manager`): The Django Manager for the table (i.e.,
            the interface through which database query operations for the
            table are exposed).

        from_db (`str`): The alias of the source database (e.g., "default").

        to_db (`str`): The alias of the destination database (e.g, "target").

        logger (`logging.Logger`): A standard logger instance.

        batch_size (`int`): The maximum number of rows to insert from the
            origin/source table to the destination table at once.
            Defaults to the value defined in configuration settings.

    Returns:
        (`int`): The number of rows added to the destination table.
    """
    # Get reference to table name
    table_name = manager.model.__name__

    # Count number of objects in tables before replication
    source_table_count = manager.count()
    dest_table_count = manager.using(to_db).count()
    logger.info(
        f"{dest_table_count:,} record(s) found in table "
        f'"{table_name}" in destination database "{to_db}"'
        f'while the same table in the "{from_db}" source '
        f"database has {source_table_count:,} record(s)."
    )

    # Fetch primary keys from table
    logger.info(
        f"Fetching primary keys from table "
        f'"{table_name}" in source database "{from_db}".'
    )
    pks = manager.using(from_db).values_list("id", flat=True).all()
    logger.info(f"{len(pks):,} key(s) found.")

    # Batch primary keys and retrieve corresponding full objects
    logger.info(
        f"Batching keys into groups of {batch_size:,} and then bulk "
        "inserting records associated with keys into destination table."
    )
    for i in range(0, len(pks), batch_size):
        pk_batch = pks[i : i + batch_size]
        objs = (obj for obj in manager.using(from_db).filter(pk__in=pk_batch).all())
        dynamic_bulk_insert(objs, manager, logger, db_alias=to_db)

    # Count final number of objects in destination table
    objs_added = manager.using(to_db).count() - dest_table_count
    logger.info(
        f"Replication complete. {objs_added:,} new record(s) "
        f'added to destination table "{table_name}".'
    )


def vacuum_db(db_name: str) -> None:
    """Performs a full vacuum on the given database.

    Args:
        db_name (`str`): The name of the database.

    Returns:
        `None`
    """
    try:
        with connections[db_name].cursor() as cursor:
            cursor.execute("VACUUM FULL")
    except KeyError as e:
        raise ValueError(
            "Failed to run full vacuum on database. "
            f'Could not locate database with name "{db_name}".'
        )
    except Exception as e:
        raise RuntimeError(f'Full vacuum on database "{db_name}" failed. {e}')
