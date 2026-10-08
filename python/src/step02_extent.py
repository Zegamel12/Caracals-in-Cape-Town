# Import 
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box

from python.src.config import ANALYSIS_CRS


def create_extent():
    # Get the right file you downloaded in step 1
    gps_file = Path("python/step_dirs/step01_download/data/s01A_GPS_data.gpkg")
    extent_file = Path("python/step_dirs/step02_extent/data/s02A_gps_extent.gpkg")

    # Extend area with a buffer zone in meters
    buffer_m = 200

    # If file does not exists, run step01
    if not gps_file.exists():
        raise FileNotFoundError(
            "GPS-file not found: first run Step01"
        )
    # Read gps points from file
    gps_points = gpd.read_file(gps_file)
    if gps_points.empty:
        raise ValueError("GPS-file does not contain GPS-points")

    # Convert points to CRS with unit in meters
    gps_points_m = gps_points.to_crs(ANALYSIS_CRS)

    # Find minimal and maximum x- and y-cordinates
    min_x, min_y, max_x, max_y = gps_points_m.total_bounds

    # Make box of area with buffer
    gps_rectangle = box(min_x, min_y, max_x, max_y)
    buffered_extent = gps_rectangle.buffer(buffer_m)

    # Convert to GeoDataFrame
    extent= gpd.GeoDataFrame(
        {"name":["gps_extent"]},
        geometry=[buffered_extent],
        crs = ANALYSIS_CRS,
    )
    # save it
    extent_file.parent.mkdir(parents=True, exist_ok=True)
    extent.to_file(extent_file, driver= "GPKG")
