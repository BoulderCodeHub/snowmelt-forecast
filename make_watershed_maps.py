import pandas as pd 
import geopandas as gpd
import os
import dash_leaflet as dl
from dash import Dash, html, dcc, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_extensions.javascript import assign
import matplotlib.pyplot as plt
import numpy as np
import json
import copy
from datetime import datetime
import subbasin_plots as sbplt
import basin_reader as br

forecast_list = {}
for f in os.scandir('forecasts'):
  if f.is_dir():
    rfc = f.path.split('\\')[-1]
    if rfc not in forecast_list:
      forecast_list[rfc] = []
    basin_list_1 = []
    for ff in os.scandir(os.path.join('forecasts',rfc)):
      forecast_loc = ff.path.split('\\')[-1]
      if forecast_loc not in basin_list_1:
        basin_list_1.append(forecast_loc)
          
    basin_key = pd.read_csv(os.path.join('basin_data', rfc + '_Basins', 'gage_ids.csv'), index_col = 0)
    if 'ID' not in basin_key.columns:
      basin_key = pd.read_csv(os.path.join('basin_data', rfc + '_Basins', 'gage_ids.csv'))
    basin_list_2 = basin_key['ID'].unique()
    for ff in basin_list_1:
      if ff in basin_list_2:
        if ff == 'GJLOC':
          forecast_list[rfc].append('GJNC2')
        else:        
          forecast_list[rfc].append(ff)
    
    

app = Dash(__name__)
lat1, lon1 = -111.49, 36.9545
obs_loc = gpd.read_file(os.path.join('basin_data', 'national_shapefile_lro_3month_95', 'national_shapefile_lro_3month_95.shp'))
new_gis = pd.DataFrame()
for index, row in obs_loc.iterrows():
  if row['RFC'] == 'mbrfc':
    this_gdf = obs_loc[obs_loc.index == index]
    new_gis = pd.concat([new_gis, this_gdf])
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
rfc_alts['California-Nevada']['features'] = ['forecasts',]
rfc_alts['Missouri']['features'] = ['None',]
rfc_alts['Northwest']['features'] = ['None',]
rfc_alts['West Gulf']['features'] = ['None',]
rfc_alts['Arkansas']['basin_id_label'] = 'CH5_ID'
rfc_alts['Colorado']['basin_id_label'] = 'CH5_ID'
rfc_alts['California-Nevada']['basin_id_label'] = 'NAME'
rfc_alts['Missouri']['basin_id_label'] = 'NAME'
rfc_alts['Northwest']['basin_id_label'] = 'CH5_ID'
rfc_alts['West Gulf']['basin_id_label'] = 'CH5_ID'
rfc_alts['Arkansas']['dissolve_precision'] = 0
rfc_alts['Colorado']['dissolve_precision'] = 0
rfc_alts['California-Nevada']['dissolve_precision'] = 0.00075
rfc_alts['Missouri']['dissolve_precision'] = 0
rfc_alts['Northwest']['dissolve_precision'] = 0
rfc_alts['West Gulf']['dissolve_precision'] = 0
input_details = html.Div(
                [
                    html.Div(
                    [
                        html.Div('Type of Map: ', id = 'map-type-text'),
                     
                    ],
                    style = {'vertical-align': 'top', "width": '97%', 'height': '6vh'},),
                    html.Div(
                    [
                        dcc.Dropdown(rfc_list, starting_rfc, id='map-type'),
                    ],
                    style = {"display": 'inline-block', 'vertical-align': 'top', "width": '97%', 'height': '6vh'},),
                    html.Div(
                    [
                        html.Div('Type of Feature: ', id = 'feature-type-text'),
                    
                    ],
                    style = {'vertical-align': 'top', "width": '97%', 'height': '6vh'},),
                    html.Div(
                    [
                        dcc.Dropdown(rfc_alts[starting_rfc]['features'], rfc_alts[starting_rfc]['features'][0], id='feature-type'),
                    ],
                    style = {'vertical-align': 'top', "width": '97%', 'height': '6vh'},),
                    html.Div(
                    [
                        html.Div('Forecast Location: ', id = 'forecast-location-text'),
                    
                    ],
                    style = {'vertical-align': 'top', "width": '97%', 'height': '6vh'},),
                    html.Div(
                    [
                        dcc.Dropdown(forecast_list[rfc_alts[starting_rfc]['rfc']], forecast_list[rfc_alts[starting_rfc]['rfc']][0], id='forecast-type'),
                    ],
                    style = {'vertical-align': 'top', "width": '97%', 'height': '6vh'},),
                    html.Div(
                    [
                        html.Div('Forecast Year: ', id = 'forecast-year-text'),
                    
                    ],
                    style = {'vertical-align': 'top', "width": '97%', 'height': '6vh'},),
                    html.Div(
                    [
                        dcc.Slider(min=0, max=1, step = 1, value=0, tooltip={"placement": "right", "always_visible": True}, id='forecast-year'),
                    ],                    
                    style = {'vertical-align': 'top', "width": '97%', 'height': '6vh', 'vertical-align': 'middle', 'text-align': 'center'},),
                    html.Div(
                    [
                        html.Div('Forecast Month: ', id = 'forecast-month-text'),
                    
                    ],
                    style = {'vertical-align': 'top', "width": '97%', 'height': '6vh'},),
                    html.Div(
                    [
                        dcc.Slider(min=1, max=12, step = 1, value=1, tooltip={"placement": "right", "always_visible": True}, id='forecast-month'),
                    ],                    
                    style = {"width": '97%', 'height': '6vh', 'vertical-align': 'middle', 'text-align': 'center'},),
                ],
                style = {"display": 'inline-block', 'vertical-align': 'top', "width": '20%', 'height': '98vh'},
)

