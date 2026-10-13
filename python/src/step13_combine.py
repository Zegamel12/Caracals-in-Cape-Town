"""Step 12: answers to the research questions, calculated on ONE common dataset.
 
Combines: 
    step 11 -> LANDSCAPE_OBSERVATIONS: speed, distance, landscape (urban / wildland) per GPS fix
    step 10 -> DAY_NIGHT_CSV:   day / night label per GPS fix
Output: answers.txt (one plain sentence per question), model summaries, group statistics, 2 plots.
"""
# References:
# pandas read_csv:     https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
# pandas merge:        https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html
# pandas to_datetime:  https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html
# pandas groupby:      https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html
# numpy log1p:         https://numpy.org/doc/stable/reference/generated/numpy.log1p.html
# GeoPandas read_file: https://geopandas.org/en/stable/docs/reference/api/geopandas.read_file.html
# Statsmodels mixedlm: https://www.statsmodels.org/stable/mixed_linear.html
# MixedLMResults (params, pvalues): https://www.statsmodels.org/stable/generated/statsmodels.regression.mixed_linear_model.MixedLMResults.html
# Formulas (* = main effects + interactions): https://www.statsmodels.org/stable/example_formulas.html
# Matplotlib boxplot:  https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.boxplot.html
# Matplotlib errorbar: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.errorbar.html
# Matplotlib plot:     https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.plot.html
# Statsmodels conf_int: https://www.statsmodels.org/stable/generated/statsmodels.regression.mixed_linear_model.MixedLMResults.conf_int.html

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd
import statsmodels.formula.api as smf

from python.src.config import DAY_NIGHT_CSV, ID_COL, LANDSCAPE_OBSERVATIONS, TIME_COL, KEYS
from python.src.step06_distance import LABELS, add_distance_class

OUT_DIR = Path("/home/osboxes/project-starter-Gezellig_positive_koffie_zebra/python/step_dirs/combined_results")
OUT_DIR.mkdir(parents=True, exist_ok=True)
GROUPS = [(landscape, period) for landscape in ["urban", "wildland"] for period in ["day", "night"]]
MIN_PER_GROUP = 30 # fewer observation in a group makes the interaction terms unreliable
COLOURS = {"urban": "tab:orange", "wildland": "tab:green"}
# One row per research question
SPEED_MODELS = {
    "A": "speed_kmh ~ distance_100m",
    "B": "speed_kmh ~ distance_100m * is_urban",
    "C": "speed_kmh ~ distance_100m * is_day",
    "E": "speed_kmh ~ distance_100m * is_urban * is_day",
}
DIST_MODEL = "log_distance ~ is_urban * is_day"
QUESTIONS = [
    ("Q1  Does speed change with distance to the nearest road?",
     SPEED_MODELS["A"], "distance_100m", False,
     "speed INCREASES with distance from roads (animals are slower near roads)",
     "speed DECREASES with distance from roads (animals are faster near roads)"),
    ("Q2  Does the speed-distance relationship differ between urban and wildland?",
     SPEED_MODELS["B"], "distance_100m:is_urban", False,
     "the slope is HIGHER in urban areas than in wildland",
     "the slope is LOWER in urban areas than in wildland"),
    ("Q3  Does the speed-distance relationship differ between day and night?",
     SPEED_MODELS["C"], "distance_100m:is_day", False,
     "the slope is HIGHER by day than by night",
     "the slope is LOWER by day than by night"),
    ("Q4a Do animals keep a different distance to roads in urban areas than in wildland?",
     DIST_MODEL, "is_urban", True,
     "animals are FURTHER from roads in urban areas",
     "animals are CLOSER to roads in urban areas"),
    ("Q4b Do animals keep a different distance to roads by day than by night?",
     DIST_MODEL, "is_day", True,
     "animals are FURTHER from roads by day",
     "animals are CLOSER to roads by day"),
    ("Q4c Does the day-night difference in road distance depend on the landscape?",
     DIST_MODEL, "is_urban:is_day", True,
     "the day-vs-night difference is LARGER (more positive) in urban areas",
     "the day-vs-night difference is SMALLER (more negative) in urban areas"),
    ("MAIN Does the urban effect on the speed-distance slope differ between day and night?",
     SPEED_MODELS["E"], "distance_100m:is_urban:is_day", False,
     "the urban-vs-wildland slope difference is LARGER by day than by night",
     "the urban-vs-wildland slope difference is SMALLER by day than by night"),
]
 

