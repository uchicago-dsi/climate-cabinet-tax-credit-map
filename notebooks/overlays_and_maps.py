#-*- coding: utf-8 -*-
## Load Dependencies
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from branca.element import Figure
pd.set_option('display.max_columns', None)

##Set Working Directory
import os
current_dir = os.getcwd()
wd = os.path.join(current_dir,'data/')
wd = wd.replace('\\', '/')
##Load Justice40 Data
justice_final_path = wd+'justice40_final/justice40_final.shp'
justice_final = gpd.read_file(justice_final_path, driver='ESRI Shapefile').to_crs(epsg=3857)

##Load the Utility Datasets (Rural CoOps and Municipal Utilities)
rural_coops_path = wd+'rural_coops/rural_coops.shp'
municipal_utils_path = wd+'municipal_utils/municipal_utils.shp'
rural_coops = gpd.read_file(rural_coops_path, driver='ESRI Shapefile').to_crs(epsg=3857)
municipal_utils= gpd.read_file(municipal_utils_path, driver='ESRI Shapefile').to_crs(epsg=3857)

##Load the Energy Communities datasets
#Coal Closure
coal_path = (wd + 'energy_coal/coal_df.shp')
coal_df = gpd.read_file(coal_path, driver='ESRI Shapefile').to_crs(epsg=3857)
#Fossil Fuel Unemployment
ffe_path = (wd + 'energy_ffe/ffe_df.shp')
ffe_df = gpd.read_file(ffe_path, driver='ESRI Shapefile').to_crs(epsg=3857)

##Making Overlays
def overlays(rural = 0, municipal = 0, community='j40'):
    if ((rural == 1) & (community=='j40')):
        j40_rural_overlay = gpd.overlay(justice_final, rural_coops, how='intersection')
        j40_rural_overlay['areaInters'] = j40_rural_overlay.geometry.area
        j40_rural_overlay['perc_cover'] = np.round((j40_rural_overlay['areaInters'] / j40_rural_overlay['area']) * 100 , 4)
        return j40_rural_overlay
    elif ((rural == 1) & (community=='coal')):
        coal_rural_overlay = gpd.overlay(coal_df, rural_coops, how='intersection')
        coal_rural_overlay['areaInters'] = coal_rural_overlay.geometry.area
        coal_rural_overlay['perc_cover'] = np.round((coal_rural_overlay['areaInters'] / coal_rural_overlay['area']) * 100 , 4)
        return coal_rural_overlay
    elif ((rural == 1) & (community=='ffe')):
        ffe_rural_overlay = gpd.overlay(ffe_df, rural_coops, how='intersection')
        ffe_rural_overlay['areaInters'] = ffe_rural_overlay.geometry.area
        ffe_rural_overlay['perc_cover'] = np.round((ffe_rural_overlay['areaInters'] / ffe_rural_overlay['area']) * 100 , 4)
        return ffe_rural_overlay
    elif ((municipal == 1) & (community=='j40')):
        j40_municipal_overlay = gpd.overlay(justice_final, municipal_utils, how='intersection')
        j40_municipal_overlay['areaInters'] = j40_municipal_overlay.geometry.area
        j40_municipal_overlay['perc_cover'] = np.round((j40_municipal_overlay['areaInters'] / j40_municipal_overlay['area']) * 100 , 4)
        return j40_municipal_overlay
    elif ((municipal == 1) & (community=='coal')):
        coal_municipal_overlay = gpd.overlay(coal_df, municipal_utils, how='intersection')
        coal_municipal_overlay['areaInters'] = coal_municipal_overlay.geometry.area
        coal_municipal_overlay['perc_cover'] = np.round((coal_municipal_overlay['areaInters'] / coal_municipal_overlay['area']) * 100 , 4)
        return coal_municipal_overlay
    elif ((municipal == 1) & (community=='ffe')):
        ffe_municipal_overlay = gpd.overlay(ffe_df, municipal_utils, how='intersection')
        ffe_municipal_overlay['areaInters'] = ffe_municipal_overlay.geometry.area
        ffe_municipal_overlay['perc_cover'] = np.round((ffe_municipal_overlay['areaInters'] / ffe_municipal_overlay['area']) * 100 , 4)
        return ffe_municipal_overlay

