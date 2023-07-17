#-*- coding: utf-8 -*-
"""
Boundary Data Preprocessing Script

This script loads and cleans county borders and state borders datasets. It processes the datasets
to ensure they are in a consistent format and projection (EPSG: 3857). The cleaned datasets are then
saved as ESRI Shapefiles.

Requirements:
- pandas
- geopandas
- hydra

Usage:
1. Ensure the necessary dependencies are installed.
2. Configure the YAML file (config.yaml) with appropriate paths for county borders, state borders, and state FIPS codes.
3. Run the script using the following command:
   python preprocess_boundaries.py

Author:Sai Krishna
Date:07-17-2023
"""

## Load Dependencies
import os
import pandas as pd
import geopandas as gpd
import logging
import hydra

## Configure the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

def load_county_borders(ct_path: str, state_fips_path: str) -> gpd.GeoDataFrame:
    """
    Load and clean the county borders dataset.

    Args:
        ct_path: Path to the county borders dataset.
        state_fips_path: Path to the state FIPS dataset.

    Returns:
        gpd.GeoDataFrame: Cleaned county borders dataset.
    """
    try:
        county_df = gpd.read_file(ct_path).to_crs(epsg=3857)
        county_df['STATEFP'] = county_df['STATEFP'].astype(int)
        states = pd.read_csv(state_fips_path)[['St_FIPS', 'State']].rename(columns={'St_FIPS':'STATEFP'})
        county_df = county_df.merge(states, on='STATEFP', how='left')
        county_df = county_df.drop(columns=['COUNTYNS','GEOID','NAME','LSAD','CLASSFP','MTFCC','CSAFP','CBSAFP','METDIVFP','FUNCSTAT'])
        county_df.rename(columns={'NAMELSAD':'County'}, inplace=True)
        return county_df
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error loading coal data: {e}')
        return None

def load_state_borders(st_path: str) -> gpd.GeoDataFrame:
    """
    Load and clean the state borders dataset.

    Args:
        st_path: Path to the state borders dataset.

    Returns:
        gpd.GeoDataFrame: Cleaned state borders dataset.
    """
    try:
        state_df = gpd.read_file(st_path).to_crs(epsg=3857)
        state_df = state_df.drop(columns=['REGION', 'DIVISION',  'STATENS', 'GEOID','LSAD','MTFCC','FUNCSTAT'])
        state_df.rename(columns={'NAME':'State'}, inplace=True)
        return state_df
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error loading coal data: {e}')
        return None

def save_gdf(gdf: gpd.GeoDataFrame, save_path:str) -> None:
    """
    Save a GeoDataFrame to a file.

    Args:
        gdf: The GeoDataFrame to be saved.
        save_path: The path to save the GeoDataFrame.

    Returns:
        None
    """
    try:
        gdf.to_file(save_path)
        logger.info(f"Saved the data to {save_path}")
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error saving the data: {e}')

@hydra.main(config_path='../conf', config_name='config')
def main(cfg) -> None:
    paths = cfg.paths
    WD = os.getcwd().replace('\\', '/')
    os.chdir(WD)  # Set the working directory explicitly
    border_paths = {
        'state_fips_path': os.path.join(WD, paths.boundaries.state_fips_path).replace('\\', '/'),
        'ct_path': os.path.join(WD, paths.boundaries.ct_path).replace('\\', '/'),
        'st_path': os.path.join(WD, paths.boundaries.st_path).replace('\\', '/'),
        'ct_clean_path': os.path.join(WD, paths.boundaries.ct_clean_path).replace('\\', '/'),
        'st_clean_path': os.path.join(WD, paths.boundaries.st_clean_path).replace('\\', '/')
    }
    for path in border_paths.values():
        os.makedirs(os.path.dirname(path), exist_ok=True)
    county_df = load_county_borders(border_paths['ct_path'], border_paths['state_fips_path'])
    state_df = load_state_borders(border_paths['st_path'])
    if (county_df is not None):
        save_gdf(county_df, border_paths['ct_clean_path'])
    if (state_df is not None):
        save_gdf(state_df, border_paths['st_clean_path'])

if __name__ == "__main__":
    main()