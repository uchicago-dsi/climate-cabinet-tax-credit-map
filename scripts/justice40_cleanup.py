#-*- coding: utf-8 -*-
## Load Dependencies
import os
import pandas as pd
import geopandas as gpd

##Set working directory and file save paths
WD = os.path.join(os.getcwd(), 'data')
J40_SHP_PATH = os.path.join(WD, "justice40 shapefile","usa","usa.shp")
SAVE_PATH = os.path.join(WD, "communities","justice40")

##Define a function to load the Justice40 data and clean it
def load_justice40_data() -> gpd.GeoDataFrame:
    try:
        justice40 = gpd.read_file(J40_SHP_PATH).to_crs(epsg=3857)
        cols_to_keep = ['GEOID10','SF', 'CF','TPF','UF_PFS','SN_C','SN_T','HRS_ET','LHE','FPL200S','UI_EXP','THRHLD','geometry']
        justice40 = justice40[cols_to_keep]
        justice40.columns = ['TractID','State','County','Tot_Pop','Unemp_Per','Disadv?','Disad_Tri?','Underinves','Low_HS_Edu','Low_Income','UI_EXP','THRHLD','geometry']
        justice_final = justice40[(justice40['Disadv?'] == 1) & (justice40['geometry'].is_valid == True)]
        justice_final.loc[:, 'Type'] = 'Justice40'
        #Compute the area of the geometry for each tract
        justice_final.loc[:, 'area_j40'] = justice_final['geometry'].area
        return justice_final
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f'Error loading utility data: {e}')
        return None


##Define a function to save the cleaned data
def save_justice40_data(justice_final: gpd.GeoDataFrame, save_path: str) -> None:
    try:
        if not os.path.exists(SAVE_PATH):
            os.mkdir(SAVE_PATH) 
        justice_final.to_file(save_path, driver='ESRI Shapefile')
        print(f'Justice40 data saved to {SAVE_PATH}')
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f'Error saving utility data: {e}')

##Make a main function to run the script
def main():
    justice_final = load_justice40_data()
    if justice_final is not None:
        save_justice40_data(justice_final, SAVE_PATH)

if __name__ == '__main__':
    main()