from python.src import (
    step01_download,
    step02_extent,
    step03_osm,
    step04_trajectories,
    step05_animation,
    step06_distance,
)

step01_download.download_gps_data()
step02_extent.create_extent()
step03_osm.download_osm_data()
step04_trajectories.create_bursts()
step05_animation.create_animation_map()
step06_distance.calculate_distance()
