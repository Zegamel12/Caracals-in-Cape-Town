# This code was mainly written by: Joep van Dongen. See the commit history for a detailed contribution record.  

# Import
import hashlib
import io
from pathlib import Path

import geopandas as gpd  #https://www.geeksforgeeks.org/python/geopandas-tutorial/
import pandas as pd  #https://www.geeksforgeeks.org/pandas/pandas-step-by-step-guide/
import requests

from python.src.config import (
    GPS_DATA,
    ANALYSIS_CRS,
    GPS_CRS,
    password_movebank,
    username_movebank
)


def download_gps_data():
    """ Retrieve gps dataset from Movebank. """
    # Movebak API explanation: https://github.com/movebank/movebank-api-doc/tree/master
    # Movebank API accesspoint
    url = "https://www.movebank.org/movebank/service/direct-read"

    # Parameters
    # Explanation: https://www.movebank.org/cms/movebank-content/movebank-attribute-dictionary#tag_attributes
    params = {
        "entity_type": "event",
        "study_id": "1832666571",
        "attributes": "individual_local_identifier,timestamp,location_long,location_lat,gps_hdop" # Only import wanted columns
    }

    # Request the dataset with the parameters defined above
    with requests.Session() as session:
        session.auth = (username_movebank, password_movebank)

        # First request retrieves the license page
        response = session.get(url, params=params, timeout=300)

        # Second request sends its MD5 hash and downloads the CSV
        params["license-md5"] = hashlib.md5(response.content).hexdigest()
        response = session.get(url, params=params, timeout=300)
    
    # Read the data into a dataframe
    gps_csv = pd.read_csv(io.BytesIO(response.content))

    # Create a GeoDataFrame with points from longitude and latitude
    # Manual: https://geopandas.org/en/stable/docs/user_guide.html
    gps_gdf = gpd.GeoDataFrame(gps_csv,
        geometry=gpd.points_from_xy(
            gps_csv["location_long"],
            gps_csv["location_lat"]),
        crs=GPS_CRS)

    # Convert projection to UTM
    gps_gdf_utm = gps_gdf.to_crs(ANALYSIS_CRS)

    # Check plot
    # gps_gdf_utm.plot()

    # Write processed dataset to file
    # https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_file.html#geopandas.GeoDataFrame.to_file
    gps_gdf_utm.to_file(GPS_DATA)

    # Clean workspace [add more]
    del url, params
