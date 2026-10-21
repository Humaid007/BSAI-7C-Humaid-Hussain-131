from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "diamonds.csv"
OUT = HERE
df = pd.read_csv(DATA)
if df.isna().any().any():
    missing = df.isna().sum()
    print("Missing values by column:\n", missing[missing > 0])
else:
    print(f"Loaded {len(df):,} rows; no missing values.")

rng = np.random.default_rng(42)
context_n = min(2500, len(df))
context = df.iloc[rng.choice(len(df), size=context_n, replace=False)].copy()
df["carat_bin"] = (np.floor(df["carat"] * 10) / 10).round(1)
med = df.groupby("carat_bin", observed=True).agg(
    median_price=("price", "median"), n=("price", "size")
).reset_index()
med = med[(med["carat_bin"] >= 0.1) & (med["carat_bin"] <= 3.0)]
med.to_csv(OUT / "median_price_by_carat_bin.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 6))
bad = df.iloc[rng.choice(len(df), size=min(5000, len(df)), replace=False)]
ax.scatter(bad["carat"], bad["price"], s=16, alpha=0.65, color="#d62728", edgecolors="none")
ax.set_title("BAD EXAMPLE", fontsize=16, weight="bold")
ax.set_xlabel("Carat")
ax.set_ylabel("Price (USD)")
ax.text(0.01, -0.18,
        f"Question: How does diamond price change as carat increases? Displayed sample: {len(bad):,} of {len(df):,} rows (seed=42).",
        transform=ax.transAxes, fontsize=9, va="top")
fig.tight_layout()
fig.savefig(OUT / "bad_example.png", dpi=300, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(context["carat"], context["price"], s=10, color="#b9bec5", alpha=0.35,
           edgecolors="none", rasterized=True, label="Sampled individual diamonds")
ax.plot(med["carat_bin"], med["median_price"], color="#1769aa", linewidth=2.8,
        marker="o", markersize=4, label="Median price per 0.1-carat bin")
ax.set_title("Median diamond price rises with carat, with a steeper climb above 1 ct",
             fontsize=15, weight="bold", loc="left", pad=12)
ax.set_xlabel("Carat (0.1-carat bins; lower edge used for median)")
ax.set_ylabel("Price (USD; medians use all rows in each bin)")
ax.grid(axis="y", color="#e5e7eb", linewidth=0.8)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(frameon=False, loc="upper left")
ax.text(0.01, -0.22,
        f"n = {len(df):,} rows analyzed; no missing values. Grey context: {context_n:,} random rows (seed=42); blue medians use all rows. Bins: 0.1 carat.",
        transform=ax.transAxes, fontsize=8.5, va="top", color="#555555")
fig.tight_layout()
fig.savefig(OUT / "perception_redesign.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("Saved bad_example.png, perception_redesign.png, and median_price_by_carat_bin.csv.")
