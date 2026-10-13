
"""
Step 11 — Compare animal speed in urban and wildland areas.

Purpose:
    Examine how road distance relates to animal speed across landscapes.

Inputs:
    TRAJECTORIES: GPS observations and animal identifiers
    DISTANCE: Step 06 nearest-road distances
    SPEED: Step 07 movement speeds
    FEATURES: Step 03 classified OSM land-use polygons

Outputs:
    Landscape-classified GPS observations
    Descriptive statistics CSV
    Mixed-effects model summary
    Speed-versus-distance plot
    Speed-by-landscape plot
"""
# References:
#     GeoPandas spatial joins:
#     https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin.html
#     GeoPandas merging:
#     https://geopandas.org/en/stable/docs/user_guide/mergingdata.html
#     pandas merge:
#     https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html
#     Matplotlib boxplot:
#     https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.boxplot.html
#     Matplotlib savefig:
#     https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.savefig.html
#     Statsmodels mixed-effects model:
#     https://www.statsmodels.org/stable/generated/statsmodels.formula.api.mixedlm.html

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.formula.api as smf

from python.src.config import (
    ANALYSIS_CRS,
    TRAJECTORIES,
    DISTANCE,
    SPEED,
    FEATURES,
    ID_COL,
    LANDSCAPE_OBSERVATIONS,
    LANDSCAPE_STATISTICS,
    MIXED_RESULTS,
    SPEED_DISTANCE_PLOT,
    SPEED_LANDSCAPE_PLOT,
)


# Define landscape categories used in the comparison.
URBAN_CLASSES = {"urban", "urban_green", "agriculture"}
WILD_CLASSES = {"natural"}

# Set a consistent priority when polygons overlap.
CLASS_PRIORITY = [
    "urban",
    "urban_green",
    "agriculture",
    "natural",
]

# Use consistent colours across figures.
COLOURS = {"urban": "red", "wildland": "green"}

# Acknowledge the data sources in the figures.
CREDIT = ("GPS: study data; land use: " "(c) OpenStreetMap contributors, ODbL")


def assign_landscape(points):
    """Assign one priority-based landscape class to each GPS point."""

    # Step 1: Read the classified land-use polygon layer.
    landuse = gpd.read_file(
        FEATURES,
        layer="landuse_classes",
    )

    # Check that the expected classification field exists.
    if "osm_class" not in landuse.columns:
        raise ValueError("Land-use layer must contain osm_class.")

    # Spatial operations require both layers to have a defined CRS.
    if points.crs is None or landuse.crs is None:
        raise ValueError("Both layers must have a defined CRS.")

    # Reproject both layers to the same projected analysis CRS.
    points = points.to_crs(ANALYSIS_CRS).copy()
    landuse = landuse.to_crs(ANALYSIS_CRS)

    # Create a unique row ID to resolve multiple polygon matches.
    points = points.reset_index(drop=True)
    points["_point_id"] = np.arange(len(points))

    # Retain only the landscape categories required for this analysis.
    landuse = landuse[
        landuse["osm_class"].isin(CLASS_PRIORITY)
    ][["osm_class", "geometry"]].copy()

    # Match GPS points to polygons using spatial intersection.
    # Source: GeoPandas sjoin documentation linked above.
    joined = gpd.sjoin(
        points,
        landuse,
        how="left",
        predicate="intersects",
    )

    # Rank intersecting polygons according to CLASS_PRIORITY.
    priority = {
        name: rank
        for rank, name in enumerate(CLASS_PRIORITY)
    }

    joined["_priority"] = (
        joined["osm_class"]
        .map(priority)
        .fillna(len(priority))
    )

    # Keep only one class per GPS point to prevent double-counting.
    joined = joined.sort_values(
        ["_point_id", "_priority"]
    ).drop_duplicates("_point_id", keep="first")

    # Remove temporary join fields.
    joined = joined.drop(
        columns=["index_right", "_priority", "_point_id"],
        errors="ignore",
    )

    # Combine detailed OSM classes into the two model groups.
    joined["landscape"] = np.select(
        [
            joined["osm_class"].isin(URBAN_CLASSES),
            joined["osm_class"].isin(WILD_CLASSES),
        ],
        ["urban", "wildland"],
        default="other",
    )

    return joined


