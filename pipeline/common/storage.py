"""Utilities for reading and writing files across data stores.
"""

import csv
import geopandas as gpd
import glob
import io
import json
import os
import pandas as pd
import tempfile
from abc import ABC, abstractmethod
from common.logger import LoggerFactory
from contextlib import contextmanager
from typing import Any, Iterator, Optional

from django.conf import settings
from pyarrow import parquet as pq
from typing import Any, Dict, Iterator, List, Optional


logger = LoggerFactory.get(__name__)

class FileSystemHelper(ABC):
    """Abstract class for accessing file systems.
    """

class FileSystemHelper(ABC):
    @abstractmethod
    def list_contents(self, pathname: Optional[str]=None) -> List[str]:
        """Lists files and directories within 
        the root data bucket defined in settings.

        Args:
            pathname (str): Paths to search for within
                the bucket. Defaults to `None`,
                in which case only files and directories
                directly under the root are listed.

        Returns:
            (list of str): The list of filenames matching
                the pathname in the bucket.
        """
        raise NotImplementedError

    @abstractmethod
    @contextmanager
    def open_file(self, filename: str, mode: str="r") -> Iterator[io.IOBase]:
        """Opens a file with the given name and mode.

        Args:
            filename (str): The file name (i.e., key), representing
                the path to the file within the data bucket
                (e.g., "states.geoparquet").

            mode (str): The file opening method. Defaults to
                reading text ("r").

        Yields:
            (`io.IOBase`): A file object.
        """
        raise NotImplementedError

class LocalFileSystemHelper(FileSystemHelper):
    """Concrete interface for accessing local file systems.
    """

    def list_contents(self, pathname: Optional[str]=None) -> List[str]:
        """Lists files and directories within 
        the root data bucket defined in settings.

        Args:
            pathname (str): Paths to search for within
                the bucket. Defaults to `None`,
                in which case only files and directories
                directly under the root are listed.

        Returns:
            (list of str): The list of filenames matching
                the pathname in the bucket.
        """
        if not pathname:
            fpath = f"{settings.DATA_DIR}/*"
        else:
            fpath = f"{settings.DATA_DIR}/{pathname}"

        return glob.glob(fpath)
    
    @contextmanager
    def open_file(self, filename: str, mode: str="r") -> Iterator[io.IOBase]:
        """Opens a file with the given name and mode.

        Args:
            filename (str): The file name (i.e., key), representing
                the path to the file within the data bucket
                (e.g., "states.geoparquet").

            mode (str): The file opening method. Defaults to
                reading text (i.e., "r").

        Yields:
            (`io.IOBase`): A file object.
        """
        f = open(settings.DATA_DIR / filename, mode)
        try:
            yield f
        finally:
            f.close()

class GoogleCloudStorageHelper(FileSystemHelper):
    """Concrete class for accessing Google Cloud Storage.
    """

    def __init__(self) -> None:
        """Initializes a new instance of a `_CloudFileSystemHelper`.

        Args:
            None

        Returns:
            None
        """
        from google.cloud import storage

        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(settings.CLOUD_STORAGE_BUCKET)

    def list_contents(self, pathname: Optional[str]=None) -> List[str]:
        """Lists files and directories within 
        the root data bucket defined in settings.

        Args:
            pathname (str): Paths to search for within
                the bucket. Defaults to `None`,
                in which case only files and directories
                directly under the root are listed.

        Returns:
            (list of str): The list of filenames matching
                the pathname in the bucket.
        """
        blobs: List[str] = [
            item.name
            for item in 
            self.storage_client.list_blobs(self.bucket, match_glob=pathname)
        ]
        return blobs
    
    @contextmanager
    def open_file(self, filename: str, mode: str='r'):
        """Opens a file with the given name and mode.

        Args:
            filename (str): The file name (i.e., key), representing
                the path to the file within the data bucket
                (e.g., "states.geoparquet").

            mode (str): The file opening method. Defaults to reading
                text (i.e., "r").

        Yields:
            (`io.IOBase`): A file object.
        """
        blob = self.bucket.blob(filename)
        f = blob.open(mode)
        try:
            yield f
        finally:
            f.close()


