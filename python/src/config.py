# This code was mainly written by: Jerom den Rooijen & Kahsu Berihu Berhe. See the commit history for a detailed contribution record.

# Here put in the consistend variables, so we can quickly change them in the whole script.

from pathlib import Path

from pathlib import Path

# Project root: Caracals-in-Cape-Town/
base = Path(__file__).resolve().parents[2]

# Step directories
step_names = [
    "step01_download",
    "step02_extent",
    "step03_osm",
    "step04_trajectories",
    "step05_animation",
    "step06_distance",
    "step07_speed",
    "step08_compare",
    "step09_visualize",
    "step10_daynight",
    "step11_urban",
    "step12_dashboard",
    "step13_combine", 
]

# Create step directories and data/temp directories
for step in step_names:
    step_dir = base / "python" / "step_dirs" / step
    (step_dir / "data").mkdir(parents=True, exist_ok=True)
    (step_dir / "temp").mkdir(parents=True, exist_ok=True)

    
# Input/output files
GPS_DATA = (base / "python" / "step_dirs" / "step01_download" / "data" / "s01a_GPS_data.gpkg")
EXTENT_FILE = (base / "python" / "step_dirs" / "step02_extent" / "data" / "s02a_gps_extent.gpkg")
ROADS = (base / "python" / "step_dirs" /"step03_osm" / "data" / "s03a_roads.gpkg")
FEATURES = (base / "python" / "step_dirs" /"step03_osm" / "data" / "s03b_landuse_classes.gpkg")
TRAJECTORIES = (base / "python" / "step_dirs" /"step04_trajectories" / "data" / "s04a_GPS_burstID.gpkg")
ANIMATION = (base / "python" / "step_dirs" /"step05_animation" / "data" / "s05a_animation.html")
DISTANCE = (base / "python" / "step_dirs" /"step06_distance" / "data" / "s06a_distance.gpkg")
SPEED = (base / "python" / "step_dirs" / "step07_speed" / "data" / "s07a_speed.gpkg")
SPEED_DISTANCE_CSV = (base / "python" / "step_dirs" / "step08_compare" / "data" / "s08a_speed_distance.csv")
SPEED_DISTANCE_MODEL = (base / "python" / "step_dirs" / "step08_compare" / "data" / "s08b_model_summary.txt")
DAY_NIGHT_CSV = (base / "python" / "step_dirs" / "step10_daynight" / "data" / "s10A_speed_distance.csv")
DAY_NIGHT_MODEL = (base / "python" / "step_dirs" / "step10_daynight" / "data" / "s10B_model_summary.txt")
DAY_NIGHT_PLOT = (base / "python" / "step_dirs" / "step10_daynight" / "data" / "s10C_day_night_scatterplot.png")
LANDSCAPE_OBSERVATIONS = (base / "python" / "step_dirs" / "step11_urban" / "data" / "s11a_landscape_observations.gpkg")
LANDSCAPE_STATISTICS = (base / "python" / "step_dirs" / "step11_urban" / "data" / "s11b_landscape_statistics.csv")
OLS_RESULTS = (base / "python" / "step_dirs" / "step11_urban" / "data" / "s11c_OLS_regression.txt")
SPEED_DISTANCE_PLOT = (base / "python" / "step_dirs" / "step11_urban" / "data" / "s11d_speed_vs_road_distance.png")
SPEED_LANDSCAPE_PLOT = (base / "python" / "step_dirs" / "step11_urban" / "data" / "s11e_speed_by_landscape.png")
MIXED_RESULTS = (base / "python" / "step_dirs" / "step11_urban" / "data" / "s11f_mixed_model.txt")
FIGURES = (base / "python" / "output" / "figures")
FIGURES.mkdir(parents=True, exist_ok=True)
DELIVERABLES = (base / "python" / "output" / "deliverables")
DELIVERABLES.mkdir(parents=True, exist_ok=True)
COMBINE_DIR = (base / "python" / "step_dirs" / "step13_combine" / "data")

# Coordinate reference systems. Cordinates lie in UTM-zone 34S, this is tied to the EPSG:32734 https://spatialreference.org/ref/epsg/32734/
GPS_CRS = "EPSG:4326"
ANALYSIS_CRS = "EPSG:32734"

#  Key Column names 
ID_COL = "individual_local_identifier"
TIME_COL = "timestamp_datetime"
KEYS = [ID_COL, TIME_COL, "burst_id"]  

# Study area and processing settings
BUFFER_M = 200
ALLOWED_INTERVALS = [1200, 7200, 10800]
TIMEZONE = "Africa/Johannesburg"
STUDY_LOCATION = {"name": "Cape Town", "region": "Western Cape", "lat": -33.9249, "lon": 18.4241}

# Movebank
MOVEbank_STUDY_ID = "1832666571"

# Set Movebank username and password
username_movebank = "Jovado" 
password_movebank = "waardeloos123"


