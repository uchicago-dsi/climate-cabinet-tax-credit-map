"""Populates the geography table with records.
"""

# Standard-library imports
import random

# Third-party imports
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.db.utils import IntegrityError, ProgrammingError

# Application imports
from common.db import dynamic_bulk_insert
from common.logger import LoggerFactory
from common.storage import ParquetDataReader
from tax_credit.models import Geography


class Command(BaseCommand):
    """Loads cleaned geo datasets from the configured storage location,
    validates the data, applies transformation functions to the
    records of each dataset in preparation for database table load,
    and then upserts the records to the geography table in batches
    using an exponential smoothing algorithm to dynamically determine
    the batch size.

    References:
    - https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/
    - https://docs.djangoproject.com/en/4.1/topics/settings/
    """

    help = "Populates the geography database table."
    name = "Load Geographies."

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

    def add_arguments(self, parser: CommandParser) -> None:
        """Provides two options: (1) "smoke-test", to load smaller
        datasets of N records each for testing that are randomly
        selected from the full data file using the random seed S,
        and (2) "geos", to load only select geography types. Valid
        choices for "geos" include:

        - counties
        - distressed communities
        - energy communities - coal
        - energy communities - fossil fuels
        - justice40 communities
        - low-income communities
        - municipalities - states
        - municipalities - territories
        - municipal utilities
        - rural cooperatives
        - states

        Args:
            parser (`CommandParser`)

        Returns:
            `None`
        """
        parser.add_argument(
            "--smoke-test",
            nargs=2,
            type=int,
            default=[],
            help=(
                "Tests the geography table load with a subset of "
                "data. Accepts two arguments. The first specifies how "
                "many records should be loaded from each dataset. The "
                "program will gracefully load all records for a dataset if "
                "the argument is greater than the total number of records "
                "available in that dataset. The second argument is for the "
                "random seed used to randomly select the subset of data."
            ),
        )
        parser.add_argument("--geos", nargs="+", default=[])

    def handle(self, *args, **options) -> None:
        """Executes the command. If the "geos" option
        has been provided, only the listed datasets
        are loaded. Otherwise, all datasets are loaded.
        Likewise, if the "smoke_test" option is given
        only the specified number of random records from
        each dataset will be loaded.

        Args:
            `None`

        Returns:
            `None`
        """
        # Initialize variables
        num_processed = 0
        reader = ParquetDataReader()
        geos = options["geos"]
        try:
            dataset_max_size, random_seed = options["smoke_test"]
        except:
            dataset_max_size = random_seed = None

        # Process each configured dataset
        for dataset_config in settings.CLEAN_DATASETS:

            # Parse dataset config
            try:
                dataset_name = dataset_config["name"]
                dataset_fpath = dataset_config["file"]
            except KeyError as e:
                self._logger.error(
                    f'Unable to parse configuration object. Missing expected key "{e}".'
                )
                exit(1)

            # Skip processing if indicated by command line options
            if geos and (dataset_name not in geos):
                continue

            # Otherwise, create custom logger for dataset type
            log_name = f"LOAD {dataset_name.upper()}"
            self._logger = LoggerFactory.get(log_name)

            # Attempt to load dataset and map each row to geography type
            self._logger.info(
                "Received request to load cleaned dataset "
                f"\"{dataset_config['name']}\" into the "
                "geographies table. Reading data file and "
                "mapping dataset rows to database table schema."
            )
            try:
                mapped_geos = (
                    Geography.from_series(row)
                    for row in reader.iterate(dataset_config["file"])
                )
            except FileExistsError:
                self._logger.error(
                    f'Failed to load dataset "{dataset_name}". '
                    f'Could not find file "{dataset_fpath}".'
                )
                exit(1)
            except RuntimeError as e:
                self._logger.error(f'Failed to load dataset "{dataset_name}". {e}')
                exit(1)

            # If conducting smoke test, take random sample of loaded geographies
            if options["smoke_test"]:
                self._logger.info(
                    "Taking random sample of mapped geographies for smoke test."
                )
                random.seed(random_seed)
                geo_indices = list(range(len(mapped_geos)))
                sample_size = min(len(mapped_geos), dataset_max_size)
                new_mapped_geos = []
                for idx in random.sample(geo_indices, sample_size):
                    new_mapped_geos.append(mapped_geos[idx])
                mapped_geos = new_mapped_geos

            # Bulk insert mapped geographies to table in batches
            try:
                self._logger.info(
                    f'Inserting "{dataset_name}" into Geography database table.'
                )
                num_inserted = dynamic_bulk_insert(
                    mapped_geos, Geography.objects, self._logger
                )
                self._logger.info(
                    f"{num_inserted:,} record(s) successfully "
                    "inserted (or ignored if already present)."
                )
            except (IntegrityError, ValueError, ProgrammingError) as e:
                self._logger.error(
                    f'Failed to insert geographies for dataset "{dataset_name}". {e}'
                )
                exit(1)

            # Update number of datasets processed
            num_processed += 1

        # Log completion of job
        if not num_processed:
            self._logger.info("No datasets found with given geography name(s).")
        else:
            self._logger.info("Geographies load complete.")
