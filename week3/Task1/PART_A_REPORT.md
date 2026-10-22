# Week 3 — Part A: Diagnose the nine charts

All supplied data are synthetic course datasets. Charts and statistics below are regenerated from the supplied CSVs. Each case includes the analyst's recipe, the misleading conclusion, a decoy objection, the mechanism supported by data, and a redesign.

## Reproducibility and exclusions
- Source CSVs are copied into `data/`; code reads them relative to the script folder.
- Charts are exported at 300 DPI with `bbox_inches='tight'`.
- No rows were dropped from cases 1–7 unless noted; numeric correlation uses numeric columns after excluding the named grouping columns. The vitals histogram/KDE uses non-missing values for the plotted field and declares n.
- Case 3 means skip missing AQI values by pandas default; the changing count of reporting stations is explicitly shown as a limitation.
- Case 6 excludes `age_band`, `study_site`, and `hr_device_model`; this leaves 20 numeric columns, including the six uncalibrated probes.
- Case 8/9 use `dropna()` on the plotted vital; no missing values are present in the provided vitals CSV.

## 1. Helmet rates
**Rebuild/self-check:** Standard 2.15; Premium 5.40 injuries per 1,000 trips. The crude premium rate is 2.51× Standard.
**Invited conclusion:** premium certification itself increases injury risk. **Decoy:** “correlation is not causation” is too vague; the data allow a more precise check.
**Mechanism:** road-type mix differs sharply: Premium riders logged 34,000 motorway trips out of 40,000, while Standard riders logged only 2,000 of 60,000. Within road type, the crude premium rate is lower on City arterial (2.20 vs 3.00) and Inner-city lanes (1.00 vs 1.39), but lower on Motorway too (6.00 vs 8.00). The aggregate reversal is a road-type composition / Simpson's-paradox style confounding pattern; speed also differs (Premium mean 67.0 kph vs Standard 30.2), so helmet-only causal inference is unsupported.
**Redesign:** stratified rate plot, shown in `case01_redesign.png`.

## 2. Chai and quiz failures
**Rebuild/self-check:** Pearson r = 0.982 (expected about 0.98); least-squares line fitted.
**Invited conclusion:** chai sales predict failures. **Decoy:** “correlation is not causation” alone is not the mechanism.
**Mechanism:** enrollment is a common scale/exposure variable. Cups sold correlate with students enrolled at r = 0.997; failures correlate with enrollment at r = 0.977. More students mean more cups and more failures in absolute counts. Exam month is available as another context variable but enrollment alone explains the near lockstep.
**Redesign:** plot failures against enrollment and show chai sales only as contextual shading (`case02_redesign.png`). Counts could also be normalized per enrolled student/open day.

## 3. AQI before/after
**Rebuild/self-check:** days 1–60 mean = 202.1; days 61–120 mean = 137.2; decrease = 32.1%.
**Invited conclusion:** the action plan caused a one-third fall. **Decoy:** the zero baseline is required by the recipe and is not the issue.
**Mechanism:** changing station coverage changes which stations contribute to each daily mean. There are 22 possible stations/day, but reporting count ranges 13–22 (mean 17.5); first 60 days contribute 1320 station-day readings and the last 60 only 780. `mean()` silently excludes blanks. The 32% comparison is therefore not a balanced same-station comparison and cannot isolate an intervention effect.
**Redesign:** separate panels for daily mean AQI and station reporting count (`case03_redesign.png`); an even stronger analysis would compare a fixed panel of continuously reporting stations.

## 4. Department quartet
**Rebuild/self-check:** computed table in `case04_statistics.csv`. All four groups have n=11 and mean hours ≈18.00, mean score ≈14.50, SD hours ≈6.63, score SD ≈2.03, Pearson r ≈0.816 and regression slope ≈0.25.
**Invited conclusion:** fund equally because the departments behave identically. **Decoy:** saying “means hide variation” is directionally true but incomplete.
**Mechanism:** the data are constructed as near-identical summary-statistic replicas; tiny score differences aside, the groups have almost the same marginal distributions and linear association. The summaries themselves do not measure funding need, cost-effectiveness, course quality, or causal return. The plot confirms there is no obvious department separation on these two variables, but that is not evidence for equal funding; the decision criterion is absent from the dataset.
**Redesign:** show department-level observations and avoid presenting the shared r as a funding recommendation (`case04_redesign.png`).

