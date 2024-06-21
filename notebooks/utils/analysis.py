"""Classes and functions used in data analyses.
"""

# Standard library imports
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import List

# Third-party imports
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
from IPython.display import display, HTML

# Application imports
from .constants import ALBERS, CLEAN_ANALYSIS_DIR
from .interpolation import areal_interpolation, point_interpolation


@dataclass
class OriginGeo:
    """Defines the data source/reference geography to interpolate."""

    name: str
    """The geography name (e.g., "block groups")."""

    area_gdf: gpd.GeoDataFrame
    """A representation of the geography as areas. """

    point_gdf: gpd.GeoDataFrame
    """A representation of the geography as points (e.g., centroids)."""

    val_col: str
    """The name of the column containing the value to interpolate."""


@dataclass
class TargetGeo:
    """Defines the geography that receives the interpolation estimates."""

    name: str
    """The geography name (e.g., "rural co-ops")."""

    input_fpath: Path
    """The path to the geography input file."""

    output_fpath: Path
    """The path to write the interpolation results."""


def _map_intersections(
    target_gdf: gpd.GeoDataFrame,
    target_name_col: str,
    target_ref_col: str,
    target_point_col: str,
    target_areal_col: str,
    target_ratio_col: str,
    points_gdf: gpd.GeoDataFrame,
    areas_gdf: gpd.GeoDataFrame,
    area_geography_type: str,
    html_file_name: str,
) -> None:
    """Maps the target geographies and all origin geographies
    (i.e., points and areas) that intersect with it, writes the
    result to an HTML file, and then opens the map in a web browser.

    Args:
        target_gdf (`gpd.GeoDataFrame`): The geographies to plot.

        target_name_col (`str`): The column storing the target
            geography names, which are displayed on the map tooltip.

        target_ref_col (`str`): The column storing the target geographies'
            reference/official values, which are displayed on the map tooltip.

        target_point_col (`str`): The column storing the point interpolation
            estimates for the target geographies.

        target_areal_col (`str`): The column storing the areal interpolation
            estimates for the target geographies.

        points_gdf (`gpd.GeoDataFrame`): The points that were used
            as the data source for interpolation.

        areas_gdf (`gpd.GeoDataFrame`): The areas that were used as the
            data source for interpolation.

        area_entity_type (`str`): A description of the area's geography type
            (e.g., "TRACT", "BLOCK GROUP"). Displayed on the map tooltip.

        html_file_name (`str`): The name to use for the HTML file.
            Saved under the project subdirectory `data/clean/analysis`.

    Returns:
        `None`
    """
    # Subset and rename columns
    col_map = {
        target_name_col: "NAME",
        target_ref_col: "OFFICIAL POPULATION",
        target_point_col: "POINT INTERPOLATION POPULATION",
        target_areal_col: "AREAL INTERPOLATION POPULATION",
        target_ratio_col: "POINT/AREAL RATIO",
        "geometry": "geometry",
    }
    target_gdf = target_gdf.rename(columns=col_map)[list(col_map.values())]

    # Project target, point, and area data to same CRS
    proj_target_gdf = target_gdf.to_crs(ALBERS)
    proj_point_gdf = points_gdf.to_crs(ALBERS)
    proj_area_gdf = areas_gdf.to_crs(ALBERS)

    # Create GeoDataFrame of areas that intersect target
    area_matches = proj_target_gdf.sjoin(
        proj_area_gdf, how="left", predicate="intersects"
    )
    filter = proj_area_gdf.index.isin(area_matches["index_right"].tolist())
    intersecting_areas_gdf = (
        proj_area_gdf[filter]
        .loc[:, ["POPULATION", "geometry"]]
        .rename(
            columns={"POPULATION": f"{area_geography_type.upper()} POPULATION"}
        )
        .dropna()
    )

    # Create GeoDataFrame of points within intersecting areas
    point_matches = intersecting_areas_gdf.sjoin(proj_point_gdf, how="left")
    filter = proj_point_gdf.index.isin(point_matches["index_right"].tolist())
    intersecting_pts_gdf = (
        proj_point_gdf[filter]
        .loc[:, ["POPULATION", "geometry"]]
        .rename(columns={"POPULATION": "CENTROID POPULATION"})
        .dropna()
    )

    # Initialize map with targets and intersecting areas
    fmap = intersecting_areas_gdf.explore()
    fmap = target_gdf.explore(m=fmap, color="green")

    # If any intersecting points exist, add to map
    if len(intersecting_pts_gdf):
        fmap = intersecting_pts_gdf.explore(m=fmap, color="red")

    # Write result to HTML file
    fpath = f"{CLEAN_ANALYSIS_DIR}/{html_file_name}"
    fmap.save(fpath)

    # Launch map in web browser
    webbrowser.open(fpath)


