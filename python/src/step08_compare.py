# Import pandas and statsmodels
import pandas as pd
import statsmodels.api as sm #https://www.statsmodels.org/stable/index.html
from pathlib import Path
import geopandas as gpd
import numpy as np

from python.src.config import DISTANCE, SPEED

# Prevent that sights of different animals get mixed up
KEYS = [
    "individual_local_identifier",
    "timestamp_datatime",
    "burst_id",
    ]

# Analysation function and read files
def compare_speed_to_distance():
    distance_data = gpd.read_file(DISTANCE)
    speed_data = gpd.read_file(SPEED)
