"""Step 06: distance from every GPS point to the nearest road.
 
Input : step04 trajectories (points) and step03 roads
Output: DISTANCE GeoPackage (points + distance_m + distance_class) and a bar chart.
"""
# References
# - geopandas sjoin_nearest: https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin_nearest.html
# - geopandas spatial joins: https://docs.geopandas.org/en/latest/gallery/spatial_joins.html
# - geopandas read_file / to_crs / to_file:
#       https://geopandas.org/en/stable/docs/reference/api/geopandas.read_file.html
#       https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html
#       https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_file.html
# - pandas Index.duplicated: https://pandas.pydata.org/docs/reference/api/pandas.Index.duplicated.html
# - pandas.cut:              https://pandas.pydata.org/docs/reference/api/pandas.cut.html
# - pandas value_counts / reindex:
#       https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
#       https://pandas.pydata.org/docs/reference/api/pandas.Series.reindex.html
# - matplotlib bar:          https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.bar.html
# - matplotlib bar_label:    https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.bar_label.html
# - matplotlib savefig:      https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html


import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from python.src.config import ANALYSIS_CRS, DISTANCE, FIGURES, ROADS, TRAJECTORIES

BINS = [0, 10, 20, 50, 100, 500, float("inf")]
LABELS = ["0-10 m", "10-20 m", "20-50 m", "50-100 m", "100-500 m", ">500 m"]


def add_distance_class(data):
    """ add a text column with the distance class)"""
    # Include_lowest=True keeps points that lie exactly on a read(distance 0)
    classes = pd.cut(data["distance_m"], bins=BINS, labels=LABELS, include_lowest=True)
    # saveed as text : catagory columns can cause trouble inGeoPackage
    data["distance_class"]= classes.astype(str)
    return data

def calculate_distance():
    """ calculate distance from GPS points to the nearest road. """
    # https://pandas.pydata.org/docs/reference/api/pandas.Index.duplicated.html
    # https://docs.geopandas.org/en/latest/gallery/spatial_joins.html
    # https://www.geeksforgeeks.org/python/pandas-cut-method-in-python/
    # https://pandas.pydata.org/docs/reference/api/pandas.cut.html

    # load Trajectores from step04 and road files from step03
    trajectories_data = gpd.read_file(TRAJECTORIES)
    roads_data = gpd.read_file(ROADS)

    # Exclude GPS records without a usable location
    trajectories_data=trajectories_data[trajectories_data.geometry.notna() & ~trajectories_data.geometry.is_empty].copy()

    # Assign a unique ID to each remaining observation
    trajectories_data = trajectories_data.reset_index(drop=True)
    trajectories_data["observation_id"] = range(len(trajectories_data))

    # Reproject to a Analysis crs
    trajectories_data = trajectories_data.to_crs(ANALYSIS_CRS)
    roads_data = roads_data.to_crs(ANALYSIS_CRS)

    # calculate the distance to the nearest road
    distance_data = gpd.sjoin_nearest(
        trajectories_data, roads_data[["geometry"]],how="left" ,distance_col="distance_m")

    # Multiple equidistant roads can return multiple rows for one GPS point.
    total_duplicated = distance_data.index.duplicated().sum()
    print(total_duplicated)

    # Keep one nearest road result per GPS point and remove the index column created by sjoin
    distance_data = (distance_data[~distance_data.index.duplicated(keep="first")].drop(columns=["index_right"]))

    # Classify distance to the nearest road, in metres and save
    distance_data= add_distance_class(distance_data)
    distance_data.to_file(DISTANCE, layer ="s06a_distance", driver = "GPKG")

    # Count GPS observations per distance class
    distance_counts = (distance_data["distance_class"].value_counts().sort_index()) # per class
    print(distance_counts)

    # Plot GPS observations per distance class
    fig, ax = plt.subplots(figsize=(9,6))
    bars = ax.bar(distance_counts.index, distance_counts.values) 

    ax.bar_label(
        bars,
        labels= [f"{int(value):,}" for value in distance_counts.values], 
        padding = 3 ) #https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.bar_label.html
    ax.set_xlabel("Distance to nearest road", fontsize=12)
    ax.set_ylabel("Number of GPS points", fontsize=12)
    ax.set_title("GPS points by distance to the nearest road", fontsize=14)
    ax.tick_params(axis = "x", rotation = 45)
    fig.text(0.99, 0.01, "GPS: Serieys et al. 2023; roads: (c) OpenStreetMap contributors (ODbL)",
             ha="right", fontsize=7)
    plt.tight_layout()

    # Save to figures dir
    fig.savefig(FIGURES / "s06a_distance_classes.png", dpi=150)

    plt.close(fig)

    return distance_counts
