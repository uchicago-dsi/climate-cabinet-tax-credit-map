# -*- coding: utf-8 -*-
"""
This script downloads and processes tract shapefiles, and then merges them into a single GeoDataFrame.

Dependencies:
- requests
- bs4 (BeautifulSoup)
- urllib.parse
- zipfile
- pandas
- geopandas
- hydra

Usage:
- Make sure the required dependencies are installed.
- Place the script in the desired working directory.
- Create a 'conf' folder in the working directory containing the configuration file 'config.yaml'.
- Update the 'config.yaml' file with the required URLs and paths for downloading and saving tract shapefiles.
- Execute the script to download tract shapefiles, merge them, and save the merged GeoDataFrame.

Notes:
- The script downloads tract shapefiles from a specific URL, extracts them, and then merges them into a single GeoDataFrame.
- The input tract shapefiles must be in ESRI Shapefile format with valid geometries.
- The merged GeoDataFrame contains essential attributes like tract ID, tract name, area, latitude, longitude, and geometry for each tract.

Author: Sai Krishna
Date: 07-17-2023
"""

## Load Dependencies
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import zipfile
import pandas as pd
import geopandas as gpd
import omegaconf
import logging

## Configure the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)


def download_and_extract(url: str, save_path: str) -> None:
    """
    Download and extract a ZIP file from the given URL to the specified save path.

    Args:
        url (str): The URL of the ZIP file to download.
        save_path (str): The path where the downloaded file will be saved.
    """
    try:
        response = requests.get(url)
        with open(save_path, "wb") as file:
            file.write(response.content)
    except (FileNotFoundError, IOError, PermissionError, ValueError) as e:
        logger.info(f"Error downloading the file: {e}")
        return None


def download_tract_shapefiles(url: str, all_tracts_path: str) -> None:
    """
    Download tract shapefiles from the given URL to the specified directory path.

    Args:
        url (str): The base URL where the shapefiles are located.
        all_tracts_path (str): The path where the downloaded shapefiles will be stored.
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("a")
        for link in links:
            href = link.get("href")
            if href is not None and href.endswith(".zip"):
                download_url = urllib.parse.urljoin(url, href)
                file_name = href.split("/")[-1]
                logger.info(f"Downloading {file_name}...")
                download_and_extract(
                    download_url, os.path.join(all_tracts_path, file_name)
                )
                logger.info(f"{file_name} downloaded successfully.")
    except (FileNotFoundError, IOError, PermissionError, ValueError) as e:
        logger.info(f"Error downloading the file: {e}")
        return None


def merge_tract_shapefiles(all_tracts_path: str) -> gpd.GeoDataFrame or None:
    """
    Merge the downloaded tract shapefiles into a single GeoDataFrame.

    Args:
        all_tracts_path (str): The path where the downloaded shapefiles are stored.

    Returns:
        gpd.GeoDataFrame or None: The merged GeoDataFrame if successful, else None.
    """
    try:
        zip_files = [
            file for file in os.listdir(all_tracts_path) if file.endswith(".zip")
        ]
        # Empty list to store GeoDataFrames
        gdfs = []
        for zip_file in zip_files:
            with zipfile.ZipFile(os.path.join(all_tracts_path, zip_file), "r") as zf:
                shp_file = [file for file in zf.namelist() if file.endswith(".shp")][0]
                gdf = gpd.read_file(
                    f"zip://{os.path.join(all_tracts_path, zip_file)}!{shp_file}"
                )
                gdfs.append(gdf)
        # Check if all the DataFrames inside the gdfs list have the same columns
        for i in range(1, len(gdfs)):
            assert gdfs[i].columns.to_list() == gdfs[i - 1].columns.to_list()
        # Concatenate all the DataFrames inside the gdfs list to a single GeoDataFrame
        merged_tracts = pd.concat(gdfs, ignore_index=True)
        # Clean the merged_tracts DataFrame
        merged_tracts = merged_tracts[
            [
                "STATEFP",
                "GEOID",
                "NAMELSAD",
                "ALAND",
                "AWATER",
                "INTPTLAT",
                "INTPTLON",
                "geometry",
            ]
        ]
        merged_tracts.columns = [
            "stateFP",
            "tract_id",
            "tract_name",
            "area_land",
            "area_water",
            "lat",
            "lon",
            "geometry",
        ]
        merged_tracts["tract_id"] = merged_tracts["tract_id"].astype("int64")
        merged_tracts["stateFP"] = merged_tracts["stateFP"].astype(int)

        return merged_tracts
    except (FileNotFoundError, IOError, PermissionError, ValueError) as e:
        logger.info(f"Error merging the files: {e}")
        return None


def save_merged_tracts(merged_tracts: gpd.GeoDataFrame, final_save_path: str):
    """
    Save the merged tract shapefile to the specified path.

    Args:
        merged_tracts (gpd.GeoDataFrame): The merged GeoDataFrame.
        final_save_path (str): The path where the merged shapefile will be saved.
    """
    merged_tracts.to_file(final_save_path)
    logger.info(f"The merged tracts shapefile saved to {final_save_path}")


def main() -> None:
    wd = os.getcwd().replace("\\", "/")
    os.chdir(wd)
    yaml_path = os.path.join(os.path.dirname(wd), "conf", "config.yaml").replace(
        "\\", "/"
    )
    cfg = omegaconf.OmegaConf.load(yaml_path)
    paths = cfg.paths
    WD = os.getcwd().replace("\\", "/")
    os.chdrir(WD)
    scraper_paths = {
        # 'base_url_2021': os.path.join(WD, paths.scraper.base_url_2021),
        "base_url_2020": os.path.join(WD, paths.scraper.base_url_2020),
        "all_tracts_path": os.path.join(WD, paths.scraper.all_tracts_path),
        "merged_tracts_path": os.path.join(WD, paths.scraper.merged_tracts_path),
    }
    for path in scraper_paths.values():
        os.makedirs(os.path.dirname(path), exist_ok=True)
    download_tract_shapefiles(
        scraper_paths["base_url_2020"], scraper_paths["all_tracts_path"]
    )
    merged_tracts = merge_tract_shapefiles(scraper_paths["all_tracts_path"])
    save_merged_tracts(merged_tracts, scraper_paths["merged_tracts_path"])


if __name__ == "__main__":
    main()
