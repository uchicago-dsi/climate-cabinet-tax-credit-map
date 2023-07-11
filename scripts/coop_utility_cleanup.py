#-*- coding: utf-8 -*-
## Load Dependencies
import os
import pandas as pd
import geopandas as gpd

##Set working directory and file save paths
WD = os.path.join(os.getcwd(), 'data')
SAVE_PATH = os.path.join(WD, "coops_utilities")
if not os.path.exists(SAVE_PATH):
    os.mkdir(SAVE_PATH)
UTILITY_SHAPE_FILE_PATH = os.path.join(WD, "utility shape file", "Electric_Retail_Service_Territories.shp")
STATE_FIPS_CSV_PATH = os.path.join(WD, "state_fips.csv")
UTIL_CLEAN_DIR = os.path.join(SAVE_PATH, "util_clean")
UTIL_CLEAN_PATH = os.path.join(UTIL_CLEAN_DIR, "util_clean.shp")
RURAL_COOPS_DIR = os.path.join(SAVE_PATH, "rural_coops")
MUNICIPAL_UTILS_DIR = os.path.join(SAVE_PATH, "municipal_utils")
RURAL_COOPS_PATH = os.path.join(RURAL_COOPS_DIR, "rural_coops.shp")
MUNICIPAL_UTILS_PATH = os.path.join(MUNICIPAL_UTILS_DIR, "municipal_utils.shp")

##Define a function to load the Utility Datasets (Rural CoOps and Municipal Utilities) and clean them
def load_utility_data() -> gpd.GeoDataFrame:
    try:
        utility_territories = gpd.read_file(UTILITY_SHAPE_FILE_PATH).to_crs(epsg=3857)
        util_cols_to_remove = ['OBJECTID','SOURCE','SOURCEDATE','VAL_METHOD','VAL_DATE']
        utility_territories.drop(util_cols_to_remove, axis = 1, inplace = True)
        utility_territories.rename(columns = {'STATE':'ST_Code'}, inplace = True)
        ##Load an external dataset with the state names and abbreviations
        states = pd.read_csv(STATE_FIPS_CSV_PATH)[['Abbreviation','State']].rename(columns = {'Abbreviation':'ST_Code'})
        util_merged = utility_territories.merge(gpd.GeoDataFrame(states), how='left', on='ST_Code')
        return util_merged
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f'Error loading utility data: {e}')
        return None
    
##Define a function to save the cleaned data
def save_cleaned_utility_data(util_data: gpd.GeoDataFrame, output_path: str) -> None:
    try:
        if not os.path.exists(UTIL_CLEAN_DIR):
            os.makedirs(UTIL_CLEAN_DIR)
        util_data.to_file(output_path, driver='ESRI Shapefile')
        print(f'Cleaned utility data saved to {output_path}')
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f'Error saving cleaned utility data: {e}')

## Separate the utilities into rural cooperatives and municipal utilities
def separate_utilities(util_data: gpd.GeoDataFrame) -> None:
    rural_coops = util_data.query('(TYPE == "COOPERATIVE")').to_crs(epsg=3857)
    rural_coops['Type'] = 'Rural Co-Op'
    rural_coops['area'] = rural_coops['geometry'].area
    if not os.path.exists(RURAL_COOPS_DIR):
        os.makedirs(RURAL_COOPS_DIR)
    rural_coops.to_file(RURAL_COOPS_PATH, driver='ESRI Shapefile')
    print(f'Rural cooperatives data saved to {RURAL_COOPS_PATH}')
    
    municipal_utils = util_data.query('(TYPE == "MUNICIPAL") | (TYPE == "POLITICAL SUBDIVISION")').to_crs(epsg=3857)
    municipal_utils['Type'] = 'Municipal/Public Utility'
    municipal_utils['area'] = municipal_utils['geometry'].area
    if not os.path.exists(MUNICIPAL_UTILS_DIR):
        os.makedirs(MUNICIPAL_UTILS_DIR)
    municipal_utils.to_file(MUNICIPAL_UTILS_PATH, driver='ESRI Shapefile')
    print(f'Municipal utilities data saved to {MUNICIPAL_UTILS_PATH}')

##Make a main function to run the script
def main() -> None:
    util_merged = load_utility_data()
    if util_merged is not None:
        save_cleaned_utility_data(util_merged, UTIL_CLEAN_PATH)
        separate_utilities(util_merged)

if __name__ == '__main__':
    main()