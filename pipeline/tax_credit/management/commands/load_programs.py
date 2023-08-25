"""Loads tax credit programs for geographies into the database."""

import pandas as pd
from common.storage import DataReaderFactory, IDataReader
from django.core.management.base import BaseCommand, CommandParser
from tax_credit.models import Program

data_reader: IDataReader = DataReaderFactory.get_reader()


class Command(BaseCommand):
    """Populates the `Program` and `GeographyTypeProgram` tables.

    References:
    - https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/
    - https://docs.djangoproject.com/en/4.1/topics/settings/
    """

    help = "Loads data to populate the tax credit program tables."

    def add_arguments(self, parser: CommandParser) -> None:
        """Updates the class' `CommandParser` with arguments passed in from the
        command line.

        Parameters:
            parser (`CommandParser`): Django's implementation of
                the `ArgParser` class from the standard library.

        Returns:
            None
        """
        pass

    def handle(self, *args, **options) -> None:
        """Executes the command. Accepts variable numbers of keyword and non-
        keyword arguments.

        Parameters:
            None

        Returns:
            None
        """
        records: list[dict[str, str]] = data_reader.read_csv(
            "program.csv", delimiter="|"
        ).to_dict(orient="records")

        programs = [
            Program(
                id=record["Id"],
                name=record["Program"],
                agency=record["Agency"],
                description=record["Description"],
                base_benefit=record["Base_benefit"],
            )
            for record in records
        ]

        Program.objects.bulk_create(programs)
