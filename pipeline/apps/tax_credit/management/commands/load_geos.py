"""Loads geographies and geography types into the database.
"""

from django.core.management.base import BaseCommand, CommandParser
from apps.tax_credit.models import Geography_Type
import pandas as pd


class Command(BaseCommand):
    """
    Populates the `Geography` and `GeographyType` tables.

    References:
    - https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/
    - https://docs.djangoproject.com/en/4.1/topics/settings/
    """

    help = "Loads data to populate the geography type tables."

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Updates the class' `CommandParser` with arguments
        passed in from the command line.

        Parameters:
            parser (`CommandParser`): Django's implementation of
                the `ArgParser` class from the standard library.

        Returns:
            None
        """
        pass

    def handle(self, *args, **options) -> None:
        """
        Executes the command. Accepts variable
        numbers of keyword and non-keyword arguments.

        Parameters:
            None

        Returns:
            None
        """

        self._load_geo_types()

    def _load_geo_types(self):
        geo_types_file = "data/geography_type.csv"
        records = pd.read_csv(geo_types_file, header=0, delimiter="|").to_dict(
            orient="records"
        )

        geography_types = [
            Geography_Type(
                id=gt["id"],
                name=gt["Name"],
            )
            for gt in records
        ]

        Geography_Type.objects.bulk_create(geography_types)
