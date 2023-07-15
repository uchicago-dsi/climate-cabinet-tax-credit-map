#-*- coding: utf-8 -*-
## Load Dependencies
import os
import pandas as pd
import numpy as np
import geopandas as gpd
import hydra
import logging
import warnings
# Disable Fiona warnings
warnings.filterwarnings("ignore", category=UserWarning, module="fiona")

## Configure the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

def load_utility_data(input_path:str, state_path: str) -> gpd.GeoDataFrame:
    """
    Load the Utility Datasets (Rural CoOps and Municipal Utilities) and clean them.

    Args:
        input_path (str): Path to the utility shape file.
        state_path (str): Path to the state abbreviations dataset.

    Returns:
        gpd.GeoDataFrame: Cleaned utility data as a GeoDataFrame or None if an error occurs.
    """
    try:
        utility_territories = gpd.read_file(input_path).to_crs(epsg=3857)
        util_cols_to_remove = ['OBJECTID','SOURCE','SOURCEDATE','VAL_METHOD','VAL_DATE']
        utility_territories.drop(util_cols_to_remove, axis = 1, inplace = True)
        utility_territories.rename(columns = {'STATE':'ST_Code'}, inplace = True)
        ##Load an external dataset with the state names and abbreviations
        states = pd.read_csv(state_path)[['Abbreviation','State']].rename(columns = {'Abbreviation':'ST_Code'})
        util_merged = utility_territories.merge(gpd.GeoDataFrame(states), how='left', on='ST_Code')
        #Compute the area of the geometry
        util_merged['area'] = np.round(util_merged['geometry'].area, 4)
        util_merged = util_merged.query('(TYPE == "MUNICIPAL") | (TYPE == "POLITICAL SUBDIVISION") | (TYPE == "COOPERATIVE")').to_crs(epsg=3857)
        #Change the column to contain either Coop or Municipality
        util_merged['Type'] = util_merged['TYPE'].apply(lambda x: 'Rural Co-Op' if x == 'COOPERATIVE' else 'Municipal/Public Utility')
        return util_merged
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.error(f'Error loading utility data: {e}')
        return None

def save_cleaned_utility_data(util_data: gpd.GeoDataFrame, output_path: str) -> None:
    """
    Save the cleaned utility data as an ESRI Shapefile.

    Args:
        util_data (gpd.GeoDataFrame): Cleaned utility data as a GeoDataFrame.
        output_path (str): Path to save the cleaned utility data.

    Returns:
        None
    """
    try:
        util_data.to_file(output_path, driver='ESRI Shapefile')
        logger.info(f'Cleaned utility data saved to {output_path}')
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.error(f'Error saving cleaned utility data: {e}')

def separate_utilities(util_data: gpd.GeoDataFrame, rural_output_path: str, municipal_output_path: str) -> None:
    """
    Separate the utilities into rural cooperatives and municipal utilities and save them as ESRI Shapefiles.

    Args:
        util_data (gpd.GeoDataFrame): Cleaned utility data as a GeoDataFrame.
        rural_output_path (str): Path to save the rural cooperatives data.
        municipal_output_path (str): Path to save the municipal utilities data.

    Returns:
        None
    """
    try:
        rural_coops = util_data.query('(Type == "Rural Co-Op")').to_crs(epsg=3857)
        rural_coops.to_file(rural_output_path, driver='ESRI Shapefile')
        logger.info(f'Rural cooperatives data saved to {rural_output_path}')
        
        municipal_utils = util_data.query('(Type == "Municipal/Public Utility")').to_crs(epsg=3857)
        municipal_utils.to_file(municipal_output_path, driver='ESRI Shapefile')
        logger.info(f'Municipal utilities data saved to {municipal_output_path}')
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.error(f'Error saving separated utility data: {e}')
        return None

@hydra.main(config_path='../conf', config_name='config')
def main(cfg) -> None:
    paths = cfg.paths
    WD = os.getcwd().replace('\\', '/')
    os.chdir(WD)  # Set the working directory explicitly
    util_paths = {
        "UTIL_SHAPE_FILE_PATH": os.path.join(WD, paths.utilities.util_shape_file_path).replace('\\', '/'),
        "UTIL_CLEAN_PATH": os.path.join(WD, paths.utilities.util_clean_path).replace('\\', '/'),
        "RURAL_COOPS_PATH": os.path.join(WD, paths.utilities.rural_coops_path).replace('\\', '/'),
        "MUNICIPAL_UTILS_PATH": os.path.join(WD, paths.utilities.municipal_utils_path).replace('\\', '/'),
        "STATE_FIPS_CSV_PATH": os.path.join(WD, paths.boundaries.state_fips_path).replace('\\', '/')
    }
    for path in util_paths.values():
        os.makedirs(os.path.dirname(path), exist_ok=True) 
    util_merged = load_utility_data(util_paths['UTIL_SHAPE_FILE_PATH'], util_paths['STATE_FIPS_CSV_PATH'])
    if util_merged is not None:
        save_cleaned_utility_data(util_merged, util_paths['UTIL_CLEAN_PATH'])
        separate_utilities(util_merged, util_paths['RURAL_COOPS_PATH'], util_paths['MUNICIPAL_UTILS_PATH'])

if __name__ == '__main__':
    main()