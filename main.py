from tqdm import tqdm

from python.src import (
    step01_download,
    step02_extent,
    step03_osm,
    step04_trajectories,
    step05_animation,
    step06_distance,
    step07_speed,
    step08_compare,
    step10_daynight,
)

# ADD STEP 9, 11 AND 12 !!!!!!!!!!!!!!!!!
#    step09_visualize,
#    step11_urban,
#    step12_dashboard,


# Create list for loading bar and runs
steps = [
    ("Downloading GPS data...", step01_download.download_gps_data),
    ("Creating extent...", step02_extent.create_extent),
    ("Downloading osm data...", step03_osm.download_osm_data),
    ("Creating bursts...", step04_trajectories.create_bursts),
    ("Creating first animations...", step05_animation.create_animation_map),
    ("Calculating distances...",step06_distance.calculate_distance),
    ("Calculating speed...",step07_speed.calculate_speed),
    ("Comparing speed vs distance...",step08_compare.compare_speed_to_distance),
    ("Comparing influence day vs night...",step10_daynight.day_night_analysis),
]

# ADD STEP 9, 11 AND 12 !!!!!!!!!!!!!!!!!
# ("Visualizing...",step09_visualize.),


bar = tqdm(steps, unit="step") # Source: https://github.com/tqdm/tqdm?tab=readme-ov-file#custom-integration : iterable_based
for name, step in bar:
    bar.set_description(name)
    step()
