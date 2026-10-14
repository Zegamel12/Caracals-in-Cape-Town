# Import 
import geopandas as gpd
from shapely.geometry import box

from python.src.config import ANALYSIS_CRS, EXTENT_FILE, GPS_DATA


def create_extent():
    """ Create an extent based on the gps data points. """
    # Get the right file you downloaded in step 1
    extent_file = EXTENT_FILE

    # Extend area with a buffer zone in meters
    buffer_m = 200

    # Read gps points from file
    gps_points = gpd.read_file(GPS_DATA)

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

    # Clean workspace
    del buffer_m
