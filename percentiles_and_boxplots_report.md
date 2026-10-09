# RESULT REPORT - Percentiles and boxplots

**PAGE:** "Percentiles and boxplots" in the Streamlit app (sidebar navigation). Run: `streamlit run data_app_gestao.py`. Code: `boxplot_percentiles.py` (analysis) + `page_percentiles_and_boxplots` in `data_app_gestao.py` (UI). Only column names, counts, percentages and aggregates appear.

### 1. Percentile, median, quartiles (Q1, Q2, Q3), IQR
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** percentiles 1, 5, 10, 25, 50, 75, 90, 95, 99 for every numeric column; Q1, the median (Q2) and Q3 split the sorted rows in four equal groups; IQR = Q3 - Q1.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: p1 0.00, Q1 1,098, median 1,500, Q3 2,477, p99 52,275; IQR 1,379
  - `vendas_660.QUANTIDADE`: p1 1.00, Q1 1.00, median 2.00, Q3 3.00, p99 30.00; IQR 2.00
  - `carteira_pacientes.DIAS_ESTOQUE`: p1 10.00, Q1 60.00, median 90.00, Q3 150, p99 900; IQR 90.00
  - `painel.DIAS_SEM_VISITA_NUM`: p1 1.00, Q1 14.00, median 30.00, Q3 240, p99 896; IQR 226
  - `vendas_1015.PRODUTO_MG`: p1 50.00, Q1 100, median 100, Q3 200, p99 200; IQR 100
  - `vendas_1015.QTD`: p1 1.00, Q1 1.00, median 1.00, Q3 1.00, p99 2.54; IQR 0.00
  - `vendas_1015.VALOR_REPRESENTANTE`: p1 290, Q1 510, median 510, Q3 1,000, p99 2,000; IQR 490
  - `vendas_1015.VALOR_VENDA`: p1 1.00, Q1 690, median 690, Q3 1,365, p99 2,743; IQR 675
  - `vendas_1015.VALOR_COMISSAO`: p1 8.70, Q1 15.30, median 15.30, Q3 100, p99 200; IQR 84.70
- **WHAT IT MEANS FOR THE PROJECT:** A percentile is the value below which that share of rows falls. The median is the 50th percentile (Q2); Q1 and Q3 are the 25th and 75th; the IQR is the width of the middle half of the data.
- **PROBLEMS OR SURPRISES:**
  - `vendas_1015.QTD`: Q1 = Q3, the IQR is 0

