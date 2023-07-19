#-*- coding: utf-8 -*-
"""
Helper Script for cleanup and preparing all the datasets for the analysis.

This script makes use of the preprocess_helper script and performs data cleaning, preprocessing
and saves the cleaned data as ESRI Shapefiles. 

Requirements:
- pandas
- numpy
- geopandas
- preprocess_helper

Usage:
1. Ensure the necessary dependencies are installed.
2. Configure the YAML file (config.yaml) with appropriate paths and other constants used.
3. Run the script using the following command:
   python preprocess_utilities.py

Author:Sai Krishna
Date: 
"""

## Load Dependencies
import os
import pandas as pd
import numpy as np
import geopandas as gpd
import logging
import scripts.preprocess_helper as helper

## Configure the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

def coops_utils_cleanup(util_shp:gpd.GeoDataFrame, state_csv_df: pd.DataFrame, consts: dict) -> gpd.GeoDataFrame:
    """
    Clean up utility data from the given input shapefile path, based on the provided constants.

    Args:
        util_shp: input shapefile containing utility data.
        state_csv_df: the CSV file containing state data.
        consts (dict): A dictionary containing constants for utility cleanup.

    Returns:
        tuple of gpd.GeoDataFrame: A tuple containing three GeoDataFrames:
            1. util_merged: The cleaned and merged utility data with state data.
            2. rural_coops: Filtered utility data for rural co-ops.
            3. municipal_utils: Filtered utility data for municipal/public utilities.

    Note:
        Make sure the input shapefile and the state CSV file have compatible data columns
        as specified in the constants.
    """
    try:
        coops_utils = util_shp.copy()
        coops_utils = helper.data_preprocess(input_df = util_shp, cols_drop = consts.drop_cols,cols_rename = consts.rename_cols)
        state_df = state_csv_df[consts.state_cols].rename(columns = consts.state_rename_col)

        util_merged = coops_utils.merge(gpd.GeoDataFrame(state_df), how='left', on=consts.st_code)
        util_merged[consts.area] = np.round(util_merged[consts.geo].area, 4)
        util_merged = util_merged[util_merged[consts.filter_col].isin(consts.filters)].to_crs(epsg=3857)
        util_merged[consts.new_col] = util_merged[consts.filter_col].\
            apply(lambda x: consts.filters_new[1] if x== consts.filters[2] else consts.filters_new[0])

        rural_coops = util_merged.query(f'{consts.new_col} == "{consts.filters_new[1]}"').to_crs(epsg=3857)
        municipal_utils = util_merged.query(f'{consts.new_col} == "{consts.filters_new[0]}"').to_crs(epsg=3857)
        
        return util_merged, rural_coops, municipal_utils
    except Exception as e:
        logger.error(f'Error in cleaning up utility data: {e}')
        raise e


def j40_cleanup(j40_shp: gpd.GeoDataFrame, consts: dict) -> gpd.GeoDataFrame:
    """
    Clean up Justice40 data from the given input shapefile path, based on the provided constants.

    Args:
        j40_shp: the input shapefile containing Justice40 data.
        consts (dict): A dictionary containing constants for Justice40 cleanup. 

    Returns:
        gpd.GeoDataFrame: Cleaned Justice40 data as a GeoDataFrame.

    Note:
        Make sure the input shapefile has compatible data columns as specified in the constants.
    """
    try:
        j40 = helper.data_preprocess(input_df = j40_shp, cols_to_keep = consts.cols_to_keep, cols_rename = consts.rename_cols)
        j40 = j40[(j40[consts.filter_cols[0]] == 1) & (j40[consts.filter_cols[1]].is_valid == True)]
        j40.loc[:, consts.new_col] = consts.new_col_val
        j40.loc[:, consts.area] = j40[consts.geo].area
        return j40
    except Exception as e:
        logger.error(f'Error in cleaning up justice40 data: {e}')
        raise e


