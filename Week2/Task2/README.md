# Week 2 — Task 2: Gestalt principles of grouping

## Outputs and how to run

Install dependencies with `pip install pandas numpy matplotlib`. Keep `stimuli_gestalt.csv` beside the script or update `POSSIBLE_DATA_PATHS`. Run the script, then call `render_all_panels()` and `render_connection_comparison()` to make the static figures. Call `run_real_reader_experiment()` with a real participant to collect their actual group-count judgements. Do not fabricate responses.

All required chart exports are 300 DPI. The closure panel intentionally retains 44 items. The similarity panel uses spatially mixed colour categories so colour—not spatial separation—signals grouping. Enclosure boundaries are drawn with unfilled grey rectangles. Connection lines are drawn between records sharing the same connector value.

## Real-reader results

The code writes `gestalt_reader_results.csv` after a participant answers all six panels and both versions of the connection panel. This file is intentionally created only by running the experiment. Report the participant's actual perceived counts and mismatches; one reader is not enough to make universal claims. For the connection cue test, compare the line-visible and line-hidden counts to judge whether connection beat similarity and proximity for this reader.

## Gestalt principles in charts

- **Proximity:** bars or points placed closer within a category than between categories are perceived as a group.
- **Similarity:** consistent colour, shape, or marker style signals that marks share a category; colour should not be the only carrier of meaning.
- **Enclosure:** a shaded region or outlined box makes marks inside it read as a group.
- **Closure:** a border or nearly closed shape lets the reader perceive a complete region despite a gap.
- **Continuity:** a line connecting successive values guides the eye along a path.
- **Connection:** a line between two marks makes them appear related even when they differ in colour or are not nearest neighbours.

## Why direct labels can reduce cognitive load

Direct labels use **proximity**: the label is placed beside the item it describes. A legend requires the reader to hold a colour/category mapping in working memory, move attention between legend and chart, and repeatedly match marks to legend entries. Direct labelling shortens that search path and reduces working-memory demand. This is a cognitive-load argument, not simply a style preference.

## Tips.csv proximity comparison

The two tips charts use the same mean tip values by day and smoker status. In the proximity version, bars within each day are separated by a smaller gap than the gap between days. In the equal-spacing version, every bar is spaced evenly. The second version makes day-level grouping less immediate, so the reader must rely more on repeated tick labels and colour legend instead of spatial chunking. If `tips.csv` is not found, place it beside the script or update the path candidates and rerun `tips_proximity_charts()`.

## Cognitive load and data-ink

Data-bearing dots, connector lines, and the enclosure rectangles carry the intended grouping information. Axis ticks, spines, and unnecessary gridlines are removed from stimulus panels because they do not help judge group count. No data-ink ratio is reported, so no unsupported ratio calculation is implied.

## Reporting note

Use finding-led titles for analytical charts and keep context neutral grey. Use no more than one visual pop-out in any final analytical chart. The six stimulus panels retain their intended categorical colour differences as part of the experimental manipulation.
