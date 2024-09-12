from datetime import datetime
import csv
import requests
import os
import pandas as pd

if not os.path.isdir('forecasts'):
  os.mkdir('forecasts')



basin_list = ['BMDC2', 'CLSC2', 'DLAC2', 'DRGC2', 'GBRW4', 'GJLOC', 'GLDA3', 'GRNU1', 'LEMC2', 'LNAC2', 'MPSC2', 'NAVC2', 'NVLOC', 'NVRN5', 'RBPC2', 'TPIC2', 'VCRC2', 'YDLC2']
fail_list = []
month_ls = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
for basin_name in basin_list:
  basin_dir = os.path.join('forecasts', basin_name)
  if not os.path.isdir(basin_dir):
    os.mkdir(basin_dir)
  for year_num in range(2013, 2025):
    for month_num in range(1, 13):
      
      CSV_URL = 'https://www.cbrfc.noaa.gov/outgoing/32month/archive/adj/' + month_ls[month_num-1] + str(year_num-2000) + '/ADJ.' + str(year_num) + '-' + str(month_num).zfill(2) + '-01.RAW.' + basin_name + '.' + month_ls[month_num-1] + str(year_num-2000) + '.txt'
      trace_df = pd.DataFrame()
      with requests.Session() as s:
        download_fail = False
        try:
          print(CSV_URL)
          download = s.get(CSV_URL)
          
        except:
          download_fail = True
        if '404 Not Found' in download.content.decode('utf-8'):
          write_data = False
          check_new_data = True
        else:
          write_data = True
          check_new_data = False
        if download_fail:
          fail_list.append('https://www.cbrfc.noaa.gov/outgoing/32month/archive/adj/' + month_ls[month_num-1] + str(year_num-2000) + '/ADJ.' + str(year_num) + '-' + str(month_num).zfill(2) + '-01.RAW.' + basin_name + '.' + month_ls[month_num-1] + str(year_num-2000) + '.txt')
          fail_list_df = pd.DataFrame(fail_list, columns = ['failed reforecast download',])
          fail_list_df.to_csv('forecasts/failed_months.csv')
          print(basin_name, end = " ")
          print(year_num, end = " ")
          print(month_num, end = " ")
          print('failed')
        elif write_data:
          decoded_content = download.content.decode('utf-8')
          cr = csv.reader(decoded_content.splitlines(), delimiter='\t')
          my_list = list(cr)
          counter = 0
          for row_all in my_list:
            row = row_all[0].split()
            if counter == 2:
              trace_df = pd.DataFrame(columns = row[2:])
            elif counter >2:
              index_use = datetime.strptime(row[0], '%m/%Y')
              for obs, row_col in zip(row[1:], trace_df.columns):
                if obs == row[0]:
                  trace_df.loc[index_use, row_col] = obs
                else:
                  trace_df.loc[index_use, row_col] = float(obs)
            counter += 1
        if len(trace_df) > 0:
          trace_df.to_csv(os.path.join(basin_dir, 'forecast_' + str(year_num) + '_' + str(month_num).zfill(2) + '.csv'))
          print(basin_name, end = " ")
          print(year_num, end = " ")
          print(month_num)
      current_day = 2
      while current_day < 32 and check_new_data and year_num < 2024:
        CSV_URL = 'https://www.cbrfc.noaa.gov/outgoing/32month/archive/raw/' + month_ls[month_num-1] + str(year_num-2000) + '/ADJ.' + str(year_num) + '-' + str(month_num).zfill(2) + '-' + str(current_day).zfill(2) + '.RAW.' + basin_name + '.' + month_ls[month_num-1] + str(year_num-2000) + '.txt'
        trace_df = pd.DataFrame()
        with requests.Session() as s:
          download_fail = False
          try:
            print(CSV_URL)
            download = s.get(CSV_URL)          
          except:
            download_fail = True
          if '404 Not Found' in download.content.decode('utf-8'):
            write_data = False
            check_new_data = True
          else:
            check_new_data = False
            write_data = True

          if write_data:
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter='\t')
            my_list = list(cr)
            counter = 0
            for row_all in my_list:
              row = row_all[0].split()
              if counter == 2:
                trace_df = pd.DataFrame(columns = row[2:])
              elif counter >2:
                index_use = datetime.strptime(row[0], '%m/%Y')
                for obs, row_col in zip(row[1:], trace_df.columns):
                  if obs == row[0]:
                    trace_df.loc[index_use, row_col] = obs
                  else:
                    trace_df.loc[index_use, row_col] = float(obs)
              counter += 1
          if len(trace_df) > 0:
            trace_df.to_csv(os.path.join(basin_dir, 'forecast_' + str(year_num) + '_' + str(month_num).zfill(2) + '.csv'))
            print(basin_name, end = " ")
            print(year_num, end = " ")
            print(month_num)

          
        current_day += 1
      