space_filler = html.Div([], style = {"display": 'inline-block', 'vertical-align': 'top', "width": '3%', 'height': '98vh'})
default_map_children = [
    dl.TileLayer(),
    dl.Pane([dl.GeoJSON(options={"style":{"color":"forestgreen"}}, 
                       id='background-basins', 
                       children = [dl.Popup(id = 'background-popup', maxHeight = 400, 
                                            maxWidth = 650, minWidth = 100, 
                                            offset = {'x':-10, 'y':-10}),])],
             style={"z-index": 1001}, name = 'P1'),
    dl.Pane([dl.GeoJSON(options={"style":{"color":"steelblue"}}, 
                       id='background-rivers')], 
             style={"z-index": 1002}, name = 'P2'),
    dl.Pane([dl.GeoJSON(options={"style":{"color":"crimson"}}, 
                        id='map-basins', 
                        children = [dl.Popup(id = 'basin-popup', maxHeight = 400, 
                                             maxWidth = 650, minWidth = 100, 
                                             offset = {'x':-10, 'y':-10}),])],
             style={"z-index": 1003}, name = 'P3'),
    dl.Pane([dl.GeoJSON(options={"style":{"color":"black"}}, id='map-forecast-points', 
                        children = [dl.Popup(id = 'gage-popup', maxHeight = 400, 
                                             maxWidth = 650, minWidth = 100, 
                                             offset = {'x':-10, 'y':-10}),])],
             style={"z-index": 1004}, name = 'P4'),
]

map_input_results_tab = html.Div(
    [
        html.H2('CAMELS-CRB basins'),
        dl.Map(
            id='leaflet-map',
            style={'width': '95%', 'height': '80vh'},
            center=[lon1, lat1],
            zoom=5.5,
            children=default_map_children
        )
    ],
    style = {"display": 'inline-block', "width": '75%', 'height': '98vh'},
)

app.layout = html.Div([input_details, space_filler, map_input_results_tab])

@app.callback(
    Output('feature-type', 'value'),
    Output('feature-type', 'options'),
    Input('forecast-type', 'value'),
    State('map-type', 'value')
    
)
def set_feature_types(forecast_location, basin_use):
  return rfc_alts[basin_use]['features'][0], rfc_alts[basin_use]['features']

