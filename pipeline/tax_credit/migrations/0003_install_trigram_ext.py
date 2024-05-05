# Manually created

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    initial = False

    dependencies = [
        ("tax_credit", "0002_install_indexed_search_fields"),
    ]

    operations = [TrigramExtension()]
