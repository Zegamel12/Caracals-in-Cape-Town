# Import matplotlib, geopandas and plotly
import geopandas as gpd
import matplotlib.pyplot as plt  #https://www.geeksforgeeks.org/python/how-to-import-matplotlib-in-python/
import plotly.express as px

from python.src.config import DISTANCE, FIGURES

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
    ax.tick_params(axis="x", rotation=-50) #S: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.tick_params.html

    # Y
    ax.set_ylabel("Number of GPS points")

    plt.tight_layout()
    
    # Save to figures dir, defined in config
    fig.savefig(FIGURES / "s09a_gps_points_per_caracal.png", dpi=150)

    plt.close()


    ### Plotly Source: https://plotly.com/python/box-plots/
    fig_px = px.box(
        gps,
        x="individual_local_identifier",
        y="distance_m",
        labels={"individual_local_identifier": "Caracal", "distance_m": "Distance to nearest road (m)"},
        title="Distance to nearest road per caracal",
    )

    # Source: https://plotly.com/python/interactive-html-export/
    fig_px.write_html(FIGURES / "s09b_distance_per_caracal.html")

    
    