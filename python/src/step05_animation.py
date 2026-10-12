""" Step05_animation.py
Input : step04 trajectories (GeoPackage with one Point per GPS)
output : an HTML file with a time enabled (plotly) -- open directory in a browser, or load into step12's dashboard.
"""
# # References
# - plotly acatter_map: https://plotly.com/python-api-reference/generated/plotly.express.scatter_map.html
# - plotly animations :https://plotly.com/python/animations/
# - plotly title map : https://plotly.com/python/tile-scatter-maps/
# - plotly HTML export (include_plotlyjs, auto_play): https://plotly.com/python/interactive-html-export/
# - time.perf_counter: https://docs.python.org/3/library/time.html#time.perf_counter
# - plotly interactive : https://www.geeksforgeeks.org/data-visualization/using-plotly-for-interactive-data-visualization-in-python/
# - pandas Period / to_period: https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.to_period.html

from pathlib import Path
import time                

import geopandas as gpd
import pandas as pd
import plotly.express as px  

from python.src.config import ANIMATION, GPS_CRS, TRAJECTORIES


def create_animation_map():
  """ Create an interactive animation GPS animal movements. 
  length of one aniimation frame (frame_freq: one frame per "h" (hour), "D" (day), "W" (week) or "M" (month)).
  One frame per timestamp would be tens of thousands of frames and plotly would not finish.
  """
  frame_freq = "W" # 123 unique values found

  # 1. load step 04 trajectory data
  trajectories_data = gpd.read_file(TRAJECTORIES)
   
  # 2. Reproject to WGS84 if not in WGS84
  trajectories_data = trajectories_data.to_crs(GPS_CRS)

   # 3. Remove records without an animal identifier.
  trajectories_data = trajectories_data.dropna(subset=["individual_local_identifier"])

  # 4. start the timer to measure animation creation time
  start = time.perf_counter()

  # 5. Make the frame label: the week(or day/month)each fix belongs to 
  trajectories_data["frame"]= (
    trajectories_data["timestamp_datetime"]
    .dt.to_period(frame_freq)
    .dt.start_time
    .dt.strftime("%Y-%m-%d")
  )
  
  # 6. Sort by frame so the animation plays in time order
  trajectories_data= trajectories_data.sort_values("frame")
  
  # 7. creation the interaction animation map
  fig = px.scatter_map(
    trajectories_data, 
    lat="location_lat",
    lon="location_long",
    animation_frame="frame",
    animation_group="individual_local_identifier",
    color="individual_local_identifier",
    hover_name="individual_local_identifier",
    center = {
      "lat": (trajectories_data["location_lat"].median()),
      "lon": trajectories_data["location_long"].median()
    },
    zoom=9,
    height=800,
    map_style="carto-positron",
    title="Caracal movements over time",
  )

    
  print(f"Plotly animation creation: {time.perf_counter() - start:.2f} seconds")
  
  # 8. savand show the animated map as HTML file 
  # https://plotly.com/python/interactive-html-export/
  fig.write_html(ANIMATION, include_plotlyjs=True, auto_play=False)

  print(f"Animation saved to: {ANIMATION.resolve()}")


  fig.show()
  
  return fig
  
