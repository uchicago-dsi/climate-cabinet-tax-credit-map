"""Cleans raw datasets.
"""

from django.core.management.base import BaseCommand, CommandParser
from common.logger import LoggerFactory
from django.conf import settings
from common.storage import DataFrameReader, DataFrameWriter
from tax_credit.datasets import DatasetFactory, GeoDataset


class Command(BaseCommand):
    """
    Loads raw datasets from the configured storage location; cleans
    them to remove irrelevant records and standardize geography
    names, FIPS codes, and geometries; and finally, saves the data as
    geoparquet and line-delimited GeoJSON files for later database
    load and Mapbox tileset creation.

    References:
    - https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/
    - https://docs.djangoproject.com/en/4.1/topics/settings/
    """

    help = "Cleans raw datasets."
    name = "Clean Data"

    def __init__(self, *args, **kwargs) -> None:
        """Initializes a new instance of the `Command`.

        Args:
            *The default positional arguments for the base class.

        Kwargs:
            **The default keyword arguments for the base class.

        Returns:
            None
        """
        self._logger = LoggerFactory.get(Command.name.upper())
        super().__init__(*args, **kwargs)        

    def add_arguments(self, parser: CommandParser) -> None:
        """Provides an option, "geos", to clean and load only
        select geography types. Valid choices include:

        - counties
        - distressed communities
        - energy communities - coal
        - energy communities - fossil fuels
        - justice40 communities
        - low-income communities
        - municipalities
        - municipal utilities
        - rural cooperatives
        - states

        Args:
            parser (`CommandParser`)

        Returns:
            `None`
        """
        parser.add_argument(
            '--geos',
            nargs='+',
            default=[]
        )

    def handle(self, *args, **options) -> None:
        """
        Executes the command. If the "geos" option
        has been provided, only the listed datasets
        are cleaned. Otherwise, all datasets are cleaned.

        Args:
            None

        Returns:
            None
        """
        # Initialize variables
        geos = options["geos"]
        reader = DataFrameReader()
        writer = DataFrameWriter()

        # Process each configured dataset
        for dataset_config in settings.RAW_DATASETS:

            # Skip processing if indicated by command line options
            if geos and dataset_config["name"] not in geos:
                continue

            # Otherwise, create custom logger for dataset type
            log_name = f"CLEAN {dataset_config['name'].upper()}"
            logger = LoggerFactory.get(log_name)

            # Initialize dataset
            logger.info("Received request to process dataset "
                        f"\"{dataset_config['name']}\". Initializing.")
            fpaths = dataset_config.pop("files")
            dataset: GeoDataset = DatasetFactory.create(
                **dataset_config,
                logger=logger,
                reader=reader,
                writer=writer
            )
            
            # Load and clean dataset
            logger.info("Beginning processing job.")
            dataset.process(**fpaths)

            # Write dataset to geoparquet file
            logger.info("Writing processed data to geoparquet file.")
            dataset.to_geoparquet()

            # Write dataset to line-delimited GeoJSON
            logger.info("Writing processed data to new line delimited GeoJSON.")
            dataset.to_geojson_lines()

        self._logger.info("Data cleaning job complete.")
