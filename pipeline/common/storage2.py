from abc import ABC, abstractmethod, abstractproperty
from typing import Any, Iterator
import os
import csv
import io
import tempfile
import json
from contextlib import contextmanager
from django.conf import settings

from .logger import LoggerFactory

from django.conf import settings

from pyarrow import parquet as pq

logger = LoggerFactory.get(__name__)

class FileSystemHelper(ABC):

    @abstractmethod
    def get_data_bucket_contents(self) -> Iterator[str]:
        """Pulls the contents from the data bucket defined in settings"""
        raise NotImplementedError
    
    @abstractmethod
    @contextmanager
    def get_file(self, filename: str, mode='rt', fmt='csv'):
        raise NotImplementedError


class _LocalFileSystemHelper(FileSystemHelper):

    def get_data_bucket_contents(self) -> list[str]:
        return os.listdir(settings.DATA_DIR)
    
    @contextmanager
    def get_file(self, filename: str, mode='rt', fmt='csv'):
        f = open(settings.DATA_DIR / filename, mode)
        try:
            yield f
        finally:
            f.close()


class _CloudFileSystemHelper(FileSystemHelper):

    def __init__(self):
        from google.cloud import storage
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(settings.CLOUD_STORAGE_BUCKET)

    def get_data_bucket_contents(self) -> list[str]:
        blobs = [item.name for item in self.storage_client.list_blobs(self.bucket)]
        logger.warn(f'Blobs : {blobs}')
        return blobs
    
    @contextmanager
    def get_file(self, filename: str, mode='rt', fmt='csv'):
        
        # if it's a csv file, save it to a temp file and return it open
        if fmt.lower() == 'csv':
            # tempdir = tempfile.gettempdir()
            # if filename in os.listdir(tempdir):
            #   f = open(f'{tempdir}/{filename}, 'rt')
            #   try:
            #       yield f
            #   finally:
            #       f.close()
            # else:
            tmp = tempfile.NamedTemporaryFile(delete=False)
            blob = self.bucket.blob(filename)
            with open(tmp.name, 'wb') as f:
                blob.download_to_file(f)
            logger.info(f"Temp file name : {tmp.name}")

            f = open(tmp.name, 'rt')
            try:
                yield f
            finally:
                f.close()

        # if it's a parquet file, establish a connection with the filesystem
        elif fmt.lower() in ['parquet', 'geoparquet']:
            logger.info("Loading geoparquet")
            logger.info(f"Gcp info file : {settings.GOOGLE_APPLICATION_CREDENTIALS}")
            with open(settings.GOOGLE_APPLICATION_CREDENTIALS, 'rb') as f:
                info = json.load(f)
                logger.warn(f"GCP connect info : {info.keys()}")

        else:
            raise ValueError(f'Error opening Google Cloud file, invalid format passed [{ fmt }] . Format should be one of [ csv, parquet, geoparquet ] .')


class FileSystemHelperFactory:
    _fileSystemHelper: FileSystemHelper = None

    @staticmethod
    def get() -> FileSystemHelper:
        if not FileSystemHelperFactory._fileSystemHelper:
            env = os.environ.get("ENV", "DEV")
            logger.info(f"Running env : {env}")

            if env == "DEV":
                FileSystemHelperFactory._fileSystemHelper = _LocalFileSystemHelper()
                return FileSystemHelperFactory._fileSystemHelper
            elif env == "PROD":
                FileSystemHelperFactory._fileSystemHelper = _CloudFileSystemHelper()
                return FileSystemHelperFactory._fileSystemHelper
            else:
                raise RuntimeError(
                    f"Unable to instantiate FileSystemHelper, invalid environment variable passed for 'ENV'. Value passed : {env} ."
                )
        
        return FileSystemHelperFactory._fileSystemHelper


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


class _CsvDataReader(DataReader):

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


class _ParquetDataReader(DataReader):

    def col_names(self, filename) -> list[str]:
        with self.fileSystemHelper.get_file(filename, mode='rb', fmt="parquet") as f:
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
    csv_data_reader = _CsvDataReader()
    parquet_data_reader = _ParquetDataReader()

    @staticmethod
    def get(type: str) -> DataReader:

        if not type:
            raise TypeError("A value of { csv, parquet, geoparquet } must be given to DataReaderFactory for type")

        if type.lower() in [ "parquet", "geoparquet" ]:
            return DataReaderFactory.parquet_data_reader
        if type.lower() == "csv":
            return DataReaderFactory.csv_data_reader
        raise TypeError(f"A valid value must be given to DataReaderFactory. Value given : {type} .")