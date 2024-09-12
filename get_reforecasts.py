from datetime import datetime
import csv
import requests
import os
import pandas as pd

if not os.path.isdir('reforecasts'):
  os.mkdir('reforecasts')

basin_list = ['BMDC2', 'CLSC2', 'DRGC2', 'GBRW4', 'GJLOC', 'GLDA3', 'GRNU1', 'MPSC2', 'NVRN5', 'TPIC2', 'VCRC2', 'YDLC2']
fail_list = []
for basin_name in basin_list:
  basin_dir = os.path.join('reforecasts', basin_name)
  if not os.path.isdir(basin_dir):
    os.mkdir(basin_dir)
  for year_num in range(1980, 2023):
    for month_num in range(1, 13):
      CSV_URL = 'https://www.cbrfc.noaa.gov/outgoing/bor_refcsts/' + basin_name + '/' + basin_name + '.' + str(year_num) + '-' + str(month_num).zfill(2) + '-01.espmvol.5yr.csv'
      trace_df = pd.DataFrame()
      with requests.Session() as s:
        download_fail = False
        try:
          download = s.get(CSV_URL)
        except:
          download_fail = True
        if download_fail:
          fail_list.append('https://www.cbrfc.noaa.gov/outgoing/bor_refcsts/' + basin_name + '/' + basin_name + '.' + str(year_num) + '-' + str(month_num).zfill(2) + '-01.espmvol.5yr.csv')
          fail_list_df = pd.DataFrame(fail_list, columns = ['failed reforecast download',])
          fail_list_df.to_csv('reforecasts/failed_months.csv')
          print(basin_name, end = " ")
          print(year_num, end = " ")
          print(month_num, end = " ")
          print('failed')
        else:
          decoded_content = download.content.decode('utf-8')
          cr = csv.reader(decoded_content.splitlines(), delimiter=',')
          my_list = list(cr)
          counter = 0
          for row in my_list:
            if len(row) > 1:
              if counter == 0:
                trace_df = pd.DataFrame(columns = row)
              else:
                index_use = datetime.strptime(row[0], '%m/%Y')
                for obs, row_col in zip(row, trace_df.columns):
                  if obs == row[0]:
                    trace_df.loc[index_use, row_col] = obs
                  else:
                    trace_df.loc[index_use, row_col] = float(obs)
              counter += 1
        if len(trace_df) > 0:
          trace_df.to_csv(os.path.join(basin_dir, 'reforecast_' + str(year_num) + '_' + str(month_num).zfill(2) + '.csv'))
          print(basin_name, end = " ")
          print(year_num, end = " ")
          print(month_num)
