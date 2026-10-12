# sources 
#https://movingpandas.readthedocs.io/en/main/api/trajectorycollection.html
#https://movingpandas.readthedocs.io/en/main/api/api/movingpandas.TrajectoryCollection.add_speed.html
#https://movingpandas.readthedocs.io/en/main/api/api/movingpandas.TrajectoryCollection.to_point_gdf.html
#https://movingpandas.readthedocs.io/en/main/api/trajectory.html

# Import movingpandas
import movingpandas as mpd
import geopandas as gpd
import pandas as pd
from python.src.config import ANALYSIS_CRS, SPEED, TRAJECTORIES

# Read input and check collumns
gps = gpd.read_file(TRAJECTORIES)
required = [
    "individual_local_identifier",
    "burst_id",
    "timestamp_datetime",
    "geometry",
]
missing= [column for column in required if column not in gps.columns]
if missing:
    raise ValueError(f"Missing columns in the trajectory data: {missing}")

# Check cordinates and timestamps
if gps.crs is None:
    raise ValueError("Trajectory data has no CRS")
gps["timestamp_datetime"] = (pd.to_datetime(
    gps["timestamp_datetime"], utc= True, errors= "raise")
    .dt.tz_localize(None)
)
gps = gps.to_crs(ANALYSIS_CRS)

# Make points in chronological order
gps= gps.sort_values(["individual_local_identifier", "burst_id", "timestamp_datetime"]
).copy()

# Give every animal their own burst_id
gps["trajectory_id"] = gps.groupby(
    ["individual_local_identifier", "burst_id"],
    sort= False,
).ngroup()

# Make trajectory of GeoDataFrame and calculate speed
TRAJECTORIES= mpd.TrajectoryCollection(
    gps,
    traj_id_col="trajectory_id",
    t= "timestamp_datetime",
)
TRAJECTORIES.add_speed(
    name= "speed_kmh",
    units=("km", "h"),
)

# Save the results
speed_data = TRAJECTORIES.to_point_gdf().reset_index()
speed_data.to_file(SPEED, layer="speed", driver="GPKG")






#def calculate_speed():
        #"""With this function speed is to be calculated in km/h between GPS
        #points within each burst."""
        #gps = gpd.read_file(TRAJECTORIES)
        #gps # Server osm is overloaded thus cannot import output of step 6, with this line I am gonna select columns like burst id, traject id and personal ids.

    #tc = mpd.TrajectoryCollection
        #tc.add_speed()
        #tc.add_timedelta()
    # To be used when I can read the file source: github.com/movingpandas/movingpandas-examples/blob/main/1-tutorials/2-computing-speed.ipynb