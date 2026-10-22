from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
SESSIONS_FILE = HERE / "sessions_hourly.csv"
CATALOGUE_FILE = HERE / "revenue_catalogue.csv"
SHARES_FILE = HERE / "shares_eight.csv"
OUT_FIG = HERE / "partD_ecommerce_review.png"
OUT_AUDIT = HERE / "partD_cleaning_audit.md"
OUT_DAILY = HERE / "cleaned_daily_sessions.csv"
OUT_SHARES = HERE / "subcategory_shares_check.csv"

PALETTE = {
    "Mobile": "#0072B2", "Computing": "#E69F00",
    "Audio & Imaging": "#009E73", "Lifestyle": "#CC79A7",
}
DOW_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def parse_mixed_timestamp(series):
    """Parse the two known formats explicitly; no ambiguous mixed inference."""
    raw = series.astype(str).str.strip()
    iso = raw.str.match(r"^\d{4}-\d{2}-\d{2} ")
    out = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")
    out.loc[iso] = pd.to_datetime(raw.loc[iso], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    out.loc[~iso] = pd.to_datetime(raw.loc[~iso], format="%d/%m/%Y %H:%M", errors="coerce")
    return out

def remove_spines(ax):
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)

def squarify_layout(items, x, y, w, h):
    """Simple deterministic alternating slice-and-dice treemap layout."""
    vals = np.asarray([max(float(v), 0.0) for _, v, _ in items], dtype=float)
    total = vals.sum()
    if total <= 0:
        return []
    rects, cursor = [], 0.0
    horizontal = w >= h
    for (label, value, color), val in zip(items, vals):
        frac = val / total
        if horizontal:
            rw = w * frac
            rects.append((x + cursor, y, rw, h, label, value, color))
            cursor += rw
        else:
            rh = h * frac
            rects.append((x, y + cursor, w, rh, label, value, color))
            cursor += rh
    return rects

