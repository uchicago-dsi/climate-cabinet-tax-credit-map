"""Loads tax credit programs for geographies into the database.
"""

from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    """
    Populates the `GeographyMetric` table.

    References:
    - https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/
    - https://docs.djangoproject.com/en/4.1/topics/settings/
    """

    help = "Loads data to populate the geography metric table."

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
        pass
