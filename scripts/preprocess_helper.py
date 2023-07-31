#-*- coding: utf-8 -*-
"""
Data Preprocessing Helper Functions

This script contains helper functions to preprocess data, including loading and saving data in CSV or shapefile format,
and performing common data cleaning tasks such as dropping columns, keeping columns, and renaming columns.

Dependencies:
- pandas
- geopandas

Usage:

Author: Sai Krishna
Date: 07/17/2023
"""

## Load Dependencies
import pandas as pd
import geopandas as gpd
import logging

## Configure the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

def load_data(input_path: str, type:str) -> pd.DataFrame or gpd.GeoDataFrame:
    """
    Load the data and return it if it is a CSV or a shapefile.

    Args:
        input_path (str): Path to the data file.
        type (str): Type of the data file.
    
    Returns:
        pd.DataFrame or gpd.GeoDataFrame: Data as a DataFrame or GeoDataFrame or None if an error occurs.
    """
    try:
        if type == 'csv':
            data = pd.read_csv(input_path)
        elif type == 'shp':
            data = gpd.read_file(input_path).to_crs(epsg=3857)
        else:
            logger.error(f'Invalid file type: {type}')
            return None
        return data
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.error(f'Error loading data: {e}')
        return None

def save_data(cleaned_data: pd.DataFrame or gpd.GeoDataFrame, output_path: str, type:str) -> None:
    """
    Save the cleaned data as a CSV or ESRI Shapefile.

    Args:
        cleaned_data (pd.DataFrame or gpd.GeoDataFrame): Cleaned data as a DataFrame or GeoDataFrame.
        output_path (str): Path to save the cleaned data.
        type (str): Type of the data file.
    
    Returns:
        None
    """
    try:
        if type == 'csv':
            cleaned_data.to_csv(output_path, index = False)
        elif type == 'shp':
            cleaned_data.to_file(output_path, driver='ESRI Shapefile')
        else:
            logger.error(f'Invalid file type: {type}')
    except (FileNotFoundError, IOError, PermissionError) as e:
        logger.error(f'Error saving data: {e}')

def data_preprocess(input_df:pd.DataFrame or gpd.GeoDataFrame, cols_drop:list or None = None, cols_to_keep:list or None = None, cols_rename:dict or None = None) -> pd.DataFrame or gpd.GeoDataFrame:
    """
    Preprocesses the dataset by dropping columns, keeping columns, and renaming columns.

    Args:
        input_df (pd.DataFrame or gpd.GeoDataFrame): Data as a DataFrame or GeoDataFrame.
        cols_drop (list or None): List of columns to drop.
        cols_to_keep (list or None): List of columns to keep.
        cols_rename (dict or None): Dictionary of columns to rename.
    
    Returns:
        pd.DataFrame or gpd.GeoDataFrame: Cleaned data as a DataFrame or GeoDataFrame or None if an error occurs.
    """
    try:
        if cols_drop:
            input_df.drop(cols_drop, axis = 1, inplace = True)
    except:
        logger.error(f'Error dropping columns: {cols_drop}')
        return None
    try:
        if cols_to_keep:
            input_df = input_df[cols_to_keep]
    except:
        logger.error(f'Error selecting columns: {cols_to_keep}')
        return None
    try:
        if cols_rename:
            input_df.rename(columns = cols_rename, inplace = True)
    except:
        logger.error(f'Error renaming columns: {cols_rename}')
        return None
    return input_df