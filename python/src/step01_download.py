# Import pandas, geopandas and pyproj
import pandas as pd
import geopandas as gpd
import pyproj



### --- Import GPS data ---

# https://github.com/movebank/movebank-api-doc/tree/master
import getpass
import hashlib
import io

import pandas as pd
import requests
from config import username_movebank, password_movebank

# Movebank API accesspoint
url = "https://www.movebank.org/movebank/service/direct-read"

# Parameters [Make more specific, remove redundant columns]
params = {
    "entity_type": "event",
    "study_id": "1832666571",
    "attributes": "all",
}

with requests.Session() as session:
    session.auth = (username_movebank, password_movebank)

    # First request retrieves the license page
    response = session.get(url, params=params, timeout=300)

    # Second request sends its MD5 hash and downloads the CSV
    params["license-md5"] = hashlib.md5(response.content).hexdigest()
    response = session.get(url, params=params, timeout=300)
   
# Read the data into a dataframe
gps_data = pd.read_csv(io.BytesIO(response.content))