### 2. Quartile calculation (position and interpolation)
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** for each column: the position of Q1, the median and Q3 in the sorted values ((n - 1) x p, counted from 0), the two neighbours, the fraction between them, and Q1 / Q3 under six methods (linear, lower, higher, midpoint, nearest, weibull).
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO` (n = 72,674): Q1 position 18,168.25 -> between values 1,098 and 1,098, fraction 0.25 -> Q1 1,098; the six methods differ by 0.00% of the IQR
  - `vendas_660.QUANTIDADE` (n = 72,674): Q1 position 18,168.25 -> between values 1.00 and 1.00, fraction 0.25 -> Q1 1.00; the six methods differ by 0.00% of the IQR
  - `carteira_pacientes.DIAS_ESTOQUE` (n = 44,144): Q1 position 11,035.75 -> between values 60.00 and 60.00, fraction 0.75 -> Q1 60.00; the six methods differ by 0.00% of the IQR
  - `painel.DIAS_SEM_VISITA_NUM` (n = 5,399): Q1 position 1,349.50 -> between values 14.00 and 14.00, fraction 0.50 -> Q1 14.00; the six methods differ by 0.00% of the IQR
  - `vendas_1015.PRODUTO_MG` (n = 347): Q1 position 86.50 -> between values 100 and 100, fraction 0.50 -> Q1 100; the six methods differ by 0.00% of the IQR
  - `vendas_1015.QTD` (n = 347): Q1 position 86.50 -> between values 1.00 and 1.00, fraction 0.50 -> Q1 1.00; the six methods differ by nan% of the IQR
  - `vendas_1015.VALOR_REPRESENTANTE` (n = 347): Q1 position 86.50 -> between values 510 and 510, fraction 0.50 -> Q1 510; the six methods differ by 0.00% of the IQR
  - `vendas_1015.VALOR_VENDA` (n = 347): Q1 position 86.50 -> between values 690 and 690, fraction 0.50 -> Q1 690; the six methods differ by 0.00% of the IQR
  - `vendas_1015.VALOR_COMISSAO` (n = 347): Q1 position 86.50 -> between values 15.30 and 15.30, fraction 0.50 -> Q1 15.30; the six methods differ by 0.00% of the IQR
  - groups of 10 rows or fewer: the six methods differ by up to 90% of the IQR
- **WHAT IT MEANS FOR THE PROJECT:** pandas and numpy interpolate linearly by default: position (n - 1) x p, then a weighted average of the two neighbouring sorted values. For large n every method gives almost the same quartile; for small groups they differ.
- **PROBLEMS OR SURPRISES:**
  - none found by these rules

### 3. Boxplot (box, median line), whisker and cap, fences and the 1.5 x IQR rule
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** box = Q1 to Q3 with the median line; fences = Q1 - 1.5 x IQR and Q3 + 1.5 x IQR; each whisker ends (cap) at the most extreme value still inside its fence; values outside are drawn as points.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: box 1,098 to 2,477, median 1,500 (29% up the box), fences -970 / 4,545, whiskers 0.00 / 4,538, mean above the box
  - `vendas_660.QUANTIDADE`: box 1.00 to 3.00, median 2.00 (50% up the box), fences -2.00 / 6.00, whiskers 1.00 / 6.00, mean above the box
  - `carteira_pacientes.DIAS_ESTOQUE`: box 60.00 to 150, median 90.00 (33% up the box), fences -75.00 / 285, whiskers 1.00 / 280, mean inside the box
  - `painel.DIAS_SEM_VISITA_NUM`: box 14.00 to 240, median 30.00 (7% up the box), fences -326 / 580, whiskers 1.00 / 568, mean inside the box
  - `vendas_1015.PRODUTO_MG`: box 100 to 200, median 100 (0% up the box), fences -50.00 / 350, whiskers 50.00 / 200, mean inside the box
  - `vendas_1015.QTD`: box 1.00 to 1.00, median 1.00 (nan% up the box), fences 1.00 / 1.00, whiskers 1.00 / 1.00, mean above the box
  - `vendas_1015.VALOR_REPRESENTANTE`: box 510 to 1,000, median 510 (0% up the box), fences -225 / 1,735, whiskers 290 / 1,530, mean inside the box
  - `vendas_1015.VALOR_VENDA`: box 690 to 1,365, median 690 (0% up the box), fences -322 / 2,378, whiskers 1.00 / 2,070, mean inside the box
  - `vendas_1015.VALOR_COMISSAO`: box 15.30 to 100, median 15.30 (0% up the box), fences -112 / 227, whiskers 8.70 / 200, mean inside the box
- **WHAT IT MEANS FOR THE PROJECT:** A boxplot draws five numbers and the outliers. Off-centre median lines and long whiskers show skew; the whisker is not the maximum.
- **PROBLEMS OR SURPRISES:**
  - `vendas_660.FATURAMENTO`: the maximum (1,259,522) is 277.5 times the upper whisker
  - `vendas_660.QUANTIDADE`: the maximum (3,001) is 500.2 times the upper whisker
  - `carteira_pacientes.DIAS_ESTOQUE`: the maximum (9,000) is 32.1 times the upper whisker
  - `vendas_1015.QTD`: the maximum (40.00) is 40.0 times the upper whisker
  - `vendas_1015.VALOR_REPRESENTANTE`: the maximum (40,000) is 26.1 times the upper whisker
  - `vendas_1015.VALOR_VENDA`: the maximum (55,600) is 26.9 times the upper whisker
  - `vendas_1015.VALOR_COMISSAO`: the maximum (4,000) is 20.0 times the upper whisker

### 4. Outlier and robust (mean vs. median / IQR)
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** outliers = values beyond the 1.5 x IQR fences (and beyond 3 x IQR as 'far out'); the position of the mean relative to the box.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: 14.4% outside the fences (0.0% low, 14.4% high), 10.4% beyond 3 x IQR; mean above the box
  - `vendas_660.QUANTIDADE`: 6.6% outside the fences (0.0% low, 6.6% high), 5.0% beyond 3 x IQR; mean above the box
  - `carteira_pacientes.DIAS_ESTOQUE`: 10.2% outside the fences (0.0% low, 10.2% high), 5.1% beyond 3 x IQR; mean inside the box
  - `painel.DIAS_SEM_VISITA_NUM`: 11.6% outside the fences (0.0% low, 11.6% high), 0.2% beyond 3 x IQR; mean inside the box
  - `vendas_1015.PRODUTO_MG`: 0.0% outside the fences (0.0% low, 0.0% high), 0.0% beyond 3 x IQR; mean inside the box
  - `vendas_1015.QTD`: 5.5% outside the fences (0.0% low, 5.5% high), 5.5% beyond 3 x IQR; mean above the box
  - `vendas_1015.VALOR_REPRESENTANTE`: 1.4% outside the fences (0.0% low, 1.4% high), 0.9% beyond 3 x IQR; mean inside the box
  - `vendas_1015.VALOR_VENDA`: 1.4% outside the fences (0.0% low, 1.4% high), 0.9% beyond 3 x IQR; mean inside the box
  - `vendas_1015.VALOR_COMISSAO`: 0.9% outside the fences (0.0% low, 0.9% high), 0.9% beyond 3 x IQR; mean inside the box
- **WHAT IT MEANS FOR THE PROJECT:** Outliers are values far from the rest; they may be errors or real extremes. Robust summaries (median, IQR) ignore them, the mean does not - when the mean is outside the box, the difference is large.
- **PROBLEMS OR SURPRISES:**
  - 3 of 9 columns have the mean above the box

### 5. Comparing groups with boxplots
- **WHERE:** vendas_1015, vendas_660
- **WHAT I RAN:** a boxplot of the first outcome measure for each level of up to two non-personal categorical columns (2 to 12 levels) per table; whether the boxes overlap; whether groups rank the same by mean and by median.
- **WHAT IT SHOWED:**
  - `vendas_660`: `FATURAMENTO` by `TIPO_REGISTRO` (4 groups, 72,674 rows, group sizes 15 to 70581): boxes overlap in 50% of pairs; highest median / lowest median = nan; rank correlation mean vs median 1.00; top group by mean `VENDA`, by median `VENDA`
  - `vendas_660`: `FATURAMENTO` by `TIPO_PAGAMENTO` (3 groups, 72,674 rows, group sizes 7231 to 54875): boxes overlap in 100% of pairs; highest median / lowest median = 3.8; rank correlation mean vs median 1.00; top group by mean `JUDICIAL`, by median `JUDICIAL`
  - `vendas_660`: `QUANTIDADE` by `TIPO_REGISTRO` (4 groups, 72,674 rows, group sizes 15 to 70581): boxes overlap in 100% of pairs; highest median / lowest median = 3.0; rank correlation mean vs median 0.63; top group by mean `ORCAMENTO`, by median `ORCAMENTO`
  - `vendas_660`: `QUANTIDADE` by `TIPO_PAGAMENTO` (3 groups, 72,674 rows, group sizes 7231 to 54875): boxes overlap in 100% of pairs; highest median / lowest median = 1.5; rank correlation mean vs median 0.87; top group by mean `JUDICIAL`, by median `JUDICIAL`
  - `vendas_1015`: `QTD` by `CANAL` (4 groups, 347 rows, group sizes 7 to 228): boxes overlap in 100% of pairs; highest median / lowest median = 1.0; rank correlation mean vs median nan; top group by mean `REMEDIO_JA`, by median `REMEDIO_JA`
  - `vendas_1015`: `QTD` by `PRODUTO` (3 groups, 347 rows, group sizes 48 to 198): boxes overlap in 100% of pairs; highest median / lowest median = 1.0; rank correlation mean vs median nan; top group by mean `Isolate Product 002`, by median `Isolate Product 036`
  - `vendas_1015`: `VALOR_REPRESENTANTE` by `CANAL` (4 groups, 347 rows, group sizes 7 to 228): boxes overlap in 100% of pairs; highest median / lowest median = 2.0; rank correlation mean vs median 0.77; top group by mean `REMEDIO_JA`, by median `REMEDIO_JA`
  - `vendas_1015`: `VALOR_REPRESENTANTE` by `PRODUTO` (3 groups, 347 rows, group sizes 48 to 198): boxes overlap in 0% of pairs; highest median / lowest median = 3.4; rank correlation mean vs median 1.00; top group by mean `Isolate Product 002`, by median `Isolate Product 002`
  - `vendas_1015`: `VALOR_VENDA` by `CANAL` (4 groups, 347 rows, group sizes 7 to 228): boxes overlap in 83% of pairs; highest median / lowest median = 3.5; rank correlation mean vs median 0.95; top group by mean `REMEDIO_JA`, by median `REMEDIO_JA`
  - `vendas_1015`: `VALOR_VENDA` by `PRODUTO` (3 groups, 347 rows, group sizes 48 to 198): boxes overlap in 0% of pairs; highest median / lowest median = 3.5; rank correlation mean vs median 1.00; top group by mean `Isolate Product 002`, by median `Isolate Product 002`
  - `vendas_1015`: `VALOR_COMISSAO` by `CANAL` (4 groups, 347 rows, group sizes 7 to 228): boxes overlap in 67% of pairs; highest median / lowest median = 6.5; rank correlation mean vs median 0.77; top group by mean `REMEDIO_JA`, by median `REMEDIO_JA`
  - `vendas_1015`: `VALOR_COMISSAO` by `PRODUTO` (3 groups, 347 rows, group sizes 48 to 198): boxes overlap in 0% of pairs; highest median / lowest median = 11.5; rank correlation mean vs median 1.00; top group by mean `Isolate Product 002`, by median `Isolate Product 002`
- **WHAT IT MEANS FOR THE PROJECT:** Putting boxes side by side compares the whole distributions: centre (median line), spread (box) and extremes (whiskers). Overlapping boxes mean differences of medians are small next to the natural spread.
- **PROBLEMS OR SURPRISES:**
  - `vendas_1015` `QTD` by `PRODUTO`: top group differs by mean (`Isolate Product 002`) and by median (`Isolate Product 036`)

### 6. The project's own Tukey fence
- **WHERE:** tables with a binary column named like a suspicion / outlier flag
- **WHAT I RAN:** for each such flag, the upper 1.5 x IQR fence of each numeric column within each category (groups of 30+ rows), compared with the flag (precision, recall).
- **WHAT IT SHOWED:**
  - `carteira_pacientes.POSOLOGIA_SUSPEITA` vs upper fence of `DIAS_ESTOQUE` per `PRODUTO`: flagged 9.5%, above fence 9.5%, both 9.5% (precision 100%, recall 100%)
- **WHAT IT MEANS FOR THE PROJECT:** The README says the churn page excludes patients flagged by a single upper Tukey fence computed upstream per product. This checks whether the stored tables contain the quantity it was computed from.
- **PROBLEMS OR SURPRISES:**
  - none found by these rules

## TOP INSIGHTS

1. **A boxplot shows skew before any statistic does: the mean falls outside the box** - In 3 of 9 numeric columns the mean sits above Q3, outside the box. `vendas_660.FATURAMENTO` has Q1 1,098, median 1,500, Q3 2,477 but mean 4,254. The median line in `painel.DIAS_SEM_VISITA_NUM` sits 7% of the way up its box (50% would be symmetric). Risk: A summary built on the mean describes a value that most rows do not reach. Fix: Look at the boxplot first; if the median line is off-centre or the mean is outside the box, report the median and the IQR.
2. **The 1.5 x IQR fences flag many rows, and 'outlier' does not mean 'error'** - For `vendas_660.FATURAMENTO` the fences are -970 and 4,545; 14.4% of its values fall outside, 10.4% even beyond the stricter 3 x IQR fences. Across all columns the share outside the 1.5 fences runs from 0.0% to 14.4%. Risk: Deleting every flagged row would remove legitimate large orders along with the typos. Fix: Treat the fences as a prompt to inspect, then decide: correct, keep, or analyse separately.
3. **Whiskers are not the minimum and maximum** - In `vendas_660.QUANTIDADE` the upper whisker ends at 6.00 (the largest value inside the fence) while the maximum is 3,001: the whisker reaches 0.20% of it. The values beyond are drawn as separate points. Risk: Reading the whisker as the range understates how far the data really go. Fix: State which whisker rule a chart uses (Tukey 1.5 x IQR here; others use min/max or the 5th and 95th percentiles).
4. **Quartile calculation: the method matters only for small groups** - For the full columns the six quartile methods differ by at most 0.00% of the IQR, but for groups of 10 rows or fewer they differ by up to 90% of the IQR (`vendas_1015.VALOR_COMISSAO` by `CANAL`, group of 7 rows). Q1 sits at position (n - 1) x 0.25 in the sorted values; when that is not a whole number, Q1 is interpolated between two neighbours. Risk: Two tools (pandas, Excel, R) can print different quartiles for the same small group. Fix: State the method (pandas and numpy use linear interpolation by default) and avoid quartiles for groups of a handful of rows.
5. **Comparing groups: overlapping boxes mean the groups are not clearly different** - Comparing `FATURAMENTO` in `vendas_660` by `TIPO_PAGAMENTO` (3 groups), 100% of the pairs of boxes overlap; the highest median is 3.8 times the lowest. Over all 12 comparisons, boxes overlap in 67% of the pairs on average. Risk: Reading a difference of medians without the boxes can make normal variation look like a real effect. Fix: Compare groups with their boxes (spread) and group sizes, not with a single number each.
6. **Robust ranking: groups ordered by mean and by median can disagree** - For `QUANTIDADE` in `vendas_660` by `TIPO_REGISTRO`, the rank correlation between the group means and the group medians is only 0.63; the top group is `ORCAMENTO` by mean and `ORCAMENTO` by median. The top group differs in 1 of 12 comparisons. Risk: 'Best group' depends on the estimate, so a ranking can change with one outlier. Fix: Rank by a robust estimate (median) and show the boxes next to it.
7. **The project already uses a Tukey fence upstream: does it match?** - The flag `carteira_pacientes.POSOLOGIA_SUSPEITA` (9.5% of rows) closely matches an upper 1.5 x IQR fence of `DIAS_ESTOQUE` computed per `PRODUTO` (above the fence: 9.5% of rows; both: 9.5%; precision 100%, recall 100%). Risk: If the flag is built from another quantity (the README says posologia), its fences cannot be checked from these tables. Fix: Document which column and which grouping each flag uses, so the fence can be audited.
8. **A zero IQR collapses the box** - 1 column(s) have Q1 = Q3 (for example `vendas_1015.QTD`, both 1.00), so the box is a line and the fences sit at the same value: every different value (5.5% here) is an outlier. Risk: A boxplot of a count column with many ties looks like an error and the 1.5 x IQR rule flags valid counts. Fix: For tied or count data show percentiles, a histogram or a bar chart of the counts instead.
