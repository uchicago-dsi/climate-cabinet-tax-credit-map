"""Unit tests for common storage clients.
"""

# Standard library imports
import shutil
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

# Third-party imports
import geopandas as gpd
import json
import pandas as pd
from django.conf import settings

# Application imports
from common.storage import (
    CsvDataReader,
    DataLoader,
    DataWriter,
    FileSystemHelperFactory,
    GoogleCloudStorageHelper,
    LocalFileSystemHelper,
    ParquetDataReader,
)


class FileSystemHelperTestMixins:
    """Generic tests for an `FileSystemHelper` client."""

    def test_list_contents_when_empty(self) -> None:
        """Asserts that an empty directory returns an empty list of contents."""
        contents = self._CLIENT.list_contents(
            root_dir=self._ROOT_DIR,
            glob_pattern=f"{self._EMPTY_DIR}/*?",
        )
        assert not len(contents)

    def test_list_contents_when_populated(self) -> None:
        """Asserts that the correct number of files are listed in a populated folder."""
        helper = self._CLIENT
        contents = helper.list_contents(
            root_dir=self._ROOT_DIR,
            glob_pattern=f"{self._POPULATED_DIR}/**/**?",
        )
        assert len(contents) == self._NUM_FILES_POPULATED_DIR

    def test_list_contents_with_filter(self) -> None:
        """Asserts that the correct number of files is listed
        when given a regular expression as a path filter.
        """
        contents = self._CLIENT.list_contents(
            root_dir=self._ROOT_DIR,
            glob_pattern=f"{self._POPULATED_DIR}/*.txt",
        )
        assert len(contents) == self._NUM_TXT_FILES_POPULATED_DIR

    def test_read_unzipped_file(self) -> None:
        """Asserts that no exceptions are raised when reading unzipped files."""
        root_dir = self._ROOT_DIR
        file_name = f"{self._POPULATED_DIR}/{self._TEST_TXT_FILE_NAME}"
        with self._CLIENT.open_file(file_name, root_dir, mode="r") as f:
            assert isinstance(f.read(), str)

    def test_read_zipped_file(self) -> None:
        """Asserts that no exceptions are raised when directly reading zipped files."""
        root_dir = self._ROOT_DIR
        file_name = f"{self._POPULATED_DIR}/{self._TEST_ZIP_FILE_NAME}"
        with self._CLIENT.open_file(
            file_name, root_dir, mode="r", zip_file_path=self._TEST_TXT_FILE_NAME
        ) as f:
            assert isinstance(f.read(), bytes)

    def test_write_unzipped_file(self) -> None:
        """Assert that no exceptions are raised when writing an unzipped file."""
        # Arrange
        root_dir = self._ROOT_DIR
        file_name = f"{self._POPULATED_DIR}/test_write.txt"
        data = {"name": "Test Geography", "lat": 41.8781, "lon": 87.6298}

        # Act
        with self._CLIENT.open_file(file_name, root_dir, mode="w") as f:
            for k, v in data.items():
                f.write(f"{k}: {v}\n")

        # Assert
        contents = self._CLIENT.list_contents(
            root_dir=self._ROOT_DIR,
            glob_pattern=file_name,
        )
        assert len(contents) == 1

    def test_write_zipped_file(self) -> None:
        """Assert that no exceptions are raised when writing a zipped file."""
        # Arrange
        root_dir = self._ROOT_DIR
        file_name = f"{self._POPULATED_DIR}/test_write.zip"
        zipped_file_name = "inner_file.csv"
        data = {"name": "Test Geography", "lat": 41.8781, "lon": 87.6298}
        df = pd.DataFrame.from_records([data])

        # Act
        with self._CLIENT.open_file(
            file_name, root_dir, mode="w", zip_file_path=zipped_file_name
        ) as f:
            df.to_csv(f, index=False)

        # Assert
        contents = self._CLIENT.list_contents(
            root_dir=self._ROOT_DIR,
            glob_pattern=file_name,
        )
        assert len(contents) == 1


