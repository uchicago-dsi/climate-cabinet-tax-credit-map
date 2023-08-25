"""Defines models used to create database tables.
"""

# from django.db import models
from django.db import models
from django.contrib.gis.db.models import MultiPolygonField

class Geography_Type(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

class Geography(models.Model):
    # Autogenerate id field
    name = models.CharField(max_length=255)
    geography_type = models.ForeignKey(
        Geography_Type, on_delete=models.CASCADE
    )
    boundary = MultiPolygonField()
    as_of = models.DateField()
    source = models.CharField(max_length=255)


class Program(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    agency = models.CharField(max_length=255)
    description = models.TextField()
    base_benefit = models.TextField()


class Geography_Type_Program(models.Model):
    geography_type = models.ForeignKey(
        Geography_Type, on_delete=models.CASCADE
    )
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE
    )
    amount_description = models.TextField()


class Geography_Metric(models.Model):
    geography = models.ForeignKey(
        Geography, on_delete=models.CASCADE
    )
    source = models.CharField(max_length=255)
    as_of = models.DateField()
    name = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=10, decimal_places=5)
    methodology = models.TextField()