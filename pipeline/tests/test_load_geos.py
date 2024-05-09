"""Integration test for loading the geographies database table.
"""

# Third-party imports
import pytest
from django.conf import settings
from django.core.management import call_command

# Application imports
from common.logger import LoggerFactory
from tax_credit.models import Geography


@pytest.mark.django_db(transaction=True)
def test_load_geos():
    """Asserts that the `load_geos` Django management command
    executes without raising an exception and returns the
    expected number of records.
    """
    # Arrange
    logger = LoggerFactory.get("TEST LOAD GEOS")
    records_per_dataset = 10
    random_seed = 12345

    # Act
    call_command("load_geos", smoke_test=[records_per_dataset, random_seed])
    geography_ct = Geography.objects.count()
    num_datasets = len(settings.RAW_DATASETS)
    logger.info(
        f"Geography count afer loading {records_per_dataset} "
        f"randomly seleted record(s) from each of the {num_datasets} "
        f"datasets using seed {random_seed}: {geography_ct}."
    )

    # Assert
    assert 0 < geography_ct <= (records_per_dataset * num_datasets)
