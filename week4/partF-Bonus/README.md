# Week 4 Part F — bonus

**Dataset:** Our World in Data Grapher, *Electricity mix*, configured for monthly generation from solar and wind. The export includes an entity/category field and monthly observations. Source page: https://ourworldindata.org/grapher/electricity-mix?frequency=monthly&metric=generation&source=solar_and_wind

**Important reproducibility note:** `partF_cycle.py` fetches the current CSV when run. The script prints the actual execution/download date and the exact `tslib.audit_index()` result; preserve that output with your submission. The source page was checked on 22 October 2026, but the CSV was not downloaded into this package in this environment, so no numeric findings or rendered figure are claimed here. Run the script with `pandas`, `numpy`, `matplotlib`, `statsmodels`, and the course `tslib.py`/`vizlib.py` files in the same folder. The script writes `partF_cycle.png` at 300 dpi and `partF_decomposition.csv`.

The script selects the World category when present, otherwise the first sorted entity. It keeps monthly frequency explicit and refuses to interpolate missing months silently. It reports the banked figure size and compares additive and multiplicative decomposition residuals. Use the actual printed residual results to finalize the two-sentence interpretation; do not submit a guessed conclusion.

**Source citation:** Ember and other sources, processed by Our World in Data, “Total electricity generation” / Electricity mix data product. Source configuration and data endpoint are defined in `partF_cycle.py`. Access date to record at execution: printed by the script.
