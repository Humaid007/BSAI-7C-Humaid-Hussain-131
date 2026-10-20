from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calendar
import sys


POSSIBLE_CSV_PATHS = [
    Path(r"C:\Users\Lenovo\Downloads\DV\data-visualization-main\week1\assignments\data\flights.csv"),
    Path.cwd() / "flights.csv",
    Path.cwd() / "data" / "flights.csv",
    Path.cwd() / "week1" / "assignments" / "data" / "flights.csv",
]
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
    POSSIBLE_CSV_PATHS.extend([SCRIPT_DIR / "flights.csv", SCRIPT_DIR.parent / "flights.csv"])
except NameError:
    SCRIPT_DIR = Path.cwd()

CSV = next((p for p in POSSIBLE_CSV_PATHS if p.exists()), None)
if CSV is None:
    tried = "\n".join(str(p) for p in POSSIBLE_CSV_PATHS)
    raise FileNotFoundError(
        "Could not find flights.csv. Put it beside task5.py or update POSSIBLE_CSV_PATHS.\nChecked:\n" + tried
    )

OUT = Path.cwd() / "Task 5 - Flights outputs"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CSV)
required = {"year", "month", "passengers"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"flights.csv is missing required columns: {sorted(missing)}")

month_names = list(calendar.month_name)[1:]
month_map = {name.lower(): i for i, name in enumerate(month_names, start=1)}
# Accept full month names or numeric month values.
if pd.api.types.is_numeric_dtype(df["month"]):
    df["month_num"] = pd.to_numeric(df["month"], errors="coerce")
else:
    df["month_num"] = df["month"].astype(str).str.strip().str.lower().map(month_map)
if df["month_num"].isna().any():
    bad = df.loc[df["month_num"].isna(), "month"].unique().tolist()
    raise ValueError(f"Unrecognized month values: {bad}")

df["year"] = pd.to_numeric(df["year"], errors="raise").astype(int)
df["month_num"] = df["month_num"].astype(int)
df["passengers"] = pd.to_numeric(df["passengers"], errors="raise")
df["date"] = pd.to_datetime(dict(year=df["year"], month=df["month_num"], day=1))
df["month_name"] = df["month_num"].map(lambda m: month_names[m - 1])
df = df.sort_values("date").reset_index(drop=True)

if df["date"].duplicated().any():
    raise ValueError("There are duplicate year-month records; each month should appear once.")

missing_summary = pd.DataFrame({"column": df.columns, "missing_count": [int(df[c].isna().sum()) for c in df.columns]})
missing_summary.to_csv(OUT / "missing_data_summary.csv", index=False)

fig, ax = plt.subplots(figsize=(11, 6))
ax.plot(df["date"], df["passengers"], linewidth=1.9)
ax.set(title="Monthly Airline Passengers, 1949–1960", xlabel="Year", ylabel="Passengers (thousands)")
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "01_passengers_over_time.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(11, 6.5))
for year, part in df.groupby("year"):
    part = part.sort_values("month_num")
    ax.plot(part["month_num"], part["passengers"], marker="o", linewidth=1.5, alpha=0.78, label=str(year))
