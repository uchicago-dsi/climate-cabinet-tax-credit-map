"""Unit tests for Mapbox API validators and request clients.
"""

# Standard library imports
import io
import string
import time
import unittest

# Third-party imports
from django.conf import settings

# Application imports
from common.logger import LoggerFactory
from mapbox.clients import MapboxTilingApiClient
from mapbox.fieldsets import *


class FieldTestMixins:
    """Generic tests for a Mapbox field."""

    def test_invalid_values_fail(self):
        """Assert that invalid values raise `ValueError`."""
        for name, value in self.invalid_subtests.items():
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    self.field(value=value)

    def test_valid_values_pass(self):
        """Assert that valid values do not raise `ValueError`."""
        for name, value in self.valid_subtests.items():
            with self.subTest(msg=name):
                self.field(value=value)


class TestUsernameField(unittest.TestCase, FieldTestMixins):
    """Tests for the field `Username`."""

    field = Username
    invalid_subtests = {"null": None}
    valid_subtests = {"not null": "test-username"}


class TestTilesetDisplayNameField(unittest.TestCase, FieldTestMixins):
    """Tests for the field `TilesetDisplayName`."""

    field = TilesetDisplayName
    invalid_subtests = {
        "is null": None,
        "is empty string": "",
        "exceeds max length": "a" * 65,
    }
    valid_subtests = {
        "is min length": "a",
        "is max length": "a" * 64,
        "has length in range": "a" * 32,
    }


class TestTilesetFormalNameField(unittest.TestCase, FieldTestMixins):
    """Tests for the field `TilesetFormalName`."""

    field = TilesetFormalName
    invalid_subtests = {
        "is null": None,
        "is empty string": "",
        "exceeds max length": "a" * 33,
        "has invalid characters": "@#$%@%^",
    }
    valid_subtests = {
        "is min length": "a",
        "is max length": "a" * 32,
        "has length in range": "a" * 16,
        "has valid chars - lower alphabet": string.ascii_lowercase,
        "has valid chars - upper alphabet": string.ascii_uppercase,
        "has valid chars - numbers": string.digits,
        "has valid chars - special": "_-",
        "has valid chars - combination": "ABC-efg678_",
    }


class TestTilesetJobIdField(unittest.TestCase, FieldTestMixins):
    """Tests for the field `TilesetJobId`."""

    field = TilesetJobId
    invalid_subtests = {"null": None}
    valid_subtests = {"not null": "test-job-id"}


class TestTilesetLayerNameField(unittest.TestCase, FieldTestMixins):
    """Tests for the field `TilesetLayerName`."""

    field = TilesetLayerName
    invalid_subtests = {
        "is null": None,
        "is empty string": "",
        "has invalid characters": "@#$%@%^-",
    }
    valid_subtests = {
        "is min length": "a",
        "has valid chars - lower alphabet": string.ascii_lowercase,
        "has valid chars - upper alphabet": string.ascii_uppercase,
        "has valid chars - numbers": string.digits,
        "has valid chars - special": "_",
        "has valid chars - combination": "ABCefg678_",
    }


class TestTilesetZoomField(unittest.TestCase, FieldTestMixins):
    """Tests for the field `TilesetZoom`."""

    field = TilesetZoom
    invalid_subtests = {"below min": -1, "above max": 20}
    valid_subtests = {"at min": 0, "at max": 16, "within range": 12}


class TestTilesetSourceIdField(unittest.TestCase, FieldTestMixins):
    """Tests for the field `TilesetSourceId`."""

    field = TilesetSourceId
    invalid_subtests = {
        "is null": None,
        "is empty string": "",
        "exceeds max length": "a" * 33,
        "has invalid characters": "@#$%@%^",
    }
    valid_subtests = {
        "is min length": "a",
        "is max length": "a" * 32,
        "has length in range": "a" * 16,
        "has valid chars - lower alphabet": string.ascii_lowercase,
        "has valid chars - upper alphabet": string.ascii_uppercase,
        "has valid chars - numbers": string.digits,
        "has valid chars - special": "_-",
        "has valid chars - combination": "ABC-efg678_",
    }