def load_data():
    """Combine landscape and day/night observations."""

    landscape = gpd.read_file(
        LANDSCAPE_OBSERVATIONS, ignore_geometry=True
    )
    daynight = pd.read_csv(DAY_NIGHT_CSV, usecols=KEYS + ["day_night"])

    # Standardise timestamps
    landscape[TIME_COL] = pd.to_datetime(landscape[TIME_COL], utc=True)
    daynight[TIME_COL] = pd.to_datetime(daynight[TIME_COL], utc=True)

    # Match GPS fixes
    data = landscape.merge(
        daynight, on=KEYS, how="inner", validate="one_to_one"
    )

    # Keep valid urban and wildland observations
    data = data[
        data["landscape"].isin(["urban", "wildland"])
    ].dropna(subset=["speed_kmh", "distance_m"]).copy()

    # Prepare model variables
    data["is_urban"] = (data["landscape"] == "urban").astype(int)
    data["is_day"] = (data["day_night"] == "day").astype(int)
    data["distance_100m"] = data["distance_m"] / 100
    data["log_distance"] = np.log1p(data["distance_m"])

    print(f"GPS fixes: {len(data)} | Animals: {data[ID_COL].nunique()}")
    return data

def check_groups(data):
    """ Summarise speed and distance by landscape and day.night."""
    stats = data.groupby(
        ["landscape", "day_night"]).agg(
            n = ("speed_kmh", "size"), 
            mean_speed=("speed_kmh", "mean"),
            mean_distance_m =("distance_m", "mean")
    )
    
    print(stats)
    stats.to_csv(OUT_DIR / "s12a_group_statistics.csv")

def fit_models(data):
    """Fit mixed-effects models with a random intercept per animal."""
    # A model shares by several questions, so each formula is fitted only once

    results = {}

    for formula in dict.fromkeys(q[1] for q in QUESTIONS):
        results[formula] = smf.mixedlm(
            formula, data=data, groups=data[ID_COL]
            ).fit()

    text = "\n\n".join(
        f"MODEL: {formula}\n{model.summary().as_text()}"
        for formula, model in results.items()
    )
    
    # Save all model summaries in one text file
    (OUT_DIR / "s12b_model_summaries.txt").write_text(text, encoding="utf-8")

    return results


def write_answers(results):
    """Summarise model results for each research question."""
    lines = []

    for question, formula, term, is_log, text_pos, text_neg in QUESTIONS:
        # Extract coefficient and p-value
        model = results[formula]
        coef = model.params[term]
        p = model.pvalues[term]

        # Calculate effect size
        size = (
            f"{(np.exp(coef) - 1) * 100:+.1f}%"
            if is_log else f"{coef:+.3f}"
        )

        # Interpret statistical significance and direction
        if p < 0.05:
            answer = (
                f"Evidence of an association (p={p:.3g}, effect={size}): "
                f"{text_pos if coef > 0 else text_neg}."
            )
        else:
            answer = (
                f"No clear statistical evidence of an association "
                f"(p={p:.3g}, effect={size})."
            )

        lines.extend([question, "   " + answer, ""])

    # Save and print answers
    output = "\n".join(lines)
    (OUT_DIR / "s12c_answers.txt").write_text(
        output, encoding="utf-8"
    )
    print(output)


def make_plots(data):
    """ plot road distanc eby landscape and day/night."""
    # 1. Distance to the nearest road per landscape x day/night group (Q4)
    values = [
        data.loc[
            (data["landscape"] == landscape) & (data["day_night"] == day),
            "distance_m"
        ]
        for landscape, day in GROUPS
    ]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.boxplot(values, tick_labels=[f"{landscape}\n{day}" for landscape, day in GROUPS],showfliers=False)
    ax.set(xlabel= "Landscape and time of day", 
           ylabel="Distance to nearest road (m)",
           title = "Road distance by landscape and time of the day")

    fig.savefig(OUT_DIR / "s12d_distance_by_group,png", dpi=300, bbox_inches ="tight")
    plt.show()
    plt.close(fig)
    
    # 2. Mean speed by road-distance class, landscape and day/night (Q1–Q3)
