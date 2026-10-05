# Here put in the consistend variables, so we can quickly change them in the whole script.

from pathlib import Path

base = Path('.') # This references the root of your current directory

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
    step_dir = base / "step_dirs" / step
    (step_dir / "data").mkdir(parents==True, exist_ok=True)
    (step_dir / "temp").mkdir(parents==True, exist_ok=True)
    

# Input/output files



# Coordinate reference systems
GPS_CRS = "EPSG:4326"
ANALYSIS_CRS = "EPSG:xxxxx"

# Movebank
MOVEbank_STUDY_ID = "1832666571"

# Set Movebank username and password
username_movebank = "Jovado" 
password_movebank = "waardeloos123"

