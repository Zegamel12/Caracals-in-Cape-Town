# Import matplotlib, geopandas and plotly
import geopandas as gpd
import matplotlib.pyplot as plt  #https://www.geeksforgeeks.org/python/how-to-import-matplotlib-in-python/
import plotly.express as px

from python.src.config import DISTANCE

### Temporary test block # s: https://docs.python.org/3/library/__main__.html
if __name__ == "__main__":
    gps = gpd.read_file(DISTANCE)

    print(len(gps))
    print(gps.columns)
    print(gps.head())
