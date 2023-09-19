"""Loads tables with 1 level of dependency on other loaded tables.
"""

from common.logger import LoggerFactory
from tax_credit.models import GeographyTypeProgram, GeographyType, Program, Geography
from tax_credit.load_job import LoadJob
from common.storage2 import DataReader, DataReaderFactory
from ...validator import Validator

from datetime import datetime
from itertools import islice

from django.core.management.base import BaseCommand, CommandParser
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.conf import settings



logger = LoggerFactory.get(__name__)


class Command(BaseCommand):
    """Loads data into Geography_Type_Program and Geography tables. These tables have 1 level of dependency on other loaded tables.
    """

    help = "Loads data to populate the Geography_Type_Program and Geography tables. `load_base_tables` must run first."

    def add_arguments(self, parser: CommandParser) -> None:
        """
        """
        pass

    def handle(self, *args, **options) -> None:
        """This funciton builds load jobs and loads data for all tables that have a dependency on one of the base tables.
        The tables loaded here, Geography_Type_Program and Geography have the base tables as direct dependencies.
        """

        logger.info("Loading dependent tables tables: geographies and geography-program match, and census tracts")
        geography_program_match_load_job = self._get_geography_program_match_load_job()

        logger.info("Building job for state geography load")
        state_geography_load_job = self._get_state_geography_load_job()

        logger.info("Building job for county geography load")
        county_geography_load_job = self._get_county_load_job()

        logger.info("Building job for distressed community geography load")
        dci_geography_load_job = self._get_dci_geography_load_job()

        logger.info("Building job for fossil fuel geography load")
        fossil_fuel_geography_load_job = self._get_fossil_fuel_geography_load_job()

        logger.info("Building job for coal geography load")
        coal_geography_load_job = self._get_coal_geography_load_job()

        logger.info("Building job for justice 40 geography load")
        j40_geography_load_job = self._get_j40_geography_load_job()

        logger.info("Building job for low income geography load")
        low_income_geography_load_job = self._get_low_income_geography_load_job()

        logger.info("Building job for municipal utilites geography load")
        util_geography_load_job = self._get_utilities_geography_load_job()

        logger.info("Building job for rural coop geography load")
        rural_coop_load_job = self._get_rural_coop_load_job()

        jobs = [
            geography_program_match_load_job, 
            state_geography_load_job, 
            dci_geography_load_job, 
            county_geography_load_job,
            fossil_fuel_geography_load_job,
            coal_geography_load_job,
            j40_geography_load_job,
            low_income_geography_load_job,
            util_geography_load_job,
            rural_coop_load_job,
        ]
        for job in jobs:
            logger.info(f"Loading job : {job.job_name} , file : {job.file_name}")

            reader: DataReader = DataReaderFactory.get(job.file_format)

            Validator.validate(job, reader)
            objs = (job.row_to_model(row) for row in reader.iterate(job.file_name))
            while True: # See django docs here for pattern, https://docs.djangoproject.com/en/4.2/ref/models/querysets/#bulk-create
                batch = list(islice(objs, settings.MAX_BATCH_LOAD_SIZE))
                if not batch:
                    logger.info(f"Job - {job.job_name} - load finished")
                    break
                logger.info(f"Job - {job.job_name} - batch in progress")
                job.model.objects.bulk_create(
                    batch, 
                    settings.MAX_BATCH_LOAD_SIZE, 
                    update_conflicts=True, 
                    unique_fields=job.unique_fields, 
                    update_fields=job.update_fields
                    )
        
        logger.info("Finished loading base tables")

    @staticmethod
    def _ensure_geos_multipolygon(geom):
        geos_geom: GEOSGeometry = GEOSGeometry(memoryview(geom))
        return geos_geom if geos_geom.geom_type == "MultiPolygon" else MultiPolygon(geos_geom)
    
    @staticmethod
    def _load_geography_program_match_row(row):
        
        # TODO isolate db io
        
        geography_type=GeographyType.objects.get(name=row["Geography_Type"])
        program=Program.objects.get(name=row["Program"])
        return GeographyTypeProgram(
                id=row["Id"],
                geography_type=geography_type,
                program=program,
                amount_description=row["Abount_Description"],
            )

    def _get_geography_program_match_load_job(self):
        return LoadJob(
            job_name="load geography program match",

            file_name=settings.GEOGRAPHY_TYPE_PROGRAM_FILE,
            model=GeographyTypeProgram,
            file_format="csv",

            row_to_model=self._load_geography_program_match_row,

            file_field_names=["Id", "Geography_Type", "Program", "Abount_Description"],
            required_models=[GeographyType, Program],

            unique_fields=["id"],
            update_fields=["geography_type", "program", "amount_description"],
        )

    @staticmethod
    def _load_state_geography_row(row):
        geography_type = GeographyType.objects.get(name="state")
        return Geography(
            name = f'{row["State"]}'.title(),
            geography_type = geography_type,
            boundary = Command._ensure_geos_multipolygon(row['geometry']),
            simple_boundary = Command._ensure_geos_multipolygon(row['simple_boundary']),
            as_of = 2020,
            source = 'United States Census Bureau',
        )

    def _get_state_geography_load_job(self):
        return LoadJob(
            job_name="load state geography",

            file_name=settings.STATE_GEOGRAPHY_FILE,
            model=Geography,
            file_format="parquet",

            row_to_model=self._load_state_geography_row,

            file_field_names=["State", "geometry", "simple_boundary"],
            required_models=[GeographyType],

            unique_fields=["name", "geography_type"],
            update_fields=["boundary", "simple_boundary", "as_of", "source"],
        )
    
    @staticmethod
    def _load_county_geography_row(row):
        geography_type = GeographyType.objects.get(name="county")
        unique_name = f'{row["County"]}, {row["State"]}' if row["State"] != None else f'{row["County"]}'
        return Geography(
            name = unique_name.title(),
            geography_type = geography_type,
            boundary = Command._ensure_geos_multipolygon(row["geometry"]),
            simple_boundary = Command._ensure_geos_multipolygon(row["simple_boundary"]),
            as_of = 2020,
            source = 'United States Census Bureau',
        )
    
    def _get_county_load_job(self):
        return LoadJob(
            job_name = "load county geography",

            file_name = settings.COUNTY_GEOGRAPHY_FILE,
            model = Geography,
            file_format = "parquet",

            row_to_model=self._load_county_geography_row,

            file_field_names=["County", "State", "geometry", "simple_boundary"],
            required_models=[GeographyType],

            unique_fields=["name", "geography_type"],
            update_fields=["boundary", "simple_boundary", "as_of", "source"],
        )

    @staticmethod
    def _load_dci_geography_row(row):
        geography_type = GeographyType.objects.get(name="distressed")
        return Geography(
            name = row["zip_code"],
            geography_type = geography_type,
            boundary = Command._ensure_geos_multipolygon(row["geometry"]),
            simple_boundary = Command._ensure_geos_multipolygon(row["simple_boundary"]),
            as_of = 2020,
            source = 'Economic Innovation Group',
        )
    
    def _get_dci_geography_load_job(self):
        return LoadJob(
            job_name="load distressed geography",

            file_name=settings.DCI_GEOGRAPHY_FILE,
            model=Geography,
            file_format="parquet",

            row_to_model=self._load_dci_geography_row,

            file_field_names=["zip_code", "geometry", "simple_boundary"],
            required_models=[GeographyType],

            unique_fields=["name", "geography_type"],
            update_fields=["boundary", "simple_boundary", "as_of", "source"],
        )
    
    @staticmethod
    def _load_fossil_fuel_geography_row(row):
        geography_type = GeographyType.objects.get(name="energy")
        return Geography(
            name = row["TractIDcty"],
            geography_type = geography_type,
            boundary = Command._ensure_geos_multipolygon(row["geometry"]),
            simple_boundary = Command._ensure_geos_multipolygon(row["simple_boundary"]),
            as_of = 2023,
            source = 'National Energy Technology Laboratory',
        )
    
    def _get_fossil_fuel_geography_load_job(self):
        return LoadJob(
            job_name="load fossil fuel geography",

            file_name=settings.FOSSIL_FUEL_GEOGRAPHY_FILE,
            model=Geography,
            file_format="parquet",

            row_to_model=self._load_fossil_fuel_geography_row,

            file_field_names=["TractIDcty", "geometry", "simple_boundary"],
            required_models=[GeographyType],

            unique_fields=["name", "geography_type"],
            update_fields=["boundary", "simple_boundary", "as_of", "source"],
        )

    @staticmethod
    def _load_coal_geography_row(row):
        geography_type = GeographyType.objects.get(name="energy")
        return Geography(
            name = row["TractID"],
            geography_type = geography_type,
            boundary = Command._ensure_geos_multipolygon(row["geometry"]),
            simple_boundary = Command._ensure_geos_multipolygon(row["simple_boundary"]),
            as_of = 2023,
            source = 'National Energy Technology Laboratory',
        )
    
    def _get_coal_geography_load_job(self):
        return LoadJob(
            job_name="load coal geography",

            file_name=settings.COAL_GEOGRAPHY_FILE,
            model=Geography,
            file_format="parquet",

            row_to_model=self._load_coal_geography_row,

            file_field_names=["TractID", "geometry", "simple_boundary"],
            required_models=[GeographyType],

            unique_fields=["name", "geography_type"],
            update_fields=["boundary", "simple_boundary", "as_of", "source"],
        )
    
    @staticmethod
    def _load_j40_geography_row(row):
        geography_type = GeographyType.objects.get(name="justice40")
        return Geography(
            name = row["TractID"],
            geography_type = geography_type,
            boundary = Command._ensure_geos_multipolygon(row["geometry"]),
            simple_boundary = Command._ensure_geos_multipolygon(row["simple_boundary"]),
            as_of = 2022,
            source = 'Climate and Economic Justice Screening Tool',
        )
    
    def _get_j40_geography_load_job(self):
        return LoadJob(
            job_name="load justice 40 geography",

            file_name=settings.J40_GEOGRAPHY_FILE,
            model=Geography,
            file_format="parquet",

            row_to_model=self._load_j40_geography_row,

            file_field_names=["TractID", "geometry", "simple_boundary"],
            required_models=[GeographyType],

            unique_fields=["name", "geography_type"],
            update_fields=["boundary", "simple_boundary", "as_of", "source"],
        )
    
    @staticmethod
    def _load_low_income_geography_row(row):
        geography_type = GeographyType.objects.get(name="low_income")
        return Geography(
            name = row["tractId"],
            geography_type = geography_type,
            boundary = Command._ensure_geos_multipolygon(row["geometry"]),
            simple_boundary = Command._ensure_geos_multipolygon(row["simple_boundary"]),
            as_of = 2020,
            source = 'United States Census Bureau',
        )
    
    def _get_low_income_geography_load_job(self):
        return LoadJob(
            job_name = "load low income geography",

            file_name = settings.LOW_INCOME_GEOGRAPHY_FILE,
            model=Geography,
            file_format="parquet",

            row_to_model=self._load_low_income_geography_row,

            file_field_names=["tractId", "geometry", "simple_boundary"],
            required_models=[GeographyType],

            unique_fields=["name", "geography_type"],
            update_fields=["boundary", "simple_boundary", "as_of", "source"],
        )
    
    @staticmethod
    def _load_utilities_geography_row(row):
        geography_type = GeographyType.objects.get(name="municipal_util")
        return Geography(
            name = row["ID"],
            geography_type = geography_type,
            boundary = Command._ensure_geos_multipolygon(row["geometry"]),
            simple_boundary = Command._ensure_geos_multipolygon(row["simple_boundary"]),
            as_of = 2022,
            source = 'Homeland Infrastructure Foundation-Level Data',
        )
    
    def _get_utilities_geography_load_job(self):
        return LoadJob(
            job_name = "load municipal utilities geography",

            file_name = settings.MUNICIPAL_UTIL_GEOGRAPHY_FILE,
            model = Geography,
            file_format = "parquet",

            row_to_model = self._load_utilities_geography_row,
            
            file_field_names = ["ID", "geometry", "simple_boundary"],
            required_models = [GeographyType],

            unique_fields=["name", "geography_type"],
            update_fields=["boundary", "simple_boundary", "as_of", "source"],
        )
    
    @staticmethod
    def _load_coop_geography_row(row):
        geography_type = GeographyType.objects.get(name="rural_coop")
        unique_name = f'{row["NAME"]}' if row["State"] is None else f'{row["NAME"]}, {row["State"]}'
        return Geography(
            name = unique_name.title(),
            geography_type = geography_type,
            boundary = Command._ensure_geos_multipolygon(row["geometry"]),
            simple_boundary = Command._ensure_geos_multipolygon(row["simple_boundary"]),
            as_of = 2022,
            source = 'Homeland Infrastructure Foundation-Level Data',
        )
    
    def _get_rural_coop_load_job(self):
        return LoadJob(
            job_name = "load rural coop geography",

            file_name = settings.RURAL_COOP_GEOGRAPHY_FILE,
            model = Geography,
            file_format = "parquet",

            row_to_model = self._load_coop_geography_row,

            file_field_names = ["NAME", "geometry", "simple_boundary"],
            required_models=[GeographyType],

            unique_fields=["name", "geography_type"],
            update_fields=["boundary", "simple_boundary", "as_of", "source"],
        )
