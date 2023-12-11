from common.logger import LoggerFactory
from common.storage import DataReader

from .load_job import LoadJob

logger = LoggerFactory.get(__name__)


class Validator:
    @staticmethod
    def validate(load_job: LoadJob, data_reader: DataReader):
        Validator.file_exists(load_job, data_reader)
        Validator.cols_exist(load_job, data_reader)
        Validator.required_tables_loaded(load_job)

    @staticmethod
    def file_exists(load_job: LoadJob, data_reader: DataReader):
        filename = load_job.filename
        bucket_contents = data_reader.get_data_bucket_contents()
        if not filename in bucket_contents:
            raise RuntimeError(
                f"Requested file [ {filename} ] is missing from data folder. Available files: [ {bucket_contents} ]"
            )

    @staticmethod
    def cols_exist(load_job: LoadJob, data_reader: DataReader):
        missing_cols = []
        actual_cols = data_reader.col_names(
            load_job.filename, delimiter=load_job.delimiter
        )
        for required_col in load_job.file_field_names:
            if required_col not in actual_cols:
                missing_cols.append(required_col)
        if missing_cols:
            raise RuntimeError(
                f"Columns are missing from the file : {missing_cols} . "
                f"Available fields : {actual_cols} ."
            )

    @staticmethod
    def required_tables_loaded(load_job: LoadJob):
        """Verifies that all dependent tables have at least some contents"""

        unloaded_tables = []
        for model in load_job.required_models:
            if not model.objects.all().count() > 0:
                unloaded_tables.append(model)

        if unloaded_tables:
            raise RuntimeError(f"Models need to be loaded : {unloaded_tables}")