def plot_speed(data):
    data = add_distance_class(data.copy())
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)

    for ax, landscape in zip(axes, ["urban", "wildland"]):
        means = data[data["landscape"] == landscape].pivot_table(
            index="distance_class", columns="day_night",
            values="speed_kmh", aggfunc="mean"
        ).reindex(LABELS)

        means.plot(ax=ax, marker="o")
        ax.set(title=landscape.capitalize(),
               xlabel="Distance to nearest road",
               ylabel="Mean speed (km/h)")
        ax.tick_params(axis="x", rotation=45)

    fig.suptitle("Mean speed by road distance, landscape and time of day")
    fig.savefig(OUT_DIR / "s12e_speed_by_distance_class.png",
                dpi=300, bbox_inches="tight")
    plt.show()
    plt.close(fig)

def plot_effects(results):
    """Plot model effects with 95% confidence intervals."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, is_log, title in zip(
        axes, [False, True],
        ["Effect on speed (km/h)", "Effect on road distance (%)"]
    ):
        rows = [q for q in QUESTIONS if q[3] == is_log]

        for i, (_, formula, term, *_) in enumerate(rows):
            model = results[formula]
            coef = model.params[term]
            low, high = model.conf_int().loc[term]

            if is_log:
                coef, low, high = [
                    (np.exp(v) - 1) * 100 for v in (coef, low, high)
                ]

            ax.errorbar(coef, i, xerr=[[coef - low], [high - coef]],
                        fmt="o", capsize=4)

        ax.axvline(0, color="grey", linestyle="--")
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels([q[2] for q in rows])
        ax.invert_yaxis()
        ax.set(xlabel="Estimate (95% CI)", title=title)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "s12f_effects.png", dpi=300, bbox_inches="tight")
    plt.show()
    plt.close(fig)

def plot_model_lines(results, data):
    """Plot predicted speed by road distance for each group."""
    p = results[SPEED_MODELS["E"]].params
    x = np.linspace(0, data["distance_m"].quantile(0.99), 100)
    d = x / 100
    fig, ax = plt.subplots(figsize=(10, 6))

    for landscape, period in GROUPS:
        u, n = int(landscape == "urban"), int(period == "day")
        y = (p["Intercept"] + p["distance_100m"] * d + p["is_urban"] * u
             + p["is_day"] * n + p["distance_100m:is_urban"] * d * u
             + p["distance_100m:is_day"] * d * n + p["is_urban:is_day"] * u * n
             + p["distance_100m:is_urban:is_day"] * d * u * n)

        ax.plot(x, y, color=COLOURS[landscape],
                linestyle="-" if period == "day" else "--",
                linewidth=2, label=f"{landscape}, {period}")

    ax.set(xlabel="Distance to nearest road (m)",
           ylabel="Predicted speed (km/h)",
           title="Predicted speed by road distance and group")
    ax.legend(title="Group")
    ax.grid(alpha=0.3)
    fig.savefig(OUT_DIR/ "s12g_model_lines.png", dpi=300, bbox_inches="tight")
    plt.show()
    plt.close(fig)

def run_combined_analysis():
    """Answer all research questions on one dataset."""
    #OUT_DIR.mkdir(parents=True, exist_ok=True)
 
    # 1. Combine landscape (step 11) and day/night (step 10) per GPS fix
    data = load_data()
 
    # 2. Check that every group has enough observations
    check_groups(data)
 
    # 3. Fit the mixed models (random intercept per animal)
    results = fit_models(data)
 
    # 4. Turn the model results into one answer per research question
    write_answers(results)
 
    # 5. Figures: distance and speed by group, effect sizes, and model lines
    make_plots(data)
    plot_effects(results)
    plot_model_lines(results, data)
    return data, results
 
 
if __name__ == "__main__":
    run_combined_analysis()