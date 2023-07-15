#-*- coding: utf-8 -*-
## Load Dependencies
import os
import pandas as pd
import geopandas as gpd
import hydra
import logging

## Configure the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

def load_coal_data(input_path:str) -> gpd.GeoDataFrame:
    """
    Load and clean the Coal Closure data.

    Args:
        input_path: Path to the Coal Closure data.

    Returns:
        gpd.GeoDataFrame: Cleaned Coal Closure data.
    """
    try:
        coal_df = gpd.read_file(input_path).to_crs(epsg=3857)
        drop_cols_coal = ['objectid', 'affgeoid_t', 'fipstate_2', 'fipcounty_', 'geoid_coun','fiptract_2','censustrac','date_last_','dataset_ve']
        coal_df.drop(columns=drop_cols_coal, inplace=True)
        coal_df.rename(columns={'geoid_trac':'TractID', 'state_name':'State','county_nam':'County','mine_closu':'mine_clos',\
                                'generator_':'gen_clos','adjacent_t':'adj_clos'}, inplace=True)
        coal_df.loc[:, 'Type'] = 'Energy Community'
        coal_df.loc[:, 'Subtype'] = 'Energy - Coal Closure'
        #Compute the area of the geometry
        coal_df.loc[:, 'area_coal'] = coal_df.geometry.area
        return coal_df
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error loading coal data: {e}')
        return None

def save_gdf(gdf: gpd.GeoDataFrame, save_path: str) -> None:
    """
    Save the cleaned GeoDataFrame to a file.

    Args:
        gdf: Cleaned GeoDataFrame.
        save_path: Path to save the data.

    Returns:
        None
    """
    try:
        gdf.to_file(save_path, driver='ESRI Shapefile')
        logger.info(f'Data saved to {save_path}')
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error saving the data: {e}')

def load_ffe_data(input_path:str) -> gpd.GeoDataFrame:
    """
    Load and clean the Fossil Fuel Employment data.

    Args:
        input_path: Path to the Fossil Fuel Employment data.

    Returns:
        gpd.GeoDataFrame: Cleaned Fossil Fuel Employment data.
    """
    try:
        ffe_df = gpd.read_file(input_path).to_crs(epsg=3857)
        drop_cols_ffe = ['ObjectID','fipstate_2','fipscty_20','geoid_cty_','MSA_area_I','Date_Last_','Dataset_ve'] 
        ffe_df.drop(columns=drop_cols_ffe, inplace=True)
        ffe_df.rename(columns = {'AFFGEOID_C':'TractIDcty','state_name':'State','county_nam':'County','FFE_qual_s':'is_FFE','MSA_NMSA_L':'M_NMSA_loc',\
                                    'Shape_Leng':'Leng_Cty','Shape_Area':'Area_Cty'}, inplace=True)
        ffe_df.loc[:, 'Type'] = 'Energy Community'
        ffe_df.loc[:, 'Subtype'] = 'Energy - Fossil Fuel Employment'
        #Compute the area of the geometry
        ffe_df.loc[:, 'area_ffe'] = ffe_df.geometry.area
        return ffe_df
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f'Error loading FFE data: {e}')
        return None

@hydra.main(config_path='../conf', config_name='config')
def main(cfg) -> None:
    paths = cfg.paths
    WD = os.getcwd().replace('\\', '/')
    os.chdir(WD)
    energy_paths = {
        'coal_shp_path': os.path.join(WD, paths.energy.coal_shp_path).replace('\\', '/'),
        'coal_clean_path': os.path.join(WD, paths.energy.coal_clean_path).replace('\\', '/'),
        'ffe_shp_path': os.path.join(WD, paths.energy.ffe_shp_path).replace('\\', '/'),
        'ffe_clean_path': os.path.join(WD, paths.energy.ffe_clean_path).replace('\\', '/')#,
        #'energy_path': os.path.join(WD, paths.energy.energy_path).replace('\\', '/')  
    }
    for path in energy_paths.values():
        os.makedirs(os.path.dirname(path), exist_ok=True)
    coal_df = load_coal_data(energy_paths['coal_shp_path'])
    if coal_df is not None:
        save_gdf(coal_df, energy_paths['coal_clean_path'])
    ffe_df = load_ffe_data(energy_paths['ffe_shp_path'])
    if ffe_df is not None:
        save_gdf(ffe_df, energy_paths['ffe_clean_path'])

if __name__ == '__main__':
    main()