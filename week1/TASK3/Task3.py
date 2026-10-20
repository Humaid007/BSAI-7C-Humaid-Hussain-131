from pathlib import Path
import shutil
import zipfile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

SOURCE_DATA_PATH = Path(
    r"C:\Users\Lenovo\Downloads\DV\data-visualization-main\week1\assignments\data\penguins.csv"
)
TASK_DIR = Path(
    r"C:\Users\Lenovo\Downloads\DV\data-visualization-main\week1\assignments\Task 3"
)
TASK_DIR.mkdir(parents=True, exist_ok=True)

if not SOURCE_DATA_PATH.exists():
    raise FileNotFoundError(
        f"Could not find penguins.csv at: {SOURCE_DATA_PATH}. "
        "Update SOURCE_DATA_PATH at the top of task3.py."
    )

shutil.copy2(SOURCE_DATA_PATH, TASK_DIR / "penguins.csv")
BASE_DIR = TASK_DIR
df = pd.read_csv(BASE_DIR / "penguins.csv")
# Normalize species and sex labels so capitalization does not break grouping.
df["species"] = df["species"].astype("string").str.strip().str.title()
df["sex"] = df["sex"].astype("string").str.strip().str.upper()
required_columns = {"species", "island", "bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g", "sex"}
missing_columns = required_columns.difference(df.columns)
if missing_columns:
    raise ValueError(f"penguins.csv is missing required columns: {sorted(missing_columns)}")

measurement_cols = [
    "bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"
]
all_measurements_missing = df[measurement_cols].isna().all(axis=1)
df_measure = df.loc[~all_measurements_missing].copy()
df_sex = df_measure.loc[df_measure["sex"].notna()].copy()
species_order = ["Adelie", "Chinstrap", "Gentoo"]
colors = {"Adelie": "tab:blue", "Chinstrap": "tab:orange", "Gentoo": "tab:green"}

print("Rows:", len(df), "| Species:", df["species"].nunique())
print("Rows with all four measurements missing:", int(all_measurements_missing.sum()))
print("Rows with missing sex:", int(df["sex"].isna().sum()))
print("Missing values by column:\\n", df.isna().sum())

fig, ax = plt.subplots(figsize=(9, 5.8))
ax.hist(df_measure["body_mass_g"].dropna(), bins=24, edgecolor="white")
ax.set(title="Distribution of Penguin Body Mass", xlabel="Body mass (g)", ylabel="Number of penguins")
ax.text(0.01, -0.19, "Missing-data decision: 2 penguins with all four measurements missing are excluded; measured body masses only.",
        transform=ax.transAxes, fontsize=8.5, va="top")