class TestLocalFileSystemHelper(unittest.TestCase, FileSystemHelperTestMixins):
    """Tests I/O operations using a `LocalFileSystemHelper` instance."""

    _CLIENT = LocalFileSystemHelper()
    _ROOT_DIR = Path(settings.DATA_DIR) / "test" / "temp-cc-bucket"
    _EMPTY_DIR = "empty"
    _POPULATED_DIR = "populated"
    _NUM_FILES_POPULATED_DIR = 3
    _NUM_TXT_FILES_POPULATED_DIR = 1
    _TEST_JSON_FILE_NAME = "test.json"
    _TEST_TXT_FILE_NAME = "test.txt"
    _TEST_ZIP_FILE_NAME = "test.zip"

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up the class before tests run."""
        # Create directories
        root = cls._ROOT_DIR
        empty = root / cls._EMPTY_DIR
        populated = root / cls._POPULATED_DIR
        for pth in (cls._ROOT_DIR, empty, populated):
            pth.mkdir(parents=True, exist_ok=True)

        # Arrange data
        data = {"name": "Test Geography", "lat": 41.8781, "lon": 87.6298}

        # Write text file to "populated" directory
        with open(populated / cls._TEST_TXT_FILE_NAME, "w") as f:
            for k, v in data.items():
                f.write(f"{k}: {v}\n")

        # Write zipped file to "populated" directory
        with ZipFile(populated / cls._TEST_ZIP_FILE_NAME, "w") as zipfile:
            with zipfile.open(cls._TEST_TXT_FILE_NAME, "w") as f:
                for k, v in data.items():
                    f.write(f"{k}: {v}\n".encode())

        # Write JSON file to "populated" directory
        with open(populated / cls._TEST_JSON_FILE_NAME, "w") as f:
            json.dump(data, f)

    @classmethod
    def tearDownClass(cls) -> None:
        """Destroys resources after all tests run."""
        shutil.rmtree(TestLocalFileSystemHelper._ROOT_DIR)


class TestGoogleCloudStorageHelper(unittest.TestCase, FileSystemHelperTestMixins):
    """Tests I/O operations using a `GoogleCloudStorageHelper` instance.
    Expects a manually-configured bucket on Google Cloud Platform
    containing (1) an empty directory and (2) a populated directory with
    three files, the names of which may be configured below.

    NOTE: Unfortunately, these tests could not be more abstracted from the
    cloud infrastructure because GCP has not yet released a Cloud Storage
    emulator and Docker images and packages available from third-parties
    don't implement the latest version of the Cloud Storage API
    (particularly the functionality for filtering lists of blobs according
    to a glob pattern).
    """

    _CLIENT = GoogleCloudStorageHelper()
    _ROOT_DIR = "temp-cc-bucket"
    _EMPTY_DIR = "empty"
    _POPULATED_DIR = "populated"
    _NUM_FILES_POPULATED_DIR = 3
    _NUM_TXT_FILES_POPULATED_DIR = 1
    _TEST_JSON_FILE_NAME = "test.json"
    _TEST_TXT_FILE_NAME = "test.txt"
    _TEST_ZIP_FILE_NAME = "test.zip"


class IterativeDataReaderTestMixins:
    """Generic tests for an `IterativeDataReader`."""

    def test_get_data_bucket_contents(self):
        """Asserts that files in the root directory can be
        listed without resulting in an exception.
        """
        contents = self._CLIENT.get_data_bucket_contents()

    def test_list_columns(self):
        """Asserts that the loaded file has the expected number of columns."""
        file_name = self._TEST_FILE_NAME
        col_names = self._CLIENT.col_names(file_name, delimiter=",")
        assert len(col_names) == self._TEST_FILE_NUM_COLS

    def test_iterate(self):
        """Asserts that the loaded file can be iterated."""
        file_name = self._TEST_FILE_NAME
        rows = [row for row in self._CLIENT.iterate(file_name, delimiter=",")]
        assert len(rows) == self._TEST_FILE_NUM_ROWS


class TestCsvDataReader(unittest.TestCase, IterativeDataReaderTestMixins):
    """Tests iterative data reading with a `CsvDataReader` instance."""

    _TEST_FILE_NAME = "test.csv"
    _TEST_FILE_NUM_COLS = 10
    _TEST_FILE_NUM_ROWS = 2

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up the class before tests run."""
        # Arrange data
        data = [
            {i: i for i in range(cls._TEST_FILE_NUM_COLS)}
            for _ in range(cls._TEST_FILE_NUM_ROWS)
        ]
        df = pd.DataFrame(data)

        # Write CSV files
        file_name = cls._TEST_FILE_NAME
        root_dir = Path(settings.DATA_DIR) / "test"
        with FileSystemHelperFactory.get().open_file(
            file_name, root_dir, mode="w"
        ) as f:
            df.to_csv(f, index=False)

        # Initialize data reader client
        cls._CLIENT = CsvDataReader(root_dir)


