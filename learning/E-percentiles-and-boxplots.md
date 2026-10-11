# Part E - Percentiles and boxplots

**Status:** concepts mapped; not learned yet with the chat-based method.

**Books:** Practical Statistics for Data Scientists, Ch.1 'Estimates Based on Percentiles' and box 'Percentile: Precise Definition', pp.16-17; 'Percentiles and Boxplots', pp.20-21; Key Ideas, p.26. Morettin & Bussab, Ch.3 §3.3, pp.41-43, and §3.4 'Box Plots', pp.47-50.

## Concept map and where each concept shows up in the project

| # | Concept | In the project | Understood on |
|---|---|---|---|
| 1 | Percentile | Not applied yet in the app's own code. | |
| 2 | Median | Summary Measure 'Median' (see Part C). | |
| 3 | Quartiles (Q1, Q2, Q3) | Used upstream by the churn flag (next rows). | |
| 4 | IQR (interquartile range) | Used upstream by the churn flag (next rows). | |
| 5 | Boxplot (box, median line) | Not applied yet. | |
| 6 | Whisker and cap | Not applied yet. | |
| 7 | Fences (lower and upper) and the 1.5 × IQR rule | `POSOLOGIA_SUSPEITA` is a single upper Tukey fence (Q3 + 1.5 × IQR) of days of stock computed per product; tested against the stored tables, the flag matched that fence on every product with enough rows (100% precision and recall). | |
| 8 | Outlier | Churns in the Month excludes the patients flagged by that fence (`calculate_churns_in_month`). | |
| 9 | Robust (mean vs. median/IQR) | Not applied yet. | |
| 10 | Comparing groups with boxplots | Not applied yet. | |
| 11 | Quartile calculation (position and interpolation) | Not applied yet. | |

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
