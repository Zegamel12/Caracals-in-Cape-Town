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

    counts = gps["individual_local_identifier"].value_counts()
    print(counts)

    # Create plot size
    fig, ax = plt.subplots(figsize = (10,6))
    
    # Title
    ax.set_title("GPS points per caracal.")

    # Give variables to x and y axes.
    ax.bar(counts.index, counts.values)
    
    # X
    ax.set_xlabel("Caracal")
    ax.tick_params(axis="x", rotation=-50)

    # Y
    ax.set_ylabel("Number of GPS points")

    plt.tight_layout()

    plt.show()