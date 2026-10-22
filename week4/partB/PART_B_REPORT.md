# Week 4 Part B — Smoothing, windows and panel shape

**Dataset:** `sessions_hourly.csv` (synthetic course data for CDB601220, Superior University Lahore).  
**Measure:** daily total sessions, obtained by summing the hourly `sessions` flow.

## Cleaning and audit

- Parsed `ts` with mixed-format parsing and `dayfirst=True` to handle both ISO and day/month/year strings.
- Removed duplicate timestamps, retaining one copy of each duplicated logger record.
- Removed sentinel `sessions = -1` values.
- Resampled valid hourly session counts to daily sums (`sum`, not `last`).
- The extract ends on 11 September 2025, so September 2025 is a partial month and is excluded from window/decomposition analysis. The analysis range is 1 April 2024–31 August 2025 (518 calendar days).
- There are 13 dates with no valid hourly observations after cleaning. They remain missing for the window report; only methods that require a complete series (decomposition and turning-point comparison) use explicit time interpolation over these 13 dates. No interpolation is treated as observed traffic.

## 1. Window report

`tslib.window_report()` gives:

| Centred window | Raw SD (sessions/day) | Smoothed SD | Raw variation removed | Periods lost at each end |
|---:|---:|---:|---:|---:|
| 7 days | 6,794.1353 | 4,593.4357 | 32.4% | 3 |
| 28 days | 6,794.1353 | 4,367.1416 | 35.7% | 14 |
| 91 days | 6,794.1353 | 4,091.3692 | 39.8% | 45 |

A 7-day window cancels the weekday/weekend cycle. A 28-day window spans four weekly cycles and suppresses more short-term variation, but it also blurs month-scale movement. A 91-day window suppresses quarter-scale changes and loses 45 observations at either edge. **For Part D, use a centred 7-day mean as the main seasonal reference** because the identifiable recurring cycle is weekly; retain the raw daily line so Black Friday and other events remain visible. If the goal were a quarter-scale trend, 91 days would be a different hypothesis, not simply a smoother chart.

## 2. Three smoothers against Black Friday

The raw daily value on 29 November 2024 is **113,710 sessions**, versus a 14-day neighbourhood median of **24,625**.

| Smoother at 29 Nov 2024 | Sessions/day |
|---|---:|
| 14-day centred mean | 32,871 |
| 14-day centred median | 24,698 |
| 14-span EWMA (`span=14`, `adjust=False`, causal) | 37,517.75 |

The centred mean is pulled upward by the one-day spike; the median is robust to it. The causal EWMA is responsive but retains the spike's influence and is not centred (it uses current and prior observations only). For a live monitoring dashboard, use a **causal EWMA alongside the raw series** to surface current changes without future data leakage. For a quarterly report, use the **centred median** when the goal is the typical level rather than the exceptional Black Friday event; show the raw spike separately and annotate it.

## 3. Seasonal decomposition

An additive decomposition with `period=7` was run on the daily series, with the 13 wholly missing days time-interpolated only for this decomposition.

- Weekly seasonal peak-to-trough amplitude: **7,324.20 sessions/day**.
- Largest positive residual: **29 November 2024**, **+75,029.08 sessions/day**.

The largest residual coincides with Black Friday, making it the clearest event to investigate after the weekly pattern and trend have been removed.

The requested `period=365` decomposition **cannot be estimated with this extract** using `seasonal_decompose`: it requires two complete cycles (730 observations), while the cleaned complete-month series has only 518 days. Conceptually, with enough annual coverage, the repeatable annual pattern would move from `resid` into `seasonal`; this dataset is too short to estimate that annual component reliably.

## 4. Trailing or centred

For a 31-day mean, `tslib.lag_at_turn()` finds:

- Centred minimum: **15 May 2024**
- Trailing minimum: **30 May 2024**
- Lag: **15 days**, exactly the half-window (15 days).

A live dashboard refreshing every morning must show a **trailing** window, because a centred mean uses future observations that have not happened yet. Caption it explicitly, for example: **“Trailing 31-day mean of daily sessions; uses today and the prior 30 days; turning points may appear about 15 days late relative to a centred estimate.”** Keep the raw series visible.

## 5. The window is a claim: trend sensitivity

For reproducibility, the 12 start months are April 2024 through March 2025. For each start month, the analysis fits an ordinary least-squares straight line to the first 7, 14, 28, 56, or 91 daily values beginning on that month's first day. The series used is the daily series with explicit interpolation of wholly missing days, and the partial September 2025 tail is excluded.

- Rising fitted slopes: **34 of 60**
- Falling fitted slopes: **26 of 60**

The direction changes with the chosen start and window. These are not 60 independent business trends; they are 60 plausible framings of the same series.

Tufte's Lie Factor is `(effect shown) / (effect in the data)`. It assumes there is a defined, comparable effect in the underlying data and a corresponding effect encoded by the graphic. A cherry-picked window has no uniquely defined reference effect: changing the endpoints changes the data effect itself, so the denominator is not fixed and the ratio is not meaningful. The honest substitute is to disclose the chosen date range and window, show the complete context/raw series, and report a **window-sensitivity analysis** (here, 34 rising vs 26 falling), rather than inventing a Lie Factor.

## Reproducibility notes

Run `python partB_analysis.py` in an environment with pandas, numpy, matplotlib, and statsmodels installed. The script writes the cleaned daily series, window report, Black Friday smoother values, decomposition metrics, turning-point report, and 60-row trend-sensitivity table to `results/`.