class FileSystemHelperFactory:
    """Factory for fetching Singleton instance 
    of file system helper based on environment.
    """
    _helper: Optional[FileSystemHelper] = None

    @staticmethod
    def get() -> FileSystemHelper:
        """Fetches a local or cloud-based file system
        helper based on the current name of the
        development environment (e.g., "DEV" or "PROD").

        Args:
            None

        Returns:
            (`FileSystemHelper`)
        """
        if not FileSystemHelperFactory._helper:
            env = os.environ.get("ENV", "DEV")

            if env == "DEV":
                FileSystemHelperFactory._helper = LocalFileSystemHelper()
            elif env == "PROD":
                FileSystemHelperFactory._helper = GoogleCloudStorageHelper()
            else:
                raise RuntimeError(
                    "Unable to instantiate FileSystemHelper. Invalid "
                    f"environment variable passed for 'ENV': {env}."
                )
        return FileSystemHelperFactory._helper

class DataReader(ABC):
    """Abstract class for reading against a data type.
    """

    def __init__(self) -> None:
        """Initializes a new instance of a `DataReader`
        with a `FileSystemHelper` corresponding to
        the current development environment.

        Args:
            `None`

        Returns:
            `None`
        """
        self._file_helper: FileSystemHelper = FileSystemHelperFactory.get()

    @abstractmethod
    def col_names(self, filename: str, **kwargs) -> List[str]:
        """An abstract method for listing column names.
        Raises an exception if not implemented by subclasses.

        Args:
            filename (str): The path to the file.

            **kwargs: Additional keywords passed to the
                reader library used by the concrete instance.

        Returns:
            (list of str): The names.
        """
        raise NotImplementedError

    @abstractmethod
    def iterate(self, filename: str, **kwargs) -> Iterator[Dict[str, Any]]:
        """An abstract method for opening a file and then
        returning a generator that yields one row at a time.

         Args:
            filename (str): The path to the file.

            **kwargs: Additional keywords passed to the
                reader library used by the concrete instance.

        Yields:
            (list of dict): The rows.
        """
        raise NotImplementedError
    
    def get_data_bucket_contents(
        self, 
        pathname: Optional[str]=None) -> List[str]:
        """Lists files and directories within 
        the root data bucket defined in settings.

        Args:
            pathname (str): Paths to search for within
                the bucket. Defaults to `None`,
                in which case only files and directories
                directly under the root are listed.

        Returns:
            (list of str): The list of filenames matching
                the pathname in the bucket.
        """
        return self._file_helper.list_contents(pathname)

class CsvDataReader(DataReader):
    """A data reader for CSV files.
    """

    def col_names(self, filename: str, **kwargs) -> List[str]:
        """Opens the CSV file and then returns its columns.
        
        Args:
            filename (str): The path to the file.

            **kwargs: Additional keywords passed to the underlying
                Python standard library's `csv.DictReader` constructor
                (e.g., "delimiter").

        Returns:
            (list of str): The column names.
        """
        # Set default value for delimiter if not specified by keyword arguments
        try:
            delimiter = kwargs.pop("delimiter")
        except KeyError:
            delimiter = "|"

        # Open file and read field names
        with self._file_helper.open_file(filename) as f:
            reader = csv.DictReader(f, delimiter=delimiter, **kwargs)
            return reader.fieldnames

    def iterate(self, filename: str, **kwargs) -> Iterator[Dict[str, Any]]:
        """Reads the CSV file and then returns a 
        generator yielding one row at a time.

         Args:
            filename (str): The path to the file.

            **kwargs: Additional keywords passed to the underlying
                Python standard library `csv.DictReader` constructor.

        Yields:
            (list of dict): The rows.
        """
        # Set default value for delimiter if not specified by keyword arguments
        try:
            delimiter = kwargs.pop("delimiter")
        except KeyError:
            delimiter = "|"

        # Open file and return generator for rows
        with self._file_helper.open_file(filename) as f:
            reader = csv.DictReader(f, delimiter=delimiter, **kwargs)
            for row in reader:
                yield row

