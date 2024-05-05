"""Provides classes for accessing population data.
"""

# Standard library imports
import logging
import math
from typing import Optional

# Third-party imports
import geopandas as gpd
import pandas as pd

# Application imports
from common.storage import DataLoader, DataWriter
from tax_credit.models import Geography


class PopulationService:
    """A data access layer for U.S. population counts."""

    def __init__(
        self,
        pop_centroids: gpd.GeoDataFrame,
        zcta_pop_df: pd.DataFrame,
        place_pop_df: pd.DataFrame,
        cousub_pop_df: pd.DataFrame,
    ) -> None:
        """Initializes a new instance of a `PopulationService`.

        Args:
            pop_centroids (`gpd.GeoDataFrame`): The centers of population
                used to compute population totals for different geographies.

            zcta_pop_df (`pd.DataFrame`): Population totals for zip code
                tabulation areas.

            place_pop_df (`pd.DataFrame`): Population totals for census places.

            cousub_pop_df (`pd.DataFrame`): Population totals for
                census county subdivisions.

            logger (`logging.Logger`):  A standard logger instance.

        Returns:
            `None`
        """
        self._pop_centroids = pop_centroids
        self._zcta_pop_df = zcta_pop_df
        self._place_pop_df = place_pop_df
        self._cousub_pop_df = cousub_pop_df

    @staticmethod
    def _build_census_block_group_centers(
        reader: DataLoader,
        house_units_fpath: str,
        shapefile_fpath: str,
        shapefile_crs: str,
        logger: logging.Logger,
    ) -> gpd.GeoDataFrame:
        """Creates a dataset of mean centers of housing units within census
        block groups (similar to mean centers of population) using census
        blocks. Calculated using the simple formula attributed to the Census
        Bureau in the reference below, although without applying additional
        corrections to move points placed in water to land. Assumes all datasets
        are from the 2020 decennial census.

        References:
        - Edward Aboufadel & David Austin (2006) A New Method for Computing
        the Mean Center of Population of the United States, The Professional
        Geographer, 58:1, 65-69, DOI: 10.1111/j.1467-9272.2006.00512.x

        Args:
            reader (`DataLoader`): A client for reading input files
                from a local or cloud data store.

            house_units_fpath (`str`): The absolute path to the
                census block housing units data file, which consolidates
                housing unit counts across different geographies.

            shapefile_fpath (`str`): The regex pattern used to load
                census block shapefiles.

            shapefile_crs (`str`): The Coordinate Reference System (CRS)
                of the shapefile.

        Returns:
            (`gpd.GeoDataFrame`): The dataset.
        """
        # Load census blocks from shapefiles
        logger.info("Loading census blocks from shapefiles.")
        blk_gdf = None
        for pth in reader.list_directory_contents(shapefile_fpath):
            gdf = reader.read_shapefile(pth, dtype=str, crs=shapefile_crs)
            blk_gdf = gdf if blk_gdf is None else pd.concat([blk_gdf, gdf])

        # Create new GeoDataFrame using census blocks' internal points as geometries
        logger.info("Parsing census block internal points as geometries.")
        blk_pts_gdf = gpd.GeoDataFrame(
            data=blk_gdf[["GEOID20", "INTPTLAT20", "INTPTLON20"]],
            geometry=gpd.points_from_xy(
                x=blk_gdf["INTPTLON20"], y=blk_gdf["INTPTLAT20"]
            ),
            crs=shapefile_crs,
        )

        # Load census block group housing unit counts
        logger.info("Loading census block group housing unit counts.")
        house_units_df = reader.read_csv(
            file_name=house_units_fpath,
            dtype=str,
            delimiter="|",
        )

        # Correct housing column data types
        logger.info("Correcting column data types.")
        house_units_df["HOUSING_UNITS"] = house_units_df["HOUSING_UNITS"].astype(int)

        # Add new housing geo id columns to facilitate future joins and aggregations
        logger.info("Adding new column geography identifiers.")
        house_units_df["GEOID_BLK"] = (
            house_units_df["STATEFP"]
            + house_units_df["COUNTYFP"]
            + house_units_df["TRACTCE"]
            + house_units_df["BLKCE"]
        )
        house_units_df["GEOID_BLKGRP"] = (
            house_units_df["STATEFP"]
            + house_units_df["COUNTYFP"]
            + house_units_df["TRACTCE"]
            + house_units_df["BLKGRPCE"]
        )

        # Merge census block point geometries with housing counts
        logger.info("Merging census block group points with housing counts.")
        merged_blk_pts_gdf = blk_pts_gdf[["GEOID20", "geometry"]].merge(
            right=house_units_df, how="left", left_on="GEOID20", right_on="GEOID_BLK"
        )

        # Group resulting records by block group
        logger.info("Grouping merged points by census block group id.")
        grouped = merged_blk_pts_gdf.groupby(by="GEOID_BLKGRP")

        # Aggregate housing unit counts at the block group level by
        # computing the mean center of the housing units within each block group
        logger.info(
            "Iterating through block groups to compute each group's mean center "
            "latitude and longitude of housing from constituent blocks."
        )
        centers = []
        for grp_key in grouped.groups:

            # Fetch blocks within block group
            logger.info(f'Processing blocks in block group "{grp_key}".')
            grp_gdf = grouped.get_group(grp_key)

            # Remove blocks without housing units from calculation
            populated_gdf = grp_gdf.query("HOUSING_UNITS > 0")
            if not len(populated_gdf):
                logger.info("No blocks in group have housing units. Skipping.")
                continue

            # Initialize variables to simplify computation of mean center
            blk_unit_counts = populated_gdf["HOUSING_UNITS"]
            total_units = populated_gdf["HOUSING_UNITS"].sum()
            longitudes = populated_gdf["geometry"].x
            latitudes = populated_gdf["geometry"].y
            proj_latitudes = latitudes.apply(math.cos)

            # Calculate mean center latitude and longitude
            # of block group housing from blocks
            center_lat = sum(blk_unit_counts * latitudes) / total_units
            center_lon = sum(blk_unit_counts * longitudes * proj_latitudes) / sum(
                blk_unit_counts * proj_latitudes
            )

            # Append new center to list
            centers.append(
                {
                    "GEOID_BLKGRP": grp_key,
                    "STATEFP": populated_gdf["STATEFP"].iloc[0],
                    "COUNTYFP": populated_gdf["COUNTYFP"].iloc[0],
                    "TRACTCE": populated_gdf["TRACTCE"].iloc[0],
                    "BLKGRPCE": populated_gdf["BLKGRPCE"].iloc[0],
                    "LATITUDE": center_lat,
                    "LONGITUDE": center_lon,
                }
            )

        # Convert centers to GeoDataFrame
        logger.info(
            f"{len(centers)} center points generated after "
            f"processing {len(grouped)} block groups. "
            "Converting points to final GeoDataFrame."
        )
        centers_gdf = gpd.GeoDataFrame(
            data=centers,
            geometry=gpd.points_from_xy(
                x=[pt["LONGITUDE"] for pt in centers],
                y=[pt["LATITUDE"] for pt in centers],
            ),
            dtype=str,
            crs=shapefile_crs,
        )

        return centers_gdf

    @staticmethod
    def _build_census_block_group_populations(
        reader: DataLoader,
        population_fpath: str,
        shapefile_fpath: str,
        shapefile_crs: str,
        logger: logging.Logger,
    ) -> gpd.GeoDataFrame:
        """Creates a dataset of census block groups with population counts.

        Args:
            reader (`DataLoader`): A client for reading input files
                from a local or cloud data store.

            population_fpath (`str`): The absolute path to the census
                block group population data file, which consolidates
                population counts across different geographies.

            shapefile_fpath (`str`): The regex pattern used to load
                census block group shapefiles.

            shapefile_crs (`str`): The Coordinate Reference System (CRS)
                of the shapefile.

            logger (`logging.Logger`): An instance of a standard logger.

        Returns:
            (`gpd.GeoDataFrame`): The dataset.
        """
        # Loading census block group shapefiles
        logger.info("Loading census block group shapefiles.")
        blkgrp_gdf = None
        for pth in reader.list_directory_contents(shapefile_fpath):
            gdf = reader.read_shapefile(pth, dtype=str, crs=shapefile_crs)
            blkgrp_gdf = gdf if blkgrp_gdf is None else pd.concat([blkgrp_gdf, gdf])

        # Load census block group populations
        logger.info("Loading census block group population counts.")
        blkgrp_pops_df = reader.read_csv(
            file_name=population_fpath, dtype=str, delimiter="|"
        )

        # Drop null population records
        logger.info(f"{len(blkgrp_pops_df)} record(s) found. Dropping nulls.")
        blkgrp_pops_df = blkgrp_pops_df.query("POPULATION == POPULATION")
        logger.info(f"{len(blkgrp_pops_df)} record(s) remain.")

        # Merge block group geographies with block group population counts
        logger.info("Merging block group geographies with population counts.")
        blkgrp_pops_df["GEOID"] = blkgrp_pops_df["GEOID"].apply(
            lambda id: id.split("US")[-1]
        )
        blkgrp_gdf = blkgrp_gdf.merge(
            right=blkgrp_pops_df[["GEOID", "POPULATION"]], how="left", on="GEOID"
        )

        return blkgrp_gdf

    @staticmethod
    def initialize(
        reader: DataLoader,
        writer: DataWriter,
        island_blk_housing_fpath: str,
        island_blk_shapefile_fpath: str,
        island_blk_shapefile_crs: str,
        island_blk_grp_pop_fpath: str,
        island_blk_grp_shapefile_fpath: str,
        island_blk_grp_shapefile_crs: str,
        us_blk_grp_centroids_fpath: str,
        us_blk_grp_centroids_crs: str,
        output_centroids_fpath: str,
        output_centroids_crs: str,
        zcta_pop_fpath: str,
        place_pop_fpath: str,
        county_subdivision_pop_fpath: str,
        logger: logging.Logger,
    ) -> "PopulationService":
        """Creates and initializes a new `PopulationService` instance by loading
        a dataset of census block group centers of population for the U.S. and its
        territories into memory, or by creating the dataset if it does not exist.

        NOTE: To estimate populations for a wide range of geographies and
        their intersections, we use centers of population defined within census
        block groups. These centers can be joined to other geographies by attribute
        (i.e., "FIPS code") or through a spatial intersection. The Census Bureau
        reports centers of population for the 50 U.S. states, the District of
        Columbia, and Puerto Rico every decennial census. However, centers of
        population must be computed manually for the remaining Island Areas—i.e.,
        American Samoa, the Commonwealth of the Northern Mariana Islands, Guam,
        and the U.S. Virgin Islands. To establish mean centers of population at the
        block group level, one can calculate the average latitude and longitude of
        its census block's centroids (internal points), weighted by population count.
        Population count do not exist at the block level for the island areas, so
        housing unit density was used as a proxy instead.

        Args:
            reader (`DataLoader`): A client for reading input files
                from a local or cloud data store.

            writer (`DataWriter`): A client for writing data to a local
                or cloud store.

            island_blk_housing_fpath (`str`): The relative path within the
                configured data store to the file containing island area
                census block housing unit counts.

            island_blk_shapefile_fpath (`str`): The relative path within
                the configured data store to island area census block
                shapefiles. Uses a regex pattern to match multiple files.

            island_blk_shapefile_crs (`str`): The Coordinate Reference System
                (CRS) of the island area census block shapefile(s).

            island_blk_grp_pop_fpath (`str`): The relative path within the
                configured data store to the island area census block group
                population data file.

            island_blk_grp_shapefile_fpath (`str`): The relative path within
                the configured data store to island area census block
                group shapefiles. Uses a regex pattern to match multiple files.

            island_blk_grp_shapefile_crs (`str`): The Coordinate Reference
                System (CRS) of the island area census block group shapefile(s).

            us_blk_grp_centroids_fpath (`str`): The relative path within the
                configured data store to the centers of population file for
                the 50 U.S. States, District of Columbia, and Puerto Rico.

            us_blk_grp_centroids_crs (`str`): The Coordinate Reference
                System (CRS) of the census block group shapefile(s) for
                the 50 U.S. State, District of Columbia, and Puerto Rico.

            output_centroids_fpath (`str`): The relative path within the
                configured data store to the file holding the final, combined
                set of center points for all of the U.S. States, District
                of Columbia, and the Island Areas.

            output_centroids_crs (`str`): The Coordinate Reference
                System (CRS) of the final dataset of center points.

            zcta_pop_fpath (`str`): The relative path within the configured
                data store to the file containing census zip code tabulation
                area population counts.

            place_pop_fpath (`str`): The relative path within the configured
                data store to the file containing census place population counts.

            county_subdivision_pop_fpath (`str`): The relative path within the
                configured data store to the file containing census county
                subdivision population counts.

            logger (`logging.Logger`): A standard logger instance.

        Returns:
            (`PopulationService`): The store instance.
        """
        # Log start of process
        logger.info("Creating and initializing new population service.")

        # Load census zip code tabulation area population counts
        logger.info("Loading population dataset for census ZCTAs.")
        zcta_pop_df = reader.read_csv(
            file_name=zcta_pop_fpath, dtype=str, delimiter="|"
        )
        logger.info(f"{len(zcta_pop_df):,} record(s) loaded.")

        # Load census place population counts
        logger.info("Loading population dataset for census places.")
        place_pop_df = reader.read_csv(
            file_name=place_pop_fpath, dtype=str, delimiter="|"
        )
        logger.info(f"{len(place_pop_df):,} record(s) loaded.")

        # Load census county subdivision population counts
        logger.info("Loading population dataset for census county subdivisions.")
        cousub_pop_df = reader.read_csv(
            file_name=county_subdivision_pop_fpath, dtype=str, delimiter="|"
        )
        logger.info(f"{len(cousub_pop_df):,} record(s) loaded.")

        # If population centroids dataset exists, load and then instantiate store
        try:
            logger.info(
                "Attempting to load pre-existing population-weighted centroids."
            )
            all_centroids_gdf = reader.read_parquet(output_centroids_fpath)
            logger.info(
                f"{len(all_centroids_gdf):,} record(s) loaded. "
                "Instantiating new population service."
            )
            return PopulationService(
                all_centroids_gdf, zcta_pop_df, place_pop_df, cousub_pop_df
            )
        except FileNotFoundError:
            logger.info("No file found. Building dataset anew.")

        # Otherwise, compute block group center points for islands using housing density
        logger.info(
            "Initiating process to compute census block group "
            "centers of population for the U.S. Island Areas."
        )
        blk_grp_centers_gdf = PopulationService._build_census_block_group_centers(
            reader,
            island_blk_housing_fpath,
            island_blk_shapefile_fpath,
            island_blk_shapefile_crs,
            logger,
        )
        logger.info(f"{len(blk_grp_centers_gdf):,} record(s) in final dataset.")

        # Create block groups with population totals for islands
        logger.info(
            "Creating block group geometries with "
            "population totals for U.S. Island Areas."
        )
        blk_grp_pops_gdf = PopulationService._build_census_block_group_populations(
            reader,
            island_blk_grp_pop_fpath,
            island_blk_grp_shapefile_fpath,
            island_blk_grp_shapefile_crs,
            logger,
        )
        logger.info(f"{len(blk_grp_pops_gdf):,} record(s) in final dataset.")

        # Set final CRS for island datasets
        logger.info("Setting final CRS for island datasets.")
        blk_grp_centers_gdf = blk_grp_centers_gdf.to_crs(output_centroids_crs)
        blk_grp_pops_gdf = blk_grp_pops_gdf.to_crs(output_centroids_crs)

        # Merge island block group centers with populations
        logger.info("Merging block group center points and population counts.")
        blk_grp_centers_gdf = blk_grp_centers_gdf.merge(
            right=blk_grp_pops_gdf.copy()[["GEOID", "POPULATION"]],
            how="inner",
            left_on="GEOID_BLKGRP",
            right_on="GEOID",
        )
        logger.info(f"{len(blk_grp_centers_gdf):,} record(s) after merge.")

        # Drop null records
        logger.info("Dropping records without null populations.")
        blk_grp_centers_gdf = blk_grp_centers_gdf.query("POPULATION == POPULATION")
        logger.info(
            f"{len(blk_grp_centers_gdf):,} record(s) in final Island Area dataset."
        )

        # Finalize columns
        logger.info("Finalizing columns.")
        blk_grp_centers_gdf = blk_grp_centers_gdf[
            [
                "STATEFP",
                "COUNTYFP",
                "TRACTCE",
                "BLKGRPCE",
                "POPULATION",
                "LATITUDE",
                "LONGITUDE",
            ]
        ]

        # Load population-weighted centroids for remaining U.S. areas
        logger.info("Loading population-weighted centroids for remaining U.S. areas.")
        us_centroids_df = reader.read_csv(
            file_name=us_blk_grp_centroids_fpath, dtype=str
        )
        logger.info(f"{len(us_centroids_df):,} centroid(s) found.")

        # Convert to GeoDataFrame and set CRS
        logger.info("Converting centroids to GeoDataFrame.")
        us_centroids_gdf = gpd.GeoDataFrame(
            data=us_centroids_df,
            geometry=gpd.points_from_xy(
                x=us_centroids_df["LONGITUDE"], y=us_centroids_df["LATITUDE"]
            ),
            crs=us_blk_grp_centroids_crs,
        )

        # Finalize CRS
        logger.info("Setting final CRS.")
        us_centroids_gdf = us_centroids_gdf.to_crs(output_centroids_crs)

        # Combine two sets of centroids into final DataFrame
        logger.info("Combining two sets of centroids into final dataset for all U.S.")
        all_centroids_gdf = pd.concat([us_centroids_gdf, blk_grp_centers_gdf])
        logger.info(f"{len(all_centroids_gdf):,} record(s) in final dataset.")

        # Finalize columns
        logger.info("Finalizing columns.")
        all_centroids_gdf["LATITUDE"] = all_centroids_gdf["LATITUDE"].astype(float)
        all_centroids_gdf["LONGITUDE"] = all_centroids_gdf["LONGITUDE"].astype(float)
        all_centroids_gdf["POPULATION"] = all_centroids_gdf["POPULATION"].astype(int)
        all_centroids_gdf = all_centroids_gdf.sort_values(
            by=["STATEFP", "COUNTYFP", "TRACTCE", "BLKGRPCE"]
        )

        # Cache data file
        logger.info("Caching to configured storage location as GeoParquet file.")
        writer.write_geoparquet(output_centroids_fpath, all_centroids_gdf)

        # Create and return new instance of store
        logger.info("Instantiating new population service.")
        return PopulationService(
            all_centroids_gdf, zcta_pop_df, place_pop_df, cousub_pop_df
        )

    def centroids_fips_join(
        self,
        df: pd.DataFrame,
        state_col: str,
        county_col: Optional[str] = None,
        tract_col: Optional[str] = None,
    ) -> pd.DataFrame:
        """Fetches population data for a geography dataset by matching on FIPS codes.

        Args:
            df (`pd.DataFrame`): The dataset.

            state_col (`str`): The name of the column holding
                the state or state-equivalent FIPS code.

            county_col (`str`): The name of the column holding
                the county or county-equivalent FIPS code.
                Defaults to `None`, in which case the population
                merge occurs at a higher geographic level
                (i.e., state).

            tract_col (`str`): The name of the column holding
                the census tract FIPS code. Defaults to `None`,
                in which case the population merge occurs at
                a higher geographic level (i.e., state or county).

        Returns:
            (`pd.DataFrame`): A copy of the original DataFrame
                with the new merged population column, "population",
                and a column indicating the aggregation method,
                "population_strategy".
        """
        # Confirm column name given for state FIPS code
        if not state_col:
            raise ValueError("Must provide name of column containing state FIPS code.")

        # Confirm that county column name given if tract column given
        if state_col and tract_col and not county_col:
            raise ValueError(
                "Expected column name for county FIPS code if "
                "column name for census tract FIPS code provided."
            )

        # Finalize merge columns
        if state_col and county_col and tract_col:
            gdf_cols = [state_col, county_col, tract_col]
            pop_cols = ["STATEFP", "COUNTYFP", "TRACTCE"]
        elif state_col and county_col:
            gdf_cols = [state_col, county_col]
            pop_cols = ["STATEFP", "COUNTYFP"]
        else:
            gdf_cols = [state_col]
            pop_cols = ["STATEFP"]

        # Aggregate population data
        agg_pops = (
            self._pop_centroids.copy()
            .loc[:, [*pop_cols, "POPULATION"]]
            .groupby(pop_cols)
            .sum()
            .reset_index()
        )

        # Merge population counts with geographies on FIPS codes
        merged_df = df.copy().merge(
            right=agg_pops, how="left", left_on=gdf_cols, right_on=pop_cols
        )

        # Finalize population columns
        merged_df = merged_df.rename(columns={"POPULATION": "population"})
        merged_df["population_strategy"] = Geography.PopulationCalculation.FIPS

        return merged_df

    def centroids_sjoin(self, gdf: gpd.GeoDataFrame, id_col: str) -> gpd.GeoDataFrame:
        """Fetches population data for a geography dataset
        by performing a spatial join of population-weighted
        centroids (i.e., points) that fall within the geographies'
        borders (i.e., using the "contains" predicate).

        Args:
            gdf (`gpd.GeoDataFrame`): The dataset.

            id_col (`str`): The name of the column that
                provides a unique identifier for each row.

        Returns:
            (`gpd.GeoDataFrame`): A copy of the original GeoDataFrame with
                the new merged population column, "population", and a column
                indicating the aggregation method, "population_strategy".
        """
        # Reproject population to geography's CRS
        centroids = self._pop_centroids.copy().to_crs(crs=gdf.crs)

        # Compute populations for geographies from centroids falling within borders
        geo_pops = (
            gdf.copy()
            .sjoin(centroids, how="left", predicate="contains")
            .loc[:, [id_col, "POPULATION"]]
            .groupby(by=id_col)
            .sum()
            .reset_index()
        )

        # Join population counts with geography dataset
        merged_gdf = gdf.copy().merge(geo_pops, how="left", on=id_col)

        # Finalize population columns
        merged_gdf = merged_gdf.rename(columns={"POPULATION": "population"})
        merged_gdf["population"] = merged_gdf["population"].astype(int)
        merged_gdf["population_strategy"] = (
            Geography.PopulationCalculation.CENTROID_SJOIN
        )

        return merged_gdf

    def municipalities_join(
        self,
        df: pd.DataFrame,
        dataset_col: str,
        place_col: str,
        cousub_col: str,
    ) -> pd.DataFrame:
        """Adds population counts to U.S. census municipalities,
        which may be places or county subdivisions, by performing
        an attribute join on FIPS code.

        Args:
            df (`pd.DataFrame`): The dataset.

            dataset_col (`str`): The name of the column holding
                the dataset type, expected to be one of "place"
                or "county subdivisions".

            place_col (`str`): The name of the column holding
                the census place FIPS code.

            cousub_col (`str`): The name of the column holding
                the census county subdivision FIPS code.

        Returns:
            (`pd.DataFrame`): A copy of the original DataFrame with
                the new merged population column, "population", and
                a column indicating the aggregation method,
                "population_strategy".
        """
        # Split GeoDataFrame by dataset type
        places_df = df[df[dataset_col] == "places"]
        cousub_df = df[df[dataset_col] == "county subdivisions"]

        # Merge population counts with place geographies on FIPS codes
        merged_places_df = places_df.copy().merge(
            right=self._place_pop_df[["GEOID_PLACE", "TOTAL_POPULATION"]],
            how="left",
            left_on=place_col,
            right_on="GEOID_PLACE",
        )

        # Merge population counts with county subdivision geographies on FIPS codes
        merged_cousub_df = cousub_df.copy().merge(
            right=self._cousub_pop_df[["GEOID_SUBDIV", "TOTAL_POPULATION"]],
            how="left",
            left_on=cousub_col,
            right_on="GEOID_SUBDIV",
        )

        # Concatenate places and county subdivisions
        merged_munis_df = pd.concat([merged_places_df, merged_cousub_df])

        # Create final population columns
        merged_munis_df = merged_munis_df.rename(
            columns={"TOTAL_POPULATION": "population"}
        )
        merged_munis_df["population_strategy"] = Geography.PopulationCalculation.FIPS

        return merged_munis_df

    def zcta_join(self, df: pd.DataFrame, zcta_col: str) -> pd.DataFrame:
        """Adds population counts to a ZCTA dataset by
        performing an attribute join on ZCTA code.

        Args:
            df (`pd.DataFrame`): The dataset.

            zcta_col (`str`): The name of the column
                containing the ZCTA code for each row.

        Returns:
            (`pd.DataFrame`): A copy of the original DataFrame with
                the new merged population column, "population", and a column
                indicating the aggregation method, "population_strategy".
        """
        # Join population counts with ZCTA dataset
        merged_df = df.copy().merge(
            right=self._zcta_pop_df[["ZCTA5CE20", "TOTAL_POPULATION"]],
            how="left",
            left_on=zcta_col,
            right_on="ZCTA5CE20",
        )

        # Finalize population columns
        merged_df = merged_df.rename(columns={"TOTAL_POPULATION": "population"})
        merged_df["population_strategy"] = Geography.PopulationCalculation.FIPS

        return merged_df
