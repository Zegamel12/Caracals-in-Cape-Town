from config import ANALYSIS_CRS, TRAJECTORIES, DISTANCE
import pandas as pd
import geopandas as gpd

def calculate_distance():
    """ calculate distance between consecutive GPS movements. """

    # load Trajectores from step04
    trajectories_data = gpd.read_file(TRAJECTORIES)

    # Reproject to a Analysis crs
    trajectories_data = trajectories_data.to_crs(ANALYSIS_CRS)

    # sort observations by timestamp and individuals
    trajectories_data = trajectories_data.soft.values(["individual_local_identifier", "timestamp_datetime"])

    # create output dataset
    distance_data = trajectories_data.copy()

    # calculate distance from previous observation
    # # https://pandas.pydata.org/docs/reference/api/pandas.api.typing.SeriesGroupBy.shift.html
    # # https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html
    # https://geopandas.org/en/stable/docs/reference/geoseries.html
    # https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.distance.html
    
    #  distance_data.geometry_distance() ??


    # save th edistance dataset
    distance_data.to_file(DISTANCE, layer = "distance", driver = "GPKG")



    return distance_data