class ParquetDataReader(DataReader):
    """A reader for Parquet files. For more information, please see the 
    [PyArrow documentation](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetFile.html).
    """

    def col_names(self, filename: str, **kwargs) -> List[str]:
        """Reads the Parquet file and then returns its columns.
        
        Args:
            filename (str): The path to the file.

            **kwargs: Additional keywords passed to the underlying
                pyarrow `ParquetFile` constructor.

        Returns:
            (list of str): The column names.
        """
        with self._file_helper.open_file(filename, mode='rb') as f:
            pf: pq.ParquetFile = pq.ParquetFile(f, **kwargs)
            try:
                return [c.name for c in pf.schema]
            finally:
                pf.close()

    def iterate(self, filename: str, **kwargs) -> Iterator[Dict[str, Any]]:
        """Reads the Parquet file and then returns a 
        generator yielding one row at a time.

         Args:
            filename (str): The path to the file.

            **kwargs: Additional keywords passed to the underlying
                pyarrow `ParquetFile` constructor.

        Yields:
            (list of dict): The GeoJSON features.
        """
        with self._file_helper.open_file(filename, mode='rb') as f:
            pf = pq.ParquetFile(f, **kwargs)
            pf_iter = pf.iter_batches(settings.PQ_CHUNK_SIZE)
            for batch in pf_iter:
                row_list = batch.to_pylist()
                for row in row_list:
                    yield row


class DataReaderFactory:
    csv_data_reader = CsvDataReader()
    parquet_data_reader = ParquetDataReader()

    @staticmethod
    def get(type: str) -> DataReader:
        if not type:
            raise TypeError(
                "A value of { csv, parquet, geoparquet } must be given to DataReaderFactory for type"
            )

        if type.lower() in ["parquet", "geoparquet"]:
            return DataReaderFactory.parquet_data_reader
        if type.lower() == "csv":
            return DataReaderFactory.csv_data_reader
        raise TypeError(f"A valid value must be given to DataReaderFactory. Value given : {type} .")

