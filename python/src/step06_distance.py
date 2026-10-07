
from python.src.config import ANALYSIS_CRS, TRAJECTORIES, DISTANCE, ROADS
import pandas as pd
import geopandas as gpd

def calculate_distance():
    """ calculate distance from GPS points to th enearest road. """
    # https://pandas.pydata.org/docs/reference/api/pandas.Index.duplicated.html
    # https://docs.geopandas.org/en/latest/gallery/spatial_joins.html

    # load Trajectores from step04 and road files from step03
    trajectories_data = gpd.read_file(TRAJECTORIES)
    roads_data = gpd.read_file(ROADS)

    # Reproject to a Analysis crs
    trajectories_data = trajectories_data.to_crs(ANALYSIS_CRS)
    roads_data = roads_data.to_crs(ANALYSIS_CRS)

    # find the nearest road and calculate distance
    distance_data = gpd.sjoin_nearest(
        trajectories_data, roads_data[["geometry"]],how="left" ,distance_col="distance_m")

    # check how many GPS indicies were created
    total_duplicated = distance_data.index.duplicated().sum()
    print(total_duplicated)

    # Keep one nearest road result per GPS point and remove the index column created by sjoin
    distance_data = (distance_data[~distance_data.index.duplicated(keep="first")].drop(columns=["index_right"]))
        
    # save th edistance dataset
    distance_data.to_file(DISTANCE, layer = "distance", driver = "GPKG")

    return distance_data
