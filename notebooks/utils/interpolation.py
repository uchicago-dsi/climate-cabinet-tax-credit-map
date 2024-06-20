"""Functions for interpolating values from one set of geographies to another.
"""

# Third-party imports
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.errors import GEOSException

# Application imports
from utils.constants import ALBERS


def point_interpolation(
    target_gdf: gpd.GeoDataFrame,
    point_gdf: gpd.GeoDataFrame,
    target_key_col: str,
    centroid_val_col: str,
) -> pd.Series:
    """Interpolates values from the point geographies
    to the target area geographies by summing the value
    of all points that fall within each area.

    Args:
        target_gdf (`gpd.GeoDataFrame`): The target areas to receive
            an estimated value.

        point_gdf (`gpd.GeoDataFrame`): The points to interpolate.

        target_key_col (`str`): The name of the column that contains
            a unique identifier for each target geography
            in the `GeoDataFrame`.

        centroid_val_col (`str`): The name of the column containing
            the value to interpolate (e.g., "POPULATION".)

    Returns:
        (`pd.Series`): The interpolated values for the target geographies.
    """
    # Ensure target and centroid geometries have same CRS
    proj_target_gdf = target_gdf.to_crs(epsg=ALBERS)
    proj_centroid_gdf = point_gdf.to_crs(epsg=ALBERS)

    # Spatially join centroids that fall within each target geometry
    joined_gdf = proj_target_gdf[[target_key_col, "geometry"]].sjoin(
        proj_centroid_gdf[[centroid_val_col, "geometry"]],
        how="left",
        predicate="contains",
    )

    # Aggregate geometries and shape output DataFrame
    return (
        joined_gdf.groupby(by=[target_key_col, "geometry"])
        .sum()
        .reset_index()
        .drop(columns="index_right")[centroid_val_col]
    )


def areal_interpolation(
    target_gdf: gpd.GeoDataFrame,
    origin_gdf: gpd.GeoDataFrame,
    target_key_col: str,
    area_val_col: str,
) -> pd.Series:
    """Interpolates values to target areas based on the
    percentage of overlap with the source/origin area.

    Args:
        target_gdf (`gpd.GeoDataFrame`): The target areas to receive
            estimated values.

        origin_gdf (`gpd.GeoDataFrame`): The source areas to interpolate.

        target_key_col (`str`): The name of the column that contains
            a unique identifier for each target geography
            in the `GeoDataFrame`.

        centroid_val_col (`str`): The name of the column containing
            the value to interpolate (e.g., "POPULATION".)

    Returns:
        (`pd.Series`): The interpolated values for the target geographies.
    """
    # Ensure target and origin geometries have same CRS
    proj_target_gdf = target_gdf.to_crs(epsg=ALBERS)
    proj_origin_gdf = origin_gdf.to_crs(epsg=ALBERS)

    # Find all target-origin geography intersection pairs
    intersected_gdf = proj_target_gdf.sjoin(
        proj_origin_gdf[[area_val_col, "geometry"]],
        how="left",
        predicate="intersects",
    )

    # Merge areas' geometries with intersections
    merged_df = intersected_gdf.merge(
        proj_origin_gdf[["geometry"]].reset_index(),
        how="left",
        left_on="index_right",
        right_on="index",
    )

    # Define local function to apportion area value
    def apportion(row: pd.Series):

        # Define target and area geometries
        target_geom = row.geometry_x
        area_geom = row.geometry_y

        # Determine intersection of geometries
        try:
            intersection_geom = target_geom.intersection(area_geom)
        except GEOSException:
            return np.nan

        # Handle case of no intersectin
        if intersection_geom is None:
            return 0

        # Apportion value to target based on intersection
        return (intersection_geom.area / area_geom.area) * row[area_val_col]

    # Apportion value
    merged_df["portion"] = merged_df.apply(apportion, axis=1)

    # Aggregate geometries and shape output DataFrame
    return (
        merged_df.loc[:, [target_key_col, "portion"]]
        .groupby(by=[target_key_col])
        .sum()
        .reset_index()
        .rename(columns={"portion": area_val_col})[area_val_col]
    )
