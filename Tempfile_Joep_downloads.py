# https://stackoverflow.com/questions/273192/how-do-i-create-a-directory-and-any-missing-parent-directories
import os
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists("output"):
    os.makedirs("output")


# https://github.com/movebank/movebank-api-doc/tree/master
import getpass
import hashlib
import io

import pandas as pd
import requests

# Set username and password [move to global parameters]
username = "Jovado" 
password = "waardeloos123"

# Movebank API accesspoint
url = "https://www.movebank.org/movebank/service/direct-read"

# Parameters [Make more specific, remove redundant columns]
params = {
    "entity_type": "event",
    "study_id": "1832666571",
    "attributes": "all",
}

with requests.Session() as session:
    session.auth = (username, password)

    # First request retrieves the license page
    response = session.get(url, params=params, timeout=300)

    # Second request sends its MD5 hash and downloads the CSV
    params["license-md5"] = hashlib.md5(response.content).hexdigest()
    response = session.get(url, params=params, timeout=300)
   
# Read the data into a dataframe
data = pd.read_csv(io.BytesIO(response.content))