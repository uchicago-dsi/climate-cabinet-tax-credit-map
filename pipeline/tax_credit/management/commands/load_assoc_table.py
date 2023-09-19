"""Loads tax credit programs for geographies into the database.
"""

from django.core.management.base import BaseCommand, CommandParser
from tax_credit.models import Geography, TargetBonusAssoc
from common.logger import LoggerFactory

from django.db import connections
from django.db.models import Model

logger = LoggerFactory.get(__name__)

class Command(BaseCommand):
    """
    Populates the `GeographyMetric` table.

    References:
    - https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/
    - https://docs.djangoproject.com/en/4.1/topics/settings/
    """

    help = "Loads data to populate the geography metric table."

    def add_arguments(self, parser: CommandParser) -> None:
        """
        """
        parser.add_argument(
            '--skip-assoc',
            nargs='+',
            default=[]
        )

    def handle(self, *args, **options) -> None:
        """
        Executes the command. Accepts variable
        numbers of keyword and non-keyword arguments.

        Parameters:
            None

        Returns:
            None
        """

        logger.info("Building association table")
        skip_assoc = options['skip_assoc']

        for target in [t for t in ["state", "county", "municipal_util", "rural_coop"] if t not in skip_assoc]:
            for bonus in [b for b in ["distressed", "energy", "justice40", "low_income"] if b not in skip_assoc]:
                self._find_and_load_overlaps(target, bonus)
                self.recycle_connection(Geography)
                self.recycle_connection(TargetBonusAssoc)
        
        logger.info("Association table is finished")

    def _find_and_load_overlaps(self, target_geom, bonus_geom):
        logger.info(f'Finding overlaps between {target_geom} and {bonus_geom}')
        target_iter = Geography.objects.filter(
            geography_type__name=target_geom
        ).iterator(chunk_size=1000)

        for target in target_iter:
            assocs = []
            bonus_iter = (
                Geography.objects.filter(
                    geography_type__name=bonus_geom,
                    boundary__intersects=target.boundary,
                )
                .exclude(boundary__touches=target.boundary)
                .iterator()
            )
            for bonus in bonus_iter:
                assocs.append(
                    TargetBonusAssoc(
                        target_geography=target,
                        target_geography_type=target.geography_type.name,
                        bonus_geography=bonus,
                        bonus_geography_type=bonus.geography_type.name,
                    )
                )
            if assocs:
                logger.info(f"Loading batch of associations, {target_geom} to {bonus_geom} : {assocs}")
                TargetBonusAssoc.objects.bulk_create(assocs, update_conflicts=True, unique_fields=["target_geography", "bonus_geography"], update_fields=["target_geography_type", "bonus_geography_type"])

    @staticmethod
    def recycle_connection(model: Model):
        """Recycles the connection from the model from the previous job. Without this the connection will expire and cause SSL errors when working with Neon Postgres."""
        db_string = model.objects.db
        logger.info(f"Recycling connection : {model}, {db_string}")
        connections[db_string].close()
