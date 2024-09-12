import os
import pandas as pd
import geopandas as gpd
basin_filename = os.path.join('basin_data', 'CBRFC_Basins', 'CBRFC_Basins.shp')
basin_gdf = gpd.read_file(basin_filename)
x_loc = []
y_loc = []
id_name = []
for index, row in basin_gdf.iterrows():
  id_name.append(row['ch5_id'])
  x_loc.append(row['x_outlet'])
  y_loc.append(row['y_outlet'])
print(y_loc)
gage_ids = pd.DataFrame()
gage_ids['ID'] = id_name
gage_ids['Latitude'] = x_loc
gage_ids['Longitude'] = y_loc
gage_ids.to_csv('basin_data/CBRFC_Basins/gage_ids.csv')

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
