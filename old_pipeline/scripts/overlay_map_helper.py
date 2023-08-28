import geopandas as gpd
import numpy as np
import folium
from branca.element import Figure
import logging
import re
from shapely.geometry import box
import pyproj

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)


def overlays(
    community: str,
    coops_utils: gpd.GeoDataFrame,
    community_data: gpd.GeoDataFrame,
    consts: dict,
) -> gpd.GeoDataFrame:
    """
    Make overlays between the coops_utils and the different community datasets.
    Parameters:
    - community (str): The name of the community dataset to overlay with coops_utils/coops/municipalities.
    - coops_utils (GeoDataFrame): The coops_utils dataset or can pass just rural_coops or municipalities shape separately.
    - community_data (dict): A dictionary containing the community datasets.

    Returns:
    - GeoDataFrame: The overlay result with added columns for area of intersection and percentage coverage.

    Raises:
    - ValueError: If the community dataset name is invalid. Valid names - ['j40', 'coal', 'ffe', 'low_income', 'dci']
    """
    if coops_utils is None or community_data is None:
        raise ValueError(
            "The 'coops_utils' and 'community_data' datasets must be provided."
        )
    if community not in consts.communities:
        raise ValueError("Invalid community dataset name")
    try:
        overlay_df = gpd.overlay(
            coops_utils, community_data, how="intersection", keep_geom_type=True
        )
        overlay_df[consts.new_cols[0]] = overlay_df.geometry.area
        overlay_df[consts.new_cols[1]] = np.round(
            (overlay_df[consts.new_cols[0]] / overlay_df[consts.area]) * 100, 4
        )
        return overlay_df
    except Exception as e:
        logger.info(f"Error making the overlay: {e}")
        return None


def calculate_state_center(bounds):
    """
    Calculate the latitude and longitude of the center point for a given bounding box.

    Parameters:
        bounds (tuple): A tuple containing the bounding box coordinates in EPSG:3857 CRS format.
                        The tuple should be in the following order: (minx, miny, maxx, maxy).

    Returns:
        tuple: A tuple containing the latitude and longitude of the center point in EPSG:4326 (WGS 84) CRS format.
               The tuple is in the following order: (latitude, longitude).
    """
    try:
        bbox = box(bounds[0], bounds[1], bounds[2], bounds[3])
        target_crs = pyproj.CRS("EPSG:4326")
        original_crs = pyproj.CRS("EPSG:3857")
        transformer = pyproj.Transformer.from_crs(
            original_crs, target_crs, always_xy=True
        )
        center_lon, center_lat = transformer.transform(bbox.centroid.x, bbox.centroid.y)
        return center_lat, center_lon
    except Exception as e:
        logger.info(e)
        return None


def create_overlay_map(
    coops_utils: gpd.GeoDataFrame,
    overlays: dict,
    cty_borders: gpd.GeoDataFrame,
    state_borders: gpd.GeoDataFrame,
    type: str,
    consts: dict,
    state: str = "Illinois",
) -> folium.Map:
    """
    Create an overlay map showing multiple GeoJSON layers representing different overlays.

    Parameters:
        coops_utils (GeoDataFrame): The coops_utils dataset representing Municipal Utilities/ Rural CoOps or a combined GeoDataFrame.
        overlays (dict): A dictionary containing the overlay datasets.
        cty_borders (GeoDataFrame): The county borders dataset.
        state_borders (GeoDataFrame): The state borders dataset.
        type (str): The type of overlay. Valid values - ['coops', 'municipal']
        state (str): The state name to focus on in the map. Default is 'Illinois'.

    Returns:
        Map: The overlay map as a Folium Map object.

    Notes:
        - The input datasets must be in the same CRS (Coordinate Reference System) for proper display.
    """
    selected_state_borders = state_borders[state_borders["State"] == state]
    bounds = selected_state_borders.total_bounds
    state_center = calculate_state_center(bounds)
    fig = Figure(width=800, height=700)
    m = folium.Map(
        location=state_center, tiles=consts.tiles, zoom_start=7, control_scale=True
    )
    util_fields = list(consts.utils.fields)
    features = dict(consts.utils.features)
    if type == "coops":
        aliases = list(consts.utils.coop_aliases)
        name = consts.utils.coop_name
    elif type == "municipal":
        aliases = list(consts.utils.util_aliases)
        name = consts.utils.util_name
    else:
        raise ValueError("Invalid overlay type. Valid values - ['coops', 'municipal']")
    try:
        folium.GeoJson(
            coops_utils[coops_utils["State"] == state],
            name=name,
            style_function=lambda feature: features,
            tooltip=folium.features.GeoJsonTooltip(
                fields=util_fields, aliases=aliases, labels=True, sticky=True
            ),
            popup=None,
        ).add_to(
            m
        )  # Base layer for coops/ municipal utilities

        for overlay_name, overlay_data in overlays.items():
            overlay_name = re.sub("_coop|_muni", "", overlay_name)
            overlay_features = dict(consts.overlay_features[overlay_name])
            print(overlay_name, "\n", overlay_features)
            folium.GeoJson(
                overlay_data[overlay_data["State"] == state],
                name=consts.overlay_names[overlay_name],
                style_function=lambda feature: overlay_features,
                tooltip=folium.features.GeoJsonTooltip(
                    fields=list(consts.overlay_fields[overlay_name]),
                    aliases=list(consts.overlay_aliases[overlay_name]),
                    labels=True,
                    sticky=True,
                ),
                popup=None,
            ).add_to(m)

        folium.GeoJson(
            cty_borders[cty_borders["State"] == state],
            name=consts.ct_name,
            style_function=lambda feature: dict(consts.ct_features),
            tooltip=None,
            popup=None,
        ).add_to(m)
        folium.GeoJson(
            state_borders,
            name=consts.st_name,
            style_function=lambda feature: dict(consts.st_features),
            tooltip=None,
            popup=None,
        ).add_to(m)
        folium.LayerControl(collapsed=False).add_to(m)
        fig.add_child(m)
        return fig
    except Exception as e:
        logger.info(e)
        return None
