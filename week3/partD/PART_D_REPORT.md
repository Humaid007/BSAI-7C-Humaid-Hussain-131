# Part D — Clinical Review Figure

## Data problems found before plotting

The required diagnostics show 10,000 rows and 16 columns with no nulls initially, but several fields are not analysis-ready.

1. **Mixed admission-date formats:** ISO dates, abbreviated month names, and slash-separated dates coexist in `admit_date`, which is stored as text. Rule: parse mixed formats to datetime; interpret slash dates day-first and coerce any unparseable entries to missing.
2. **Inconsistent ward labels:** case, spacing, punctuation, and aliases split the same ward across 12 labels. Rule: trim and canonicalize known aliases to General Medicine, Cardiology, Day Surgery, and Intensive Care.
3. **Implausible heart rates:** range is 0–415 bpm. Rule: treat values outside 30–220 bpm as missing in the analysis copy; do not guess replacements.
4. **Implausible BMI entries:** range is 0.0–999.0 kg/m², including obvious sentinel-like values. Rule: treat values outside 10–80 kg/m² as missing in the analysis copy.
5. **Extreme length-of-stay values:** maximum is 273.65 days. Rule: flag values above 60 days as requiring source verification and exclude them from the plotted distribution/boxplot by setting them missing in the analysis copy. This threshold is an explicit review rule, not proof that every long stay is erroneous.
6. **Derived measurement:** `map_mmhg` is a derived blood-pressure indicator. Rule: retain it in the cleaned data but omit it from the correlation heatmap to avoid presenting a derived duplicate as independent evidence.

The original CSV is preserved unchanged. The cleaning actions and affected row counts are in `data_quality_audit.csv`.

## Figure panels

1. **Distribution:** histogram of length of stay, with 0.5-day bin width stated on the x-axis. It reveals a right-skewed distribution among records that pass the explicit LOS review rule.
2. **Ward comparison:** boxplots of length of stay across the four canonical wards. Fliers are hidden for legibility; flagged LOS values are not plotted.
3. **Relationship:** scatterplot of systolic versus diastolic blood pressure, selected because the correlation heatmap identifies this as the strongest useful non-derived vital-sign pair. Pearson r in the panel title is computed from available paired records.
4. **Correlation:** annotated Pearson correlation heatmap of cleaned age, blood pressure, heart rate, SpO₂, BMI, cholesterol, glucose, and LOS. MAP is excluded because it is derived from systolic/diastolic pressure.

## Implementation and reproducibility

- Uses `vizlib.PALETTE` and `style_defaults()` for consistent styling; colour is not the only carrier of information.
- Axis labels include measurement units; top/right spines are removed.
- The script holds the figure as `fig` and calls `fig.savefig(..., dpi=300, bbox_inches='tight')` before closing it.
- Run with `python taskD_clinical_review.py` from this folder.
- The assignment mentions `data/ward_los_wide.csv` and `starter/starter.py`, but neither was present in the supplied files available for this package. The supplied `vitals_10k.csv` is used directly, and the ward boxplot uses patient-level long-form data rather than fabricating a missing wide source.

## Key counts after standardization

- General Medicine: 4,018 records
- Cardiology: 2,682 records
- Intensive Care: 1,821 records
- Day Surgery: 1,479 records
