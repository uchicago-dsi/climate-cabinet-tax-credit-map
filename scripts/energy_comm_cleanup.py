#-*- coding: utf-8 -*-
## Load Dependencies
import os
import pandas as pd
import geopandas as gpd

##Set working directory and file save paths
WD = os.path.join(os.getcwd(), 'data')
COAL_SHP_PATH = os.path.join(WD, "ira_data_coalclosure_energycomm_20231","IRA_Coal_Closure_Energy_Comm_SHP","Coal_Closure_Energy_Communities_shp", \
                             "Coal_Closure_Energy_Communities.shp") #Coal closure dataset
COAL_SAVE_PATH = os.path.join(WD, "communities","energy_coal") #Save path for coal closure dataset
FFE_SHP_PATH = os.path.join(WD, "ira_data_msanmsa_ffe_20231","MSA_NMSA_FFE_SHP","MSA_NMSA_FFE_SHP.shp") #Fossil fuel employment dataset
FFE_SAVE_PATH = os.path.join(WD, "communities","energy_ffe") #Save path for fossil fuel employment dataset

##Define a function to load the Coal Closure data and clean it
def load_coal_data() -> gpd.GeoDataFrame:
    try:
        coal_df = gpd.read_file(COAL_SHP_PATH).to_crs(epsg=3857)
        drop_cols_coal = ['objectid', 'affgeoid_t', 'fipstate_2', 'fipcounty_', 'geoid_coun','fiptract_2','censustrac','date_last_','dataset_ve']
        coal_df.drop(columns=drop_cols_coal, inplace=True)
        coal_df.rename(columns={'geoid_trac':'TractID', 'state_name':'State','county_nam':'County','mine_closu':'mine_clos',\
                                'generator_':'gen_clos','adjacent_t':'adj_clos'}, inplace=True)
        coal_df.loc[:, 'Type'] = 'Energy Community'
        coal_df.loc[:, 'Subtype'] = 'Energy - Coal Closure'
        return coal_df
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f'Error loading coal data: {e}')
        return None

##Define a function to save the cleaned data
def save_coal_data(coal_df: gpd.GeoDataFrame, save_path: str) -> None:
    try:
        if not os.path.exists(COAL_SAVE_PATH):
            os.mkdir(COAL_SAVE_PATH) 
        coal_df.to_file(save_path, driver='ESRI Shapefile')
        print(f'Coal data saved to {COAL_SAVE_PATH}')
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f'Error saving coal data: {e}')

##Define a function to load the Fossil Fuel Employment data and clean it
def load_ffe_data() -> gpd.GeoDataFrame:
    try:
        ffe_df = gpd.read_file(FFE_SHP_PATH).to_crs(epsg=3857)
        drop_cols_ffe = ['ObjectID','fipstate_2','fipscty_20','geoid_cty_','MSA_area_I','Date_Last_','Dataset_ve'] 
        ffe_df.drop(columns=drop_cols_ffe, inplace=True)
        ffe_df.rename(columns = {'AFFGEOID_C':'TractIDcty','state_name':'State','county_nam':'County','FFE_qual_s':'is_FFE','MSA_NMSA_L':'M_NMSA_loc',\
                                    'Shape_Leng':'Leng_Cty','Shape_Area':'Area_Cty'}, inplace=True)
        ffe_df.loc[:, 'Type'] = 'Energy Community'
        ffe_df.loc[:, 'Subtype'] = 'Energy - Fossil Fuel Employment'
        return ffe_df
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f'Error loading FFE data: {e}')
        return None
    
##Define a function to save the cleaned data
def save_ffe_data(ffe_df: gpd.GeoDataFrame, save_path: str) -> None:
    try:
        if not os.path.exists(FFE_SAVE_PATH):
            os.mkdir(FFE_SAVE_PATH) 
        ffe_df.to_file(save_path, driver='ESRI Shapefile')
        print(f'FFE data saved to {FFE_SAVE_PATH}')
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f'Error saving FFE data: {e}')

##Make a main function to run the script
def main():
    coal_df = load_coal_data()
    if coal_df is not None:
        save_coal_data(coal_df, os.path.join(COAL_SAVE_PATH, 'coal_closure.shp'))
    ffe_df = load_ffe_data()
    if ffe_df is not None:
        save_ffe_data(ffe_df, os.path.join(FFE_SAVE_PATH, 'ffe.shp'))

if __name__ == '__main__':
    main()