def energy_cleanup(coal_shp:gpd.GeoDataFrame, ffe_shp:gpd.GeoDataFrame, consts:dict) -> gpd.GeoDataFrame:
    """
    Cleans and processes energy-related data for coal and fuel-fired electric power plants.

    This function takes two GeoDataFrames representing the shapefiles of coal-related and
    fuel-fired electric power plant data, respectively. It then applies data preprocessing
    and cleanup operations to both dataframes as specified by the provided 'consts' dictionary.
    The result is a cleaned GeoDataFrame for each data source.

    Args:
        coal_shp (gpd.GeoDataFrame): GeoDataFrame representing the shapefile of coal-related data.
        ffe_shp (gpd.GeoDataFrame): GeoDataFrame representing the shapefile of fuel-fired electric
            power plant data.
        consts (dict): A dictionary containing constants required for data processing, column names,
            data preprocessing configurations, etc.

    Returns:
        Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]: A tuple containing two GeoDataFrames - the cleaned
        GeoDataFrame for coal-related data (coal_df) and the cleaned GeoDataFrame for fuel-fired
        electric power plant data (ffe_df).
    """
    try:
        coal_df = helper.data_preprocess(input_df = coal_shp, cols_drop = consts.coal_drop_cols, cols_rename = consts.coal_rename_cols)
        ffe_df = helper.data_preprocess(input_df = ffe_shp, cols_drop = consts.ffe_drop_cols, cols_rename = consts.ffe_rename_cols)
        coal_df.loc[:, consts.new_cols[0]] = consts.type_val
        coal_df.loc[:, consts.new_cols[1]] = consts.coal_subtype
        coal_df.loc[:, consts.coal_area] = coal_df[consts.geo].area
        ffe_df.loc[:, consts.new_cols[0]] = consts.type_val
        ffe_df.loc[:, consts.new_cols[1]] = consts.ffe_subtype
        ffe_df.loc[:, consts.ffe_area] = ffe_df[consts.geo].area
        return coal_df, ffe_df
    except Exception as e:
        logger.error(f'Error in cleaning up energy data: {e}')
        raise e

def low_inc_cleanup(pov_csv_path:str, li_tract_csv_path:str, li_st_csv_path:str, li_msa_csv_path:str, tracts_shp_path:str ,msa_shp_path:str, consts:dict) -> gpd.GeoDataFrame:
    """
    Cleans and processes low-income data and performs spatial operations.

    This function takes various input files containing low-income data, cleans and preprocesses them,
    and then performs data merging and spatial join operations. It computes low-income conditions for
    each census tract based on specific criteria, and finally, it returns the resulting GeoDataFrame.

    Args:
        pov_csv_path (str): Path to the poverty data CSV file.
        li_tract_csv_path (str): Path to the tract-level income data CSV file.
        li_st_csv_path (str): Path to the state-level income data CSV file.
        li_msa_csv_path (str): Path to the MSA-level income data CSV file.
        tracts_shp_path (str): Path to the census tracts shapefile.
        msa_shp_path (str): Path to the MSA shapefile.
        consts (dict): A dictionary containing constants required for data processing, column names, etc.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing the cleaned and processed low-income data, including
        spatial information about census tracts and associated low-income conditions.
    """
    try:
        pov_df = helper.load_data(pov_csv_path, type='csv')
        pov_df = pov_df.dropna(axis =1, how ='all')
        pov_df = helper.data_preprocess(input_df = pov_df.copy(), cols_to_keep = consts.pov_cols_to_keep, cols_rename = consts.pov_renamed_cols)
        pov_df[consts.state] = pov_df[consts.state].apply(lambda x: x.upper())
        pov_df[consts.pov_perc] = pov_df[consts.pov_pop]/pov_df[consts.pov_tot_pop]
        
        li_tract_df = helper.load_data(li_tract_csv_path, type='csv')
        li_tract_df = li_tract_df.dropna(axis =1, how ='all')
        li_tract_df = helper.data_preprocess(input_df = li_tract_df.copy(), cols_to_keep = consts.li_tract_csv_cols_to_keep, \
                                                    cols_rename = consts.li_tract_csv_renamed_cols)
        li_tract_df[consts.state] = li_tract_df[consts.state].apply(lambda x: x.upper())
        
        li_st_df = helper.load_data(li_st_csv_path, type='csv')
        li_st_df = li_st_df.dropna(axis =1, how ='all')
        li_st_df = helper.data_preprocess(input_df = li_st_df.copy(), cols_to_keep = consts.st_csv_cols_to_keep, \
                                            cols_rename = consts.st_csv_renamed_cols)
        li_st_df[consts.state] = li_st_df[consts.state].apply(lambda x: x.upper())

        inc_merged_csv = pd.merge(li_tract_df, li_st_df, on = consts['state'], how = 'left')
        
        li_msa_df = helper.load_data(li_msa_csv_path, type='csv')
        li_msa_df = li_msa_df.dropna(axis =1, how ='all')
        li_msa_df = helper.data_preprocess(input_df = li_msa_df.copy(), cols_to_keep = consts.msa_csv_cols_to_keep, \
                                            cols_rename = consts.msa_csv_renamed_cols)
        li_msa_df[consts.state] = li_msa_df[consts.state].apply(lambda x: x.upper())
        
        msa_shp_df = helper.load_data(msa_shp_path, type='shp')
        msa_shp_df = helper.data_preprocess(input_df = msa_shp_df.copy(), cols_to_keep = consts.msa_shp_cols_to_keep, \
                                            cols_rename = consts.msa_shp_renamed_cols)
        msa_shp_df[consts.msa_shp_cbsaId] = msa_shp_df[consts.msa_shp_cbsaId].astype(int)
        
        msa_merge_shp = pd.merge(li_msa_df, msa_shp_df[consts.msa_shp_merge_cols], on = consts.msa_shp_cbsaId, how = 'left')
        msa_merge_shp = gpd.GeoDataFrame(msa_merge_shp, geometry=consts.geo)
        
        all_tracts_shp = helper.load_data(tracts_shp_path, type='shp')
        
        
        inc_merged_shp = pd.merge(inc_merged_csv[consts.merge_all.inc_merged_cols], all_tracts_shp[consts.merge_all.tract_shp_cols],\
                                    left_on = consts.merge_all.leftid, right_on = consts.merge_all.rightid, how = 'left')
        inc_merged_shp.rename(columns = consts.merge_all.inc_merged_cols_renamed, inplace = True)
        
        inc_pov_merged = pd.merge(inc_merged_shp, pov_df[consts.merge_all.pov_cols], on = consts.merge_all.leftid, how = 'left')
        inc_pov_merged.drop(columns = consts.merge_all.pov_drop_cols, inplace = True)
        inc_pov_merged = gpd.GeoDataFrame(inc_pov_merged, geometry=consts.geo)
        
        msa_merge_shp = helper.data_preprocess(input_df = msa_merge_shp.copy(), cols_to_keep =consts.merge_all.msa_inc_shp_cols_to_keep, \
                                                cols_rename = consts.merge_all.msa_inc_shp_renamed_cols)
        msa_merge_shp = gpd.GeoDataFrame(msa_merge_shp, geometry=consts.geo)
        
        final_lic_shp = gpd.sjoin(inc_pov_merged, msa_merge_shp, how = 'left', predicate = 'intersects').drop(columns = ['index_right'])

        final_lic_shp = final_lic_shp[consts.merge_all.final_merged_col_order]
        final_lic_shp = final_lic_shp.dissolve(by = consts.merge_all.leftid) 
        final_lic_shp[consts.merge_all.area] = final_lic_shp[consts.geo].area

        final_lic_shp[consts.li_conds.li_col] = ""
        final_lic_shp.loc[final_lic_shp[consts.li_conds.pov_perc] > 20, consts.li_conds.li_col] = "Low Income"
        final_lic_shp.loc[final_lic_shp[consts.li_conds.med_inc] < final_lic_shp[consts.li_conds.st_med_inc]*0.8, consts.li_conds.li_col] = "Low Income"
        final_lic_shp.loc[(final_lic_shp[consts.li_conds.lsad] == 'M1') & \
            (final_lic_shp[consts.li_conds.med_inc] < final_lic_shp[consts.li_conds.msa_medInc]*0.8), consts.li_conds.li_col] = "Low Income"
        final_lic_shp.loc[final_lic_shp[consts.li_conds.li_col] == "", consts.li_conds.li_col] = "Not Low Income"

        return final_lic_shp
    except Exception as e:
        logger.error(e)
        return None

