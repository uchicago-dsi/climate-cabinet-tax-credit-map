#-*- coding: utf-8 -*-
## Load Dependencies
import pandas as pd
import geopandas as gpd
import os
import numpy as np

##Set working directory and file save paths
WD = os.path.join(os.getcwd(), 'data')
LIC_PATH = os.path.join(WD, 'Low Income Communities')
FINAL_SHP_PATH = os.path.join(WD, "communities","low_income")
#Poverty
POV_DIR = os.path.join(LIC_PATH, "poverty","R13409161_SL140.csv")
POV_SAVE_PATH = os.path.join(LIC_PATH, "poverty","poverty_clean.csv")
#Income Tract Level csv
TRACT_INC_DIR = os.path.join(LIC_PATH, "income","R13409069_SL140.csv")
TRACT_INC_SAVE_PATH = os.path.join(LIC_PATH, "income","income_clean.csv")
#Income State Level csv
ST_INC_DIR = os.path.join(LIC_PATH, "income","R13411548_SL040.csv")
ST_INC_SAVE_PATH = os.path.join(LIC_PATH, "income","income_state_clean.csv")
#Income State and Tract Merged 
ST_TRACT_MERGED_SAVE_PATH = os.path.join(LIC_PATH, "income","income_tract_st_merged.csv")
#Income MSA Level csv
MSA_INC_DIR = os.path.join(LIC_PATH, "income","R13411591_SL320.csv")
MSA_SAVE_PATH = os.path.join(LIC_PATH, "income","income_msa_clean.csv")
#MSA Shapefile
MSA_SHP_DIR = os.path.join(LIC_PATH, "income","2021_msa_shp", "tl_2021_us_cbsa.shp")
MSA_CLEAN_SHP_DIR = os.path.join(LIC_PATH, "income","msa_clean_shp")
if not os.path.exists(MSA_CLEAN_SHP_DIR):
    os.makedirs(MSA_CLEAN_SHP_DIR)
MSA_CLEAN_SAVE_PATH = os.path.join(LIC_PATH, "income","msa_clean_shp", "msa_clean.shp")
#MSA Income Merged
MSA_INC_SHP_DIR = os.path.join(LIC_PATH, "income","msa_income_shp")
if not os.path.exists(MSA_INC_SHP_DIR):
    os.makedirs(MSA_INC_SHP_DIR)
MSA_INC_SHP_SAVE_PATH = os.path.join(LIC_PATH, "income","msa_income_shp", "msa_income_shp.shp")
#Census Tract Shapefile
# TRACT_SHP_DIR = os.path.join(LIC_PATH, "merged_tracts","merged_tracts.shp") #For 2021 Census Tracts
TRACT_SHP_DIR = os.path.join(LIC_PATH, "merged_tracts_2020","merged_tracts_2020.shp") #For 2020 Census Tracts
#Final Merged Low Income Shapefile
if not os.path.exists(FINAL_SHP_PATH):
    os.makedirs(FINAL_SHP_PATH)
FINAL_SHP_SAVE_PATH = os.path.join(FINAL_SHP_PATH, "low_income_tracts.shp")


##Define a function to clean and save the poverty data
def clean_pov_data():
    poverty_df = pd.read_csv(POV_DIR)
    #Remove the columns with all null values
    poverty_df = poverty_df.dropna(axis=1, how='all')
    #Removing other columns as needed as per the data dictionary
    cols_to_keep = ['Geo_STUSAB','Geo_GEOID','Geo_QName','Geo_FIPS','Geo_AREALAND','Geo_AREAWATR','ACS20_5yr_B17020001','ACS20_5yr_B17020002',]
    poverty_df = poverty_df[cols_to_keep]
    poverty_df.columns = ['state','geo_id','tract_name','tractId','area_land','area_water','total_pop','pov_pop']
    poverty_df['state'] = poverty_df['state'].apply(lambda x: x.upper())
    poverty_df['pov_perc'] = (poverty_df['pov_pop']/poverty_df['total_pop'])*100
    # poverty_df = poverty_df[poverty_df['poverty_percent'] >= 20]
    poverty_df.to_csv(POV_SAVE_PATH, index=False)
    return poverty_df

