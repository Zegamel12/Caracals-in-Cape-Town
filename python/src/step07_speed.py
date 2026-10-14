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
# https://movingpandas.readthedocs.io/en/main/api/trajectorycollection.html
# https://movingpandas.readthedocs.io/en/main/api/api/movingpandas.TrajectoryCollection.add_speed.html
# https://movingpandas.readthedocs.io/en/main/api/api/movingpandas.TrajectoryCollection.to_point_gdf.html
# https://movingpandas.readthedocs.io/en/main/api/trajectory.html

# Import movingpandas
import geopandas as gpd
import movingpandas as mpd

from python.src.config import SPEED, TIME_COL, TRAJECTORIES


def calculate_speed():
    """
    Calculate speed in kilometers per hour between consecutive GPS observations within each animal's burst.

    Inputs:
        TRAJECTORIES: GPS observations containing animal identifiers, burst identifiers  and timestamps (output step 4).

    Outputs:
        SPEED: GeoPackage containing the GPS observations with new speed_kmh column.
    """
    
    # Read input previous steps
    gps_data = gpd.read_file(TRAJECTORIES)

    # Sort values: make points in chronological order
    gps_data = gps_data.sort_values(["individual_local_identifier", "burst_id", "timestamp_datetime"]
    ).copy()

    # Assign a unique trajectory_id to each animal–burst combination
    gps_data["trajectory_id"] = gps_data.groupby(
        ["individual_local_identifier", "burst_id"],
        sort= False,
    ).ngroup()

    # Create trajectories from the GPS data using trajectory_id and timestamps
    trajectory_collection= mpd.TrajectoryCollection(
        gps_data,
        traj_id_col="trajectory_id",
        t= TIME_COL,
    )

    # Calculate speed in km/h
    trajectory_collection.add_speed(
        name= "speed_kmh",
        units=("km", "h"),
    )

    # Save the results
    # https://movingpandas.readthedocs.io/en/main/api/api/movingpandas.TrajectoryCollection.to_point_gdf.html
    speed_data = trajectory_collection.to_point_gdf().reset_index()
    speed_data.to_file(SPEED, layer="speed", driver="GPKG")
