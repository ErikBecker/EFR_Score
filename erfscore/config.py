#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 07:25:48 2024

@author: ebecker
"""

import os

## DEFINE DATA DIRECTORY
# DATADIR = "/scratch/ebecker/EFR"
datadir = "/home/ebecker/sf_work/PhD/paper_EFR/ERF"

## DEFINE PROJECTION TO USE
proj_string = "+proj=longlat +datum=WGS84 +no_defs"

yml_files = os.path.join(datadir,"radar_params")

cubiod_params = {'lat':1.3521,
                 'lon':103.8198,
                 'x_size':200,
                 'y_size':200,
                 'z_size':15,
                 'grid_size':0.25,
                 'proj_string':proj_string}

cubiod_proj = "+proj=aeqd +lat_0=" + str(cubiod_params['lat']) + " +lon_0=" + str(cubiod_params['lon']) + " +x_0=0 +y_0=0 +datum=WGS84 +units=km +no_defs"

er = 6378.137         # Earth Radius @ sea level equator in km
RfR = (4/3)*er        # Effective Radius assuming standard refraction in km
pbb_threshold = 0.33  # If pbb exceed percentage of beam blockage it will discard radar pixel from scan array.