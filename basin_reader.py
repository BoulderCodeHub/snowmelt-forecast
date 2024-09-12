import pandas as pd
import numpy as np
import os
from shapely import Point, LineString, buffer
from shapely.geometry import shape, mapping
import geopandas as gpd
import matplotlib.pyplot as plt
def make_gage_data(file_name, crs_use = 4326, id_row = 'ID', lat_row = 'Latitude', long_row = 'Longitude'):
  basin_key = pd.read_csv(os.path.join('basin_data', file_name + '_Basins', 'gage_ids.csv'), index_col = 0)
  if id_row not in basin_key.columns:
    basin_key = pd.read_csv(os.path.join('basin_data', file_name + '_Basins', 'gage_ids.csv'))
    
  geom_list = []
  for index, row in basin_key.iterrows():
    if float(row[lat_row]) < 0 and float(row[long_row]) > 0:
      geom_list.append(Point(row[lat_row], row[long_row]))
    elif float(row[lat_row]) > 0 and float(row[long_row]) < 0:
      geom_list.append(Point(row[lat_row] * (-1.0), row[long_row] * (-1.0)))
    elif float(row[lat_row]) > 0:
      geom_list.append(Point(row[lat_row] * (-1.0), row[long_row]))
    elif float(row[long_row]) < 0:
      geom_list.append(Point(row[lat_row], row[long_row] * (-1.0)))
  basin_gdf = gpd.GeoDataFrame(index = basin_key[id_row], geometry = geom_list)
  basin_gdf.set_crs(epsg=crs_use, inplace=True)
  
  return basin_gdf

def clip_gage_data(forecast_loc, basin_gdf):
  new_shapefile = gpd.GeoDataFrame()
  geom_list = []
  this_loc = basin_gdf[basin_gdf.index == forecast_loc]
  if len(this_loc.index) > 0:
    new_shapefile = pd.concat([new_shapefile, this_loc], axis = 0)
  new_shapefile = gpd.GeoDataFrame(new_shapefile, crs = basin_gdf.crs, geometry = new_shapefile.geometry)
  return new_shapefile
  
def strip_joined_gdf(gdf_use, type_strip = 'index', keys_leave = []):
  if type_strip == 'index':
    try:
      gdf_use = gdf_use.drop(['index_right',], axis=1)
    except:
      pass
    try:
      gdf_use = gdf_use.drop(['index_left',], axis=1)
    except:
      pass
  elif type_strip == 'all':
    for col_nm in gdf_use.columns:
      if '_right' in col_nm or '_left' in col_nm:
        reg_name = col_nm.strip('_right').strip('_left')
        delete_name = True
        for keep_name in keys_leave:
          if reg_name == keep_name:
            delete_name = False
        if delete_name:
          gdf_use = gdf_use.drop([col_nm,], axis = 1)      
  return gdf_use

def join_select_no_duplicate(df_use, index_use, key_use):
  try:
    selected_value = df_use.loc[index_use, key_use]
  except:
    selected_value = df_use.loc[index_use, key_use + '_left']
  try:
    selected_value = selected_value.iloc[0]
  except:
    pass
  return selected_value
  
def select_on_size_segment(downstream_basin, downstream_segment):      
  line_lengths = np.zeros(len(downstream_segment.index))
  full_lengths = np.zeros(len(downstream_segment.index))
  num_segs = len(downstream_segment.index)
  min_length_contribution = 1.0 / float(num_segs * 2)
  min_length_in_basin = 0.5
  intersect_geom = downstream_basin['geometry'].iloc[0]
  for idx in range(0, len(line_lengths)):
    exception_count = False
    this_segment = downstream_segment[downstream_segment.index == downstream_segment.index[idx]]
    try:
      intersection = this_segment.intersection(intersect_geom)
      try:
        line_lengths[idx] = intersection.length.iloc[0]
        full_lengths[idx] = this_segment.length.iloc[0]
      except:
        pass
    except:
      exception_count = True
  downstream_segment_final = pd.DataFrame()
  for idx in range(0, len(line_lengths)):    
    if line_lengths[idx] / np.sum(line_lengths) > min_length_contribution or line_lengths[idx] / full_lengths[idx] > min_length_in_basin:
      downstream_segment_final = pd.concat([downstream_segment_final, downstream_segment[downstream_segment.index == downstream_segment.index[idx]]])
  return downstream_segment_final

def split_dual_basins(basins_use, id_col_nm, basin_key):
  new_basins = pd.DataFrame()
  if len(basin_key) == 8:
    basin_start = basin_key[:5]
    basin_end = basin_key[-3:]
    for index, row in basins_use.iterrows():
      if len(row[id_col_nm]) == 8:
        joined_start = row[id_col_nm][:5]
        joined_end = row[id_col_nm][-3:]
        if joined_start == basin_start:
          if basin_end == 'HUF' and joined_end == 'HLF':
            new_basins = pd.concat([new_basins, basins_use[basins_use.index == index]])
          elif basin_end == 'LUF' and joined_end == 'LLF':
            new_basins = pd.concat([new_basins, basins_use[basins_use.index == index]])
          elif basin_end == 'HOF' and joined_end == 'LOF':
            new_basins = pd.concat([new_basins, basins_use[basins_use.index == index]])
  return new_basins

