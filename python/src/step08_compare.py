# This code was mainly written by: Silke Zeeuwen. See the commit history for a detailed contribution record.

# Import
import geopandas as gpd
import numpy as np
import pandas as pd
import statsmodels.api as sm  #https://www.statsmodels.org/stable/index.html
import statsmodels.formula.api as smf

from python.src.config import DISTANCE, SPEED, SPEED_DISTANCE_CSV, SPEED_DISTANCE_MODEL


def compare_speed_to_distance():
    """Compare animal speed with distance to the nearest road.

    Inputs:
        DISTANCE: GPS observations containing distance-to-road values in column distance_m (step 6 output).
        SPEED: GPS observations containing movement-speed values in column speed_kmh (step 7 output).

    Outputs:
        A CSV file containing the matched observations and a .txt file containing the mixed-effects model summary.
    """

    # Columns used to uniquely identify each GPS observation
    KEYS = [
        "individual_local_identifier",
        "timestamp_datetime",
        "burst_id",
    ]
    
    # Read input data
    distance_data = gpd.read_file(DISTANCE)
    speed_data = gpd.read_file(SPEED)

    # Remove observations with missing matching keys
    distance_data = distance_data.dropna(subset=KEYS).copy()
    speed_data = speed_data.dropna(subset=KEYS).copy()

    # Ensure timestamps use the same datetime format
    distance_data["timestamp_datetime"] = pd.to_datetime(
        distance_data["timestamp_datetime"],
        utc=True,
        errors="raise",
    )

    speed_data["timestamp_datetime"] = pd.to_datetime(
        speed_data["timestamp_datetime"],
        utc=True,
        errors="raise",
    )

    # Check that each dataset contains only one row per observation key
    for name, data in [
        ("distance", distance_data),
        ("speed", speed_data),
    ]:
        if data.duplicated(KEYS).any():
            raise ValueError(
                f"Duplicate observation keys in {name} data"
            )

    # Keep only the columns needed for the comparison
    distance_table = distance_data[KEYS + ["distance_m"]]
    speed_table = speed_data[KEYS + ["speed_kmh"]]

    # Match distance and speed observations
    gps_dataset = distance_table.merge(
        speed_table,
        on=KEYS,
        how="inner",
        validate="one_to_one",
    )

    # Convert values to numeric and remove invalid observations
    for column in ["distance_m", "speed_kmh"]:
        gps_dataset[column] = pd.to_numeric(
            gps_dataset[column],
            errors="coerce",
        )

    valid_values = (
        np.isfinite(gps_dataset["distance_m"])
        & np.isfinite(gps_dataset["speed_kmh"])
        & (gps_dataset["distance_m"] >= 0)
        & (gps_dataset["speed_kmh"] >= 0)
    )

    gps_dataset = gps_dataset.loc[valid_values].copy()

    # Express distance in units of 100 metres
    gps_dataset["distance_100m"] = gps_dataset["distance_m"] / 100

    # Make sure all columns have the right data type
    # Source: https://stackoverflow.com/questions/71166523/cleaning-gps-data-csv-file-with-python
    gps_dataset["speed_kmh"] = pd.to_numeric(gps_dataset["speed_kmh"], errors="coerce")

    gps_dataset["distance_100m"] = pd.to_numeric(gps_dataset["distance_100m"], errors="coerce")

    # Remove NAN
    gps_dataset = gps_dataset.dropna(
        subset=[
            "speed_kmh",
            "distance_100m",
            "individual_local_identifier",
        ]
    ).copy()

    # Fit a mixed-effects model with animal-specific grouping
    model = smf.mixedlm(
        "speed_kmh ~ distance_100m",
        data=gps_dataset,
        groups=gps_dataset["individual_local_identifier"],
    )

    # Running the model and printen the summarised results
    results = model.fit()
    print(results.summary())

     # Save the updated dataset and model results
    gps_dataset.to_csv(SPEED_DISTANCE_CSV, index=False)

    SPEED_DISTANCE_MODEL.write_text(
        results.summary().as_text(),
        encoding="utf-8")

if __name__ == "__main__":
    compare_speed_to_distance()