"""Step 07: speed (km/h) between consecutive GPS fixes within each burst.
 
Input : step 06 points (they already hold distance_m, so the output holds speed AND distance)
Output: SPEED GeoPackage and plots.
"""

# sources 
# # MovingPandas TrajectoryCollection: https://movingpandas.readthedocs.io/en/main/api/trajectorycollection.html
# MovingPandas add_speed:    https://movingpandas.readthedocs.io/en/main/api/api/movingpandas.TrajectoryCollection.add_speed.html
# MovingPandas to_point_gdf: https://movingpandas.readthedocs.io/en/main/api/api/movingpandas.TrajectoryCollection.to_point_gdf.html
# MovingPandas speed tutorial: https://github.com/movingpandas/movingpandas-examples/blob/main/1-tutorials/2-computing-speed.ipynb
# Matplotlib hist:  https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.hist.html
# Matplotlib boxplot: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.boxplot.html
# GeoPandas read_file / to_crs / to_file: https://geopandas.org/en/stable/docs/reference/api/geopandas.html

# Import movingpandas
import movingpandas as mpd
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

from python.src.config import ANALYSIS_CRS, SPEED, TRAJECTORIES, FIGURES, ID_COL, TIME_COL

EXAMPLE_ANIMAL = "Disa - TMC27"   # animal and day used for the time-series plot
EXAMPLE_DAY = "2016-07-08"

def calculate_speed():
    # Read input and check collumns
    gps = gpd.read_file(TRAJECTORIES)
    required = [
        ID_COL,
        "burst_id",
        TIME_COL,
        "geometry",
    ]
    missing= [column for column in required if column not in gps.columns]
    if missing:
        raise ValueError(f"Missing columns in the trajectory data: {missing}")


    # Check cordinates and timestamps
    if gps.crs is None:
        raise ValueError("Trajectory data has no CRS")
    gps[TIME_COL] = (pd.to_datetime(
        gps[TIME_COL], utc= True, errors= "raise")
        .dt.tz_localize(None)
        )
    gps = gps.to_crs(ANALYSIS_CRS)


    # Make points in chronological order
    gps= gps.sort_values([ID_COL, "burst_id", TIME_COL]
    ).copy()

    # Give every animal their own burst_id
    gps["trajectory_id"] = gps.groupby(
        [ID_COL, "burst_id"],
        sort= False,
    ).ngroup()

    # Make trajectory of GeoDataFrame and calculate speed
    trajectory_collection= mpd.TrajectoryCollection(
        gps,
        traj_id_col="trajectory_id",
        t= TIME_COL,
    )
    # calculate speed in km/h
    trajectory_collection.add_speed(
        name= "speed_kmh",
        units=("km", "h"),
    )

    # Save the results
    speed_data = trajectory_collection.to_point_gdf().reset_index() #https://movingpandas.readthedocs.io/en/main/api/api/movingpandas.TrajectoryCollection.to_point_gdf.html
    speed_data.to_file(SPEED, layer="speed", driver="GPKG")

    # Visualization of results ()
    
    # 1. Histogram: movement speed distribution
    speeds = speed_data["speed_kmh"].dropna()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(speeds, bins=50, edgecolor="black")
    ax.set(
        title="Distribution of Caracal Movement Speed",
        xlabel="Speed (km/h)",
        ylabel="Number of GPS observations",
    )
    fig.tight_layout()
    fig.savefig(FIGURES / "s07a_speed_histogram.png", dpi=300)
    plt.show()


    # 2. Boxplot: movement speed and potential outliers
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.boxplot(speeds, vert=True)
    ax.set(
        title="Caracal Movement Speed: Boxplot",
        ylabel="Speed (km/h)",
    )
    fig.tight_layout()
    fig.savefig(FIGURES / "s07b_speed_boxplot.png", dpi=300)
    plt.show()


    # 3. Disa's speed through time on 8 July 2016
    disa = speed_data[
        (speed_data[ID_COL] == "Disa - TMC27")
    ].copy()

    disa[TIME_COL] = pd.to_datetime(
        disa[TIME_COL]
    )

    disa = disa[
        disa[TIME_COL].dt.date == pd.Timestamp("2016-07-08").date()
    ].sort_values(TIME_COL)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        disa[TIME_COL],
        disa["speed_kmh"],
        marker="o",
    )
    ax.set(
        title="Movement Speed of Disa — 8 July 2016",
        xlabel="Time",
        ylabel="Speed (km/h)",
    )
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(FIGURES / "s07c_disa_speed_timeseries.png", dpi=300)
    plt.show()




#def calculate_speed():
        #"""With this function speed is to be calculated in km/h between GPS
        #points within each burst."""
        #gps = gpd.read_file(TRAJECTORIES)
        #gps # Server osm is overloaded thus cannot import output of step 6, with this line I am gonna select columns like burst id, traject id and personal ids.

    #tc = mpd.TrajectoryCollection
        #tc.add_speed()
        #tc.add_timedelta()
    # To be used when I can read the file source: github.com/movingpandas/movingpandas-examples/blob/main/1-tutorials/2-computing-speed.ipynb