def prepare_data():
    """Load, validate, merge and classify the observations."""

    # Step 2: Read GPS trajectories, road distances and speed data.
    # Keep trajectory geometry as the output geometry.
    trajectories = gpd.read_file(
        TRAJECTORIES
    ).to_crs(ANALYSIS_CRS)

    distance = gpd.read_file(DISTANCE)
    speed = gpd.read_file(SPEED)

    # Define the keys that identify each GPS observation.
    keys = [
        ID_COL,
        "timestamp_datetime",
        "burst_id",
    ]

    # Check that all three datasets contain the required keys.
    for name, frame in [
        ("TRAJECTORIES", trajectories),
        ("DISTANCE", distance),
        ("SPEED", speed),
    ]:
        missing = [
            col for col in keys
            if col not in frame.columns
        ]

        if missing:
            raise ValueError(
                f"{name} is missing columns: {missing}"
            )

    # Confirm the expected measurement fields exist.
    if "distance_m" not in distance.columns:
        raise ValueError(
            "Step 06 output must contain distance_m."
        )

    if "speed_kmh" not in speed.columns:
        raise ValueError(
            "Step 07 output must contain speed_kmh."
        )

    # Remove observations without complete matching keys.
    trajectories = trajectories.dropna(subset=keys).copy()
    distance = distance.dropna(
        subset=keys + ["distance_m"]
    ).copy()
    speed = speed.dropna(
        subset=keys + ["speed_kmh"]
    ).copy()

    # A nearest-road join may return tied nearest roads.
    # Retain the minimum distance for each GPS observation.
    distance = (
        distance.groupby(keys, as_index=False)["distance_m"]
        .min()
    )

    # Check that speed and trajectories have unique matching keys.
    if speed.duplicated(keys).any():
        raise ValueError(
            "Duplicate keys in SPEED; inspect Step 07."
        )

    if trajectories.duplicated(keys).any():
        raise ValueError(
            "Duplicate keys in TRAJECTORIES; inspect the GPS data."
        )

    # Step 3: Merge Step 06 distances with Step 07 speeds.
    # pandas merge validates that each key matches at most one row.
    dist_speed = distance.merge(
        speed[keys + ["speed_kmh"]],
        on=keys,
        how="inner",
        validate="one_to_one",
    )

    # Attach measurements to the original GPS trajectory points.
    data = trajectories.merge(
        dist_speed,
        on=keys,
        how="left",
        validate="one_to_one",
    )

    # Report missing measurements to help assess data coverage.
    print("GPS points:", len(data))
    print("Missing speed:", data["speed_kmh"].isna().sum())
    print("Missing distance:", data["distance_m"].isna().sum())

    # Remove missing and physically invalid measurement values.
    data = data.dropna(
        subset=["speed_kmh", "distance_m"]
    ).copy()

    data = data[
        (data["speed_kmh"] >= 0)
        & (data["distance_m"] >= 0)
    ].copy()

    # Step 4: Assign the land-use category to each GPS point.
    data = assign_landscape(data)

    # Retain only the urban and wildland groups for the comparison.
    data = data[
        data["landscape"].isin(["urban", "wildland"])
    ].copy()

    # Check that both groups are represented.
    if data["landscape"].nunique() < 2:
        raise ValueError(
            "Both urban and wildland observations are required. "
            "Check the osm_class values and landscape assignment."
        )

    # Create a binary predictor for the interaction model:
    # 0 = wildland; 1 = urban/agriculture.
    data["is_urban"] = (
        data["landscape"] == "urban"
    ).astype(int)

    # Express distance in 100-metre units for easier interpretation.
    data["distance_100m"] = data["distance_m"] / 100

    return data


def save_statistics(data):
    """Calculate and save descriptive speed statistics by landscape."""

    # Step 5: Summarise the number and distribution of speed values.
    statistics = (
        data.groupby("landscape")["speed_kmh"]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .reset_index()
    )

    # Create the output directory if it does not exist.
    LANDSCAPE_STATISTICS.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Save the descriptive statistics as a CSV file.
    statistics.to_csv(
        LANDSCAPE_STATISTICS,
        index=False,
    )

    print("\nSpeed statistics by landscape:")
    print(statistics.to_string(index=False))

    return statistics


def fit_model(data):
    """Fit a mixed-effects model with an animal-level random intercept."""

    # Step 6: Model speed as a function of road distance,
    # landscape group and their interaction.
    # groups=ID_COL accounts for repeated observations per animal.
    model = smf.mixedlm(
        "speed_kmh ~ distance_100m * is_urban",
        data=data,
        groups=data[ID_COL],
    )

    # Estimate fixed effects and animal-level random intercept variance.
    result = model.fit()

    # Save the model summary to a text file.
    MIXED_RESULTS.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        MIXED_RESULTS,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(result.summary().as_text())

    print("\nMixed-effects model:")
    print(result.summary())

    return result


