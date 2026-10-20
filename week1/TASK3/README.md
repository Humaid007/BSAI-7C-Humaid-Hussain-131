# Task 3 — Penguin Distributions and Simpson's Paradox

## Missing data and decisions

The dataset contains 344 rows.

- Two penguins have all four numeric measurements missing. They are excluded from charts that require those measurements; no measurements are imputed.
- Eleven penguins have missing sex. They remain in charts that do not require sex, but are excluded from the species-and-sex body-mass comparison because their sex group is unknown.
- Each chart includes a note explaining the relevant missing-data decision.

## 1. Overall body-mass distribution

The overall histogram combines all species. It can show more than one hump because species have different typical body masses.

## 2. Body mass split by species

Splitting the distribution by species makes the mixture clearer. Gentoo penguins are generally heavier, while Adelie and Chinstrap penguins tend to have lower and partly overlapping body masses. The combined shape is therefore influenced by differences between species rather than representing one homogeneous group.

## 3. Bill length versus bill depth

The overall Pearson correlation is **-0.235**, which is negative. Within each species, the correlations are positive:

- Adelie: r = 0.391
- Chinstrap: r = 0.654
- Gentoo: r = 0.643

This is an example of **Simpson's paradox**: an association in the combined data reverses direction when the data are examined within subgroups. Species have different typical bill dimensions and occupy different regions of the scatter plot. The between-species differences can dominate the positive relationships within species, creating a negative pooled association.

Neither result is a calculation error. They describe different levels of the data. Splitting the plot by species prevents the overall pattern from being mistaken for the relationship within each species. See the Stanford Encyclopedia of Philosophy: https://plato.stanford.edu/entries/paradox-simpson/

## 4. Average body mass by species and sex

The grouped bar chart compares average body mass for females and males within each species. Sample sizes are shown above the bars. Penguins with missing sex are excluded only from this chart rather than being assigned an invented sex.

## Files

- `01_body_mass_distribution.png`
- `02_body_mass_by_species.png`
- `03_bill_length_vs_depth.png`
- `04_mean_body_mass_species_sex.png`
- `body_mass_summary_by_species.csv`
- `mean_body_mass_by_species_and_sex.csv`
- `missing_data_summary.csv`
- `penguins.csv`
- `task3.py`

## Run

Install dependencies if needed:

    pip install pandas numpy matplotlib

Then run:

    python task3.py
