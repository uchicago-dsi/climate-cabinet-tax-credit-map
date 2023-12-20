"""Defines models used to create database tables.
"""

from django.contrib.gis.db.models import MultiPolygonField, PointField
from django.db import models


class GeographyType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"[ id : {self.id} , name : {self.name} ]"

    class Meta:
        db_table = "tax_credit_geography_type"


class Geography(models.Model):
    # Autogenerate id field
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    fips = models.CharField(max_length=255, blank=True, default="")
    geography_type = models.ForeignKey(GeographyType, on_delete=models.CASCADE)
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
        return f"[ {self.id}, {self.name}, {self.fips}, {self.geography_type} ]"


class Program(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    agency = models.CharField(max_length=255)
    description = models.TextField()
    base_benefit = models.TextField()


class GeographyTypeProgram(models.Model):
    id = models.IntegerField(primary_key=True)
    geography_type = models.ForeignKey(GeographyType, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    amount_description = models.TextField()

    class Meta:
        db_table = "tax_credit_geography_type_program"
        unique_together = [["geography_type", "program"]]


class TargetBonusAssoc(models.Model):
    # Auto create ID
    target_geography = models.ForeignKey(
        Geography, related_name="target_geo_set", on_delete=models.CASCADE
    )
    target_geography_type = models.CharField(max_length=255)
    bonus_geography = models.ForeignKey(
        Geography, related_name="bonus_geo_set", on_delete=models.CASCADE
    )
    bonus_geography_type = models.CharField(max_length=255)

    class Meta:
        db_table = "tax_credit_target_bonus_assoc"
        unique_together = [["target_geography", "bonus_geography"]]

    def __str__(self):
        return f"{self.target_geography.name} <-> {self.bonus_geography.name}"


class CensusBlockGroup(models.Model):
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