class TestParquetDataReader(unittest.TestCase, IterativeDataReaderTestMixins):
    """Tests iterative data reading with a `ParquetDataReader` instance."""

    _TEST_FILE_NAME = "test.parquet"
    _TEST_FILE_NUM_COLS = 10
    _TEST_FILE_NUM_ROWS = 2

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up the class before tests run."""
        # Arrange data
        data = [
            {i: i for i in range(cls._TEST_FILE_NUM_COLS)}
            for _ in range(cls._TEST_FILE_NUM_ROWS)
        ]
        df = pd.DataFrame(data)

        # Write CSV files
        file_name = cls._TEST_FILE_NAME
        root_dir = Path(settings.DATA_DIR) / "test"
        with FileSystemHelperFactory.get().open_file(
            file_name, root_dir, mode="wb"
        ) as f:
            df.to_parquet(f, index=False)

        # Initialize data reader client
        cls._CLIENT = ParquetDataReader(root_dir)


class TestDataLoader(unittest.TestCase):
    """Tests loading entire data files with a `DataLoader` instance."""

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up the class before tests run."""
        # Initialize variables for managing file writes
        helper = FileSystemHelperFactory.get()
        files = {
            "csv": "test.csv",
            "csv-zipped": "test.csv.zip",
            "excel": "test.xlsx",
            "excel-zipped": "test.xlsx.zip",
            "json": "test.json",
            "json-zipped": "test.json.zip",
            "parquet": "test.parquet",
            "parquet-zipped": "test.parquet.zip",
            "shp-zipped": "test.shp.zip",
        }
        root_dir = Path(settings.DATA_DIR) / "test"

        # Arrange data
        data = {"name": "city", "latitude": 30, "longitude": 60}
        df = pd.DataFrame([data])
        gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(x=df.longitude, y=df.latitude)
        )

        # Write CSV file
        with helper.open_file(files["csv"], root_dir, mode="w") as f:
            df.to_csv(f, index=False)

        # Write Excel file
        with helper.open_file(files["excel"], root_dir, mode="wb") as f:
            df.to_excel(f, index=False)

        # Write JSON file
        with helper.open_file(files["json"], root_dir, mode="w") as f:
            json.dump(data, f)

        # Write Parquet file
        with helper.open_file(files["parquet"], root_dir, mode="wb") as f:
            gdf.to_parquet(f, index=False)

        # Write zipped Shapefile (comprised of several smaller files)
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_fpath = f"{temp_dir}/{files['shp-zipped']}"
            gdf.to_file(tmp_fpath, driver="ESRI Shapefile")
            with open(tmp_fpath, "rb") as tmp:
                with helper.open_file(files["shp-zipped"], root_dir, mode="wb") as f:
                    f.write(tmp.read())

        # Zip remaining files
        for key, file_name in files.items():
            if key.endswith("zipped") and not key.startswith("shp"):
                base_file_name = file_name.split(".zip")[0]
                with helper.open_file(base_file_name, root_dir, mode="rb") as f:
                    with helper.open_file(
                        file_name, root_dir, mode="w", zip_file_path=base_file_name
                    ) as z:
                        z.write(f.read())

        # Set class variables
        cls._CLIENT = DataLoader(root_dir)
        cls._FILES = files

    def test_read_csv(self) -> None:
        """Asserts that reading a CSV file into a Pandas
        DataFrame does not result in an exception.
        """
        csv_file_name = self._FILES["csv"]
        zip_file_name = self._FILES["csv-zipped"]
        unzipped = self._CLIENT.read_csv(csv_file_name)
        zipped = self._CLIENT.read_csv(
            file_name=zip_file_name, zip_file_path=csv_file_name
        )
        assert len(unzipped) == len(zipped) == 1

    def test_read_excel(self) -> None:
        """Asserts that reading an Excel file into a Pandas
        DataFrame does not result in an exception.
        """
        excel_file_name = self._FILES["excel"]
        zip_file_name = self._FILES["excel-zipped"]
        unzipped = self._CLIENT.read_excel(excel_file_name)
        zipped = self._CLIENT.read_excel(
            file_name=zip_file_name, zip_file_path=excel_file_name
        )
        assert len(unzipped) == len(zipped) == 1

    def test_read_json(self) -> None:
        """Asserts that reading a JSON file into a Python
        dictionary does not result in an exception.
        """
        json_file_name = self._FILES["json"]
        zip_file_name = self._FILES["json-zipped"]
        unzipped = self._CLIENT.read_json(json_file_name)
        zipped = self._CLIENT.read_json(
            file_name=zip_file_name, zip_file_path=json_file_name
        )
        assert (unzipped == zipped) and (unzipped is not None)

    def test_read_parquet(self) -> None:
        """Asserts that reading a Parquet file into a
        GeoDataFrame does not result in an exception.
        """
        parquet_file_name = self._FILES["parquet"]
        zip_file_name = self._FILES["parquet-zipped"]
        unzipped = self._CLIENT.read_parquet(parquet_file_name)
        zipped = self._CLIENT.read_parquet(
            file_name=zip_file_name, zip_file_path=parquet_file_name
        )
        assert len(unzipped) == len(zipped) == 1

    def test_read_zipped_shapefile(self) -> None:
        """Asserts that reading a zipped Shapefile into a
        GeoDataFrame does not result in an exception.
        """
        gdf = self._CLIENT.read_shapefile(self._FILES["shp-zipped"])
        assert len(gdf) == 1