@app.callback(
    Output('forecast-year', 'value'), 
    Output('forecast-month', 'value'), 
    Output('forecast-year', 'min'), 
    Output('forecast-year', 'max'), 
    Output('forecast-year', 'marks'), 
    Input('forecast-type', 'value'),
    Input('feature-type', 'value'),
    State('map-type', 'value')
    
)
def set_forecast_year_slider(forecast_location, feature_plot, basin_use):
  if forecast_location == 'GJNC2':
    forecast_folder = 'GJLOC'
  else:
    forecast_folder = forecast_location
  folder_name = os.path.join('reforecasts', rfc_alts[basin_use]['rfc'], forecast_folder)
  folder_name_alt = os.path.join('forecasts', rfc_alts[basin_use]['rfc'], forecast_folder)
  min_year = 99999
  max_year = 0
  start_month = 1
  try:
    for f in os.scandir(folder_name):
      forecast_date = f.path.split('\\')[-1]
      forecast_date_vals = forecast_date[:-4].split('_')
      if int(forecast_date_vals[1]) < min_year:
        start_month = int(forecast_date_vals[2])
        start_year = int(forecast_date_vals[1])
      min_year = min(min_year, int(forecast_date_vals[1]))
      max_year = max(max_year, int(forecast_date_vals[1]))
  except:
    pass
  try:    
    for f in os.scandir(folder_name_alt):
      forecast_date = f.path.split('\\')[-1]
      forecast_date_vals = forecast_date[:-4].split('_')
      if int(forecast_date_vals[1]) < min_year:
        start_month = int(forecast_date_vals[2])
        start_year = int(forecast_date_vals[1])
      min_year = min(min_year, int(forecast_date_vals[1]))
      max_year = max(max_year, int(forecast_date_vals[1]))
  except:
    pass

  return start_year, start_month, min_year, max_year, {min_year: {'label': str(min_year)}, max_year: {'label': str(max_year)}}
@app.callback(
    Output('background-popup', 'children'), 
    Input('background-basins', 'n_clicks'),
    State('background-basins', 'clickData'),
    State('background-popup', 'children')    
)
def create_feature_popups(click_count, click_data, popup_old):
  if click_data:
    if 'properties' in click_data:
      if 'NAME' in click_data['properties']:
        return click_data['properties']['NAME']
  return {}
@app.callback(
    Output('basin-popup', 'children'), 
    Input('map-basins', 'n_clicks'),
    State('map-basins', 'clickData'),
    State('basin-popup', 'children')    
)
def create_feature_popups(click_count, click_data, popup_old):
  if click_data:
    if 'properties' in click_data:
      if 'NAME' in click_data['properties']:
        return click_data['properties']['NAME']
  return {}
@app.callback(
    Output('gage-popup', 'children'), 
    Input('map-forecast-points', 'n_clicks'),
    Input('forecast-year', 'value'), 
    Input('forecast-month', 'value'), 
    State('feature-type', 'value'),
    State('forecast-type', 'value'),
    State('map-type', 'value')
    
)
def create_popup_plot(click_feature, forecast_year, forecast_month, feature_plot, forecast_location, basin_use):
  print(click_feature)
  if click_feature is None:
      return None
  
  folder_name = os.path.join(feature_plot, rfc_alts[basin_use]['rfc'], forecast_location)
  forecast_filename = feature_plot[:-1] + '_' + str(forecast_year) + '_' + str(forecast_month).zfill(2) + '.csv'
  try:
    all_forecasts = pd.read_csv(os.path.join(folder_name, forecast_filename), index_col = 0)
  except:
    return html.P(['Selected dates are', html.Br(), 'out of forecast range'], style={'textAlign': 'center'})
  all_forecasts.index = pd.to_datetime(all_forecasts.index)
  if rfc_alts[basin_use]['rfc'] == 'CBRFC':
    fig = sbplt.make_forecast_figure_CBRFC(all_forecasts)
  elif rfc_alts[basin_use]['rfc'] == 'CNRFC':
    fig = sbplt.make_forecast_figure_CNRFC(all_forecasts)
  # Create a figure. Or an image. Or anything else :)
  return dcc.Graph(figure=fig)

@app.callback(
    Output('forecast-type', 'options'),
    Output('forecast-type', 'value'),
    Input('map-type', 'value')
)
def update_forecast_stations(basin_use):
  return forecast_list[rfc_alts[basin_use]['rfc']], forecast_list[rfc_alts[basin_use]['rfc']][0]
  
