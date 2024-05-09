"""A command to migrate database tables to a production instance.
"""

# Standard library imports
import os

# Third-party imports
from django.core.management.base import BaseCommand
from django.db import connection

# Application imports
from common.db import get_db_size, replicate_db_table, vacuum_db
from common.logger import LoggerFactory
from tax_credit.models import Geography, TargetBonusGeographyOverlap


class Command(BaseCommand):
    """Replaces the geometries in the tax credit geography column with their bounding
    boxes, performs a full vacuum on the database table to understand its total size,
    and then replicates the `tax_credit_geography` and `tax_credit_target_bonus_overlap'
    tables to the final production (cloud) database. This step is done in an effort
    to reduce the costs of Google Cloud SQL servers; after computing the target-bonus
    associations, the precise boundaries are no longer needed by the application and
    can be discarded, which permits the use of smaller, cheaper database. An entirely
    new database is required because Google Cloud SQL cannot vertically scale down
    once created.

    References:
    - https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/
    - https://docs.djangoproject.com/en/4.1/topics/settings/
    """

    help = (
        "Replaces tax credit geographies' boundaries with their bounding boxes "
        "and then replicates the simplified geographies and their associations "
        "in the final production database table."
    )
    name = "Replicate Database"

    def __init__(self, *args, **kwargs) -> None:
        """Initializes a new instance of the `Command`.

        Args:
            *The default positional arguments for the base class.

        Kwargs:
            **The default keyword arguments for the base class.

        Returns:
            `None`
        """
        self._logger = LoggerFactory.get(Command.name.upper())
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options) -> None:
        """Executes the command.

        Args:
            `None`

        Returns:
            `None`
        """
        # Log start of process
        self._logger.info("Starting database replication.")

        # Retrieve name of source and target databases from environment
        try:
            self._logger.info(
                "Retrieving aliases of source and target "
                "databases from environment variables."
            )
            source_db_alias = os.environ["POSTGRES_ALIAS"]
            target_db_alias = os.environ["RESIZED_POSTGRES_ALIAS"]
            self._logger.info(
                f'Found source database "{source_db_alias}" '
                f'and target database "{target_db_alias}".'
            )
        except KeyError as e:
            self._logger.error(f'Missing expected environment variable "{e}".')
            exit(1)

        # Log database size before processing
        try:
            self._logger.info(
                "Checking size of source database before simplifying geometries."
            )
            size = get_db_size(source_db_alias)
            self._logger.info(
                f'Alias "{source_db_alias}" currently occuplies {size} of memory.'
            )
        except RuntimeError as e:
            self._logger.error(f"Database replication failed. {e}")
            exit(1)

        # Simplify geographies' geometries to bounding boxes
        try:
            self._logger.info(
                "Simplifying source database geographies' geometries to bounding boxes."
            )
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE tax_credit_geography
                    SET geometry = ST_MULTI(ST_ENVELOPE(geometry));
                    """
                )
            self._logger.info(f"{cursor.rowcount:,} row(s) successfully updated.")
        except Exception as e:
            self._logger.error(
                "Database replication failed. Error changing tax credit "
                f"geographies' geometries to bounding boxes. {e}"
            )
            exit(1)

        # Vacuum table to reclaim memory
        try:
            self._logger.info(
                "Performing full vacuum of source database to reclaim space."
            )
            vacuum_db(source_db_alias)
            self._logger.info("Vacuum completed.")
        except Exception as e:
            self._logger.error(f"Data replication failed. {e}")
            exit(1)

        # Log new size of database
        try:
            self._logger.info("Checking size of database after simplifying geometries.")
            size = get_db_size(source_db_alias)
            self._logger.info(f'Final size of source database: "{size}".')
        except RuntimeError as e:
            self._logger.error(f"Database replication failed. {e}")
            exit(1)

        # Insert geographies into production database table
        try:
            self._logger.info(
                "Replicating source database geographies table in destination database."
            )
            replicate_db_table(
                Geography.objects, source_db_alias, target_db_alias, self._logger
            )
        except Exception as e:
            self._logger.error(f"Replication failed. {e}")
            exit(1)

        # Insert target-bonus associations into production database table
        try:
            self._logger.info(
                "Replicating source database geography "
                "intersections table in destination database."
            )
            replicate_db_table(
                TargetBonusGeographyOverlap.objects,
                source_db_alias,
                target_db_alias,
                self._logger,
            )
        except Exception as e:
            self._logger.error(f"Replication failed. {e}")
            exit(1)

        # Log end of process
        self._logger.info("Database replication completed successfully.")
