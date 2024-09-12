import requests
import os
import pandas as pd
import csv
import numpy as np
import datetime as datetime
rfc_folder = os.path.join('forecasts','NWRFC')
if not os.path.isdir('forecasts'):
  os.mkdir('forecasts')
if not os.path.isdir(rfc_folder):
  os.mkdir(rfc_folder)
basin_list = ['BMDC2', 'CLSC2', 'DRGC2', 'GBRW4', 'GJLOC', 'GLDA3', 'GRNU1', 'MPSC2', 'NVRN5', 'TPIC2', 'VCRC2', 'YDLC2']
fail_list = []
for year_num in range(2012, 2025):
  for month_num in range(1, 13):
    day_use = 1
    still_looking = True
    while still_looking and day_use <32:
      print(year_num, end = " ")
      print(month_num, end = " ")
      print(day_use, end = " ")      
      CSV_URL = 'https://www.nwrfc.noaa.gov/water_supply/ws_report_csv.cgi?Type=ALL&Source=ALL&Wyr=' + str(year_num) + '&WyrDate=' + str(year_num) + str(month_num).zfill(2) + str(day_use).zfill(2)
      print(CSV_URL)
      with requests.Session() as s:
        try:
          download = s.get(CSV_URL)
          decoded_content = download.content.decode('utf-8')
          cr = csv.reader(decoded_content.splitlines(), delimiter=',')
          my_list = list(cr)
          if len(my_list) <= 10:
            day_use += 1
          else:
            still_looking = False
        except:
          day_use += 1
    if day_use < 32:
      counter = 0
      for row in my_list:
        if len(row) > 1:
          if counter == 0:
            trace_df = pd.DataFrame(columns = row)
          else:
            for obs, row_col in zip(row, trace_df.columns):
              try:
                trace_df.loc[counter, row_col] = float(obs)
              except:
                trace_df.loc[counter, row_col] = obs
          counter += 1
      basin_names = trace_df.ID.unique()
      for basin_id in basin_names:
        basin_folder = os.path.join(rfc_folder, basin_id)
        if not os.path.isdir(basin_folder):
          os.mkdir(basin_folder)
        this_basin_data = trace_df[trace_df['ID'] == basin_id]
        this_basin_data.index = this_basin_data['FcstPeriod']
        try:
          basin_forecast_df = this_basin_data[['90%Fcst','75%Fcst','50%Fcst','25%Fcst','10%Fcst']]
        except:
          basin_forecast_df = this_basin_data[['90%Fcst','50%Fcst','10%Fcst']]
        basin_forecast_df.to_csv(os.path.join(basin_folder, 'forecast_' + str(year_num) + '_' + str(month_num).zfill(2) + '.csv'))
