#-*- coding: utf-8 -*-
"""
This script performs data processing and spatial overlays on different datasets to analyze environmental justice and low-income communities.
It loads various datasets, performs necessary data cleaning and merging, and then calculates overlays between the coops_utils dataset and different community datasets.
The resulting overlays are saved as shapefiles for further analysis and visualization.

Dependencies:
- pandas
- geopandas
- numpy
- os
- hydra
- logging

Usage:
- Make sure the required dependencies are installed.
- Place the script in the desired working directory.
- Create a 'conf' folder in the working directory containing the configuration file 'config.yaml'.
- Update the 'config.yaml' file with paths to input datasets and desired output directories.
- Execute the script to perform the data processing and overlays.

Note:
- Make sure the input datasets are in ESRI Shapefile format with valid geometries.
- The script assumes the input datasets are projected in EPSG:3857 (Web Mercator) to ensure consistent spatial units for overlay operations.

Author: Sai Krishna
Date: 07-17-2023
"""

## Load Dependencies
import pandas as pd
import geopandas as gpd
import numpy as np
import os
import hydra
import logging

## Configure the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

def load_data(requested_df:str=None, paths:dict = None) -> dict or gpd.GeoDataFrame:
    '''
    Load the datasets used in the analysis.
    
    Parameters:
    - requested_df (str): The name of the specific dataset to load. If None, all datasets are loaded.
    - paths (dict): A dictionary containing the paths to the datasets.

    Returns:
    - dict or GeoDataFrame: A dictionary containing the loaded datasets or a specific dataset if requested.
    '''
    try:
        data_dict = {
            "coops_utils": paths.get('util_clean_path'),
            "j40": paths.get('j40_path'),
            "coal": paths.get('coal_path'),
            "ffe": paths.get('ffe_path'),
            "low_income": paths.get('low_income_path')
        }
        if requested_df is not None:
            return gpd.read_file(data_dict[requested_df], driver='ESRI Shapefile').to_crs(epsg=3857)
        return {df_name: gpd.read_file(df_path, driver='ESRI Shapefile').to_crs(epsg=3857)
            for df_name, df_path in data_dict.items()}
    except (FileNotFoundError, IOError, PermissionError, ValueError) as e:
        logger.info(f'Error loading the data: {e}')
        return None
    
def overlays(community:str, coops_utils:gpd.GeoDataFrame, community_data:gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    '''
    Make overlays between the coops_utils and the different community datasets.
    Parameters:
    - community (str): The name of the community dataset to overlay with coops_utils.
    - coops_utils (GeoDataFrame): The coops_utils dataset.
    - community_data (dict): A dictionary containing the community datasets.

    Returns:
    - GeoDataFrame: The overlay result with added columns for area of intersection and percentage coverage.

    Raises:
    - ValueError: If the community dataset name is invalid. Valid names - ['j40', 'coal', 'ffe', 'low_income']
    '''
    if coops_utils is None or community_data is None:
        raise ValueError("The 'coops_utils' and 'community_data' datasets must be provided.")
    if community not in ['j40', 'coal', 'ffe', 'low_income']:
        raise ValueError("Invalid community dataset name")
    try:
        overlay_df = gpd.overlay(coops_utils, community_data, how='intersection', keep_geom_type=True)
        overlay_df['areaInters'] = overlay_df.geometry.area
        overlay_df['perc_cover'] = np.round((overlay_df['areaInters'] / overlay_df['area']) * 100, 4)
        return overlay_df
    except (ValueError, TypeError) as e:
        logger.info(f'Error making the overlay: {e}')
        return None
    
def save_overlays(overlay_df:gpd.GeoDataFrame, save_path:str) -> None:
    """
    Save the overlays to a shapefile.

    Parameters:
    - overlay_df (GeoDataFrame): The overlay dataset to save.
    - save_path (str): The path to save the overlay dataset as a shapefile.
    """
    overlay_df.to_file(save_path)

@hydra.main(config_path='../conf',config_name = 'config')
def main(cfg):
    paths = cfg.paths
    WD = os.getcwd().replace('\\','/')
    os.chdir(WD)
    overlay_paths = {
        'util_clean_path' : os.path.join(WD, paths.utilities.util_clean_path).replace('\\','/'),
        'j40_path': os.path.join(WD, paths.j40.j40_clean_path).replace('\\','/'),
        'coal_path': os.path.join(WD, paths.energy.coal_clean_path).replace('\\','/'),
        'ffe_path': os.path.join(WD, paths.energy.ffe_clean_path).replace('\\','/'),
        #'energy_path" : os.path.join(WD, paths.energy.energy_path).replace('\\','/'),
        'low_income_path': os.path.join(WD, paths.low_income.low_inc_clean_path).replace('\\','/'),
        'j40_overlay_path': os.path.join(WD, paths.overlays.j40_overlay_path).replace('\\','/'),
        'coal_overlay_path': os.path.join(WD, paths.overlays.coal_overlay_path).replace('\\','/'),
        'ffe_overlay_path': os.path.join(WD, paths.overlays.ffe_overlay_path).replace('\\','/'),
        #'energy_overlay_path': os.path.join(WD, paths.overlays.energy_overlay_path).replace('\\','/'),
        'low_income_overlay_path': os.path.join(WD, paths.overlays.low_income_overlay_path).replace('\\','/')
    }
    for path in overlay_paths.values():  
        os.makedirs(os.path.dirname(path), exist_ok= True)
    data = load_data(paths = overlay_paths)
    coops_utils = data['coops_utils'] 
    j40_data = data['j40']
    coal_data = data['coal']
    ffe_data = data['ffe']
    low_income_data = data['low_income']
    j40_overlay = overlays('j40', coops_utils, j40_data)
    coal_overlay = overlays('coal', coops_utils, coal_data)
    ffe_overlay = overlays('ffe', coops_utils, ffe_data)
    low_income_overlay = overlays('low_income', coops_utils, low_income_data)

    save_overlays(j40_overlay, overlay_paths['j40_overlay_path'])
    save_overlays(coal_overlay, overlay_paths['coal_overlay_path'])
    save_overlays(ffe_overlay, overlay_paths['ffe_overlay_path'])
    save_overlays(low_income_overlay, overlay_paths['low_income_overlay_path'])

if __name__ == '__main__':
    main()