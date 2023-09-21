"""Loads tax credit programs for geographies into the database.
"""
from ...load_job import LoadJob
from ...validator import Validator
from common.storage import DataReader, DataReaderFactory
from tax_credit.models import GeographyType, Program, CensusTract, CensusBlockGroup

from itertools import islice

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point

from common.logger import LoggerFactory

logger = LoggerFactory.get(__name__)


class Command(BaseCommand):
    """
    Populates the `Geography_Type`, `Program`, `Census_Tract` tables.
    """

    help = "Loads data to populate the geography metric table."

    def add_arguments(self, parser: CommandParser) -> None:
        """ """
        pass

    def handle(self, *args, **options) -> None:
        """ """
        logger.info("Loading base tables: geography types, programs, and census tracts")

        logger.info("Building job for geography type load")
        geography_type_load_job = self._get_geography_type_load_job()

        logger.info("Building job for program load")
        program_load_job = self._get_program_load_job()

        logger.info("Building job for census tract load")
        census_tract_load_job = self._get_census_load_job()

        logger.info("Building job for census tract load")
        census_block_group_load_job = self._get_census_blocks_load_job()

        jobs = [geography_type_load_job, program_load_job, census_tract_load_job, census_block_group_load_job]
        for job in jobs:
            logger.info(f"Loading job : {job.job_name}")

            reader: DataReader = DataReaderFactory.get(job.file_format)

            Validator.validate(job, reader)
            objs = (job.row_to_model(row) for row in reader.iterate(job.file_name, delimiter=job.delimiter))
            while True: # See django docs here for pattern, https://docs.djangoproject.com/en/4.2/ref/models/querysets/#bulk-create
                batch = list(islice(objs, settings.SMALL_CHUNK_SIZE))
                if not batch:
                    logger.info(f"Job - {job.job_name} - load finished")
                    break
                logger.info(f"Job - {job.job_name} - batch in progress")
                job.model.objects.bulk_create(
                    batch, 
                    settings.SMALL_CHUNK_SIZE, 
                    update_conflicts=True, 
                    unique_fields=job.unique_fields, 
                    update_fields=job.update_fields
                    )
        
        logger.info("Finished loading base tables")

    @staticmethod
    def _load_geography_type_row(row):
        return GeographyType(
            id = row["Id"],
            name = row["Name"],
        )
    
    def _get_geography_type_load_job(self):
        return LoadJob(
            job_name="load geography types",

            file_name=settings.GEOGRAPHY_TYPE_FILE,
            model=GeographyType,
            file_format="csv",

            row_to_model=self._load_geography_type_row,

            file_field_names=["Id", "Name"],
            required_models=[],

            unique_fields=["id"],
            update_fields=["name"],
        )

    @staticmethod
    def _load_program_type_row(row):
        return Program(
            id = row["Id"],
            name = row["Program"],
            agency = row["Agency"],
            description = row["Description"],
            base_benefit = row["Base_benefit"],
        )
    
    def _get_program_load_job(self):
        return LoadJob(
            job_name="load programs",

            file_name=settings.PROGRAM_FILE,
            model=Program,
            file_format="csv",

            row_to_model=self._load_program_type_row,

            file_field_names=["Id", "Program", "Agency", "Description", "Base_benefit"],
            required_models=[],

            unique_fields=["id"],
            update_fields=["name", "agency", "description", "base_benefit"],
        )
    
    @staticmethod
    def _load_census_tract_row(row):
        return CensusTract(
            id=row["tractId"],
            centroid=GEOSGeometry(memoryview(row["geometry"])).centroid,
            population=row["total_pop"],
        )
    
    def _get_census_load_job(self):
        return LoadJob(
            job_name="load census tracts",
            delimiter=',',

            file_name=settings.CENSUS_TRACT_FILE,
            model=CensusTract,
            file_format="geoparquet",

            row_to_model=self._load_census_tract_row,

            file_field_names=["tractId", "geometry", "total_pop"],
            required_models=[],

            unique_fields=["id"],
            update_fields=["centroid", "population"],
        )
    
    @staticmethod
    def _load_census_block_row(row):
        # logger.info(f"Row here : {row}")
        return CensusTract(
            id=f'{row["COUNTYFP"]}-{row["TRACTCE"]}-{row["BLKGRPCE"]}',
            centroid=GEOSGeometry(Point(float(row["LONGITUDE"]), float(row["LATITUDE"]))),
            population=row["POPULATION"],
        )
    
    def _get_census_blocks_load_job(self):
        return LoadJob(
            job_name="load block tracts",
            delimiter=',',

            file_name=settings.CENSUS_BLOCK_FILE,
            model=CensusBlockGroup,
            file_format="csv",

            row_to_model=self._load_census_block_row,

            file_field_names=["COUNTYFP", "TRACTCE", "BLKGRPCE", "LATITUDE", "LONGITUDE", "POPULATION"], # TODO field names
            required_models=[],

            unique_fields=["id"],
            update_fields=["centroid", "population"], # TODO field names
        )
    # TODO load census blocks
    
