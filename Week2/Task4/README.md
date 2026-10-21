# Week 2 — Task 4: Channel effectiveness

## Encoding choices
- **Position:** two dots on a shared invisible scale.
- **Length:** two bars from a common zero baseline.
- **Angle:** two pie wedges representing each value's share of the pair total.
- **Area:** circle area is proportional to value; radius scales with the square root of value. In `ax.scatter`, `s` is area, not radius.
- **Colour:** sequential greyscale lightness, not rainbow colour.

## Real-reader procedure
The 30 supplied trials are shuffled. Enter the participant's actual estimate of the smaller value as a percentage of the larger. True ratios are not displayed during trials. The script calculates `absolute_error = abs(reader_estimate/100 - true_ratio)` and saves `channel_results.csv`. Do not fabricate estimates.

## Interpreting the ranking
The assignment's published order is `position > length > angle > area > volume > colour`, where greater means more accurate. This experiment tests only five channels, so it cannot rank volume. With six ratios and one reader, the results are descriptive for this reader and these stimuli; they cannot establish population-level rankings or statistical significance. The published ranking remains a useful prior guideline because it reflects broader evidence than this small sample. Report disagreement honestly; individual strategy, practice and noise can affect a small experiment.

## Iris application
Both charts show the same mean petal length by species. Position on a common scale is recommended because position is generally decoded more accurately than lightness. The second chart uses sequential greyscale tiles and omits exact values to demonstrate the lower-precision channel.