@app.callback(
    Output('map-forecast-points', 'data'),
    Input('forecast-type', 'value'),
    State('map-type', 'value')
)
def update_forecast_locations(forecast_location, basin_use):
  file_name = rfc_alts[basin_use]['rfc']
  basin_gdf = br.make_gage_data(file_name)
  if forecast_location == 'All':
    return basin_gdf.__geo_interface__
  else:
    new_shapefile = br.clip_gage_data(forecast_location, basin_gdf)
    return new_shapefile.__geo_interface__
  
  
@app.callback(
    Output('background-basins', 'data'),
    Input('map-type', 'value')
)
def update_basin_background(basin_use):
  file_name = rfc_alts[basin_use]['rfc']
#  file_path = os.path.join('basin_data', 'rf12ja05', 'rf12ja05.shp')
  file_path = os.path.join('basin_data', file_name + '_Basins', 'b_' + file_name.lower() + '.shp')
  basin_gdf = gpd.read_file(file_path)
  basin_gdf = basin_gdf.to_crs(crs=4326)
#  this_basin = basin_gdf[basin_gdf['BASIN_ID'] == file_name]
  return basin_gdf.__geo_interface__
  

@app.callback(
    Output('background-rivers', 'data'),
    Input('map-type', 'value')
)
def update_river_background(basin_use):
  new_rivers = gpd.read_file('basin_data/' + rfc_alts[basin_use]['rfc'] +  '_Rivers/rivs_' + rfc_alts[basin_use]['rfc'].lower() + '.shp')
  new_rivers = new_rivers.to_crs(crs=4326)
  return new_rivers.__geo_interface__

@app.callback(
    Output('map-basins', 'data'),
    Input('forecast-type', 'value'),
    State('map-type', 'value')
)
def update_estimates(forecast_loc, basin_use):
  file_name = rfc_alts[basin_use]['rfc']
  file_path = os.path.join('basin_data', file_name + '_Basins', 'b_' + file_name.lower() + '.shp')
  basin_gdf = gpd.read_file(file_path)
  basin_gdf = basin_gdf.to_crs(crs=4326)
  json_file_path = os.path.join('basin_data', file_name + '_upstream_network.json')
  with open(json_file_path) as f_in:
    full_upstream_record = json.load(f_in)
    
#  if file_name == 'CNRFC':
#    full_upstream_record_int = {}
#    for station in full_upstream_record:
#      if station[:-3] not in full_upstream_record_int:
#        full_upstream_record_int[station[:-3]] = []
#      for up_loc in full_upstream_record[station]:
#        if up_loc[:-3] not in full_upstream_record_int[station[:-3]]:
#          full_upstream_record_int[station[:-3]].append(up_loc[:-3])
#    full_upstream_record = {}
#    for station in full_upstream_record_int:
#      full_upstream_record[station] = []
#      for up_loc in full_upstream_record_int[station]:
#        full_upstream_record[station].append(up_loc)

#  if file_name == 'NWRFC':
#    full_upstream_record_int = {}
#    for station in full_upstream_record:
#      if station[:5] not in full_upstream_record_int:
#        full_upstream_record_int[station[:5]] = []
#      for up_loc in full_upstream_record[station]:
#        if up_loc[:5] not in full_upstream_record_int[station[:5]]:
#          full_upstream_record_int[station[:5]].append(up_loc[:5])
#    full_upstream_record = {}
#    for station in full_upstream_record_int:
#      full_upstream_record[station] = []
#      for up_loc in full_upstream_record_int[station]:
#        full_upstream_record[station].append(up_loc)

