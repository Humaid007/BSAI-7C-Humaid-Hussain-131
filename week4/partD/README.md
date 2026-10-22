# Week 4 Part D — E-commerce review figure

## Contents
- `partD_review_figure.py`: reproducible end-to-end cleaning, audit, and plotting script.
- `partD_ecommerce_review.png`: final 2×2 figure at 300 dpi.
- `partD_cleaning_audit.md`: six data problems, cleaning rules, panel questions, and validation.
- `cleaned_daily_sessions.csv`: daily sessions after timestamp parsing, duplicate removal, sentinel handling, and exclusion of the partial final month.
- `subcategory_shares_check.csv`: deduplicated net-revenue shares compared with `shares_eight.csv`.
- `sessions_hourly.csv`, `revenue_catalogue.csv`, `shares_eight.csv`: input files.

## Run
Requires Python 3.10+ and pandas, numpy, matplotlib.

```bash
python -m pip install pandas numpy matplotlib
python partD_review_figure.py
```

The script uses explicit parsing for `%Y-%m-%d %H:%M:%S` and `%d/%m/%Y %H:%M`, audits hourly gaps before resampling, and saves the PNG before closing the figure.

## Important choices
- Duplicate timestamps are duplicate exports with identical metrics/device; keep one instead of double-counting.
- `sessions == -1` is an invalid sentinel and is set to missing.
- The final partial month (September 2025) is excluded from the trend, not extrapolated.
- Daily sessions use `.resample("D").sum(min_count=1)` so a day with no valid observations remains missing, not zero.
- Seven-day centred mean cancels the weekday/weekend cycle; the raw daily series remains visible.
- Duplicate SKU rows are deduplicated by SKU. Negative net revenue values are retained because they represent returns exceeding revenue.
