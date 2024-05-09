"""Populates the target-bonus geography association table with records.
"""

# Standard library imports
import itertools
from datetime import datetime, timedelta, UTC

# Third-party imports
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.db.utils import IntegrityError, ProgrammingError

# Application imports
from common.db import dynamic_bulk_insert
from common.logger import LoggerFactory
from common.storage import DataLoader, DataWriter
from tax_credit.associations import AssociationsService
from tax_credit.models import TargetBonusGeographyOverlap
from tax_credit.population import PopulationService


class Command(BaseCommand):
    """Calculates spatial intersections between "target" geographies
    adminstered by government officials (e.g., states, counties,
    municipalities, public utilities and rural cooperatives) and
    tax credit "bonus" geographies (e.g., Justice 40 communities,
    low-income census tracts). Then estimates the population within
    the overlapping area(s). Finally, bulk inserts the geography
    associations with their population counts into the database.

    References:
    - https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/
    - https://docs.djangoproject.com/en/4.1/topics/settings/
    """

    help = "Populates the target-bonus geography association table."
    name = "Load Target-Bonus Associations"

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

    def add_arguments(self, parser: CommandParser):
        """Provides two options, "target" and "bonus", which specify
        which target and bonus geography types, respectively, should be
        included within the database load. Each entry in "target" will
        have its records joined with each listed bonus entry's records
        using either an attribute or spatial intersection.

        Valid choices for "target" include:

        - county
        - municipality
        - rural cooperative
        - state

        Meanwhile, valid choices for "bonus" include:

        - distressed
        - energy
        - low-income
        - justice40

        When "target" or "bonus" is not provided, all available target
        and bonus geography types are used.

        Args:
            parser (`CommandParser`)

        Returns:
            `None`
        """
        parser.add_argument(
            "--target",
            nargs="+",
            default=[
                "county",
                "municipality",
                "municipal utility",
                "rural cooperative",
                "state",
            ],
            choices=[
                "county",
                "municipality",
                "municipal utility",
                "rural cooperative",
                "state",
            ],
            help="Restricts the targets that will be used for associations.",
        )
        parser.add_argument(
            "--bonus",
            nargs="+",
            default=[
                "distressed",
                "energy",
                "low-income",
                "justice40",
            ],
            choices=[
                "distressed",
                "energy",
                "low-income",
                "justice40",
            ],
            help="Restricts the bonuses that will be used for associations.",
        )

    def handle(self, *args, **options):
        """Executes the command. If the "target" and/or
        "bonus" option(s), have been provided, only the
        listed geography types are processed. Otherwise,
        all geography types are processed.

        Args:
            `None`

        Returns:
            `None`
        """
        # Initialize variables
        reader = DataLoader()
        writer = DataWriter()
        population_service = PopulationService.initialize(
            reader, writer, *settings.POPULATION_SERVICE.values(), self._logger
        )
        assoc_service = AssociationsService(population_service)

        # Iterate through each combination of target and bonus geography type
        for geo_type_combo in itertools.product(options["target"], options["bonus"]):

            # Create custom logger for dataset type
            target_geo_type, bonus_geo_type = geo_type_combo
            log_name = f"LOAD {target_geo_type.upper()} <> {bonus_geo_type.upper()}"
            logger = LoggerFactory.get(log_name)

            # Log and time start of processing
            logger.info(
                "Calculating intersections between geography types "
                f'"{target_geo_type}" (target) and "{bonus_geo_type}" (bonus).'
            )
            start_time = datetime.now(UTC)

            # Find bonus type geography matches
            logger.info("Searching for bonus geography matches.")
            matches = assoc_service.find_bonus_matches(target_geo_type, bonus_geo_type)
            logger.info(f"{len(matches)} match(es) found.")
            if not matches:
                continue

            # Define generator to construct table records
            target_bonus_geos = (
                TargetBonusGeographyOverlap(None, *match) for match in matches
            )

            # Perform bulk insert of matches into database
            try:
                logger.info(
                    f"Inserting {len(matches)} target-bonus "
                    "association(s) into database in batches."
                )
                num_inserted = dynamic_bulk_insert(
                    target_bonus_geos,
                    TargetBonusGeographyOverlap.objects,
                    logger,
                )
                elapsed = datetime.now(UTC) - start_time
                logger.info(
                    f"{num_inserted:,} record(s) successfully "
                    "inserted (or ignored if already present) "
                    f"in {elapsed}."
                )
            except (IntegrityError, ValueError, ProgrammingError) as e:
                logger.error(f"Failed to insert associations. {e}")
                exit(1)

            # Log completion
            logger.info(
                f'Finished matching "{target_geo_type}" geographies '
                f'with "{bonus_geo_type}" geographies and loading into '
                f"database in {elapsed}."
            )

            # Log warning if matching and load time exceeded configured threshold
            if elapsed > timedelta(minutes=settings.SLOW_LOAD_THRESHOLD_IN_MINUTES):
                logger.warn(
                    "Matching and load time exceeded the threshold "
                    f"of {settings.SLOW_LOAD_THRESHOLD_IN_MINUTES}."
                )

        # Mark end of process
        self._logger.info(
            "Database load of target-bonus associations completed successfully."
        )
