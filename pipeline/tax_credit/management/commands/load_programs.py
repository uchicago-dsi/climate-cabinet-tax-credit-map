"""Loads tax credit programs for geographies into the database."""

import pandas as pd
from common.storage import DataReaderFactory, IDataReader
from django.core.management.base import BaseCommand, CommandParser
from tax_credit.models import Geography_Type, Geography_Type_Program, Program

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
        # load program names
        program_df: pd.DataFrame = data_reader.read_csv("program.csv", delimiter="|")
        programs = [
            Program(
                id=record["Id"],
                name=record["Program"],
                agency=record["Agency"],
                description=record["Description"],
                base_benefit=record["Base_benefit"],
            )
            for _, record in program_df.iterrows()
        ]
        Program.objects.bulk_create(programs)

        # load program specifics for geography types
        # TODO if not geography is loaded, throw error
        type_program_df: pd.DataFrame = data_reader.read_csv(
            "geography_type_program.csv", delimiter="|"
        )
        geo_program_matches = [
            Geography_Type_Program(
                id=row["Id"],
                geography_type=Geography_Type.objects.get(
                    name=row["Geography_Type"]
                ),  # TODO will this be super slow?
                program=Program.objects.get(name=row["Program"]),  # TODO this slow too?
                amount_description=row["Abount_Description"],
            )
            for _, row in type_program_df.iterrows()
        ]
        Geography_Type_Program.objects.bulk_create(geo_program_matches, ignore_conflicts=True)
