# sources 
# https://movingpandas.readthedocs.io/en/main/api/trajectorycollection.html
# https://movingpandas.readthedocs.io/en/main/api/api/movingpandas.TrajectoryCollection.add_speed.html
# https://movingpandas.readthedocs.io/en/main/api/api/movingpandas.TrajectoryCollection.to_point_gdf.html
# https://movingpandas.readthedocs.io/en/main/api/trajectory.html

# Import movingpandas
import geopandas as gpd
import movingpandas as mpd

from python.src.config import SPEED, TRAJECTORIES


def calculate_speed():
    """Calculate GPS-based movement speed for each animal burst.

    Purpose:
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
        t= "timestamp_datetime",
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
