# Import pandas and statsmodels
from multiprocessing import Value
import pandas as pd
import statsmodels.api as sm #https://www.statsmodels.org/stable/index.html
from pathlib import Path
import geopandas as gpd
import numpy as np

from python.src.config import DISTANCE, SPEED
def create_comparison()
    # Prevent that sights of different animals get mixed up
    KEYS = [
        "individual_local_identifier",
        "timestamp_datatime",
        "burst_id",
        ]

    # Analysation function and read files
    def compare_speed_to_distance():
        distance_data = gpd.read_file(DISTANCE)
        speed_data = gpd.read_file(SPEED)

    # Make sure the right collums are present
    required_distance = KEYS + ["distance_m"]
    required_speed = KEYS + ["speed_kmh"]

    missing_distance = [
        column for column in required_distance
        if column not in distance_data.columns
    ]
    missing_speed= [
        column for column in required_speed
        if column not in speed_data.columns
    ]
    # Step07 is still in process atm, this gives clear error if valuenames change
    if missing_distance:
        raise ValueError (f"Missing from distance data:
        {missing_distance}")
    if missing_speed:
        raise ValueError (f"Missing from speed data:
        {missing_speed}")

    # Make timestamps the same and check keys
    distance_data["timestamp_datetime"] = pd.to_datetime(
        distance_data["timestamp_datetime"], utc=True
    )
    speed_data["timestamp_datetime"] = pd.to_datetime(
        speed_data["timestamp_datetime"], utc=True
    )
    for name, data in [
        ("distance", distance_data),
        ("speed", speed_data),
    ]:
    if data.duplicated(KEYS).any():
        raise ValueError(f"Dublicate observation keys in {name} data")

    # Pair only the needed data
    distance_table = distance_data[KEYS+["distance_m"]]
    speed_table= speed_data[KEYS+["speed_kmh"]]

    analysis = distance_table.merge(
        speed_table,
        on=KEYS, 
        how="inner",
        validate= "one_to_one",
    )
    print(f"Matched observations: {len(analysis)}")

    # Take out missing or untrue values
    for column in ["distance_m", "speed_kmh"]:
        analysis[column] = pd.to_numeric(
            analysis[column], errors= "coerce"
        )
    valid_values = (
        np.isfinite(analysis["distance_m"])
        & np.isfinite(analysis["speed_kmh"])
        & (analysis["distance_m"] >= 0)
        & (analysis["speed_kmh"] >= 0)
    )
    analysis = analysis.loc[valid_values].copy()

    if analysis.empty:
        raise ValueError("There are no valid matched observations")

    print(f"Valid observation: {len(analysis)}")
    print(
        "Animals:",
        analysis["individual_local_identifier"].nunique(),
    )

    # Scale the distance and apply a model
    analysis["distance_100m"] = analysis ["distance_m"] /100
    model = smf.mixedlm(
        "speed_kmh ~distance_100m",
        data=analysis,
        groups= analysis ["individual_local_identifier"],
    )
    results = model.fit()
    print(results.summary())

    # Save the paired data and model results
    output_dir= Path("python/step_dirs/step08_compare/data")
    analysis.to_cvs(
        output_dir / "s08b_speed_distance.csv",
        index=False,
    )
    (output_dir/ "s08b_model_summary.txt").write_text(
        results.summary().as_text(),
        endocing= "utf-8",
        )

    if __name__ == "__main__":
        compare_speed_to_distance()