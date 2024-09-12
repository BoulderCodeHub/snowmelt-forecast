import pandas as pd 
import geopandas as gpd
import os
import plotly.graph_objects as go
import folium
import dash_leaflet as dl
from dash import Dash, html, dcc, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_extensions.javascript import assign
from shapely import Point, LineString, buffer
import matplotlib.pyplot as plt
import numpy as np
import json
import copy

premade_outlet_method = False
if premade_outlet_method:
  basin_filename = os.path.join('basin_data', 'CBRFC_Basins', 'CBRFC_Basins.shp')
  basin_gdf = gpd.read_file(basin_filename)
  basin_gdf = basin_gdf.to_crs(crs=4326)
  upstream_key = {}
  for index in basin_gdf.index:
    this_loc = basin_gdf[basin_gdf.index == index]
    geom_list = []
    if len(this_loc.index) > 0:
      geom_list.append(buffer(Point(this_loc.loc[this_loc.index[0], 'x_outlet'], this_loc.loc[this_loc.index[0], 'y_outlet']), 0.001))
    new_shapefile = gpd.GeoDataFrame(this_loc, crs = basin_gdf.crs, geometry = geom_list)
    downstream_basins = gpd.sjoin(basin_gdf, new_shapefile, how = 'inner', predicate = 'intersects')
    for dwn_idx in downstream_basins.index:
      if dwn_idx != index:
        downstream_basin = downstream_basins.loc[dwn_idx, 'ch5_id_left']
        upstream_basin = basin_gdf.loc[index, 'ch5_id']
        if downstream_basin in upstream_key:
          if upstream_basin not in upstream_key[downstream_basin]:
            upstream_key[downstream_basin].append(upstream_basin)
        else:
          upstream_key[downstream_basin] = [upstream_basin,]

