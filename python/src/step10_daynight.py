# Import
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf  # https://www.statsmodels.org/stable/index.html
from astral import LocationInfo
from astral.sun import sun


def day_night_analysis():
    """Analyse the difference between day and night observations."""
    # Temporary dataframe for testing !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    gps_file = pd.DataFrame({
        "individual_local_identifier": [
            "animal_001",
            "animal_001",
            "animal_003",
            "animal_001",
            "animal_003",
        ],
        "timestamp_datetime": pd.to_datetime([
            "2014-11-24 06:00",
            "2014-11-24 12:00",
            "2014-11-24 18:00",
            "2014-11-24 21:00",
            "2014-11-25 05:00",
        ], utc=False),
        "burst_id": [
            1,
            2,
            2,
            4,
            5,
        ],
        "distance_m": [
            125.0,
            450.0,
            800.0,
            250.0,
            100.0,
        ],
        "speed_kmh": [
            2.5,
            5.8,
            7.2,
            3.1,
            1.8,
        ],
    })

    # Recreate the scaled distance column from the previous step TEMP !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    gps_file["distance_100m"] = (
        gps_file["distance_m"] / 100
    )
   
    # Load data from previous step
    #gps_file = pd.read_csv("python/step_dirs/step08_compare/data/s08b_speed_distance.csv")

    # Define city [extract from extent or is this also fine?]
    city = LocationInfo("Cape Town", "Western Cape", "Africa/Johannesburg", -33.9249, 18.4241)

    # Define timezone
    timezone_ct = ZoneInfo("Africa/Johannesburg") # Check location!!

    # Localise the timestamp_datetime column to fit the timezone
    # https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.tz_localize.html
    gps_file["timestamp_datetime"] = (
        gps_file["timestamp_datetime"]
        .dt.tz_localize(timezone_ct)
    )

    # create empty lists to store the data
    sunrises = []
    sunsets = []
    day_night = []

    # Loop adding day or night to each observation
    for timestamp in gps_file["timestamp_datetime"]:
        # Retrieve sunset and sunrise times
        # https://sffjunkie.github.io/astral/
        times = sun(
            city.observer,
            date=timestamp.date(),
            tzinfo=timezone_ct,
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
    gps_file["day_night"] = day_night

    # Clean workspace
    del sunrises, sunsets, day_night, times
        
    # Fit a mixed-effects model to evaluate the relationship between speed and distance, including whether this relationship differs between daytime and nighttime observations.
    # https://www.statsmodels.org/stable/mixed_linear.html
    # Making a model: 
    model = smf.mixedlm(
        "speed_kmh ~ distance_100m * C(day_night)",
        data=gps_file,
        groups=gps_file["individual_local_identifier"]
    )

    # Running the model and printen the summarised results
    results = model.fit()
    print(results.summary())

    # Save the updated dataset and model results
    output_dir = Path("python/step_dirs/step10_daynight/data")
    
    gps_file.to_csv(output_dir / "s10A_speed_distance.csv", index=False)
    
    (output_dir / "s10B_model_summary.txt").write_text(
    results.summary().as_text(),
    encoding="utf-8")

    # Reuse matplotlib to visualize the difference between day and night observations in a scatterplot  
    # https://stackoverflow.com/questions/66071223/pandas-scatter-plot-not-coloring-by-column-value
    gps_file.plot.scatter(
        x="distance_100m",
        y="speed_kmh",
        c=gps_file["day_night"].map({"day": "orange", "night": "navy"}),
    )

    plt.xlabel("Distance (100 m)")
    plt.ylabel("Speed (km/h)")
    plt.title("Speed vs. distance by day and night")
    plt.savefig(output_dir / "s10C_day_night_scatterplot.png", dpi=300) # Save the plot
    plt.show()
    
    # Return output of function
    return gps_file #temp !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

if __name__ == "__main__":
    day_night_analysis()


