#-*- coding: utf-8 -*-
"""
Low Income Data Preprocessing Script

This script loads and cleans various low-income-related datasets, including poverty data, state level income data,
tract level income data, MSA level income data, and MSA shapefile. It then merges these datasets and applies 
low-income conditions to identify low-income tracts. The cleaned and processed data is saved as ESRI Shapefiles
for further analysis.

Requirements:
- pandas
- geopandas
- numpy
- hydra

Usage:
1. Ensure the necessary dependencies are installed.
2. Configure the YAML file (config.yaml) with the appropriate paths for the low-income datasets.
3. Run the script using the following command:
   python preprocess_low_income_data.py

Author: Sai Krishna
Date: 07-17-2023
"""

## Load Dependencies
import pandas as pd
import geopandas as gpd
import os
import numpy as np
import hydra
import logging

## Configure the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

def clean_pov_data(pov_path:str, pov_save_path:str) -> pd.DataFrame:
    """
    Cleans and saves the poverty data.

    Args:
        pov_path (str): Path to the input poverty data file.
        pov_save_path (str): Path to save the cleaned poverty data.

    Returns:
        pd.DataFrame: Cleaned poverty data as a Pandas DataFrame.
    """
    try:
        poverty_df = pd.read_csv(pov_path)
        #Remove the columns with all null values
        poverty_df = poverty_df.dropna(axis=1, how='all')
        #Removing other columns as needed as per the data dictionary
        cols_to_keep = ['Geo_STUSAB','Geo_GEOID','Geo_QName','Geo_FIPS','Geo_AREALAND','Geo_AREAWATR','ACS20_5yr_B17020001','ACS20_5yr_B17020002',]
        poverty_df = poverty_df[cols_to_keep]
        poverty_df.columns = ['state','geo_id','tract_name','tractId','area_land','area_water','total_pop','pov_pop']
        poverty_df['state'] = poverty_df['state'].apply(lambda x: x.upper())
        poverty_df['pov_perc'] = (poverty_df['pov_pop']/poverty_df['total_pop'])*100
        # poverty_df = poverty_df[poverty_df['poverty_percent'] >= 20]
        poverty_df.to_csv(pov_save_path, index=False)
        logger.info(f'Poverty data saved to {pov_save_path}')
        return poverty_df
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error loading poverty data: {e}')
        return None

def clean_tract_income_data(li_path:str, li_save_path:str) -> pd.DataFrame:
    """
    Cleans and saves the tract level income data.

    Args:
        li_path (str): Path to the input tract level income data file.
        li_save_path (str): Path to save the cleaned tract level income data.

    Returns:
        pd.DataFrame: Cleaned tract level income data as a Pandas DataFrame.
    """
    try:     
        li_df = pd.read_csv(li_path)
        #Remove the columns with all null values
        li_df = li_df.dropna(axis=1, how='all')
        #Removing other columns as needed as per the data dictionary
        li_cols_to_keep = ['Geo_STUSAB','Geo_GEOID','Geo_QName', 'Geo_FIPS', 'Geo_AREALAND', 'Geo_AREAWATR','ACS20_5yr_B19113001']
        li_df = li_df[li_cols_to_keep]
        li_df.columns = ['state','geoId','tractName','tractId','area_land','area_water','med_inc']
        li_df['state'] = li_df['state'].apply(lambda x: x.upper())
        li_df.to_csv(li_save_path, index=False)
        logger.info(f'Low income data saved to {li_save_path}')
        return li_df
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error loading low income data: {e}')
        return None
    
def clean_state_income_data(st_path:str, st_save_path:str) -> pd.DataFrame:
    """
    Cleans and saves the state level income data.

    Args:
        st_path (str): Path to the input state level income data file.
        st_save_path (str): Path to save the cleaned state level income data.

    Returns:
        pd.DataFrame: Cleaned state level income data as a Pandas DataFrame.
    """

    try:
        income_state_df = pd.read_csv(st_path)
        #Remove the columns with all null values
        income_state_df = income_state_df.dropna(axis=1, how='all')
        #Removing other columns as needed as per the data dictionary
        cols_to_keep_stw = ['Geo_STUSAB','Geo_GEOID','Geo_QName','Geo_AREALAND', 'Geo_AREAWATR','ACS20_5yr_B19113001']
        income_state_df = income_state_df[cols_to_keep_stw]
        income_state_df.columns = ['state','geoId','st_name','area_land','area_water','st_med_inc']
        income_state_df['state'] = income_state_df['state'].apply(lambda x: x.upper())
        income_state_df.to_csv(st_save_path, index=False)
        logger.info(f'State level income data saved to {st_save_path}')
        return income_state_df
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error loading state level income data: {e}')
        return None