##Making Maps based off of the overlays
def overlayed_plot(rural=0, municipal=0, State = "Illinois"):
    if (rural ==1):
        fig = Figure(width=800,height=700)
        m = folium.Map(location=(40,-89),zoom_start=7)
        ##Base Co-op Layer
        folium.GeoJson(rural_coops[rural_coops['State']==State], name='Co-Op Territories',  style_function=lambda feature: {'fillColor': 'yellow','color': 'black','opacity':1,'weight': 0.4},
               tooltip=folium.features.GeoJsonTooltip(fields= ['NAME', 'TYPE'], aliases=['Co-Op:', 'Type:'], labels=True, sticky=True),
               popup=None
               ).add_to(m)
        ##Overlay J40 Layer
        intersection_j40_state = overlays(rural=1, community = 'j40')
        intersection_j40_state = intersection_j40_state[intersection_j40_state['State_1']==State].to_crs(epsg=3857)
        folium.GeoJson(intersection_j40_state, name='Justice40 Layer',  style_function=lambda feature: {'fillColor': 'blue','color': 'black','opacity':1,'weight': 0.4},
               tooltip=folium.features.GeoJsonTooltip(fields=['NAME','County', 'TractID', 'Tot_Pop','perc_cover', 'Type_1'], aliases=['Co-Op:', 'County:', 'Tract ID:', 'Population:','Percent Area Covered:','Type:'],labels=True, sticky=True),
                popup=None  # Disable the popup
                ).add_to(m)
        ##Overlay Coal Layer
        intersection_coal_state = overlays(rural=1, community = 'coal')
        intersection_coal_state = intersection_coal_state[intersection_coal_state['State_1']==State].to_crs(epsg=3857)
        folium.GeoJson(intersection_coal_state, name='Energy Communities - Coal Layer',  style_function=lambda feature: {'fillColor': 'red','color': 'black','opacity':1,'weight': 0.4},
               tooltip=folium.features.GeoJsonTooltip(fields=['NAME','County', 'TractID', 'label','perc_cover', 'Type_1'], aliases=['Co-Op:', 'County:', 'TractID:', 'Label:','Percent Area Covered:','Type:'],labels=True, sticky=True),
                popup=None  # Disable the popup
                ).add_to(m)
        ##Overlay FFE Layer
        intersection_ffe_state = overlays(rural=1, community = 'ffe')
        intersection_ffe_state = intersection_ffe_state[intersection_ffe_state['State_1']==State].to_crs(epsg=3857)
        folium.GeoJson(intersection_ffe_state, name='Energy Communities - FFE Layer',  style_function=lambda feature: {'fillColor': 'green','color': 'black','opacity':1,'weight': 0.4},
               tooltip=folium.features.GeoJsonTooltip(fields=['NAME','County', 'TractIDcty', 'MSA_NMSA','perc_cover', 'Type_1'], aliases=['Co-Op:', 'County:', 'CountyID:', 'MSA/NMSA:','Percent Area Covered:','Type:'],labels=True, sticky=True),
                popup=None  # Disable the popup
                ).add_to(m)
        fig.add_child(m)
    if (municipal ==1):
        fig = Figure(width=800,height=700)
        m = folium.Map(location=(40,-89),zoom_start=7)
        ##Base Co-op Layer
        folium.GeoJson(municipal_utils[municipal_utils['State']==State], name='Municipal Utility Territories',  style_function=lambda feature: {'fillColor': 'yellow','color': 'black','opacity':1,'weight': 0.4},
               tooltip=folium.features.GeoJsonTooltip(fields= ['NAME','TYPE'], aliases=['Utility:','Type:'], labels=True, sticky=True),
               popup=None
               ).add_to(m)
        ##Overlay J40 Layer
        intersection_j40_state = overlays(municipal=1, community = 'j40')
        intersection_j40_state = intersection_j40_state[intersection_j40_state['State_1']==State].to_crs(epsg=3857)
        folium.GeoJson(intersection_j40_state, name='Justice40 Layer',  style_function=lambda feature: {'fillColor': 'blue','color': 'black','opacity':1,'weight': 0.4},
               tooltip=folium.features.GeoJsonTooltip(fields=['NAME','County', 'TractID', 'Tot_Pop','perc_cover', 'Type_1'], aliases=['Utility:', 'County:', 'Tract ID:', 'Population:','Percent Area Covered:','Type:'],labels=True, sticky=True),
                popup=None  # Disable the popup
                ).add_to(m)
        ##Overlay Coal Layer
        intersection_coal_state = overlays(municipal=1, community = 'coal')
        intersection_coal_state = intersection_coal_state[intersection_coal_state['State_1']==State].to_crs(epsg=3857)
        folium.GeoJson(intersection_coal_state, name='Energy Communities - Coal Layer',  style_function=lambda feature: {'fillColor': 'red','color': 'black','opacity':1,'weight': 0.4},
               tooltip=folium.features.GeoJsonTooltip(fields=['NAME','County', 'TractID', 'label','perc_cover', 'Type_1'], aliases=['Utility:', 'County:', 'TractID:', 'Label:','Percent Area Covered:','Type:'],labels=True, sticky=True),
                popup=None  # Disable the popup
                ).add_to(m)
        ##Overlay FFE Layer
        intersection_ffe_state = overlays(municipal=1, community = 'ffe')
        intersection_ffe_state = intersection_ffe_state[intersection_ffe_state['State_1']==State].to_crs(epsg=3857)
        folium.GeoJson(intersection_ffe_state, name='Energy Communities - FFE Layer',  style_function=lambda feature: {'fillColor': 'green','color': 'black','opacity':1,'weight': 0.4},
               tooltip=folium.features.GeoJsonTooltip(fields=['NAME','County', 'TractIDcty', 'MSA_NMSA','perc_cover', 'Type_1'], aliases=['Utility:', 'County:', 'CountyID:', 'MSA/NMSA:','Percent Area Covered:','Type:'],labels=True, sticky=True),
                popup=None  # Disable the popup
                ).add_to(m)
        fig.add_child(m)

    folium.TileLayer('openstreetmap').add_to(m)   
    folium.LayerControl(collapsed= False).add_to(m)   
    return fig

if __name__ == "__main__":
    fig =  overlayed_plot(rural=1, municipal=0)  # Call the function with desired parameters
    # Save the map as an HTML file
    fig.save('map.html')

import webbrowser
webbrowser.open('map.html',new=2)