import os
import yaml
import glob
from dataclasses import dataclass, field
from typing import List

@dataclass
class RadarStation:
    name: str
    Lat: float
    Lon: float
    BeamWidth: float
    Height: float
    minRange: float
    maxRange: float
    elev: List[float]
    nbins: List[int]
    rscale: List[float]
    nrays: int
    step_angle: float

def load_radar_station_from_yaml(file_path: str) -> RadarStation:
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return RadarStation(**data)

def load_radar_params(dir_path: str) -> List[RadarStation]:
    radar_params = []
    search_path = os.path.join(dir_path,"*.yml")
    yml_files = glob.glob(search_path)        
    for file_path in yml_files:                 
        radar_params.append(load_radar_station_from_yaml(file_path))
    return radar_params
