from common.logger import LoggerFactory
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point

from .models import (
    CensusBlockGroup,
    CensusTract,
    Geography,
    GeographyType,
    GeographyTypeProgram,
    Program,
)

logger = LoggerFactory.get(__name__)


def ensure_geos_multipolygon(geom):
    geos_geom: GEOSGeometry = GEOSGeometry(memoryview(geom))
    return (
        geos_geom if geos_geom.geom_type == "MultiPolygon" else MultiPolygon(geos_geom)
    )


def load_geography_type_row(row):
    return GeographyType(
        id=row["Id"],
        name=row["Name"],
    )


def load_program_type_row(row):
    return Program(
        id=row["Id"],
        name=row["Program"],
        agency=row["Agency"],
        description=row["Description"],
        base_benefit=row["Base_benefit"],
    )


def load_census_tract_row(row):
    return CensusTract(
        id=row["tractId"],
        centroid=GEOSGeometry(memoryview(row["geometry"])).centroid,
        population=row["total_pop"],
    )


def load_census_block_row(row):
    return CensusBlockGroup(
        id=f'{row["STATEFP"]}-{row["COUNTYFP"]}-{row["TRACTCE"]}-{row["BLKGRPCE"]}',
        centroid=GEOSGeometry(Point(float(row["LONGITUDE"]), float(row["LATITUDE"]))),
        population=row["POPULATION"],
    )


def load_county_geography_row(row):
    geography_type = GeographyType.objects.get(name="county")
    unique_name = (
        f'{row["County"]}, {row["State"]}'
        if row["State"] is not None
        else f'{row["County"]}'
    )
    return Geography(
        name=unique_name.title(),
        geography_type=geography_type,
        boundary=ensure_geos_multipolygon(row["geometry"]),
        simple_boundary=ensure_geos_multipolygon(row["simple_boundary"]),
        as_of="2020-01-01",
        source="United States Census Bureau",
        fips_info=f'{row["STATEFP"]}{row["COUNTYFP"]}',
    )


def load_low_income_geography_row(row):
    geography_type = GeographyType.objects.get(name="low_income")
    return Geography(
        name=row["tractId"],
        geography_type=geography_type,
        boundary=ensure_geos_multipolygon(row["geometry"]),
        simple_boundary=ensure_geos_multipolygon(row["simple_boundary"]),
        as_of="2020-01-01",
        source="United States Census Bureau",
        fips_info=str(row["tractId"])[:5],
    )


def load_state_geography_row(row):
    geography_type = GeographyType.objects.get(name="state")
    return Geography(
        name=f'{row["State"]}'.title(),
        geography_type=geography_type,
        boundary=ensure_geos_multipolygon(row["geometry"]),
        simple_boundary=ensure_geos_multipolygon(row["simple_boundary"]),
        as_of="2020-01-01",
        source="United States Census Bureau",
        fips_info=row["STATEFP"],
    )


def load_coop_geography_row(row):
    geography_type = GeographyType.objects.get(name="rural_coop")
    unique_name = (
        f'{row["NAME"]}' if row["State"] is None else f'{row["NAME"]}, {row["State"]}'
    )
    return Geography(
        name=unique_name.title(),
        geography_type=geography_type,
        boundary=ensure_geos_multipolygon(row["geometry"]),
        simple_boundary=ensure_geos_multipolygon(row["simple_boundary"]),
        as_of="2022-01-01",
        source="Homeland Infrastructure Foundation-Level Data",
    )


def load_geography_program_match_row(row):
    try:
        geography_type = GeographyType.objects.get(name=row["Geography_Type"])
        program = Program.objects.get(name=row["Program"])
        return GeographyTypeProgram(
            id=row["Id"],
            geography_type=geography_type,
            program=program,
            amount_description=row["Abount_Description"],
        )
    except Exception as e:
        logger.error("ERROR!!!!! Could not process row")
        logger.error(
            f"ERROR while matching [ {GeographyType} ] for [ {row['Geography_Type']} ] "
            f"and [ {Program} ] for [ {row['Program']} ]"
        )
        raise e


def load_dci_geography_row(row):
    geography_type = GeographyType.objects.get(name="distressed")
    return Geography(
        name=row["zip_code"],
        geography_type=geography_type,
        boundary=ensure_geos_multipolygon(row["geometry"]),
        simple_boundary=ensure_geos_multipolygon(row["simple_boundary"]),
        as_of="2020-01-01",
        source="Economic Innovation Group",
    )


def load_fossil_fuel_geography_row(row):
    geography_type = GeographyType.objects.get(name="energy")
    return Geography(
        name=row["TractIDcty"],
        geography_type=geography_type,
        boundary=ensure_geos_multipolygon(row["geometry"]),
        simple_boundary=ensure_geos_multipolygon(row["simple_boundary"]),
        as_of="2023-01-01",
        source="National Energy Technology Laboratory",
        fips_info=row["TractIDcty"][-5:],
    )


def load_coal_geography_row(row):
    geography_type = GeographyType.objects.get(name="energy")
    return Geography(
        name=row["TractID"],
        geography_type=geography_type,
        boundary=ensure_geos_multipolygon(row["geometry"]),
        simple_boundary=ensure_geos_multipolygon(row["simple_boundary"]),
        as_of="2023-01-01",
        source="National Energy Technology Laboratory",
        fips_info=row["TractID"][:5],
    )


def load_j40_geography_row(row):
    geography_type = GeographyType.objects.get(name="justice40")
    return Geography(
        name=row["TractID"],
        geography_type=geography_type,
        boundary=ensure_geos_multipolygon(row["geometry"]),
        simple_boundary=ensure_geos_multipolygon(row["simple_boundary"]),
        as_of="2022-01-01",
        source="Climate and Economic Justice Screening Tool",
        fips_info=row["TractID"][:5],
    )


def load_utilities_geography_row(row):
    geography_type = GeographyType.objects.get(name="municipal_util")
    return Geography(
        name=row["ID"],
        geography_type=geography_type,
        boundary=ensure_geos_multipolygon(row["geometry"]),
        simple_boundary=ensure_geos_multipolygon(row["simple_boundary"]),
        as_of="2022-01-01",
        source="Homeland Infrastructure Foundation-Level Data",
    )
