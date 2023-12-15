from typing import Optional

from common.logger import LoggerFactory
from common.storage import DataReaderFactory
from django.conf import settings
from django.core.management import BaseCommand, CommandParser
from tax_credit.config_reader import get_load_config_reader
from tax_credit.database_helper import DatabaseHelper
from tax_credit.validator import Validator

config = get_load_config_reader(settings.CONFIG_FILE)

logger = LoggerFactory.get(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        pass

    def handle(self, *args, **options):
        load_batch_size: int = settings.LOAD_BATCH_SIZE
        batch_number_of: Optional[int] = None

        for job in config.dependent_jobs:
            try:
                reader = DataReaderFactory.get(job.file_format)
                Validator.validate(job, reader)
                DatabaseHelper.load_batched(
                    job, reader, load_batch_size, batch_number_of
                )
            except RuntimeError as re:
                logger.error(
                    f"Could not validate load job [ {job.job_name} ]. Records will not load."
                )
                logger.error(f"ERROR : {re}")
