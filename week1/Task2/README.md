# Task 2 — Trends and the Spaghetti Problem

## 1. Problems with the spaghetti chart

The chart draws one line for each of 142 countries, making it crowded and difficult to read. The lines overlap, many colours compete for attention, and the 142-item legend is too large to scan. It is difficult to identify an overall trend or compare individual countries.

## 2(a). Aggregate by continent

The continent chart replaces 142 country lines with five lines showing average life expectancy by continent. This makes broad regional trends easier to compare. Average life expectancy increased in every continent from 1952 to 2007.

Aggregation is clearer for regional patterns, but it hides variation between countries within each continent.

## 2(b). Highlight three countries

The highlight chart keeps all country lines in the background in grey and emphasizes China, the United States, and Afghanistan with colour and direct labels. This retains context while making the selected trajectories easier to follow.

Unlike aggregation, highlighting preserves individual country trends. However, it does not summarize continent-level patterns as clearly, and the grey background can still be busy.

## 3. Aggregate versus highlight

The aggregate chart is best for comparing broad regional trends and reducing clutter, but it hides country-level differences. The highlight chart is best for examining selected countries while retaining wider context, but it does not provide a concise summary of all countries.

## 4. Has the richest-poorest GDP gap narrowed?

This analysis measures the gap using the ratio of the highest to lowest GDP per capita in each year. The ratio was approximately 362.67 in 1952 and 177.83 in 2007. Therefore, by this measure, the ratio was lower in 2007 than in 1952, although the trend was not steadily downward.

The chart uses a logarithmic y-axis because the ratios vary considerably. The countries at the extremes may change from year to year, so this measure does not describe the gap between typical countries.

## 5. GDP histogram and log scale

GDP per capita is strongly right-skewed: many observations are at lower values, while a smaller number of high values stretch the distribution to the right. On the raw scale, the large values compress much of the distribution near the left side.

A log10 transformation spreads lower values apart and compresses higher values, making the distribution easier to inspect. The transformation is valid here because GDP per capita is positive. However, a log scale changes how distances between values appear.

## How to run

Install the required libraries if necessary:

    pip install pandas numpy matplotlib

Keep gapminder.csv beside task2.py, then run:

    python task2.py

The script creates four charts and two CSV output tables in the same folder.
