#-*- coding: utf-8 -*-
"""
This script performs spatial overlays on different datasets to analyze environmental justice and low-income communities. 
It creates a map with multiple GeoJSON layers representing different overlays and saves it as an interactive HTML file.

Dependencies:
- pandas
- numpy
- geopandas
- folium
- branca.element
- os
- hydra
- logging

Usage:
- Make sure the required dependencies are installed.
- Place the script in the desired working directory.
- Create a 'conf' folder in the working directory containing the configuration file 'config.yaml'.
- Update the 'config.yaml' file with paths to input datasets and the desired output directory for the map.
- Execute the script to perform spatial overlays and create the overlay map.

Note:
- The input datasets must be in ESRI Shapefile format with valid geometries.
- The script assumes the input datasets are projected in EPSG:3857 (Web Mercator) to ensure consistent spatial units for overlay operations.
- The map is focused on the state of Illinois by default, but you can change the focus state by modifying the 'state' parameter in the 'create_overlay_map' function.

Author: Sai Krishna
Date: 07-17-2023
"""
## Load Dependencies
import geopandas as gpd
import folium
from branca.element import Figure
import os
import hydra
import logging

## Configure the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)


##Define a function to create a map of the overlays
def create_overlay_map(j40: gpd.GeoDataFrame, coal: gpd.GeoDataFrame, ffe: gpd.GeoDataFrame, low_income: gpd.GeoDataFrame, coops_utils: gpd.GeoDataFrame, 
                       cty_borders: gpd.GeoDataFrame, state_borders: gpd.GeoDataFrame, state:str = 'Illinois') -> folium.Map:
    """
    Create an overlay map showing multiple GeoJSON layers representing different overlays.

    Parameters:
    - j40 (GeoDataFrame): The Justice40 overlay dataset.
    - coal (GeoDataFrame): The Energy Communities - Coal Closure overlay dataset.
    - ffe (GeoDataFrame): The Energy Communities - Fossil Fuel Unemployment overlay dataset.
    - low_income (GeoDataFrame): The Low Income Communities overlay dataset.
    - coops_utils (GeoDataFrame): The coops_utils dataset representing Municipal Utilities/ Rural CoOps.
    - cty_borders (GeoDataFrame): The county borders dataset.
    - state_borders (GeoDataFrame): The state borders dataset.
    - state (str): The state name to focus on in the map. Default is 'Illinois'.

    Returns:
    - Map: The overlay map as a Folium Map object.

    Notes:
    - The input datasets must be in the same CRS (Coordinate Reference System) for proper display.

    Example:
    j40_overlay = gpd.read_file('j40_overlay.shp')
    coal_overlay = gpd.read_file('coal_overlay.shp')
    ffe_overlay = gpd.read_file('ffe_overlay.shp')
    low_income_overlay = gpd.read_file('low_income_overlay.shp')
    coops_utils = gpd.read_file('coops_utils.shp')
    cty_borders = gpd.read_file('county_borders.shp')
    state_borders = gpd.read_file('state_borders.shp')

    map = create_overlay_map(j40_overlay, coal_overlay, ffe_overlay, low_income_overlay, coops_utils, cty_borders, state_borders, state='Illinois')
    map.save('overlay_map.html')
    """
    try:
        fig = Figure(width=800,height=700)
        m = folium.Map(location=[39.7837, -89.2719], tiles='cartodbpositron', zoom_start=4, control_scale=True)
        state = 'Illinois'
        #Add the base layer of the Utility territories to the map as a GeoJSON layer
        folium.GeoJson(coops_utils[coops_utils['State']==state], name = "Utilities/CoOps", style_function= lambda feature: {'fillColor':'yellow','color':'black','opacity':1,'weight':0.4},
                        tooltip=folium.features.GeoJsonTooltip(fields = ['NAME','Type_1'], aliases = ['Name:','Type:'], labels = True, sticky = True),
                        popup=None).add_to(m)
        #Add the J40 overlay to the map as a GeoJSON layer
        folium.GeoJson(j40[j40['State_1']==state], name = "Justice40", style_function= lambda feature: {'fillColor':'blue','color':'black','opacity':1,'weight':0.4},
                            tooltip=folium.features.GeoJsonTooltip(fields = ['Type_2','County','TractID','Tot_Pop','NAME','Type_1','perc_cover'], 
                                                                    aliases = ['Community:','County:','Tract ID:','Population:','Name:','Utility Type:','Percent Area Covered:']),
                                                                    popup=None).add_to(m)
        #Add the Coal overlay to the map as a GeoJSON layer
        folium.GeoJson(coal[coal['State_1']==state], name = "Energy Communities - Coal", style_function= lambda feature: {'fillColor':'red','color':'black','opacity':1,'weight':0.4},
                            tooltip=folium.features.GeoJsonTooltip(fields = ['Type_2','County','TractID','Subtype','NAME','Type_1','perc_cover'],
                                                                        aliases = ['Community:','County:','Tract ID:','Community Subtype:','Name:','Utility Type:','Percent Area Covered:']),
                                                                        popup=None).add_to(m)
        #Add the FFE overlay to the map as a GeoJSON layer
        folium.GeoJson(ffe[ffe['State_1']==state], name = "Energy Communities - Fossil Fuel Unemployment", style_function= lambda feature: {'fillColor':'green','color':'black','opacity':1,'weight':0.4},
                            tooltip=folium.features.GeoJsonTooltip(fields = ['Type_2','County','TractIDcty','MSA_NMSA','Subtype','NAME','Type_1','perc_cover'],
                                                                        aliases = ['Community:','County:','County Tract ID:','MSA/NMSA','Community Subtype:','Name:','Utility Type:','Percent Area Covered:']),
                                                                        popup=None).add_to(m)
        #Add the Low Income overlay to the map as a GeoJSON layer
        folium.GeoJson(low_income[low_income['State']==state], name = "Low Income Communities", style_function= lambda feature: {'fillColor':'purple','color':'black','opacity':1,'weight':0.4},
                            tooltip=folium.features.GeoJsonTooltip(fields = ['Type_2','msaName','msaTractId','NAME','Type_1','perc_cover'],
                                                                        aliases = ['Community:','MSA:','MSA Tract ID:','Name:','Utility Type:','Percent Area Covered:']),
                                                                        popup=None).add_to(m)
        #add the county borders to the map as a GeoJSON layer with no tooltips
        folium.GeoJson(cty_borders[cty_borders['State']==state], name = "County Borders", style_function= lambda feature: {'fillColor':'none','color':'black','opacity':1,'weight':0.4},
                            tooltip=None, popup=None).add_to(m)
        #add the state borders to the map as a GeoJSON layer with no tooltips
        folium.GeoJson(state_borders, name = "State Borders", style_function= lambda feature: {'fillColor':'none','color':'black','opacity':1,'weight':0.4},
                            tooltip=None, popup=None).add_to(m)
        #Add a layer control to the map
        folium.LayerControl(collapsed=False).add_to(m)
        fig.add_child(m)
        #Return the map
        return fig
    except Exception as e:
        logger.info(e)
        return None

