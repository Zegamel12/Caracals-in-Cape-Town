""" Download OPenStreetMap data for extent of study area made in step02 with pyrosm (.dbf)
   1. The road network  -> distance to road
   2. Land use / leisure / natural polygons, classified as urban / natural / urban_green
               -> Urban Vs Non Urban(Wildland) comparison.

   Input : step02 extent (Geopackage)
   Output : roads (ROADS) and classified landuse polygones(FEATURES), both in ANLAYSIS_CRS
"""
# References
# - pyrosm reference:        https://pyrosm.readthedocs.io/en/stable/reference.html
# - pyrosm get_data_by_bbox: https://pyrosm.readthedocs.io/en/latest/api/pyrosm.get_data_by_bbox.html
# - pyrosm downloading data: https://pyrosm.readthedocs.io/en/latest/downloading_data.html
# - pyrosm FAQ:              https://pyrosm.readthedocs.io/en/latest/faq.html
# - Geofabrik extracts:      https://download.geofabrik.de/
# - OSM tags: https://wiki.openstreetmap.org/wiki/Key:landuse
#             https://wiki.openstreetmap.org/wiki/Key:leisure
#             https://wiki.openstreetmap.org/wiki/Key:natural
# - numpy.select:            https://numpy.org/doc/stable/reference/generated/numpy.select.html
# - GeoPackage (no lists):   https://www.geopackage.org/spec/
# - OSM license (ODbL):      https://www.openstreetmap.org/copyright
# - Course tutorial Python Vector: https://geoscripting-wur.github.io/PythonVector/



# Import

import osmnx as ox
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyrosm import OSM, get_data_by_bbox


# from python.src.step02_extent import extent -> bracket for testing of main.py

from python.src.config import (
    ANALYSIS_CRS,
    FEATURES,
    GPS_CRS,
    ROADS,
    FIGURES,
    EXTENT_FILE,
)

ox.settings.log_console = True


