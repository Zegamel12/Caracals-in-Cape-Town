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
# - GeoDataFrame to_file:        https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_file.html
# - GeoPackage cannot hold lists: https://www.geopackage.org/spec/
# - geopandas mapping:           https://geopandas.org/en/stable/docs/user_guide/mapping.html
# - numpy.select:                https://numpy.org/doc/stable/reference/generated/numpy.select.html
# - pandas Series.isin:          https://pandas.pydata.org/docs/reference/api/pandas.Series.isin.html
# - matplotlib legend handles:   https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html
# - matplotlib savefig:          https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html


#import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from pyrosm import OSM, get_data_by_bbox

# from python.src.step02_extent import extent -> bracket for testing of main.py
from python.src.config import (
    ANALYSIS_CRS,
    EXTENT_FILE,
    FEATURES,
    FIGURES,
    GPS_CRS,
    ROADS,
)

SOURCE_DATA = "Data: © OpenStreetMap contributors (ODbL), downloaded via pyrosm/Geofabrik"
 
# OSM tags to extract (https://wiki.openstreetmap.org/wiki/Key:landuse)
TAGS = {
        "landuse": ["residential", "commercial", "industrial", "retail", "grass", "forest",
                  "meadow", "farmland", "orchard", "vineyard"],
        "leisure": ["park", "nature_reserve", "garden"],
        "natural": ["wood", "scrub", "grassland"],
        }

# How OSM values map to classes. Farmland/orchards/vineyards are human-made, so they
# get their own class instead of "natural" (otherwise wildland would contain agriculture).
URBAN_LANDUSE = {"residential", "commercial", "industrial", "retail"}
NATURAL_LANDUSE = {"forest"}
AGRICULTURE_LANDUSE = {"farmland", "orchard", "vineyard"}
GREEN_LANDUSE = {"grass", "meadow"}
GREEN_LEISURE = {"park", "garden"}
NATURAL_LEISURE = {"nature_reserve"}
NATURAL_NATURAL = {"wood", "scrub", "grassland"}

def read_extent_bbox(extent_file=EXTENT_FILE):
    """ return the study area bounding box (west, soth, east, north) in WGS84 """
    
    if not extent_file.exists():
        raise FileNotFoundError(f"{extent_file} not found, first run Step02"
        )
    # Source: https://geopandas.org/en/stable/docs/reference/api/geopandas.read_file.html
    extent = gpd.read_file(extent_file)
    if extent.empty:
        raise ValueError("Step02-file does not contain area")
    if extent.crs is None:
        raise ValueError("Step 01 extent has no defined CRS.")
    
     # Source: https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html
    return list(extent.to_crs(GPS_CRS).total_bounds)

def extract_roads(osm, crs=ANALYSIS_CRS):
    """ extract the driving road networks as lines in the given CRS."""
    # Source: https://pyrosm.readthedocs.io/en/stable/reference.html (OSM.get_network)
    roads = osm.get_network(network_type="driving", nodes=False)
    if roads is None or roads.empty:
        raise ValueError("No roads were found in the study area")
    roads = roads.to_crs(crs).reset_index(drop=True)
    
    # GeoPackage cannot hold lists, so store the highway type as text
    # Source: https://www.geopackage.org/spec/
    roads["highway"] = roads["highway"].astype(str)
    keep = [c for c in ["highway", "name", "length", "geometry"] if c in roads.columns]
    return roads[keep]

def classify_features(features):
    """ add an 'osm_class' column: urban /natural / agriculture / urban_green / others.
    np.select takes the first matching condition, so the order is the priority.
    """
    empty=pd.Series(pd.NA, index=features.index, dtype="object")
    landuse= features.get("landuse", empty)
    leisure = features.get("leisure", empty)
    natural = features.get("natural", empty)

    # Source: https://pandas.pydata.org/docs/reference/api/pandas.Series.isin.html
    conditions = [
        landuse.isin(URBAN_LANDUSE),
        landuse.isin(NATURAL_LANDUSE) | leisure.isin(NATURAL_LEISURE) | natural.isin(NATURAL_NATURAL),
        landuse.isin(AGRICULTURE_LANDUSE),
        landuse.isin(GREEN_LANDUSE) | leisure.isin(GREEN_LEISURE),
    ]
    # Source: https://numpy.org/doc/stable/reference/generated/numpy.select.html
    features["osm_class"] = np.select(
        conditions, ["urban", "natural", "agriculture", "urban_green"], default="others"
    )
    return features


