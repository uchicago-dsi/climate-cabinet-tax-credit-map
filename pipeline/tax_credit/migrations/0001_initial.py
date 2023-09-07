# Generated by Django 4.2.4 on 2023-09-07 21:29

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Geography',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('boundary', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('as_of', models.DateField()),
                ('source', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Geography_Type',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('agency', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('base_benefit', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Geography_Type_Program',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_description', models.TextField()),
                ('geography_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tax_credit.geography_type')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tax_credit.program')),
            ],
        ),
        migrations.CreateModel(
            name='Geography_Metric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=255)),
                ('as_of', models.DateField()),
                ('name', models.CharField(max_length=255)),
                ('value', models.DecimalField(decimal_places=5, max_digits=10)),
                ('methodology', models.TextField()),
                ('geography', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tax_credit.geography')),
            ],
        ),
        migrations.AddField(
            model_name='geography',
            name='geography_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tax_credit.geography_type'),
        ),
    ]
