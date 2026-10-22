# Week 4 Part B package

Files:
- `PART_B_REPORT.md`: worked report and interpretation.
- `partB_analysis.py`: reproducible calculations.
- `sessions_hourly.csv`: uploaded source data.
- `tslib.py`, `vizlib.py`: course helper libraries.
- `results/`: generated CSV outputs.

Run from this directory:
```bash
python -m pip install pandas numpy statsmodels matplotlib
python partB_analysis.py
```

All data are synthetic course data. The script explicitly interpolates missing whole days only for methods that require a complete series; the cleaned daily CSV retains missing days as blank.
