import pandas as pd
import requests
from xml.etree import ElementTree

url = 'https://www.cnrfc.noaa.gov/data/kml/ensPoints.xml'
response = requests.get(url)
tree = ElementTree.fromstring(response.content)
station_names = []
station_ids = []
station_lats = []
station_longs = []
for child in tree:
  station_names.append(child.attrib['stationName'].split('(')[0].strip() + ', ' + child.attrib['riverName'])
  station_ids.append(child.attrib['id'])
  station_longs.append(child.attrib['printLon'])
  station_lats.append(child.attrib['printLat'])

df_cols = ['Name', 'ID', 'Latitude', 'Longitude']
station_id_df = pd.DataFrame(columns = df_cols)
for col_nm, list_data in zip(df_cols, [station_names, station_ids, station_lats, station_longs]):
  station_id_df[col_nm] = list_data
station_id_df.to_csv('basin_data/CNRFC_Basins/gage_ids.csv')