class TestTilesetSourceFileField(unittest.TestCase, FieldTestMixins):
    """Tests for the field `TilesetSourceFile`."""

    field = TilesetSourceFile
    invalid_subtests = {"null": None}
    valid_subtests = {"not null": io.BytesIO()}


class TestTokenField(unittest.TestCase, FieldTestMixins):
    """Tests for the field `Token`."""

    field = Token
    invalid_subtests = {"null": None}
    valid_subtests = {"not null": "test-token"}


class TestTilesetJobStage(unittest.TestCase, FieldTestMixins):
    """Tests for the field `TilesetJobStage`."""

    field = TilesetJobStage
    invalid_subtests = {
        "non-existent choice": "processingZ",
    }
    valid_subtests = {
        "processing": "processing",
        "queued": "queued",
        "success": "success",
        "failed": "failed",
        "superseded": "superseded",
        "None": None,
    }


class TestTilesetTypeField(unittest.TestCase, FieldTestMixins):
    """Tests for the field `TilesetType`."""

    field = TilesetType
    invalid_subtests = {
        "non-existent choice": "rasterZ",
    }
    valid_subtests = {"raster": "raster", "vector": "vector", "None": None}


class TestResultSetLimitField(unittest.TestCase, FieldTestMixins):
    """Tests for the field `ResultSetLimit`."""

    field = ResultSetLimit
    invalid_subtests = {
        "below min": 0,
        "exceeds max": 501,
        "is wrong type - float": 30.5,
        "is wrong type - string": "40",
    }
    valid_subtests = {"is min": 1, "is max": 500, "is other number in range": 100}


class TestResultSetSortByParam(unittest.TestCase, FieldTestMixins):
    """Tests for the field `ResultSetTimestampSortBy`."""

    field = ResultSetTimestampSortBy
    invalid_subtests = {
        "non-existent choice": "createdZ",
    }
    valid_subtests = {"created": "created", "modified": "modified", "None": None}


class TestTilesetVisibilityParam(unittest.TestCase, FieldTestMixins):
    """Tests for the field `TilesetVisibility`."""

    field = TilesetVisibility
    invalid_subtests = {
        "non-existent choice": "publicZ",
    }
    valid_subtests = {"public": "public", "private": "private", "None": None}


class TestResultSetStartField(unittest.TestCase, FieldTestMixins):
    """Tests for the field `ResultSetStart`."""

    field = ResultSetStart
    invalid_subtests = {}
    valid_subtests = {"example": "start link", "None": None}


class TestTilesetSources(unittest.TestCase):
    """Tests requests related to Mapbox tileset sources."""

    @classmethod
    def setUpClass(cls):
        """Sets up the class before tests run."""
        cls._client = MapboxTilingApiClient()
        cls._test_data_fpath = f"{settings.DATA_DIR}/test/test.geojsonl"
        cls._source_id = "test"

    @classmethod
    def tearDownClass(cls):
        """Destroys resources after all tests run."""
        for source in TestTilesetSources._client.list_tileset_sources():
            TestTilesetSources._client.delete_tileset_source(source["id"])

    def setUp(self):
        """Sets up a test before it runs."""
        time.sleep(10)

    def test_create_or_append(self):
        """Asserts that creating a tileset does not raise an exception."""
        id = TestTilesetSources._source_id
        with open(TestTilesetSources._test_data_fpath) as f:
            TestTilesetSources._client.create_or_append_tileset_source(id, f)

    def test_delete(self):
        """Asserts that deleting a tileset does not raise an exception"""
        id = TestTilesetSources._source_id
        TestTilesetSources._client.delete_tileset_source(id)

    def test_list(self):
        """Asserts that listing Mapbox tileset sources does not
        result in an unexpected exception.
        """
        TestTilesetSources._client.list_tileset_sources()


