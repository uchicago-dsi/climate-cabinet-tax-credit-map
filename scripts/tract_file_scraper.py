#-*- coding: utf-8 -*-
## Load Dependencies
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import zipfile
import pandas as pd
import geopandas as gpd

##Set working directory, file save paths and the base url
WD = os.path.join(os.getcwd(), 'data','Low Income Communities')
ALL_TRACTS_PATH = os.path.join(WD, 'all_tracts_2020')
if not os.path.exists(ALL_TRACTS_PATH):
    os.makedirs(ALL_TRACTS_PATH)
MERGED_TRACTS_PATH = os.path.join(WD, 'merged_tracts_2020')
FINAL_SAVE_PATH = os.path.join(MERGED_TRACTS_PATH, 'merged_tracts_2020.shp')
# BASE_URL = 'https://www2.census.gov/geo/tiger/TIGER2021/TRACT/' #if 2021 shape files are needed.
BASE_URL = 'https://www2.census.gov/geo/tiger/TIGER2020/TRACT/' #for 2020 shape files

##Define a function to download and write the ZIP files
def download_and_extract(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)

## Define a function to download tract shapefiles from the Census Bureau website (FTP Layer)
def download_tract_shapefiles():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href is not None and href.endswith('.zip'):
            download_url = urllib.parse.urljoin(BASE_URL, href)
            file_name = href.split('/')[-1]
            print(f'Downloading {file_name}...')
            download_and_extract(download_url, os.path.join(ALL_TRACTS_PATH, file_name))
            print(f'{file_name} downloaded successfully.')

##Define a function to extract and merge the downloaded tract shapefiles
def merge_tract_shapefiles():
    zip_files = [file for file in os.listdir(ALL_TRACTS_PATH) if file.endswith('.zip')]
    #Empty list to store GeoDataFrames
    gdfs = []
    for zip_file in zip_files:
        with zipfile.ZipFile(os.path.join(ALL_TRACTS_PATH, zip_file), 'r') as zf:
            shp_file = [file for file in zf.namelist() if file.endswith('.shp')][0]
            gdf = gpd.read_file(f'zip://{os.path.join(ALL_TRACTS_PATH, zip_file)}!{shp_file}')
            gdfs.append(gdf)
    #Check if all the DataFrames inside the gdfs list have the same columns
    for i in range(1, len(gdfs)):
        assert gdfs[i].columns.to_list() == gdfs[i-1].columns.to_list()
    #Concatenate all the DataFrames inside the gdfs list to a single GeoDataFrame
    merged_tracts = pd.concat(gdfs, ignore_index=True)
    #Clean the merged_tracts DataFrame
    merged_tracts = merged_tracts[['STATEFP', 'GEOID', 'NAMELSAD', 'ALAND', 'AWATER', 'INTPTLAT', 'INTPTLON', 'geometry']]
    merged_tracts.columns = ['stateFP', 'tract_id', 'tract_name', 'area_land', 'area_water', 'lat', 'lon', 'geometry']
    merged_tracts['tract_id'] = merged_tracts['tract_id'].astype('int64')
    merged_tracts['stateFP'] = merged_tracts['stateFP'].astype(int)

    return merged_tracts

#Define a function to save the merged tract shapefile
def save_merged_tracts(merged_tracts):
    if not os.path.exists(MERGED_TRACTS_PATH):
        os.makedirs(MERGED_TRACTS_PATH)
    merged_tracts.to_file(FINAL_SAVE_PATH)
    print(f"The merged tracts shapefile saved to {FINAL_SAVE_PATH}")

# Make a mian function to run the script
def main():
    download_tract_shapefiles()
    merged_tracts = merge_tract_shapefiles()
    save_merged_tracts(merged_tracts)

if __name__ == '__main__':
    main()