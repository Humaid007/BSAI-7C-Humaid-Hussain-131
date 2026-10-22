# Part D cleaning and design audit

## Initial required diagnostics
- `df.info()`: 12,670 rows; 5 columns; `ts` and `device` are objects, the three metrics are integers.
- `df.describe().T`: `sessions` minimum is -1, indicating an invalid sentinel.
- `df.device.value_counts()`: mixed casing/whitespace splits device categories (`Mobile`, `mobile`, `MOBILE `; `Desktop`, `desktop`).
- `df.ts.head(10).tolist()`: mixed ISO and day-first slash formats; input is not chronologically sorted.

## Six issues and explicit rules
1. **Mixed timestamp formats:** parse ISO `%Y-%m-%d %H:%M:%S` and day-first `%d/%m/%Y %H:%M` separately; 0 failures.
2. **Unsorted rows:** sort by the parsed timestamp before analysis.
3. **Invalid sentinel:** set `sessions == -1` to missing; 287 rows after timestamp deduplication.
4. **Inconsistent device labels:** trim and normalize capitalization.
5. **Duplicate timestamps:** 286 duplicate rows beyond first (286 rows in duplicate groups, 286 timestamp groups); duplicate rows have identical metrics/device, so keep one rather than summing twice.
6. **Missing hourly periods:** expected hourly slots across the observed span = 12,696; unique timestamps = 12,384; missing hours = 312. This count is done before daily resampling.

## Date-parse trap
- Explicitly parsed range: 2024-04-01 00:00:00 to 2025-09-11 23:00:00.
- `format="mixed"` is intentionally not used; mixed inference can reinterpret day-first strings and move the series to incorrect dates despite parsing all rows.

## Daily series
- Daily index: 2024-04-01 to 2025-09-11.
- Missing daily totals (`NaN`, no valid hourly sessions): 13.
- Final partial month excluded from trend: September 2025 (11 calendar days observed in the partial month).
- Rolling mean: centred 7-day mean on the daily series, chosen to cancel the weekly day-of-week cycle; raw daily totals remain visible.
- Daily aggregation: sum of valid hourly sessions; missing days are kept as `NaN` via `sum(min_count=1)` rather than converted to zero.

## Catalogue rules
- Rows in source catalogue: 345; duplicate SKU count: 1. Keep first occurrence per SKU because the repeated SKU row duplicates the same item/revenue.
- Negative net revenue rows: 7; retained because net revenue is revenue less returns, and a negative net value represents returns exceeding sales. Do not silently drop or clip these rows.
- Subcategory shares use the sum of `net_revenue_pkr_m` after SKU deduplication as the denominator.
- Maximum absolute share difference vs `shares_eight.csv`: 0.243 percentage points.\n
## What each panel answers
1. **Daily traffic:** Is the underlying traffic level changing once the weekly cycle is damped? Raw daily totals remain visible for spikes.
2. **Weekday-hour heatmap:** At what times are mean sessions higher or lower by weekday and hour?
3. **Treemap:** Where is the net-revenue mass located across parent categories and their subcategories?
4. **Sorted bars:** By how much does each subcategory contribute, and what is the exact rank/value difference?

## Figure finishing
- Four panels in one 2×2 figure; finding-led titles; units and aggregation in axis labels.
- Spines removed; sequential `YlGnBu` heatmap; Okabe–Ito-inspired parent-category hues for treemap.
- Figure saved with `fig.savefig(..., dpi=300, bbox_inches="tight")` before closing; source note included.
