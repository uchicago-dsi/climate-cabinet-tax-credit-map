# Generated by Django 4.2.7 on 2023-11-06 18:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tax_credit', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='geography',
            name='simple_boundary',
        ),
    ]