def download_osm_data():
    """ Download OSM roads and landuse for step02 extent. """
    
    # 1.  Read the existing step02 buffered extent and define OSM tags 
    extent_file = EXTENT_FILE

    if not extent_file.exists():
        raise FileNotFoundError(f"{extent_file} not found, first run Step02"
        )

    extent = gpd.read_file(extent_file)
    if extent.empty:
        raise ValueError("Step02-file does not contain area")
    if extent.crs is None:
        raise ValueError("Step 01 extent has no defined CRS.")

    # Build WGS84 extent polygon and bbox for PBF downlod (minx, miny, maxx, maxy)
    extent_wgs84 = extent.to_crs(GPS_CRS) 
    #extent_mask = extent_wgs84.union_all()

    # Bounds order: west, south, east, north.
    bbox = tuple(extent_wgs84.total_bounds)
    print(f"OSM bounding box:{bbox}")
    
    # 2.Define OSM tags and classification groups

    tags = {"landuse":["residential", "commercial", "industrial", "retail", "grass", "forest", 
                       "meadow", "farmland", "orchard", "vineyard"],
            "leisure":["park", "nature_reserve", "garden"],
            "natural": ["wood", "scrub", "grassland"]
            }
    # How each OSM value is classed. Farmland, orchards and vineyards are human-made, 
    # so they get their own class instead of "natural": 
    # otherwise the wildland group would contain agriculture.
    
    urban_landuse = {"residential", "commercial", "industrial", "retail"}
    natural_landuse = {"forest"}
    agriculture_landuse = {"farmland", "orchard", "vineyard"}
    green_landuse = {"grass", "meadow"}
    green_leisure = {"park", "garden"}
    natural_leisure = {"nature_reserve"}
    natural_natural = {"wood", "scrub", "grassland"}
    
    
    # 3.Download regional OSM extract with pyrosm
    # https://pyrosm.readthedocs.io/en/latest/api/pyrosm.get_data_by_bbox.html
    
    pbf_file = get_data_by_bbox(bbox = bbox)
    osm = OSM(pbf_file)

    # Extract roads network and reproject to Analysis crs
    # https://pyrosm.readthedocs.io/en/stable/reference.html
    roads = osm.get_network(network_type= "driving", 
             nodes = False
             ).to_crs(ANALYSIS_CRS
             ).reset_index(drop=True)

  

    # Convert 'Highway' values to strings for Geopackage compatibilty
    #  Source: GeoPackage cannot hold lists, https://www.geopackage.org/spec/
    #  roads["highway"].dtype()
    roads["highway"] = roads["highway"].astype(str)
    roads = roads[[column 
            for column in ["highway", "name", "length", "geometry"] 
            if column in roads.columns]
            ]

   # check raw data
   # print(f"Road features: {len(roads)}")
   # print(f"Roads_cliped CRS: {roads.crs}")
   # print("roads columns:", list(roads.columns))
   # roads.plot()

    # save the road networks
    roads.to_file(ROADS, layer ="roads", driver="GPKG")

    # 2.Extract and classify lanuse /leisure /natural areas
    # osm_keys_to_keep makes sure the tag columns exist in the result. 
    features = osm.get_data_by_custom_criteria(
        custom_filter = tags,
        osm_keys_to_keep =list(tags),
        filter_type = "keep",
        keep_nodes = False
    )

    if features is None or features.empty:
        raise ValueError("No features matching the OSM tags were found")

    # retain polygon areas only.
    features = features[features.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
    if features.empty:
        raise ValueError("No polygon features were found.") 


    # check feature data
    # print(f"OSM features: {len(features)}")
    # print(f"OSM CRS: {features.crs}")
    # print(f"OSM columns: {features.columns}")
    # features.plot()

    # read tag columns: using missing valuesif a column is absent.
    landuse = features.get("landuse", pd.Series(pd.NA, index=features.index, dtype="object"))
    leisure = features.get("leisure", pd.Series(pd.NA, index=features.index, dtype="object"))
    natural = features.get("natural", pd.Series(pd.NA, index=features.index, dtype="object"))

    
    # Classify features: np.select takes the FIRST matching condition, so the order is the priority.
    # https://numpy.org/doc/stable/reference/generated/numpy.select.html
    conditions = [
        landuse.isin(urban_landuse),
        (
            landuse.isin(natural_landuse)
            | leisure.isin(natural_leisure)
            | natural.isin(natural_natural)
        ),

        landuse.isin(agriculture_landuse),
        (
            landuse.isin(green_landuse)
            | leisure.isin(green_leisure)
        ),      
    ]

    features["osm_class"] = np.select(
        conditions, ["urban", "natural", "agriculture", "urban_green"],
        default = "others"
        )
    # retain the required output fields add reproject to Anlaysis crs
    # https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html
    
    features = features.to_crs(ANALYSIS_CRS)

    features = features[
        [
            column 
            for column in ["landuse", "leisure", "natural", "osm_class", "geometry"]
            if column in features.columns
        ]
    ]
    
    print(f"OSM features: {len(features)}")
    print(f"OSM CRS: {features.crs}")
    print(features["osm_class"].value_counts())
    
    # save landuse data
    features.to_file(FEATURES, layer ="landuse_classes", driver = "GPKG")

    # Visualisation of results
     # 1. plot roads
    fig,ax = plt.subplots(figsize=(10,6))
    roads.plot(ax=ax, linewidth = 0.4)
    ax.set_title("OSM road network")
    ax.set_axis_off()
    fig.savefig(FIGURES / "s03a_roads.png", dpi=150)
    plt.close(fig)

    # 2. plot landuse classes
    fig,ax = plt.subplots(figsize=(10,6))
    features.plot(ax=ax, linewidth = 0.4)
    ax.set_title("OSM landuse classes")
    ax.set_axis_off()
    fig.savefig(FIGURES / "s03b_landuse_classes.png", dpi=150)
    plt.close(fig)
    
    return features, roads

# download_osm_data() -> bracket for testing of main.py
