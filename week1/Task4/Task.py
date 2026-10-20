from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = Path.cwd()
POSSIBLE_CSV_PATHS = [
    Path(r"C:\Users\Lenovo\Downloads\DV\data-visualization-main\week1\assignments\data\mpg.csv"),
    BASE_DIR / "mpg.csv",
]

if "__file__" in globals():
    POSSIBLE_CSV_PATHS.append(Path(__file__).resolve().parent / "mpg.csv")

CSV = next((path for path in POSSIBLE_CSV_PATHS if path.exists()), None)
if CSV is None:
    checked_paths = "\n".join(str(path) for path in POSSIBLE_CSV_PATHS)
    raise FileNotFoundError(
        "Could not find mpg.csv. Put mpg.csv in the notebook's current folder or "
        "update the first path in POSSIBLE_CSV_PATHS. Paths checked:\n" + checked_paths
    )

OUT = BASE_DIR / "Task 4 - MPG outputs"
OUT.mkdir(parents=True, exist_ok=True)

print(f"Loading dataset from: {CSV}")
print(f"Saving outputs to: {OUT}")
df = pd.read_csv(CSV)
required = ['mpg','cylinders','displacement','horsepower','weight','acceleration','model_year','origin','name']
missing = set(required) - set(df.columns)
if missing:
    raise ValueError(f'mpg.csv is missing required columns: {sorted(missing)}')

df['origin'] = df['origin'].astype(str).str.strip().str.lower()
origin_names = {'usa':'American', 'europe':'European', 'japan':'Japanese'}
df['origin_label'] = df['origin'].map(origin_names).fillna(df['origin'].str.title())
df['year'] = pd.to_numeric(df['model_year'], errors='coerce').astype('Int64') + 1900
# model_year values are 70..82, so 1900 + code gives 1970..1982.
df['year'] = df['year'].astype(int)

missing_summary = pd.DataFrame({
    'column': df.columns,
    'missing_count': [int(df[c].isna().sum()) for c in df.columns],
    'missing_percent': [round(float(df[c].isna().mean()*100), 2) for c in df.columns],
})
missing_summary.to_csv(OUT / 'missing_data_summary.csv', index=False)

annual = df.groupby('year', as_index=False).agg(mean_mpg=('mpg','mean'), median_mpg=('mpg','median'), cars=('mpg','size'))
annual.to_csv(OUT / 'fuel_efficiency_by_year.csv', index=False)
fig, ax = plt.subplots(figsize=(10,6))
ax.plot(annual['year'], annual['mean_mpg'], marker='o', linewidth=2.4, label='Mean MPG')
ax.plot(annual['year'], annual['median_mpg'], marker='s', linewidth=1.6, linestyle='--', label='Median MPG')
ax.set(title='Did Cars Become More Fuel-Efficient? (1970–1982)', xlabel='Model year', ylabel='Fuel efficiency (miles per gallon)')
ax.set_xticks(annual['year'])
ax.tick_params(axis='x', rotation=45)
ax.grid(alpha=.25)
ax.legend(frameon=False)
ax.text(.01, -.22, 'Each point summarizes cars from that model year; horsepower missingness does not affect this chart.', transform=ax.transAxes, fontsize=8.5)
fig.tight_layout()
fig.savefig(OUT / '01_fuel_efficiency_over_time.png', dpi=180, bbox_inches='tight'); plt.close(fig)

origin_order = ['American','European','Japanese']
origin_data = [df.loc[df['origin_label']==name, 'mpg'].dropna().to_numpy() for name in origin_order]
origin_summary = df.groupby('origin_label', as_index=False).agg(cars=('mpg','size'), mean_mpg=('mpg','mean'), median_mpg=('mpg','median'))
origin_summary.to_csv(OUT / 'fuel_efficiency_by_origin.csv', index=False)
fig, ax = plt.subplots(figsize=(9,6))
box = ax.boxplot(origin_data, tick_labels=origin_order, patch_artist=True, showmeans=True, meanline=False)
for patch in box['boxes']:
    patch.set_alpha(.55)
for i, vals in enumerate(origin_data, start=1):
    rng = np.random.default_rng(100+i)
    x = rng.normal(i, 0.055, size=len(vals))
    ax.scatter(x, vals, s=13, alpha=.28, zorder=2)
for i, row in enumerate(origin_summary.set_index('origin_label').reindex(origin_order).itertuples(), start=1):
    ax.text(i, max(origin_data[i-1]) + 1.2, f"n={len(origin_data[i-1])}", ha='center', fontsize=9)
