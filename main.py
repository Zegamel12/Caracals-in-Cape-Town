from tqdm import tqdm

from python.src import (
    step01_download,
    step02_extent,
    step03_osm,
    step04_trajectories,
    step05_animation,
    step06_distance,
)

# Create list for loading bar and runs
steps = [
    ("Downloading GPS data...", step01_download.download_gps_data),
    ("Creating extent...", step02_extent.create_extent),
    ("Downloading osm data...", step03_osm.download_osm_data),
    ("Creating bursts...", step04_trajectories.create_bursts),
    ("Creating first animations...", step05_animation.create_animation_map),
    ("Calculating distances...",step06_distance.calculate_distance),
]

bar = tqdm(steps, unit="step") # Source: https://github.com/tqdm/tqdm?tab=readme-ov-file#custom-integration : iterable_based
for name, step in bar:
    bar.set_description(name)
    step()