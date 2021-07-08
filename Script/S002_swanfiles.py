import os
import itertools
from glob import glob
import pandas as pd
import xarray as xr
import numpy as np
import math

def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

def conversiongrib2toCSVNOAA(path_src, path_out, area, min_year, max_year):
    # area = [N, W, S, E]
    years  = np.arange(min_year, max_year + 1, 1, dtype=int).astype('str').tolist()
    months = ['0'+str(m) if m<10 else str(m) for m in np.linspace(1, 12, num=12, dtype=int)]
    years_months = [year+month for year, month in itertools.product(years, months)]
    for year_month in years_months:
        if os.path.isfile(path_out+'/datos_'+year_month+'.csv')==False:
            ds = xr.open_mfdataset(
                path_src+'/*'+year_month+'.grb2', engine='cfgrib', drop_variables = ['surface','time']
                )
            ds = ds.assign_coords(step=(ds.valid_time)).rename({'step':'time'}).drop_vars("valid_time")
            ds = ds.assign_coords(longitude=(((ds.longitude + 180) % 360) - 180)).sortby('longitude')
            ds = ds.where(ds.latitude <= area[0], drop=True)\
                .where(ds.longitude >= area[1], drop=True)\
                    .where(ds.latitude >= area[2], drop=True)\
                        .where(ds.longitude <= area[3], drop=True)
            ds = ds.drop_isel(time=-1)
            _ = [os.remove(file) for file in glob("Data/grib_NOAA/*.idx")]
            ds.to_dataframe().dropna().reset_index().to_csv(path_out+'/datos_'+year_month+'.csv', index=False)
        else:
            pass
    if os.path.isfile(path_out+'/_entrada_modelo.csv') == False:
        df = [pd.read_csv(path_file) for path_file in glob(path_out+'/*csv') if (path_file != path_out+'/_entrada_modelo.csv')]
        df = pd.concat(df)
        df.to_csv(path_out+'/_entrada_modelo.csv', index=False)
        return df
    else:
        df = pd.read_csv(path_out+'/_entrada_modelo.csv')
        df.time = pd.to_datetime(df.time, format="%Y-%m-%d %H:%M:%S")
        return df

def get_values(n, ds, nodos):
    sub_ds = ds.isel(time=n).sel(latitude=nodos[0][0], longitude=nodos[0][1])
    hs, tp, dp = sub_ds['swh'].values, sub_ds['perpw'].values, sub_ds['dirpw'].values
    return hs, tp, dp