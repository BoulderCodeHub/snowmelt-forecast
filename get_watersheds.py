import pandas as pd 
import geopandas as gpd
import os
import plotly.graph_objects as go
import folium
import dash_leaflet as dl
import matplotlib.pyplot as plt

camels_basins = gpd.read_file(os.path.join('basin_data', 'basin_set_full_res', 'HCDN_nhru_final_671.shp'))

us_states = gpd.read_file(os.path.join('basin_data', 'cb_2018_us_state_500k', 'cb_2018_us_state_500k.shp'))
us_states = us_states.to_crs(crs=4326)
fig, ax = plt.subplots()
camels_basins.plot(ax = ax)
us_states.plot(ax = ax, facecolor = 'none', edgecolor = 'black', linewidth = 2.0)
ax.set_xlim([-115, -105])
ax.set_ylim([30, 40])
plt.show()

# basin data comes from 'https://www.cbrfc.noaa.gov/OUTGOING/BASINS'
list_of_files = ['CBRFC_Basins', 'CBRFC_FGroups', 'CBRFC_Zones_GSL', 'CBRFC_Zones_LC', 'CBRFC_Zones_UC']
list_of_enders = ['.dbf', '.prj', '.qpj', '.shp', '.shx']
for file_name in list_of_files:
  data_folder_current = os.path.join('basin_data', file_name)
  print(file_name)
  basin_filename = os.path.join(data_folder_current, file_name + '.shp')
  basin_gdf = gpd.read_file(basin_filename)
  basin_gdf = basin_gdf.to_crs("epsg:4326")
  basin_names = basin_gdf['ch5_id'].unique()
  print(basin_names)
  centroid_point = basin_gdf.dissolve().centroid
  basin_json = basin_gdf.to_json()
  print(centroid_point[0])
  m = folium.Map(location=[centroid_point[0].x, centroid_point[0].y], zoom_start=10)
  folium.GeoJson(basin_json).add_to(m)
  m.save(file_name + '.html')
