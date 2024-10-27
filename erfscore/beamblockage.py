#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 08:05:01 2024

@author: ebecker
"""
import numpy as np

def calc_beamblockage(demZ,Z,B):
    
    PBB = np.zeros_like(demZ)
    
    y = demZ-Z
    a = B / 2
    
    PBB[y<=-(a)] = 0.
    PBB[y>=a] = 1.
    
    y_ = y[(y>(-a))&(y<a)]
    a_ = a[(y>(-a))&(y<a)]
    PBB[(y>(-a))&(y<a)] = (1/np.pi)*((y_/(a_*a_))*np.sqrt((a_*a_)-(y_*y_))+np.arcsin(y_/a_)+(np.pi/2))
    
    for col in range(len(PBB[0])-1):  # iterate over columns, except last one
        for row in range(len(PBB)):  # iterate over rows
            if PBB[row][col+1] < PBB[row][col]:
                PBB[row][col+1] = PBB[row][col]
                
    return PBB