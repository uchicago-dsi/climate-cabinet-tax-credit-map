from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.db import connection
from django.db.models import F, Q, Subquery
from django.db.models.functions import Substr

from common.logger import LoggerFactory
from tax_credit.config_reader import get_load_config_reader
from tax_credit.database_helper import DatabaseHelper
from tax_credit.models import Geography, TargetBonusAssoc

logger = LoggerFactory.get(__name__)

config = get_load_config_reader(settings.CONFIG_FILE)


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--target",
            nargs="+",
            default=[],
            help="Restrict to the targets that will be used for associations",
        )
        parser.add_argument(
            "--bonus",
            nargs="+",
            default=[],
            help="Restrict to the bonuses that will be used for associations",
        )

    def handle(self, *args, **options):
        for job in config.assoc_jobs:
            allowed_targets = options["target"]
            if allowed_targets:
                logger.info(f"Allowed targets {allowed_targets}")
            if allowed_targets and job.target not in allowed_targets:
                logger.info(
                    f"SKIPPING association job [ {job.target} <-> {job.bonus} ], not in allowed targets"
                )
                continue

            allowed_bonuses = options["bonus"]
            if allowed_bonuses:
                logger.info(f"Allowed bonuses : {allowed_bonuses}")
            if allowed_bonuses and job.bonus not in allowed_bonuses:
                logger.info(
                    f"SKIPPING association job [ {job.target} <-> {job.bonus} ], not in allowed bonuses"
                )
                continue

            logger.info(f"Running job : {job.job_name}")

            # cache target pk's
            target_type_filter = Q(geography_type__name=job.target)
            target_records: list = DatabaseHelper.query_and_cache(
                Geography, "id", target_type_filter
            )

            for target in target_records:
                st_time = datetime.now()

                logger.debug(f"Matching and loading [ {job.job_name} ] record : {target}")
                target_record = Geography.objects.filter(id=target.id).annotate(
                    state_fips=Substr("fips", 1, 2),
                    county_fips=Substr("fips", 1, 5)
                ).values(
                    "id", "state_fips", "county_fips", "geography_type__name"
                )[:1]

                strategy = job.assoc_strategy.lower()
                matches = self.match_fips(strategy, target_record, job.bonus)

                matches = matches.annotate(
                    target_id=target_record.values("id"),
                    target_geography_type_name=target_record.values(
                        "geography_type__name"
                    ),
                ).values(
                    bonus_geography_type=F("geography_type__name"),
                    bonus_geography_id=F("id"),
                    target_geography_type=F("target_geography_type_name"),
                    target_geography_id=F("target_id"),
                )
                raw_sql_query, params = matches.query.sql_with_params()
                insert_query = (
                    f"INSERT INTO {TargetBonusAssoc._meta.db_table} "
                    "("
                    "target_geography_type, "
                    "bonus_geography_type, "
                    "bonus_geography_id, "
                    "target_geography_id"
                    ") "
                    "SELECT "
                    "target_geography_type, "
                    "bonus_geography_type, "
                    "bonus_geography_id, "
                    "target_geography_id "
                    f"FROM ({raw_sql_query}) AS subquery "
                    "ON CONFLICT DO NOTHING"
                )
                logger.debug(f"Running parameters and query : {params} {insert_query}")
                with connection.cursor() as cursor:
                    cursor.execute(
                        insert_query,
                        params,
                    )
                match_batch_load_time = datetime.now() - st_time
                logger.debug(f"Finishled batching and loading [ {job.job_name} ] record {target} in time : {match_batch_load_time}")
                if match_batch_load_time > timedelta(minutes=1):
                    logger.warn(f"Matching and load time is getting bigger than it should be : [ {match_batch_load_time} ] for [ {job.job_name} ] [ {target} ]")
    
    def match_fips(self, strategy: str, target_record, bonus: str):
        """Matches geographies to the entities that contain them using one of several defined strategies

        Args:
            strategy (str): The name of the matching strategy to use
            target_record: The target record to match on
            bonus (str): The bonus type to match on

        Raises:
            ValueError: If the matching strategy is not defined, raises
        """
        logger.debug(f"Matching with {strategy}")
        if strategy == "fips_county":
            matches = self.match_county_fips(
                target_record.values("county_fips"), bonus
            )
        elif strategy == "fips_state":
            matches = self.match_state_fips(
                target_record.values("state_fips"), bonus
            )
        elif strategy == "overlap":
            matches = self.match_overlap(target_record.values("id"), bonus)
        else:
            raise ValueError(
                f"Invalid association strategy : {strategy}"
            )
        return matches

    def match_county_fips(self, fips, bonus: str):
        return Geography.objects.annotate(county_fips=Substr("fips", 1, 5)).filter(
            geography_type__name=str(bonus), county_fips=fips
        )

    def match_state_fips(self, fips, bonus: str):
        # It may seem a little funny matching a substring to a full fips string
        # but remember that state fips info will only have 2 characters to begin
        # with
        return Geography.objects.annotate(state_fips=Substr("fips", 1, 2)).filter(
            geography_type__name=bonus,
            state_fips=fips,
        )

    def match_overlap(self, target_id: str, bonus_type: str):
        target_boundary = Geography.objects.filter(id=target_id).values("geometry")
        return Geography.objects.filter(
            geography_type__name=bonus_type,
            geometry__intersects=Subquery(target_boundary),
        )
