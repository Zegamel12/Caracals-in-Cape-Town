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
    step09_visualize,
    step10_daynight,
    step11_urban,
    step13_combine,
)

# ADD STEP 9
#    step09_visualize,




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
    ("Comparing urban vs wildlands",step11_urban.compare_urban_wildland),
    ("Creating (interactive) graphs..",step09_visualize.create_figures),
    ("Running final analysis...",step13_combine.run_combined_analysis),
    ("Creating final graphs for dashboard...",step13_combine.make_question_graphs),
]



bar = tqdm(steps, unit="step") # Source: https://github.com/tqdm/tqdm?tab=readme-ov-file#custom-integration : iterable_based
for name, step in bar:
    bar.set_description(name)
    step()
