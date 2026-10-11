""" Step05_animation.py
Input : time- enabled trajectory map (plotly) straight from step04's
output : data/trajectory_animation.html -- open directory in a browser, or load into step12's dashboard.
"""
# # References
# https://plotly.com/python-api-reference/generated/plotly.express.scatter_map.html
# https://plotly.com/python/animations/
# https://plotly.com/python/tile-scatter-maps/

# Import geopandas, movingpandas and plotly.express

import geopandas as gpd
import pandas as pd
import plotly.express as px  #https://www.geeksforgeeks.org/data-visualization/using-plotly-for-interactive-data-visualization-in-python/
import time                #  https://docs.python.org/3/library/time.html#time.perf_counter

from python.src.config import ANIMATION, GPS_CRS, TRAJECTORIES


def create_animation_map():
  """ Create an interactive animation GPS animal movements. """
  

  # load step 04 data
  trajectories_data = gpd.read_file(TRAJECTORIES)
   
  # Reproject to WGS84 if not in WGS84
  trajectories_data = trajectories_data.to_crs(GPS_CRS)

  # Measure animation creation time
  start = time.perf_counter()


  # creation Animation
  fig = px.scatter_map(
    trajectories_data, 
    lat= "location_lat", 
    lon= "location_long",
    animation_frame= "timestamp_datetime",
    animation_group= "individual_local_identifier", 
    color="individual_local_identifier",
    hover_name="individual_local_identifier", 
    zoom= 9, 
    height= 700, 
    map_style = "open-street-map",
    title="Caracal movements over time"
    )
    
  print(f"Plotly animation creation: {time.perf_counter() - start:.2f} seconds")
  
  #  save GPS animation map 
  # https://plotly.com/python/interactive-html-export/
  fig.write_html(ANIMATION)
  
  return fig
  