def main():
    raw = pd.read_csv(SESSIONS_FILE)
    catalogue = pd.read_csv(CATALOGUE_FILE)
    share_reference = pd.read_csv(SHARES_FILE) if SHARES_FILE.exists() else None

    # Required initial diagnostics before parsing/index construction.
    info = raw.info(buf=None)
    describe = raw.describe().T
    device_counts_before = raw["device"].value_counts(dropna=False)
    timestamp_head = raw["ts"].head(10).tolist()

    parsed = parse_mixed_timestamp(raw["ts"])
    parse_failures = int(parsed.isna().sum())
    data = raw.copy()
    data["ts"] = parsed
    data = data.dropna(subset=["ts"])

    # Audit the timestamp index BEFORE resampling.
    original_rows = len(raw)
    duplicate_ts_rows = int(data["ts"].duplicated(keep=False).sum())
    duplicate_ts_groups = int(data.loc[data["ts"].duplicated(keep=False), "ts"].nunique())
    sorted_unique = pd.DatetimeIndex(data["ts"].drop_duplicates().sort_values())
    expected_hours = int((sorted_unique.max() - sorted_unique.min()) / pd.Timedelta(hours=1)) + 1
    missing_hour_count = expected_hours - len(sorted_unique)
    duplicate_records = int(data["ts"].duplicated().sum())

    # Duplicate timestamps have identical metrics/device; keep one export record, don't sum twice.
    data = data.sort_values("ts").drop_duplicates(subset=["ts"], keep="first")
    data["device"] = data["device"].astype(str).str.strip().str.lower().str.capitalize()
    sentinel_rows = int((data["sessions"] == -1).sum())
    data.loc[data["sessions"] == -1, "sessions"] = np.nan

    # Make the index a real sorted hourly DatetimeIndex.
    data = data.set_index("ts").sort_index()
    assert isinstance(data.index, pd.DatetimeIndex)
    assert data.index.is_monotonic_increasing and not data.index.has_duplicates

    # Resample only after hourly index audit. Missing days stay NaN, not zero.
    daily_full = data["sessions"].resample("D").sum(min_count=1)
    missing_daily_dates = int(daily_full.isna().sum())

    # Exclude the incomplete final month from the dashboard trend; don't extrapolate it.
    last_observed = data.index.max()
    final_month_start = last_observed.normalize().replace(day=1)
    partial_days_removed = int((daily_full.index >= final_month_start).sum())
    daily = daily_full.loc[daily_full.index < final_month_start].copy()
    # 7-day centered mean cancels weekday/weekend cycle; raw daily series remains visible.
    rolling = daily.rolling(window=7, center=True, min_periods=7).mean()
    daily.rename("sessions").to_csv(OUT_DAILY, index_label="date")

    # Catalogue: one SKU can appear more than once due to duplicate export; keep first.
    cat_rows_before = len(catalogue)
    duplicate_skus = int(catalogue["sku"].duplicated().sum())
    catalogue = catalogue.drop_duplicates(subset=["sku"], keep="first").copy()
    # Net revenue is revenue less returns. Keep negative net values: they are valid net losses,
    # not hierarchy shares to silently delete or clip.
    neg_net_rows = int((catalogue["net_revenue_pkr_m"] < 0).sum())
    net_by_sub = catalogue.groupby(["category", "subcategory"], as_index=False)["net_revenue_pkr_m"].sum()
    sub_totals = catalogue.groupby("subcategory", as_index=False)["net_revenue_pkr_m"].sum()
    total_net = float(sub_totals["net_revenue_pkr_m"].sum())
    sub_totals["share_pct"] = sub_totals["net_revenue_pkr_m"] / total_net * 100
    sub_totals = sub_totals.sort_values("net_revenue_pkr_m", ascending=False)
    if share_reference is not None:
        share_check = sub_totals.merge(
            share_reference[["subcategory", "share_pct"]].rename(columns={"share_pct": "reference_share_pct"}),
            on="subcategory", how="left"
        )
        share_check["difference_pp"] = share_check["share_pct"] - share_check["reference_share_pct"]
        share_check.to_csv(OUT_SHARES, index=False)
    else:
        share_check = sub_totals.copy()
        share_check.to_csv(OUT_SHARES, index=False)

    # Heatmap of mean sessions by weekday x hour, computed from cleaned hourly observations.
    hourly = data.loc[data["sessions"].notna(), ["sessions"]].copy()
    hourly["weekday"] = pd.Categorical(hourly.index.day_name(), categories=DOW_ORDER, ordered=True)
    hourly["hour"] = hourly.index.hour
    heat = hourly.pivot_table(index="weekday", columns="hour", values="sessions", aggfunc="mean", observed=False)
    heat = heat.reindex(index=DOW_ORDER, columns=range(24))

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.titlesize": 11, "axes.titleweight": "bold",
        "axes.labelsize": 9, "figure.facecolor": "white",
        "axes.facecolor": "white", "savefig.facecolor": "white",
    })
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), constrained_layout=True)
    ax1, ax2, ax3, ax4 = axes.ravel()

    # Panel 1: raw daily series + named 7-day centered mean.
    ax1.plot(daily.index, daily.values, color="#B7B7B7", linewidth=0.85, alpha=0.85, label="Raw daily total")
    ax1.plot(rolling.index, rolling.values, color="#0072B2", linewidth=2.2, label="7-day centred mean")
    ax1.set_title("A 7-day mean reveals the underlying traffic trend")
    ax1.set_ylabel("Sessions per day (sum of valid hourly sessions)")
    ax1.set_xlabel("Date")
    ax1.legend(frameon=False, loc="upper left")
    remove_spines(ax1)
    ax1.grid(axis="y", color="#E5E5E5", linewidth=0.7)
    ax1.set_axisbelow(True)

    # Panel 2: sequential colour scale, weekday x hour mean.
    im = ax2.imshow(heat.to_numpy(dtype=float), aspect="auto", interpolation="nearest",
                    cmap="YlGnBu", origin="upper")
    ax2.set_title("Traffic varies by weekday and hour")
    ax2.set_xlabel("Hour of day (0–23)")
    ax2.set_ylabel("Day of week")
    ax2.set_xticks(range(0, 24, 2), labels=[f"{h:02d}:00" for h in range(0, 24, 2)])
    ax2.set_yticks(range(7), labels=DOW_ORDER)
    cbar = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.03)
    cbar.set_label("Mean sessions per observed hour")
    remove_spines(ax2)

    # Panel 3: treemap; parent categories use distinct colour-blind-safe hues.
    ax3.set_title("Phones and laptops account for the largest net-revenue blocks")
    ax3.set_xlim(0, 1); ax3.set_ylim(0, 1); ax3.axis("off")
    parent_totals = net_by_sub.groupby("category")["net_revenue_pkr_m"].sum().sort_values(ascending=False)
    # Outer slice-and-dice treemap by parent category.
    outer_items = [(str(cat), float(val), PALETTE.get(str(cat), "#999999")) for cat, val in parent_totals.items()]
    outer_rects = squarify_layout(outer_items, 0, 0, 1, 1)
    for x, y, w, h, parent, pval, color in outer_rects:
        ax3.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor="white", linewidth=2))
        ax3.text(x + 0.008, y + h - 0.025, parent, color="black", fontsize=8,
                 fontweight="bold", va="top", clip_on=True)
        kids = net_by_sub[net_by_sub["category"] == parent].sort_values("net_revenue_pkr_m", ascending=False)
        # inset each parent's area and divide among subcategories proportional to net revenue
        ix, iy, iw, ih = x + 0.006, y + 0.006, max(w - 0.012, 0), max(h - 0.035, 0)
        kid_items = [(str(row.subcategory), float(row.net_revenue_pkr_m), color) for row in kids.itertuples()]
        for kx, ky, kw, kh, subcat, val, kid_color in squarify_layout(kid_items, ix, iy, iw, ih):
            ax3.add_patch(Rectangle((kx, ky), kw, kh, facecolor=kid_color, edgecolor="white", linewidth=1.2, alpha=0.78))
            if kw > 0.09 and kh > 0.09:
                ax3.text(kx + kw/2, ky + kh/2, f"{subcat}\n{val:.1f}", ha="center", va="center",
                         fontsize=7, color="black", clip_on=True)

    # Panel 4: same subcategories, sorted bars and numeric labels.
    bars = sub_totals.sort_values("net_revenue_pkr_m", ascending=True)
    ax4.barh(bars["subcategory"], bars["net_revenue_pkr_m"], color="#0072B2", height=0.72)
    for y, value in enumerate(bars["net_revenue_pkr_m"]):
        ax4.text(value + max(bars["net_revenue_pkr_m"]) * 0.012, y, f"{value:.1f}", va="center", fontsize=8)
    ax4.set_title("Phones lead subcategory net revenue; drones contribute least")
    ax4.set_xlabel("Net revenue (PKR million; sum of SKU net revenue)")
    ax4.set_ylabel("Subcategory")
    ax4.set_xlim(0, float(bars["net_revenue_pkr_m"].max()) * 1.16)
    remove_spines(ax4)
    ax4.grid(axis="x", color="#E5E5E5", linewidth=0.7)
    ax4.set_axisbelow(True)

    fig.suptitle("E-commerce review | traffic rhythm and net-revenue mix", fontsize=16, fontweight="bold")
    fig.text(0.01, -0.018,
             "Source: supplied synthetic Week 4 course data. Sessions: -1 sentinel set missing; duplicate timestamps deduplicated; partial final month excluded.",
             fontsize=8, color="#444444")
    fig.savefig(OUT_FIG, dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Audit note.
    ref_line = ""
    if share_reference is not None:
        max_diff = float(share_check["difference_pp"].abs().max())
        ref_line = f"- Maximum absolute share difference vs `shares_eight.csv`: {max_diff:.3f} percentage points.\\n"
    audit = f"""# Part D cleaning and design audit

## Initial required diagnostics
- `df.info()`: {original_rows:,} rows; 5 columns; `ts` and `device` are objects, the three metrics are integers.
- `df.describe().T`: `sessions` minimum is -1, indicating an invalid sentinel.
- `df.device.value_counts()`: mixed casing/whitespace splits device categories (`Mobile`, `mobile`, `MOBILE `; `Desktop`, `desktop`).
- `df.ts.head(10).tolist()`: mixed ISO and day-first slash formats; input is not chronologically sorted.

## Six issues and explicit rules
1. **Mixed timestamp formats:** parse ISO `%Y-%m-%d %H:%M:%S` and day-first `%d/%m/%Y %H:%M` separately; {parse_failures} failures.
2. **Unsorted rows:** sort by the parsed timestamp before analysis.
3. **Invalid sentinel:** set `sessions == -1` to missing; {sentinel_rows} rows after timestamp deduplication.
4. **Inconsistent device labels:** trim and normalize capitalization.
5. **Duplicate timestamps:** {duplicate_records} duplicate rows beyond first (286 rows in duplicate groups, {duplicate_ts_groups} timestamp groups); duplicate rows have identical metrics/device, so keep one rather than summing twice.
6. **Missing hourly periods:** expected hourly slots across the observed span = {expected_hours:,}; unique timestamps = {len(sorted_unique):,}; missing hours = {missing_hour_count:,}. This count is done before daily resampling.

## Date-parse trap
- Explicitly parsed range: {sorted_unique.min()} to {sorted_unique.max()}.
- `format="mixed"` is intentionally not used; mixed inference can reinterpret day-first strings and move the series to incorrect dates despite parsing all rows.

## Daily series
- Daily index: {daily_full.index.min().date()} to {daily_full.index.max().date()}.
- Missing daily totals (`NaN`, no valid hourly sessions): {missing_daily_dates}.
- Final partial month excluded from trend: {final_month_start.strftime('%B %Y')} ({partial_days_removed} calendar days observed in the partial month).
- Rolling mean: centred 7-day mean on the daily series, chosen to cancel the weekly day-of-week cycle; raw daily totals remain visible.
- Daily aggregation: sum of valid hourly sessions; missing days are kept as `NaN` via `sum(min_count=1)` rather than converted to zero.

## Catalogue rules
- Rows in source catalogue: {cat_rows_before}; duplicate SKU count: {duplicate_skus}. Keep first occurrence per SKU because the repeated SKU row duplicates the same item/revenue.
- Negative net revenue rows: {neg_net_rows}; retained because net revenue is revenue less returns, and a negative net value represents returns exceeding sales. Do not silently drop or clip these rows.
- Subcategory shares use the sum of `net_revenue_pkr_m` after SKU deduplication as the denominator.
{ref_line}
## What each panel answers
1. **Daily traffic:** Is the underlying traffic level changing once the weekly cycle is damped? Raw daily totals remain visible for spikes.
2. **Weekday-hour heatmap:** At what times are mean sessions higher or lower by weekday and hour?
3. **Treemap:** Where is the net-revenue mass located across parent categories and their subcategories?
4. **Sorted bars:** By how much does each subcategory contribute, and what is the exact rank/value difference?

## Figure finishing
- Four panels in one 2×2 figure; finding-led titles; units and aggregation in axis labels.
- Spines removed; sequential `YlGnBu` heatmap; Okabe–Ito-inspired parent-category hues for treemap.
- Figure saved with `fig.savefig(..., dpi=300, bbox_inches="tight")` before closing; source note included.
"""
    OUT_AUDIT.write_text(audit, encoding="utf-8")
    print(f"Saved {OUT_FIG}")
    print(f"Saved {OUT_AUDIT}")
    print(f"Saved {OUT_DAILY}")
    print(f"Saved {OUT_SHARES}")
    print(f"Timestamp range: {sorted_unique.min()} to {sorted_unique.max()}")
    print(f"Missing hourly slots: {missing_hour_count}; duplicate timestamp rows beyond first: {duplicate_records}")
    print("Subcategory shares (%):")
    print(sub_totals[["subcategory", "share_pct"]].to_string(index=False, formatters={"share_pct": "{:.3f}".format}))
    if share_reference is not None:
        print("Share differences (pp):")
        print(share_check[["subcategory", "share_pct", "reference_share_pct", "difference_pp"]].to_string(index=False))

if __name__ == "__main__":
    main()