def plot_speed_vs_distance(data, result):
    """Plot observations and mixed-model fixed-effect trends."""

    # Step 7: Compare observed speed with distance to the nearest road.
    fig, ax = plt.subplots(figsize=(9, 6))

    # Plot the observations for each landscape group.
    for group, colour in COLOURS.items():
        subset = data[data["landscape"] == group]

        ax.scatter(
            subset["distance_m"],
            subset["speed_kmh"],
            color=colour,
            alpha=0.25,
            s=12,
            label=f"{group} observations",
        )

    # Generate distances for the predicted fixed-effect lines.
    x = np.linspace(
        0,
        data["distance_m"].max(),
        100,
    )
    x_100m = x / 100
    params = result.fe_params

    # Wildland predictions: is_urban = 0.
    wildland_y = (
        params["Intercept"]
        + params["distance_100m"] * x_100m
    )

    # Urban predictions: is_urban = 1.
    urban_y = (
        params["Intercept"]
        + params["is_urban"]
        + (
            params["distance_100m"]
            + params["distance_100m:is_urban"]
        ) * x_100m
    )

    # Add the model-based trend lines to the scatterplot.
    ax.plot(
        x,
        wildland_y,
        color=COLOURS["wildland"],
        linewidth=2,
        label="Wildland model",
    )

    ax.plot(
        x,
        urban_y,
        color=COLOURS["urban"],
        linewidth=2,
        label="Urban model",
    )

    # Label and format the plot.
    ax.set(
        xlabel="Distance to nearest road (m)",
        ylabel="Animal speed (km/h)",
        title="Animal Speed vs Distance to Nearest Road",
    )

    ax.legend()
    ax.grid(alpha=0.2)

    # Add source credit and reserve space for it.
    fig.text(0.01, 0.01, CREDIT, fontsize=8)
    fig.tight_layout(rect=[0, 0.04, 1, 1])

    # Save the distance plot to its own output path.
    SPEED_DISTANCE_PLOT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    fig.savefig(
        SPEED_DISTANCE_PLOT,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def plot_speed_by_landscape(data):
    """Compare speed distributions in urban and wildland areas."""

    # Step 8: Create a separate boxplot for the two landscape groups.
    fig, ax = plt.subplots(figsize=(7, 5))

    groups = ["urban", "wildland"]

    values = [
        data.loc[
            data["landscape"] == group,
            "speed_kmh",
        ].dropna()
        for group in groups
    ]

    # Draw a boxplot for each group.
    ax.boxplot(
        values,
        tick_labels=groups,
        showfliers=False,
    )

    # Label and format the plot.
    ax.set(
        xlabel="Landscape",
        ylabel="Animal speed (km/h)",
        title="Animal Speed by Landscape",
    )
    ax.grid(axis="y", alpha=0.2)

    # Add source credit and reserve space for it.
    fig.text(0.01, 0.01, CREDIT, fontsize=8)
    fig.tight_layout(rect=[0, 0.04, 1, 1])

    # Save this figure separately from the distance plot.
    SPEED_LANDSCAPE_PLOT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    fig.savefig(
        SPEED_LANDSCAPE_PLOT,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def compare_urban_wildland():
    """Run Step 11 and save all outputs."""

    # Step 9: Prepare, classify and save the observations.
    data = prepare_data()

    LANDSCAPE_OBSERVATIONS.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data.to_file(
        LANDSCAPE_OBSERVATIONS,
        driver="GPKG",
    )

    print("\nObservations retained:", len(data))
    print("Observations by landscape:")
    print(data["landscape"].value_counts().to_string())

    # Calculate descriptive statistics and fit the mixed model.
    save_statistics(data)
    result = fit_model(data)

    # Create and save the two separate figures.
    plot_speed_vs_distance(data, result)
    plot_speed_by_landscape(data)

    # Report output locations.
    print("\nStep 11 completed.")
    print("Observations:", LANDSCAPE_OBSERVATIONS)
    print("Statistics:", LANDSCAPE_STATISTICS)
    print("Mixed model:", MIXED_RESULTS)
    print("Distance plot:", SPEED_DISTANCE_PLOT)
    print("Landscape plot:", SPEED_LANDSCAPE_PLOT)

    return {
        "observations": data,
        "model": result,
    }