def _plot_distribution(df: pd.DataFrame, cols: List[str]) -> None:
    """Plots the distribution of the given columns in the DataFrame
    using an informational table, histogram, and box-and-whisker plot.

    Args:
        df (`pd.DataFrame`): The DataFrame.

        cols (`list` of `str`): The columns to plot.

    Returns:
        `None`
    """
    # Display informational table
    display(df[cols].describe())

    # Display box plot
    box = df[cols].plot.box(rot=90, title="Box-and-Whisker Plot")
    plt.tight_layout()
    plt.show()

    # Display histogram
    hist = df[cols].plot.hist(
        stacked=True, bins=100, density=True, grid=True, title="Histogram"
    )
    plt.show()


def get_interpolations(
    target_geo: TargetGeo,
    origin_geos: List[OriginGeo],
    use_cached: bool = True,
) -> gpd.GeoDataFrame:
    """Loads interpolated data for the target geography from
    file if it exists and the cache option is specified. Otherwise,
    interpolates the data anew and persists the result to the cache
    —overwriting any previously-saved file—before returning the result.

    Args:
        target_geo (`TargetGeo`): The target geography.

        use_cached (`bool`): A boolean indicating whether the
            the data should be loaded from file if it is available.

    Returns:
        (`gpd.GeoDataFrame`): The interpolation results.
    """
    # Attempt to load interpolation results from file if indicated
    if use_cached:
        try:
            return gpd.read_parquet(target_geo.output_fpath)
        except FileNotFoundError:
            pass

    # Otherwise,load target geography dataset
    target_gdf = gpd.read_parquet(target_geo.input_fpath)

    # Store reference to pre-computed population
    reference_pop_col = "reference_pop"
    reference_pops = target_gdf["population"].astype(float)
    pop_cols = [(reference_pop_col, reference_pops)]

    # Subset columns to speed processing
    target_gdf = target_gdf[["name", "geometry"]].copy()

    # Interpolate values from each origin data source and store results
    for origin in origin_geos:

        # Estimate target geography populations using centroid strategy
        centroid_estimates = point_interpolation(
            target_gdf,
            origin.point_gdf,
            target_key_col="name",
            centroid_val_col="POPULATION",
        )

        # Estimate target geography populations using areal strategy
        areal_estimates = areal_interpolation(
            target_gdf,
            origin.area_gdf,
            target_key_col="name",
            area_val_col="POPULATION",
        )

        # Standardize origin name
        std_origin_name = origin.name.lower().replace(" ", "_")

        # Append centroid estimates to results
        centroid_col = f"{std_origin_name}_centroids_pop"
        pop_cols.append((centroid_col, centroid_estimates))

        # Append areal estimates to results
        areal_col = f"{std_origin_name}_areal_pop"
        pop_cols.append((areal_col, areal_estimates))

        # Append difference between centroid, reference estimates to results
        centroid_diff_col = f"{std_origin_name}_centroids_ref_pop_diff"
        centroid_diffs = centroid_estimates - reference_pops
        pop_cols.append((centroid_diff_col, centroid_diffs))

        # Append difference between areal, reference estimates to results
        areal_diff_col = f"{std_origin_name}_areal_ref_pop_diff"
        areal_diffs = areal_estimates - reference_pops
        pop_cols.append((areal_diff_col, areal_diffs))

        # Define local function to take max ratio of population estimates
        def calculate_ratio(row: pd.Series) -> pd.Series:
            try:
                centroids_pop = row[centroid_col]
                areal_pop = row[areal_col]
                return abs(centroids_pop - areal_pop) / (
                    centroids_pop + areal_pop
                )
            except ZeroDivisionError:
                return np.nan

        # Calculate ratio
        diffs = pd.concat(
            [centroid_estimates, areal_estimates],
            keys=[centroid_col, areal_col],
            axis=1,
        )
        diffs = diffs.apply(calculate_ratio, axis=1)

        # Append column to results
        diff_col = f"{std_origin_name}_centroid_areal_pop_ratio"
        pop_cols.append((diff_col, diffs))

    # Add estimates with metadata to target geography GeoDataFrame
    for col_name, col_val in pop_cols:
        target_gdf[col_name] = col_val

    # Drop rows with any NaN value
    target_gdf = target_gdf.dropna()

    # Persist interpolations to file
    Path.mkdir(target_geo.output_fpath.parent, parents=True, exist_ok=True)
    target_gdf.to_parquet(target_geo.output_fpath)

    return target_gdf


