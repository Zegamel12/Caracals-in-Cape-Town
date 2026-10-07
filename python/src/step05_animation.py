# Import geopandas, movingpandas and plotly.express

from python.src.config import GPS_CRS,TRAJECTORIES,ANIMATION

import geopandas as gpd
import pandas as pd
import plotly.express as px #https://www.geeksforgeeks.org/data-visualization/using-plotly-for-interactive-data-visualization-in-python/

def create_animation_map():
  """ Create an interactive animation GPS animal movements. """
  # https://plotly.com/python-api-reference/generated/plotly.express.scatter_map.html
  # https://plotly.com/python/animations/
  # https://plotly.com/python/tile-scatter-maps/

  # load step 04 data
  trajectories_data = gpd.read_file(TRAJECTORIES)
   
  # Reproject to WGS84 if not in WGS84
  trajectories_data = trajectories_data.to_crs(GPS_CRS)


  # creation Animation
  fig = px.scatter_map(
    trajectories_data, 
    lat= "location_lat", 
    lon= "location_long",
    animation_frame= "timestamp_datetime",
    animation_group= "individual_local_identifier", 
    color="individual_local_identifier",
    hover_name="individual_local_identifier", 
    zoom= 10, 
    height= 700, 
    title="GPS Animal Movement"
    )
    
  # USE OpenStreetMapp as backgrround map
  fig.update_layout(
    map_style = "open-street-map"
    )
    
  #  save GPS animation map 
  # https://plotly.com/python/interactive-html-export/
  fig.write_html(ANIMATION)
  
  return fig
  
