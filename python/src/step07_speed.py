# Import movingpandas
import movingpandas as mpd
import geopandas as gpd

from python.src.config import SPEED, TRAJECTORIES

def calculate_speed():
        """With this function speed is to be calculated in km/h between GPS
        points within each burst."""
        gps = gpd.read_file(TRAJECTORIES)
        gps # Server osm is overloaded thus cannot import output of step 6, with this line I am gonna select columns like burst id, traject id and personal ids.

    tc = mpd.TrajectoryCollection
        tc.add_speed()
        tc.add_timedelta()
    # To be used when I can read the file source: github.com/movingpandas/movingpandas-examples/blob/main/1-tutorials/2-computing-speed.ipynb