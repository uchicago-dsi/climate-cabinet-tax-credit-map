"""Utilities for reading and writing files across data stores.
"""

# Standard library imports
import csv
import glob
import io
import json
import os
import tempfile
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union
from zipfile import BadZipFile, ZipFile

# Third-party imports
import geopandas as gpd
import pandas as pd
from django.conf import settings
from pyarrow import parquet as pq


class IFileStrategy(ABC):
    """An abstract strategy for yielding the contents of a file."""

    def execute(self, fpath: Path, mode: str, **kwargs) -> io.IOBase:
        """Executes the strategy.

        Args:
            fpath (`str`): The absolute path to the file.

            mode (`str`): The file opening method.

        Yields:
            (`io.IOBase`): A file object.
        """
        raise NotImplementedError


class UnzippedFileStrategy(IFileStrategy):
    """A strategy for yielding the contents of an unzipped file."""

    def execute(self, fpath: Path, mode: str, **kwargs) -> Iterator[io.IOBase]:
        """Executes the strategy.

        Args:
            fpath (`str`): The absolute path to the file.

            mode (`str`): The file opening method.

        Yields:
            (`io.IOBase`): A file object.
        """
        # Detect UTF-8 BOM encoding if applicable
        try:
            with open(fpath, "rb") as f:
                first_bytes = f.read(3)
            encoding = "utf-8-sig" if first_bytes == b"\xef\xbb\xbf" else None
        except FileNotFoundError:
            encoding = None

        # Open file
        f = open(fpath, mode, encoding=encoding)

        # Yield file
        try:
            yield f
        finally:
            f.close()


class ZippedFileStrategy(IFileStrategy):
    """A strategy for yielding the contents of a zipped file."""

    def execute(self, fpath: Path, mode: str, **kwargs) -> Iterator[io.IOBase]:
        """Executes the strategy.

        Args:
            fpath (`str`): The absolute path to the file.

            mode (`str`): The file opening method.

        Yields:
            (`io.IOBase`): A file object.
        """
        # Parse keyword arguments
        try:
            zip_file_path = kwargs["zip_file_path"]
        except KeyError:
            raise RuntimeError(
                'Expected a keyword argument of type "str", "zip_file_path".'
            )

        # Detect UTF-8 BOM encoding if applicable
        try:
            with ZipFile(fpath, "r") as zip_file:
                with zip_file.open(zip_file_path, "r") as f:
                    first_bytes = f.read(3)
            encoding = "utf-8-sig" if first_bytes == b"\xef\xbb\xbf" else None
        except (FileNotFoundError, BadZipFile):
            encoding = None

        # Open file
        zip_file = ZipFile(fpath, mode)
        f = zip_file.open(zip_file_path, mode, encoding)

        # Yield file
        try:
            yield f
        finally:
            f.close()
            zip_file.close()


class FileSystemHelper(ABC):
    """Abstract class for accessing file systems."""

    @abstractmethod
    def list_contents(
        self,
        root_dir: Union[Path, str] = settings.DATA_DIR,
        glob_pattern: str = "**/**?",
    ) -> List[str]:
        """Recursively lists absolute paths to all files
        under the given root directory, with the option of
        filtering the paths using a glob pattern. Directories
        are ignored.

        References:
        - [glob — Unix style pathname pattern expansion](https://docs.python.org/3.11/library/glob.html)

        Args:
            root_dir (`pathlib.Path` | `str`): The absolute path to
                the parent/top-most directory of the file
                system. Defaults to the data directory
                defined in the Django settings module that
                corresponds to the current development environment.

            glob_pattern (`str`): A relative path to search
                for within the root directory. May contain
                shell-like wildcards. Defaults to `**/**?`, in
                which case all files under the root directory
                and its nested subdirectories are listed.

        Returns:
            (`list` of `str`): The list of absolute file paths
                matching the glob pattern within the directory.
        """
        raise NotImplementedError

    @abstractmethod
    @contextmanager
    def open_file(
        self,
        file_name: str,
        root_dir: Union[Path, str] = settings.DATA_DIR,
        mode: str = "r",
        zip_file_path: Optional[str] = None,
    ) -> Iterator[io.IOBase]:
        """Opens a file with the given name and mode.

        Args:
            file_name (`str`): The file name, representing the
                relative path to the file within the root directory.

            root_dir (`pathlib.Path` | `str`): The designated
                parent/top-most directory of the file system.
                Defaults to the data directory defined in the
                Django settings module that corresponds to
                the current development environment.

            mode (`str`): The file opening method. Defaults to
                reading text ("r").

            zip_file_path (`str`): If applicable, the path to the
                extracted file to read once the larger file is
                unzipped. Defaults to `None`, which assumes that
                the argument `filename` does not refer to a ZIP file.

        Yields:
            (`io.IOBase`): A file object.
        """
        raise NotImplementedError


