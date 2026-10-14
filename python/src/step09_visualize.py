# Import matplotlib, geopandas and plotly
import geopandas as gpd
import matplotlib.pyplot as plt  #https://www.geeksforgeeks.org/python/how-to-import-matplotlib-in-python/
import pandas as pd
import plotly.express as px

from python.src.config import DISTANCE, FIGURES, ID_COL, SPEED, SPEED_DISTANCE_CSV
from python.src.step06_distance import LABELS, add_distance_class


def plot_points_per_caracal(gps):
    """Bar chart with number of GPS points per caracal."""
    # Count gps points per caracal
    counts = gps[ID_COL].value_counts()

    # Create plot size
    fig, ax = plt.subplots(figsize = (10,6))

    # Title
    ax.set_title("GPS points per caracal")

    # Give variables to x and y axes.
    ax.bar(counts.index, counts.values)

    # X
    ax.set_xlabel("Caracal")
    ax.tick_params(axis="x", rotation=90) #S: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.tick_params.html

    # Y
    ax.set_ylabel("Number of GPS points")

    plt.tight_layout()

    # Save to figures dir, defined in config. Source: https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.savefig.html
    fig.savefig(FIGURES / "s09a_gps_points_per_caracal.png", dpi=150)

    plt.close(fig)    

def plot_distance_per_caracal(gps):
    """Interactive boxplot of the distance to the nearest road per caracal."""
    fig_px = px.box(
        gps,
        x=ID_COL,
        y="distance_m",
        labels={ID_COL: "Caracal", "distance_m": "Distance to nearest road (m)"},
        title="Distance to nearest road per caracal",
    )

    # Save as html. Source: https://plotly.com/python/interactive-html-export/
    fig_px.write_html(FIGURES / "s09b_distance_per_caracal.html")


### Speed distribution (step 7 data)
def plot_speed_distribution(speed):
    """Histogram of speed. Logaritmic y axis because most values are around zero mark."""
    # Create plot size
    fig, ax = plt.subplots(figsize = (10,6))

    # Title
    ax.set_title("Distribution of caracal speed")

    # Give variables to the histogram: 50 bars. Source: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.hist.html
    ax.hist(speed["speed_kmh"].dropna(), bins=50)

    # X
    ax.set_xlabel("Speed (km/h)")

    # Y, with log scale. Source: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_yscale.html
    ax.set_ylabel("Number of GPS points (log scale)")
    ax.set_yscale("log")

    plt.tight_layout()

    # Save to figures dir, defined in config
    fig.savefig(FIGURES / "s09c_speed_distribution.png", dpi=150)

    plt.close(fig)

### Speed per distance class (step 8 data)
def plot_speed_per_distance_class(speed_distance):
    """Boxplot of speed per distance class."""
    # Sort from close to far, so classes appear in theright order
    speed_distance = speed_distance.sort_values("distance_m")

    # Make list with speeds of each distance class
    groups = []
    for label in LABELS:
        speeds = speed_distance[speed_distance["distance_class"] == label]["speed_kmh"]
        groups.append(speeds)

    # Create size of plot
    fig, ax = plt.subplots(figsize = (10,6))

    # Title
    ax.set_title("Speed per distance class to the nearest road")

    # Boxplot without outliers, otherwise the boxes are invisible Source: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.boxplot.html
    ax.boxplot(groups, tick_labels=LABELS, showfliers=False)

    # X
    ax.set_xlabel("Distance to nearest road")

    # Y
    ax.set_ylabel("Speed (km/h)")

    plt.tight_layout()

    #Save to figures dir, defined in config
    fig.savefig(FIGURES / "s09d_speed_per_distance_class.png", dpi=150)

    plt.close(fig)

    ##Same boxplot interactive source: https://plotly.com/python/box-plots/
    fig_px = px.box(
        speed_distance,
        x="distance_class",
        y="speed_kmh",
        points=False,
        labels={"distance_class": "Distance to nearest road", "speed_kmh": "Speed (km/h)"},
        title="Speed per distance class to the nearest road",
    )

    # Save as html
    fig_px.write_html(FIGURES / "s09e_speed_vs_distance.html")


def create_figures():
    #Load data from s06, s07 and s08
    gps = gpd.read_file(DISTANCE)
    speed = gpd.read_file(SPEED)
    speed_distance = pd.read_csv(SPEED_DISTANCE_CSV)

    #Adding classes to step 8 data with function of step 6
    speed_distance = add_distance_class(speed_distance)

    #Create all figures and save to figures dirt
    plot_points_per_caracal(gps)
    plot_distance_per_caracal(gps)
    plot_speed_distribution(speed)
    plot_speed_per_distance_class(speed_distance)
    