ax.grid(axis="y", alpha=0.2)
fig.tight_layout()
fig.savefig(BASE_DIR / "01_body_mass_distribution.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 6))
data = [df_measure.loc[df_measure["species"] == s, "body_mass_g"].dropna() for s in species_order]
ax.hist(data, bins=18, label=species_order, alpha=0.62, edgecolor="white")
ax.set(title="Body Mass Distribution by Penguin Species", xlabel="Body mass (g)", ylabel="Number of penguins")
ax.legend(title="Species")
ax.text(0.01, -0.19, "Missing-data decision: 2 penguins with all four measurements missing are excluded.",
        transform=ax.transAxes, fontsize=8.5, va="top")
ax.grid(axis="y", alpha=0.2)
fig.tight_layout()
fig.savefig(BASE_DIR / "02_body_mass_by_species.png", dpi=180, bbox_inches="tight")
plt.close(fig)

gall = df_measure.dropna(subset=["bill_length_mm", "bill_depth_mm"])
overall_corr = gall[["bill_length_mm", "bill_depth_mm"]].corr().iloc[0, 1]
fig, ax = plt.subplots(figsize=(10, 7))
for species in species_order:
    g = gall[gall["species"] == species]
    r = g[["bill_length_mm", "bill_depth_mm"]].corr().iloc[0, 1]
    ax.scatter(g["bill_length_mm"], g["bill_depth_mm"], s=36, alpha=0.72,
               label=f"{species} (r={r:.2f})", color=colors[species],
               edgecolors="white", linewidths=0.35)
    slope, intercept = np.polyfit(g["bill_length_mm"], g["bill_depth_mm"], 1)
    xx = np.linspace(g["bill_length_mm"].min(), g["bill_length_mm"].max(), 80)
    ax.plot(xx, slope * xx + intercept, color=colors[species], linewidth=2)
slope, intercept = np.polyfit(gall["bill_length_mm"], gall["bill_depth_mm"], 1)
xx = np.linspace(gall["bill_length_mm"].min(), gall["bill_length_mm"].max(), 100)
ax.plot(xx, slope * xx + intercept, color="black", linestyle="--", linewidth=2.2,
        label=f"All penguins (r={overall_corr:.2f})")
ax.set(title="Bill Length vs Bill Depth: Overall and Within Species",
       xlabel="Bill length (mm)", ylabel="Bill depth (mm)")
ax.legend()
ax.text(0.01, -0.17, "Missing-data decision: 2 penguins with all four measurements missing are excluded. Coloured lines are within-species fits; dashed black is the pooled fit.",
        transform=ax.transAxes, fontsize=8.5, va="top")
ax.grid(alpha=0.18)
fig.tight_layout()
fig.savefig(BASE_DIR / "03_bill_length_vs_depth.png", dpi=180, bbox_inches="tight")
plt.close(fig)

sex_summary = df_sex.groupby(["species", "sex"])["body_mass_g"].agg(
    count="count", mean_body_mass_g="mean"
).reset_index()
sex_summary.to_csv(BASE_DIR / "mean_body_mass_by_species_and_sex.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 6))
xpos = np.arange(len(species_order))
bar_width = 0.34
for j, sex in enumerate(["FEMALE", "MALE"]):
    sub = sex_summary[sex_summary["sex"] == sex].set_index("species")
    means = [sub.loc[s, "mean_body_mass_g"] if s in sub.index else np.nan for s in species_order]
    counts = [int(sub.loc[s, "count"]) if s in sub.index else 0 for s in species_order]
    bars = ax.bar(xpos + (j - 0.5) * bar_width, means, width=bar_width, label=sex.title(), alpha=0.86)
    for bar, n, mean in zip(bars, counts, means):
        if np.isfinite(mean):
            ax.annotate(f"n={n}", (bar.get_x() + bar.get_width()/2, bar.get_height()),
                        xytext=(0, 4), textcoords="offset points", ha="center", fontsize=8)
ax.set_xticks(xpos)
ax.set_xticklabels(species_order)
ax.set(title="Average Body Mass by Species and Sex", xlabel="Species", ylabel="Mean body mass (g)")
ax.legend(title="Sex")
ax.text(0.01, -0.17, "Missing-data decision: 11 penguins with unknown sex are excluded from this chart; labels show known-sex sample sizes.",
        transform=ax.transAxes, fontsize=8.5, va="top")
ax.grid(axis="y", alpha=0.2)
fig.tight_layout()
fig.savefig(BASE_DIR / "04_mean_body_mass_species_sex.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Save summaries
df_measure.groupby("species")["body_mass_g"].agg(
    count="count", mean_body_mass_g="mean", median_body_mass_g="median"
).reset_index().to_csv(BASE_DIR / "body_mass_summary_by_species.csv", index=False)
pd.DataFrame({"column": df.columns, "missing_count": [int(df[c].isna().sum()) for c in df.columns]}).to_csv(
    BASE_DIR / "missing_data_summary.csv", index=False
)

print("\nOverall bill-length/depth correlation:", round(float(overall_corr), 3))
print("Within-species correlations:")
for species, g in gall.groupby("species"):
    print(f"  {species}: {g[['bill_length_mm','bill_depth_mm']].corr().iloc[0,1]:.3f}")
print("\nMean body mass by species and sex:")
print(sex_summary.round(2).to_string(index=False))
print("\nCharts and CSV summaries saved in:", BASE_DIR)


# Create README with the data decisions and interpretation.
measurement_cols = [
    "bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"
]
all_measurements_missing = df[measurement_cols].isna().all(axis=1)
known_measurements = df.loc[~all_measurements_missing].copy()
overall_r = known_measurements[["bill_length_mm", "bill_depth_mm"]].corr().iloc[0, 1]
within_r = {}
for species, group in known_measurements.groupby("species"):
    within_r[species] = group[["bill_length_mm", "bill_depth_mm"]].corr().iloc[0, 1]

correlation_text = "\n".join(
    f"- {species}: r = {value:.3f}" for species, value in within_r.items()
)
readme = f"""# Task 3 — Penguin Distributions and Simpson's Paradox

## Missing data and decisions

The dataset contains {len(df)} rows.

- Two penguins have all four numeric measurements missing. They are excluded from charts that require those measurements; no measurements are imputed.
- Eleven penguins have missing sex. They remain in charts that do not require sex, but are excluded from the species-and-sex body-mass comparison because their sex group is unknown.
- Each chart includes a note explaining the relevant missing-data decision.

## 1. Overall body-mass distribution

The overall histogram combines all species. It can show more than one hump because species have different typical body masses.

## 2. Body mass split by species

Splitting the distribution by species makes the mixture clearer. Gentoo penguins are generally heavier, while Adelie and Chinstrap penguins tend to have lower and partly overlapping body masses. The combined shape is therefore influenced by differences between species rather than representing one homogeneous group.

## 3. Bill length versus bill depth

The overall Pearson correlation is **{overall_r:.3f}**, which is negative. Within each species, the correlations are positive:

{correlation_text}

This is an example of **Simpson's paradox**: an association in the combined data reverses direction when the data are examined within subgroups. Species have different typical bill dimensions and occupy different regions of the scatter plot. The between-species differences can dominate the positive relationships within species, creating a negative pooled association.

Neither result is a calculation error. They describe different levels of the data. Splitting the plot by species prevents the overall pattern from being mistaken for the relationship within each species. See the Stanford Encyclopedia of Philosophy: https://plato.stanford.edu/entries/paradox-simpson/

## 4. Average body mass by species and sex

The grouped bar chart compares average body mass for females and males within each species. Sample sizes are shown above the bars. Penguins with missing sex are excluded only from this chart rather than being assigned an invented sex.

## Files

- `01_body_mass_distribution.png`
- `02_body_mass_by_species.png`
- `03_bill_length_vs_depth.png`
- `04_mean_body_mass_species_sex.png`
- `body_mass_summary_by_species.csv`
- `mean_body_mass_by_species_and_sex.csv`
- `missing_data_summary.csv`
- `penguins.csv`
- `task3.py`

## Run

Install dependencies if needed:

    pip install pandas numpy matplotlib

Then run:

    python task3.py
"""
(BASE_DIR / "README.md").write_text(readme, encoding="utf-8")

# Package all deliverables after charts, tables, and README exist.
ZIP_PATH = TASK_DIR.parent / "week1_task3_penguins.zip"
if ZIP_PATH.exists():
    ZIP_PATH.unlink()

with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for file_path in sorted(TASK_DIR.rglob("*")):
        if file_path.is_file():
            zf.write(file_path, Path(TASK_DIR.name) / file_path.relative_to(TASK_DIR))

print("\nTask folder:", TASK_DIR)
print("ZIP package:", ZIP_PATH)
print("Files:")
for file_path in sorted(TASK_DIR.iterdir()):
    print("-", file_path.name)
