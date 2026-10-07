# TO DO: use moving pandas?
# import movingpandas as mpd

# Main processing workflow from: https://wec.wur.nl/dse/33-ts3.html, https://wec.wur.nl/dse/31-ts1.html 

# Import
import geopandas as gpd # https://geopandas.org/en/stable/docs/user_guide.html
import pathlib # https://docs.python.org/3/library/pathlib.html#
import pandas as pd # https://pandas.pydata.org/docs/user_guide/index.html

# Load gps dataset
gps_data = gpd.read_file(pathlib.Path("python/step_dirs/step01_download/data/s01A_GPS_data.gpkg"))

# Add new column with timestamps as datetime insetad of string
# https://pandas.pydata.org/docs/getting_started/intro_tutorials/05_add_columns.html
gps_data["timestamp_datetime"] = pd.to_datetime(gps_data["timestamp"])

# Sort by individual and timestamp
# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
gps_data = gps_data.sort_values(["individual_local_identifier", "timestamp_datetime"])

# Create delta_time, time difference from the previous observation, in seconds for each individual
# https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.total_seconds.html
gps_data["delta_time"] = (
    gps_data.groupby("individual_local_identifier")["timestamp_datetime"]
    .diff()
    .dt.total_seconds()
)

# Create a column with the previous observation delta_time for each individual
# https://www.geeksforgeeks.org/python/python-pandas-dataframe-shift/
gps_data["previous_dt"] = (
    gps_data
    .groupby("individual_local_identifier")["delta_time"]
    .shift(1)
)

# Set allowed intervals (most common)
allowed_intervals = [1200, 7200, 10800]

# Create the burstID flag (TRUE/FALSE), created by comparing current time_delta, previous_dt and the allowed intervals.
# TRUE if delta_time is NA OR delta_time is not equal to previous_dt OR delta_time is not a aloowed interval.
new_burst = (
    gps_data["delta_time"].isna()
    | gps_data["delta_time"].ne(gps_data["previous_dt"])
    | ~gps_data["delta_time"].isin(allowed_intervals)
)

# Move TRUE one row lower within each individual using shift. This makes more sense, start a new burst at the new individual
gps_data["new_burst"] = (
    new_burst
    .groupby(gps_data["individual_local_identifier"])
    .shift(1)
    .fillna(False)
    .astype(bool)
)

# Calculate burst ID!
# https://www.geeksforgeeks.org/numpy/numpy-cumsum-in-python/
gps_data["burst_id"] = (
    gps_data
    .groupby("individual_local_identifier")["new_burst"]
    .cumsum()
)

# Clean dataset and workspace
del new_burst
gps_data = gps_data.drop(columns=["timestamp", "previous_dt", "new_burst", "delta_time"])

# Write processed dataset to file
# https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_file.html#geopandas.GeoDataFrame.to_file
gps_data.to_file("python/step_dirs/step04_trajectories/data/s04A_GPS_burstID.gpkg")