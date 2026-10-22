# Week 4 Part C — Part-to-whole legality and ranking

## 1. Legality checks

### `case08_channel_attrib.csv` — four `touch_*` columns
**Verdict: bar chart, not pie.** The channel flags are not mutually exclusive: one customer can touch multiple channels. The rates are channel touch rates rather than exclusive shares of a single whole, so the first and third tests fail for a pie even if the denominator (all customers) is meaningful.

### `shares_eight.csv` — eight categories
**Verdict: pie is legal, if the question is category composition.** The eight listed percentages sum to 100.0%. The categories are presented as exclusive parts of that whole, and share is the question. A sorted horizontal bar chart is also legal and makes precise ranking easier.

### `case09_premium_share.csv` — premium vs other revenue, 2025Q4
**Verdict: pie or bar chart.** Premium revenue is PKR 228m and other revenue PKR 372m, giving 38% and 62% of PKR 600m total. The categories are complementary and sum to the whole.

## 2–3. Reader ranking
The pie and bar stimuli and a blank results CSV are supplied. **Reader results are intentionally blank** until one real reader completes both tasks. Do not report response times or error counts until those measurements are entered.

True order, largest first:
A (24.6%) > B (18.4%) > C (15.0%) > H (13.1%) > G (11.2%) > D (9.2%) > E (6.1%) > F (2.4%).

After recording the reader's two orders, run `python score_results.py`. It reports wrong letter positions for each stimulus.

A sample of one can describe that reader's performance in these two tasks, but cannot establish a general claim about all readers or prove the deck's prediction.

## 4. Rule
Draw a pie only when parts are mutually exclusive, form a meaningful whole, and the question is specifically about their shares; otherwise use a bar chart or another appropriate display.
