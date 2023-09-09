from django.test import SimpleTestCase
from django.core.management import call_command
from unittest.mock import patch
from django.conf import settings
from common.storage import CloudDataReader, LocalDataReader


class Test_Load_Geos(
    SimpleTestCase
):  # REMEMBER using simple test case over TestCase so that it doesn't setup
    # the database -- be careful, it may run the tests directly against any
    # database connection it can make and WILL NOT roll back the transaction.
    # One solution is a custom runner
    @patch(
        "tax_credit.models.Geography_Type"
    )  # REMEMBER patching the database connection so that it unittests
    @patch("tax_credit.models.Geography")
    def test_load_geos_runs(self, patch_geo_type, patch_geography):
        call_command("load_geos")


class TestDataReaders(SimpleTestCase):
    def test_read_local_geoparquet(self):
        filepath = settings.DATA_DIR / "state_clean.geoparquet"
        reader = LocalDataReader()
        iterator = reader.geoparquet_iterator(filepath)
        first_item = next(iterator)
        # TODO: this will throw an exception if we don't get an iterator back,
        # but can add more assertions here

    def test_read_google_cloud_geoparquet(self):
        filepath = "state_clean.geoparquet"
        reader = CloudDataReader()
        iterator = reader.geoparquet_iterator(filepath)
        first_item = next(iterator)

    # TODO: should we have tests for reading CSVs also?