def map_block_group_discrepancies(
    results_gdf: gpd.GeoDataFrame,
    points_gdf: gpd.GeoDataFrame,
    areas_gdf: gpd.GeoDataFrame,
    target_geo_type: str,
    threshold: float = 0.75,
) -> None:
    """Displays a map of the top discrepancies between census
    block group point and areal interpolation results.

    Args:
        results_gdf (`gpd.GeoDataFrame`): The interpolation results.

        points_gdf (`gpd.GeoDataFrame`): The points that were used
            as the data source for interpolation.

        areas_gdf (`gpd.GeoDataFrame`): The areas that were used as the
            data source for interpolation.

        target_geo_type (`str`): A description of the target geography
            type (e.g., "distressed communities"). Used in the
            map HTML file name.

        threshold (`float`): The threshold for discrepancies that
            determines which geographies should display on the map.
            Defaults to 0.75, in which case all interpolated geographies
            with a centroid/areal population ratio of 0.75 or greater
            are shown.

    Returns:
        `None`
    """
    ratio_col = "census_block_groups_centroid_areal_pop_ratio"
    std_geo_type = target_geo_type.lower().replace(" ", "_")

    _map_intersections(
        results_gdf.query(f"{ratio_col} >= {threshold}"),
        target_name_col="name",
        target_ref_col="reference_pop",
        target_point_col="census_block_groups_centroids_pop",
        target_areal_col="census_block_groups_areal_pop",
        target_ratio_col=ratio_col,
        points_gdf=points_gdf,
        areas_gdf=areas_gdf,
        area_geography_type="BLOCK GROUP",
        html_file_name=f"{std_geo_type}_discrepancies_block_group.html",
    )


def map_tract_discrepancies(
    results_gdf: gpd.GeoDataFrame,
    points_gdf: gpd.GeoDataFrame,
    areas_gdf: gpd.GeoDataFrame,
    target_geo_type: str,
    threshold: float = 0.75,
) -> None:
    """Displays a map of the top discrepancies between census
    tract point and areal interpolation results.

    Args:
        results_gdf (`gpd.GeoDataFrame`): The interpolation results.

        points_gdf (`gpd.GeoDataFrame`): The points that were used
            as the data source for interpolation.

        areas_gdf (`gpd.GeoDataFrame`): The areas that were used as the
            data source for interpolation.

        target_geo_type (`str`): A description of the target geography
            type (e.g., "distressed communities"). Used in the
            map HTML file name.

        threshold (`float`): The threshold for discrepancies that
            determines which geographies should display on the map.
            Defaults to 0.75, in which case all interpolated geographies
            with a centroid/areal population ratio of 0.75 or greater
            are shown.

    Returns:
        `None`
    """
    ratio_col = "census_tracts_centroid_areal_pop_ratio"
    std_geo_type = target_geo_type.lower().replace(" ", "_")

    _map_intersections(
        results_gdf.query(f"{ratio_col} >= {threshold}"),
        target_name_col="name",
        target_ref_col="reference_pop",
        target_point_col="census_tracts_centroids_pop",
        target_areal_col="census_tracts_areal_pop",
        target_ratio_col=ratio_col,
        points_gdf=points_gdf,
        areas_gdf=areas_gdf,
        area_geography_type="TRACT",
        html_file_name=f"{std_geo_type}_discrepancies_tract.html",
    )


def plot_population_distribution(df: pd.DataFrame) -> None:
    """Plots the distribution of all population columns in the `DataFrame`
    using a data table and stacked histograms and box-and-whisker plots.

    Args:
        df (`pd.DataFrame`): The DataFrame.

    Returns:
        `None`
    """
    _plot_distribution(
        df=df,
        cols=[
            "reference_pop",
            "census_block_groups_centroids_pop",
            "census_block_groups_areal_pop",
            "census_tracts_centroids_pop",
            "census_tracts_areal_pop",
        ],
    )


def plot_population_error_distribution(df: pd.DataFrame) -> None:
    """Plots the distribution of all population difference columns
    in the `DataFrame` using a data table and stacked histograms
    and box-and-whisker plots.

    Args:
        df (`pd.DataFrame`): The DataFrame.

    Returns:
        `None`
    """
    _plot_distribution(
        df=df,
        cols=[
            "census_block_groups_centroids_ref_pop_diff",
            "census_block_groups_areal_ref_pop_diff",
            "census_tracts_centroids_ref_pop_diff",
            "census_tracts_areal_ref_pop_diff",
        ],
    )


def run_paired_t_test(sample_a: List[float], sample_b: List[float]) -> None:
    """Performs a two-tailed, paired t-test to accept or reject
    the null hypothesis that no statistically significant
    difference exists between the means of the two randomly-sampled
    datasets and then displays the results.

    Args:
        sample_a (`list` of `float`): The first dataset.

        sample_b (`list` of `float`): The second dataset.

    Returns:
        `None`
    """
    t_statistic, p_value = stats.ttest_rel(sample_a, sample_b)
    display(
        HTML(
            f"""
            <p>t-statistic: {t_statistic}</p>
            <p>p-value: {p_value}</p>
        """
        )
    )
