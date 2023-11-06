import logging
import sys
from logging import Logger
from typing import Any, Optional, Union

from common.logger import LoggerFactory
from common.storage import DataReaderFactory
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from tax_credit.config_reader import get_load_config_reader
from tax_credit.database_helper import DatabaseHelper
from tax_credit.validator import Validator

logger: Logger = LoggerFactory.get(__name__)
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_handler)

config = get_load_config_reader(settings.CONFIG_FILE)


class Command(BaseCommand):
    help = (
        "Loads the database tables that have no dependencies on other tables"
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--smoke-test",
            nargs=2,
            help="Minimal data load test config, 2 args : [batch size] [batch num]",
        )

        return super().add_arguments(parser)

    def handle(
        self, *args: list[str], **options: dict[str, Any]
    ) -> Union[str, None]:
        load_batch_size: int = settings.LOAD_BATCH_SIZE
        batch_number_of: Optional[int] = None

        if options.get("smoke_test", None):
            smoke_test_batch_size, smoke_test_batch_num_of = options[
                "smoke_test"
            ]
            load_batch_size, batch_number_of = int(smoke_test_batch_size), int(
                smoke_test_batch_num_of
            )

        for job in config.base_jobs:
            try:
                reader = DataReaderFactory.get(job.file_format)
                Validator.validate(job, reader)
                DatabaseHelper.load_batched(
                    job, reader, load_batch_size, batch_number_of
                )
            except RuntimeError as re:
                logger.error("ERROR!!!!! Could not validate load job, job will not run.")
                logger.error(f"ERROR : {re}")
