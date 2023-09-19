from unittest.mock import patch, Mock
from django.conf import settings
from common.storage import CloudDataReader, LocalDataReader
from tax_credit.models import Geography, GeographyType

from datetime import datetime

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon


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

    def test_read_google_cloud_csv(self):
        reader = CloudDataReader()
        records = reader.read_csv("geography_type.csv", delimiter="|")
        geography_types = [
            Geography_Type(id=geo_type["Id"], name=geo_type["Name"])
            for _, geo_type in records.iterrows()
        ]


class TestBuffering(TestCase):
    # @patch("tax_credit.models.GeographyType")
    def test_buffering_intersections(self):
        geography_type_instance = GeographyType(id=1, name="test")
        geography_type_instance.save()

        # Create a target boundary for testing
        geom = GEOSGeometry("POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")
        geom.srid = 4326
        target_boundary = MultiPolygon(geom)

        # Geometries that barely touch, overlap significantly, and don't intersect at all
        geom = GEOSGeometry("POLYGON((5 5, 15 5, 15 15, 5 15, 5 5))")
        geom.srid = 4326
        overlap_significantly = MultiPolygon(geom)

        geom = GEOSGeometry("POLYGON((10 5, 15 5, 15 15, 10 15, 10 5))")
        geom.srid = 4326
        barely_touch = MultiPolygon(geom)

        geom = GEOSGeometry("POLYGON((20 20, 30 20, 30 30, 20 30, 20 20))")
        geom.srid = 4326
        no_intersection = MultiPolygon(geom)

        # Creating the Geography objects for testing
        Geography.objects.create(
            name="barely_touch",
            boundary=barely_touch,
            simple_boundary=barely_touch,
            as_of=datetime.now(),
            source="test_case",
            geography_type=geography_type_instance,
        )
        Geography.objects.create(
            name="overlap_significantly",
            boundary=overlap_significantly,
            simple_boundary=overlap_significantly,
            as_of=datetime.now(),
            source="test_case",
            geography_type=geography_type_instance,
        )
        Geography.objects.create(
            name="no_intersection",
            boundary=no_intersection,
            simple_boundary=no_intersection,
            as_of=datetime.now(),
            source="test_case",
            geography_type=geography_type_instance,
        )

        buffered_boundary = target_boundary.buffer(
            -0.001
        )  # maybe this is a good number for degrees?
        overlapping_geos = Geography.objects.filter(
            boundary__intersects=buffered_boundary
        )

        self.assertNotIn(barely_touch, [geo.boundary for geo in overlapping_geos])
        self.assertIn(overlap_significantly, [geo.boundary for geo in overlapping_geos])
        self.assertNotIn(no_intersection, [geo.boundary for geo in overlapping_geos])
