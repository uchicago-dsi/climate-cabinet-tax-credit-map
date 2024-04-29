"""Handles geography linkages and intersections.
"""

# Standard library imports
from typing import Dict, List

# Third-party imports
import geopandas as gpd
import pandas as pd
import shapely
from django.conf import settings
from django.db import connection

# Application imports
from tax_credit.models import Geography
from tax_credit.population import PopulationService


class AssociationsService:
    """Joins geographies of different types and adds metadata to their associations."""

    STATE_FIPS_MATCH_OPTIONS = [
        (Geography.GeographyType.STATE, Geography.GeographyType.ENERGY),
        (Geography.GeographyType.STATE, Geography.GeographyType.JUSTICE40),
        (Geography.GeographyType.STATE, Geography.GeographyType.LOW_INCOME),
    ]
    """Geography types that can be joined by state FIPS code."""

    COUNTY_FIPS_MATCH_OPTIONS = [
        (Geography.GeographyType.COUNTY, Geography.GeographyType.ENERGY),
        (Geography.GeographyType.COUNTY, Geography.GeographyType.JUSTICE40),
        (Geography.GeographyType.COUNTY, Geography.GeographyType.LOW_INCOME),
    ]
    """Geography types that can be joined by county FIPS code."""

    SPATIAL_OVERLAP_MATCH_OPTIONS = [
        (Geography.GeographyType.STATE, Geography.GeographyType.DISTRESSED),
        (Geography.GeographyType.COUNTY, Geography.GeographyType.DISTRESSED),
        (Geography.GeographyType.MUNICIPAL_UTILITY, Geography.GeographyType.DISTRESSED),
        (Geography.GeographyType.MUNICIPAL_UTILITY, Geography.GeographyType.ENERGY),
        (Geography.GeographyType.MUNICIPAL_UTILITY, Geography.GeographyType.JUSTICE40),
        (Geography.GeographyType.MUNICIPAL_UTILITY, Geography.GeographyType.LOW_INCOME),
        (Geography.GeographyType.MUNICIPALITY, Geography.GeographyType.DISTRESSED),
        (Geography.GeographyType.MUNICIPALITY, Geography.GeographyType.ENERGY),
        (Geography.GeographyType.MUNICIPALITY, Geography.GeographyType.JUSTICE40),
        (Geography.GeographyType.MUNICIPALITY, Geography.GeographyType.LOW_INCOME),
        (Geography.GeographyType.RURAL_COOPERATIVE, Geography.GeographyType.DISTRESSED),
        (Geography.GeographyType.RURAL_COOPERATIVE, Geography.GeographyType.ENERGY),
        (Geography.GeographyType.RURAL_COOPERATIVE, Geography.GeographyType.JUSTICE40),
        (Geography.GeographyType.RURAL_COOPERATIVE, Geography.GeographyType.LOW_INCOME),
    ]
    """Geography types that can only be joined by a spatial intersection."""

    def __init__(self, population_service: PopulationService) -> None:
        """Initializes a new instance of an `AssociationsService`.

        Args:
            `None`

        Returns:
            `None`
        """
        self._population_service = population_service

    def find_bonus_matches(self, target_type: str, bonus_type: str) -> List[Dict]:
        """Finds tax credit bonus geography records that "match"
        a target record according to the most accurate strategy (e.g.,
        a shared FIPS code or the existence of a spatial intersection).

        Args:
            target_typ (`str`): The type of target geographies to search.

            bonus_type (`str`): The type of bonus geographies to search.

        Returns:
            (`list` of `Dict`): The bonus geography matches.
        """
        lookup_key = (target_type, bonus_type)

        if lookup_key in self.STATE_FIPS_MATCH_OPTIONS:
            return self.within_state(bonus_type)

        elif lookup_key in self.COUNTY_FIPS_MATCH_OPTIONS:
            return self.within_county(bonus_type)

        elif lookup_key in self.SPATIAL_OVERLAP_MATCH_OPTIONS:
            return self.within_spatial_overlap(target_type, bonus_type)

        else:
            all_options = [
                f"Target: {target}, Bonus: {bonus}"
                for target, bonus in (
                    self.STATE_FIPS_MATCH_OPTIONS
                    + self.COUNTY_FIPS_MATCH_OPTIONS
                    + self.SPATIAL_OVERLAP_MATCH_OPTIONS
                )
            ]
            raise ValueError(
                "Received an unexpected combination of target and bonus "
                f"geography types: Target ({target_type}), Bonus (bonus_type). "
                f"Expected one of the following instead: {'; '.join(all_options)}."
            )

    def within_county(self, bonus_type: str) -> List[Dict]:
        """Finds intersections between counties and records of
        the bonus type using an attribute join (i.e., shared
        county FIPS code). The bonus geography is assumed to
        fall completely within the county.

        Args:
            bonus_type (`str`): The type of bonus geographies to search.

        Returns:
            (`list` of `dict`): The bonus geography matches.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    target.id AS target_id,
                    bonus.id AS bonus_id,
                    bonus.population,
                    %s AS population_strategy
                FROM tax_credit_geography target, tax_credit_geography bonus
                WHERE (
                    target.geography_type =  %s AND
                    bonus.geography_type = %s AND
                    SUBSTRING(target.fips, 1, 5) = SUBSTRING(bonus.fips, 1, 5)
                );
                """,
                [
                    Geography.PopulationCalculation.FIPS,
                    Geography.GeographyType.COUNTY,
                    bonus_type,
                ],
            )
            return cursor.fetchall()

    def within_spatial_overlap(self, target_type: str, bonus_type: str) -> List[Dict]:
        """Finds spatial intersections between geographies
        of the target type and geographies of the bonus type
        while excluding cases where the borders touch or
        barely overlap due to geometry imprecisions.

        Args:
            bonus_type (`str`): The type of bonus geographies to search.

        Returns:
            (`list` of `dict`): The bonus geography matches.
        """
        # Find all spatial intersections between target and bonus geographies
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    target.id AS target_id,
                    target.population AS target_population,
                    bonus.id AS bonus_id,
                    bonus.population AS bonus_population,
                    ST_COLLECTIONEXTRACT(
                        ST_INTERSECTION(target.geometry, bonus.geometry), 3
                    ) AS geometry,
                    ST_SRID(target.geometry) AS srid
                FROM tax_credit_geography target, tax_credit_geography bonus
                WHERE (
                    target.geography_type = %s AND
                    bonus.geography_type = %s AND
                    ST_INTERSECTS(target.geometry, bonus.geometry) AND
                    ST_AREA(ST_INTERSECTION(target.geometry, bonus.geometry)) > %s	
                );
                """,
                [target_type, bonus_type, settings.INTERSECTION_AREA_THRESHOLD],
            )
            matches = cursor.fetchall()

        # Return if no intersections found
        if not matches:
            return []

        # Otherwise, read records into GeoDataFrame
        crs = f"EPSG:{matches[0][-1]}"
        df = pd.DataFrame(
            matches,
            columns=[
                "target_id",
                "target_population",
                "bonus_id",
                "bonus_population",
                "geometry",
                "srid",
            ],
        )
        df["geometry"] = df["geometry"].apply(shapely.from_wkb)
        gdf = gpd.GeoDataFrame(df, geometry="geometry", crs=crs)

        # Join records with population-weighted centroids to aggregate population counts
        gdf["id"] = gdf["target_id"].astype(str) + ", " + gdf["bonus_id"].astype(str)
        merged_gdf = self._population_service.centroids_sjoin(gdf, id_col="id")

        # Ensure population estimate isn't greater than those of overlapping geographies
        merged_gdf["population"] = merged_gdf[
            ["target_population", "bonus_population", "population"]
        ].min(axis=1)

        # Subset to final columns
        merged_gdf = merged_gdf[
            ["target_id", "bonus_id", "population", "population_strategy"]
        ]

        # Return as records
        return list(merged_gdf.itertuples(index=False, name=None))

    def within_state(self, bonus_type: str) -> List[Dict]:
        """Finds intersections between states and records of
        the bonus type using an attribute join (i.e., shared
        state FIPS code). The bonus geography is assumed to
        fall completely within the state.

        Args:
            bonus_type (`str`): The type of bonus geographies to search.

        Returns:
            (`list` of `dict`): The bonus geography matches.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    target.id AS target_id,
                    bonus.id AS bonus_id,
                    bonus.population,
                    %s AS population_strategy
                FROM tax_credit_geography target, tax_credit_geography bonus
                WHERE (
                    target.geography_type =  %s AND
                    bonus.geography_type = %s AND
                    SUBSTRING(target.fips, 1, 2) = SUBSTRING(bonus.fips, 1, 2)
                );
                """,
                [
                    Geography.PopulationCalculation.FIPS,
                    Geography.GeographyType.STATE,
                    bonus_type,
                ],
            )
            return cursor.fetchall()
