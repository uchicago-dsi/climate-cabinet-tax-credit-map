"""Defines models used to create database tables.
"""

# Third-party imports
import json
import pandas as pd
from django.db.models import Case, Value, When
from django.db.models.functions import Cast
from django.contrib.gis.db.models import MultiPolygonField
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.db import models


class Geography(models.Model):
    """Represents a geography published by a data source."""

    class GeographyType(models.TextChoices):
        """Enumerates geography types."""

        COUNTY = "county"
        DISTRESSED = "distressed"
        ENERGY = "energy"
        JUSTICE40 = "justice40"
        LOW_INCOME = "low-income"
        MUNICIPALITY = "municipality"
        MUNICIPAL_UTILITY = "municipal utility"
        RURAL_COOPERATIVE = "rural cooperative"
        STATE = "state"

    class FipsPattern(models.TextChoices):
        """Enumerates FIPS code structures."""

        STATE = "STATE(2)"
        STATE_COUNTY = "STATE(2) + COUNTY(3)"
        STATE_COUNTY_COUNTY_SUBDIVISION = "STATE(2) + COUNTY(3) + COUNTY SUBDIVISION(5)"
        STATE_COUNTY_TRACT = "STATE(2) + COUNTY(3) + TRACT(6)"
        STATE_PLACE = "STATE(2) + PLACE(5)"

    class PopulationCalculation(models.TextChoices):
        """Enumerates methodologies used to calculate geography population totals."""

        CENTROID_SJOIN = "Population-Weighted Block Group Centroid Spatial Join"
        FIPS = "FIPS Code Match"

    class TaxCreditProgram(models.TextChoices):
        """Enumerates tax credit bonus programs."""

        ALTERNATIVE_FUEL = "Alternative Fuel Refueling Property Credit"
        DIRECT_PAY_INVESTMENT = "Direct Pay Clean Energy Investment Tax Credits"
        DIRECT_PAY_PRODUCTION = "Direct Pay Clean Energy Production Tax Credits"
        NEIGHBORHOOD_ACCESS_AND_EQUITY = "Neighborhood Access & Equity Grant"
        SOLAR_FOR_ALL = "Solar For All"

    GEOGRAPHY_TYPE_PROGRAM_MAP = {
        GeographyType.DISTRESSED: [
            TaxCreditProgram.NEIGHBORHOOD_ACCESS_AND_EQUITY,
            TaxCreditProgram.SOLAR_FOR_ALL,
        ],
        GeographyType.ENERGY: [
            TaxCreditProgram.DIRECT_PAY_INVESTMENT,
            TaxCreditProgram.DIRECT_PAY_PRODUCTION,
        ],
        GeographyType.JUSTICE40: [TaxCreditProgram.SOLAR_FOR_ALL],
        GeographyType.LOW_INCOME: [
            TaxCreditProgram.ALTERNATIVE_FUEL,
            TaxCreditProgram.DIRECT_PAY_INVESTMENT,
            TaxCreditProgram.DIRECT_PAY_PRODUCTION,
            TaxCreditProgram.SOLAR_FOR_ALL,
        ],
    }

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    fips = models.CharField(max_length=255, blank=True, default="")
    fips_pattern = models.CharField(choices=FipsPattern, blank=True, default="")
    geography_type = models.CharField(choices=GeographyType)
    population = models.IntegerField(null=True)
    population_strategy = models.CharField(choices=PopulationCalculation)
    as_of = models.DateField()
    published_on = models.DateField(null=True)
    source = models.TextField()
    programs = models.GeneratedField(
        expression=Cast(
            Case(
                *[
                    When(
                        geography_type=_geotype,
                        then=Value(json.dumps(_programs)),
                    )
                    for _geotype, _programs in GEOGRAPHY_TYPE_PROGRAM_MAP.items()
                ],
                default=Value(json.dumps([])),
                output_field=models.CharField(),
            ),
            output_field=models.JSONField(),
        ),
        output_field=models.JSONField(),
        db_persist=True,
    )
    geometry = MultiPolygonField()

    class Meta:
        db_table = "tax_credit_geography"
        constraints = [
            models.UniqueConstraint(
                fields=("name", "fips", "geography_type"), name="unique_geography"
            )
        ]

    def __str__(self):
        attrs = {
            "id": self.id,
            "name": self.name,
            "fips": self.fips,
            "fips_pattern": self.fips_pattern,
            "geography_type": self.geography_type,
        }
        return f"Geography({attrs})"

    @staticmethod
    def from_series(data: pd.Series) -> "Geography":
        """Maps a row from a cleaned geography dataset
        into a `Geography` database model object.

        Args:
            data (`pd.Series`): The row. Expected to
                have the columns "geometry", "name",
                "fips", "fips_pattern", "geography_type",
                "as_of", "published_on" and "source".

        Returns:
            (`Geography`): The object.
        """
        try:
            # Correct row geometry to ensure MultiPolygon type
            geos_geom: GEOSGeometry = GEOSGeometry(memoryview(data["geometry"]))
            safe_geometry = (
                geos_geom
                if geos_geom.geom_type == "MultiPolygon"
                else MultiPolygon(geos_geom)
            )

            # Build geography
            return Geography(
                name=data["name"],
                fips="" if not data["fips"] else data["fips"],
                fips_pattern=("" if not data["fips_pattern"] else data["fips_pattern"]),
                geography_type=data["geography_type"],
                population=data["population"],
                population_strategy=data["population_strategy"],
                as_of=data["as_of"],
                published_on=data["published_on"],
                source=data["source"],
                geometry=safe_geometry,
            )
        except KeyError as e:
            raise RuntimeError(
                f"Failed to create Geography database record. "
                f'Data missing expected key "{e}". The actual '
                f"keys are: {', '.join(data.keys())}."
            ) from e


class TargetBonusGeographyOverlap(models.Model):
    """Represents an association between a target geography
    of interest to a governmental representative and a (tax
    credit) bonus geography that spatially intersects with it.
    """

    target = models.ForeignKey(
        Geography, related_name="target_geo_set", on_delete=models.CASCADE
    )
    bonus = models.ForeignKey(
        Geography, related_name="bonus_geo_set", on_delete=models.CASCADE
    )
    population = models.IntegerField()
    population_strategy = models.CharField(choices=Geography.PopulationCalculation)

    class Meta:
        db_table = "tax_credit_target_bonus_overlap"
        constraints = [
            models.UniqueConstraint(
                fields=["target", "bonus"],
                name="unique_target_bonus_overlap",
            )
        ]

    def __str__(self):
        target_attrs = {
            "name": self.target.name,
            "type": self.target.geography_type,
        }
        bonus_attrs = {
            "name": self.bonus.name,
            "type": self.bonus.geography_type,
        }
        return f"Target({target_attrs}) <-> Bonus({bonus_attrs})"