class DataFrameReader:
    """Base class for reading GeoDataFrames from data stores.
    """

    def __init__(self) -> None:
        """Initializes a new instance of a `DataWriter`.
        Maintains a reference to a `FileSystemHelper`
        that reads and writes to and from either
        Google Cloud or the local file system.

        Args:
            None

        Returns:
            None
        """
        self._file_helper = FileSystemHelperFactory.get()

    def get_data_bucket_contents(
        self, 
        pathname: Optional[str]=None) -> List[str]:
        """Lists files and directories within 
        the root data bucket defined in settings.

        Args:
            pathname (str): Paths to search for within
                the bucket. Defaults to `None`,
                in which case only files and directories
                directly under the root are listed.

        Returns:
            (list of str): The list of filenames matching
                the pathname in the bucket.
        """
        return self._file_helper.list_contents(pathname)

    def read_csv(self, filename: str, **kwargs) -> pd.DataFrame:
        """Reads a CSV file into a Pandas DataFrame.

        References:
        - https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

        Args:
            filename (str): The path to the file.

            **kwargs: Additional keywords to pass to the 
                underlying `pandas.read_csv` method.

        Returns:
            (`pd.DataFrame`): The `DataFrame`.
        """
        with self._file_helper.open_file(filename, mode='rb') as f:
            return pd.read_csv(f, **kwargs)
        
    def read_excel(self, filename: str, **kwargs) -> pd.DataFrame:
        """Reads a Microsoft Excel file into a Pandas DataFrame.

        References:
        - https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html

        Args:
            filename (str): The path to the file.

            **kwargs: Additional keywords to pass to the 
                underlying `pandas.read_excel` method.

        Returns:
            (`pd.DataFrame`): The `DataFrame`.
        """
        with self._file_helper.open_file(filename, mode='rb') as f:
            return pd.read_excel(f, **kwargs)

    def read_parquet(self, filename: str, **kwargs) -> gpd.GeoDataFrame:
        """Reads an Apache Parquet file into a Geopandas GeoDataFrame.

        References:
        - https://geopandas.org/en/stable/docs/reference/api/geopandas.read_parquet.html

        Args:
            filename (str): The path to the file.

            **kwargs: Additional keywords to pass to the 
                underlying `geopandas.read_parquet` method.

        Returns:
            (`gpd.DataFrame`): The `GeoDataFrame`.
        """
        with self._file_helper.open_file(filename, mode='rb') as f:
            return gpd.read_parquet(f, **kwargs)
        
    def read_shapefile(
        self, 
        filename: str, 
        zip_file_path: str=None, 
        **kwargs) -> gpd.GeoDataFrame:
        """Reads a Shapefile into a Geopandas GeoDataFrame.

        References:
        - https://geopandas.org/en/stable/docs/reference/api/geopandas.read_file.html

        Args:
            filename (str): The path to the file.

            zip_file_path (str): The path to the dataset
                within the shapefile if the shapefile
                is zipped. Defaults to `None`.

            **kwargs: Additional keywords to pass to the 
                underlying `geopandas.read_file` method.

        Returns:
            (`gpd.DataFrame`): The `GeoDataFrame`.
        """
        # Instantiate GeoDataFrame directly from file-like object
        # if there is no need to reference subdirectories of a zipfile
        if not zip_file_path:
            with self._file_helper.open_file(filename, mode='rb') as f:
                return gpd.read_file(f, engine="pyogrio")
        
        # Otherwise, create temp directory
        with tempfile.TemporaryDirectory() as temp_dir:

            # Open new file in directory and transfer contents of remote zipfile
            tmp_fpath = f"{temp_dir}/tmp.zip"
            with open(tmp_fpath, "wb") as tmp:
                with self._file_helper.open_file(filename, mode='rb') as f:
                    tmp.write(f.read())

            # Read the zipped datset as GeoDataFrame
            data_fpath = f"{tmp_fpath}!{zip_file_path}"
            return gpd.read_file(data_fpath, engine="pyogrio")

class DataFrameWriter:
    """Base class for writing GeoDataFrames to data stores.
    """

    def __init__(self) -> None:
        """Initializes a new instance of a `DataWriter`.
        Maintains a reference to a `FileSystemHelper`
        that reads and writes to and from either
        Google Cloud or the local file system.

        Args:
            None

        Returns:
            None
        """
        self._file_helper = FileSystemHelperFactory.get()
            
    def write_geojsonl(
        self,
        filename: str,
        data: gpd.GeoDataFrame,
        index: bool=False) -> None:
        """Writes a line-delimited GeoJSON file to the data bucket
        configured in settings.

        Args:
            filename (str): The file name/key in the bucket.
            
            data (`gpd.GeoDataFrame`): The data.

            index (bool): Boolean indicating whether the index
                should be kept in the output GeoJSON lines.

        Returns:
            None
        """
        counter = 0
        num_features = len(data)
        obj_key = f"{settings.GEOJSONL_DIRECTORY}/{filename}"
        with self._file_helper.open_file(obj_key, mode="w") as f:
            for row in data.iterfeatures(drop_id=True):
                f.write(json.dumps(row))
                counter += 1
                if counter != num_features:
                    f.write("\n")

    def write_geoparquet(
        self,
        filename: str,
        data: gpd.GeoDataFrame,
        index: bool=False) -> None:
        """Writes a geoparquet file to the data bucket
        configured in settings.

        Args:
            filename (str): The file name/key in the bucket.

            data (`gpd.GeoDataFrame`): The data.

            index (bool): Boolean indicating whether the
                GeoDataFrame index should be kept in the
                output geoparquet file.

        Returns:
            None
        """
        obj_key = f"{settings.GEOPARQUET_DIRECTORY}/{filename}"
        with self._file_helper.open_file(obj_key, mode="wb") as f:
            data.to_parquet(f, index=index)
