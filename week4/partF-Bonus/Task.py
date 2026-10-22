from pathlib import Path
from datetime import date
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

from tslib import audit_index, banked_figsize, cycle_plot

OUT = Path(__file__).resolve().parent
URL = ("https://ourworldindata.org/grapher/electricity-mix.csv"
       "?v=1&csvType=full&useColumnShortNames=false"
       "&frequency=monthly&metric=generation&source=solar_and_wind")
SOURCE_PAGE = "https://ourworldindata.org/grapher/electricity-mix?frequency=monthly&metric=generation&source=solar_and_wind"

def main():
    df = pd.read_csv(URL, storage_options={"User-Agent": "CDB601220 course analysis"})
    # OWID Grapher exports Entity, Code, Year, and the configured indicator.
    value_col = next(c for c in df.columns if c not in {"Entity", "Code", "Year"})
    df = df.rename(columns={"Entity": "category", "Year": "date", value_col: "generation"})
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["generation"] = pd.to_numeric(df["generation"], errors="coerce")
    df = df.dropna(subset=["date", "generation"])
    # Use a clearly defined single category so the time series is comparable.
    # The source's Entity field is the category column; choose World if present.
    available = df["category"].astype(str).unique()
    category = "World" if "World" in available else sorted(available)[0]
    s = (df.loc[df["category"].eq(category), ["date", "generation"]]
           .drop_duplicates("date").sort_values("date").set_index("date")["generation"])
    # Monthly frequency: align to month starts, expose missing periods rather than silently fill.
    s.index = s.index.to_period("M").to_timestamp()
    s = s[~s.index.duplicated(keep="first")].asfreq("MS")
    if s.notna().sum() < 18:
        raise ValueError(f"Only {s.notna().sum()} valid monthly observations; need at least 18.")
    if s.isna().any():
        print(f"Missing monthly values: {int(s.isna().sum())}; decomposition uses only the longest complete segment.")
        # Do not silently interpolate: choose the longest contiguous non-missing segment.
        groups = (s.isna()).cumsum()
        candidates = [g.dropna() for _, g in s.groupby(groups) if g.notna().any()]
        s = max(candidates, key=len)
    audit = audit_index(s, "MS")
    print("SOURCE:", SOURCE_PAGE)
    print("DOWNLOAD DATE:", date.today().isoformat(), "(actual script execution date)")
    print("CATEGORY:", category, "| UNIT: TWh/month")
    print("OBSERVATIONS:", len(s), "| RANGE:", s.index.min().date(), "to", s.index.max().date())
    print("tslib.audit_index:", audit)
    if len(s) < 24:
        raise ValueError("Need at least 24 consecutive monthly values for 2 annual cycles.")
    # Banked aspect ratio: use the toolkit's calculation and report it.
    figsize = banked_figsize(s.to_numpy())
    print("BANKED FIGSIZE (inches):", tuple(round(float(x), 3) for x in figsize))
    additive = seasonal_decompose(s, model="additive", period=12, extrapolate_trend="freq")
    multiplicative = seasonal_decompose(s, model="multiplicative", period=12, extrapolate_trend="freq")
    cycle = s.groupby(s.index.month).mean()
    fig = plt.figure(figsize=(13, 10), constrained_layout=True)
    gs = fig.add_gridspec(2, 2)
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(s.index, s.values, lw=1.6, label="Monthly generation")
    ax1.set_title(f"{category}: monthly solar + wind generation")
    ax1.set_ylabel("TWh per month")
    ax1.set_xlabel("Month")
    ax1.legend(frameon=False)
    ax1.text(.99, .02, f"Banked figsize = {figsize[0]:.2f} × {figsize[1]:.2f} in",
             transform=ax1.transAxes, ha="right", va="bottom", fontsize=9)
    ax2 = fig.add_subplot(gs[1, 0])
    # Cycle plot: each calendar year is a line, x is month of year.
    for year, part in s.groupby(s.index.year):
        ax2.plot(part.index.month, part.values, marker="o", ms=2.5, alpha=.65, label=str(year))
    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels(["J","F","M","A","M","J","J","A","S","O","N","D"])
    ax2.set_title("Cycle plot: align each year by month")
    ax2.set_ylabel("TWh per month")
    ax2.set_xlabel("Calendar month")
    ax2.legend(ncol=3, fontsize=7, frameon=False)
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(s.index, additive.resid, label="Additive residual", lw=1.2)
    ax3.plot(s.index, multiplicative.resid, label="Multiplicative residual", lw=1.2)
    ax3.axhline(0, lw=.8, color="black")
    ax3.set_title("Decomposition residuals")
    ax3.set_ylabel("Additive: TWh; multiplicative: ratio-scale")
    ax3.set_xlabel("Month")
    ax3.legend(frameon=False, fontsize=8)
    fig.suptitle("Week 4 Part F — seasonality versus growth", fontsize=15)
    fig.savefig(OUT / "partF_cycle.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    result = pd.DataFrame({
        "date": s.index,
        "observed": s.values,
        "additive_residual": additive.resid.values,
        "multiplicative_residual": multiplicative.resid.values,
    })
    result.to_csv(OUT / "partF_decomposition.csv", index=False)
    # Quantitative comparison: residual scale relative to fitted trend.
    trend_level = float(s.mean())
    add_cv = float(additive.resid.std() / trend_level)
    mult_cv = float(multiplicative.resid.std())
    print(f"RESIDUAL COMPARISON: additive residual SD / mean level = {add_cv:.4f}; "
          f"multiplicative residual SD = {mult_cv:.4f}")
    if add_cv > mult_cv:
        print("TWO-SENTENCE ANSWER: The seasonal swing is more consistent with proportional growth if the multiplicative residuals are comparatively smaller and steadier than additive residuals. Here, the reported residual scales are the evidence; inspect the plotted residuals before concluding.")
    else:
        print("TWO-SENTENCE ANSWER: The seasonal swing is not clearly explained by proportional growth alone if additive residuals are comparatively smaller and steadier. Here, the reported residual scales are the evidence; inspect the plotted residuals before concluding.")

if __name__ == "__main__":
    main()
