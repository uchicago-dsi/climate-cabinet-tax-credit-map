from common.logger import LoggerFactory
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.db import connection
from django.db.models import F, Q, Subquery
from django.db.models.functions import Substr
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
                target_record = Geography.objects.filter(id=target.id).values(
                    "id", "fips_info", "geography_type__name"
                )[:1]

                strategy = job.assoc_strategy.lower()
                if strategy == "fips_county":
                    matches = self.match_county_fips(
                        target_record.values("fips_info"), job.bonus
                    )
                elif strategy == "fips_state":
                    matches = self.match_state_fips(
                        target_record.values("fips_info"), job.bonus
                    )
                elif strategy == "overlap":
                    matches = self.match_overlap(target_record.values("id"), job.bonus)
                else:
                    raise ValueError(
                        f"Invalid association strategy : {job.assoc_strategy}"
                    )

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
                    f"FROM ({raw_sql_query}) AS subquery"
                )
                with connection.cursor() as cursor:
                    cursor.execute(
                        insert_query,
                        params,
                    )

    def match_county_fips(self, fips_info, bonus: str):
        return Geography.objects.filter(
            geography_type__name=str(bonus), fips_info=fips_info
        )

    def match_state_fips(self, fips_info, bonus: str):
        # It may seem a little funny matching a substring to a full fips string
        # but remember that state fips info will only have 2 characters to begin
        # with
        return Geography.objects.annotate(state_fips=Substr("fips_info", 1, 2)).filter(
            geography_type__name=bonus,
            state_fips=fips_info,
        )

    def match_overlap(self, target_id: str, bonus_type: str):
        target_boundary = Geography.objects.filter(id=target_id).values("boundary")
        return Geography.objects.filter(
            geography_type__name=bonus_type,
            boundary__intersects=Subquery(target_boundary),
        )
