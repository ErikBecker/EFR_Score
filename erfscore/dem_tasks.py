#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 07:13:03 2024

@author: ebecker
"""

import config
import numpy as np
import multiprocessing
from joblib import Parallel, delayed
from osgeo import gdal
import pyproj
from skimage.draw import polygon
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

def read_dem(tif_file):
    
    # Open the raster file using gdal
    raster_dataset = gdal.Open(tif_file)
    
    geotransform = raster_dataset.GetGeoTransform()
    ymax = geotransform[3]
    pixel_width = geotransform[1]
    xmin = geotransform[0]
    pixel_height = geotransform[5]
    width = raster_dataset.RasterXSize
    height = raster_dataset.RasterYSize
    xmax = xmin + pixel_width * width
    ymin = ymax + pixel_height * height
    
    xlon = np.linspace(xmin, xmax,width)
    ylat = np.linspace(ymax, ymin,height)
    # ylat = np.linspace(ymin, ymax,height)
    
    DEM = np.array(raster_dataset.ReadAsArray())
    
    return {'DEM':DEM,'xlon':xlon,'ylat':ylat}

def get_dem_ave(elev,points,dem):
    
    arc = []  
    for min_val, max_val in zip(points['min_azim'], points['max_azim']):
        arr = np.arange(min_val, max_val, 0.01)
        arc.append(arr) 

    num_cores = multiprocessing.cpu_count()
    num_arc = len(arc)      
    demZ = Parallel(n_jobs=num_cores)(delayed(process_arc)(j,arc,points['min_ranges'],points['max_ranges'],elev,dem) for j in tqdm(range(num_arc)))
    demZ = np.array(demZ)/1000
        
    return demZ

def process_arc(j,arc,min_ranges,max_ranges,elev,DEM):
    

    xmin_idx, ymin_idx = calc_xy_index(min_ranges,arc[j],elev,DEM['xlon'],DEM['ylat'])
    xmax_idx, ymax_idx = calc_xy_index(max_ranges,arc[j],elev,DEM['xlon'],DEM['ylat'])

    xmax_idx = np.flipud(xmax_idx)
    ymax_idx = np.flipud(ymax_idx)

    x_idx = np.vstack([xmin_idx,xmax_idx])
    y_idx = np.vstack([ymin_idx,ymax_idx])

    demZ_row = np.zeros(x_idx.shape[1])
    for icol in range(x_idx.shape[1]):
        # Define the polygon vertices
        polygon_coords = np.array([y_idx[:,icol],x_idx[:,icol]]).T
        # Draw the polygon on the canvas
        rr, cc = polygon(polygon_coords[:, 0], polygon_coords[:, 1], DEM['DEM'].shape)
        demZ_row[icol] = np.nanmean(DEM['DEM'][rr, cc])

    return demZ_row

def calc_xy_index(ranges,arc,elev,xlon,ylat):
    
    ra_grid = np.meshgrid(ranges, arc)
    ThetaE = (np.pi/180)*elev + np.arctan((ra_grid[0]*np.cos((np.pi/180)*elev))/(config.RfR+ra_grid[0]*np.sin((np.pi/180)*elev)))
    X = (ra_grid[0] * np.cos(ThetaE) * np.sin((np.pi/180)*ra_grid[1]))
    Y = (ra_grid[0] * np.cos(ThetaE) * np.cos((np.pi/180)*ra_grid[1]))
    X,Y = pyproj.transform(config.cubiod_proj, config.proj_string, X, Y)
    x_idx = np.array([np.argmin(np.abs(x - xlon)) for x in X.ravel()])
    x_idx = x_idx.reshape(X.shape)
    y_idx = np.array([np.argmin(np.abs(y - ylat)) for y in Y.ravel()])
    y_idx = y_idx.reshape(Y.shape)
    
    return x_idx,y_idx