ax.set(title='Fuel Efficiency by Country of Origin', xlabel='Origin', ylabel='Fuel efficiency (miles per gallon)')
ax.grid(axis='y', alpha=.25)
ax.text(.01, -.18, 'Boxes show the median and interquartile range; points show individual cars. Six missing horsepower values are irrelevant here.', transform=ax.transAxes, fontsize=8.5)
fig.tight_layout()
fig.savefig(OUT / '02_mpg_by_origin_boxplot.png', dpi=180, bbox_inches='tight'); plt.close(fig)

fig, ax = plt.subplots(figsize=(9,6))
for label in origin_order:
    part = df[df['origin_label']==label]
    ax.scatter(part['weight'], part['mpg'], s=28, alpha=.65, label=label)
valid = df[['weight','mpg']].dropna()
slope, intercept = np.polyfit(valid['weight'], valid['mpg'], 1)
xx = np.linspace(valid['weight'].min(), valid['weight'].max(), 120)
cor = valid['weight'].corr(valid['mpg'])
ax.plot(xx, slope*xx+intercept, color='black', linewidth=2.2, linestyle='--', label=f'Linear trend (r={cor:.2f})')
ax.set(title='Heavier Cars Tend to Have Lower Fuel Efficiency', xlabel='Weight (lb)', ylabel='Fuel efficiency (miles per gallon)')
ax.grid(alpha=.22); ax.legend(frameon=False)
ax.text(.01, -.18, 'Each point is a car; dashed line is the overall least-squares trend. Horsepower missingness does not affect this chart.', transform=ax.transAxes, fontsize=8.5)
fig.tight_layout()
fig.savefig(OUT / '03_weight_vs_mpg_scatter.png', dpi=180, bbox_inches='tight'); plt.close(fig)

cyl_counts = df['cylinders'].value_counts().sort_index().rename_axis('cylinders').reset_index(name='cars')
cyl_counts['percent'] = cyl_counts['cars'] / len(df) * 100
cyl_counts.to_csv(OUT / 'cylinder_distribution.csv', index=False)
fig, ax = plt.subplots(figsize=(8,5.5))
bars = ax.bar(cyl_counts['cylinders'].astype(str), cyl_counts['cars'], edgecolor='white', alpha=.85)
ax.bar_label(bars, labels=[f'{int(n)} ({p:.1f}%)' for n,p in zip(cyl_counts['cars'],cyl_counts['percent'])], padding=3, fontsize=9)
ax.set(title='How Many Cylinders Do Cars Have?', xlabel='Number of cylinders', ylabel='Number of cars')
ax.set_ylim(0, max(cyl_counts['cars'])*1.18)
ax.grid(axis='y', alpha=.22)
ax.text(.01, -.17, f'All {len(df)} cars are included; bars are ordered by cylinder count.', transform=ax.transAxes, fontsize=8.5)
fig.tight_layout()
fig.savefig(OUT / '04_cylinder_count_distribution.png', dpi=180, bbox_inches='tight'); plt.close(fig)

annual_weight = df.groupby('year', as_index=False).agg(mean_weight=('weight','mean'), median_weight=('weight','median'), cars=('weight','size'))
annual_both = annual.merge(annual_weight, on='year', suffixes=('_mpg','_weight'))
annual_both.to_csv(OUT / 'mpg_and_weight_by_year.csv', index=False)
fig, (ax1, ax2) = plt.subplots(2,1,figsize=(10,8),sharex=True)
ax1.plot(annual_both['year'], annual_both['mean_mpg'], marker='o', linewidth=2.2)
ax1.set(title='Did Cars Get More Efficient Because They Got Lighter?', ylabel='Mean MPG')
ax1.grid(alpha=.22)
ax2.plot(annual_both['year'], annual_both['mean_weight'], marker='s', linewidth=2.2)
ax2.set(xlabel='Model year', ylabel='Mean weight (lb)')
ax2.grid(alpha=.22)
ax2.set_xticks(annual_both['year']); ax2.tick_params(axis='x', rotation=45)
fig.text(.01, .005, 'Both panels use the same years and annual averages. This shows whether fuel economy rose while average weight fell; it does not prove weight is the only cause.', fontsize=8.5)
fig.tight_layout(rect=[0,.04,1,1])
fig.savefig(OUT / '05_mpg_and_weight_over_time.png', dpi=180, bbox_inches='tight'); plt.close(fig)


