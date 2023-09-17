"""Loads geographies and geography types into the database."""

from datetime import datetime
from logging import Logger
from typing import Any, Iterator

from common.storage import DataReaderFactory, IDataReader
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.core.management.base import BaseCommand, CommandParser
from geopandas import GeoDataFrame
from tax_credit.models import Census_Tract, Geography, GeographyType, Target_Bonus_Assoc
from django.db import reset_queries

from pprint import pprint

# from shapely.geometry.Multipolygon

data_reader: IDataReader = DataReaderFactory.get_reader()
logger: Logger = Logger(__file__)


class GeographyLoadJob:
    def __init__(
        self,
        file_name: str,
        geography_type_value: str,
        feature_col_in_src: str,
    ):
        """
        Creates a job loading a given parquet file into the DB

        Args:
            file_name (str): the name of the parquet file to laod
            geography_type_value (str): type of the geography -- MUST be a value in the geography type database
            feature_col_in_src (str): this is the value given to the Name field in the tax_credit_geography table
        """
        self.file_name = file_name
        self.geography_type_value = geography_type_value
        self.feature_col_in_src = feature_col_in_src

    def __str__(self):
        return f"[ Job : [ {self.file_name}, {self.geography_type_value}, {self.feature_col_in_src} ] ]"


class Command(BaseCommand):
    """Populates the `Geography` and `GeographyType` tables.

    References:
    - https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/
    - https://docs.djangoproject.com/en/4.1/topics/settings/
    """

    help = "Loads data to populate the geography type tables."

    def add_arguments(self, parser: CommandParser) -> None:
        """Updates the class' `CommandParser` with arguments passed in from the
        command line.

        Parameters:
            parser (`CommandParser`): Django's implementation of
                the `ArgParser` class from the standard library.

        Returns:
            None
        """
        parser.add_argument(
            "--smoke-test",
            action="store_true",
            help="Run the command in testing mode",
        )

        parser.add_argument(
            "--load-all",
            action="store_true",
            help="Load all data into the database",
        )

        parser.add_argument(
            "--load-states",
            action="store_true",
            help="Load state data into the database",
        )

        parser.add_argument(
            "--load-distressed",
            action="store_true",
            help="Load distressed community data into the database",
        )

        parser.add_argument(
            "--load-energy",
            action="store_true",
            help="Load energy community data into the database",
        )

        parser.add_argument(
            "--load-coal",
            action="store_true",
            help="Load coal closure community data into the database",
        )

        parser.add_argument(
            "--load-low-income",
            action="store_true",
            help="Load low income community data into the database",
        )

        parser.add_argument(
            "--load-municipal",
            action="store_true",
            help="Load municipal utility data into the database",
        )

        parser.add_argument(
            "--load-rural",
            action="store_true",
            help="Load rural coop data into the database",
        )

        parser.add_argument(
            "--load-census",
            action="store_true",
            help="Load census tract data into the database",
        )

        parser.add_argument(
            "--load-counties",
            action="store_true",
            help="Load county data into the database",
        )

        parser.add_argument(
            "--load-assoc",
            action="store_true",
            help="Loads associations between different geometries into the database",
        )

    def handle(self, *args, **options) -> None:
        """Executes the command. Accepts variable numbers of keyword and non-
        keyword arguments.

        Parameters:
            None

        Returns:
            None
        """

        # TODO check right name field used for each... dict? Ideally human readable, otherwise id

        # first load geotypes
        self._load_geo_types()

        if options.get("load_counties", False) or options.get("load_all", False):
            self._load_counties()

        # Dict is structured to iterate through and create GeographyLoadJob
        # from entries based upon commands passed to manage.py
        # Tuple is command passed to manage, file, and field in the geoparquet
        # for the load job
        jobs_dict = {
            "state": ("load_states", "state_clean.geoparquet", "State"),
            "distressed": ("load_distressed", "dci_clean.geoparquet", "zip_code"),
            "energy": ("load_energy", "ffe.geoparquet", "TractIDcty"),
            "coal_closure": ("load_coal", "coal_closure.geoparquet", "TractID"),
            "low_income": (
                "load_low-income",
                "low_income_tracts.geoparquet",
                "tractId",
            ),
            "municipal_util": ("load_municipal", "municipal_utils.geoparquet", "ID"),
            "rural_coop": ("load_rural", "rural_coops.geoparquet", "NAME"),
        }

        geo_file_load_jobs = []
        for key, value in jobs_dict.items():
            command, file, field = value
            if options.get(command, False) or options.get("load_all", False):
                # coal and energy communities need to be loaded together
                if key == "coal_closure":
                    key = "energy"
                job = GeographyLoadJob(file, key, field)
                geo_file_load_jobs.append(job)

        for job in geo_file_load_jobs:
            print(f"Loading job : {job}")
            try:
                self._load_geography_file(job, options)
            except Exception as e:
                raise RuntimeError(f"Error loading the file : {job}") from e
            print()
            reset_queries()  # Memory leak without this when DEBUG = True, https://stackoverflow.com/questions/60972577/django-postgres-memory-leak

        if options.get("load_census", False) or options.get("load_all", False):
            self._load_census_tracts()

        if options.get("load_assoc", False) or options.get("load_all", False):
            self._build_target_geo_asoc()

    def _load_census_tracts(self) -> None:
        print("Loading census tracts")

        iter_tracts: Iterator[dict[str, Any]] = data_reader.geoparquet_iterator(
            "census_tract_pop.geoparquet"
        )

        for batch in iter_tracts:
            geographies: list[Geography] = [
                Census_Tract(
                    id=row["tractId"],
                    centroid=row["geometry"].centroid,
                    population=row["total_pop"],
                )
                for row in batch
            ]
            Census_Tract.objects.bulk_create(geographies, ignore_conflicts=True)

    def _build_target_geo_asoc(self) -> None:
        print("LOADING THE ASSOCIATION TABLE")

        target_iter = Geography.objects.filter(
            geography_type__name__in=["state", "county", "municipal_util", "rural_coop"]
        ).iterator(chunk_size=1000)

        for target in target_iter:
            print(f"\t{target}")
            assocs = []
            bonus_iter = (
                Geography.objects.filter(
                    geography_type__name__in=[
                        "distressed",
                        "fossil_fuel",
                        "justice40",
                        "low_income",
                    ],
                    boundary__intersects=target.boundary,
                )
                .exclude(boundary__touches=target.boundary)
                .iterator()
            )
            for bonus in bonus_iter:
                print(f"\t\t{bonus}")
                assocs.append(
                    Target_Bonus_Assoc(
                        target_geography=target,
                        target_geography_type=target.geography_type.name,
                        bonus_geography=bonus,
                        bonus_geography_type=bonus.geography_type.name,
                    )
                )
            if assocs:
                Target_Bonus_Assoc.objects.bulk_create(assocs, ignore_conflicts=True)

    def _load_counties(self) -> None:
        """This needs custom handling as we must transform the name to include the state as well as the county itself"""
        print("Loading counties")
        geography_type = GeographyType.objects.get(name="county")

        iter_parquet: Iterator[dict[str, Any]] = data_reader.geoparquet_iterator(
            "county_clean.geoparquet"
        )

        for batch in iter_parquet:
            # r = batch[0]
            # print(f"First row : {r}")

            geographies: list[Geography] = [
                Geography(
                    name=f'{row["County"]}, {row["State"]}'.title(),
                    geography_type=geography_type,
                    boundary=self._ensure_multipolygon(row["geometry"]),
                    simple_boundary=self._ensure_multipolygon(row["geometry"]),
                    as_of=datetime.now(),  # TODO this is wrong, need to look into finding as of... probbly a column header to validate and use
                    source="county_clean.geoparquet",  # TODO again this isn't it......
                )
                for row in batch
            ]
            Geography.objects.bulk_create(geographies, ignore_conflicts=True)

    def _load_geography_file(self, job, options) -> None:
        """Helper method to load a set of geographies from a given geoparquet
        file into Postgres. This method makes the assumption that all records
        in a given geoparquet file are from the same source. the method does
        not use any sort of chunking or streaming so it should only be used for
        files that can comfortably fit in memory.

        Args:
            file_name (str): unqualified file name for a set of geographies that will be loaded into tax_credit_geography
            geography_type_value (str): value to insert for the geography-type foreign key. ** THIS MUST MATCH A VALUE IN THE GEOGRAPHY TYPE TABLE **
            src_name (str): the column name in the source geoparquet for the feature loaded from the row

        Returns:
            None
        """
        # TODO add check that geography_type is valid, i.e. exists and len 1, etc.
        # TODO validate that src_name in columns
        # TODO (probably in reader) load columns with correct types? Load only required columns?
        # second is maybe too much info to carry around and files too small to be worth it

        geography_type = GeographyType.objects.get(name=job.geography_type_value)

        iter_parquet: Iterator[dict[str, Any]] = data_reader.geoparquet_iterator(
            job.file_name, batch_size=25
        )
        if options["smoke_test"]:
            from itertools import islice

            iter_parquet = islice(iter_parquet, 1)
        logger.info(f"Read {job.file_name} to dataframe.")

        for batch in iter_parquet:
            geographies: list[Geography] = [
                Geography(
                    name=f"{row[job.feature_col_in_src]}".title(),
                    geography_type=geography_type,
                    boundary=self._ensure_multipolygon(row["geometry"]),
                    simple_boundary=self._ensure_multipolygon(row["geometry"]),
                    as_of=datetime.now(),  # TODO this is wrong, need to look into finding as of... probbly a column header to validate and use
                    source=job.file_name,  # TODO again this isn't it......
                )
                for row in batch
            ]
            Geography.objects.bulk_create(geographies, ignore_conflicts=True)
            # geographies = None
            # del(geographies)

    def _load_geo_types(self) -> None:
        """Helper method specifically to load geography types into Postgres.

        Parameters:
            None

        Returns:
            None
        """
        records = data_reader.read_csv("geography_type.csv", delimiter="|")
        print(records.head())
        geography_types = [
            GeographyType(id=geo_type["Id"], name=geo_type["Name"])
            for _, geo_type in records.iterrows()
        ]
        GeographyType.objects.bulk_create(geography_types, ignore_conflicts=True)

    def _ensure_multipolygon(self, geom: GEOSGeometry):
        """Ensures that the Django Geometry type is a multipolygon as opposed
        to a polygon as polygons cause an error in the model.

        Args:
            geom: a Geometry from a GeoDataFrame

        Returns:
            A Django multipolygon that can be inserted into
        """
        return geom if geom.geom_type == "MultiPolygon" else MultiPolygon(geom)