class LocalFileSystemHelper(FileSystemHelper):
    """Concrete class for accessing local file systems."""

    def list_contents(
        self,
        root_dir: Union[Path, str] = settings.DATA_DIR,
        glob_pattern: str = "**/**?",
    ) -> List[str]:
        """Recursively lists relative paths to all files
        under the given root directory, with the option of
        filtering the paths using a glob pattern. Directories
        are ignored regardless of the pattern.

        References:
        - [glob — Unix style pathname pattern expansion](https://docs.python.org/3.11/library/glob.html)

        Args:
            root_dir (`pathlib.Path` | `str`): The absolute path to
                the parent/top-most directory of the file
                system. Defaults to the data directory
                defined in the Django settings module that
                corresponds to the current development environment.

            glob_pattern (`str`): A relative path to search
                for within the root directory. May contain
                shell-like wildcards. Defaults to `**/**?`, in
                which case all files under the root and any
                of its nested subdirectories are listed.

        Returns:
            (`list` of `str`): The list of relative file paths
                matching the glob pattern within the directory.
        """
        out = []
        for pth in glob.glob(glob_pattern, root_dir=root_dir, recursive=True):
            full_pth = Path(root_dir) / pth
            if os.path.isfile(full_pth):
                out.append(pth)
        return out

    @contextmanager
    def open_file(
        self,
        file_name: str,
        root_dir: Union[Path, str] = settings.DATA_DIR,
        mode: str = "r",
        zip_file_path: Optional[str] = None,
    ) -> Iterator[io.IOBase]:
        """Opens a file with the given name and mode.

        Args:
            file_name (`str`): The file name, representing the
                the relative path to the file within the root
                directory.

            root_dir (`pathlib.Path` | `str`): The absolute path to
                the parent/top-most directory of the file
                system. Defaults to the data directory
                defined in the Django settings module that
                corresponds to the current development environment.

            mode (`str`): The file opening method. Defaults to
                reading text ("r").

            zip_file_path (`str`): If applicable, the path to the
                extracted file to read once the larger file is
                unzipped. Defaults to `None`, which assumes that
                the argument `filename` does not refer to a ZIP file.

        Yields:
            (`io.IOBase`): A file object.
        """
        # Resolve file path
        fpath = Path(root_dir) / file_name

        # Create file's parent directories if writing
        if not fpath.exists():
            Path(fpath).parent.mkdir(parents=True, exist_ok=True)

        # Determine strategy necessary to yield file contents
        file_strategy: IFileStrategy = (
            ZippedFileStrategy()
            if zip_file_path is not None
            else UnzippedFileStrategy()
        )

        # Execute strategy, returning file iterator
        return file_strategy.execute(fpath, mode, zip_file_path=zip_file_path)


