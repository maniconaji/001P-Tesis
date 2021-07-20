import os
import cdsapi
import numpy as np
import xarray as xr
import pandas as pd
from glob import glob

def descargas_era5copernicus(path_folder, year, variables, area):
    """
    Función para descargar archivos provenientes del centro de modelamiento ambiental del NOAA
    https://polar.ncep.noaa.gov/waves/download.shtml?
    
    path_folder   (str): dirección donde serán descargados los archivos.
    min_year      (int): año mínimo a descargar.
    max_year      (int): año máximo a descargar.
    variables    (list): lista con variables a descargar.
    area         (list): lista con coordenadas -> [N, W, S, E] ejemplo: [-35, -76, -39,-72]
    """
    
    
    months = ['0'+str(m) if m<10 else str(m) for m in np.linspace(1, 12, num=12, dtype=int)]
    days   = ['0'+str(d) if d<10 else str(d) for d in np.linspace(1, 31, num=31, dtype=int)]
    hours  = ['00:00', '03:00', '06:00','09:00', '12:00', '15:00', '18:00', '21:00',]

    if os.path.isfile(path_folder+'/wave_y'+str(year)+'.grib')==False:
        c = cdsapi.Client()
        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': variables,
                'year': str(year),
                'month': months,
                'day': days,
                'time': hours,
                'area': area,
                'format': 'grib',
            }, path_folder+'/wave_y'+str(year)+'.grib')
    else:
        pass
    return

def conversiongrib2toCSVCopernicus(path_src, path_out, min_year, max_year):
    if os.path.isfile(path_out+'/datos_'+str(min_year)+'-'+str(max_year)+'.csv')==False:
        ds_all = xr.open_mfdataset(path_src+"/*.grib", combine="nested", concat_dim="time")\
            .drop_vars(["number","step", "meanSea", "valid_time"])
        df_all = ds_all.to_dataframe()
        df_all.dropna().reset_index().to_csv(path_out+'/datos_'+str(min_year)+'-'+str(max_year)+'.csv', index=False)
        _ = [os.remove(file) for file in glob(path_src+"/*.idx")]
        df_all.time = pd.to_datetime(df_all.time, format="%Y-%m-%d %H:%M:%S")
        return df_all
    else:
        df = pd.read_csv(path_out+'/datos_'+str(min_year)+'-'+str(max_year)+'.csv')
        df.time = pd.to_datetime(df.time, format="%Y-%m-%d %H:%M:%S")
        _ = [os.remove(file) for file in glob(path_src+"/*.idx")]
        return df