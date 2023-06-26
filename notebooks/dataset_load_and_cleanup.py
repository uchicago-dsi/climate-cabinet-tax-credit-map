#-*- coding: utf-8 -*-
## Load Dependencies
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import folium
import shapely
import os
pd.set_option('display.max_columns', None)

##Set Working Directory
wd = '../data/'

##Load the Utility Datasets (Rural CoOps and Municipal Utilities) and clean them
utility_territories = gpd.read_file(wd + 'utility shape file/Electric_Retail_Service_Territories.shp').to_crs(epsg=3857)
util_cols_to_remove = ['OBJECTID','SOURCE','SOURCEDATE','VAL_METHOD','VAL_DATE']
utility_territories.drop(util_cols_to_remove, axis = 1, inplace = True)
utility_territories.rename(columns = {'STATE':'ST_Code'}, inplace = True)
###Load an external dataset with the state names and abbreviations
states = pd.read_csv(wd+'states.csv')
states = states[['Abbreviation','State']].rename(columns = {'Abbreviation':'ST_Code'})
util_merged = utility_territories.merge(gpd.GeoDataFrame(states), how='left', left_on='ST_Code', right_on='ST_Code')
if not os.path.exists(wd + 'util_clean'):
    os.mkdir(wd + 'util_clean')
util_clean_path = wd+'util_clean/util_clean.shp'
util_merged.to_file(util_clean_path, driver='ESRI Shapefile')
###Separate the utilities into rural cooperatives and municipal utilities
rural_coops = util_merged.query('(TYPE == "COOPERATIVE")').to_crs(epsg=3857)
rural_coops['Type'] = 'Rural Co-Op'
rural_coops['area'] = rural_coops['geometry'].area  
if not os.path.exists(wd + 'rural_coops'):
    os.mkdir(wd + 'rural_coops')
rural_coops_path = wd+'rural_coops/rural_coops.shp'
rural_coops.to_file(rural_coops_path, driver='ESRI Shapefile')

municipal_utils = util_merged.query('(TYPE == "MUNICIPAL") | (TYPE == "POLITICAL SUBDIVISION")').to_crs(epsg=3857)
municipal_utils['Type'] = 'Municipal/Public Utility'
municipal_utils['area'] = municipal_utils['geometry'].area
if not os.path.exists(wd + 'municipal_utils'):
    os.mkdir(wd + 'municipal_utils')
municipal_utils_path = wd+'municipal_utils/municipal_utils.shp'
municipal_utils.to_file(municipal_utils_path, driver='ESRI Shapefile')

##Load Justice40 Data and clean it
justice40 = gpd.read_file(wd +'justice40 shapefile/usa/usa.shp')
cols_to_keep = ['GEOID10','SF', 'CF','TPF','UF_PFS','SN_C','SN_T','HRS_ET','LHE','FPL200S','UI_EXP','THRHLD','geometry']
justice40 = justice40[cols_to_keep]
justice40.columns = ['GeoID','State','County','Tot_Pop','Unemp_Per','Disadv?','Disad_Tri?','Underinves','Low_HS_Edu','Low_Income','UI_EXP','THRHLD','geometry']
justice_final = justice40[(justice40['Disadv?'] == 1) & (justice40['geometry'].is_valid == True)]
justice_final.rename(columns = {'GeoID':'TractID'}, inplace = True)
justice_final['Type'] = 'Justice40'
if not os.path.exists(wd + 'justice40_final'):
    os.mkdir(wd + 'justice40_final')
justice_final_path = wd+'justice40_final/justice40_final.shp'
justice_final = justice_final.to_crs(epsg=3857)
justice_final.to_file(justice_final_path, driver='ESRI Shapefile')

##Load the energy communities datasets and clean it
##Coal Closure dataset
coal_shp_path = wd + 'ira_data_coalclosure_energycomm_20231\IRA_Coal_Closure_Energy_Comm_SHP\Coal_Closure_Energy_Communities_shp\Coal_Closure_Energy_Communities.shp'
coal_df = gpd.read_file(coal_shp_path, driver = 'ESRI Shapefile').to_crs(epsg=3857)
drop_cols_coal = ['objectid', 'affgeoid_t', 'fipstate_2', 'fipcounty_', 'geoid_coun','fiptract_2','censustrac','date_last_','dataset_ve']
coal_df.drop(columns=drop_cols_coal, inplace=True)
coal_df.rename(columns={'geoid_trac':'TractID', 'state_name':'State','county_nam':'County','mine_closu':'mine_clos',
                          'generator_':'gen_clos','adjacent_t':'adj_clos'}, inplace=True)
coal_df['Type'] = 'Energy-Coal'
if not os.path.exists(wd + 'energy_coal'):
    os.mkdir(wd + 'energy_coal')
coal_path = wd + 'energy_coal/coal_df.shp'
coal_df.to_file(coal_path, driver='ESRI Shapefile')
##Fossil Fuel Employment dataset
ffe_path = wd + '/ira_data_msanmsa_ffe_20231/MSA_NMSA_FFE_SHP/MSA_NMSA_FFE_SHP.shp'
ffe_df = gpd.read_file(ffe_path, driver = 'ESRI Shapefile').to_crs(epsg=3857)
drop_cols_ffe = ['ObjectID','fipstate_2','fipscty_20','geoid_cty_','MSA_area_I','Date_Last_','Dataset_ve']
ffe_df.drop(columns=drop_cols_ffe, inplace=True)
ffe_df.rename(columns = {'AFFGEOID_C':'TractIDcty','state_name':'State','county_nam':'County','FFE_qual_s':'is_FFE','MSA_NMSA_L':'M_NMSA_loc',
                          'Shape_Leng':'Leng_Cty','Shape_Area':'Area_Cty'}, inplace=True)
ffe_df['Type'] = 'Energy-FFE'
if not os.path.exists(wd + 'energy_ffe'):
    os.mkdir(wd + 'energy_ffe')
ffe_df_path = wd + 'energy_ffe/ffe_df.shp'
ffe_df.to_file(ffe_df_path, driver='ESRI Shapefile')