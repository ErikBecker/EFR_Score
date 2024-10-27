

import config

from dem_tasks import read_dem
from create_scan_strategy_points import create_scan_array

import numpy as np
import os

import pyproj
from radar_site import load_radar_params

import warnings
warnings.filterwarnings('ignore')

def define_cuboid_coords(lat,lon,x_size,y_size,z_size,grid_size,proj_string):
        
    size = x_size / 2
    X = np.arange(-size,size,grid_size)
    X += grid_size / 2.
    size = y_size / 2
    Y= np.arange(-size,size,grid_size)
    Y += grid_size / 2.
    Z = np.arange(0,z_size,grid_size)
    Z += grid_size / 2.

    X,Y = pyproj.transform(config.cubiod_proj, proj_string, X, Y)
    
    return {'X_coords':X,'Y_coords':Y,'Z_coords':Z}





if __name__ == "__main__":
    
    ####### LOAD RADAR SCAN PARAMETERS ##########
    
    print("LOAD - RADAR PARAMETERS")
    
    Radars = load_radar_params(config.yml_files)
    
    ############### DEFINE CART CUBE ############

    print("DEFINE - CUBE")
    
    cuboid = define_cuboid_coords(**config.cubiod_params)
    
    ########## LOAD DEM ############

    print("LOAD - DEM")

    ## Specify the file path of the raster TIFF file
    tif_file = os.path.join(config.datadir,"data/dem/sing_500km_dem_buildings.tif")
    DEM = read_dem(tif_file)
    
    ##############
     
    print('CREATE SCAN STRATEGY POINTS')
    
    radar_scans = []
    for radar in Radars:

        if not os.path.isfile(f"{config.datadir}/data/radar_scans/{radar.name}.npy"):
            print(f'SCAN STRATEGY - {radar.name}')
            scan_geo_points = create_scan_array(radar,DEM)
            np.save(f"{config.datadir}/data/radar_scans/{radar.name}.npy",scan_geo_points)
        else:
            scan_geo_points = np.load(f"{config.datadir}/data/radar_scans/{radar.name}.npy")
        
        radar_scans.append(scan_geo_points)
        
   
                
          
         
        
        
        
        
        break
    
    