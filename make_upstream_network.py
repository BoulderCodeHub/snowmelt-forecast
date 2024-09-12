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
basin_list = ['CBRFC', 'CNRFC', 'NWRFC', 'ABRFC', 'MBRFC', 'WGRFC']
id_category = ['NAME', 'NAME', 'NAME', 'NAME', 'NAME', 'NAME']
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
  for index, row in new_basins.iterrows():
    # find current channel segment
    this_basin = new_basins[new_basins.index == index]
    print(basin, end = " ")
    print(this_basin[id_col_nm].iloc[0], end = " ")
    print(index)
    
    # find basins holding the current & downstream segments of the channel
    this_segment = gpd.sjoin(new_rivers, this_basin, how  = 'inner', op = 'intersects')
    this_segment = br.strip_joined_gdf(this_segment)
    
    this_segment_unique = br.filter_unique_downstream(new_basins, new_rivers, this_segment, this_basin[id_col_nm].iloc[0], downstream_key, id_col_nm)
      
    if len(this_segment_unique.index) > 0:
      if len(this_segment_unique.index) > 1:
        this_segment_unique = br.select_on_size_segment(this_basin, this_segment_unique)
        downstream_id_list = br.find_all_downstream(this_segment_unique, downstream_key)
        if this_basin[id_col_nm].iloc[0] == basin_key:
          print(this_segment_unique[downstream_key])
          fig, ax = plt.subplots()
          if len(this_segment_unique.index) > 0:
            this_segment_unique.plot(ax = ax, color = 'green')
          this_basin.plot(ax = ax, facecolor = 'red', alpha = 0.2)
          plt.show()
          plt.close()
      else:
        downstream_id_list = [this_segment_unique.loc[this_segment_unique.index[0], downstream_key],]
        
      downstream_segment_all = pd.DataFrame()
      downstream_op_all = pd.DataFrame()
      for did in downstream_id_list:
        if did != '0':
          downstream_segment_int = new_rivers[new_rivers['RR'] == str(did)]
          if this_basin[id_col_nm].iloc[0] == basin_key:
            print(did, end = " ")
            print(downstream_id_list)
            fig, ax = plt.subplots()
            this_segment_unique.plot(ax = ax, color = 'green')
            this_basin.plot(ax = ax, facecolor = 'red', alpha = 0.2)
            if len(downstream_segment_int.index) > 0:
              downstream_segment_int.plot(ax = ax, color = 'blue')
            plt.show()
            plt.close()
          if len(downstream_segment_int.index) > 0:
            downstream_basin = gpd.sjoin(new_basins, downstream_segment_int, how = 'inner', op = 'intersects')
            downstream_basin = br.strip_joined_gdf(downstream_basin)
            downstream_basin_list_int = br.find_only_downstream_basin(downstream_basin, this_basin[id_col_nm].iloc[0], id_col_nm + '_left')
            if len(downstream_basin_list_int) > 0:
              downstream_segment_all = pd.concat([downstream_segment_all, downstream_segment_int])
          if len(downstream_segment_int.index) == 0:
            all_streams_to_lake = new_rivers[new_rivers[downstream_key] == str(did)]
            basins_to_lake = gpd.sjoin(new_basins, all_streams_to_lake, how = 'inner', op = 'intersects')
            basins_to_lake = br.strip_joined_gdf(basins_to_lake)
            basins_to_lake_no_dups = br.select_on_size(basins_to_lake, all_streams_to_lake, 'xxx', id_col_nm)
            downstream_segment_int = gpd.sjoin(op_water, basins_to_lake_no_dups, how = 'inner', op = 'intersects')
            downstream_segment_int = br.strip_joined_gdf(downstream_segment_int, type_strip = 'all', keys_leave = [downstream_key,])
            if len(downstream_segment_int.index) > 0:
              if len(downstream_segment_int.index) > 1:              
                downstream_segment_int = br.select_on_size_segment(this_basin, downstream_segment_int)
              for idx2 in range(0, len(downstream_segment_int.index)):
                downstream_id = br.join_select_no_duplicate(downstream_segment_int, downstream_segment_int.index[idx2], downstream_key)
                downstream_segment_all = pd.concat([downstream_segment_all, new_rivers[new_rivers['RR'] == str(downstream_id)]])                          
            downstream_op_all = pd.concat([downstream_op_all, downstream_segment_int])
        
      downstream_basin_all = pd.DataFrame()
      if len(downstream_segment_all.index) > 0:
        downstream_segment_all = gpd.GeoDataFrame(downstream_segment_all, crs = new_rivers.crs, geometry = downstream_segment_all['geometry'])
        downstream_basin = gpd.sjoin(new_basins, downstream_segment_all, how = 'inner', op = 'intersects')
        downstream_basin = br.strip_joined_gdf(downstream_basin)
        downstream_basin_all = br.select_on_size(downstream_basin, downstream_segment_all, this_basin[id_col_nm].iloc[0], id_col_nm)
      downstream_op_basins_all = pd.DataFrame()
      if len(downstream_op_all.index) > 0:
        downstream_op_all = gpd.GeoDataFrame(downstream_op_all, crs = new_rivers.crs, geometry = downstream_op_all['geometry'])
        downstream_basin = gpd.sjoin(new_basins, downstream_op_all, how = 'inner', op = 'intersects')
        downstream_basin = br.strip_joined_gdf(downstream_basin)
        downstream_op_basins_all = br.select_on_size(downstream_basin, downstream_op_all, this_basin[id_col_nm].iloc[0], id_col_nm)

      if this_basin[id_col_nm].iloc[0] == basin_key:
        print(downstream_basin)
        print(downstream_segment_all)
      if this_basin[id_col_nm].iloc[0] == basin_key:
        fig, ax = plt.subplots()
        if len(downstream_segment_all.index) > 0:
          downstream_segment_all.plot(ax = ax, color = 'green')
        if len(downstream_op_all.index) > 0:
          downstream_op_all.plot(ax = ax, color = 'blue')
        this_basin.plot(ax = ax, facecolor = 'red', alpha = 0.2)
        if len(downstream_basin_all.index) > 0:
          downstream_basin_all.plot(ax = ax, facecolor = 'orange', alpha = 0.2)
        if len(downstream_op_basins_all.index) > 0:
          downstream_op_basins_all.plot(ax = ax, facecolor = 'yellow', alpha = 0.4)
        plt.show()
        plt.close()
        
      
      all_downstream_list = []
      for index_d, row_d in downstream_basin_all.iterrows():
        try:
          downstream_id_name = row_d[id_col_nm]
        except:
          downstream_id_name = row_d[id_col_nm + '_left']
        if downstream_id_name not in all_downstream_list:
          all_downstream_list.append(downstream_id_name)
          if this_basin[id_col_nm].iloc[0] == basin_key:
            print('1', end = " ")
            print(downstream_id_name)
      for index_d, row_d in downstream_op_basins_all.iterrows():
        try:
          downstream_id_name = row_d[id_col_nm]
        except:
          downstream_id_name = row_d[id_col_nm + '_left']
        if downstream_id_name not in all_downstream_list:
          all_downstream_list.append(downstream_id_name)
          if this_basin[id_col_nm].iloc[0] == basin_key:
            print('1.5', end = " ")
            print(downstream_id_name)
          
      joined_basins = gpd.sjoin(new_basins, this_segment, how = 'inner', op = 'intersects')
      joined_basins = br.strip_joined_gdf(joined_basins)
      joined_basins_downstream = br.split_dual_basins(joined_basins, id_col_nm, this_basin[id_col_nm].iloc[0])
      for index_j, row_j in joined_basins_downstream.iterrows():
        try:
          downstream_id_name = row_j[id_col_nm]
        except:
          downstream_id_name = row_j[id_col_nm + '_left']
        if downstream_id_name not in all_downstream_list:
          all_downstream_list.append(downstream_id_name)
          if this_basin[id_col_nm].iloc[0] == basin_key:
            print('2', end = " ")
            print(downstream_id_name)
      if len(all_downstream_list) == 0:
        joined_basins = gpd.sjoin(new_basins, this_segment, how = 'inner', op = 'intersects')
        joined_basins = br.strip_joined_gdf(joined_basins)
        joined_basins = br.select_on_size(joined_basins, this_segment, this_basin[id_col_nm].iloc[0], id_col_nm)
        for index_j, row_j in joined_basins.iterrows():
          try:
            downstream_id_name = row_j[id_col_nm]
          except:
            downstream_id_name = row_j[id_col_nm + '_left']
          if downstream_id_name not in all_downstream_list and downstream_id_name != this_basin[id_col_nm].iloc[0]:
            all_downstream_list.append(downstream_id_name)
            if this_basin[id_col_nm].iloc[0] == basin_key:
              print('3', end = " ")
              print(downstream_id_name)
                
      for upstream_basin_idx in this_basin.index:
        # get upstream id
        upstream_name = this_basin.loc[upstream_basin_idx, id_col_nm]
        for downstream_name in all_downstream_list:
          if this_basin[id_col_nm].iloc[0] == basin_key:
            print(upstream_name, end = " ")
            print(downstream_name)
          if downstream_name in upstream_key:
            if upstream_name not in upstream_key[downstream_name]:
              upstream_key[downstream_name].append(upstream_name)
          else:
            upstream_key[downstream_name] = [upstream_name,] 
  # loop through the dictionary of upstream/downstream neighbors
  # to make a dictionary of all upstream sub-basins for each sub-basin
  for index in new_basins.index:
    all_upstream = []
    # get id for current sub-basin
    basin_name = new_basins.loc[index, id_col_nm]    
    # find all direct upstream basins for that basin id
    len_upstream = 0    
    if basin_name in upstream_key:
      for upstream_basin in upstream_key[basin_name]:
        if upstream_basin not in all_upstream:
          all_upstream.append(upstream_basin)
    # find all basins upstream of the direct upstream basins
    while len_upstream < len(all_upstream):  
      len_upstream = len(all_upstream)    
      all_upstream_int = []
      # find all upstream basins for everything
      # in the 'upstream list'
      # if no new upstream basins are discovered
      # the search ends
      for downstream_basin in all_upstream:
        if downstream_basin in upstream_key:
          for upstream_basin in upstream_key[downstream_basin]:
            all_upstream_int.append(upstream_basin)
      # add new upstream basins to upstream list
      for upstream_basin in all_upstream_int:
        if upstream_basin not in all_upstream:
          all_upstream.append(upstream_basin)
    full_upstream_record[basin_name] = all_upstream
  # write dictionaries to json
  filename_write = 'basin_data/' + basin +  '_upstream_network.json'
  with open(filename_write, "w") as fp:
    json.dump(full_upstream_record , fp)
  fp.close()    
