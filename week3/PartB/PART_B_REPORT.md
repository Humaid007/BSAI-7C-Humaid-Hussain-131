# Week 3 — Part B: Lie Factor (15 marks)

## Method

For each chart, the **data effect** is the relative change in the underlying value:

`(value_end - value_start) / value_start`

The **graphic effect** is the relative change in the visual encoding. Where a graphic's area is encoded, the linear scale ratio is squared (`ink_dimension = 2`):

`(ink_end / ink_start) ** ink_dimension - 1`

The lie factor is `graphic_effect / data_effect`. A value near 1 is proportionate; above 1 exaggerates; below 1 understates. Calculations use the supplied `vizlib.py` implementation and `case07_lie_factor.csv` data.

## Results

| ID | Chart | Data change | Graphic change | Lie factor | Verdict |
|---|---|---:|---:|---:|---|
| A | Corporate tax rate | 6.67% | 500.00% | 75.00 | exaggerates 75.00x |
| B | Federal health budget (Rs bn) | 50.00% | 125.00% | 2.50 | exaggerates 2.50x |
| C | Export earnings ($ bn) | 20.00% | 20.00% | 1.00 | honest |
| D | Air-pollution index | 50.00% | 12.50% | 0.25 | understates (0.25) |
| E | City population (millions) | 300.00% | 1500.00% | 5.00 | exaggerates 5.00x |

## Interpretation

- **A — Corporate tax rate:** 30 to 32 is a 6.67% data increase, but the visible ink grows from 4 to 24 mm (500% graphic increase). The bars begin at a 29.6% baseline, so the truncated baseline dramatically magnifies the apparent change. **Lie factor: 75.00 — exaggerates.**
- **B — Federal health budget:** Rs 40bn to Rs 60bn is a 50% data increase. The coin icon grows 1.5× in both height and width, so its area grows to 2.25× (125% graphic increase). **Lie factor: 2.50 — exaggerates.** The dimension must be 2 because the visual uses area, not just a single linear dimension.
- **C — Export earnings:** $25bn to $30bn is a 20% increase; bar height grows from 5 to 6 cm, also 20%. **Lie factor: 1.00 — honest.**
- **D — Air-pollution index:** 100 to 150 is a 50% increase, while bar height grows from 8 to 9 cm (12.5%). **Lie factor: 0.25 — understates.** This could make worsening pollution look less severe; the data alone does not establish the designer's intent.
- **E — City population:** 2m to 8m is a 300% increase. The bubble radius grows 1× to 4×, so area grows 1× to 16× (a 1500% increase). **Lie factor: 5.00 — exaggerates.** The dimension must be 2 because the displayed quantity is bubble area.

## Dual-axis chart note (related case)

A dual-axis revenue/cost chart does not have one unambiguous lie factor when each series has an independent vertical scale: the apparent visual change depends on the axis ranges. In the supplied series, revenue rises from 52 to 78 PKR million (**50.00%**) and cost rises from 44 to 53 PKR million (**20.45%**); revenue remains above cost in every listed month and the gap increases from 8 to 25 PKR million. Do not infer a crossover or that costs exceed revenue from visual line crossings on independent axes.

## Conclusion

Chart **C** is the only proportionate chart in this set. A, B and E exaggerate changes, while D understates its change. For area-based symbols, calculate the graphic effect from area (square the linear ratio), and always check whether an axis baseline or independent scale distorts interpretation.
