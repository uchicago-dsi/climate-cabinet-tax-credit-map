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

##Define a function to load the Justice40 data and clean it
def load_justice40_data(input_path:str) -> gpd.GeoDataFrame:
    """
    Load and clean the Justice40 data.

    Args:
        input_path: Path to the Justice40 data.

    Returns:
        gpd.GeoDataFrame: Cleaned Justice40 data.
    """
    try:
        justice40 = gpd.read_file(input_path).to_crs(epsg=3857)
        cols_to_keep = ['GEOID10','SF', 'CF','TPF','UF_PFS','SN_C','SN_T','HRS_ET','LHE','FPL200S','UI_EXP','THRHLD','geometry']
        justice40 = justice40[cols_to_keep]
        justice40.columns = ['TractID','State','County','Tot_Pop','Unemp_Per','Disadv?','Disad_Tri?','Underinves','Low_HS_Edu','Low_Income','UI_EXP','THRHLD','geometry']
        justice_final = justice40[(justice40['Disadv?'] == 1) & (justice40['geometry'].is_valid == True)]
        justice_final.loc[:, 'Type'] = 'Justice40'
        #Compute the area of the geometry for each tract
        justice_final.loc[:, 'area_j40'] = justice_final['geometry'].area
        return justice_final
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error loading utility data: {e}')
        return None


##Define a function to save the cleaned data
def save_justice40_data(justice_final: gpd.GeoDataFrame, save_path: str) -> None:
    """
    Save the cleaned Justice40 data.

    Args:
        justice_final: Cleaned Justice40 data as a GeoDataFrame.
        save_path: Path to save the cleaned Justice40 data.

    Returns:
        None
    """
    try:
        justice_final.to_file(save_path, driver='ESRI Shapefile')
        logger.info(f'Justice40 data saved to {save_path}')
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error saving utility data: {e}')

@hydra.main(config_path='../conf', config_name='config')
def main(cfg) -> None:
    paths = cfg.paths
    WD = os.getcwd().replace('\\', '/')
    os.chdir(WD)
    j40_paths = {
        'j40_shp_path': os.path.join(WD, paths.j40.j40_shp_path).replace('\\', '/'),
        'j40_clean_path': os.path.join(WD, paths.j40.j40_clean_path).replace('\\', '/')
    }
    for path in j40_paths.values():
        os.makedirs(os.path.dirname(path), exist_ok=True)
    justice_final = load_justice40_data(j40_paths['j40_shp_path'])
    if justice_final is not None:
        save_justice40_data(justice_final, j40_paths['j40_clean_path'])

if __name__ == '__main__':
    main()