class GoogleCloudStorageHelper(FileSystemHelper):
    """Concrete class for accessing Google Cloud Storage."""

    def __init__(self) -> None:
        """Initializes a new instance of a `GoogleCloudStorageHelper`.

        Args:
            `None`

        Returns:
            `None`
        """
        from google.cloud import storage

        self.storage_client = storage.Client()

    def list_contents(
        self,
        root_dir: Union[Path, str] = settings.CLOUD_STORAGE_BUCKET,
        glob_pattern: str = "**/**?",
    ) -> List[str]:
        """Lists relative paths to all blobs within the given
        bucket, with the option of filtering the blobs using
        a glob pattern. Directories (i.e., prefixes) are ignored.

        References:
        - [Cloud Storage Documentation | "Class Client (2.14.0)"](https://cloud.google.com/python/docs/reference/storage/latest/google.cloud.storage.client.Client#google_cloud_storage_client_Client_list_blobs)
        - [Cloud Storage Documentation | "Class Blob (2.14.0)"](https://cloud.google.com/python/docs/reference/storage/latest/google.cloud.storage.blob.Blob)
        - [Cloud Storage Documentation | "List objects and prefixes using glob"](https://cloud.google.com/storage/docs/json_api/v1/objects/list#list-objects-and-prefixes-using-glob)
        - [google-api-core | "Page Iterators"](https://googleapis.dev/python/google-api-core/latest/page_iterator.html)

        Args:
            root_dir (`pathlib.Path` | `str`): The cloud
                storage bucket name. Defaults to the bucket
                defined in the Django settings module.

            glob_pattern (`str`): A relative path to search
                for within the bucket. May contain shell-like
                wildcards. Defaults to `**?`, in which case
                all blobs wihin the bucket are listed.

        Returns:
            (`list` of `str`): The list of relative file paths
                matching the glob pattern within the bucket.
        """
        # Create reference to storage bucket
        bucket = self.storage_client.bucket(root_dir)

        # Return object keys for blobs
        try:
            return [
                item.name
                for item in self.storage_client.list_blobs(
                    bucket, match_glob=glob_pattern
                )
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to list blobs in storage bucket. {e}") from None

    @contextmanager
    def open_file(
        self,
        file_name: str,
        root_dir: Union[Path, str] = settings.DATA_DIR,
        mode: str = "r",
        zip_file_path: Optional[str] = None,
    ) -> Iterator[io.IOBase]:
        """Opens a file with the given name and mode.

        References:
        - [Cloud Storage Documentation | "Module fileio (2.14.0)"](https://cloud.google.com/python/docs/reference/storage/latest/google.cloud.storage.fileio)

        Args:
            file_name (`str`): The file/blob name, representing the
                the relative path to the blob within the bucket.

            root_dir (`pathlib.Path` | `str`): The cloud
                storage bucket name. Defaults to the bucket
                defined in the Django settings module.

            mode (`str`): The file opening method. Defaults to
                reading text ("r").

            zip_file_path (`str`): If applicable, the path to the
                extracted file to read once the larger file is
                unzipped. Defaults to `None`, which assumes that
                the argument `filename` does not refer to a ZIP file.

        Yields:
            (`io.IOBase`): A file object.
        """
        # Create reference to blob
        bucket = self.storage_client.bucket(root_dir)
        blob = bucket.blob(file_name)

        # Determine strategy necessary to yield file contents
        file_strategy: IFileStrategy = (
            ZippedFileStrategy()
            if zip_file_path is not None
            else UnzippedFileStrategy()
        )

        # Open temporary file on disk
        tf = tempfile.NamedTemporaryFile(delete=False)

        # Download contents if reading
        if mode.startswith("r"):
            blob.download_to_filename(tf.name)

        # Execute file strategy
        try:
            yield from file_strategy.execute(tf.name, mode, zip_file_path=zip_file_path)
        finally:
            if not mode.startswith("r"):
                blob.upload_from_file(tf)
            tf.close()
            os.remove(tf.name)


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
            `None`

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


class IterativeDataReader(ABC):
    """Abstract class for iteratively reading against a data type."""

    def __init__(self, root_dir: Union[Path, str] = settings.DATA_DIR) -> None:
        """Initializes a new instance of an `IterativeDataReader`
        with a `FileSystemHelper` corresponding to the current
        development environment.

        Args:
            root_dir (`pathlib.Path` | `str`): The absolute path to
                the parent/top-most directory of the file
                system. Defaults to the data directory
                defined in the Django settings module that
                corresponds to the current development environment.

        Returns:
            `None`
        """
        self._root_dir = root_dir
        self._file_helper = FileSystemHelperFactory.get()

    @abstractmethod
    def col_names(self, file_name: str, **kwargs) -> List[str]:
        """An abstract method for listing column names.
        Raises an exception if not implemented by subclasses.

        Args:
            file_name (`str`): The relative path to the file
                within the root directory.

            **kwargs: Additional keywords passed to the
                reader library used by the concrete instance.

        Returns:
            (`list` of `str`): The names.
        """
        raise NotImplementedError

    @abstractmethod
    def iterate(self, file_name: str, **kwargs) -> Iterator[Dict[str, Any]]:
        """An abstract method for opening a file and then
        returning a generator that yields one row at a time.
        Raises an exception if not implemented by subclasses.

         Args:
            file_name (`str`): The relative path to the file
                within the root directory.

            **kwargs: Additional keywords passed to the
                reader library used by the concrete instance.

        Yields:
            (`list` of `dict`): The rows.
        """
        raise NotImplementedError

    def get_data_bucket_contents(self, glob_pattern: str = "**/**?") -> List[str]:
        """Lists files and directories within
        the root data bucket defined in settings.

        Args:
            glob_pattern (`str`): A relative path to search
                for within the root directory. May contain
                shell-like wildcards. Defaults to `**?`, in
                which case all files under the root are listed.

        Returns:
            (`list` of `str`): The list of filenames matching
                the pathname in the bucket.
        """
        return self._file_helper.list_contents(self._root_dir, glob_pattern)


class CsvDataReader(IterativeDataReader):
    """An iterative data reader for CSV files."""

    def col_names(self, file_name: str, **kwargs) -> List[str]:
        """Opens the CSV file and then returns its columns.

        Args:
            file_name (`str`): The relative path to the file
                within the root directory.

            **kwargs: Additional keywords passed to the underlying
                Python standard library's `csv.DictReader` constructor
                (e.g., "delimiter").

        Returns:
            (`list` of `str`): The column names.
        """
        # Set default value for delimiter if not specified by keyword arguments
        try:
            delimiter = kwargs.pop("delimiter")
        except KeyError:
            delimiter = "|"

        # Open file and read field names
        with self._file_helper.open_file(file_name, self._root_dir) as f:
            reader = csv.DictReader(f, delimiter=delimiter, **kwargs)
            return reader.fieldnames

    def iterate(self, file_name: str, **kwargs) -> Iterator[Dict[str, Any]]:
        """Reads the CSV file and then returns a
        generator yielding one row at a time.

         Args:
            file_name (`str`): The relative path to the file
                within the root directory.

            **kwargs: Additional keywords passed to the underlying
                Python standard library `csv.DictReader` constructor
                (e.g., "delimiter").

        Yields:
            (`list` of `dict`): The rows.
        """
        # Set default value for delimiter if not specified by keyword arguments
        try:
            delimiter = kwargs.pop("delimiter")
        except KeyError:
            delimiter = "|"

        # Open file and return generator for rows
        with self._file_helper.open_file(file_name, self._root_dir) as f:
            reader = csv.DictReader(f, delimiter=delimiter, **kwargs)
            for row in reader:
                yield row


class ParquetDataReader(IterativeDataReader):
    """An iterative reader for Parquet files. For more information, please see the
    [PyArrow documentation](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetFile.html).
    """

    def col_names(self, file_name: str, **kwargs) -> List[str]:
        """Reads the Parquet file and then returns its columns.

        Args:
            file_name (`str`): The relative path to the file
                within the root directory.

            **kwargs: Additional keywords passed to the underlying
                pyarrow `ParquetFile` constructor.

        Returns:
            (`list` of `str`): The column names.
        """
        with self._file_helper.open_file(file_name, self._root_dir, mode="rb") as f:
            pf: pq.ParquetFile = pq.ParquetFile(f)
            try:
                return [c.name for c in pf.schema]
            finally:
                pf.close()

    def iterate(self, file_name: str, **kwargs) -> Iterator[Dict[str, Any]]:
        """Reads the Parquet file and then returns a
        generator yielding one row at a time.

         Args:
            file_name (`str`): The relative path to the file
                within the root directory.

            **kwargs: Additional keywords passed to the underlying
                pyarrow `ParquetFile` constructor.

        Yields:
            (`list` of `dict`): The GeoJSON features.
        """
        with self._file_helper.open_file(file_name, self._root_dir, mode="rb") as f:
            pf = pq.ParquetFile(f)
            pf_iter = pf.iter_batches(settings.PQ_CHUNK_SIZE)
            for batch in pf_iter:
                row_list = batch.to_pylist()
                for row in row_list:
                    yield row


class IterativeDataReaderFactory:
    """A factory for returning concrete `IterativeDataReader` instances."""

    @staticmethod
    def get(
        type: str, root_dir: Union[Path, str] = settings.DATA_DIR
    ) -> IterativeDataReader:
        """Fetches an `IterativeDataReader` by type name.

        Args:
            type (`str`): The type of reader to return. Must
                be one of "csv", "parquet", or "geoparquet".

            root_dir (`pathlib.Path` | `str`): The absolute path to
                the parent/top-most directory of the file
                system. Defaults to the data directory
                defined in the Django settings module that
                corresponds to the current development environment.

        Raises:
            - `TypeError` if the argument `type` is not a string.
            - `ValueError` if the argument `type` is not one of the expected values.

        Returns:
            (`IterativeDataReader`): The data reader.
        """
        if not type:
            raise TypeError(
                'A value of "csv", "parquet", or "geoparquet" must be '
                'given to IterativeDataReaderFactory for "type".'
            )
        elif type.lower() in ["parquet", "geoparquet"]:
            return ParquetDataReader(root_dir)
        elif type.lower() == "csv":
            return CsvDataReader(root_dir)
        else:
            raise ValueError(
                "A valid value must be given to IterativeDataReaderFactory. "
                f'Value given: "{type}".'
            )


class DataLoader:
    """Loads entire file contents from data stores into Python objects."""

    def __init__(self, root_dir: Union[Path, str] = settings.DATA_DIR) -> None:
        """Initializes a new instance of a `DataLoader`.
        Maintains a reference to a `FileSystemHelper` that
        reads from either Google Cloud or the local file
        system based on the current development environment.

        Args:
            root_dir (`pathlib.Path` | `str`): The absolute path to
                the parent/top-most directory of the file
                system. Defaults to the data directory
                defined in the Django settings module that
                corresponds to the current development environment.

        Returns:
            `None`
        """
        self._root_dir = root_dir
        self._file_helper = FileSystemHelperFactory.get()

    def list_directory_contents(self, glob_pattern: str = "**/**?") -> List[str]:
        """Recursively lists all files within the root directory.

        Args:
           glob_pattern (`str`): A relative path to search
                for within the directory for the purpose of
                filtering results. May contain shell-like
                wildcards. Defaults to `**/**?`, in which case
                all files under the directory and its nested
                subdirectories are listed.

        Returns:
            (`list` of `str`): The list of file names matching
                the glob pattern in the directory.
        """
        return self._file_helper.list_contents(self._root_dir, glob_pattern)

    def read_csv(
        self,
        file_name: str,
        zip_file_path: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Reads a CSV file into a Pandas DataFrame.

        References:
        - https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

        Args:
            file_name (`str`): The relative path to the file
                within the root directory.

            zip_file_path (`str`): The path to the CSV file
                within a zip folder, if applicable. Defaults
                to `None`.

            **kwargs: Additional keywords to pass to the
                underlying `pandas.read_csv` method.

        Returns:
            (`pd.DataFrame`): The `DataFrame`.
        """
        mode = "r" if zip_file_path else "rb"
        with self._file_helper.open_file(
            file_name, self._root_dir, mode, zip_file_path
        ) as f:
            return pd.read_csv(f, **kwargs)

    def read_excel(
        self,
        file_name: str,
        zip_file_path: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Loads a Microsoft Excel file into a Pandas DataFrame.

        References:
        - https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html

        Args:
            file_name (`str`): The relative path to the file
                within the root directory.

            zip_file_path (`str`): The path to the Excel file
                within a zip folder, if applicable. Defaults
                to `None`.

            **kwargs: Additional keywords to pass to the
                underlying `pandas.read_excel` method.

        Returns:
            (`pd.DataFrame`): The `DataFrame`.
        """
        mode = "r" if zip_file_path else "rb"
        with self._file_helper.open_file(
            file_name, self._root_dir, mode, zip_file_path
        ) as f:
            return pd.read_excel(f, **kwargs)

    def read_json(
        self,
        file_name: str,
        zip_file_path: Optional[str] = None,
        **kwargs,
    ) -> Dict:
        """Loads a JSON file as a Python dictionary.

        Args:
            file_name (`str`): The relative path to the file
                within the root directory.

            zip_file_path (`str`): The path to the JSON file
                within a zip folder, if applicable. Defaults
                to `None`.

            **kwargs: Additional keywords to pass to the
                underlying `json.load` method.

        Returns:
            (`Dict`): The dictionary.
        """
        mode = "r" if zip_file_path else "rb"
        with self._file_helper.open_file(
            file_name, self._root_dir, mode, zip_file_path
        ) as f:
            return json.load(f, **kwargs)

    def read_parquet(
        self,
        file_name: str,
        zip_file_path: Optional[str] = None,
        **kwargs,
    ) -> gpd.GeoDataFrame:
        """Loads an Apache Parquet file into a Geopandas GeoDataFrame.

        References:
        - https://geopandas.org/en/stable/docs/reference/api/geopandas.read_parquet.html

        Args:
            file_name (`str`): The relative path to the file
                within the root directory.

            zip_file_path (`str`): The path to the Parquet file
                within a zip folder, if applicable. Defaults
                to `None`.

            **kwargs: Additional keywords to pass to the
                underlying `geopandas.read_parquet` method.

        Returns:
            (`gpd.DataFrame`): The `GeoDataFrame`.
        """
        mode = "r" if zip_file_path else "rb"
        with self._file_helper.open_file(
            file_name, self._root_dir, mode, zip_file_path
        ) as f:
            return gpd.read_parquet(f, **kwargs)

    def read_shapefile(
        self,
        file_name: str,
        zip_file_path: Optional[str] = None,
        **kwargs,
    ) -> gpd.GeoDataFrame:
        """Loads a Shapefile into a Geopandas GeoDataFrame.

        References:
        - https://geopandas.org/en/stable/docs/reference/api/geopandas.read_file.html

        Args:
            file_name (`str`): The relative path to the file
                within the root directory.

            zip_file_path (`str`): The path to the Shapefile
                within a zip folder, if applicable. Defaults
                to `None`.

            **kwargs: Additional keywords to pass to the
                underlying `geopandas.read_file` method.

        Returns:
            (`gpd.DataFrame`): The `GeoDataFrame`.
        """
        # Instantiate GeoDataFrame directly from file-like object
        # if there is no need to reference subdirectories of a zipfile
        if not zip_file_path:
            with self._file_helper.open_file(file_name, self._root_dir, mode="rb") as f:
                return gpd.read_file(f, engine="pyogrio")

        # Otherwise, create temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Open new file in directory and transfer contents of remote zipfile
            tmp_fpath = f"{temp_dir}/tmp.zip"
            with open(tmp_fpath, "wb") as tmp:
                with self._file_helper.open_file(
                    file_name, self._root_dir, mode="rb"
                ) as f:
                    tmp.write(f.read())

            # Read the zipped dataset as GeoDataFrame
            data_fpath = f"{tmp_fpath}!{zip_file_path}"
            return gpd.read_file(data_fpath, engine="pyogrio")


class DataWriter:
    """Writes Python objects to data stores."""

    def __init__(self, root_dir: Union[Path, str] = settings.DATA_DIR) -> None:
        """Initializes a new instance of a `DataWriter`.
        Maintains a reference to a `FileSystemHelper`
        that writes to either Google Cloud or the local file
        system based on the current development environment.

        Args:
            root_dir (`pathlib.Path` | `str`): The absolute path to
                the parent/top-most directory of the file
                system. Defaults to the data directory
                defined in the Django settings module that
                corresponds to the current development environment.

        Returns:
            `None`
        """
        self._root_dir = root_dir
        self._file_helper = FileSystemHelperFactory.get()

    def write_geojsonl(
        self,
        file_name: str,
        data: gpd.GeoDataFrame,
        zip_file_path: Optional[str] = None,
        index: bool = False,
    ) -> None:
        """Writes a line-delimited GeoJSON file to the
        designated file path within the root directory.

        Args:
            file_name (`str`): The relative path to the file
                within the root directory.

            data (`gpd.GeoDataFrame`): The data.

            zip_file_path (`str`|`None`): The path to the shapefile
                within a zip folder, if applicable. Defaults
                to `None`.

            index (`bool`): Boolean indicating whether the index
                should be kept in the output GeoJSON lines.
                Defaults to `False`.

        Returns:
            `None`
        """
        counter = 0
        num_features = len(data)
        mode = "w"
        parse_row = lambda r: (
            json.dumps(r).encode() if zip_file_path else json.dumps(r)
        )
        obj_key = f"{settings.GEOJSONL_DIRECTORY}/{file_name}"
        with self._file_helper.open_file(
            obj_key, self._root_dir, mode, zip_file_path
        ) as f:
            for row in data.iterfeatures(drop_id=True):
                f.write(parse_row(row))
                counter += 1
                if counter != num_features:
                    f.write("\n")

    def write_geoparquet(
        self,
        file_name: str,
        data: gpd.GeoDataFrame,
        zip_file_path: Optional[str] = None,
        index: bool = False,
    ) -> None:
        """Writes a geoparquet file to the designated
        file path within the root directory.

        Args:
            file_name (`str`): The relative path to the file
                within the root directory.

            data (`gpd.GeoDataFrame`): The data.

            zip_file_path (`str`|`None`): The path to the Shapefile
                within a zip folder, if applicable. Defaults
                to `None`.

            index (`bool`): Boolean indicating whether the
                GeoDataFrame index should be kept in the
                output geoparquet file. Defaults to `False`.

        Returns:
            `None`
        """
        mode = "w" if zip_file_path else "wb"
        obj_key = f"{settings.GEOPARQUET_DIRECTORY}/{file_name}"
        with self._file_helper.open_file(
            obj_key, self._root_dir, mode, zip_file_path
        ) as f:
            data.to_parquet(f, index=index)
