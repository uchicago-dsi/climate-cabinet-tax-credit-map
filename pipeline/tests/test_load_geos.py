from django.test import SimpleTestCase
from django.core.management import call_command
from unittest.mock import patch

class Test_Load_Geos(SimpleTestCase): # REMEMBER using simple test case over TestCase so that it doesn't setup the database -- be careful, it may run the tests directly against any database connection it can make and WILL NOT roll back the transaction. One solution is a custom runner
    
    @patch('tax_credit.models.Geography_Type') # REMEMBER patching the database connection so that it unittests
    @patch('tax_credit.models.Geography')
    def test_load_geos_runs(self, patch_geo_type, patch_geography):
        call_command('load_geos')
