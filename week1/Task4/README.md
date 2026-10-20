# Task 4 — Pick the Right Chart, Five Times (MPG)

## Data checks and missing values

The dataset contains 398 cars and years 1970–1982. The `horsepower` column has 6 missing values. None of the five questions requires horsepower, so all 398 cars are retained for these charts; no horsepower values are imputed. The missingness summary is saved as `missing_data_summary.csv`.

## 1. Did cars get more fuel-efficient between 1970 and 1982?

**Chart:** Line chart of annual mean and median MPG. A line chart is appropriate because model year is ordered in time and the question asks about change over time.

Mean MPG changed from **17.69** in 1970 to **31.71** in 1982 (change: +14.02 MPG). The annual pattern indicates whether fuel efficiency generally improved; the line may fluctuate between individual years.

## 2. Do American, European and Japanese cars differ in fuel efficiency?

**Chart:** Box plot with individual observations overlaid. A box plot compares distributions across categories, showing medians, spread and possible outliers; the points reveal the individual cars behind each summary. Mean MPG: American 20.08, European 27.89, Japanese 30.45.

## 3. What is the relationship between weight and fuel efficiency?

**Chart:** Scatter plot with an overall fitted line. Both weight and MPG are numeric measurements, so a scatter plot shows the direction, strength, spread and potential outliers of their relationship. The overall Pearson correlation is **-0.832**; a negative value indicates heavier cars tend to have lower MPG.

## 4. How is the number of cylinders distributed across the fleet?

**Chart:** Ordered bar chart. Cylinder count is a discrete category, so bars make it easy to compare the number and percentage of cars in each category.

3 cylinders: 4 cars (1.0%), 4 cylinders: 204 cars (51.3%), 5 cylinders: 3 cars (0.8%), 6 cylinders: 84 cars (21.1%), 8 cylinders: 103 cars (25.9%).

## 5. Is the improvement in fuel efficiency explained by cars getting lighter?

**Chart:** Two aligned line charts showing annual mean MPG and annual mean weight. Using the same year axis makes it easy to compare the trends without mixing different units on one axis. Mean weight changed from **3372.8 lb** in 1970 to **2453.5 lb** in 1982 (change: -919.2 lb), while mean MPG changed by +14.02. If MPG rises while weight falls, lighter cars are a plausible contributor, but these descriptive charts cannot establish that weight alone explains the improvement; engine technology and other factors may also matter.

## Redraw the weakest chart

I chose the origin-comparison chart (Question 2) as the weakest first version because a box plot alone can hide how many observations sit within each group. The redraw keeps the same comparison but overlays jittered individual points, labels each median, and simplifies the styling. This makes sample distribution and group medians easier to compare without switching to a chart type that would obscure the spread.

## Output files

- `01_fuel_efficiency_over_time.png`
- `02_mpg_by_origin_boxplot.png`
- `03_weight_vs_mpg_scatter.png`
- `04_cylinder_count_distribution.png`
- `05_mpg_and_weight_over_time.png`
- `06_redraw_origin_comparison.png`
- CSV summaries and `missing_data_summary.csv`
- `mpg.csv` and `task4.py`

## Run

Install dependencies: `pip install pandas numpy matplotlib`

Keep `mpg.csv` beside `task4.py`, then run: `python task4.py`
