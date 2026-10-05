# Here put in the consistend variables, so we can quickly change them in the whole script.

from pathlib import Path

base = Path('.') # This references the root of your current directory

# Folders/directories
(base / "data").mkdir(exist_ok=True)
(base / "data" / "raw").mkdir(exist_ok=True)
(base / "data" / "output").mkdir(exist_ok=True)

# Data files
GPS_RAW = base / "data" / "raw" / "...." # ... replace with file name and its extensions
GPS_PROCESSED = base / "data" / "processed" / "...."

ROADS = base / "data" / "processed" / "...."
URBAN = base / "data" / "processed" / "...."

# Input variables
GPS_CRS = "EPSG:4326"
ANALYSIS_CRS = "EPSG:xxxxx"