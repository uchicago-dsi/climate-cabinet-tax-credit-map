"""Loads tax credit programs for geographies into the database.
"""

from django.core.management.base import BaseCommand, CommandParser
import pandas as pd
from apps.tax_credit.models import Program


class Command(BaseCommand):
    """
    Populates the `Program` and `GeographyTypeProgram` tables.

    References:
    - https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/
    - https://docs.djangoproject.com/en/4.1/topics/settings/
    """

    help = "Loads data to populate the tax credit program tables."

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
        programs_file = "data/program.csv"
        records = pd.read_csv(programs_file, header=0, delimiter="|").to_dict(
            orient="records"
        )

        programs = [
            Program(
                name=record["Program"],
                agency=record["Agency"],
                description=record["Description"],
                base_benefit=record["Base_benefit"],
            )
            for record in records
        ]

        Program.objects.bulk_create(programs)
