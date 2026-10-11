
from python.src.config import ANALYSIS_CRS, TRAJECTORIES, DISTANCE, ROADS
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def calculate_distance():
    """ calculate distance from GPS points to th enearest road. """
    # https://pandas.pydata.org/docs/reference/api/pandas.Index.duplicated.html
    # https://docs.geopandas.org/en/latest/gallery/spatial_joins.html
    # https://www.geeksforgeeks.org/python/pandas-cut-method-in-python/
    # https://pandas.pydata.org/docs/reference/api/pandas.cut.html

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

    # Define distance classes in meter for visualisations 
    distance_data["distance_class"] = pd.cut(
        distance_data["distance_m"],
        bins=[0, 10, 20, 50, 100, 500,float("inf")],
        labels=["0-10 m", "10-20 m", "20-50 m", "50-100 m", "100-500 m", ">500 m"]
        )
    
    # save the distance dataset
    distance_data.to_file(DISTANCE, layer = "distance", driver = "GPKG")

    # check results of distance classes
    distance_counts = (distance_data["distance_class"].value_counts().sort_index()) # per class
    print(distance_counts)

    # Visualise number GPS counts per class
    fig, ax = plt.subplots(figsize=(9,6))
    bars = ax.bar(distance_counts.index, distance_counts.values) 
    ax.bar_label(bars,labels= [f"{int(value):,}" for value in distance_counts.values], padding = 3 ) #https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.bar_label.html
    ax.set_xlabel("Distance to nearest road", fontsize=12)
    ax.set_ylabel("Number of GPS points", fontsize=12)
    ax.set_title("GPS points to the nearest road", fontsize=14)
    ax.tick_params(axis = "x", rotation = 45)
    plt.tight_layout()
    plt.show()

    return distance_counts