#  if file_name == 'MBRFC':
#    full_upstream_record_int = {}
#    for station in full_upstream_record:
#      if len(station) > 5:
#        if station[:5] not in full_upstream_record_int:
#          full_upstream_record_int[station[:5]] = []
#        for up_loc in full_upstream_record[station]:
#          if len(up_loc) > 5:
#            if up_loc[:5] not in full_upstream_record_int[station[:5]]:
#              full_upstream_record_int[station[:5]].append(up_loc[:5])
#          else:
#            if up_loc not in full_upstream_record_int[station[:5]]:
#              full_upstream_record_int[station[:5]].append(up_loc)          
#      else:
#        if station not in full_upstream_record_int:
#          full_upstream_record_int[station] = []
#        for up_loc in full_upstream_record[station]:
#          if len(up_loc) > 5:
#            if up_loc[:5] not in full_upstream_record_int[station]:
#              full_upstream_record_int[station].append(up_loc[:5])
#          else:
#            if up_loc not in full_upstream_record_int[station]:
#              full_upstream_record_int[station].append(up_loc)          
      
#    full_upstream_record = {}
#    for station in full_upstream_record_int:
#      full_upstream_record[station] = []
#      for up_loc in full_upstream_record_int[station]:
#        full_upstream_record[station].append(up_loc)

       
  all_upstream_gdf = gpd.GeoDataFrame()
  if forecast_loc == 'All':
    return all_upstream_gdf.__geo_interface__    
  points_gdf = br.make_gage_data(file_name)
  this_loc = points_gdf[points_gdf.index == forecast_loc]
  buffered_loc = gpd.GeoDataFrame(this_loc, crs = this_loc.crs, geometry = this_loc.geometry.buffer(0.01))
  print(buffered_loc)
  print(basin_gdf)
  current_subbasin = gpd.sjoin(basin_gdf, buffered_loc, how = 'inner', predicate = 'intersects')
  for col_nm in current_subbasin.columns:
    print(current_subbasin[col_nm])
  basin_id_label = rfc_alts[basin_use]['basin_id_label']
  tie_vals = False
  if len(current_subbasin.index) > 1:
    max_upstream = 0
    print(current_subbasin)
    for index, row in current_subbasin.iterrows():
      if row[basin_id_label] == forecast_loc or forecast_loc in row[basin_id_label]:
        current_subbasin = current_subbasin[current_subbasin.index == index]
        basin_loc = current_subbasin.loc[current_subbasin.index[0], basin_id_label]
        break
  if len(current_subbasin.index) > 1:
    for index, row in current_subbasin.iterrows():
      basin_loc1 = current_subbasin.loc[index, basin_id_label]
      basin_counter = 0
      for index2, row2 in current_subbasin.iterrows():
        basin_loc2 = current_subbasin.loc[index2, basin_id_label]
        if basin_loc1 in full_upstream_record[basin_loc2] or basin_loc1 == basin_loc2:
          basin_counter += 1
        print(index, end = " ")
        print(index2, end = " ")
        print(basin_loc1, end = " ")
        print(basin_loc2, end = " ")
        print(basin_counter, end = " ")
        print(max_upstream, end = " ")
        print(tie_vals)
      if basin_counter > max_upstream:
        basin_loc = current_subbasin.loc[index, basin_id_label]
        max_upstream = basin_counter * 1
        tie_vals = False
        print(basin_loc, end = " ")
        print(max_upstream, end = " ")
        print(tie_vals)
      elif basin_counter == max_upstream:
        tie_vals = True
    if tie_vals:   
      current_subbasin = gpd.sjoin(basin_gdf, this_loc, how = 'inner', predicate = 'intersects')
      basin_loc = current_subbasin.loc[current_subbasin.index[0], basin_id_label]
  else:
    basin_loc = current_subbasin.loc[current_subbasin.index[0], basin_id_label]
        
          
         
  print(current_subbasin)
  print(basin_id_label)
  print(basin_loc)
  if basin_loc in full_upstream_record:
    for index in basin_gdf.index:
      this_basin_id = basin_gdf.loc[index,basin_id_label]
      if this_basin_id in full_upstream_record[basin_loc] or this_basin_id == basin_loc:
        all_upstream_gdf = pd.concat([all_upstream_gdf, basin_gdf[basin_gdf.index == index]])
    all_upstream_gdf = gpd.GeoDataFrame(all_upstream_gdf, crs = basin_gdf.crs, geometry = all_upstream_gdf['geometry'])      
  return all_upstream_gdf.__geo_interface__
  
             
        
if __name__ == '__main__':
    app.run_server(debug=False)

