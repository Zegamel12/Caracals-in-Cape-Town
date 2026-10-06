# Import geopandas, movingpandas and plotly.express
from main import gps_data
from python.src.step02_extent import gps_points
import geopandas as gpd
import movingpandas as mpd
import plotly.express as px #https://www.geeksforgeeks.org/data-visualization/using-plotly-for-interactive-data-visualization-in-python/

from config import GPS_CRS
from step01_download import gps_gdf

# def create_animation_map(gps_gdf):
  #https://plotly.com/python-api-reference/generated/plotly.express.scatter_map.html
  #https://plotly.com/python/animations/
  # https://plotly.com/python/tile-scatter-maps/

fig = px.scatter_map(gps_gdf, lat= gps_gdf.geometry.y, lon=gps_gdf.geometry.x, color=...., hover_name=".....", zoom=.., height= ..,)

  # Set map Style

fig.update_layout(
    hovermode='closest',
    map=dict(
        bearing=0,
        center=go.layout.map.Center(
            lat=45,
            lon=-73
        ),
        pitch=0,
        zoom=5
    )
)

fig.show()

# return fig
