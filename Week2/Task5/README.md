# Week 2 Task 5 — Capstone: Perception redesign

## Files
- `task5_perception_redesign.ipynb`: notebook with the audit, chart creation, interpretation prompts, and human-reader record field.
- `task5_perception_redesign.py`: standalone script to regenerate both charts and the median summary CSV.
- `bad_example.png`: intentionally cluttered starting chart, 300 DPI.
- `perception_redesign.png`: redesigned chart, 300 DPI with `bbox_inches="tight"`.
- `median_price_by_carat_bin.csv`: medians and row counts by 0.1-carat bin, computed from all records.
- `data/diamonds.csv`: supplied source data.

## Data handling
The supplied CSV contains 53,940 rows and 11 columns. There are no missing values in the supplied columns. All 53,940 rows are used to calculate median price in each 0.1-carat bin. A deterministic sample of 2,500 rows (seed 42) is shown only as grey background context in the redesign; the bad example displays 5,000 sampled rows. This is disclosed on the figures. No rows are excluded from the median calculations.

## Question
How does diamond price change as carat increases?

## Perception audit — before

| Row | Audit of BAD EXAMPLE |
|---|---|
| Preattentive | Position (carat and price), colour hue, and point density are immediately visible. Red hue does not encode a meaningful variable; it adds noise rather than helping answer the question. |
| Pop-out | The saturated red cloud attracts attention everywhere, so no single finding pops out. The title only says “BAD EXAMPLE” and does not state a result. |
| Gestalt | **Proximity** groups nearby points into a dense cloud, but overplotting makes local density and individual values difficult to separate. |
| Cognitive load | **Intrinsic:** interpreting the carat–price relationship and the spread. **Extraneous:** 5,000 overlapping red marks, no summary, weak hierarchy. **Germane:** comparing x and y positions to infer association. |
| Channels | Carat → horizontal position (high-ranking quantitative channel). Price → vertical position (high-ranking quantitative channel). Red hue → colour (not useful for these numeric variables). Point density is an unintended secondary cue. |
| Working memory | More than ~4 chunks: the reader must mentally track the cloud, possible clusters, outliers, spread, and overall trend at once. |


## Redesign choices
- **Finding-led title:** “Median diamond price rises with carat, with a steeper climb above 1 ct.”
- **One intended pop-out:** the blue median line. Grey dots are context. The line is also labelled in the legend, so colour is not the only carrier.
- **Highest-ranking channel:** position on common quantitative axes for carat and price.
- **Named Gestalt principle:** similarity; grey points are treated as a contextual group, while the continuous blue line forms one summary series.
- **Chunking:** reader can focus on the grey distribution, blue median trend, and the single takeaway.
- **Trade-off / what becomes harder to see:** individual diamond prices and subtle local clusters are harder to compare because most points are greyed and only a 2,500-row sample is drawn as context. The median trend is clearer, but it hides the full distribution and outliers in the unsampled records.

## Perception audit — after

| Row | Audit of redesign |
|---|---|
| Preattentive | Position carries both quantitative variables. Grey points establish the distribution; one blue median line is the single strong-colour focal element. |
| Pop-out | The blue median line is the only intended pop-out and directly supports the finding-led title. The line is also explicitly named in the legend, so colour is not the sole carrier of meaning. |
| Gestalt | **Similarity** groups the grey points as background context, while the continuous blue line is perceived as one summary series. The grouping principle is named explicitly. |
| Cognitive load | **Intrinsic:** carat–price association and variation. **Extraneous:** removed red saturation and most overplotting; light grid is restrained. **Germane:** the median line compresses the trend into a readable summary. |
| Channels | Carat → horizontal position; price → vertical position; both are high-ranking quantitative channels. Blue hue separates the summary series from grey context but is redundant with line continuity, marker shape, and legend label. |
| Working memory | About 3 chunks: grey distribution, blue median trend, and the finding (steeper increase above 1 ct). |


## Human reader test — required real observation
Show **only `perception_redesign.png`** to someone who has not seen this dataset. Ask: “In one sentence, what does this chart show?” Record their answer exactly, including their wording and punctuation. Do not invent or paraphrase their response.

- Reader's verbatim sentence: **[FILL IN AFTER A REAL TEST]**
- Does it match the title? **[YES / PARTLY / NO — explain after the test]**
- What misled them, if anything? **[FILL IN]**
- What would you change next? **[FILL IN]**

## Reproduce
Install dependencies if needed:
```bash
%pip install pandas numpy matplotlib
```
In Jupyter, run the notebook cells from top to bottom. For the standalone script:
```bash
python task5_perception_redesign.py
```
The script resolves data relative to its own folder first. If running in Jupyter, the notebook uses the copied `data/diamonds.csv` path relative to the notebook's current working directory.
