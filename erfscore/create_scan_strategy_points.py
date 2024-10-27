#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 07:07:54 2024

@author: ebecker
"""

from beamblockage import calc_beamblockage
import config
from dem_tasks import get_dem_ave
import numpy as np
import pyproj

def create_scan_points(radar_params,index):
    
    min_ranges = (np.arange(radar_params.nbins[index]) * radar_params.rscale[index]) / 1000.
    max_ranges = ((np.arange(radar_params.nbins[index]) * radar_params.rscale[index]) + radar_params.rscale[index]) / 1000.
    min_idx = np.argmin(np.abs(radar_params.minRange - min_ranges))
    max_idx = np.argmin(np.abs(radar_params.maxRange - max_ranges))
    
    min_ranges = min_ranges[min_idx:max_idx]    
    max_ranges = max_ranges[min_idx:max_idx]    
    min_azim = np.arange(radar_params.nrays) * radar_params.step_angle
    max_azim = (np.arange(radar_params.nrays) * radar_params.step_angle) + radar_params.step_angle
    return {'min_ranges':min_ranges, 'max_ranges':max_ranges, 'min_azim':min_azim, 'max_azim':max_azim}

def convert_to_cart(points,radar_params,index,elev):
    
    min_ranges = (np.arange(radar_params.nbins[index]) * radar_params.rscale[index]) / 1000.
    max_ranges = ((np.arange(radar_params.nbins[index]) * radar_params.rscale[index]) + radar_params.rscale[index]) / 1000.
    min_idx = np.argmin(np.abs(radar_params.minRange - min_ranges))
    max_idx = np.argmin(np.abs(radar_params.maxRange - max_ranges))
    
    ranges = ((np.arange(radar_params.nbins[index]) * radar_params.rscale[index]) + (radar_params.rscale[index]/2)) / 1000.
    ranges = ranges[min_idx:max_idx]
    azim = (np.arange(radar_params.nrays) * radar_params.step_angle) + (radar_params.step_angle/2)
    
    ra_grid = np.meshgrid(ranges,azim)
    
    ThetaE = (np.pi/180)*elev + np.arctan((ra_grid[0]*np.cos((np.pi/180)*elev))/(config.RfR+ra_grid[0]*np.sin((np.pi/180)*elev)))
    
    X = ra_grid[0] * np.cos(ThetaE) * np.sin((np.pi/180)*ra_grid[1])
    Y = ra_grid[0] * np.cos(ThetaE) * np.cos((np.pi/180)*ra_grid[1])
    Z = np.sqrt(ra_grid[0]**2 + config.RfR**2 + 2*ra_grid[0]*config.RfR*np.sin((np.pi/180)*elev)) - config.RfR + (radar_params.Height/1000)
    B = ra_grid[0] * np.tan((np.pi/180)*radar_params.BeamWidth)
    
    return {"X":X,"Y":Y,"Z":Z,"B":B}

def include_valid_point(xyz_scan):
    # Extract x, y, and z columns as separate arrays
    x, y, z, b, pbb = xyz_scan.T  
    # Create a boolean mask for points that fall within the desired range
    mask = (z >= 0) & (z <= 15) & (b >= 0)  & (pbb < 0.33)
    # Use the boolean mask to filter the rows of xyz_scan
    output = xyz_scan[mask]
    return np.unique(output,axis=0)


def create_scan_array(radardata,DEM):
    
    # GET CENTER POINT OF POLAR POINTS
    X,Y,Z,B,PBB = np.array([]),np.array([]),np.array([]),np.array([]),np.array([])
    for i,elev in enumerate(radardata.elev):
        
        print("Processing Elevation: ",elev)
        scan_points = create_scan_points(radardata,i)
        demZ = get_dem_ave(elev,scan_points,DEM)
        cart_points = convert_to_cart(scan_points,radardata,i,elev)
        PBB_ = calc_beamblockage(demZ,cart_points["Z"],cart_points["B"])
    
        X_,Y_ = pyproj.transform(config.cubiod_proj, config.proj_string, cart_points['X'], cart_points['Y'])
        Z_ = cart_points["Z"]
        B_ = cart_points["B"]
        
        X = np.append(X,X_.ravel())     
        Y = np.append(Y,Y_.ravel())            
        Z = np.append(Z,Z_.ravel())     
        B = np.append(B,B_.ravel())     
        PBB = np.append(PBB,PBB_.ravel())     
                
    xyz_scan = np.array([X,Y,Z,B,PBB]).T
    
    xyz_scan = include_valid_point
    
    return xyz_scan