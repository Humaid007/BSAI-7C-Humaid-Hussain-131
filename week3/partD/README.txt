WEEK 3 PART D — CLINICAL REVIEW FIGURE

Files
- taskD_clinical_review.py: reproducible analysis and plotting script
- taskD_clinical_review.ipynb: notebook version with required diagnostics
- vitals_10k.csv: original supplied data
- vizlib.py: course plotting defaults and palette
- clinical_review_figure.png: final 2x2 figure (300 dpi)
- cleaned_vitals.csv: analysis copy after documented cleaning rules
- data_quality_audit.csv: data issue, rule, count, action
- PART_D_REPORT.md: findings and method
- run_log.txt: console output from script execution

Run from this directory in an environment with pandas, numpy, matplotlib, seaborn, and IPython/Jupyter for notebook use:
  python taskD_clinical_review.py

The prompt mentions data/ward_los_wide.csv and starter/starter.py, but those files were not present among the supplied files. This package uses the supplied patient-level vitals_10k.csv directly; it does not fabricate or silently substitute a missing source file. The ward boxplot receives long-form patient records.