class TestTilesets(unittest.TestCase):
    """Tests requests related to Mapbox tilesets."""

    @classmethod
    def _reset_environment(cls):
        """Deletes all tileset sources and tilesets for
        the current test Mapbox API account.
        """
        for source in TestTilesets._client.list_tileset_sources():
            try:
                source_id = source["id"].split("/")[-1]
                TestTilesets._client.delete_tileset_source(source_id)
            except:
                pass

        for tileset in TestTilesets._client.list_tilesets():
            tileset_formal_name = tileset["id"].split(".")[-1]
            TestTilesets._client.delete_tileset(tileset_formal_name)

    @classmethod
    def setUpClass(cls):
        """Sets up the class before its individual tests run."""
        # Initialize client
        client = MapboxTilingApiClient()

        # Set up class properties
        source_id = "test_low_income_tracts"
        cls._logger = LoggerFactory.get("test-tilesets")
        cls._client = client
        cls._tileset_params = {
            "formal_name": "test_census_tracts",
            "display_name": "Test Census Tracts",
            "source_id": source_id,
            "layer_name": "test_layer",
            "min_zoom": 5,
            "max_zoom": 10,
        }

        # Reset environment
        TestTilesets._reset_environment()

        # Create test tileset source
        source_fpath = f"{settings.DATA_DIR}/test/test.geojsonl"
        with open(source_fpath) as f:
            client.create_or_append_tileset_source(source_id, f)

    @classmethod
    def tearDownClass(cls):
        """Destroys resources after all tests run."""
        TestTilesets._reset_environment()

    def test_lifecycle(self):
        """Asserts that creating a tileset with valid
        parameters does not raise an exception.
        """
        # Create tileset
        TestTilesets._logger.info("Creating new tileset:")
        t = TestTilesets._client.create_tileset(**TestTilesets._tileset_params)
        TestTilesets._logger.info(t)

        # Create reference to tileset formal name
        tileset_formal_name = TestTilesets._tileset_params["formal_name"]

        # Publish tileset
        TestTilesets._logger.info("Kicking off job to publish tileset:")
        job = TestTilesets._client.publish_tileset(tileset_formal_name)
        TestTilesets._logger.info(job)

        # List all processing jobs
        TestTilesets._logger.info("Job list:")
        all_jobs = TestTilesets._client.list_tileset_jobs(tileset_formal_name)
        TestTilesets._logger.info(all_jobs)

        # Monitor current tileset processing job until complete
        while True:
            TestTilesets._logger.info("Current job:")
            res_body = TestTilesets._client.get_tileset_job(
                tileset_formal_name, job["jobId"]
            )
            TestTilesets._logger.info(res_body)

            if res_body["stage"] == "success":
                break
            elif res_body["stage"] in ("failed", "superseded"):
                errs = " ".join(e for e in res_body["errors"]).strip()
                raise ValueError(f"The job terminated. {errs}")
            else:
                TestTilesets._logger.info("Tileset. not ready. Sleeping.")
                time.sleep(60)

        # List currently published tilesets
        TestTilesets._logger.info("Fetching all published tilesets.")
        tilesets = TestTilesets._client.list_tilesets()
        TestTilesets._logger.info(tilesets)

        # Assert that the published tileset is newly created
        matches = [t for t in tilesets if t["id"].split(".")[-1] == tileset_formal_name]
        if not matches:
            raise AssertionError(
                "The newly-created tileset did not appear "
                "in the list of tilesets. Expected to see "
                f'"{tileset_formal_name}".'
            )

        # Get tileset metadata
        TestTilesets._logger.info(
            "Fetching TileJSON metadata for newly-published tileset."
        )
        meta = TestTilesets._client.get_tilejson_metadata(tileset_formal_name)
        TestTilesets._logger.info(meta)

        # Update tileset recipe
        TestTilesets._logger.info("Updating tileset recipe.")
        TestTilesets._client.update_tileset_recipe(
            tileset_formal_name=tileset_formal_name,
            source_id=TestTilesets._tileset_params["source_id"],
            layer_name="updated_layer_name",
            min_zoom=TestTilesets._tileset_params["min_zoom"],
            max_zoom=TestTilesets._tileset_params["max_zoom"],
        )
        TestTilesets._logger.info("Recipe successfully updated.")

        # Delete tileset
        TestTilesets._logger.info("Deleting tileset.")
        TestTilesets._client.delete_tileset(tileset_formal_name)
        TestTilesets._logger.info("Tileset successfully deleted.")
