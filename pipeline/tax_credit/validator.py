from .load_job import LoadJob
from common.storage2 import DataReader, DataReaderFactory
from common.logger import LoggerFactory

from django.conf import settings

from tax_credit.models import Program


logger = LoggerFactory.get(__name__)

csv_data_reader: DataReader = DataReaderFactory.get("csv")
parquet_data_reader: DataReader = DataReaderFactory.get("geoparquet")

class Validator():

    @staticmethod
    def validate(load_job: LoadJob, data_reader: DataReader):

        # TODO Custom errors

        Validator.file_exists(load_job, data_reader)
        Validator.cols_exist(load_job, data_reader)
        Validator.required_tables_loaded(load_job)
        

    @staticmethod
    def file_exists(load_job: LoadJob, data_reader: DataReader):
        filename = load_job.file_name
        bucket_contents = [item.name for item in data_reader.get_data_bucket_contents()]
        if not filename in bucket_contents:
            raise RuntimeError(f"Requeste file is missing from data folder : {filename} . Available files : {bucket_contents} .")

    @staticmethod
    def cols_exist(load_job: LoadJob, data_reader: DataReader):

        missing_cols = []
        actual_cols = data_reader.col_names(load_job.file_name)
        for required_col in load_job.file_field_names:
            if not required_col in actual_cols:
                missing_cols.append(required_col)
        if missing_cols:
            raise RuntimeError(f"Columns are missing from the file : {missing_cols} . Available fields : {actual_cols} .")

    @staticmethod
    def required_tables_loaded(load_job: LoadJob):
        """Verifies that all dependent tables have at least some contents"""

        unloaded_tables = []
        for model in load_job.required_models:
            if not model.objects.all().count() > 0:
                unloaded_tables.append(model)
        
        if unloaded_tables:
            raise RuntimeError(f"Models need to be loaded : {unloaded_tables}")