@hydra.main(config_path='../conf',config_name = 'config')
def main(cfg):
    paths = cfg.paths
    WD = os.getcwd().replace("\\","/")
    os.chdir(WD)
    map_paths = {
        'coops_utils': os.path.join(WD, paths.utilities.util_clean_path).replace("\\","/"),
        'j40': os.path.join(WD, paths.overlays.j40_overlay_path).replace("\\","/"),
        'coal': os.path.join(WD, paths.overlays.coal_overlay_path).replace("\\","/"),
        'ffe': os.path.join(WD, paths.overlays.ffe_overlay_path).replace("\\","/"),
        # 'energy': os.path.join(WD, paths.overlays.energy_overlay_path).replace("\\","/"),
        'low_income': os.path.join(WD, paths.overlays.low_income_overlay_path).replace("\\","/"),
        'cty_borders': os.path.join(WD, paths.boundaries.ct_clean_path).replace("\\","/"),
        'state_borders': os.path.join(WD, paths.boundaries.st_clean_path).replace("\\","/"),
        'output_html': os.path.join(WD, paths.maps.output_html_path).replace("\\","/")
    }
    for path in map_paths.values():
        os.makedirs(os.path.dirname(path), exist_ok=True)
    coops_utils = gpd.read_file(map_paths['coops_utils'], driver='ESRI Shapefile').to_crs(epsg=3857)
    j40 = gpd.read_file(map_paths['j40'], driver='ESRI Shapefile').to_crs(epsg=3857)
    coal = gpd.read_file(map_paths['coal'], driver='ESRI Shapefile').to_crs(epsg=3857)
    ffe = gpd.read_file(map_paths['ffe'], driver='ESRI Shapefile').to_crs(epsg=3857)
    #energy = gpd.read_file(map_paths['energy'], driver='ESRI Shapefile').to_crs(epsg=3857)
    low_income = gpd.read_file(map_paths['low_income'], driver='ESRI Shapefile').to_crs(epsg=3857)
    cty_borders = gpd.read_file(map_paths['cty_borders'], driver='ESRI Shapefile').to_crs(epsg=3857)
    state_borders = gpd.read_file(map_paths['state_borders'], driver='ESRI Shapefile').to_crs(epsg=3857)
    fig = create_overlay_map(j40, coal, ffe, low_income, coops_utils, cty_borders, state_borders, state = 'Illinois')
    fig.save(map_paths['output_html'])

if __name__ == "__main__":
    main()