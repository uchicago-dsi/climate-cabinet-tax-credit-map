"""Defines models used to create database tables.
"""

from django.contrib.gis.db.models import MultiPolygonField, PointField
from django.db import models


class Geography(models.Model):
    """Represents a geography published by a data source.
    """
    class GeographyType(models.TextChoices):
        COUNTY = "county"
        DISTRESSED = "distressed"
        ENERGY = "energy"
        JUSTICE40 = "justice40"
        LOW_INCOME = "low-income"
        MUNICIPALITY = "municipality"
        MUNICIPAL_UTILITY = "municipal utility"
        RURAL_COOPERATIVE = "rural cooperative"
        STATE = "state"


    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    fips = models.CharField(max_length=255, blank=True, default="")
    geography_type = models.CharField(choices=GeographyType)
    as_of = models.DateField()
    published_on = models.DateField(null=True)
    source = models.CharField(max_length=255)
    geometry = MultiPolygonField()

    class Meta:
        db_table = "tax_credit_geography"
        constraints = [
            models.UniqueConstraint(
                fields=("name", "geography_type", "fips"),
                name="unique_geography"
            )
        ]
    
    def __str__(self):
        attrs = {
            "id": self.id,
            "name": self.name,
            "fips": self.fips,
            "geography_type": self.geography_type
        }
        return f"Geography({attrs})"


class Program(models.Model):
    """Represents a tax credit program.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    agency = models.CharField(max_length=255)
    description = models.TextField()
    base_benefit = models.TextField()
    bonus_amounts = models.JSONField()

    def __str__(self):
        attrs = {
            "id": self.id,
            "name": self.name,
            "agency": self.agency
        }
        return f"Program({attrs})"


class TargetBonusAssoc(models.Model):
    """Represents an association between a target geography
    of interest to a governmental representative and a (tax
    credit) bonus geography that spatially intersects with it.
    """
    target_geography = models.ForeignKey(
        Geography, related_name="target_geo_set", on_delete=models.CASCADE
    )
    bonus_geography = models.ForeignKey(
        Geography, related_name="bonus_geo_set", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "tax_credit_target_bonus_assoc"
        constraints = [
            models.UniqueConstraint(
                fields=["target_geography", "bonus_geography"],
                name="unique_target_bonus_geography_association"
            )
        ]

    def __str__(self):
        target_attrs = {
            "name": self.target_geography.name,
            "type": self.target_geography.geography_type,
        }
        bonus_attrs = {
            "name": self.bonus_geography.name,
            "type": self.bonus_geography.geography_type
        }
        return f"Target({target_attrs}) <-> Bonus({bonus_attrs})"


class CensusBlockGroup(models.Model):
    """Represents a U.S. census block group defined for a given year.
    """
    id = models.BigAutoField(primary_key=True)
    fips = models.CharField(max_length=255)
    centroid = PointField()
    population = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        db_table = "tax_credit_census_block_group"
        constraints = [
            models.UniqueConstraint(
                fields=["fips", "year"],
                name="unique_census_block_group"
            )
        ]

    def __str__(self):
        attrs = {
            "fips": self.fips,
            "year": self.year,
            "population": self.population
        }
        return f"CensusBlockGroup({attrs})"
