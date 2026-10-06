import os
#import functions.py as functions

#if not os.path.exists(directory):
 #   os.makedirs(directory)


from python.src.step03_osm import download_osm_data
from python.src.step05_animation import create_animation_map
from python.src.step06_distance import calculate_distance

# Step03: donwload OSM data
raods, features = download_osm_data(bbox)

#  Step005: create animation map
fig = create_animation_map()
fig.show()

# Step06: calculate distance

distance_data = calculate_distance()