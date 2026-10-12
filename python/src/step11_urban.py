""" Step11 : Compare animal movement across classifies landscape and model it.
urban vs wildland """

# Refrences:
# GeoPandas spatial join: https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin.html
# pandas merge: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html
# Matplotlib boxplot: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.boxplot.html
# Statsmodels OLS: https://www.statsmodels.org/stable/generated/statsmodels.formula.api.ols.html
# boxplot : https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.boxplot.html

import geopandas as gpd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

from python.src.config import (
    ANALYSIS_CRS, FEATURES, TRAJECTORIES, DISTANCE, SPEED, 
    LANDSCAPE_OBSERVATIONS, LANDSCAPE_STATISTICS, SPEED_LANDSCAPE_PLOT,
     OLS_RESULTS, SPEED_LANDSCAPE_PLOT,SPEED_DISTANCE_PLOT
)

def compare_urban_wildland():
    """Compare GPS speed and road distance in urban and wildland areas."""

    # 1. Load input data
    distance = gpd.read_file(DISTANCE).to_crs(ANALYSIS_CRS)
    trajectories_data = gpd.read_file(TRAJECTORIES).to_crs(ANALYSIS_CRS)
    landuse = gpd.read_file(FEATURES).to_crs(ANALYSIS_CRS)
    speed = gpd.read_file(SPEED).to_crs(ANALYSIS_CRS)

    keys = [
        "individual_local_identifier",
        "timestamp_datetime",
        "burst_id"
    ]

    # 2. Remove rows with incomplete merge keys
    trajectories_clean = trajectories_data.dropna(subset=keys).copy()
    distance_clean = distance.dropna(subset=keys).copy()
    speed_clean = speed.dropna(subset=keys).copy()

    # 3. Merge speed and distance measurements
    dist_speed_m = distance_clean.merge(
        speed_clean[keys + ["speed_kmh"]],
        on=keys,
        how="left",
        validate="one_to_one",
    )

    trajectories_m = trajectories_clean.merge(
        dist_speed_m[keys + ["distance_m", "speed_kmh"]],
        on=keys,
        how="left",
        validate="one_to_one",
    )
    print("GPS points retained:", len(trajectories_m))
    print("Missing speed:", trajectories_m["speed_kmh"].isna().sum())
    print("Missing distance:", trajectories_m["distance_m"].isna().sum())

    # 4. Define landscape classes
    urban_classes = {"urban", "urban_green", "agriculture"}
    wild_classes = {"natural"}

    landuse = landuse[["osm_class", "geometry"]].copy()
    landuse = landuse[
        landuse["osm_class"].isin(urban_classes | wild_classes)
    ].copy()

    # 5. Assign landscape classes to GPS points
    trajectories_join = gpd.sjoin(
        trajectories_m,
        landuse,
        how="left",
        predicate="intersects",
    )

    trajectories_m_urban = trajectories_join[
        trajectories_join["osm_class"].isin(urban_classes)
    ].copy()

    trajectories_m_wild = trajectories_join[
        trajectories_join["osm_class"].isin(wild_classes)
    ].copy()

    # 6. Descriptive statistics
    print("Urban observations:", len(trajectories_m_urban))
    print("Wildland observations:", len(trajectories_m_wild))

    # 7. Visualise road distance versus speed.
    # use a Separate trend lines to allow a visual comparison of the relationships
    fig, ax = plt.subplots(figsize=(12, 6))
    
    urban = trajectories_m_urban.dropna(
        subset=["distance_m", "speed_kmh"]
    )
    wild = trajectories_m_wild.dropna(
        subset=["distance_m", "speed_kmh"]
    )
    ax.scatter(
        wild["distance_m"], wild["speed_kmh"],
        c="green", marker="x", s=14, alpha=0.6,
        label="Wildland observations"
    )
    ax.scatter(
        urban["distance_m"], urban["speed_kmh"],
        c="red", marker="o", s=12, alpha=0.6,
        label="Urban observations"
        )
    
    # Separate linear trend lines
    for data, label, colour in [
        (urban, "Urban", "red"),
        (wild, "Wildland", "green")]:
        
        if len(data) >= 2 and data["distance_m"].nunique() >= 2:
            x = data["distance_m"].to_numpy()
            y = data["speed_kmh"].to_numpy()
            slope, intercept = np.polyfit(x, y, 1)
            x_line = np.linspace(x.min(), x.max(), 100)

            ax.plot(
                x_line, slope * x_line + intercept,
                color=colour, linewidth=2.5,
                label=f"{label} trend"
                )

    ax.set_xlabel("Distance to nearest road (m)")
    ax.set_ylabel("Animal speed (km/h)")
    ax.set_title("Animal Speed vs Distance to Nearest Road")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


    # 8. Compare animal speed distributions across landscape classes.

    landscape_order = ["urban", "urban_green", "agriculture", "natural"]

    landscape_data = trajectories_join.dropna(
        subset=["osm_class", "speed_kmh"]
        )

    speed_groups = [
        landscape_data.loc[
        landscape_data["osm_class"] == landscape,"speed_kmh"
        ].to_numpy()
        for landscape in landscape_order
    ]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.boxplot(
        speed_groups,
        tick_labels=landscape_order
        )

    ax.set_xlabel("Landscape class")
    ax.set_ylabel("Animal speed (km/h)")
    ax.set_title("Animal Speed Across Landscape Classes")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.show()



    # 8. Prepare data for regression
    model_data = trajectories_join.dropna(
        subset=["speed_kmh", "distance_m", "osm_class"]
    ).copy()

    model_data = model_data[
        model_data["osm_class"].isin(urban_classes | wild_classes)
    ].copy()

    model_data["is_urban"] = (
        model_data["osm_class"].isin(urban_classes)
    ).astype(int)

    # 9. Fit linear regression with an interaction
    model = smf.ols(
        "speed_kmh ~ distance_m * is_urban",
        data=model_data,
    ).fit()

    # 10.  Display model results
    print("\nOLS regression results:")
    print(model.summary())

   # 11. save the required outputs

    #  Save landscape-classified GPS observations.
    trajectories_join.to_file(
        LANDSCAPE_OBSERVATIONS, driver="GPKG")

    #  Save descriptive statistics by landscape class.
    landscape_data.groupby("osm_class")[
        ["speed_kmh", "distance_m"]
        ].describe().to_csv(
            LANDSCAPE_STATISTICS
            )

    #  Save the OLS regression summary.
    with open(OLS_RESULTS, "w", encoding="utf-8") as file:
        file.write(model.summary().as_text())

    #  Save the speed-versus-distance scatterplot.
    fig.savefig(SPEED_DISTANCE_PLOT, dpi=300, bbox_inches="tight")
    fig.savefig(SPEED_LANDSCAPE_PLOT,dpi=300,bbox_inches="tight")
    print("Step 11 data and regression results saved.")

    # Return results 
    return {
        "urban": trajectories_m_urban,
        "wildland": trajectories_m_wild,
        "model_data": model_data,
        "model": model
        }