ax.set_xticks(range(1, 13), month_names)
ax.tick_params(axis="x", rotation=35)
ax.set(title="Seasonal Cycle by Year", xlabel="Month", ylabel="Passengers (thousands)")
ax.grid(alpha=0.22)
ax.legend(title="Year", ncol=3, fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(OUT / "02_seasonal_cycle_by_year.png", dpi=180, bbox_inches="tight")
plt.close(fig)

year_mean = df.groupby("year")["passengers"].transform("mean")
df["seasonal_index_pct"] = df["passengers"] / year_mean * 100
seasonal = df.groupby(["month_num", "month_name"], as_index=False).agg(
    mean_passengers=("passengers", "mean"), mean_seasonal_index_pct=("seasonal_index_pct", "mean"),
    median_seasonal_index_pct=("seasonal_index_pct", "median"), years_observed=("year", "nunique")
).sort_values("month_num")
seasonal.to_csv(OUT / "seasonal_summary_by_month.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.bar(seasonal["month_name"], seasonal["mean_seasonal_index_pct"], alpha=0.85)
ax.axhline(100, linestyle="--", linewidth=1.5, label="Annual average (100%)")
ax.bar_label(bars, labels=[f"{v:.0f}%" for v in seasonal["mean_seasonal_index_pct"]], padding=3, fontsize=8)
ax.set(title="Which Month Is Busiest? Average Seasonal Index (1949–1960)", xlabel="Month", ylabel="Passengers as % of that year's average")
ax.tick_params(axis="x", rotation=35)
ax.set_ylim(0, max(seasonal["mean_seasonal_index_pct"]) * 1.18)
ax.grid(axis="y", alpha=0.22)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUT / "03_busiest_month_seasonal_index.png", dpi=180, bbox_inches="tight")
plt.close(fig)

peak = seasonal.loc[seasonal["mean_seasonal_index_pct"].idxmax()]
peak_month = peak["month_name"]
first_year, last_year = int(df["year"].min()), int(df["year"].max())
first_avg = float(df.loc[df["year"] == first_year, "passengers"].mean())
last_avg = float(df.loc[df["year"] == last_year, "passengers"].mean())
first_peak = float(df.loc[df["year"] == first_year, "passengers"].max())
last_peak = float(df.loc[df["year"] == last_year, "passengers"].max())
first_trough = float(df.loc[df["year"] == first_year, "passengers"].min())
last_trough = float(df.loc[df["year"] == last_year, "passengers"].min())
first_abs_swing = first_peak - first_trough
last_abs_swing = last_peak - last_trough
first_rel_swing = first_abs_swing / first_avg * 100
last_rel_swing = last_abs_swing / last_avg * 100

summary = pd.DataFrame([
    {"metric": "mean passengers per month", "first_year": first_year, "first_value": first_avg, "last_year": last_year, "last_value": last_avg},
    {"metric": "within-year peak minus trough", "first_year": first_year, "first_value": first_abs_swing, "last_year": last_year, "last_value": last_abs_swing},
    {"metric": "peak-trough swing as percent of annual mean", "first_year": first_year, "first_value": first_rel_swing, "last_year": last_year, "last_value": last_rel_swing},
])
summary.to_csv(OUT / "growth_and_seasonality_summary.csv", index=False)

readme = f'''# Task 5 — A Real Time Series (Flights)

## Data preparation

The dataset contains {len(df)} monthly records from {first_year} through {last_year}. I converted `year` and `month` into a real datetime column by assigning the first day of each month, then sorted chronologically. This is important because month names alone do not form a continuous, ordered time axis across years.

## 1. Monthly passengers over time

**Chart:** `01_passengers_over_time.png` — a single line chart. A line chart suits ordered monthly observations and shows both the long-term growth and repeating annual pattern. The monthly average rose from {first_avg:.1f} passengers (thousands) in {first_year} to {last_avg:.1f} in {last_year}.

## 2. Seasonal cycle by year

**Chart:** `02_seasonal_cycle_by_year.png` — one line per year with months aligned on the x-axis. This makes within-year peaks and troughs easier to compare across years, but the overlapping lines and changing overall scale make it busy.

## 3. Which month is consistently busiest?

**Chart:** `03_busiest_month_seasonal_index.png` — a bar chart of each month's average passenger count relative to that year's average (annual average = 100%). Normalizing within each year reduces the influence of the long-term growth trend and makes the recurring seasonal pattern easier to compare. **{peak_month}** has the highest average seasonal index ({float(peak['mean_seasonal_index_pct']):.1f}% of the annual average).

## 4. Which chart belongs in a report?

I would put **Chart 1 (monthly passengers over time)** in a general report because it gives the essential overview: the long-term increase and the repeating seasonal pattern in one compact graphic. I would not put Charts 2 and 3 beside it in the same short report unless the report specifically discusses seasonality: Chart 2 is detailed and visually busy, while Chart 3 repeats the seasonal story in a more focused, normalized form. Use Chart 2 for a technical seasonal comparison and Chart 3 when the main question is which months are unusually busy.

## Written question: Is the seasonal swing growing, or is the airline growing?

The absolute peak-to-trough swing grew from {first_abs_swing:.1f} in {first_year} to {last_abs_swing:.1f} in {last_year}, while the annual mean also rose substantially. That alone cannot tell us whether seasonality itself became stronger: a larger airline naturally has a larger absolute seasonal swing. Compare **relative seasonality** by dividing each month's passengers by that year's average (or annual total) and plotting the normalized monthly index over time. The chart in Question 3 averages that index across years; to settle whether seasonality strengthens over time, the next chart would show the normalized index for each month-year, with one line per year or a year-by-month heatmap. If the peak-to-trough percentage gap increases, seasonality is strengthening; if it stays roughly similar, the larger absolute swing is mainly explained by overall growth.

The relative peak-to-trough swing was {first_rel_swing:.1f}% of the annual mean in {first_year} and {last_rel_swing:.1f}% in {last_year}. This comparison is a useful first check, but the full normalized year-by-month chart is the stronger way to inspect the pattern across all years.

## Output files

- `01_passengers_over_time.png`
- `02_seasonal_cycle_by_year.png`
- `03_busiest_month_seasonal_index.png`
- `seasonal_summary_by_month.csv`
- `growth_and_seasonality_summary.csv`
- `missing_data_summary.csv`
- `flights.csv` and `task5.py`

## Run

Install dependencies with `pip install pandas numpy matplotlib`. Keep `flights.csv` beside `task5.py`, then run `python task5.py`.
'''
(OUT / "README.md").write_text(readme, encoding="utf-8")

print(f"Loaded: {CSV}")
print(f"Rows: {len(df)} | years: {first_year}-{last_year}")
print(f"Busiest month by average normalized seasonal index: {peak_month} ({float(peak['mean_seasonal_index_pct']):.1f}% of annual average)")
print(f"Mean passengers: {first_avg:.1f} ({first_year}) -> {last_avg:.1f} ({last_year})")
print(f"Outputs saved to: {OUT.resolve()}")
