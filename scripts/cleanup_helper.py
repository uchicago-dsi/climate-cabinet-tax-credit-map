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
Date: 07/25/2023
"""

## Load Dependencies
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
    coops_utils = util_shp.copy()
    assert len(coops_utils) > 0, 'No data found in the input shapefile.'
    try:
        coops_utils = helper.data_preprocess(input_df = coops_utils, cols_drop = consts.drop_cols,\
                                             cols_rename = consts.rename_cols)
    except:
        logger.error('Error in cleaning up utility data: Invalid column names.')
        raise ValueError('Invalid column names in the input shapefile.')
    
    state_df = state_csv_df[consts.state_cols].rename(columns = consts.state_rename_col)
    util_merged = coops_utils.merge(gpd.GeoDataFrame(state_df), how='left', on=consts.st_code)
    util_merged[consts.area] = np.round(util_merged[consts.geo].area, 4)
    util_merged = util_merged[util_merged[consts.filter_col].isin(consts.filters)].to_crs(epsg=3857)
    util_merged[consts.new_col] = util_merged[consts.filter_col].\
        apply(lambda x: consts.filters_new[1] if x== consts.filters[2] else consts.filters_new[0])

    rural_coops = util_merged.query(f'{consts.new_col} == "{consts.filters_new[1]}"').to_crs(epsg=3857)
    municipal_utils = util_merged.query(f'{consts.new_col} == "{consts.filters_new[0]}"').to_crs(epsg=3857)
    
    return util_merged, rural_coops, municipal_utils


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
        j40 = helper.data_preprocess(input_df = j40_shp, cols_to_keep = consts.cols_to_keep, \
                                     cols_rename = consts.rename_cols)
    except:
        logger.error('Error in cleaning up justice40 data: Invalid column names.')
        raise ValueError('Invalid column names in the input shapefile.')
    j40 = j40[(j40[consts.filter_cols[0]] == 1) & (j40[consts.filter_cols[1]].is_valid == True)]
    j40.loc[:, consts.new_col] = consts.new_col_val
    j40.loc[:, consts.area] = j40[consts.geo].area
    return j40


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
        coal_df = helper.data_preprocess(input_df = coal_shp, cols_drop = consts.coal_drop_cols,\
                                          cols_rename = consts.coal_rename_cols)
    except:
        logger.error('Error in cleaning up coal data: Invalid column names.')
        raise ValueError('Invalid column names in the input shapefile.')
    try:
        ffe_df = helper.data_preprocess(input_df = ffe_shp, cols_drop = consts.ffe_drop_cols, \
                                        cols_rename = consts.ffe_rename_cols)
    except:
        logger.error('Error in cleaning up FFE data: Invalid column names.')
        raise ValueError('Invalid column names in the input shapefile.')
    coal_df.loc[:, consts.new_cols[0]] = consts.type_val
    coal_df.loc[:, consts.new_cols[1]] = consts.coal_subtype
    coal_df.loc[:, consts.coal_area] = coal_df[consts.geo].area
    ffe_df.loc[:, consts.new_cols[0]] = consts.type_val
    ffe_df.loc[:, consts.new_cols[1]] = consts.ffe_subtype
    ffe_df.loc[:, consts.ffe_area] = ffe_df[consts.geo].area
    return coal_df, ffe_df

def cty_st_borders_cleanup(county_df: gpd.GeoDataFrame, st_fips_csv:pd.DataFrame, st_df:gpd.GeoDataFrame,\
                            consts: dict) -> gpd.GeoDataFrame:
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
    except:
        logger.error('Error in cleaning up state FIPS data: Invalid column names.')
        raise ValueError('Invalid column names in the input CSV file.')
    county_df[consts.statefp] = county_df[consts.statefp].astype(int)
    county_df = county_df.merge(states_fips, on = consts.statefp, how = 'left')
    county_df = county_df.drop(columns = consts.cols_drop_cty)
    county_df.rename(columns = consts.ct_rename_cols, inplace = True)
    try:
        st_df = helper.data_preprocess(input_df = st_df, cols_drop = consts.st_drop_cols, \
                                            cols_rename = consts.st_rename_cols)
    except:
        logger.error('Error in cleaning up state borders data: Invalid column names.')
        raise ValueError('Invalid column names in the input shapefile.')
    return county_df, st_df
    
def dci_cleanup(dci_csv_df: pd.DataFrame, zip_shp: gpd.GeoDataFrame, consts: dict) ->gpd.GeoDataFrame:
    """
    Clean up DCI dataset. This function takes a DCI DataFrame and a zip code GeoDataFrame as input.
    It performs data preprocessing to clean and merge the DCI and zip code datasets based on specific columns.
    The cleaned GeoDataFrame is returned after the process.

    Args:
        dci_csv_df (pd.DataFrame): The DataFrame containing DCI data.
        zip_shp (gpd.GeoDataFrame): The GeoDataFrame containing zip code data.
        consts (dict): The dictionary containing constants.
    
    Returns:
        gpd.GeoDataFrame: The GeoDataFrame containing DCI data after cleaning and merging.
                            If an error occurs during processing, None is returned.
    """
    zip_shp[consts.geoid] = zip_shp[consts.geoid].astype('int64')
    dci_shp = dci_csv_df.merge(zip_shp, left_on = consts.zip, right_on = consts.geoid, how = 'left')
    try:
        dci_shp = helper.data_preprocess(input_df = dci_shp.copy(), cols_to_keep = consts.cols_to_keep, \
                                            cols_rename = consts.cols_rename)
    except:
        logger.error('Error in cleaning up DCI data: Invalid column names.')
        raise ValueError('Invalid column names in the input shapefile.')
    dci_shp = dci_shp[~dci_shp[consts.geo].isnull()] #all the 4 null zips have quintile scores not equal to 5
    dci_shp = dci_shp[dci_shp[consts.quintile] == 5]
    dci_shp[consts.new_col.name] = consts.new_col.val
    dci_shp = gpd.GeoDataFrame(dci_shp, geometry=consts.geo).to_crs(epsg = consts.crs)
    return dci_shp

class LowIncomeCleanup:
    """
    A class to clean and process low-income data and perform spatial operations.

    Attributes:
        consts (dict): A dictionary containing constants required for data processing, column names, etc.
    """
    def __init__(self, consts):
        self.consts = consts

    def _load_preprocess_data(self, path, cols_to_keep, cols_rename, data_type='csv'):
        """
        Load data from a CSV/shp file, preprocess it, and convert the 'State' column to uppercase.

        Args:
            path (str): Path to the CSV/shp file.
            data_type (str, optional): Type of data to load ('csv' or 'shp'). Default is 'csv'.

        Returns:
            pd.DataFrame or gpd.GeoDataFrame: The loaded and preprocessed DataFrame or GeoDataFrame.
        """
        data = helper.load_data(path, type=data_type).dropna(axis=1, how='all')
        data = helper.data_preprocess(input_df=data.copy(), cols_to_keep= cols_to_keep, cols_rename=cols_rename)
        if data_type == 'csv':
            data[self.consts.state] = data[self.consts.state].str.upper()
        return data

    def _merge_dataframes(self, df1, df2, on=None):
        """
        Merge two DataFrames based on the 'State' column.

        Args:
            df1 (pd.DataFrame): The first DataFrame to merge.
            df2 (pd.DataFrame): The second DataFrame to merge.

        Returns:
            pd.DataFrame: The merged DataFrame.
        """
        return pd.merge(df1, df2, on= on, how='left')

    def _merge_geodataframes(self, gdf1, gdf2, on=None, left_on=None, right_on=None):
        """
        Merge two GeoDataFrames based on the 'CBSAId' column.

        Args:
            gdf1 (gpd.GeoDataFrame): The first GeoDataFrame to merge.
            gdf2 (gpd.GeoDataFrame): The second GeoDataFrame to merge.

        Returns:
            gpd.GeoDataFrame: The merged GeoDataFrame.
        """
        if on is not None:
            return gpd.GeoDataFrame(pd.merge(gdf1, gdf2, on=on, how='left'), geometry=self.consts.geo)
        elif left_on is not None and right_on is not None:
            return gpd.GeoDataFrame(pd.merge(gdf1, gdf2, left_on=left_on, right_on=right_on, how='left'),\
                                     geometry=self.consts.geo)
        else:
            raise ValueError('Invalid merge parameters.')

    def _spatial_join(self, gdf1, gdf2, predicate='intersects'):
        """
        Perform a spatial join between two GeoDataFrames.

        Args:
            gdf1 (gpd.GeoDataFrame): The first GeoDataFrame to join.
            gdf2 (gpd.GeoDataFrame): The second GeoDataFrame to join.
            predicate (str, optional): The spatial predicate to use for the join. Default is 'intersects'.

        Returns:
            gpd.GeoDataFrame: The spatially joined GeoDataFrame.
        """
        return gpd.sjoin(gdf1, gdf2, how='left', predicate=predicate).drop(columns=['index_right'])

    def _apply_low_income_conditions(self, gdf):
        """
        Apply low-income conditions to the GeoDataFrame.

        Args:
            gdf (gpd.GeoDataFrame): The GeoDataFrame containing low-income data.

        Returns:
            gpd.GeoDataFrame: The GeoDataFrame with low-income conditions applied.
        """
        gdf[self.consts.li_conds.li_col] = ""
        gdf.loc[gdf[self.consts.li_conds.pov_perc] > 20, self.consts.li_conds.li_col] = "Low Income"
        gdf.loc[gdf[self.consts.li_conds.med_inc] < gdf[self.consts.li_conds.st_med_inc] * 0.8, self.consts.li_conds.li_col] = "Low Income"
        gdf.loc[(gdf[self.consts.li_conds.lsad] == 'M1') & (gdf[self.consts.li_conds.med_inc] < gdf[self.consts.li_conds.msa_medInc] * 0.8), self.consts.li_conds.li_col] = "Low Income"
        gdf.loc[gdf[self.consts.li_conds.li_col] == "", self.consts.li_conds.li_col] = "Not Low Income"
        return gdf[gdf[self.consts.li_conds.li_col] == "Low Income"].reset_index()

    def clean_data(self, pov_csv_path, li_tract_csv_path, li_st_csv_path, li_msa_csv_path, \
                   tracts_shp_path, msa_shp_path):
        """
        Clean and process low-income data and perform spatial operations.

        Args:
            pov_csv_path (str): Path to the poverty data CSV file.
            li_tract_csv_path (str): Path to the tract-level income data CSV file.
            li_st_csv_path (str): Path to the state-level income data CSV file.
            li_msa_csv_path (str): Path to the MSA-level income data CSV file.
            tracts_shp_path (str): Path to the census tracts shapefile.
            msa_shp_path (str): Path to the MSA shapefile.

        Returns:
            gpd.GeoDataFrame: A GeoDataFrame containing the cleaned and processed low-income data,
            including spatial information about census tracts and associated low-income conditions.
        """
        #Load the data
        pov_df = self._load_preprocess_data(pov_csv_path, cols_to_keep=self.consts.pov_cols_to_keep, \
                                            cols_rename=self.consts.pov_renamed_cols)
        li_tract_df = self._load_preprocess_data(li_tract_csv_path, cols_to_keep=self.consts.li_tract_csv_cols_to_keep,\
                                                  cols_rename=self.consts.li_tract_csv_renamed_cols)
        li_st_df = self._load_preprocess_data(li_st_csv_path, cols_to_keep=self.consts.st_csv_cols_to_keep, \
                                              cols_rename=self.consts.st_csv_renamed_cols)
        li_msa_df = self._load_preprocess_data(li_msa_csv_path, cols_to_keep=self.consts.msa_csv_cols_to_keep, \
                                               cols_rename=self.consts.msa_csv_renamed_cols)
        msa_shp_df = self._load_preprocess_data(msa_shp_path, cols_to_keep=self.consts.msa_shp_cols_to_keep, \
                                                cols_rename= self.consts.msa_shp_renamed_cols,\
                                                data_type='shp')
        all_tracts_shp = helper.load_data(tracts_shp_path, type='shp') #Load the census tracts shapefile

        pov_df[self.consts.pov_perc] = pov_df[self.consts.pov_pop]/pov_df[self.consts.pov_tot_pop]
        msa_shp_df[self.consts.msa_shp_cbsaId] = msa_shp_df[self.consts.msa_shp_cbsaId].astype(int)
        #Merge the datasets together
        inc_merged_csv = self._merge_dataframes(li_tract_df, li_st_df, on = self.consts.state) #Tract + State income data
        msa_merge_shp = self._merge_geodataframes(li_msa_df, msa_shp_df[self.consts.msa_shp_merge_cols], \
                                                  on = self.consts.msa_shp_cbsaId) #MSA + MSA shapefile

        inc_merged_shp = self._merge_geodataframes(inc_merged_csv[self.consts.merge_all.inc_merged_cols], \
                                                   all_tracts_shp[self.consts.merge_all.tract_shp_cols],\
                                                   left_on = self.consts.merge_all.leftid, \
                                                    right_on = self.consts.merge_all.rightid) #Inc Tract + Tract shapefile
        inc_merged_shp.rename(columns=self.consts.merge_all.inc_merged_cols_renamed, inplace=True)

        inc_pov_merged = self._merge_dataframes(inc_merged_shp, pov_df[self.consts.merge_all.pov_cols], \
                                                on = self.consts.merge_all.leftid) #Inc Tract+Tract shapefile+Poverty data
        inc_pov_merged.drop(columns=self.consts.merge_all.pov_drop_cols, inplace=True)
        
        msa_merge_shp = helper.data_preprocess(input_df = msa_merge_shp.copy(), \
                                               cols_to_keep =self.consts.merge_all.msa_inc_shp_cols_to_keep, \
                                                cols_rename = self.consts.merge_all.msa_inc_shp_renamed_cols) 
        msa_merge_shp = gpd.GeoDataFrame(msa_merge_shp, geometry=self.consts.geo)
        #Perform spatial operations
        final_lic_shp = self._spatial_join(inc_pov_merged, msa_merge_shp)
        final_lic_shp = final_lic_shp.dissolve(by = self.consts.merge_all.leftid)
        final_lic_shp[self.consts.merge_all.area] = final_lic_shp[self.consts.geo].area
        #Apply low-income conditions
        final_lic_shp = self._apply_low_income_conditions(final_lic_shp)

        return final_lic_shp
    
#Cleanup class for the population datasets
class PopulationCleanup:
    def __init__(self, consts):
        self.consts = consts

    def _clean_csv_data(self, raw_df, merge_key):
        cols_to_drop = self.consts[merge_key].cols_to_drop
        clean_df = raw_df.dropna(axis=1, how='all')
        clean_df = clean_df.drop(columns=cols_to_drop)
        cols_renamed = self.consts[merge_key].cols_renamed
        clean_df.rename(columns=cols_renamed, inplace=True)
        clean_df['state'] = clean_df['state'].str.upper()
        return clean_df

    def _merge_with_shapefile(self, clean_df, shp_df, merge_key):
        merge_config = self.consts.merge[merge_key]
        merged_df = pd.merge(clean_df, shp_df[merge_config.shp_cols], \
                             left_on=merge_config.leftid, \
                             right_on=merge_config.rightid, how='left')
        merged_df = gpd.GeoDataFrame(merged_df, geometry=self.consts.geo).to_crs(epsg=self.consts.crs)
        return merged_df

    def _convert_to_int(self, df, column):
        try:
            df[column] = df[column].astype(int)
        except ValueError:
            pass

    def merge_data_with_shapefile(self, clean_df, shp_df, merge_key):
        if merge_key in ['county', 'msa']:
            self._convert_to_int(clean_df, self.consts.merge[merge_key].leftid)
            self._convert_to_int(shp_df, self.consts.merge[merge_key].rightid)

        merged_df = self._merge_with_shapefile(clean_df, shp_df, merge_key)
        return merged_df