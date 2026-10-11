# Here put in the consistend variables, so we can quickly change them in the whole script.

from pathlib import Path

base = Path('.') # This references the root of the current directory

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
    "step12_dashboard"
]

# Create step directories and data/temp directories
for step in step_names:
    step_dir = base / "python" / "step_dirs" / step
    (step_dir / "data").mkdir(parents=True, exist_ok=True)
    (step_dir / "temp").mkdir(parents=True, exist_ok=True)

    
# Input/output files
EXTENT_FILE = (base / "python" / "step_dirs" /"step03_osm" / "data" / "extent_file.gpkg")
ROADS = (base / "python" / "step_dirs" /"step03_osm" / "data" / "roads.gpkg")
FEATURES = (base / "python" / "step_dirs" /"step03_osm" / "data" / "landuse_classes.gpkg")
TRAJECTORIES = (base / "python" / "step_dirs" /"step04_trajectories" / "data" / "s04A_GPS_burstID.gpkg")
ANIMATION = (base / "python" / "step_dirs" /"step05_animation" / "data" / "animation.html")
DISTANCE = (base / "python" / "step_dirs" /"step05_animation" / "data" / "distance.gpkg")
SPEED = (base / "python" / "step_dirs" / "step07_speed" / "data" / "s07a_speed.gpkg")

# Coordinate reference systems. Cordinates lie in UTM-zone 34S, this is tied to the EPSG:32734 https://spatialreference.org/ref/epsg/32734/
GPS_CRS = "EPSG:4326"
ANALYSIS_CRS = "EPSG:32734"

# Movebank
MOVEbank_STUDY_ID = "1832666571"

# Set Movebank username and password
username_movebank = "Jovado" 
password_movebank = "waardeloos123"