##Define a function to clean and save the tract level income data
def clean_tract_income_data():
    li_df = pd.read_csv(TRACT_INC_DIR)
    #Remove the columns with all null values
    li_df = li_df.dropna(axis=1, how='all')
    #Removing other columns as needed as per the data dictionary
    li_cols_to_keep = ['Geo_STUSAB','Geo_GEOID','Geo_QName', 'Geo_FIPS', 'Geo_AREALAND', 'Geo_AREAWATR','ACS20_5yr_B19113001']
    li_df = li_df[li_cols_to_keep]
    li_df.columns = ['state','geoId','tractName','tractId','area_land','area_water','med_inc']
    li_df['state'] = li_df['state'].apply(lambda x: x.upper())
    li_df.to_csv(TRACT_INC_SAVE_PATH, index=False)
    return li_df

##Define a function to clean and save the state level income data
def clean_state_income_data():
    income_state_df = pd.read_csv(ST_INC_DIR)
    #Remove the columns with all null values
    income_state_df = income_state_df.dropna(axis=1, how='all')
    #Removing other columns as needed as per the data dictionary
    cols_to_keep_stw = ['Geo_STUSAB','Geo_GEOID','Geo_QName','Geo_AREALAND', 'Geo_AREAWATR','ACS20_5yr_B19113001']
    income_state_df = income_state_df[cols_to_keep_stw]
    income_state_df.columns = ['state','geoId','st_name','area_land','area_water','st_med_inc']
    income_state_df['state'] = income_state_df['state'].apply(lambda x: x.upper())
    income_state_df.to_csv(ST_INC_SAVE_PATH, index=False)
    return income_state_df

##Define a function to merge the state and tract level income data
def merge_state_tract_income():
    income_merged = pd.merge(clean_tract_income_data(), clean_state_income_data()[['state','st_med_inc']], on=['state'], how='left')
    income_merged.to_csv(ST_TRACT_MERGED_SAVE_PATH, index=False)  
    return income_merged

##Define a function to clean and save the MSA level income data
def clean_msa_income_data():
    income_msa_df = pd.read_csv(MSA_INC_DIR)
    #Remove the columns with all null values
    income_msa_df = income_msa_df.dropna(axis=1, how='all')
    #Removing other columns as needed as per the data dictionary
    msa_cols_to_keep = ['Geo_STUSAB','Geo_CBSA','Geo_GEOID','Geo_QName','Geo_FIPS','Geo_AREALAND',  'Geo_AREAWATR','ACS20_5yr_B19113001']
    income_msa_df = income_msa_df[msa_cols_to_keep]
    income_msa_df.columns = ['state','cbsaId','geoId','msaName', 'msaTractId','area_land','area_water','msa_medInc']
    income_msa_df['state'] = income_msa_df['state'].apply(lambda x: x.upper())
    income_msa_df.to_csv(MSA_SAVE_PATH, index=False)
    return income_msa_df

##Define a function to clean and save the MSA shapefile
def clean_msa_shp():
    msa_shp_df = gpd.read_file(MSA_SHP_DIR).to_crs(epsg=3857)
    # assert sum(msa_shp_df['CBSAFP']== msa_shp_df['GEOID']) == len(msa_shp_df)
    msa_shp_df = msa_shp_df[['GEOID','NAMELSAD','LSAD','ALAND','AWATER','INTPTLAT','INTPTLON','geometry']]
    msa_shp_df.columns = ['cbsaId','msaName','lsad','area_land','area_water','lat','lon','geometry']
    msa_shp_df['cbsaId'] = msa_shp_df['cbsaId'].astype(int)
    msa_shp_df.to_file(MSA_CLEAN_SAVE_PATH)
    return msa_shp_df

##Define a function to merge the MSA shapefile and MSA level income data
def merge_msa_income_shp():
    msa_income_shp = pd.merge(clean_msa_income_data(), clean_msa_shp()[['cbsaId','lsad','lat','lon','geometry']], on=['cbsaId'], how='left')
    msa_income_shp = gpd.GeoDataFrame(msa_income_shp, geometry='geometry')
    msa_income_shp.to_file(MSA_INC_SHP_SAVE_PATH)
    return msa_income_shp

