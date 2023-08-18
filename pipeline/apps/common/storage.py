"""Provides clients for reading and writing to file storage.
"""

import os
import pandas as pd
from abc import ABC, abstractmethod
from django.conf import settings
from google.cloud import storage
from io import BytesIO
from typing import Union


class IDataReader(ABC):
    """Duck-typed interface for reading data
    from a generic source given a file path.
    """

    @abstractmethod
    def read_csv(self, file_name: str) -> Union[None, pd.DataFrame]:
        """An abstract method for reading CSV data
        given its file path.

        Args:
            file_name (str): The path to the file.

        Returns:
            (pd.DataFrame | None): A Pandas DataFrame
                with the file contents or `None`
                if the file does not exist.
        """
        raise NotImplementedError


class CloudDataReader(IDataReader):
    """A concrete implementation of `IDataReader` that
    reads files from a Google Cloud Storage bucket.
    Behaves like a Singleton.
    """

    def __new__(cls):
        """The class constructor.

        Args:
            cls (type of `CloudDataReader`):
                The class to be instantiated.

        Returns:
            (`CloudDataReader`): An instance of
                the `CloudDataReader`.
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(CloudDataReader, cls).__new__(cls)
        return cls.instance


    def __init__(
        self,
        download_retries: int = 3,
        download_timeout_in_sec: int=60) -> None:
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


    def read_csv(self, file_name: str) -> pd.DataFrame:
        """Downloads the contents of a CSV file saved in
        a Google Cloud Storage bucket and then uses
        the contents to create a new Pandas DataFrame.
        Raises a `FileNotFound` exception if the file
        doesn't exist.

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
            raise FileNotFoundError("The requested CSV "
                f"file was not found at '{file_name}' in " 
                f"Google Cloud Storage bucket {self.bucket_name}.")

        # Otherwise, download as bytes and read into Pandas DataFrame
        timeout_params = (self.download_retries, self.download_timeout_in_sec)
        file_bytes = blob.download_as_bytes(timeout=timeout_params)
        return pd.read_table(BytesIO(file_bytes), encoding='utf-8')


class LocalDataReader(IDataReader):
    """A concrete implementation of `IDataReader`
    that reads files from the local directory.
    Behaves like a Singleton.
    """
    
    def __new__(cls):
        """The class constructor.

        Args:
            cls (type of `LocalDataReader`):
                The class to be instantiated.

        Returns:
            (`LocalDataReader`): An instance of the
                `LocalDataReader`.
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(LocalDataReader, cls).__new__(cls)
        return cls.instance


    def read_csv(self, file_name: str) -> pd.DataFrame:
        """Reads a local CSV file into a new Pandas DataFrame.
        Raises a `FileNotFound` error if the CSV file does
        not exist.

        Args:
            file_name (str): The CSV file name.

        Returns:
            (`pd.DataFrame`): A Pandas DataFrame
                with the file contents.
        """
        file_path = f"{settings.DATA_DIR}/{file_name}"
        if not os.path.exists(file_path):
             raise FileNotFoundError("The requested local CSV "
                f"file '{file_name}' was not found in the "
                f"expected directory '{settings.DATA_DIR}'.")

        return pd.read_csv(file_path)


class IDataReaderFactory():
    """A factory for creating an `IDataReader` based
    on the current development environment.
    """

    def get_reader(self) -> IDataReader:
        """Creates a new instance of an `IDataReader`
        based on the given environment.

        Args:
            None

        Returns:
            (`IDataReader`): The concrete reader instance.
        """
        env = os.environ.get('ENV', 'DEV')
        if env == 'DEV':
            return LocalDataReader()
        elif env == 'PROD':
            return CloudDataReader()
        else:
            raise Exception("Unable to create a concrete "
                f"IDataReader. The environment is {env} "
                "when 'DEV' or 'PROD' was expected.")
