# Week 2 — Task 1: Preattentive Attributes and Visual Search

## Important design note
The brief asks for 18 trials and also says to include one target-present and one target-absent trial for every condition × set-size cell. Since 3 conditions × 5 set sizes × 2 target statuses = 30 trials, these cannot both be true. The provided script follows the 18-trial limit by using set sizes 9, 25, and 49. Change `EXPERIMENT_SET_SIZES` to all five set sizes if your instructor confirms that 30 trials are expected.

## Files
- `task1_visual_search.py`: complete script.
- `stimuli_search.csv`: supplied stimulus dataset.
- `01_trial_rendering_check.png`: generated verification preview showing one 25-item trial from each condition.

## Run in Jupyter
Install packages if needed:
```bash
pip install pandas numpy matplotlib
```
Run the script cell, then call:
```python
preview_one_per_condition()
results = run_human_experiment()
summary, slopes = analyze_results(results)
write_readme(results, slopes)
```

The script measures a real participant's response time with `time.perf_counter()`, records correctness, and saves `search_results.csv`. It does not fabricate participant data. The response-time chart and slope report are created only after the experiment is completed.

## Required interpretations
- A feature-search condition is expected to have a near-flat target-present response-time slope.
- The conjunction condition is expected to rise with set size because colour and shape must be bound together; distractors share one target feature, so attention may need to inspect candidate items.
- Target-absent trials are kept separate from target-present trials.
- Slopes describe one reader and a small number of observations. If the pattern differs from theory, report the observed slope and possible reasons rather than changing the data.
- A chart that uses both colour and marker shape to identify series can unintentionally ask readers to find a conjunction of visual features.
