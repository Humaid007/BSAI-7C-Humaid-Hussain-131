# Task 5 — A Real Time Series (Flights)

## Data preparation

The dataset contains 144 monthly records from 1949 through 1960. I converted `year` and `month` into a real datetime column by assigning the first day of each month, then sorted chronologically. This is important because month names alone do not form a continuous, ordered time axis across years.

## 1. Monthly passengers over time

**Chart:** `01_passengers_over_time.png` — a single line chart. A line chart suits ordered monthly observations and shows both the long-term growth and repeating annual pattern. The monthly average rose from 126.7 passengers (thousands) in 1949 to 476.2 in 1960.

## 2. Seasonal cycle by year

**Chart:** `02_seasonal_cycle_by_year.png` — one line per year with months aligned on the x-axis. This makes within-year peaks and troughs easier to compare across years, but the overlapping lines and changing overall scale make it busy.

## 3. Which month is consistently busiest?

**Chart:** `03_busiest_month_seasonal_index.png` — a bar chart of each month's average passenger count relative to that year's average (annual average = 100%). Normalizing within each year reduces the influence of the long-term growth trend and makes the recurring seasonal pattern easier to compare. **August** has the highest average seasonal index (123.7% of the annual average).

## 4. Which chart belongs in a report?

I would put **Chart 1 (monthly passengers over time)** in a general report because it gives the essential overview: the long-term increase and the repeating seasonal pattern in one compact graphic. I would not put Charts 2 and 3 beside it in the same short report unless the report specifically discusses seasonality: Chart 2 is detailed and visually busy, while Chart 3 repeats the seasonal story in a more focused, normalized form. Use Chart 2 for a technical seasonal comparison and Chart 3 when the main question is which months are unusually busy.

## Written question: Is the seasonal swing growing, or is the airline growing?

The absolute peak-to-trough swing grew from 44.0 in 1949 to 232.0 in 1960, while the annual mean also rose substantially. That alone cannot tell us whether seasonality itself became stronger: a larger airline naturally has a larger absolute seasonal swing. Compare **relative seasonality** by dividing each month's passengers by that year's average (or annual total) and plotting the normalized monthly index over time. The chart in Question 3 averages that index across years; to settle whether seasonality strengthens over time, the next chart would show the normalized index for each month-year, with one line per year or a year-by-month heatmap. If the peak-to-trough percentage gap increases, seasonality is strengthening; if it stays roughly similar, the larger absolute swing is mainly explained by overall growth.

The relative peak-to-trough swing was 34.7% of the annual mean in 1949 and 48.7% in 1960. This comparison is a useful first check, but the full normalized year-by-month chart is the stronger way to inspect the pattern across all years.

## Output files

- `01_passengers_over_time.png`
- `02_seasonal_cycle_by_year.png`
- `03_busiest_month_seasonal_index.png`
- `seasonal_summary_by_month.csv`
- `growth_and_seasonality_summary.csv`
- `missing_data_summary.csv`
- `flights.csv` and `task5.py`

## Run

Install dependencies with `pip install pandas numpy matplotlib`. Keep `flights.csv` beside `task5.py`, then run `python task5.py`.
