from abc import ABC, abstractmethod, abstractproperty
from typing import Any, Iterator
import os
import csv
from io import BytesIO
from contextlib import contextmanager

from .logger import LoggerFactory

from django.conf import settings

from pyarrow import parquet as pq
from google.cloud import storage

logger = LoggerFactory.get(__name__)
storage_client = storage.Client()
bucket = storage_client.bucket(settings.CLOUD_STORAGE_BUCKET)

class FileSystemHelper(ABC):

    @abstractmethod
    def get_data_bucket_contents(self) -> Iterator[str]:
        """Pulls the contents from the data bucket defined in settings"""
        raise NotImplementedError
    
    @abstractmethod
    @contextmanager
    def get_file(self, filename: str, mode='rt'):
        raise NotImplementedError


class LocalFileSystemHelper(FileSystemHelper):

    def get_data_bucket_contents(self) -> list[str]:
        return os.listdir(settings.DATA_DIR)
    
    @contextmanager
    def get_file(self, filename: str, mode='rt'):
        f = open(settings.DATA_DIR / filename, mode)
        try:
            yield f
        finally:
            f.close()


class CloudFileSystemHelper(FileSystemHelper):

    def get_data_bucket_contents(self) -> list[str]:
        blobs = storage_client.list_blobs(bucket)
        logger.warn(f'Blobs : {blobs}')
        return blobs
    
    @contextmanager
    def get_file(self, filename: str, mode='rt'):
        blob = bucket.blob(filename)
        file_bytes = BytesIO(blob.download_as_bytes(timeout=(3, 30)))
        yield file_bytes

    # TODO implement


class FileSystemHelperFactory:
    @staticmethod
    def get() -> FileSystemHelper:
        env = os.environ.get(
            "ENV",
            "DEV",
        )
        if env == "DEV":
            return LocalFileSystemHelper()
        elif env == "PROD":
            return CloudFileSystemHelper()
        else:
            raise RuntimeError(
                "Unable to instantiate FileSystemHelper, invalid environment variable passed for 'ENV'. Value passed : {env} ."
            )


class DataReader(ABC):
    def __init__(self):
        self.fileSystemHelper: FileSystemHelper = FileSystemHelperFactory.get()

    @abstractmethod
    def col_names(self, filename) -> list[str]:
        raise NotImplementedError
    
    @abstractmethod
    def iterate() -> Iterator[dict[str, Any]]:
        raise NotImplementedError
    
    def get_data_bucket_contents(self):
        return self.fileSystemHelper.get_data_bucket_contents()


class CsvDataReader(DataReader):

    def col_names(self, filename) -> list[str]:
        logger.info(f"Getting col names : {filename}")
        with self.fileSystemHelper.get_file(filename) as f:
            reader = csv.DictReader(f, delimiter='|')
            return reader.fieldnames

    def iterate(self, filename) -> Iterator[dict[str, Any]]:
        with self.fileSystemHelper.get_file(filename) as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                yield row


class ParquetDataReader(DataReader):

    def col_names(self, filename) -> list[str]:
        with self.fileSystemHelper.get_file(filename, mode='rb') as f:
            pf: pq.ParquetFile = pq.ParquetFile(f)
            try:
                return [c.name for c in pf.schema]
            finally:
                pf.close()

    
    def iterate(self, filename) -> Iterator[dict[str, Any]]:
        with self.fileSystemHelper.get_file(filename, mode='rb') as f:
            pf = pq.ParquetFile(f)
            pf_iter = pf.iter_batches(settings.PQ_CHUNK_SIZE)
            for batch in pf_iter:
                row_list = batch.to_pylist()
                for row in row_list:
                    yield row

class DataReaderFactory:

    @staticmethod
    def get(type: str) -> DataReader:

        if not type:
            raise TypeError("A value of { csv, parquet, geoparquet } must be given to DataReaderFactory for type")

        if type.lower() in [ "parquet", "geoparquet" ]:
            return ParquetDataReader()
        if type.lower() == "csv":
            return CsvDataReader()
        raise TypeError(f"A valid value must be given to DataReaderFactory. Value given : {type} .")