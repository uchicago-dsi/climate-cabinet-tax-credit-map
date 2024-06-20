"""Functions for loading and merging datasets.
"""

# Standard library import
import glob
from pathlib import Path

# Third-party imports
import geopandas as gpd
import pandas as pd
from .constants import (
    BLOCK_GROUP_POP_AREA_FPATH,
    BLOCK_GROUP_POP_CENTROIDS_FPATH,
    BLOCK_GROUPS_FPATH,
    NAD83,
    TRACT_POP_AREA_FPATH,
    TRACT_POP_CENTROIDS_FPATH,
    TRACTS_FPATH,
)


def _read_pop_centroid_file(
    fpath: Path, lat_col: str, lon_col: str, crs: str
) -> gpd.GeoDataFrame:
    """Loads population-weighted centroids into a `GeoDataFrame`.

    Args:
        fpath (`Path`): The path to the file.

        lat_col (`str`): The name of the latitude column.

        lon_col (`str`): The name of the longitude column.

        crs (`str`): The Coordinate Reference System (CRS) of the data.

    Returns:
        (`gpd.GeoDataFrame`): The loaded dataset.
    """
    centroids_df = pd.read_csv(fpath)
    geoms = gpd.points_from_xy(
        x=centroids_df[lon_col], y=centroids_df[lat_col]
    )
    return gpd.GeoDataFrame(centroids_df, geometry=geoms, crs=crs)


def _read_shapefiles(glob_pattern: Path) -> gpd.GeoDataFrame:
    """Reads one or more Shapefiles into a `GeoDataFrame`.

    Args:
        glob_pattern (`Path`): The pattern to use
            when locating the file(s).

    Returns:
        (`gpd.GeoDataFrame`): The loaded dataset.
    """
    gdf = None
    for fpath in sorted(glob.glob(glob_pattern.as_posix())):
        loaded_gdf = gpd.read_file(fpath)
        gdf = loaded_gdf if gdf is None else pd.concat([gdf, loaded_gdf])
    return gdf


def _load_boundaries(
    boundary_fpath: Path, pop_fpath: Path, pop_id_col: str, pop_val_col: str
) -> gpd.GeoDataFrame:
    """Loads generic U.S. census boundaries with
    population counts for the year 2020 into a `GeoDataFrame`.

    Args:
        boundary_fpath (`Path`): The glob pattern pointing to
            the boundary file path(s).

        pop_fpath (`Path`): The path to the file containing
            population counts for the boundaries.

        pop_id_col (`str`): The column containing the unique
            identifier for each row in the population file.

        pop_val_col (`str`): The column containing population counts.

    Returns:
        (`gpd.GeoDataFrame`): The loaded dataset.
    """
    # Load block groups
    boundaries_gdf = _read_shapefiles(boundary_fpath)

    # Load block group population counts
    pop_df = pd.read_csv(pop_fpath, sep="|")

    # Standardize GEOID column
    pop_df.loc[:, pop_id_col] = pop_df[pop_id_col].apply(
        lambda id: id.split("US")[-1]
    )

    # Merge block group population counts with block groups on GEOID
    merged_gdf = boundaries_gdf.merge(
        right=pop_df[[pop_id_col, pop_val_col]],
        how="left",
        left_on="GEOID",
        right_on=pop_id_col,
    )

    # Drop records without population (i.e., a few in island territories)
    merged_gdf = merged_gdf.query(f"{pop_val_col} == {pop_val_col}")

    # Correct population data type
    merged_gdf.loc[:, pop_val_col] = merged_gdf[pop_val_col].astype(int)

    # Rename population column
    merged_gdf = merged_gdf.rename(columns={pop_val_col: "POPULATION"})

    return merged_gdf


def load_block_groups() -> gpd.GeoDataFrame:
    """Loads U.S. census block groups with population counts
    for the year 2020 into a `GeoDataFrame`.

    Args:
        `None`

    Returns:
        (`gpd.GeoDataFrame`): The loaded dataset.
    """
    return _load_boundaries(
        boundary_fpath=BLOCK_GROUPS_FPATH,
        pop_fpath=BLOCK_GROUP_POP_AREA_FPATH,
        pop_id_col="GEOID",
        pop_val_col="POPULATION",
    )


def load_block_group_pop_centroids() -> gpd.GeoDataFrame:
    """Loads population-weighted centroids for U.S. census
    block groups for the year 2020 into a `GeoDataFrame`.

    Args:
        `None`

    Returns:
        (`gpd.GeoDataFrame`): The loaded dataset.
    """
    return _read_pop_centroid_file(
        BLOCK_GROUP_POP_CENTROIDS_FPATH,
        lat_col="LATITUDE",
        lon_col="LONGITUDE",
        crs=NAD83,
    )


def load_tracts() -> gpd.GeoDataFrame:
    """Loads U.S. census tracts with population counts
    for the year 2020 into a `GeoDataFrame`.

    Args:
        `None`

    Returns:
        (`gpd.GeoDataFrame`): The loaded dataset.
    """
    return _load_boundaries(
        boundary_fpath=TRACTS_FPATH,
        pop_fpath=TRACT_POP_AREA_FPATH,
        pop_id_col="GEO_ID",
        pop_val_col="TOTAL_POPULATION",
    )


def load_tract_pop_centroids() -> gpd.GeoDataFrame:
    """Loads population-weighted centroids for U.S. census
    tracts for the year 2020 into a `GeoDataFrame`.

    Args:
        `None`

    Returns:
        (`gpd.GeoDataFrame`): The loaded dataset.
    """
    return _read_pop_centroid_file(
        TRACT_POP_CENTROIDS_FPATH,
        lat_col="LATITUDE",
        lon_col="LONGITUDE",
        crs=NAD83,
    )
