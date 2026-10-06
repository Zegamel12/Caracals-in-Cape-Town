### --- Import road network ---

# https://osmnx.readthedocs.io/en/stable/user-reference.html

from config import ANALYSIS_CRS
import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio #https://rasterio.readthedocs.io/en/stable/quickstart.html

from config import ANALYSIS_CRS
from extent import get_extent # if get_extent is found in step 2

# def_get_road_network(bbox):
# Example BBox [improve and move to config.py]
# bbox  # (extent from step 2)

# Get road network
road_network = ox.graph.graph_from_bbox(bbox=bbox, network_type='drive')

# convert the road network to GeoDataFrame
nodes, roads = ox.graph_to_gdfs(road_network)

# Set CRS of the OSM data
roads=roads.to_crs(ANALYSIS_CRS)

# save the road networks
roads.to_file(ROADS, layer ="roads", driver="GPKG")

#return roads



