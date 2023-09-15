"""Defines models used to create database tables.
"""

from django.contrib.gis.db.models import MultiPolygonField, PointField
from django.db import models


class GeographyType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "tax_credit_geography_type"


class Geography(models.Model):
    # Autogenerate id field
    id = models.BigAutoField(primary_key=True)
    # id = models.CharField(max_length=255, primary_key=True) # TODO should be source + name
    name = models.CharField(max_length=255)
    geography_type = models.ForeignKey(GeographyType, on_delete=models.CASCADE)
    boundary = MultiPolygonField()
    simple_boundary = MultiPolygonField()
    as_of = models.DateField()
    source = models.CharField(max_length=255)

    class Meta:
        unique_together = [['name', 'geography_type']]


class Program(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    agency = models.CharField(max_length=255)
    description = models.TextField()
    base_benefit = models.TextField()


class Geography_Type_Program(models.Model):
    id = models.IntegerField(primary_key=True)
    geography_type = models.ForeignKey(GeographyType, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    amount_description = models.TextField()

    class Meta:
        unique_together = [['geography_type', 'program']]


class Target_Bonus_Assoc(models.Model):
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
        unique_together = [['target_geography', 'bonus_geography']]


class Census_Tract(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    centroid = PointField()
    population = models.IntegerField()
