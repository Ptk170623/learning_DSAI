# Part C - Estimates of location

**Status:** concepts mapped; not learned yet with the chat-based method.

**Books:** Practical Statistics for Data Scientists, Ch.1 'Estimates of Location', pp.7-13. Morettin & Bussab, Ch.3 §3.1 'Medidas de Posição', p.35, and §3.3, p.43.

## Concept map and where each concept shows up in the project

| # | Concept | In the project | Understood on |
|---|---|---|---|
| 1 | Estimate of location | Each 660 benchmark is one number that stands for the typical value of a metric over a window of past months. | |
| 2 | Sample | The window of past months used for a benchmark is the sample of history behind it. | |
| 3 | Estimate | The benchmark is an estimate computed from that window; the current month is judged against it. | |
| 4 | Outlier | Not applied yet to the app's own metrics. | |
| 5 | Robust | The Summary Measure option 'Median' is the robust choice for the benchmark. | |
| 6 | Mean | Summary Measure 'Mean' (`transform.py`: `values.mean()`). | |
| 7 | Trimmed mean | Not applied yet. | |
| 8 | Median | Summary Measure 'Median' (`transform.py`: `values.median()`). | |
| 9 | Weight | Not applied yet. | |
| 10 | Weighted mean | Not applied yet. | |
| 11 | Weighted median | Not applied yet. | |
| 12 | Mean vs median: when to use each | The Mean / Median switch of the 660 pages is exactly this choice: it can change how a month is classified. | |

## Reviews

Reviews are set once the part is understood: 1 day, 7 days and 30 days after. Fill in the dates as they are scheduled and when they are done.

| # | Scheduled for | Done on | Notes |
|---|---|---|---|
| 1 (1 day) | | | |
| 2 (7 days) | | | |
| 3 (30 days) | | | |

## Still unclear

-

## Applied in the project (decided with the teacher)

-
