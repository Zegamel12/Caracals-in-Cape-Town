### --- Import road network ---

# https://osmnx.readthedocs.io/en/stable/user-reference.html

import osmnx as ox
import matplotlib.pyplot as plt
import geopandas as gpd
import pyproj
import rasterio #https://rasterio.readthedocs.io/en/stable/quickstart.html

from config import ANALYSIS_CRS, LANDUSE, ROADS, GPS_CRS
from python.src.step02_extent import extent



# def_get_road_network(bbox):

# Example BBox [improve and move to config.py]
extent_wgs84= extent.to_crs(GPS_CRS)
minx, ymin, xmax, ymax = extent_wgs84.total_bounds
bbox= (minx, ymin, xmax, ymax)

# Get road network
road_network = ox.graph.graph_from_bbox(bbox=bbox, network_type='drive')

# convert the road network to GeoDataFrame
nodes, roads = ox.graph_to_gdfs(road_network)

# Set CRS of the OSM data
roads=roads.to_crs(ANALYSIS_CRS)

# save the road networks
roads.to_file(ROADS, layer ="roads", driver="GPKG")


# def get_landuse(bbox):
""" Download landuse datasets from OSM"""

# Download landuse data from OSM 
landuse = ox.features_from_bbox(bbox=bbox, tags={"landuse":Tue} )

# Reproject landuse to Anlaysis crs
landuse = landuse.to_crs(ANALYSIS_CRS)

# save landuse data
landuse.to_file(LANDUSE, layer = "landuse", driver = "GPKG")

#return landuse, roads


