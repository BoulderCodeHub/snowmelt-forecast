basins = gpd.read_file('BasinSummary/BasinSummary.shp')
outletPoints = gpd.read_file('OutletPoints/OutletPoints.shp')
geom_list = []
name_list = []
index_list = []
id_list = []
for index, row in outletPoints.iterrows():
  if row['geometry'].x > 0:
    geom_list.append(row['geometry'].buffer(5000))
    name_list.append(row['Location'])
    id_list.append(row['Id'])
    index_list.append(index)

basin_outline = basins.dissolve()
new_outlet = pd.DataFrame(index = index_list)
new_outlet['Location'] = name_list
new_outlet['ID'] = id_list
new_outlet_points = gpd.GeoDataFrame(new_outlet, columns = ['Location', 'ID'], geometry = geom_list, crs = outletPoints.crs)
fig, ax = plt.subplots()
basins.plot(ax = ax)
new_outlet_points.plot(ax = ax, color = 'red')
plt.show()
upstream_key = {}
for index, row in new_outlet_points.iterrows():
  this_outlet = new_outlet_points[new_outlet_points.index == index]
  watersheds_int = gpd.sjoin(basins, this_outlet, how = 'inner', predicate = 'intersects')
  if len(watersheds_int.index) == 2:
    upstream_name = ''
    downstream_name = ''
    for index_basin, row_basin in watersheds_int.iterrows():
      print(row_basin)
      if int(row['ID']) != int(row_basin['ID_left']):
        downstream_name += row_basin['NAME']
      else:      
        upstream_name += row_basin['NAME']
    if len(upstream_name) > 0 and len(downstream_name) > 0:
      upstream_key[downstream_name] = ''
      upstream_key[downstream_name] += upstream_name
  else:
    print(watersheds_int)
    print(this_outlet)
    fig, ax = plt.subplots()
    basin_outline.plot(ax = ax, facecolor = 'beige', edgecolor = 'black', linewidth = 4.0)
    watersheds_int.plot(ax = ax)
    this_outlet.plot(ax = ax, color = 'red', edgecolor = 'red', linewidth = 10.0)
    plt.show()
    plt.close()
  
print(upstream_key)
for index, row in new_outlet_points.iterrows():
  this_outlet = new_outlet_points[new_outlet_points.index == index]
  watersheds_int = gpd.sjoin(basins, this_outlet, how = 'inner', predicate = 'intersects')
  all_upstream_name = []
  all_upstream_id = []
  all_upstream_index = []
  all_upstream_geom = []
  
  for index_basin, row_basin in watersheds_int.iterrows():
    if int(row['ID']) == int(row_basin['ID_left']):
      upstream_gdf = basins[basins['NAME'] == row_basin['NAME']]
      upstream_toggle = True
      downstream_loc = ''
      downstream_loc += row_basin['NAME']
      while upstream_toggle:
        try:
          upstream_loc = upstream_key[downstream_loc]
          this_basin = basins[basins['NAME'] == upstream_loc]
          upstream_gdf = pd.concat([upstream_gdf, this_basin])
          downstream_loc = ''
          downstream_loc += upstream_loc
        except:
          upstream_toggle = False        
      upstream_gdf = gpd.GeoDataFrame(upstream_gdf, crs = basins.crs, geometry = upstream_gdf['geometry'])
      upstream_all = upstream_gdf.dissolve()
       
      print(upstream_gdf)
      print(this_outlet)
      fig, ax = plt.subplots()
      basin_outline.plot(ax = ax, facecolor = 'beige', edgecolor = 'black', linewidth = 4.0)
      upstream_all.plot(ax = ax)
      this_outlet.plot(ax = ax, color = 'red', edgecolor = 'red', linewidth = 10.0)
      plt.show()
      plt.close()
