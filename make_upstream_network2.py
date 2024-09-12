import os
import numpy as np
import pandas as pd 
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import Point, LineString, buffer
import json
import copy
import basin_reader as br
# basin/river data from: https://www.nohrsc.noaa.gov/gisdatasets/
# loop through data from each of the 6 western RFC:
# California-Nevada
# Northwest
# Colorado Basin
# Arkansas-Red
# Missouri Basin
# West Gulf
#basin_list = ['CBRFC', 'CNRFC', 'NWRFC', 'ABRFC', 'MBRFC', 'WGRFC']
#id_category = ['NAME_left', 'NAME_left', 'CH5_ID', 'NAME_left', 'NAME_left', 'NAME_left']
basin_list = ['CNRFC', 'NWRFC', 'ABRFC', 'MBRFC', 'WGRFC']
id_category = ['ID', 'CH5_ID', 'NAME', 'NAME', 'NAME']
downstream_key = 'DOWN_REACH'
# loop through RFCs
for basin, id_col_nm in zip(basin_list, id_category):
  # upstream_key is a dictionary of lists, each string in the list
  # is the id of every sub-basins directly (i.e., neighboring) upstream
  # of the sub-basins id used as the key
  upstream_key = {}
  # full_upstream_record is a dictionary of lists, each string in the list
  # is the id of all sub-basins upstream (i.e., not just direct neighbors)
  # of the sub-basins id used as the key
  full_upstream_record = {}

  new_gages = br.make_gage_data(basin)
  print(new_gages)
  print(new_gages.crs)
  print(new_gages)
  # shapefile of the watershed area and channel locations for all sub-basins in each RFC
  new_basins = gpd.read_file('basin_data/' + basin +  '_Basins/b_' + basin.lower() + '.shp')
  print(new_basins.crs)
  #new_basins = new_basins.to_crs(crs=4326)
  new_rivers = gpd.read_file('basin_data/' + basin +  '_Rivers/rivs_' + basin.lower() + '.shp')
  print(new_rivers.crs)
  #new_rivers = new_rivers.to_crs(crs=4326)
  print(new_rivers.crs)
  op_water_int = new_rivers[pd.notna(new_rivers['OPEN_WAT_1'])]
  op_water = op_water_int[op_water_int['OPEN_WAT_1'] != '0']
  
  # loop through each segment of the channel network
  exception_list = []
  no_downstream_list = []
  basin_key = 'SREC1LLF'
  upstream_dict = {}
  for index, row in new_gages.iterrows():
    if index not in upstream_dict:
      upstream_dict[index] = []
    # find current channel segment
    this_loc = new_gages[new_gages.index == index]
    this_basin = gpd.GeoDataFrame(this_loc, crs = this_loc.crs, geometry = this_loc.geometry.buffer(0.01))
    this_segment = gpd.sjoin(new_rivers, this_basin, how  = 'inner', op = 'intersects')
    counter = 1
    while len(this_segment.index) == 0:
      this_basin = gpd.GeoDataFrame(this_loc, crs = this_loc.crs, geometry = this_loc.geometry.buffer(0.01 + 0.005 * float(counter)))
      this_segment = gpd.sjoin(new_rivers, this_basin, how  = 'inner', op = 'intersects')
      counter += 1
    print(index, end = " ")
    
    # find basins holding the current & downstream segments of the channel
    all_upstream_segments = pd.DataFrame()
    print(len(this_segment.index))
    this_segment = br.strip_joined_gdf(this_segment)
    segment_id_list = br.find_all_downstream(this_segment, 'RR')
    tot_len = 0
    while len(segment_id_list) > tot_len:
      tot_len = len(segment_id_list)
      for sid in segment_id_list:
        upstream_segments = new_rivers[new_rivers['DOWN_REACH'] == str(sid)]
        new_ids = upstream_segments['RR'].unique()
        for nid in new_ids:
          if nid not in segment_id_list:
            segment_id_list.append(nid)
        all_upstream_segments = pd.concat([all_upstream_segments, upstream_segments])
    all_upstream_segments = gpd.GeoDataFrame(all_upstream_segments, crs = new_rivers.crs, geometry = all_upstream_segments['geometry'])
    all_upstream_basins = pd.DataFrame()
    for index_us, row_us in all_upstream_segments.iterrows():
      this_us_segment = all_upstream_segments[all_upstream_segments.index == index_us]
      upstream_basin = gpd.sjoin(new_basins, this_us_segment, how = 'inner', op = 'intersects')
      upstream_basin = br.strip_joined_gdf(upstream_basin)
      upstream_basin_int = br.select_on_size(upstream_basin, this_us_segment, 'xxx', 'NAME')
      for index_ub, row_ub in upstream_basin_int.iterrows():
        upstream_id = row_ub['NAME_left']
        if upstream_id not in upstream_dict[index]:
          upstream_dict[index].append(upstream_id)
          all_upstream_basins = pd.concat([all_upstream_basins, upstream_basin_int[upstream_basin_int.index == index]])
    all_upstream_basin = br.strip_joined_gdf(all_upstream_basin)
    all_upstream_basin = gpd.GeoDataFrame(all_upstream_basin, crs = new_basins.crs, geometry = all_usptream_basin['geometry'])
    all_lakes = gpd.sjoin(    
  # write dictionaries to json
  filename_write = 'basin_data/' + basin +  '_upstream_network2.json'
  with open(filename_write, "w") as fp:
    json.dump(upstream_dict , fp)
  fp.close()    