def cty_st_borders_cleanup(county_df: gpd.GeoDataFrame, st_fips_csv:pd.DataFrame, st_df:gpd.GeoDataFrame, consts: dict) -> gpd.GeoDataFrame:
    """
    Clean up county and state borders datasets.

    This function takes a county GeoDataFrame, a path to the state FIPS file, and a state GeoDataFrame as input.
    It performs data preprocessing to clean and merge the county and state datasets based on specific columns.
    The cleaned GeoDataFrames are returned after the process.

    Args:
        county_df (gpd.GeoDataFrame): The GeoDataFrame containing county borders data.
        st_fips_path (str): The file path to the state FIPS dataset.
        st_df (gpd.GeoDataFrame): The GeoDataFrame containing state borders data.

    Returns:
        tuple: A tuple containing two GeoDataFrames (county_df, st_df) after cleaning and merging.
               If an error occurs during processing, (None, None) is returned.
    """
    try:
        states_fips = helper.data_preprocess(input_df = st_fips_csv.copy(), cols_to_keep = consts.cols_read_csv, \
                                            cols_rename = consts.cols_rename_csv)
        
        county_df[consts.statefp] = county_df[consts.statefp].astype(int)
        county_df = county_df.merge(states_fips, on = consts.statefp, how = 'left')
        county_df = county_df.drop(columns = consts.cols_drop_cty)
        county_df.rename(columns = consts.ct_rename_cols, inplace = True)

        st_df = helper.data_preprocess(input_df = st_df, cols_to_keep = consts.st_drop_cols, \
                                            cols_rename = consts.st_rename_cols)
        
        return county_df, st_df
    except Exception as e:
        logger.error(e)
        return None, None