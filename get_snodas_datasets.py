import requests
###Western US snow reanalysis: https://www.nature.com/articles/s41597-022-01768-7
###https://nsidc.org/data/wus_ucla_sr/versions/1
##national water model: https://console.cloud.google.com/storage/browser/national-water-model-v2;tab=objects?prefix=&forceOnObjectsSortingFiltering=false
##Others: https://nsidc.org/data/mod10a1/versions/61
# https://www.tandfonline.com/doi/full/10.1080/20964471.2023.2177435
# https://tc.copernicus.org/articles/14/1579/2020/
# https://www.nohrsc.noaa.gov/archived_data/

file_url = "https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v3.0.csv"
r = requests.get(file_url)
r.raise_for_status()
except requests.exceptions.HTTPError as err:	
    raise SystemExit(err)
with open("N_seaice_extent_daily_v3.0.csv", "wb") as f:	
    f.write(r.content)