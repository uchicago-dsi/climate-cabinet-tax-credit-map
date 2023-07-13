#-*- coding: utf-8 -*-
## Load Dependencies
import pandas as pd
import geopandas as gpd
import numpy as np
import os

##Set working directory and file save paths
WD = os.path.join(os.getcwd(), 'data')
UTIL_COOP_PATH = os.path.join(WD, "coops_utilities","util_clean","util_clean.shp") #Rural Coops dataset
J40_PATH = os.path.join(WD, "communities","justice40","justice40.shp") #Justice40 dataset
ENERGY_COAL_PATH = os.path.join(WD, "communities", "energy_coal","coal_closure.shp") #Coal Closure dataset
ENERGY_FFE_PATH = os.path.join(WD, "communities", "energy_ffe","ffe.shp") #Fossil Fuel Unemployment dataset
#ENERGY_PATH = os.path.join(WD, "communities", "energy","energy.shp") #Energy dataset
LOW_INCOME_PATH = os.path.join(WD, "communities", "low_income","low_income_tracts.shp") #Low Income dataset
J40_OVERLAY_PATH = os.path.join(WD, "overlays", "j40_overlays.shp") #Justice40 Overlays dataset save path
COAL_OVERLAY_PATH = os.path.join(WD, "overlays", "coal_overlays.shp") #Coal Overlays dataset save path
FFE_OVERLAY_PATH = os.path.join(WD, "overlays", "ffe_overlays.shp") #Fossil Fuel Unemployment Overlays dataset save path
#ENERGY_OVERLAY_PATH = os.path.join(WD, "overlays", "energy_overlays.shp") #Energy Overlays dataset save path
LOW_INCOME_OVERLAY_PATH = os.path.join(WD, "overlays", "low_income_overlays.shp") #Low Income Overlays dataset save path

##Define a function to load the datasets
def load_data(requested_df=None):
    '''
    Load the datasets used in the analysis.
    Parameters:
    - requested_df (str): The name of the specific dataset to load. If None, all datasets are loaded.

    Returns:
    - dict or GeoDataFrame: A dictionary containing the loaded datasets or a specific dataset if requested.

    Raises:
    - ValueError: If the requested_df parameter is not a valid dataset name.
    '''
    data_dict = {"coops_utils": UTIL_COOP_PATH,"j40": J40_PATH, "coal": ENERGY_COAL_PATH,"ffe": ENERGY_FFE_PATH,"low_income": LOW_INCOME_PATH}
    if requested_df is not None:
        if requested_df not in data_dict:
            raise ValueError("Invalid requested dataframe")
        else:
            return gpd.read_file(data_dict[requested_df], driver='ESRI Shapefile').to_crs(epsg=3857)
    return {df_name: gpd.read_file(df_path, driver='ESRI Shapefile').to_crs(epsg=3857)
        for df_name, df_path in data_dict.items()}

##Define a function to make overlays and calculate the percentage of the community that is covered by the overlay
def overlays(community='j40', coops_utils=None, community_data=None):
    '''
    Make overlays between the coops_utils and the different community datasets.
    Parameters:
    - community (str): The name of the community dataset to overlay with coops_utils.
    - coops_utils (GeoDataFrame): The coops_utils dataset.
    - community_data (dict): A dictionary containing the community datasets.

    Returns:
    - GeoDataFrame: The overlay result with added columns for area of intersection and percentage coverage.

    Raises:
    - ValueError: If coops_utils or community_data is not provided or if community not within ['j40', 'coal', 'ffe', 'low_income'].
    '''
    if coops_utils is None or community_data is None:
        raise ValueError("The 'coops_utils' and 'community_data' datasets must be provided.")
    if community not in ['j40', 'coal', 'ffe', 'low_income']:
        raise ValueError("Invalid community dataset name")
    overlay_df = gpd.overlay(coops_utils, community_data, how='intersection', keep_geom_type=True)
    overlay_df['areaInters'] = overlay_df.geometry.area
    overlay_df['perc_cover'] = np.round((overlay_df['areaInters'] / overlay_df['area']) * 100, 4)

    return overlay_df

##Define a function to save the overlays
def save_overlays(overlay_df, save_path):
    """
    Save the overlays to a shapefile.

    Parameters:
    - overlay_df (GeoDataFrame): The overlay dataset to save.
    - save_path (str): The path to save the overlay dataset as a shapefile.
    """
    overlay_df.to_file(save_path)

##Make a main function to run the script
def main():
    data = load_data()
    coops_utils = data['coops_utils'] 
    j40_data = data['j40']
    coal_data = data['coal']
    ffe_data = data['ffe']
    low_income_data = data['low_income']
    j40_overlay = overlays('j40', coops_utils, j40_data)
    coal_overlay = overlays('coal', coops_utils, coal_data)
    ffe_overlay = overlays('ffe', coops_utils, ffe_data)
    low_income_overlay = overlays('low_income', coops_utils, low_income_data)

    save_overlays(j40_overlay, J40_OVERLAY_PATH)
    save_overlays(coal_overlay, COAL_OVERLAY_PATH)
    save_overlays(ffe_overlay, FFE_OVERLAY_PATH)
    save_overlays(low_income_overlay, LOW_INCOME_OVERLAY_PATH)

if __name__ == '__main__':
    main()