#-*- coding: utf-8 -*-
## Load Dependencies
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from branca.element import Figure
import os

##Set working directory and file save paths
WD = os.path.join(os.getcwd(), 'data')
COOPS_UTILS_PATH = os.path.join(WD, "coops_utilities","util_clean","util_clean.shp") #Rural Coops dataset
J40_OVERLAY_PATH = os.path.join(WD, "overlays", "j40_overlays.shp") #Justice40 Overlays dataset 
COAL_OVERLAY_PATH = os.path.join(WD, "overlays", "coal_overlays.shp") #Coal Overlays dataset 
FFE_OVERLAY_PATH = os.path.join(WD, "overlays", "ffe_overlays.shp") #Fossil Fuel Unemployment Overlays dataset
#ENERGY_OVERLAY_PATH = os.path.join(WD, "overlays", "energy_overlays.shp") #Energy Overlays dataset 
LOW_INCOME_OVERLAY_PATH = os.path.join(WD, "overlays", "low_income_overlays.shp") #Low Income Overlays dataset 
CTY_BORDERS_PATH = os.path.join(WD, "boundaries","county_clean","county_clean.shp") #County Borders dataset
STATE_BORDERS_PATH = os.path.join(WD, "boundaries","state_clean","state_clean.shp") #State Borders dataset
OUTPUT_SAVE_PATH = os.path.join(os.getcwd(), 'results')

##Define a function to create a map of the overlays
def create_overlay_map(j40: gpd.GeoDataFrame, coal: gpd.GeoDataFrame, ffe: gpd.GeoDataFrame, low_income: gpd.GeoDataFrame, coops_utils: gpd.GeoDataFrame, 
                       cty_borders: gpd.GeoDataFrame, state_borders: gpd.GeoDataFrame, state = 'Illinois') -> folium.Map:
    try:
        #Create a map of the US
        fig = Figure(width=800,height=700)
        m = folium.Map(location=[39.8283, -98.5795], tiles='cartodbpositron', zoom_start=4, control_scale=True)
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
                            tooltip=folium.features.GeoJsonTooltip(fields = ['Type','County','TractID','Subtype','NAME','Type_1','perc_cover'],
                                                                     aliases = ['Community:','County:','Tract ID:','Community Subtype:','Name:','Utility Type:','Percent Area Covered:']),
                                                                     popup=None).add_to(m)
        #Add the FFE overlay to the map as a GeoJSON layer
        folium.GeoJson(ffe[ffe['State_1']==state], name = "Energy Communities - Fossil Fuel Unemployment", style_function= lambda feature: {'fillColor':'green','color':'black','opacity':1,'weight':0.4},
                            tooltip=folium.features.GeoJsonTooltip(fields = ['Type','County','TractIDcty','MSA_NMSA','Subtype','NAME','Type_1','perc_cover'],
                                                                        aliases = ['Community:','County:','County Tract ID:','MSA/NMSA','Community Subtype:','Name:','Utility Type:','Percent Area Covered:']),
                                                                        popup=None).add_to(m)
        #Add the Low Income overlay to the map as a GeoJSON layer
        folium.GeoJson(low_income[low_income['State']==state], name = "Low Income Communities", style_function= lambda feature: {'fillColor':'purple','color':'black','opacity':1,'weight':0.4},
                            tooltip=folium.features.GeoJsonTooltip(fields = ['Type','County','TractID','NAME','Type_1','perc_cover'],
                                                                        aliases = ['Community:','County:','Tract ID:','Name:','Utility Type:','Percent Area Covered:']),
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
        print(e)


##Make a main function to load the datasets and run the script
def main():
    coops_utils = gpd.read_file(COOPS_UTILS_PATH, driver='ESRI Shapefile').to_crs(epsg=3857)
    j40 = gpd.read_file(J40_OVERLAY_PATH, driver='ESRI Shapefile').to_crs(epsg=3857)
    coal = gpd.read_file(COAL_OVERLAY_PATH, driver='ESRI Shapefile').to_crs(epsg=3857)
    ffe = gpd.read_file(FFE_OVERLAY_PATH, driver='ESRI Shapefile').to_crs(epsg=3857)
    #energy = gpd.read_file(ENERGY_OVERLAY_PATH, driver='ESRI Shapefile').to_crs(epsg=3857)
    low_income = gpd.read_file(LOW_INCOME_OVERLAY_PATH, driver='ESRI Shapefile').to_crs(epsg=3857)
    cty_borders = gpd.read_file(CTY_BORDERS_PATH, driver='ESRI Shapefile').to_crs(epsg=3857)
    state_borders = gpd.read_file(STATE_BORDERS_PATH, driver='ESRI Shapefile').to_crs(epsg=3857)
    fig = create_overlay_map(j40, coal, ffe, low_income, coops_utils, cty_borders, state_borders, state = 'Illinois')
    fig.save(os.path.join(OUTPUT_SAVE_PATH, 'IL_overlay_map.html'))

if __name__ == "__main__":
    main()