class TestDataWriter(unittest.TestCase):
    """Tests writing files to data stores using a `DataWriter` instance."""

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up the class before tests run."""
        # Arrange data
        df = pd.DataFrame([{"name": "city", "latitude": 30, "longitude": 60}])

        # Set class variables
        root_dir = Path(settings.DATA_DIR) / "test"
        cls._DATA = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(x=df.longitude, y=df.latitude)
        )
        cls._CLIENT = DataWriter(root_dir)
        cls._LOADER = DataLoader(root_dir)

    def test_write_geojsonl(self) -> None:
        """Asserts that writing line-delimited GeoJSON
        files to the store does not raise an exception.
        """
        # Write unzipped file
        file_name = "tmp.geojsonl"
        self._CLIENT.write_geojsonl(file_name, self._DATA)

        # Write zipped file
        zip_file_name = f"{file_name}.zip"
        self._CLIENT.write_geojsonl(
            zip_file_name,
            self._DATA,
            zip_file_path=file_name,
        )

        # Confirm files successfully written
        contents = self._LOADER.list_directory_contents()
        file_names = [pth.split("/")[-1] for pth in contents]
        assert (file_name in file_names) and (zip_file_name in file_names)

    def test_write_geoparquet(self) -> None:
        """Asserts that writing GeoParquet files to
        the store does not raise an exception.
        """
        # Write unzipped file
        file_name = "tmp.geoparquet"
        self._CLIENT.write_geoparquet(file_name, self._DATA)

        # Write zipped file
        zip_file_name = f"{file_name}.zip"
        self._CLIENT.write_geoparquet(
            zip_file_name,
            self._DATA,
            zip_file_path=file_name,
        )

        # # Confirm files successfully written
        contents = self._LOADER.list_directory_contents()
        file_names = [pth.split("/")[-1] for pth in contents]
        assert (file_name in file_names) and (zip_file_name in file_names)
