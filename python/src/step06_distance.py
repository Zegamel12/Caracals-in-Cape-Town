from config import ROADS
from config import ANALYSIS_CRS, TRAJECTORIES, DISTANCE
import pandas as pd
import geopandas as gpd

def calculate_distance():
    """ calculate distance between consecutive GPS movements. """

    # load Trajectores from step04 and road files from step03
    trajectories_data = gpd.read_file(TRAJECTORIES)
    roads_data = gpd.read_file(ROADS)

    # Reproject to a Analysis crs
    trajectories_data = trajectories_data.to_crs(ANALYSIS_CRS)
    roads_data = roads_data.to_crs(ANALYSIS_CRS)

    # find the nearest road and calculate distance
    distance_data = gpd.sjoin_nearest(
        trajectories_data, roads_data[["geometry"]],................) # to be updated

    # 
        
    # save th edistance dataset
    distance_data.to_file(DISTANCE, layer = "distance", driver = "GPKG")



    return distance_data