def merge_state_tract_income(tract_df: pd.DataFrame, state_df: pd.DataFrame, merged_save_path:str):
    """
    Merges the state and tract level income data.

    Args:
        tract_df (pd.DataFrame): State level income data as a Pandas DataFrame.
        state_df (pd.DataFrame): Tract level income data as a Pandas DataFrame.
        save_path (str): Path to save the merged data.

    Returns:
        pd.DataFrame: Merged state and tract level income data as a Pandas DataFrame.
    """
    try:
        income_merged = pd.merge(tract_df, state_df, on=['state'], how='left')
        income_merged.to_csv(merged_save_path, index=False)  
        logger.info(f'Merged state and tract level income data saved to {merged_save_path}')
        return income_merged
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error merging state and tract level income data: {e}')
        return None

def clean_msa_income_data(msa_path:str, msa_save_path:str) -> pd.DataFrame:
    """
    Cleans and saves the MSA level income data.

    Args:
        msa_path (str): Path to the input MSA level income data file.
        msa_save_path (str): Path to save the cleaned MSA level income data.

    Returns:
        pd.DataFrame: Cleaned MSA level income data as a Pandas DataFrame.
    """
    try:
        income_msa_df = pd.read_csv(msa_path)
        #Remove the columns with all null values
        income_msa_df = income_msa_df.dropna(axis=1, how='all')
        #Removing other columns as needed as per the data dictionary
        msa_cols_to_keep = ['Geo_STUSAB','Geo_CBSA','Geo_GEOID','Geo_QName','Geo_FIPS','Geo_AREALAND',  'Geo_AREAWATR','ACS20_5yr_B19113001']
        income_msa_df = income_msa_df[msa_cols_to_keep]
        income_msa_df.columns = ['state','cbsaId','geoId','msaName', 'msaTractId','area_land','area_water','msa_medInc']
        income_msa_df['state'] = income_msa_df['state'].apply(lambda x: x.upper())
        income_msa_df.to_csv(msa_save_path, index=False)
        logger.info(f'MSA level income data saved to {msa_save_path}')
        return income_msa_df
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error loading MSA level income data: {e}')
        return None

def clean_msa_shp(msa_shp_path:str, msa_shp_save_path:str) -> gpd.GeoDataFrame:
    """
    Cleans and saves the MSA shapefile.

    Args:
        msa_shp_path (str): Path to the input MSA shapefile.
        msa_shp_save_path (str): Path to save the cleaned MSA shapefile.

    Returns:
        gpd.GeoDataFrame: Cleaned MSA shapefile as a GeoDataFrame.
    """
    try:
        msa_shp_df = gpd.read_file(msa_shp_path).to_crs(epsg=3857)
        # assert sum(msa_shp_df['CBSAFP']== msa_shp_df['GEOID']) == len(msa_shp_df)
        msa_shp_df = msa_shp_df[['GEOID','NAMELSAD','LSAD','ALAND','AWATER','INTPTLAT','INTPTLON','geometry']]
        msa_shp_df.columns = ['cbsaId','msaName','lsad','area_land','area_water','lat','lon','geometry']
        msa_shp_df['cbsaId'] = msa_shp_df['cbsaId'].astype(int)
        msa_shp_df.to_file(msa_shp_save_path)
        logger.info(f'MSA shapefile saved to {msa_shp_save_path}')
        return msa_shp_df
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error loading MSA shapefile: {e}')
        return None
    
def merge_msa_income_shp(msa_inc_df: pd.DataFrame, msa_shp: gpd.GeoDataFrame, merged_msa_path:str) -> gpd.GeoDataFrame:
    """
    Merges the MSA shapefile and MSA level income data.

    Args:
        msa_inc_df (pd.DataFrame): MSA level income data as a Pandas DataFrame.
        msa_shp (gpd.GeoDataFrame): MSA shapefile as a GeoDataFrame.
        merged_msa_path (str): Path to save the merged data.

    Returns:
        gpd.GeoDataFrame: Merged MSA shapefile and MSA level income data as a GeoDataFrame.
    """
    try:
        msa_income_shp = pd.merge(msa_inc_df, msa_shp[['cbsaId','lsad','lat','lon','geometry']], on=['cbsaId'], how='left')
        msa_income_shp = gpd.GeoDataFrame(msa_income_shp, geometry='geometry')
        msa_income_shp.to_file(merged_msa_path)
        logger.info(f'Merged MSA shapefile and MSA level income data saved to {merged_msa_path}')
        return msa_income_shp
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error merging MSA shapefile and MSA level income data: {e}')
        return None

