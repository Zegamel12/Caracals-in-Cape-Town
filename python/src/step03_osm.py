### --- Import road network ---

# https://osmnx.readthedocs.io/en/stable/user-reference.html

import osmnx as ox

# Example BBox [improve and move to config.py]
BBox = (25.35, -29.20, 25.50, -29.05)

# Get road network
road_network = ox.graph.graph_from_bbox(BBox, network_type='drive')

import matplotlib.pyplot as plt

# Plot the network
ox.plot.plot_graph(road_network)
