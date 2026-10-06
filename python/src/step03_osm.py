
from config import ANALYSIS_CRS, FEATURES, ROADS, GPS_CRS
# from python.src.step02_extent import extent
from python.src.step01_download import gps_gdf

import osmnx as ox
import matplotlib.pyplot as plt
import geopandas as gpd
import pyproj
import rasterio #https://rasterio.readthedocs.io/en/stable/quickstart.html


def download_osm_data(bbox):

    # https://osmnx.readthedocs.io/
    # OSMnx user reference:
    # https://osmnx.readthedocs.io/en/stable/user-reference.html
    
    # Boundary box (bbox) 
    
    # option 1 from step 2
    # extent_wgs84= extent.to_crs(GPS_CRS)
    # minx, ymin, xmax, ymax = extent_wgs84.total_bounds
    # bbox= (minx, ymin, xmax, ymax)

    #option2 form step 1
    bbox= gps_gdf.geometry.total_bounds

    # 1. Download road network
    road_network = ox.graph.graph_from_bbox(
        bbox=bbox, 
        network_type='drive'
        )

    # convert the road network to GeoDataFrame
    nodes, roads = ox.graph_to_gdfs(road_network)

    # Reproject roads to Analysis CRS
    roads=roads.to_crs(ANALYSIS_CRS)

    # check raw data
    print(f"Road features: {len(roads)}")
    print(f"Road CRS: {roads.crs}")
    roads.plot()

    # save the road networks
    roads.to_file(ROADS, layer ="roads", driver="GPKG")

    # 2. Download landuse and leisure features

    tags = {"landuse":["residential", "commercial", "industrial", "retail", "grass", "forest"],
            "leisure":["park", "nature_reserve"]
            }

    features = ox.features_from_bbox(bbox=bbox, tags=tags )

    # Reproject landuse to Anlaysis crs
    features = features.to_crs(ANALYSIS_CRS)

    #check feature data
    print(f"OSM features: {len(features)}")
    print(f"OSM CRS: {features.crs}")
    print("OSM columns: {features.columns}")

    # save landuse data
    features.to_file(FEATURES, layer ="urban_boundaries", driver = "GPKG")

    return features, roads


