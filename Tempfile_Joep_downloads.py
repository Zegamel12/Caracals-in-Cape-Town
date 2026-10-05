import os

# https://stackoverflow.com/questions/273192/how-do-i-create-a-directory-and-any-missing-parent-directories
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists("output"):
    os.makedirs("output")

import requests
import pandas as pd

url = (
    "https://www.movebank.org/movebank/service/direct-read"
    "?entity_type=event"
    "&study_id=1832666571"
    "&attributes=all"
    "&i_have_download_access=true"
)

import pandas as pd
from requests.auth import HTTPBasicAuth

url = (
    "https://www.movebank.org/movebank/service/direct-read"
    "?entity_type=event"
    "&study_id=1832666571"
    "&attributes=all"
)

data = pd.read_csv(url)