## 5. Same-statistics shapes
**Rebuild/self-check:** `case05_statistics.csv` shows each cohort has n=180, means ≈48 and 63, SDs ≈12.03 and 15.04, and r≈0.420.
**Invited conclusion:** cohorts behave the same because summary statistics match. **Decoy:** sample size is not small (180 per cohort), so this is not a small-sample objection.
**Mechanism:** different joint distributions can share the same first two moments and correlation. The actual shapes—straight line, ring, star, X, and two clusters—differ visibly even though the summaries match. Aggregating to mean/SD/r destroys shape information.
**Redesign:** small multiples of the actual observations (`case05_redesign.png`), with shared axes so shape differences are directly comparable.

## 6. Sensor correlation matrix
**Rebuild/self-check:** matrix is 20×20; creatinine↔HbA1c r=0.77; systolic↔MAP r=0.96.
**Invited conclusion:** creatinine tracks HbA1c as a meaningful clinical finding. **Decoy:** “correlation is not causation” is not the specific problem.
**Mechanism in the data:** MAP is arithmetically derived from systolic and diastolic pressure, so systolic↔MAP r=0.958 is partly built into the formula. `probe_a`–`probe_f` are uncalibrated instrument channels, not clinical measurements, yet the correlation matrix treats them as meaningful variables. Creatinine↔HbA1c r=0.765 is an association in this synthetic cohort, not by itself a validated clinical finding.
**Drawing problem:** `cmap='Reds'` with no fixed `vmin`/`vmax` makes positive/negative distinctions hard and maps colour intensity to each plot's data range; showing both symmetric triangles duplicates every correlation. A diverging palette fixed to [-1,1] and one triangle improves interpretation, but **does not solve** the invalid interpretation of derived MAP or uncalibrated probes. Redesign in `case06_redesign.png`.

## 7. Dual-axis revenue and cost
**Rebuild/self-check:** dual axes make cost appear above revenue during the first four months because their independently chosen scales differ.
**Invited conclusion:** losses until May. **Decoy:** “the y-axis is truncated” is true but does not fully name the mechanism.
**Mechanism:** independent affine rescaling of two axes visually changes their relative vertical positions. In actual values, revenue exceeds cost in every month: Jan 52>44, Feb 58>46, Mar 61>47, Apr 66>49, May 71>51, Jun 78>53 (PKR millions). Profit is positive throughout, from 8 to 25 million. The y-axis truncation and twin scales manufacture a false crossing impression.
**Redesign:** two aligned panels with zero baselines and same units, no dual axis (`case07_redesign.png`).

## 8. Histogram bin widths
**Rebuild/self-check:** n=10,000 in each panel; all use the same systolic observations.
**Invited conclusion:** the data have three different distributions depending on bins. **Decoy:** the sample size is not changing; n is identical in all panels.
**Mechanism:** histogram binning is a discretization choice. Three bins hide modality and shape; 400 bins create sparse jagged bars; 45 is an intermediate view. The observations did not change, only the partition of the x-axis did.
**Redesign:** use a declared 2 mmHg bin width and label n (`case08_redesign.png`). This is a design choice, not a uniquely correct binning for all purposes.

## 9. SpO₂ KDE beyond 100%
**Rebuild/self-check:** observed maximum = 100; observed values above 100 = 0. The Gaussian KDE nevertheless assigns positive smoothed density above 100 because its kernels spread beyond each observation.
**Invited conclusion:** 4.4% of observed saturation lies above 100%. **Decoy:** the x-axis extension is not a data error; it simply reveals the estimator's tail.
**Mechanism:** Gaussian kernel density estimation is a smoothing estimator with unbounded kernels. At a hard physical boundary (100%), symmetric kernels leak estimated density beyond the allowed support. The tail is a model artefact, not observed patients. The exact integrated KDE tail depends on the default bandwidth and should not be described as an observed-data percentage.
**Redesign:** show the empirical proportion at each integer SpO₂ value and mark the 100% ceiling (`case09_redesign.png`).

## Files
- `outputs/caseNN_rebuild.png`: recipe reproduction (cases 1–9).
- `outputs/caseNN_redesign.png`: more honest redesign.
- `outputs/case04_statistics.csv`, `case05_statistics.csv`, `case06_correlation_matrix.csv`: tables.
- `taskA_diagnose_nine.py`: regenerates the deliverables.

## Important interpretation note
Case 4 cannot establish that departments should be funded equally: funding criteria are not in the CSV. Case 1's stratified rates show road-type composition and rider speed are relevant confounders; they do not establish a causal helmet effect. Case 3 is an uncontrolled before/after comparison with varying station coverage.
