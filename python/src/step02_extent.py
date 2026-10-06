# Import pandas, geopandas and pyproj
from config import ANALYSIS_CRS
import pandas as pd
import geopandas as gpd
import pyproj
from pathlib import Path
from shapely.geometry import box

# Get the right file you downloaded in step 1
gps_file = Path("data/raw/gps_data.csv")
extent_file = Path("data/processed/gps_extent.geojson")

# Extend area with a buffer zone in meters
buffer_m = 1000

# Cordinates lie in UTM-zone 34S, this is tied to the EPSG:32734 https://spatialreference.org/ref/epsg/32734/
ANALYSIS_CRS = "EPSG:32734"

# Read the GPS-table 
gps_csv = pd.read_csv(gps_file)

# Convert cordinates to numerical data. 
gps_csv["location_long"] = pd.to_numeric(
    gps_csv["location_long"], errors="coerce"
)
gps_csv["location_lat"] = pd.to_numeric(
    gps_csv["location_lat"], errors="coerce"
)
gps_csv = gps_csv.dropna(
    subset=["location_long", "location_lat"]
).copy()

if gps_csv.empty:
    raise ValueError("No GPS-cordinates found in CSV-file")

# Make GPS points
gps_points = gpd.GeoDataFrame(
    gps_csv,
    geometry = gpd.points_from_xy(
        gps_csv["location_long"],
        gps_csv["location_lat"],
    ),
    crs="EPSG:32734"
)

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
).to_crs("EPSG:32734")

#