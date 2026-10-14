# This code was mainly written by: Kahsu Berihu Berhe. See the commit history for a detailed contribution record.

"""Step 12: answers to the research questions, calculated on ONE common dataset.
 
Combines: 
    step 11 -> LANDSCAPE_OBSERVATIONS: speed, distance, landscape (urban / wildland) per GPS observation location
    step 10 -> DAY_NIGHT_CSV:   day / night label per GPS observation location
Output: answers.txt (one plain sentence per question), model summaries, group statistics, and plots.
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
# Matplotlib savefig:  https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html
# Mixed model with a random intercept per animal (formula "y ~ a * b" = a + b + a:b):
#       https://www.statsmodels.org/stable/mixed_linear.html
#       Bates, Maechler, Bolker & Walker (2015), J. Stat. Softw. 67(1): https://doi.org/10.18637/jss.v067.i01
# log(1 + x) for skewed distances:  https://numpy.org/doc/stable/reference/generated/numpy.log1p.html
# Percent change from a log-model coefficient = (exp(b) - 1) * 100:
#       https://stats.oarc.ucla.edu/other/mult-pkg/faq/general/faqhow-do-i-interpret-a-regression-model-when-some-variables-are-log-transformed/
#       https://data.library.virginia.edu/interpreting-log-transformations-in-a-linear-model
#   95% confidence interval of a coefficient:
# https://www.statsmodels.org/stable/generated/statsmodels.regression.mixed_linear_model.MixedLMResults.conf_int.html
# Summary as text(return tables as string) : https://www.statsmodels.org/devel/generated/statsmodels.iolib.summary.Summary.as_text.html

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd
import statsmodels.formula.api as smf

from python.src.config import DAY_NIGHT_CSV, ID_COL, LANDSCAPE_OBSERVATIONS, TIME_COL, KEYS, COMBINE_DIR, FIGURES, DELIVERABLES
from python.src.step06_distance import LABELS, add_distance_class

GROUPS = [(landscape, period) for landscape in ["urban", "wildland"] for period in ["day", "night"]]
MIN_PER_GROUP = 30 # fewer observation in a group makes the interaction terms unreliable
LAND_COLOURS = {"urban": "red", "wildland": "green"}
TIME_COLOURS = {"night": "navy", "day": "orange"}
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

    # Match GPS observation locationes
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

    print(f"GPS observation locationes: {len(data)} | Animals: {data[ID_COL].nunique()}")
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
    stats.to_csv(DELIVERABLES / "s13a_group_statistics.csv")

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
    (DELIVERABLES / "s13b_model_summaries.txt").write_text(text, encoding="utf-8")

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
    (DELIVERABLES / "s13c_answers.txt").write_text(
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

    fig.savefig(FIGURES / "s12d_distance_by_group.png", dpi=300, bbox_inches ="tight")
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
    fig.savefig(FIGURES / "s12e_speed_by_distance_class.png",
                dpi=300, bbox_inches="tight")
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
    fig.savefig(FIGURES / "s12f_effects.png", dpi=300, bbox_inches="tight")
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

        ax.plot(x, y, color=LAND_COLOURS[landscape],
                linestyle="-" if period == "day" else "--",
                linewidth=2, label=f"{landscape}, {period}")

    ax.set(xlabel="Distance to nearest road (m)",
           ylabel="Predicted speed (km/h)",
           title="Predicted speed by road distance and group")
    ax.legend(title="Group")
    ax.grid(alpha=0.3)
    fig.savefig(FIGURES / "s12g_model_lines.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def run_combined_analysis():
    """Answer all research questions on one dataset."""
    #COMBINE_DIR.mkdir(parents=True, exist_ok=True)
 
    # 1. Combine landscape (step 11) and day/night (step 10) per GPS observation location
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

def mean_ci(values):
    """Mean and 95% margin of error (1.96 x standard error)."""
    return values.mean(), 1.96 * values.sem()   

def labelled(groups):
    """Axis labels with the number of observation locationes: 'urban (n=4,718)'."""
    return [f"{name}\n(n={len(values):,})" for name, values in groups.items()]

def fitted_lines(params, flag, d):
    """Fitted lines for flag = 0 and flag = 1 from the model 'speed ~ distance_100m * flag'."""
    base = params["Intercept"] + params["distance_100m"] * d
    return base, base + params[flag] + params[f"distance_100m:{flag}"] * d


def model_line_panel(ax, data, results, formula_key, flag, colours):
    """Faint observations plus the two fitted lines (flag = 0 and flag = 1)."""
    sample = data.sample(min(len(data), 5000), random_state=1)   # faint points only give the background
    ax.scatter(sample["distance_m"], sample["speed_kmh"], s=4, alpha=0.08, color="grey", rasterized=True)
    x = np.linspace(0, data["distance_m"].quantile(0.99), 100)   # leave out the extreme tail
    low, high = fitted_lines(results[SPEED_MODELS[formula_key]].params, flag, x / 100)
    names = list(colours)   # first name = flag 0, second name = flag 1
    ax.plot(x, low, color=colours[names[0]], linewidth=2.5, label=f"{names[0]} (model)")
    ax.plot(x, high, color=colours[names[1]], linewidth=2.5, label=f"{names[1]} (model)")
    ax.set_xlabel("Distance to nearest road (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.set_ylim(0, data["speed_kmh"].quantile(0.99))
    ax.legend()


def figure_q1(data, results):
    """Q1: does speed change with distance to the nearest road?"""
    data = add_distance_class(data.copy())
    groups = {c: data.loc[data["distance_class"] == c, "speed_kmh"] for c in LABELS}
    groups = {c: v for c, v in groups.items() if len(v) > 1}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.boxplot(list(groups.values()), tick_labels=labelled(groups), showfliers=False)
    ax1.set_title("Speed distribution per distance class")
    ax2.errorbar(range(len(groups)), [mean_ci(v)[0] for v in groups.values()],
                 yerr=[mean_ci(v)[1] for v in groups.values()], fmt="o-", capsize=4)
    ax2.set_xticks(range(len(groups)))
    ax2.set_xticklabels(list(groups))
    ax2.set_title("Mean speed (95% interval) per distance class")
    for ax in (ax1, ax2):
        ax.set_xlabel("Distance to nearest road")
        ax.set_ylabel("Speed (km/h)")
        ax.tick_params(axis="x", rotation=30)
    fig.suptitle("Q1: Do caracals move at different speeds close to roads than far from roads?")
    return fig


def figure_q2(data, results):
    """Q2: does the speed-distance relationship differ between urban and wildland?"""
    groups = {g: data.loc[data["landscape"] == g] for g in LAND_COLOURS}
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(17, 5))
    ax1.boxplot([g["speed_kmh"] for g in groups.values()], tick_labels=labelled(groups), showfliers=False)
    ax1.set_ylabel("Speed (km/h)")
    ax1.set_title("Speed")
    ax2.boxplot([g["distance_m"] for g in groups.values()], tick_labels=labelled(groups), showfliers=False)
    ax2.set_ylabel("Distance to nearest road (m)")
    ax2.set_title("Distance to the nearest road")
    # Model lines: flag 0 = wildland, flag 1 = urban
    model_line_panel(ax3, data, results, "B", "is_urban", {"wildland": "green", "urban": "red"})
    ax3.set_title("Speed vs distance: model lines")
    fig.suptitle("Q2: Does the relationship between speed and road distance differ between urban and wildland?")
    return fig


def figure_q3(data, results):
    """Q3: does the speed-distance relationship differ between day and night?"""
    groups = {t: data.loc[data["day_night"] == t] for t in ("day", "night")}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    ax1.boxplot([g["speed_kmh"] for g in groups.values()], tick_labels=labelled(groups), showfliers=False)
    ax1.set_ylabel("Speed (km/h)")
    ax1.set_title("Speed by time of day")
    # Model lines: flag 0 = night, flag 1 = day
    model_line_panel(ax2, data, results, "C", "is_day", TIME_COLOURS)
    ax2.set_title("Speed vs distance: model lines")
    fig.suptitle("Q3: Does the relationship between speed and road distance differ between day and night?")
    return fig


def figure_q4(data, results):
    """Optional Q4: different road proximity by landscape and time of day?"""
    groups = {f"{l}\n{t}": data.loc[(data["landscape"] == l) & (data["day_night"] == t), "distance_m"]
              for l in LAND_COLOURS for t in ("day", "night")}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.boxplot(list(groups.values()), tick_labels=labelled(groups), showfliers=False)
    ax1.set_title("Distance to the nearest road")
    ax2.errorbar(range(len(groups)), [mean_ci(v)[0] for v in groups.values()],
                 yerr=[mean_ci(v)[1] for v in groups.values()], fmt="o", capsize=4)
    ax2.set_xticks(range(len(groups)))
    ax2.set_xticklabels(list(groups))
    ax2.set_title("Mean distance (95% interval)")
    ax2.set_ylim(bottom=0) # Source: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylim.html
    for ax in (ax1, ax2):
        ax.set_xlabel("Landscape and time of day")
        ax.set_ylabel("Distance to nearest road (m)")
    fig.suptitle("Q4: Do caracals show different road proximity by landscape and time of day?")
    return fig

FIGURES_PER_QUESTION = {
    "s13_q1_speed_vs_distance.png": figure_q1,
    "s13_q2_urban_vs_wildland.png": figure_q2,
    "s13_q3_day_vs_night.png": figure_q3,
    "s13_q4_road_proximity.png": figure_q4,
}

def make_question_graphs():
    """Create and save one figure per research question."""
    # 1. Data and models from step 12
    COMBINE_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data()
    results = fit_models(data)

    # 2. One figure per question, with the data credit, saved in the figures folder
    COMBINE_DIR.mkdir(parents=True, exist_ok=True)
    for filename, make_figure in FIGURES_PER_QUESTION.items():
        fig = make_figure(data, results)
        #fig.text(0.99, 0.01, CREDIT, ha="right", fontsize=7)
        fig.tight_layout()
        fig.savefig(FIGURES / filename, dpi=300, bbox_inches="tight") # Matplotlib savefig   # Matplotlib savefig
        plt.close(fig)
        print("Saved", filename)


if __name__ == "__main__":
    make_question_graphs(), run_combined_analysis()