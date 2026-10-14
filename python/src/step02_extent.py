# This code was mainly written by: Silke Zeeuwen. See the commit history for a detailed contribution record.  

# Import 
import geopandas as gpd
from shapely.geometry import box

from python.src.config import ANALYSIS_CRS, EXTENT_FILE, GPS_DATA


def create_extent():
    """ Create an extent based on the gps data points. """
     # Extend area with a buffer zone in meters
    buffer_m = 200

    # Read gps points from file (step 1)
    gps_points = gpd.read_file(GPS_DATA)

    # Convert points to CRS with unit in meters
    gps_points_m = gps_points.to_crs(ANALYSIS_CRS)

    # Find minimal and maximum x- and y-cordinates
    # https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.total_bounds.html
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

    # Save it
    extent.to_file(EXTENT_FILE)

    # Clean workspace
    del buffer_m
