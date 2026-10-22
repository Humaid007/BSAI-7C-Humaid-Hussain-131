from pathlib import Path
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
import tslib

BASE = Path(__file__).resolve().parent
DATA = BASE / "sessions_hourly.csv"
RESULTS = BASE / "results"
RESULTS.mkdir(exist_ok=True)

raw = pd.read_csv(DATA)
raw["dt"] = pd.to_datetime(raw["ts"], format="mixed", dayfirst=True, errors="coerce")
parse_failures = int(raw["dt"].isna().sum())
clean = raw.dropna(subset=["dt"]).sort_values("dt").drop_duplicates("dt", keep="first").copy()
duplicate_count = int(raw.dropna(subset=["dt"])["dt"].duplicated().sum())
sentinel_count = int((clean["sessions"] == -1).sum())
clean = clean[clean["sessions"] >= 0].copy()

hourly = clean.set_index("dt")["sessions"].sort_index()
daily = hourly.resample("D").sum(min_count=1)
daily = daily.loc[: "2025-08-31"]  # September 2025 is partial (extract ends Sep 11)
daily.index = pd.DatetimeIndex(daily.index, name="date")
daily.to_csv(RESULTS / "cleaned_daily_sessions.csv", header=["sessions"])

# Window report uses the missing days as NaN rather than inventing observations.
wr = tslib.window_report(daily, windows=(7, 28, 91), center=True)
wr.to_csv(RESULTS / "window_report.csv", index=False)

bf_date = pd.Timestamp("2024-11-29")
bf = {
    "date": str(bf_date.date()),
    "raw_sessions": float(daily.loc[bf_date]),
    "fortnight_neighbourhood_median_2024-11-22_to_2024-12-06": float(daily.loc["2024-11-22":"2024-12-06"].median()),
    "centred_14_day_mean": float(daily.rolling(14, center=True, min_periods=14).mean().loc[bf_date]),
    "centred_14_day_median": float(daily.rolling(14, center=True, min_periods=14).median().loc[bf_date]),
    "ewma_span_14_adjust_false_causal": float(daily.ewm(span=14, adjust=False, min_periods=1).mean().loc[bf_date]),
}
pd.DataFrame([bf]).to_csv(RESULTS / "black_friday_smoothers.csv", index=False)

# Explicit interpolation only for algorithms requiring a complete daily index.
daily_interp = daily.interpolate(method="time", limit_area="inside")
dec7 = seasonal_decompose(daily_interp, model="additive", period=7)
resid = dec7.resid.dropna()
decomp = {
    "period": 7,
    "missing_days_interpolated_for_decomposition": int(daily.isna().sum()),
    "weekly_seasonal_min": float(dec7.seasonal.min()),
    "weekly_seasonal_max": float(dec7.seasonal.max()),
    "weekly_seasonal_peak_to_trough": float(dec7.seasonal.max() - dec7.seasonal.min()),
    "largest_positive_residual_date": str(resid.idxmax().date()),
    "largest_positive_residual_sessions": float(resid.max()),
    "largest_negative_residual_date": str(resid.idxmin().date()),
    "largest_negative_residual_sessions": float(resid.min()),
    "period_365_status": "not estimable: seasonal_decompose requires 730 observations; available 518",
}
pd.DataFrame([decomp]).to_csv(RESULTS / "decomposition_metrics.csv", index=False)
try:
    seasonal_decompose(daily_interp, model="additive", period=365)
    decomp["period_365_status"] = "ran successfully"
except ValueError as e:
    decomp["period_365_status"] = str(e)
pd.DataFrame([decomp]).to_csv(RESULTS / "decomposition_metrics.csv", index=False)

lag = tslib.lag_at_turn(daily_interp, 31, how="min")
pd.DataFrame([{
    "window_days": lag["window"],
    "centred_minimum_date": lag["centred_turn"].date(),
    "trailing_minimum_date": lag["trailing_turn"].date(),
    "lag_days": lag["lag_periods"],
    "half_window_days": lag["half_window"],
}]).to_csv(RESULTS / "trailing_vs_centred.csv", index=False)

# Defined sensitivity experiment: first 7/14/28/56/91 days from each of
# 12 month starts, April 2024 through March 2025.
starts = pd.date_range("2024-04-01", periods=12, freq="MS")
rows = []
for start in starts:
    for window in (7, 14, 28, 56, 91):
        segment = daily_interp.loc[start : start + pd.Timedelta(days=window - 1)]
        x = np.arange(len(segment), dtype=float)
        slope = float(np.polyfit(x, segment.to_numpy(dtype=float), 1)[0])
        rows.append({
            "start_month": start.strftime("%Y-%m"),
            "window_days": window,
            "n_days": len(segment),
            "slope_sessions_per_day_per_day": slope,
            "direction": "rising" if slope > 0 else ("falling" if slope < 0 else "flat"),
        })
trends = pd.DataFrame(rows)
trends.to_csv(RESULTS / "trend_sensitivity_60_combinations.csv", index=False)
counts = trends["direction"].value_counts().to_dict()
pd.DataFrame([{
    "rising": int(counts.get("rising", 0)),
    "falling": int(counts.get("falling", 0)),
    "flat": int(counts.get("flat", 0)),
    "total": len(trends),
    "start_months": "2024-04 through 2025-03",
    "windows_days": "7,14,28,56,91",
}]).to_csv(RESULTS / "trend_sensitivity_counts.csv", index=False)

audit = {
    "parse_failures": parse_failures,
    "duplicate_timestamps_removed": duplicate_count,
    "sentinel_sessions_minus_one_removed": sentinel_count,
    "clean_hourly_rows": len(clean),
    "analysis_start": str(daily.index.min().date()),
    "analysis_end": str(daily.index.max().date()),
    "daily_calendar_days": len(daily),
    "days_with_no_valid_hourly_observations": int(daily.isna().sum()),
    "partial_month_excluded": "2025-09 (data ends 2025-09-11)",
}
pd.DataFrame([audit]).to_csv(RESULTS / "cleaning_audit.csv", index=False)

print("Part B analysis complete. Results saved in", RESULTS)
print(wr.to_string(index=False))
print(pd.DataFrame([bf]).to_string(index=False))
print(pd.DataFrame([decomp]).to_string(index=False))
print(pd.DataFrame([{
    "centred_minimum": lag["centred_turn"], "trailing_minimum": lag["trailing_turn"],
    "lag_days": lag["lag_periods"], "half_window": lag["half_window"]
}]).to_string(index=False))
print("Trend counts:", counts)
