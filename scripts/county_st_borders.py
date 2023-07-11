#-*- coding: utf-8 -*-
## Load Dependencies
import os
import pandas as pd
import geopandas as gpd

##Set working directory and file save paths
WD = os.path.join(os.getcwd(), 'data')
STATE_FIPS_PATH = os.path.join(WD, "state_fips.csv") #State FIPS dataset
CT_PATH = os.path.join(WD, "county_tract","tl_2020_us_county.shp") #County borders dataset
ST_PATH = os.path.join(WD, "state_tract","tl_2020_us_state.shp") #State borders dataset
CT_SAVE_PATH = os.path.join(WD, "boundaries", "county_clean") #County borders dataset save path
ST_SAVE_PATH = os.path.join(WD, "boundaries", "state_clean") #State borders dataset save path

##Define a function to load and clean the county borders dataset
def load_county_borders() -> gpd.GeoDataFrame:
    try:
        county_df = gpd.read_file(CT_PATH).to_crs(epsg=3857)
        county_df['STATEFP'] = county_df['STATEFP'].astype(int)
        states = pd.read_csv(STATE_FIPS_PATH)[['St_FIPS', 'State']].rename(columns={'St_FIPS':'STATEFP'})
        county_df = county_df.merge(states, on='STATEFP', how='left')
        county_df = county_df.drop(columns=['COUNTYNS','GEOID','NAME','LSAD','CLASSFP','MTFCC','CSAFP','CBSAFP','METDIVFP','FUNCSTAT'])
        county_df.rename(columns={'NAMELSAD':'County'}, inplace=True)
        return county_df
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f'Error loading coal data: {e}')
        return None

##Define a function to load and clean the state borders dataset
def load_state_borders() -> gpd.GeoDataFrame:
    try:
        state_df = gpd.read_file(ST_PATH).to_crs(epsg=3857)
        state_df = state_df.drop(columns=['REGION', 'DIVISION',  'STATENS', 'GEOID','LSAD','MTFCC','FUNCSTAT'])
        state_df.rename(columns={'NAME':'State'}, inplace=True)
        return state_df
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f'Error loading coal data: {e}')
        return None

##Define a function to save the state and county borders datasets
def save_county_borders(county_df: gpd.GeoDataFrame) -> None:
    try:
        county_df.to_file(CT_SAVE_PATH)
        print(f"Saved county data to {CT_SAVE_PATH}")
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f'Error saving coal data: {e}')

def save_state_borders(state_df: gpd.GeoDataFrame) -> None:
    try:
        state_df.to_file(ST_SAVE_PATH)
        print(f"Saved state data to {ST_SAVE_PATH}")
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f'Error saving coal data: {e}')

##Make a main function to run the script
def main():
    county_df = load_county_borders()
    state_df = load_state_borders()
    if (county_df is not None):
        save_county_borders(county_df)
    if (state_df is not None):
        save_state_borders(state_df)

if __name__ == "__main__":
    main()