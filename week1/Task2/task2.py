from pathlib import Path
import zipfile, textwrap

base = Path("/mnt/data")
script = r'''from pathlib import Path
import shutil
import zipfile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DATA_PATH = Path(
    r"C:\Users\Lenovo\Downloads\DV\data-visualization-main\week1\assignments\data\gapminder.csv"
)
TASK_DIR = Path(
    r"C:\Users\Lenovo\Downloads\DV\data-visualization-main\week1\assignments\Task 2"
)
ZIP_PATH = TASK_DIR.parent / "week1_task2_gapminder.zip"

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Could not find gapminder.csv at:\n{DATA_PATH}\n"
        "Update DATA_PATH at the top of this script."
    )

TASK_DIR.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(DATA_PATH)

required_columns = {"country", "continent", "year", "lifeExp", "pop", "gdpPercap"}
missing_columns = required_columns - set(df.columns)
if missing_columns:
    raise ValueError(f"Dataset is missing required columns: {sorted(missing_columns)}")

shutil.copy2(DATA_PATH, TASK_DIR / "gapminder.csv")

print("DATASET CHECK")
print("Rows:", len(df))
print("Countries:", df["country"].nunique())
print("Years:", sorted(df["year"].unique().tolist()))
print("Missing values:", int(df.isna().sum().sum()))
print("Output folder:", TASK_DIR)

fig, ax = plt.subplots(figsize=(14, 8))
for country, group in df.sort_values("year").groupby("country"):
    ax.plot(group["year"], group["lifeExp"], linewidth=1, alpha=0.8, label=country)

ax.set(
    title="Life Expectancy Over Time — All Countries",
    xlabel="Year",
    ylabel="Life expectancy (years)"
)
ax.legend(
    loc="center left", bbox_to_anchor=(1.02, 0.5),
    fontsize=5, ncol=2, frameon=False
)
fig.tight_layout()
fig.savefig(TASK_DIR / "01_spaghetti_all_countries.png", dpi=180, bbox_inches="tight")
plt.close(fig)

continent = (
    df.groupby(["continent", "year"], as_index=False)["lifeExp"]
    .mean()
    .rename(columns={"lifeExp": "average_lifeExp"})
)

fig, ax = plt.subplots(figsize=(10, 6))
for name, group in continent.groupby("continent"):
    ax.plot(group["year"], group["average_lifeExp"], marker="o", linewidth=2.5, label=name)

ax.set(
    title="Average Life Expectancy Over Time by Continent",
    xlabel="Year",
    ylabel="Average life expectancy (years)"
)
ax.legend(title="Continent", frameon=False)
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig(TASK_DIR / "02a_continent_averages.png", dpi=180, bbox_inches="tight")
plt.close(fig)
continent.to_csv(TASK_DIR / "continent_life_expectancy.csv", index=False)

selected = ["China", "United States", "Afghanistan"]
colors = {"China": "tab:red", "United States": "tab:blue", "Afghanistan": "tab:green"}

fig, ax = plt.subplots(figsize=(11, 7))
for country, group in df.sort_values("year").groupby("country"):
    if country not in selected:
        ax.plot(
            group["year"], group["lifeExp"],
            color="lightgrey", linewidth=1, alpha=0.7, zorder=1
        )

for country in selected:
    group = df[df["country"] == country].sort_values("year")
    if group.empty:
        print(f"Warning: {country} was not found in the dataset.")
        continue
    ax.plot(
        group["year"], group["lifeExp"],
        color=colors[country], linewidth=2.8, zorder=3
    )
    last = group.iloc[-1]
    ax.annotate(
        country, (last["year"], last["lifeExp"]),
        xytext=(7, 0), textcoords="offset points",
        va="center", fontsize=10, color=colors[country]
    )

ax.set(
    title="Life Expectancy: Three Countries Highlighted",
    xlabel="Year",
    ylabel="Life expectancy (years)"
)
ax.grid(alpha=0.2)
fig.tight_layout()
fig.savefig(TASK_DIR / "02b_highlight_three_countries.png", dpi=180, bbox_inches="tight")
plt.close(fig)

if (df["gdpPercap"] <= 0).any():
    raise ValueError("Log10 histogram requires all GDP per capita values to be positive.")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].hist(df["gdpPercap"], bins=35, edgecolor="white")
axes[0].set(
    title="GDP per Capita (Raw Scale)",
    xlabel="GDP per capita",
    ylabel="Number of observations"
)

axes[1].hist(np.log10(df["gdpPercap"]), bins=35, edgecolor="white")
axes[1].set(
    title="GDP per Capita (Log10 Scale)",
    xlabel="log10(GDP per capita)",
    ylabel="Number of observations"
)
fig.tight_layout()
fig.savefig(TASK_DIR / "03_gdp_histograms_raw_vs_log.png", dpi=180, bbox_inches="tight")
plt.close(fig)

yearly = (
    df.groupby("year")["gdpPercap"]
    .agg(richest="max", poorest="min")
    .reset_index()
)
yearly["absolute_gap"] = yearly["richest"] - yearly["poorest"]
yearly["ratio"] = yearly["richest"] / yearly["poorest"]

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(yearly["year"], yearly["ratio"], marker="o", linewidth=2.5)
ax.set(
    title="Richest-to-Poorest GDP per Capita Ratio Over Time",
    xlabel="Year",
    ylabel="Richest GDP per capita / Poorest GDP per capita"
)
ax.set_yscale("log")
ax.grid(alpha=0.25, which="both")
fig.tight_layout()
fig.savefig(TASK_DIR / "04_richest_poorest_gap.png", dpi=180, bbox_inches="tight")
plt.close(fig)

yearly.to_csv(TASK_DIR / "richest_poorest_gap.csv", index=False)

print("\nGDP PER CAPITA")
print("Minimum:", round(float(df["gdpPercap"].min()), 2))
print("Maximum:", round(float(df["gdpPercap"].max()), 2))

print("\nRICHEST-TO-POOREST GDP PER CAPITA RATIO BY YEAR")
print(yearly[["year", "richest", "poorest", "ratio"]].round(2).to_string(index=False))

print("\nAVERAGE LIFE EXPECTANCY BY CONTINENT (1952 AND 2007)")
print(
    continent[continent["year"].isin([1952, 2007])]
    .pivot(index="continent", columns="year", values="average_lifeExp")
    .round(2)
)

ratio_1952 = float(yearly.loc[yearly["year"] == yearly["year"].min(), "ratio"].iloc[0])
ratio_2007 = float(yearly.loc[yearly["year"] == yearly["year"].max(), "ratio"].iloc[0])
first_year = int(yearly["year"].min())
last_year = int(yearly["year"].max())

readme = f"""# Task 2 — Trends and the Spaghetti Problem

## 1. What is wrong with the spaghetti chart?

The chart draws one line for every country, making it crowded and difficult to read. Lines overlap, and the large legend is difficult to scan. It is hard to identify an overall trend or compare individual countries. The chart contains a lot of data, but visual clutter makes it difficult to interpret.

## 2(a). Aggregate by continent

The continent chart replaces the country lines with one average life-expectancy line per continent. This makes broad regional trends easier to compare. The chart shows how average life expectancy changes over time across regions.

Aggregation is clearer for regional patterns, but it hides differences between countries within each continent. A continent average can conceal countries that perform very differently from the regional average.

## 2(b). Highlight three countries

The highlight chart keeps the other country lines in grey and emphasizes China, the United States, and Afghanistan with colour and direct labels. This retains the context of other countries while making the selected trajectories easier to follow.

Unlike aggregation, highlighting preserves individual country trends. However, the grey background can still be busy, and the chart does not summarize regional patterns as clearly as the continent chart.

## 3. Aggregate versus highlight

The aggregate chart is best for comparing broad regional trends and reducing clutter, but it hides country-level variation. The highlight chart is best for examining selected countries while retaining wider context, but it does not provide a concise summary of all countries. The best chart depends on the question being asked.

## 4. Has the gap between richest and poorest countries narrowed?

This analysis defines the gap as the ratio of the highest to the lowest GDP per capita in each year. The ratio was approximately {ratio_1952:.2f} in {first_year} and {ratio_2007:.2f} in {last_year}. Therefore, by this measure, the richest-to-poorest ratio was lower at the end than at the beginning, although the trend was not steadily downward.

A logarithmic y-axis is used because the ratios vary substantially across years. The countries at the extremes may change from year to year, so this measure does not describe the gap between typical countries.

## 5. GDP per capita histogram and log scale

GDP per capita is strongly right-skewed: many observations have lower values, while a smaller number of very high values stretch the distribution to the right. On the raw scale, high values compress much of the distribution near the left side of the histogram.

A log10 transformation spreads lower values apart and compresses higher values, making the distribution easier to inspect. It is valid for this dataset because GDP per capita values are positive. The log transformation is useful for visualizing skew, but it changes how distances between values appear.

## Files produced

- `01_spaghetti_all_countries.png`
- `02a_continent_averages.png`
- `02b_highlight_three_countries.png`
- `03_gdp_histograms_raw_vs_log.png`
- `04_richest_poorest_gap.png`
- `continent_life_expectancy.csv`
- `richest_poorest_gap.csv`
- `gapminder.csv`


Install dependencies if needed:

    pip install pandas numpy matplotlib

Keep `gapminder.csv` beside `task2.py`, then run:

    python task2.py
"""
(TASK_DIR / "README.md").write_text(readme, encoding="utf-8")

# Save this combined script in the task folder for future use.
# This file contains the same analysis so the project is self-contained.
current_script = Path(__file__) if "__file__" in globals() else None
if current_script and current_script.exists():
    shutil.copy2(current_script, TASK_DIR / "task2.py")
else:
    # In a notebook, write the script source separately from this orchestration cell.
    # The current notebook cell performs the analysis and packaging directly.
    (TASK_DIR / "task2.py").write_text(
        "# Run the combined Task 2 notebook cell to regenerate charts and tables.\n"
        "# This project uses gapminder.csv in this folder.\n",
        encoding="utf-8"
    )


if ZIP_PATH.exists():
    ZIP_PATH.unlink()

with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for file_path in sorted(TASK_DIR.rglob("*")):
        if file_path.is_file() and file_path != ZIP_PATH:
            zf.write(file_path, Path(TASK_DIR.name) / file_path.relative_to(TASK_DIR))

print("\nAll charts, tables, README, and dataset saved in:")
print(TASK_DIR)
print("\nZIP package created:")
print(ZIP_PATH)
print("\nFiles in task folder:")
for file_path in sorted(TASK_DIR.iterdir()):
    print("-", file_path.name)
'''
path = base / "combined_task2.py"
path.write_text(script, encoding="utf-8")
print(path)
