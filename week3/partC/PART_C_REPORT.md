# Week 3 — Part C: Prove the palette, do not claim it

## Method

The chosen comparison palette is the first four colours of Matplotlib `tab10` (`#1F77B4`, `#FF7F0E`, `#2CA02C`, `#D62728`). It was selected as a familiar default, not presumed safe. `vizlib.simulate_cvd()` was applied to each palette for deutan, protan and tritan simulations. Swatch images show original colours and each simulated result. `vizlib.worst_pair()` checks every pair; ΔE is the course library's OKLab distance multiplied by 100.

## Worst-pair results

| Palette | Vision condition | Slots | Original colours | Simulated ΔE | Interpretation |
|---|---|---:|---|---:|---|
| tab10_first_four | deutan | 3–4 | #2CA02C / #D62728 | 4.06 | FAILS — same colour |
| tab10_first_four | protan | 2–3 | #FF7F0E / #2CA02C | 0.68 | FAILS — same colour |
| tab10_first_four | tritan | 1–3 | #1F77B4 / #2CA02C | 6.72 | needs a second channel |
| tab10_first_four | normal vision | 2–4 | #FF7F0E / #D62728 | 18.60 | clear |
| course_palette_three | deutan | 2–3 | #D55E00 / #009E73 | 11.01 | ok |
| course_palette_three | protan | 2–3 | #D55E00 / #009E73 | 12.95 | ok |
| course_palette_three | tritan | 1–3 | #0072B2 / #009E73 | 8.37 | ok |
| course_palette_three | normal vision | 1–3 | #0072B2 / #009E73 | 18.71 | clear |
| course_palette_four | deutan | 3–4 | #009E73 / #CC79A7 | 7.55 | needs a second channel |
| course_palette_four | protan | 1–4 | #0072B2 / #CC79A7 | 9.49 | ok |
| course_palette_four | tritan | 1–3 | #0072B2 / #009E73 | 8.37 | ok |
| course_palette_four | normal vision | 2–4 | #D55E00 / #CC79A7 | 16.42 | clear |

## Interpretation and rule for the rest of the course

The course palette's fourth colour (`#CC79A7`) is explicitly a weaker slot: the supplied `vizlib.py` documentation says it reduces the CVD separation margin to ΔE 7.6 and falls below 3:1 contrast against the white surface. It must not be used as a colour-only category. If the fourth category is genuinely needed, pair it with a redundant cue such as a distinct marker shape, direct label, texture/pattern, or table view. For charts with more than three categories, I will keep the first three categories colour-coded and distinguish any additional categories using non-colour channels (especially direct labels and different marker shapes/line styles); I will not simply add more hues and rely on a legend.

**ΔE guide from `vizlib.py`:** ≥15 clear for normal vision; ≥8 target after CVD simulation; 6–8 requires a second encoding channel; <6 means the pair effectively collapses and the palette must be fixed.
