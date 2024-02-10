from common.logger import LoggerFactory
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point
from .models import CensusBlockGroup, Geography, Program

logger = LoggerFactory.get(__name__)


def ensure_geos_multipolygon(geom):
    geos_geom: GEOSGeometry = GEOSGeometry(memoryview(geom))
    return (
        geos_geom if geos_geom.geom_type == "MultiPolygon" else MultiPolygon(geos_geom)
    )


def load_program_row(row):
    return Program(
        id=row["Id"],
        name=row["Program"],
        agency=row["Agency"],
        description=row["Description"],
        base_benefit=row["Base_Benefit"],
        bonus_amounts=row["Bonus_Amounts"],
    )


def load_census_block_row_2010(row):
    return CensusBlockGroup(
        fips=f'{row["STATEFP"]}-{row["COUNTYFP"]}-{row["TRACTCE"]}-{row["BLKGRPCE"]}',
        centroid=GEOSGeometry(Point(float(row["LONGITUDE"]), float(row["LATITUDE"]))),
        population=row["POPULATION"],
        year=2010,
    )


def load_census_block_row_2020(row):
    return CensusBlockGroup(
        fips=f'{row["STATEFP"]}-{row["COUNTYFP"]}-{row["TRACTCE"]}-{row["BLKGRPCE"]}',
        centroid=GEOSGeometry(Point(float(row["LONGITUDE"]), float(row["LATITUDE"]))),
        population=row["POPULATION"],
        year=2020,
    )


def load_geography_dataset_row(row):
    return Geography(
        name=row["name"],
        fips="" if not row["fips"] else row["fips"],
        fips_pattern="" if not row["fips_pattern"] else row["fips_pattern"],
        geography_type=row["geography_type"],
        as_of=row["as_of"],
        published_on=row["published_on"],
        source=row["source"],
        geometry=ensure_geos_multipolygon(row["geometry"]),
    )
