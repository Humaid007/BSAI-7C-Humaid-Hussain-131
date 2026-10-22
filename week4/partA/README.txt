Week 4 — Part A: Rebuild nine charts and diagnose them

Contents
- partA_charts.py: reproducible script that rebuilds the nine published recipes and nine redesigns.
- partA_diagnosis.pdf: 27-page report: original figure, redesign, and diagnosis for each of nine cases.
- PART_A_DIAGNOSIS.md: editable diagnoses with mechanism evidence and source references.
- figures/: 18 PNGs (original recipe + redesign per case), each exported at 300 dpi.
- case01...case09 CSVs: supplied synthetic course datasets.
- tslib.py, vizlib.py, DATA_DICTIONARY.md: supplied course toolkit and data dictionary.

Run
  python -m pip install pandas numpy matplotlib
  python partA_charts.py

The script uses matplotlib's Agg backend and writes figures to figures/. It imports
PALETTE, style_defaults(), and save_fig() from the supplied vizlib.py.

Data provenance
All datasets and numbers are synthetic, generated for CDB601220 Week 4. They are
not evidence about a real company. The supplied data dictionary defines columns;
diagnoses are derived from the supplied CSV rows and the assignment's published
recipes/self-checks.

Important notes
- Case 2's redesign preserves the calendar gaps instead of pretending each row is
  an equal elapsed-time interval; it does not fabricate weekend observations.
- Case 3 retains gaps in the hourly record and uses a daily mean for a level.
- Case 6 marks October as partial (11/31 days); no extrapolated monthly total is
  invented.
- Case 8 displays overlapping channel-touch rates as bars, not a pie.
- Case 9 separates the numerator and denominator in the same units.
