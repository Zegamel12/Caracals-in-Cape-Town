### --- Import road network ---

# https://osmnx.readthedocs.io/en/stable/user-reference.html

import osmnx as ox
import matplotlib.pyplot as plt

# Plot the network
# Import osmx and rasterio
import geopandas as gpd
import pyproj
import osmnx as ox
import rasterio #https://rasterio.readthedocs.io/en/stable/quickstart.html
<<<<<<< HEAD
from config import ANALYSIS_CRS, LANDUSE, ROADS
from extent import get_extent # if get_extent is found in step 2

# def_get_road_network(bbox):

# Example BBox [improve and move to config.py]

# Get road network
road_network = ox.graph.graph_from_bbox(bbox=bbox, network_type='drive')

# convert the road network to GeoDataFrame
nodes, roads = ox.graph_to_gdfs(road_network)

# Set CRS of the OSM data
roads=roads.to_crs(ANALYSIS_CRS)

# save the road networks
roads.to_file(ROADS, layer ="roads", driver="GPKG")

#return roads


# def get_landuse(bbox):
""" Download landuse datasets from OSM"""

# Download landuse data from OSM 
landuse = ox.features_from_bbox(bbox=bbox, tags={"landuse=Tue"} )

# Reproject landuse to Anlaysis crs
landuse = landuse.to_crs(ANALYSIS_CRS)

# save landuse data
landuse.file(LANDUSE, layer = "landuse", driver = "GPKG")

#return landuse


#return roads

