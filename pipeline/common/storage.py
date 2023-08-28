"""Provides clients for reading and writing to file storage."""

import os
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Iterator, Optional

import pandas as pd
import pyarrow.parquet as pq
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from google.cloud import storage


class IDataReader(ABC):
    """Duck-typed interface for reading data from a generic source given a file
    path."""

    @abstractmethod
    def read_csv(
        self,
        file_name: str,
        delimiter: str = ",",
    ) -> Optional[pd.DataFrame]:
        """An abstract method for reading CSV data given its file path.

        Args:
            file_name (str): The path to the file.

        Returns:
            (pd.DataFrame | None): A Pandas DataFrame
                with the file contents or `None`
                if the file does not exist.
        """
        raise NotImplementedError

    @abstractmethod
    def geoparquet_iterator(self, file_name: str, batch_size=1_000) -> Iterator[list[dict[str, Any]]]:
        """Returns an iterator that pulls batches of records from a parquet
        file to be processed until all records in the file have finised."""

        # TODO better documentation
        raise NotImplementedError


class CloudDataReader(IDataReader):
    """A concrete implementation of `IDataReader` that reads files from a
    Google Cloud Storage bucket.

    Behaves like a Singleton.
    """

    def __new__(
        cls,
    ):
        """The class constructor.

        Args:
            cls (type of `CloudDataReader`):
                The class to be instantiated.

        Returns:
            (`CloudDataReader`): An instance of
                the `CloudDataReader`.
        """
        if not hasattr(
            cls,
            "instance",
        ):
            cls.instance = super(
                CloudDataReader,
                cls,
            ).__new__(cls)
        return cls.instance

    def __init__(
        self,
        download_retries: int = 3,
        download_timeout_in_sec: int = 60,
    ) -> None:
        """Initializes the class instance.

        Args:
            download_retries (int): The number
                of times a failed file download
                should be re-attempted before
                raising an `Exception`. Defaults
                to 3.

            download_timeout_in_sec (int): The
                number of seconds to wait for
                a file download operation to
                complete before raising a timeout
                error. Defaults to 60.

        Returns:
            None
        """
        storage_client = storage.Client()
        self.bucket = storage_client.bucket(settings.STORAGE_BUCKET)
        self.download_retries = download_retries
        self.download_timeout_in_sec = download_timeout_in_sec

    def read_csv(
        self,
        file_name: str,
        delimiter: str = ",",
    ) -> pd.DataFrame:
        """Downloads the contents of a CSV file saved in a Google Cloud Storage
        bucket and then uses the contents to create a new Pandas DataFrame.
        Raises a `FileNotFound` exception if the file doesn't exist.

        Args:
            file_name (str): The location of the
                file within the bucket (i.e., the
                object storage key).

        Returns:
            (pd.DataFrame): A Pandas DataFrame
                with the file contents.

        References:
            - https://googleapis.dev/python/storage/latest/buckets.html
            - https://googleapis.dev/python/storage/latest/blobs.html
        """
        # Create reference to file/blob
        blob = self.bucket.blob(file_name)

        # Return if blob doesn't exist
        if not blob.exists():
            raise FileNotFoundError(
                "The requested CSV "
                f"file was not found at '{file_name}' in "
                f"Google Cloud Storage bucket {self.bucket}."
            )

        # Otherwise, download as bytes and read into Pandas DataFrame
        timeout_params = (
            self.download_retries,
            self.download_timeout_in_sec,
        )
        file_bytes = blob.download_as_bytes(timeout=timeout_params)
        return pd.read_table(
            BytesIO(file_bytes),
            encoding="utf-8",
        )

    # TODO implement geoparquet iterator


class LocalDataReader(IDataReader):
    """A concrete implementation of `IDataReader` that reads files from the
    local directory.

    Behaves like a Singleton.
    """

    def __new__(
        cls,
    ):
        """The class constructor.

        Args:
            cls (type of `LocalDataReader`):
                The class to be instantiated.

        Returns:
            (`LocalDataReader`): An instance of the
                `LocalDataReader`.
        """
        if not hasattr(
            cls,
            "instance",
        ):
            cls.instance = super(
                LocalDataReader,
                cls,
            ).__new__(cls)
        return cls.instance

    def read_csv(
        self,
        file_name: str,
        delimiter: str = ",",
    ) -> pd.DataFrame:
        """Reads a local CSV file into a new Pandas DataFrame. Raises a
        `FileNotFound` error if the CSV file does not exist.

        Args:
            file_name (str): The CSV file name.

        Returns:
            (`pd.DataFrame`): A Pandas DataFrame
                with the file contents.
        """
        file_path = settings.DATA_DIR / file_name
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                "The requested local CSV "
                f"file '{file_name}' was not found in the "
                f"expected directory '{settings.DATA_DIR}'."
            )

        return pd.read_csv(
            file_path,
            header=0,
            delimiter=delimiter,
        )

    def geoparquet_iterator(self, file_name: str, batch_size: int=1_000) -> Iterator[list[dict[str, Any]]]:
        file_path = settings.DATA_DIR / file_name

        # Open a parque file for sequential reading
        pf = pq.ParquetFile(file_path)
        try:

            # Capture column names from metadata to reference and note the geometry col
            col_names = pf.schema.names
            geom_col_index = col_names.index('geometry')

            # Iterate over the batches -- parquet file reads return columns, not rows
            batches = pf.iter_batches(batch_size)
            for columns in batches:

                # create an empty array to hold the batch of records
                py_row_batch: list[dict[str, Any]] = []

                # Reorient from columns to rows within the batch
                for arrow_row in zip(*columns):

                    # build the record up -- if it's a normal column, add it to the record; if it's the geometry, convert it to Django type first
                    py_row: dict[str, Any] = {}
                    for idx, r in enumerate(arrow_row):
                        if idx == geom_col_index:
                            py_row['geometry'] = GEOSGeometry(memoryview(r.as_py()))
                        else:
                            py_row[col_names[idx]] = r.as_py()
                    
                    # Add the record to the batch
                    py_row_batch.append(py_row)
                
                # Yield the batch
                yield py_row_batch

        finally:
            # Close the file
            pf.close()


class DataReaderFactory:
    """A factory for creating an `IDataReader` based on the current development
    environment."""

    @staticmethod
    def get_reader() -> IDataReader:
        """Creates a new instance of an `IDataReader` based on the given
        environment.

        Args:
            None

        Returns:
            (`IDataReader`): The concrete reader instance.
        """
        env = os.environ.get(
            "ENV",
            "DEV",
        )
        if env == "DEV":
            return LocalDataReader()
        elif env == "PROD":
            return CloudDataReader()
        else:
            raise Exception(
                "Unable to create a concrete "
                f"IDataReader. The environment is {env} "
                "when 'DEV' or 'PROD' was expected."
            )
