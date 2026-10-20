from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
df = pd.read_csv(BASE_DIR / "gapminder.csv")

print("Rows:", len(df))
print("Countries:", df["country"].nunique())
print("Missing values:", int(df.isna().sum().sum()))

fig, ax = plt.subplots(figsize=(14, 8))

for country, group in df.sort_values("year").groupby("country"):
    ax.plot(
        group["year"], group["lifeExp"],
        linewidth=1, alpha=0.8, label=country
    )

ax.set(
    title="Life Expectancy Over Time — All 142 Countries",
    xlabel="Year",
    ylabel="Life expectancy (years)"
)

ax.legend(
    loc="center left",
    bbox_to_anchor=(1.02, 0.5),
    fontsize=5,
    ncol=2,
    frameon=False
)

fig.tight_layout()
fig.savefig(
    BASE_DIR / "01_spaghetti_all_countries.png",
    dpi=180, bbox_inches="tight"
)
plt.close(fig)

continent = (
    df.groupby(["continent", "year"], as_index=False)["lifeExp"]
    .mean()
)

fig, ax = plt.subplots(figsize=(10, 6))

for name, group in continent.groupby("continent"):
    ax.plot(
        group["year"], group["lifeExp"],
        marker="o", linewidth=2.5, label=name
    )

ax.set(
    title="Average Life Expectancy Over Time by Continent",
    xlabel="Year",
    ylabel="Average life expectancy (years)"
)
ax.legend(title="Continent", frameon=False)
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig(
    BASE_DIR / "02a_continent_averages.png",
    dpi=180, bbox_inches="tight"
)
plt.close(fig)

continent.to_csv(
    BASE_DIR / "continent_life_expectancy.csv",
    index=False
)

selected = ["China", "United States", "Afghanistan"]

colors = {
    "China": "tab:red",
    "United States": "tab:blue",
    "Afghanistan": "tab:green"
}

fig, ax = plt.subplots(figsize=(11, 7))

for country, group in df.sort_values("year").groupby("country"):
    if country not in selected:
        ax.plot(
            group["year"], group["lifeExp"],
            color="lightgrey",
            linewidth=1,
            alpha=0.7,
            zorder=1
        )
for country in selected:
    group = df[df["country"] == country].sort_values("year")

    if group.empty:
        print("Warning: country not found:", country)
        continue

    ax.plot(
        group["year"], group["lifeExp"],
        color=colors[country],
        linewidth=2.8,
        zorder=3
    )

    last = group.iloc[-1]

    ax.annotate(
        country,
        (last["year"], last["lifeExp"]),
        xytext=(7, 0),
        textcoords="offset points",
        va="center",
        fontsize=10,
        color=colors[country]
    )

ax.set(
    title="Life Expectancy: Three Countries Highlighted",
    xlabel="Year",
    ylabel="Life expectancy (years)"
)
ax.grid(alpha=0.2)
fig.tight_layout()
fig.savefig(
    BASE_DIR / "02b_highlight_three_countries.png",
    dpi=180, bbox_inches="tight"
)
plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].hist(df["gdpPercap"], bins=35, edgecolor="white")
axes[0].set(
    title="GDP per Capita (Raw Scale)",
    xlabel="GDP per capita",
    ylabel="Number of observations"
)

axes[1].hist(
    np.log10(df["gdpPercap"]),
    bins=35,
    edgecolor="white"
)
axes[1].set(
    title="GDP per Capita (Log10 Scale)",
    xlabel="log10(GDP per capita)",
    ylabel="Number of observations"
)

fig.tight_layout()
fig.savefig(
    BASE_DIR / "03_gdp_histograms_raw_vs_log.png",
    dpi=180, bbox_inches="tight"
)
plt.close(fig)


yearly = (
    df.groupby("year")["gdpPercap"]
    .agg(richest="max", poorest="min")
    .reset_index()
)

yearly["absolute_gap"] = yearly["richest"] - yearly["poorest"]
yearly["ratio"] = yearly["richest"] / yearly["poorest"]

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(
    yearly["year"], yearly["ratio"],
    marker="o", linewidth=2.5
)

ax.set(
    title="Richest-to-Poorest GDP per Capita Ratio Over Time",
    xlabel="Year",
    ylabel="Richest GDP per capita / Poorest GDP per capita"
)

ax.set_yscale("log")
ax.grid(alpha=0.25, which="both")
fig.tight_layout()
fig.savefig(
    BASE_DIR / "04_richest_poorest_gap.png",
    dpi=180, bbox_inches="tight"
)
plt.close(fig)

yearly.to_csv(
    BASE_DIR / "richest_poorest_gap.csv",
    index=False
)

print("\nRichest-to-poorest GDP per capita ratio by year:")
print(
    yearly[["year", "richest", "poorest", "ratio"]]
    .round(2)
    .to_string(index=False)
)

print("\nAll charts and output tables saved in:", BASE_DIR)
