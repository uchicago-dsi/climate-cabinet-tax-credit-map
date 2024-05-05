"""Integration tests for loading the target-bonus geography association table.
"""

# Third-party imports
import pytest
from django.core.management import call_command

# Application imports
from common.logger import LoggerFactory
from tax_credit.models import TargetBonusGeographyOverlap


@pytest.fixture(scope="function")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("load_geos")


@pytest.mark.django_db(transaction=True)
def test_load_associations_with_county_fips_match():
    """Asserts that the `load_associations` Django management
    command executes without raising an exception when matching
    target and bonus geographies on county FIPS codes.
    """
    # Arrange
    logger = LoggerFactory.get("TEST LOAD ASSOCIATIONS - COUNTY FIPS MATCH")

    # Act
    call_command(
        "load_associations",
        target=["county"],
        bonus=["low-income", "justice40", "energy"],
    )
    assoc_ct = TargetBonusGeographyOverlap.objects.count()
    logger.info(f"Association table count after loading : {assoc_ct}")

    # Assert
    assert assoc_ct > 0


@pytest.mark.django_db(transaction=True)
def test_load_associations_with_state_fips_match():
    """Asserts that the `load_associations` Django management
    command executes without raising an exception when matching
    target and bonus geographies on state FIPS codes.
    """
    # Arrange
    logger = LoggerFactory.get("TEST LOAD ASSOCIATIONS - STATE FIPS MATCH")

    # Act
    call_command(
        "load_associations",
        target=["state"],
        bonus=["low-income", "justice40", "energy"],
    )
    assoc_ct = TargetBonusGeographyOverlap.objects.count()
    logger.info(f"Association table count after loading : {assoc_ct}")

    # Assert
    assert assoc_ct > 0


@pytest.mark.django_db(transaction=True)
def test_load_associations_with_spatial_intersection():
    """Asserts that the `load_associations` Django management
    command executes without raising an exception when matching
    on spatial intersections.
    """
    # Arrange
    logger = LoggerFactory.get("TEST LOAD ASSOCIATIONS - SPATIAL INTERSECTION MATCH")

    # Act
    # Fetch associations for targets that only ever match on spatial intersections
    call_command(
        "load_associations",
        target=["municipality", "municipal utility", "rural cooperative"],
    )
    spatial_only_assoc_ct = TargetBonusGeographyOverlap.objects.count()
    logger.info(
        f"Association table count after loading matches between "
        f"bonus territories and municipalities, municipal utilities, "
        f"and rural cooperatives: {spatial_only_assoc_ct}."
    )

    # Fetch associations for targets that match spatially given some bonuses
    call_command("load_associations", target=["state", "county"], bonus=["distressed"])
    state_county_assoc_ct = (
        TargetBonusGeographyOverlap.objects.count() - spatial_only_assoc_ct
    )
    logger.info(
        f"Additional associations added after loading matches between "
        f"distressed communities and states and counties: {state_county_assoc_ct}."
    )

    # Assert
    assert spatial_only_assoc_ct > 0
    assert state_county_assoc_ct > 0
