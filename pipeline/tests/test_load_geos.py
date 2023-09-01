from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase


class Test_Load_Geos(
    SimpleTestCase
):
    @patch(
        "tax_credit.models.Geography_Type"
    )
    @patch("tax_credit.models.Geography")
    def test_load_geos_runs(self, patch_geo_type, patch_geography):
        call_command("load_geos")