def merge_all_data(pov_df: pd.DataFrame, inc_merged_df: pd.DataFrame, msa_inc_shp: gpd.GeoDataFrame, tracts_shp: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Merges all the low income datasets and the census tracts together.

    Args:
        pov_df (pd.DataFrame): Poverty data as a Pandas DataFrame.
        inc_merged_df (pd.DataFrame): Merged state and tract level income data as a Pandas DataFrame.
        msa_inc_shp (gpd.GeoDataFrame): MSA level income data with shapefile as a GeoDataFrame.
        tracts_shp (gpd.GeoDataFrame): Tracts shapefile as a GeoDataFrame.

    Returns:
        gpd.GeoDataFrame: Merged data as a GeoDataFrame.
    """
    try:
        #Merging the income_merged dataframe with the tracts shapefile
        income_shp_merged = pd.merge(inc_merged_df[['state','geoId','tractName','tractId','med_inc','st_med_inc']], 
                                tracts_shp[['stateFP','tract_id','tract_name','area_land','area_water','lat','lon','geometry']], 
                                left_on=['tractId'], right_on =['tract_id'], how='left')
        inc_pov_merged = pd.merge(income_shp_merged, pov_df[['tractId','total_pop','pov_pop','pov_perc']], on = ['tractId'], how='left')
        # Cleaning up the apprearance of the dataframe
        inc_pov_merged.drop(columns=['tract_id', 'tract_name'], inplace=True)
        #reordering how the columns appear
        inc_pov_merged = inc_pov_merged[['stateFP','state','geoId','tractId','tractName','med_inc','st_med_inc','total_pop','pov_pop',\
                                        'pov_perc','area_land','area_water','lat','lon','geometry']]
        #Convert the dataframe to a geodataframe before making spatial join
        inc_pov_merged = gpd.GeoDataFrame(inc_pov_merged, geometry='geometry')
        msa_inc_shp = gpd.GeoDataFrame(msa_inc_shp, geometry='geometry')
        #Make a spatial join with the msa_inc_shp to get the msa name and msa income for each tract
        msa_cols_to_keep = ['state','cbsaId','geoId','msaName','msaTractId','lsad','msa_medInc','geometry']
        msa_inc_shp_join = msa_inc_shp[msa_cols_to_keep]
        #rename the columns to avoid left and right suffixes
        msa_inc_shp_join.columns = ['state_msa','cbsaId','geoIdMsa','msaName','msaTractId','lsad','msa_medInc','geometry']
        final_merged_shp = gpd.sjoin(inc_pov_merged, msa_inc_shp_join, how='left', predicate='intersects').drop(columns=['index_right'])
        #Reorder the columns to make the appearance of columns better
        final_merged_shp = final_merged_shp[['stateFP','state','geoId','tractId','tractName','cbsaId','geoIdMsa','msaName','msaTractId','lsad',\
                                            'med_inc','st_med_inc','msa_medInc','total_pop','pov_pop','pov_perc','area_land','area_water','lat','lon','geometry']]
        final_merged_shp_dissolved = final_merged_shp.dissolve(by='tractId')
        #Compute the area of the geometry
        final_merged_shp_dissolved['area_LI'] = final_merged_shp_dissolved['geometry'].area
        final_merged_shp_dissolved.reset_index(inplace=True)
        return final_merged_shp_dissolved
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error merging all the datasets together: {e}')
        return None

def apply_low_income_conditions(merged_shp: gpd.GeoDataFrame, li_save_path:str) -> gpd.GeoDataFrame:
    """
    Applies low income conditions to the merged dataframe and saves it as a shapefile.

    Args:
        merged_shp (gpd.GeoDataFrame): Merged data with income and poverty information as a GeoDataFrame.
        li_save_path (str): Path to save the low income conditions applied data.

    Returns:
        gpd.GeoDataFrame: Merged data with low income conditions applied as a GeoDataFrame.
    """
    try:
        merged_shp['low_income'] = 0
        merged_shp['Type'] = ''
        #if poverty percentage is greater than 20, then the tract is low income
        merged_shp.loc[merged_shp['pov_perc'] > 20, 'low_income'] = 1
        # if the median income is less than 80% of the state median income, then the tract is low income
        merged_shp.loc[merged_shp['med_inc'] < merged_shp['st_med_inc']*0.8, 'low_income'] = 1
        #if the median income is less than 80% of the MSA median income in case if LSAD is M1, then the tract is low income
        merged_shp.loc[(merged_shp['lsad'] == 'M1') & (merged_shp['med_inc'] < merged_shp['msa_medInc']*0.8), 'low_income'] = 1
        merged_shp.loc[ :,'Type'] = 'Low Income'
        merged_shp.to_file(li_save_path, driver='ESRI Shapefile')
        logger.info(f'Low income conditions applied and saved to {li_save_path}')
        # return merged_shp
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.info(f'Error applying low income conditions: {e}')
        return None

@hydra.main(config_path='../conf', config_name='config')
def main(cfg) -> None:
    paths = cfg.paths
    WD = os.getcwd().replace("\\","/")
    os.chdir(WD)
    low_income_paths = {
        "pov_dir": os.path.join(WD, paths.low_income.pov_dir).replace("\\","/"),
        "pov_save_path": os.path.join(WD, paths.low_income.pov_save_path).replace("\\","/"),
        "tract_inc_dir": os.path.join(WD, paths.low_income.tract_inc_dir).replace("\\","/"),
        "tract_inc_save_path": os.path.join(WD, paths.low_income.tract_inc_save_path).replace("\\","/"),
        "st_inc_dir": os.path.join(WD, paths.low_income.st_inc_dir).replace("\\","/"),
        "st_inc_save_path": os.path.join(WD, paths.low_income.st_inc_save_path).replace("\\","/"),
        "st_tract_merged_save_path": os.path.join(WD, paths.low_income.st_tract_merged_save_path).replace("\\","/"),
        "msa_inc_dir": os.path.join(WD, paths.low_income.msa_inc_dir).replace("\\","/"),
        "msa_save_path": os.path.join(WD, paths.low_income.msa_save_path).replace("\\","/"),
        "msa_shape_path": os.path.join(WD, paths.low_income.msa_shape_path).replace("\\","/"),
        "msa_clean_save_path": os.path.join(WD, paths.low_income.msa_clean_save_path).replace("\\","/"),
        "msa_inc_shp_save_path": os.path.join(WD, paths.low_income.msa_inc_shp_save_path).replace("\\","/"),
        "tract_shp_path": os.path.join(WD, paths.low_income.tract_shp_path).replace("\\","/"),
        "low_inc_clean_path": os.path.join(WD, paths.low_income.low_inc_clean_path).replace("\\","/")
    }
    for path in low_income_paths.values():
        os.makedirs(os.path.dirname(path), exist_ok =True)
    poverty_df = clean_pov_data(low_income_paths['pov_dir'], low_income_paths['pov_save_path'])
    tract_inc_df = clean_tract_income_data(low_income_paths['tract_inc_dir'], low_income_paths['tract_inc_save_path'])
    st_inc_df = clean_state_income_data(low_income_paths['st_inc_dir'], low_income_paths['st_inc_save_path'])
    st_tract_merged_df = merge_state_tract_income(tract_inc_df, st_inc_df[['state','st_med_inc']], low_income_paths['st_tract_merged_save_path'])
    msa_inc_df = clean_msa_income_data(low_income_paths['msa_inc_dir'], low_income_paths['msa_save_path'])
    msa_shape_df = clean_msa_shp(low_income_paths['msa_shape_path'], low_income_paths['msa_clean_save_path'])
    msa_inc_shp_df = merge_msa_income_shp(msa_inc_df, msa_shape_df, low_income_paths['msa_inc_shp_save_path'])
    tracts_df = gpd.read_file(low_income_paths['tract_shp_path']).to_crs(epsg=3857)
    merged_df = merge_all_data(poverty_df, st_tract_merged_df, msa_inc_shp_df, tracts_df)
    apply_low_income_conditions(merged_df, low_income_paths['low_inc_clean_path'])

if __name__ == '__main__':
    main()