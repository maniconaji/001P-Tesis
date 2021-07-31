import xarray as xr
import os

def reading_allNCfiles(path_src, concat_dim, combine):

    if os.path.isfile():
        ds = xr.open_mfdataset(path_src, concat_dim=concat_dim, combine=combine)