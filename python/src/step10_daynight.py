# Import
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from astral import LocationInfo
from astral.sun import sun

#import plotly.express as px
#import statsmodels.api as sm

# Temporary dataframe
gps_file = pd.DataFrame({
    "timestamp_datetime": pd.to_datetime([
        "2014-11-24 06:00",
        "2014-11-24 12:00",
        "2014-11-24 18:00",
        "2014-11-24 21:00",
        "2014-11-25 05:00"
        ])
})

# Get starting data set [change later]
gps_file = Path("python/step_dirs/step04_trajectories/data/s04A_GPS_burstID.gpkg")

if not gps_file.exists():
     raise FileNotFoundError(
        "GPS-file not found: first run Step04"
        )

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
    

# Split data sets based on this new column [TBC]

# Reuse of statsmodels to test speed vs. distance relationship based on daytime or nighttime values.  

# Reuse matplotlib and plotly for visualization as stated in previous steps.  