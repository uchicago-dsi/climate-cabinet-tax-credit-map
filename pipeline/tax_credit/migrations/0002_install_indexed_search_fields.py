# Manually created

from django.contrib.postgres.indexes import GinIndex
from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("tax_credit", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
              ALTER TABLE tax_credit_geography
              ADD COLUMN name_vector tsvector 
              GENERATED ALWAYS AS (to_tsvector('english', name)) STORED;
            """,
            reverse_sql="""
              ALTER TABLE tax_credit_geography DROP COLUMN name_vector;
            """,
        ),
        migrations.RunSQL(
            sql="""
                CREATE INDEX name_vector_idx 
                ON tax_credit_geography 
                USING gin(name_vector);
            """,
            reverse_sql="""
                DROP INDEX name_vector_idx
            """,
        ),
    ]