marks = [0, 10, 20, 50, 100, 200, 500, 1000]
colorscale = ['#FFEDA0', '#FED976', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026']
forecast_list = ['All',]
for f in os.scandir('forecasts'):
  if f.is_dir():
    if f.path.split('\\')[-1] == 'GJLOC':
      forecast_list.append('GJNC2')
    else:
      forecast_list.append(f.path.split('\\')[-1])

def get_style(feature):
    color = [colorscale[i] for i, item in enumerate(marks) if feature["properties"]["density"] > item][-1]
    return dict(fillColor=color, weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)


app = Dash(__name__)
lat1, lon1 = 36.9545, -111.49

app = Dash()
rfc_list = ['Arkansas', 'Colorado', 'California-Nevada', 'Missouri', 'Northwest', 'West Gulf']
starting_rfc = 'Colorado'
rfc_alts = {}
for rfc in rfc_list:
  rfc_alts[rfc] = {}
rfc_alts['Arkansas']['rfc'] = 'ABRFC'
rfc_alts['Colorado']['rfc'] = 'CBRFC'
rfc_alts['California-Nevada']['rfc'] = 'CNRFC'
rfc_alts['Missouri']['rfc'] = 'MBRFC'
rfc_alts['Northwest']['rfc'] = 'NWRFC'
rfc_alts['West Gulf']['rfc'] = 'WGRFC'
rfc_alts['Arkansas']['features'] = ['None',]
rfc_alts['Colorado']['features'] = ['reforecasts',]
rfc_alts['California-Nevada']['features'] = ['None',]
rfc_alts['Missouri']['features'] = ['None',]
rfc_alts['Northwest']['features'] = ['None',]
rfc_alts['West Gulf']['features'] = ['None',]

input_details = html.Div(
                [
                    html.Div(
                    [
                        html.Div(
                        [
                            html.Div('Type of Map: ', id = 'map-type-text'),
                     
                        ],
                        style = {"display": 'inline-block', 'vertical-align': 'top', "width": '45%', 'height': '4vh'},),
                        html.Div(
                        [
                            html.Div('Type of Feature: ', id = 'feature-type-text'),
                    
                        ],
                        style = {"display": 'inline-block', 'vertical-align': 'top', "width": '45%', 'height': '4vh'},),
                    ],
                    style = {"width": '95%', 'height': '4vh', 'vertical-align': 'top', },),

                    html.Div(
                    [
                        html.Div(
                        [
                            dcc.Dropdown(rfc_list, starting_rfc, id='map-type'),
                        ],
                        style = {"display": 'inline-block', 'vertical-align': 'top', "width": '45%', 'height': '4vh'},),
                        html.Div(
                        [
                            dcc.Dropdown(rfc_alts[starting_rfc]['features'], rfc_alts[starting_rfc]['features'][0], id='feature-type'),
                        ],
                        style = {"display": 'inline-block', 'vertical-align': 'top', "width": '45%', 'height': '4vh'},),
                    ],
                    style = {"width": '95%', 'height': '4vh', 'vertical-align': 'top', },),
                    html.Div(
                    [
                        html.Div(
                        [
                            html.Div('Forecast Location: ', id = 'forecast-location-text'),
                     
                        ],
                        style = {"display": 'inline-block', 'vertical-align': 'top', "width": '45%', 'height': '4vh'},),
                    ],
                    style = {"width": '95%', 'height': '4vh', 'vertical-align': 'top', },),
                    html.Div(
                    [
                        html.Div(
                        [
                            dcc.Dropdown(forecast_list, forecast_list[0], id='forecast-type'),
                        ],
                        style = {"display": 'inline-block', 'vertical-align': 'top', "width": '45%', 'height': '4vh'},),
                    ],
                    style = {"width": '95%', 'height': '4vh', 'vertical-align': 'top', },),

                ],
                style = {"display": 'inline-block', 'vertical-align': 'top', "width": '45%', 'height': '98vh'},
)


default_map_children = [
    dl.TileLayer(),
    dl.GeoJSON(id='map-basins'),
    dl.GeoJSON(id='map-forecast-points', options={"style":{"color":"yellow"}}),
]

map_input_results_tab = html.Div(
    [
        html.H2('CAMELS-CRB basins'),
        dl.Map(
            id='leaflet-map',
            style={'width': '95%', 'height': '80vh'},
            center=[lat1, lon1],
            zoom=5,
            children=default_map_children
        )
    ],
    style = {"display": 'inline-block', "width": '45%', 'height': '92vh'},
)

app.layout = html.Div([input_details, map_input_results_tab])

  
@app.callback(
    Output('map-forecast-points', 'data'),
    Input('forecast-type', 'value')
)
def update_forecast_locations(forecast_location):
  basin_filename = os.path.join('basin_data', 'CBRFC_Basins', 'CBRFC_Basins.shp')
  basin_gdf = gpd.read_file(basin_filename)
  basin_gdf = basin_gdf.to_crs(crs=4326)

  new_shapefile = gpd.GeoDataFrame()
  geom_list = []
  for forecast_loc in forecast_list:
    if forecast_loc == forecast_location or forecast_location == 'All':
      this_loc = basin_gdf[basin_gdf['ch5_id'] == forecast_loc]
      if len(this_loc.index) > 0:
        new_shapefile = pd.concat([new_shapefile, this_loc], axis = 0)
        geom_list.append(Point(this_loc.loc[this_loc.index[0], 'x_outlet'], this_loc.loc[this_loc.index[0], 'y_outlet']))
  new_shapefile = gpd.GeoDataFrame(new_shapefile, crs = basin_gdf.crs, geometry = geom_list)
  return new_shapefile.__geo_interface__
  
@app.callback(
    Output('map-basins', 'data'),
    Input('forecast-type', 'value'),
    Input('map-type', 'value')
)
def update_estimates(forecast_loc, basin_use):
#    if basin_use == 'All':
#      basin_gdf = pd.DataFrame()
#      full_upstream_record = {}
#      for rfc in rfc_list:
#        if rfc != 'All':
#          file_name = rfc_alts[rfc]['rfc']
#          file_path = os.path.join('basin_data', file_name + '_Basins', 'b_' + file_name.lower() + '.shp')
#          basin_gdf_int = gpd.read_file(file_path)
#          basin_gdf_int = basin_gdf_int.to_crs(crs=4326)
#          basin_gdf = pd.concat([basin_gdf, basin_gdf_int], axis = 0)
#          json_file_path = os.path.join('basin_data', file_name + '_upstream_network.json')
#          with open(json_file_path) as f_in:
#            full_record_int = json.load(f_in)
#          for basin in full_record_int:
#            full_upstream_record[basin] = full_record_int[basin].copy()
#          
#            
#      basin_gdf = gpd.GeoDataFrame(basin_gdf, crs = basin_gdf_int.crs, geometry = basin_gdf['geometry'])
#    else:
    file_name = rfc_alts[basin_use]['rfc']
    file_path = os.path.join('basin_data', file_name + '_Basins', 'b_' + file_name.lower() + '.shp')
    basin_gdf = gpd.read_file(file_path)
    basin_gdf = basin_gdf.to_crs(crs=4326)
    json_file_path = os.path.join('basin_data', file_name + '_upstream_network.json')
    with open(json_file_path) as f_in:
      full_upstream_record = json.load(f_in)
    data_folder_current = os.path.join('basin_data', file_name)
    basin_filename = os.path.join(data_folder_current, file_name + '.shp')
    for col in basin_gdf.columns:
      print(col)
      print(basin_gdf[col])
      
    basin_id_label = 'CH5_ID'
    all_upstream_gdf = gpd.GeoDataFrame()
    for index in basin_gdf.index:
      if forecast_loc == 'All':
        all_upstream_gdf = pd.concat([all_upstream_gdf, basin_gdf[basin_gdf.index == index]])
      elif forecast_loc in full_upstream_record:
        if basin_gdf.loc[index,basin_id_label] in full_upstream_record[forecast_loc] or basin_gdf.loc[index, basin_id_label] == forecast_loc:
          all_upstream_gdf = pd.concat([all_upstream_gdf, basin_gdf[basin_gdf.index == index]])
    all_upstream_gdf = gpd.GeoDataFrame(all_upstream_gdf, crs = basin_gdf.crs, geometry = all_upstream_gdf['geometry'])      

    basin_key = pd.read_csv('basin_data/gage_ids.csv', index_col = 0)
    basin_display = {}
    if basin_id_label in basin_gdf:
      basin_names = basin_gdf[basin_id_label].unique()
      for basin_id in basin_names:
        try:
          basin_display[basin_id] = basin_key.loc[basin_id, 'DESCRIPTION']
        except:
          pass
      basin_disp = []
      for index_val in all_upstream_gdf.index:
        try:
          basin_disp.append(basin_display[all_upstream_gdf.loc[index_val, basin_id_label]])
        except:
          basin_disp.append('No name')
      return all_upstream_gdf.__geo_interface__
    else:
      return all_upstream_gdf.__geo_interface__
      
        
        
if __name__ == '__main__':
    app.run_server(debug=True)

