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

import time
from pathlib import Path

import geopandas as gpd
import pandas as pd
import plotly.express as px

from python.src.config import ANIMATION, ID_COL, TRAJECTORIES


def load_points(path = TRAJECTORIES, frame_freq = "W"):
  """ Read the required columns only and add a frame label(day/week/month 
  (length of one aniimation frame (frame_freq: one frame per "h" (hour), "D" (day), "W" (week) or "M" (month))).
  One frame per timestamp would be tens of thousands of frames and plotly would not finish.
  """

  # 1. load step 04 trajectory data
  # Source: https://geopandas.org/en/stable/docs/reference/api/geopandas.read_file.html
  points = gpd.read_file(
    path, 
    columns = [ID_COL, "timestamp_datetime", "location_long", "location_lat"],
    ignore_geometry=True
    ).dropna(subset=[ID_COL, "timestamp_datetime"])
   
  # Source: https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html
  times = pd.to_datetime(points["timestamp_datetime"], utc=True).dt.tz_localize(None)
  # Source: https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.to_period.html
  points["frame"] = times.dt.to_period(frame_freq).dt.start_time.dt.strftime("%Y-%m-%d")
  return points.sort_values("frame")

def create_animation_map(frame_frq ="W", output = ANIMATION):
  """ Create and save the interactive animation of Animal movements."""
  points= load_points(frame_freq=frame_frq)

  # start the timer to measure animation creation time
  # Source: https://docs.python.org/3/library/time.html#time.perf_counter
  start = time.perf_counter()

  # several fixes per animal share a frame, and plotly needs
  # Therefore, a unique row per group and frame to morph between frames.
  # Source: https://plotly.com/python-api-reference/generated/plotly.express.scatter_map.html

  fig = px.scatter_map(
    points, 
    lat="location_lat",
    lon="location_long",
    animation_frame="frame",
    color=ID_COL,
    hover_name=ID_COL,
    center = {
      "lat": (points["location_lat"].median()),
      "lon": points["location_long"].median()
    },
    zoom=9,
    height=800,
    map_style="carto-positron",
    title="Caracal movements over time (basemap: CARTO, @ OpenStreetMAp contribution)",
    labels={ID_COL: "Carcal", "frame": "Period starting"},
  )
    
  print(f"Plotly animation creation: {time.perf_counter() - start:.2f} seconds")
  
  # 8. savE and show the animated map as HTML file 
  # https://plotly.com/python/interactive-html-export/
  # "cdn" keeps the HTML small; needs internet to view
  
  fig.write_html(output, include_plotlyjs=True, auto_play=False)

  print(f"Animation saved to: {Path(output).resolve()}")

  # fig.show()
  
  return fig
  