def select_on_size(downstream_basin, downstream_segment, basin_key, id_col):
  downstream_basins_new = pd.DataFrame()
  for index, row in downstream_basin.iterrows():
    try:
      this_basin_name = row[id_col]
    except:
      this_basin_name = row[id_col + '_left']
    if len(basin_key) == 8 and len(this_basin_name) == 8:
      basin_start = basin_key[:5]
      basin_end = basin_key[-3:]
      joined_start = this_basin_name[:5]
      joined_end = this_basin_name[-3:]
    else:
      basin_start = 'a'
      basin_end = 'b'
      joined_start = 'c'
      joined_end = 'd'
      
    if this_basin_name != basin_key:
      if basin_start != joined_start:
        downstream_basins_new = pd.concat([downstream_basins_new, downstream_basin[downstream_basin.index == index]])
      else:
        if basin_end == 'LLF':
          if joined_end != 'LUF':
            downstream_basins_new = pd.concat([downstream_basins_new, downstream_basin[downstream_basin.index == index]])
        elif basin_end == 'HLF':
          if joined_end != 'HUF':
            downstream_basins_new = pd.concat([downstream_basins_new, downstream_basin[downstream_basin.index == index]])
        elif basin_end == 'LOF':
          if joined_end != 'HOF':
            downstream_basins_new = pd.concat([downstream_basins_new, downstream_basin[downstream_basin.index == index]])
        else:
          downstream_basins_new = pd.concat([downstream_basins_new, downstream_basin[downstream_basin.index == index]])
        
  if len(downstream_basins_new.index) > 1:
    downstream_basin_no_dups = downstream_basins_new[~downstream_basins_new.index.duplicated(keep='first')]
    line_lengths = np.zeros(len(downstream_basin_no_dups.index))
    full_lengths = np.zeros(len(downstream_basin_no_dups.index))
    for idx in range(0, len(line_lengths)):
      intersect_geom = downstream_basin_no_dups.loc[downstream_basin_no_dups.index[idx], 'geometry']
      exception_count = False     
      try:
        intersection = downstream_segment.intersection(intersect_geom)
        try:
          for idy in range(0, len(downstream_segment.index)):
            line_lengths[idx] += intersection.length.iloc[idy]
        except:
          pass
      except:
        exception_count = True
      
    downstream_basin_final = pd.DataFrame()
    for idx in range(0, len(line_lengths)):    
      if line_lengths[idx] / np.sum(line_lengths) > 0.1:
        downstream_basin_final = pd.concat([downstream_basin_final, downstream_basin_no_dups[downstream_basin_no_dups.index == downstream_basin_no_dups.index[idx]]])
    return downstream_basin_final
  else:
    return downstream_basins_new

def filter_unique_downstream(new_basins, new_rivers, this_segment, basin_id, downstream_key, id_col_nm):
  new_segments = pd.DataFrame()
  for index_use in this_segment.index:
    downstream_id = join_select_no_duplicate(this_segment, index_use, downstream_key)
    downstream_segment = new_rivers[new_rivers['RR'] == str(downstream_id)]
    downstream_basin = gpd.sjoin(new_basins, this_segment, how = 'inner', op = 'intersects')
    downstream_basin = strip_joined_gdf(downstream_basin)
    downstream_basin_list_int = find_only_downstream_basin(downstream_basin, basin_id, id_col_nm + '_left')
    if len(downstream_basin_list_int) > 0:
      new_segments = pd.concat([new_segments, this_segment[this_segment.index == index_use]], axis = 0)
  
  if len(new_segments.index) > 0:
    new_segments = gpd.GeoDataFrame(new_segments, crs = this_segment.crs, geometry = new_segments['geometry'])
    
  return new_segments
  
def find_only_downstream_basin(downstream_basin, current_basin, basin_id):
  basin_list = []
  for index, row in downstream_basin.iterrows():
    if row[basin_id] != current_basin:
      basin_list.append(row[basin_id])
  return basin_list

def find_all_downstream(this_segment, downstream_key):
  #line_lengths = np.zeros(len(this_segment.index))
  down_ids = []
  #intersect_geom = this_basin.loc[this_basin.index[0], 'geometry']
  for idx in range(0, len(this_segment.index)):
    #current_segment = this_segment[this_segment.index == this_segment.index[idx]]
    #try:
      #intersection = current_segment.intersection(intersect_geom)
      #line_lengths[idx] = intersection.length
    downstream_id = this_segment.loc[this_segment.index[idx], downstream_key]
    try:
      downstream_id = downstream_id.iloc[0]
    except:
      pass
    if downstream_id not in down_ids:
      down_ids.append(downstream_id)
    #except:
    #  down_ids.append('')

  #downstream_options = {}
  #tot_val = 0.0
  #for dwn_cnt, downst in enumerate(down_ids):
    #tot_val += line_lengths[dwn_cnt]
    #if downst in downstream_options:
      #downstream_options[downst] += line_lengths[dwn_cnt]
    #else:
      #downstream_options[downst] = line_lengths[dwn_cnt]
      
#  downstream_id_list = []
#  for downst in downstream_options:
#    if downstream_options[downst] / tot_val > 0.05:
#      downstream_id_list.append(downst)

  return down_ids