##Define a function to merge all the datasets together
def merge_all_data():
    #Read all the datasets
    poverty_df = clean_pov_data()
    income_merged = merge_state_tract_income()
    msa_income_shp = merge_msa_income_shp()
    merged_tracts = gpd.read_file(TRACT_SHP_DIR).to_crs(epsg=3857)
    #Merging the income_merged dataframe with the tracts shapefile
    income_shp_merged = pd.merge(income_merged[['state','geoId','tractName','tractId','med_inc','st_med_inc']], 
                             merged_tracts[['stateFP','tract_id','tract_name','area_land','area_water','lat','lon','geometry']], 
                             left_on=['tractId'], right_on =['tract_id'], how='left')
    inc_pov_merged = pd.merge(income_shp_merged, poverty_df[['tractId','total_pop','pov_pop','pov_perc']], on = ['tractId'], how='left')
    # Cleaning up the apprearance of the dataframe
    inc_pov_merged.drop(columns=['tract_id', 'tract_name'], inplace=True)
    #reordering how the columns appear
    inc_pov_merged = inc_pov_merged[['stateFP','state','geoId','tractId','tractName','med_inc','st_med_inc','total_pop','pov_pop',\
                                    'pov_perc','area_land','area_water','lat','lon','geometry']]
    #Convert the dataframe to a geodataframe before making spatial join
    inc_pov_merged = gpd.GeoDataFrame(inc_pov_merged, geometry='geometry')
    msa_income_shp = gpd.GeoDataFrame(msa_income_shp, geometry='geometry')
    #Make a spatial join with the msa_income_shp to get the msa name and msa income for each tract
    msa_cols_to_keep = ['state','cbsaId','geoId','msaName','msaTractId','lsad','msa_medInc','geometry']
    msa_income_shp_join = msa_income_shp[msa_cols_to_keep]
    #rename the columns to avoid left and right suffixes
    msa_income_shp_join.columns = ['state_msa','cbsaId','geoIdMsa','msaName','msaTractId','lsad','msa_medInc','geometry']
    final_merged_shp = gpd.sjoin(inc_pov_merged, msa_income_shp_join, how='left', predicate='intersects').drop(columns=['index_right'])
    #Reorder the columns to make the appearance of columns better
    final_merged_shp = final_merged_shp[['stateFP','state','geoId','tractId','tractName','cbsaId','geoIdMsa','msaName','msaTractId','lsad',\
                                        'med_inc','st_med_inc','msa_medInc','total_pop','pov_pop','pov_perc','area_land','area_water','lat','lon','geometry']]
    final_merged_shp_dissolved = final_merged_shp.dissolve(by='tractId')
    #Compute the area of the geometry
    final_merged_shp_dissolved['area_LI'] = final_merged_shp_dissolved['geometry'].area
    final_merged_shp_dissolved.reset_index(inplace=True)
    return final_merged_shp_dissolved

##Define a function to apply the low income conditions to the merged dataframe and save it as a shapefile
def apply_low_income_conditions():
    final_merged_shp_dissolved = merge_all_data()
    final_merged_shp_dissolved['low_income'] = 0
    final_merged_shp_dissolved['Type'] = ''
    #if poverty percentage is greater than 20, then the tract is low income
    final_merged_shp_dissolved.loc[final_merged_shp_dissolved['pov_perc'] > 20, 'low_income'] = 1
    # if the median income is less than 80% of the state median income, then the tract is low income
    final_merged_shp_dissolved.loc[final_merged_shp_dissolved['med_inc'] < final_merged_shp_dissolved['st_med_inc']*0.8, 'low_income'] = 1
    #if the median income is less than 80% of the MSA median income in case if LSAD is M1, then the tract is low income
    final_merged_shp_dissolved.loc[(final_merged_shp_dissolved['lsad'] == 'M1') & (final_merged_shp_dissolved['med_inc'] < final_merged_shp_dissolved['msa_medInc']*0.8), 'low_income'] = 1
    final_merged_shp_dissolved.loc[ :,'Type'] = 'Low Income'
    final_merged_shp_dissolved.to_file(FINAL_SHP_SAVE_PATH, driver='ESRI Shapefile')
    return final_merged_shp_dissolved

##Make a main function to run the script
def main():
    apply_low_income_conditions()

if __name__ == '__main__':
    main()