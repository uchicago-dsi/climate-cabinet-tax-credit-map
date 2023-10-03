"""Loads tax credit programs for geographies into the database.
"""
from itertools import islice
import sys

from django.core.management.base import BaseCommand, CommandParser
from tax_credit.models import Geography, TargetBonusAssoc
from common.logger import LoggerFactory

from django.db import connections
from django.db.models.functions import Substr
from django.db.models import Model
from django.conf import settings

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
            '--only-assoc',
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

        # Ugly code... essentially if the option --only assoc, it will load only the geography types passed. Otherwise it loads all geographies in succession
        targets = ["state", "county", "municipal_util", "rural_coop"]
        bonuses = ["distressed", "energy", "justice40", "low_income"]
        logger.info("Building association table")
        only_assoc = options['only_assoc']
        logger.info(f'Here is only_assoc : {only_assoc}')
        if not only_assoc:
            only_assoc.extend(targets)
            only_assoc.extend(bonuses)

        for target in [t for t in targets if t in only_assoc]:
            for bonus in [b for b in bonuses if b in only_assoc]:
                
                if target in ["state", "county"] and bonus in ["energy", "justice40", "low_income"]:
                    if target == "state":
                        self._find_and_load_matching_state_fips(target, bonus)
                    elif target == "county":
                        self._find_and_load_matching_county_fips(target, bonus)
                    else:
                        raise ValueError("This shouldn't happen. Value was supposed to be in [ state, county ] .")
                else:
                    logger.info("Need to use overlaps")
                    self._find_and_load_overlaps(target, bonus)
                
                # self.recycle_connection(Geography)
                # self.recycle_connection(TargetBonusAssoc)
        
        logger.info("Association table is finished")

    def _find_and_load_overlaps(self, target_geom, bonus_geom):
        # TODO dry this out and use this batching for all load patterns

        logger.info(f'Finding overlaps between {target_geom} and {bonus_geom}')
        target_iter = Geography.objects.filter(
            geography_type__name=target_geom
        ).iterator(chunk_size=settings.SMALL_CHUNK_SIZE)

        for target in target_iter:
            
            bonus_iter = (
                Geography.objects.filter(
                    geography_type__name=bonus_geom,
                    boundary__intersects=target.boundary,
                )
                .exclude(boundary__touches=target.boundary)
                .iterator()
            )

            while True:
                try:
                    batch = list(islice(bonus_iter, settings.SMALL_CHUNK_SIZE))
                except Exception as e:
                    logger.error(f"Error with the batch : {e}")
                    batch = []
                logger.info(f"Size of batch to load: {sys.getsizeof(batch)}")
                if not batch:
                    logger.info(f"Loading finished for : {target_geom} {target}")
                    break
                assocs = []
                for bonus in batch:
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
                    TargetBonusAssoc.objects.bulk_create(assocs, settings.SMALL_CHUNK_SIZE, update_conflicts=True, unique_fields=["target_geography", "bonus_geography"], update_fields=["target_geography_type", "bonus_geography_type"])


    def _find_and_load_matching_state_fips(self, target_geom, bonus_geom):
        logger.info(f'Finding overlaps between {target_geom} and {bonus_geom}')
        target_iter = Geography.objects.filter(
            geography_type__name=target_geom
        ).iterator(chunk_size=settings.SMALL_CHUNK_SIZE)

        for target in target_iter:
            assocs = []
            bonus_iter = (
                Geography.objects.annotate(
                    state_fips = Substr("fips_info", 1, 2)
                ).filter(
                    geography_type__name=bonus_geom,
                    state_fips=target.fips_info,
                )
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
            
            while True:
                batch = list(islice(bonus_iter, settings.SMALL_CHUNK_SIZE))
                logger.info(f"Size of batch to load: {sys.getsizeof(batch)}")
                if not batch:
                    logger.info(f"Loading finished for : {target_geom} {target}")
                    break
                assocs = []
                for bonus in batch:
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



    def _find_and_load_matching_county_fips(self, target_geom, bonus_geom):
        logger.info(f'Finding overlaps between {target_geom} and {bonus_geom}')
        target_iter = Geography.objects.filter(
            geography_type__name=target_geom
        ).iterator(chunk_size=settings.SMALL_CHUNK_SIZE)

        for target in target_iter:
            logger.info(f'\nTarget : {target.fips_info}')
            assocs = []
            bonus_iter = (
                Geography.objects.filter(
                    geography_type__name=bonus_geom,
                    fips_info=target.fips_info,
                )
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
            # logger.info(f"Finished iterating bonuses, assocs : {assocs}")
            while True:
                batch = list(islice(bonus_iter, settings.SMALL_CHUNK_SIZE))
                logger.info(f"Size of batch to load: {sys.getsizeof(batch)}")
                if not batch:
                    logger.info(f"Loading finished for : {target_geom} {target}")
                    break
                assocs = []
                for bonus in batch:
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
        conn = connections[db_string]
        if conn:
            conn.close()