def extract_landuse(osm, crs=ANALYSIS_CRS):
    """Extract land-use/leisure/natural polygons, classified, in the given CRS."""
    # Source: https://pyrosm.readthedocs.io/en/stable/reference.html (get_data_by_custom_criteria)
    features = osm.get_data_by_custom_criteria(
        custom_filter=TAGS,
        osm_keys_to_keep=list(TAGS),
        filter_type="keep",
        keep_nodes=False,
    )
    if features is None or features.empty:
        raise ValueError("No features matching the OSM tags were found")
 
    features = features[features.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
    if features.empty:
        raise ValueError("No polygon features were found")
 
    features = classify_features(features).to_crs(crs)
    keep = [c for c in ["landuse", "leisure", "natural", "osm_class", "geometry"] if c in features.columns]
    return features[keep].reset_index(drop=True)

def finish_map(ax, title):
    """Add the elements every map needs: title, axis labels, north arrow, scale bar, source."""
    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Easting (m, UTM zone 34S)")
    ax.set_ylabel("Northing (m, UTM zone 34S)")
    #add_north_arrow(ax)
    #add_scale_bar(ax)
    ax.text(0.99, 0.01, SOURCE_DATA, transform=ax.transAxes, ha="right", va="bottom", fontsize=7)

def plot_roads(roads, path):
    """Save a map of the road network."""
    fig, ax = plt.subplots(figsize=(10, 7))
    roads.plot(ax=ax, linewidth=0.4, color="black")
    # Source: https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html
    ax.legend(handles=[Line2D([0], [0], color="black", lw=1, label="Driving roads")], loc="upper left")
    finish_map(ax, "OSM road network of the study area")
    # Source: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
 
 
def plot_landuse(features, path):
    """Save a map of the classified land-use polygons."""
    fig, ax = plt.subplots(figsize=(10, 7))
    # Source: https://geopandas.org/en/stable/docs/user_guide/mapping.html
    features.plot(ax=ax, column="osm_class", legend=True, linewidth=0.2,
                  legend_kwds={"title": "Land-use class", "loc": "upper left"})
    finish_map(ax, "OSM land-use classes of the study area")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

def download_osm_data(force=False):
    """Download and save OSM roads and land use for the step02 extent.
 
    Skips the download when both output files already exist (unless force=True).
    Returns (features, roads).
    """
    if not force and ROADS.exists() and FEATURES.exists():
        print("OSM data already downloaded, reading cached files.")
        return (gpd.read_file(FEATURES, layer="landuse_classes"),
                gpd.read_file(ROADS, layer="roads"))
 
    bbox = read_extent_bbox()
    print(f"OSM bounding box: {bbox}")
 
    # Download a regional extract and only read the study-area bounding box from it
    # Source: https://pyrosm.readthedocs.io/en/latest/api/pyrosm.get_data_by_bbox.html
    pbf_file = get_data_by_bbox(bbox=bbox)
    osm = OSM(pbf_file, bounding_box=bbox)
 
    # Source: https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_file.html
    roads = extract_roads(osm)
    roads.to_file(ROADS, layer="s03a_roads", driver="GPKG")
 
    features = extract_landuse(osm)
    print(features["osm_class"].value_counts())
    features.to_file(FEATURES, layer="landuse_classes", driver="GPKG")
 
    FIGURES.mkdir(parents=True, exist_ok=True)
    plot_roads(roads, FIGURES / "s03a_roads.png")
    plot_landuse(features, FIGURES / "s03b_landuse_classes.png")
    return features, roads
    