"""Defines models used to create database tables.
"""

from django.contrib.gis.db.models import MultiPolygonField, PointField
from django.db import models


class Geography_Type(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)


class Geography(models.Model):
    # Autogenerate id field
    id = models.BigAutoField(primary_key=True)
    # id = models.CharField(max_length=255, primary_key=True) # TODO should be source + name
    name = models.CharField(max_length=255)
    geography_type = models.ForeignKey(Geography_Type, on_delete=models.CASCADE)
    boundary = MultiPolygonField()
    as_of = models.DateField()
    source = models.CharField(max_length=255)


class Program(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    agency = models.CharField(max_length=255)
    description = models.TextField()
    base_benefit = models.TextField()


class Geography_Type_Program(models.Model):
    id = models.IntegerField(primary_key=True)
    geography_type = models.ForeignKey(Geography_Type, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    amount_description = models.TextField()


# class Geography_Metric(models.Model):
#     geography = models.ForeignKey(Geography, on_delete=models.CASCADE)
#     source = models.CharField(max_length=255)
#     as_of = models.DateField()
#     name = models.CharField(max_length=255)
#     value = models.DecimalField(max_digits=10, decimal_places=5)
#     methodology = models.TextField()


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


class Census_Tract(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    centroid = PointField()
    population = models.IntegerField()
