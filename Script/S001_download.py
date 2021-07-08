#Importar paquetes y definir funciones principales (ver haciendo doble click)
import wget
import os
import numpy as np
import urllib.request
import cdsapi

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
    anho_min      (int): año máximo a descargar, las modelaciones comenzaron el año 2006.
    anho_max      (int): año mínimo a descargar, considerando que el máximo es el año 2018.

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
    print("termino iteración de variable:", variable)
    return

def descargas_era5copernicus(path_folder, min_year, max_year, variables, area):
    """
    Función para descargar archivos provenientes del centro de modelamiento ambiental del NOAA
    https://polar.ncep.noaa.gov/waves/download.shtml?
    
    path_folder   (str): dirección donde serán descargados los archivos.
    min_year      (int): año mínimo a descargar.
    max_year      (int): año máximo a descargar.
    variables    (list): lista con variables a descargar.
    area         (list): lista con coordenadas -> [N, W, S, E] ejemplo: [-35, -76, -39,-72]
    """
    c = cdsapi.Client()
    
    years  = np.arange(min_year, max_year + 1, 1, dtype=int).astype('str').tolist()
    months = ['0'+str(m) if m<10 else str(m) for m in np.linspace(1, 12, num=12, dtype=int)]
    days   = ['0'+str(d) if d<10 else str(d) for d in np.linspace(1, 31, num=31, dtype=int)]
    hours  = ['00:00', '03:00', '06:00','09:00', '12:00', '15:00','18:00', '21:00',]

    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'variable': variables,
            'year': years,
            'month': months,
            'day': days,
            'time': hours,
            'area': area,
            'format': 'grib',
        }, path_folder+'/wave_miny'+str(min_year)+'-'+str(max_year)+'.grib')
    return