fig, ax = plt.subplots(figsize=(9,6))
parts = [df.loc[df['origin_label']==name, 'mpg'].dropna().to_numpy() for name in origin_order]
box = ax.boxplot(parts, tick_labels=origin_order, patch_artist=True, showmeans=True, widths=.52,
                 medianprops={'linewidth':2.2}, whiskerprops={'linewidth':1.3}, capprops={'linewidth':1.3})
for patch in box['boxes']:
    patch.set_alpha(.38)
for i, vals in enumerate(parts, start=1):
    rng = np.random.default_rng(200+i)
    ax.scatter(rng.normal(i, .07, len(vals)), vals, s=17, alpha=.36, edgecolors='none')
    med = float(np.median(vals))
    ax.annotate(f'median {med:.1f}', (i, med), xytext=(8,0), textcoords='offset points', va='center', fontsize=8.5)
ax.set(title='Redrawn: Comparing MPG Across Origins', xlabel='Origin', ylabel='Fuel efficiency (miles per gallon)')
ax.grid(axis='y', alpha=.22)
ax.text(.01, -.18, 'Redesign: added individual observations, labelled medians, widened spacing and simplified the display.', transform=ax.transAxes, fontsize=8.5)
fig.tight_layout()
fig.savefig(OUT / '06_redraw_origin_comparison.png', dpi=180, bbox_inches='tight'); plt.close(fig)

first_year, last_year = int(annual['year'].min()), int(annual['year'].max())
first_mpg = float(annual.loc[annual.year==first_year,'mean_mpg'].iloc[0])
last_mpg = float(annual.loc[annual.year==last_year,'mean_mpg'].iloc[0])
first_weight = float(annual_weight.loc[annual_weight.year==first_year,'mean_weight'].iloc[0])
last_weight = float(annual_weight.loc[annual_weight.year==last_year,'mean_weight'].iloc[0])
mpg_change = last_mpg-first_mpg
weight_change = last_weight-first_weight
origin_means = origin_summary.set_index('origin_label')['mean_mpg'].to_dict()
cyl_text = ', '.join(f"{int(r.cylinders)} cylinders: {int(r.cars)} cars ({r.percent:.1f}%)" for r in cyl_counts.itertuples())
readme = f'''# Task 4 — Pick the Right Chart, Five Times (MPG)

## Data checks and missing values

The dataset contains {len(df)} cars and years {first_year}–{last_year}. The `horsepower` column has {int(df['horsepower'].isna().sum())} missing values. None of the five questions requires horsepower, so all {len(df)} cars are retained for these charts; no horsepower values are imputed. The missingness summary is saved as `missing_data_summary.csv`.

## 1. Did cars get more fuel-efficient between 1970 and 1982?

**Chart:** Line chart of annual mean and median MPG. A line chart is appropriate because model year is ordered in time and the question asks about change over time.

Mean MPG changed from **{first_mpg:.2f}** in {first_year} to **{last_mpg:.2f}** in {last_year} (change: {mpg_change:+.2f} MPG). The annual pattern indicates whether fuel efficiency generally improved; the line may fluctuate between individual years.

## 2. Do American, European and Japanese cars differ in fuel efficiency?

**Chart:** Box plot with individual observations overlaid. A box plot compares distributions across categories, showing medians, spread and possible outliers; the points reveal the individual cars behind each summary. Mean MPG: American {origin_means.get('American', float('nan')):.2f}, European {origin_means.get('European', float('nan')):.2f}, Japanese {origin_means.get('Japanese', float('nan')):.2f}.

## 3. What is the relationship between weight and fuel efficiency?

**Chart:** Scatter plot with an overall fitted line. Both weight and MPG are numeric measurements, so a scatter plot shows the direction, strength, spread and potential outliers of their relationship. The overall Pearson correlation is **{cor:.3f}**; a negative value indicates heavier cars tend to have lower MPG.

## 4. How is the number of cylinders distributed across the fleet?

**Chart:** Ordered bar chart. Cylinder count is a discrete category, so bars make it easy to compare the number and percentage of cars in each category.

{cyl_text}.

## 5. Is the improvement in fuel efficiency explained by cars getting lighter?

**Chart:** Two aligned line charts showing annual mean MPG and annual mean weight. Using the same year axis makes it easy to compare the trends without mixing different units on one axis. Mean weight changed from **{first_weight:.1f} lb** in {first_year} to **{last_weight:.1f} lb** in {last_year} (change: {weight_change:+.1f} lb), while mean MPG changed by {mpg_change:+.2f}. If MPG rises while weight falls, lighter cars are a plausible contributor, but these descriptive charts cannot establish that weight alone explains the improvement; engine technology and other factors may also matter.

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
'''
(OUT/'README.md').write_text(readme, encoding='utf-8')
