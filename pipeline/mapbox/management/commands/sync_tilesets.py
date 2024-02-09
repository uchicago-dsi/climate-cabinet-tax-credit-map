"""Syncs tileset data in the datastore with that in Mapbox.
"""

# Third-party imports
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser

# Application imports
from common.logger import LoggerFactory
from mapbox.clients import MapboxTilesetSyncClient


class Command(BaseCommand):
    """Updates Mapbox tileset sources and recipes and then
    creates and publishes tilesets from those elements.

    References:
    - https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/
    - https://docs.djangoproject.com/en/4.1/topics/settings/
    """

    help = "Syncs Mapbox tilesets."
    name = "Sync Tilesets"

    def __init__(self, *args, **kwargs) -> None:
        """Initializes a new instance of the `Command` with a logger.

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
        """Provides an option, "geos", to sync tilesets for only
        select geography types. Valid choices include:

        - counties
        - distressed communities
        - energy communities
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
        parser.add_argument("--geos", nargs="+", default=[])

    def handle(self, *args, **options) -> None:
        """Executes the command. If the "geos" option
        has been provided, only the listed datasets
        are synced. Otherwise, all datasets are synced.

        Args:
            `None`

        Returns:
            `None`
        """
        # Log start of command
        self._logger.info("Received command to sync Mapbox tilesets from data.")

        # Process each configured geography type
        geos = options["geos"]
        with MapboxTilesetSyncClient(self._logger) as client:
            for config in settings.MAPBOX_TILESETS:
                if geos and config["display_name"] not in geos:
                    continue
                else:
                    try:
                        client.sync_tileset(**config)
                    except RuntimeError as e:
                        self._logger.error(
                            f"Failed to process dataset "
                            f"\"{config['display_name']}\". {e}"
                        )

        # Log completion
        self._logger.info("Mapbox tileset sync complete.")
