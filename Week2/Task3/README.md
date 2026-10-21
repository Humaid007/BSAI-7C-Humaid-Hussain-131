# Week 2 — Task 3: Cognitive Load and Data-Ink Ratio

## Data and units
The supplied `car_crashes.csv` contains 51 rows and columns `total, speeding, alcohol, not_distracted, no_previous, ins_premium, ins_losses, abbrev`. This task plots only `total`. Do not put `speeding`, `alcohol`, `not_distracted`, `no_previous`, `ins_premium`, or `ins_losses` on the same axis: these represent different units/scales. The `tips.csv` file contains 244 rows.

## 1. Deliberately overloaded chart
`01_BAD_EXAMPLE_overloaded.png` is explicitly labelled **BAD EXAMPLE**. It uses 51 distinct colours, all state labels rotated, heavy gridlines in both directions, a full frame, and a 51-entry legend. A 3-D effect is intentionally omitted because it would add distortion without useful information; the other requested sources of clutter are present.

## 2. Element classification and data-ink estimate
See `load_classification.csv` for each element, its category, and rationale. Classification depends on purpose: bars encode the values (intrinsic), scale/ticks help decode values (germane), while arbitrary colours, excessive gridlines, redundant legend and frame are extraneous. State labels identify observations but all 51 rotated labels are excessive in this layout.

**Estimated data-ink ratio working:** count each of the 51 bars as one data mark. Estimate 271 non-data marks from labels, gridline segments, frame, legend and axes/ticks. Then data-ink ratio ≈ 51 / (51 + 271) = **0.158**. This is a transparent approximate mark-count method, not a pixel-based measurement; results depend on the counting rule.

## 3. Five-panel reduction
`02_five_panel_reduction.png` shows progressive edits. Sorting is especially valuable because it adds no ink: it changes position only and makes rank immediately visible. The last panel labels only the five highest values and uses a single pop-out for the highest bar. A small grey tick-label system preserves context.

## 4. Working-memory chunking
`03_chunked_top5_other46.png` shows the top five states individually and pools the remaining 46 as one mean. This yields six chunks, within the practical 4 ± 1 range. Cost: the individual values and ordering within the pooled 46 states are hidden; the mean is not a substitute for their full distribution.

## 5. Over-stripped example and stopping rule
`04_BAD_EXAMPLE_overstripped.png` removes labels, tick values and units. The data-ink ratio could rise because explanatory marks disappear, but readers can no longer identify values or interpret the scale.

**Stopping rule:** Remove an element only when it contributes no meaningful encoding, orientation, comparison, or context needed for the reader's task.

## Question: adding ink can lower cognitive load
`05_tips_reference_line.png` plots mean tip percentage by day and adds an overall-mean reference line with a direct numeric label. The line and annotation add ink but spare readers from calculating the overall mean mentally and comparing it across bars. Maximising data-ink is a heuristic, not a rule: the goal is fast and accurate interpretation, not the fewest possible marks.

## Outputs
- `01_BAD_EXAMPLE_overloaded.png`
- `02_five_panel_reduction.png`
- `03_chunked_top5_other46.png`
- `04_BAD_EXAMPLE_overstripped.png`
- `05_tips_reference_line.png`
- `load_classification.csv`
- `data_ink_ratio_working.csv`

All charts are exported at 300 DPI. Code uses the object-oriented Matplotlib API (`fig, ax = plt.subplots()` and `ax` methods).
