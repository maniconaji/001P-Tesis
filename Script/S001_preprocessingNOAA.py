#Importar paquetes y definir funciones principales (ver haciendo doble click)
import wget
import os
import itertools
import numpy as np
import pandas as pd
from glob import glob
import urllib.request
import xarray as xr

def url_is_alive(url):
    """
    Checks that a given URL is reachable.
    :param url: A URL
    :rtype: bool
    """
    request = urllib.request.Request(url)
    request.get_method = lambda: 'HEAD'

    try:
        urllib.request.urlopen(request)
        return True
    except urllib.request.HTTPError:
        return False

def descargasarchivos_multi1(path_folder, variable, anho_min, anho_max,**kwargs):
    """
    Función para descargar archivos provenientes del centro de modelamiento ambiental del NOAA
    https://polar.ncep.noaa.gov/waves/download.shtml?
    
    path_folder   (str): dirección donde serán descargados los archivos.
    variable      (str): variable a descargar, puede ser dp, hs, tp y wind.
    anho_min      (int): año mínimo. (2006 para .grb2, 1997 para .grb)
    anho_max      (int): año máximo. (2018 para .grb2, 2005 para .grb)

    example url: "https://www.ncei.noaa.gov/thredds-ocean/fileServer/ncep/nww3/2006/01/glo_30m/multi_1.glo_30m.wind.200601.grb2"
    example url: "https://www.ncei.noaa.gov/thredds-ocean/fileServer/ncep/nww3/2017/01/gribs/multi_1.glo_30m.dp.201701.grb2"
    """

    path_src = "https://www.ncei.noaa.gov/thredds-ocean/fileServer/ncep/nww3/"
    #crear lista con años y meses a descargar
    anhos = np.arange(anho_min, anho_max + 1, 1, dtype = int).astype('str') 
    meses = [str(m) if m > 9 else '0'+str(m) for m in np.arange(1, 12 + 1, 1, dtype = int)]
    #chequear que carpeta se encuentra creada y correctamente digitada
    owd = os.getcwd()
    if os.path.isdir(path_folder) == True:
        #cambio de dirección
        os.chdir(path_folder)
        # comienza el proceso de iteración
        for anho in anhos:
            for mes in meses:
                #definición del nombre objetivo del archivo que contiene información para todo el mundo.
                name_file = 'multi_1.glo_30m.'+variable+'.'+anho+mes+'.grb2'
                #verificar si el archivo ya se encuentra descargado
                if os.path.isfile(name_file) != True:
                    #   descargar el archivo
                    if url_is_alive(path_src+anho+"/"+mes+"/glo_30m/"+name_file) == True:
                        wget.download(path_src+anho+"/"+mes+"/glo_30m/"+name_file)
                    elif url_is_alive(path_src+anho+"/"+mes+"/gribs/"+name_file) == True:
                        wget.download(path_src+anho+"/"+mes+"/gribs/"+name_file)
    os.chdir(owd)
    print("termino variable:", variable)
    return

def conversiongrib2toCSVNOAA(path_src, path_out, area, min_year, max_year):
    """
    Función para convertir los archivos .grb o .grb2 a .csv
    https://polar.ncep.noaa.gov/waves/download.shtml?
    
    path_src      (str): dirección donde serán descargados los archivos
    path_out      (str): dirección donde serán descargados los archivos.
    area         (list): lista con los valores de la coordenada en WSG84 [N, W, S, E]
    min_year      (int): año mínimo.
    max_year      (int): año máximo.
    """
    #crear lista con años y meses.
    years  = np.arange(min_year, max_year + 1, 1, dtype=int).astype('str').tolist()
    months = ['0'+str(m) if m<10 else str(m) for m in np.linspace(1, 12, num=12, dtype=int)]
    #crear lista año-meses juntos.
    years_months = [year+month for year, month in itertools.product(years, months)]

    for year_month in years_months:
        #revisar que archivo no este escrito
        if os.path.isfile(path_out+'/datos_'+year_month+'.csv')==False:
            #abren archivos grb2
            ds = xr.open_mfdataset(
                path_src+'/*'+year_month+'.grb2', engine='cfgrib', drop_variables = ['surface','time']
                )
            #asignar como coordenadas la variable de tiempo 
            ds = ds.assign_coords(step=(ds.valid_time)).rename({'step':'time'}).drop_vars("valid_time")
            #asignar como coordenadas la variable de la longitud en formato (-180,180)
            ds = ds.assign_coords(longitude=(((ds.longitude + 180) % 360) - 180)).sortby('longitude')
            #recortar la grilla según el área necesaria
            ds = ds.where(ds.latitude <= area[0], drop=True)\
                .where(ds.longitude >= area[1], drop=True)\
                    .where(ds.latitude >= area[2], drop=True)\
                        .where(ds.longitude <= area[3], drop=True)
            #eliminar última variable de tiempo
            ds = ds.drop_isel(time=-1)
            #eliminar los archivos .idx generados cuando se leen archivos .grb y .grb2
            _ = [os.remove(file) for file in glob("Data/grib_NOAA/*.idx")]
            #crear dataframe con los archivos
            ds.to_dataframe().dropna().reset_index().to_csv(path_out+'/datos_'+year_month+'.csv', index=False)
        else:
            pass
    #verificar si el archivo con todos los datos existe.
    if os.path.isfile(path_out+'/_entrada_modelo.csv') == False:
        #leer cada archivo y crear el archivo con todos los datos.
        df = [pd.read_csv(path_file) for path_file in glob(path_out+'/*csv') if (path_file != path_out+'/_entrada_modelo.csv')]
        df = pd.concat(df)
        df.to_csv(path_out+'/_entrada_modelo.csv', index=False)
        return df
    else:
        # leer el archivo ya creado.
        df = pd.read_csv(path_out+'/_entrada_modelo.csv')
        df.time = pd.to_datetime(df.time, format="%Y-%m-%d %H:%M:%S")
        return df