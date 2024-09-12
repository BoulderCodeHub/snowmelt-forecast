import requests
import os
import pandas as pd
import csv
import numpy as np
from datetime import datetime
import geopandas as gpd

rfc_folder = os.path.join('forecasts','MBRFC')
if not os.path.isdir('forecasts'):
  os.mkdir('forecasts')
if not os.path.isdir(rfc_folder):
  os.mkdir(rfc_folder)
CSV_URL = 'https://forecast.weather.gov/product.php?site=NWS&issuedby=KRF&product=ESP&version='
CSV_URL1 = 'https://forecast.weather.gov/product.php?site=NWS&issuedby=KRF&product=ESP&format=txt&version='
CSV_URL2 = '&glossary=0'
all_stations = {}
year_use = 2024
gage_ids = pd.DataFrame()
all_mbrfc_forecasts = gpd.read_file(os.path.join('basin_data', 'national_shapefile_obs', 'national_shapefile_obs.shp'))
id_list = all_mbrfc_forecasts['GaugeLID'].unique()
counter = 0
for x in id_list:
  print(x, end = " ")
  print(counter, end = " ")
  print(len(id_list))
counter += 1
for v_num in range(0, 7):
  print(CSV_URL)
  index_no = 0
  with requests.Session() as s:
    try:
      download = s.get(CSV_URL1 + str(v_num + 1) + CSV_URL2)
      decoded_content = download.content.decode('utf-8')
      cr = csv.reader(decoded_content.splitlines(), delimiter=',')
      my_list = list(cr)
      count = 0
      for x in my_list:
        if len(x) > 0:
          if count == 3:
            line_text = x[0].split()
            if len(line_text) == 1:
              new_vals = pd.DataFrame()
              new_vals.loc[period_use, 'AVE'] = new_val_list[-1]
              new_vals.loc[period_use, '90%'] = new_val_list[-2]
              new_vals.loc[period_use, '50%'] = new_val_list[-3]
              new_vals.loc[period_use, '10%'] = new_val_list[-4]
              if not os.path.isdir(os.path.join(rfc_folder, line_text[0])):
                os.mkdir(os.path.join(rfc_folder, line_text[0]))
              if line_text[0] in id_list:
                this_gauge = all_mbrfc_forecasts[all_mbrfc_forecasts['GaugeLID'] == line_text[0]]
                new_vals.to_csv(os.path.join(rfc_folder, line_text[0], 'forecast_' + str(year_use) + '_' + str(7 - v_num).zfill(2) + '.csv'))
                gage_ids.loc[index_no, 'ID'] = line_text[0]
                gage_ids.loc[index_no, 'Latitude'] = this_gauge.loc[this_gauge.index[0], 'geometry'].x
                gage_ids.loc[index_no, 'Longitude'] = this_gauge.loc[this_gauge.index[0], 'geometry'].y
                index_no += 1
              
            else:
              new_val_list[-1] = float(line_text[-1])          
              new_val_list[-2] = float(line_text[-2])          
              new_val_list[-3] = float(line_text[-5])          
              new_val_list[-4] = float(line_text[-3])
              period_use = line_text[-6]
            
          if 'MISSOURI/YELLOWSTONE/PLATTE' in x[0]:
            count = 1
          if count == 1 and 'FORECAST POINT' in x[0]:
            count = 2
          if count == 2 and '--------' in x[0]:
            count = 3
        else:
          new_val_list = np.zeros(4)        
    except:
      print('error')
gage_ids.to_csv(os.path.join('basin_data', 'MBRFC_Basins', 'gage_ids.csv'))