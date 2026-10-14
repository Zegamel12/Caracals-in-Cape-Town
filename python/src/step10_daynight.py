# This code was mainly written by: Joep van Dongen. See the commit history for a detailed contribution record.

# Import
from zoneinfo import ZoneInfo

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf  # https://www.statsmodels.org/stable/index.html
from astral import LocationInfo
from astral.sun import sun

from python.src.config import (
    DAY_NIGHT_CSV,
    DAY_NIGHT_MODEL,
    DAY_NIGHT_PLOT,
    SPEED_DISTANCE_CSV,
    STUDY_LOCATION,
    TIMEZONE,
)


def day_night_analysis():
    """Analyse the difference between day and night observations."""
    # Load data from previous step
    gps_data = gpd.read_file(SPEED_DISTANCE_CSV)

    # Define city source: https://sffjunkie.github.io/astral/
    city = LocationInfo(
        STUDY_LOCATION["name"],
        STUDY_LOCATION["region"],
        TIMEZONE,
        STUDY_LOCATION["lat"],
        STUDY_LOCATION["lon"],
    )

    # Define timezone
    timezone = ZoneInfo(TIMEZONE)

    # Localise the timestamp_datetime column to fit the timezone
    # https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.tz_localize.html
    gps_data["timestamp_datetime"] = pd.to_datetime(
        gps_data["timestamp_datetime"],
        utc=True,
        errors="raise",
        format="mixed",
    ).dt.tz_convert(timezone)

    # create empty lists to store the data
    sunrises = []
    sunsets = []
    day_night = []

    # Loop adding day or night to each observation
    for timestamp in gps_data["timestamp_datetime"]:
        # Retrieve sunset and sunrise times
        # https://sffjunkie.github.io/astral/
        times = sun(
            city.observer,
            date=timestamp.date(),
            tzinfo=timezone,
        )

        # For each observation write to list
        sunrise = times["sunrise"]
        sunrises.append(sunrise)
        sunset = times["sunset"]
        sunsets.append(sunset)
    
        # Make list. create day / time for each observation.
        day_night.append(
            "day" if sunrise <= timestamp <= sunset else "night"
        )

    # Add the created day_night list to the gps dataset as new column
    gps_data["day_night"] = day_night

    # Clean workspace
    del sunrises, sunsets, day_night, times

     # Make sure all columns have the right data type
     # Source: https://stackoverflow.com/questions/71166523/cleaning-gps-data-csv-file-with-python
    gps_data["speed_kmh"] = pd.to_numeric(gps_data["speed_kmh"], errors="coerce")

    gps_data["distance_100m"] = pd.to_numeric(gps_data["distance_100m"], errors="coerce")
    
    ## Remove NAN
    gps_data = gps_data.dropna(
        subset=[
            "speed_kmh",
            "distance_100m",
            "individual_local_identifier",
        ]
    ).copy()

    # Make day_night a categorical column with only two categories
    gps_data["day_night"] = pd.Categorical(
    gps_data["day_night"],
    categories=["night", "day"],
)    
    # Fit a mixed-effects model to evaluate the relationship between speed and distance, including whether this relationship differs between daytime and nighttime observations.
    # https://www.statsmodels.org/stable/mixed_linear.html
    # Making a model: 
    model = smf.mixedlm(
        "speed_kmh ~ distance_100m * day_night",
        data=gps_data,
        groups=gps_data["individual_local_identifier"]
    )

    # Running the model and printen the summarised results
    results = model.fit()
    print(results.summary())

    # Save the updated dataset and model results
    gps_data.to_csv(DAY_NIGHT_CSV, index=False)

    DAY_NIGHT_MODEL.write_text(
        results.summary().as_text(),
        encoding="utf-8")

    # Reuse matplotlib to visualize the difference between day and night observations in a scatterplot  
    # https://stackoverflow.com/questions/66071223/pandas-scatter-plot-not-coloring-by-column-value
    gps_data.plot.scatter(
        x="distance_100m",
        y="speed_kmh",
        c=gps_data["day_night"].map({"day": "orange", "night": "navy"}),
    )

    plt.xlabel("Distance (100 m)")
    plt.ylabel("Speed (km/h)")
    plt.title("Speed vs. distance by day and night")
    plt.savefig(DAY_NIGHT_PLOT, dpi=300) # Save the plot
    plt.close()

if __name__ == "__main__":
    day_night_analysis()


