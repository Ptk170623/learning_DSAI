# RESULT REPORT - Estimates of location

**PAGE:** "Estimates of location" in the Streamlit app (sidebar navigation). Run: `streamlit run data_app_gestao.py`. Code: `location_estimates.py` (analysis) + `page_estimates_of_location` in `data_app_gestao.py` (UI). Only column names, counts, percentages and aggregates appear.

### 1. Estimate of location, sample, estimate
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** 400 random samples of up to 200 rows per numeric column; for each, the sample mean and median.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: full-data mean 4,254, median 1,500; across samples the mean varies by 24.8% and the median by 7.4% (std as % of the full-data value)
  - `vendas_660.QUANTIDADE`: full-data mean 3.39, median 2.00; across samples the mean varies by 52.5% and the median by 0.0% (std as % of the full-data value)
  - `carteira_pacientes.DIAS_ESTOQUE`: full-data mean 135, median 90.00; across samples the mean varies by 9.1% and the median by 3.9% (std as % of the full-data value)
  - `painel.DIAS_SEM_VISITA_NUM`: full-data mean 170, median 30.00; across samples the mean varies by 11.3% and the median by 12.7% (std as % of the full-data value)
  - `vendas_1015.PRODUTO_MG`: full-data mean 122, median 100; across samples the mean varies by 5.4% and the median by 0.0% (std as % of the full-data value)
  - `vendas_1015.QTD`: full-data mean 1.20, median 1.00; across samples the mean varies by 21.0% and the median by 0.0% (std as % of the full-data value)
  - `vendas_1015.VALOR_REPRESENTANTE`: full-data mean 802, median 510; across samples the mean varies by 33.3% and the median by 0.0% (std as % of the full-data value)
  - `vendas_1015.VALOR_VENDA`: full-data mean 993, median 690; across samples the mean varies by 36.3% and the median by 0.0% (std as % of the full-data value)
  - `vendas_1015.VALOR_COMISSAO`: full-data mean 55.74, median 15.30; across samples the mean varies by 50.1% and the median by 0.0% (std as % of the full-data value)
- **WHAT IT MEANS FOR THE PROJECT:** An estimate of location is one number that stands for a column's centre. A different sample gives a different estimate, so every estimate carries uncertainty. The tables here hold the data the project has; treating them as a sample of the business means any figure is an estimate.
- **PROBLEMS OR SURPRISES:**
  - `vendas_660.FATURAMENTO`: the sample mean varies 3.4x more than the sample median
  - `carteira_pacientes.DIAS_ESTOQUE`: the sample mean varies 2.3x more than the sample median
  - `vendas_1015.VALOR_COMISSAO`: the sample mean varies 2157784950312634.5x more than the sample median

### 2. Mean, median, trimmed mean
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** mean, median and 10% trimmed mean (drop the lowest and highest 10%), plus skew, for every numeric column.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO` (continuous, n=72,674): mean 4,254, median 1,500, trimmed mean 1,921, mean vs median +184%, skew 23.5
  - `vendas_660.QUANTIDADE` (discrete, n=72,674): mean 3.39, median 2.00, trimmed mean 2.06, mean vs median +70%, skew 111.7
  - `carteira_pacientes.DIAS_ESTOQUE` (continuous, n=44,144): mean 135, median 90.00, trimmed mean 103, mean vs median +50%, skew 13.6
  - `painel.DIAS_SEM_VISITA_NUM` (discrete, n=5,399): mean 170, median 30.00, trimmed mean 111, mean vs median +467%, skew 1.7
  - `vendas_1015.PRODUTO_MG` (discrete, n=347): mean 122, median 100, trimmed mean 122, mean vs median +22%, skew 0.5
  - `vendas_1015.QTD` (discrete, n=347): mean 1.20, median 1.00, trimmed mean 1.00, mean vs median +20%, skew 16.5
  - `vendas_1015.VALOR_REPRESENTANTE` (continuous, n=347): mean 802, median 510, trimmed mean 638, mean vs median +57%, skew 16.3
  - `vendas_1015.VALOR_VENDA` (continuous, n=347): mean 993, median 690, trimmed mean 784, mean vs median +44%, skew 16.1
  - `vendas_1015.VALOR_COMISSAO` (continuous, n=347): mean 55.74, median 15.30, trimmed mean 36.01, mean vs median +264%, skew 15.8
- **WHAT IT MEANS FOR THE PROJECT:** The three estimates answer slightly different questions: the mean is the total shared equally, the median is the middle row, the trimmed mean is an average that ignores the extremes.
- **PROBLEMS OR SURPRISES:**
  - `vendas_660.FATURAMENTO`: mean is +184% from the median
  - `vendas_660.QUANTIDADE`: mean is +70% from the median
  - `carteira_pacientes.DIAS_ESTOQUE`: mean is +50% from the median
  - `painel.DIAS_SEM_VISITA_NUM`: mean is +467% from the median
  - `vendas_1015.PRODUTO_MG`: mean is +22% from the median
  - `vendas_1015.QTD`: mean is +20% from the median
  - `vendas_1015.VALOR_REPRESENTANTE`: mean is +57% from the median
  - `vendas_1015.VALOR_VENDA`: mean is +44% from the median
  - `vendas_1015.VALOR_COMISSAO`: mean is +264% from the median

### 3. Outlier and robust
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** Tukey fences (1.5 x IQR); recompute mean and median without the outliers and compare how far each moved.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: 14.4% outliers (max = 840 x median); without them the mean moves -64% and the median -7.3%
  - `vendas_660.QUANTIDADE`: 6.6% outliers (max = 1,500 x median); without them the mean moves -39% and the median +0.0%
  - `carteira_pacientes.DIAS_ESTOQUE`: 10.2% outliers (max = 100 x median); without them the mean moves -30% and the median +0.0%
  - `painel.DIAS_SEM_VISITA_NUM`: 11.6% outliers (max = 31 x median); without them the mean moves -48% and the median -10.0%
  - `vendas_1015.PRODUTO_MG`: 0.0% outliers (max = 2 x median); without them the mean moves +0% and the median +0.0%
  - `vendas_1015.QTD`: 5.5% outliers (max = 40 x median); without them the mean moves -17% and the median +0.0%
  - `vendas_1015.VALOR_REPRESENTANTE`: 1.4% outliers (max = 78 x median); without them the mean moves -21% and the median +0.0%
  - `vendas_1015.VALOR_VENDA`: 1.4% outliers (max = 81 x median); without them the mean moves -23% and the median +0.0%
  - `vendas_1015.VALOR_COMISSAO`: 0.9% outliers (max = 261 x median); without them the mean moves -29% and the median +0.0%
- **WHAT IT MEANS FOR THE PROJECT:** An outlier is a value far from the rest. An estimate is robust when a few outliers barely move it: the median and the trimmed mean are robust, the mean is not.
- **PROBLEMS OR SURPRISES:**
  - `vendas_1015.QTD`: IQR is 0, the outlier rule is degenerate (5.5% flagged)

### 4. Weight, weighted mean, weighted median
- **WHERE:** vendas_1015, vendas_660
- **WHAT I RAN:** a unit value (money / quantity) averaged plainly and with the quantity as weight; group means averaged plainly and weighted by group size.
- **WHAT IT SHOWED:**
  - `vendas_660`: `FATURAMENTO` / `QUANTIDADE`: mean 1,175 vs weighted mean 1,254 (-6%); median 695 vs weighted median 979
  - `vendas_1015`: `VALOR_REPRESENTANTE` / `QTD`: mean 622 vs weighted mean 666 (-7%); median 510 vs weighted median 510
  - `vendas_1015`: `VALOR_VENDA` / `QTD`: mean 743 vs weighted mean 824 (-10%); median 690 vs weighted median 690
  - `vendas_1015`: `VALOR_COMISSAO` / `QTD`: mean 39.04 vs weighted mean 46.28 (-16%); median 15.30 vs weighted median 15.30
  - `vendas_660`: mean of 68 `NOME_BLOCO` means of `FATURAMENTO` = 4,248 vs overall mean 3,537 (+20%); weighted by group size = 3,537
  - `vendas_1015`: mean of 27 `BLOCO` means of `VALOR_REPRESENTANTE` = 1,067 vs overall mean 693 (+54%); weighted by group size = 693
- **WHAT IT MEANS FOR THE PROJECT:** A weight says how much each value counts. The weighted mean of a unit value is total value / total quantity, which reconciles with the accounting totals; the plain mean does not.
- **PROBLEMS OR SURPRISES:**
  - `vendas_1015`: the plain mean of `VALOR_COMISSAO` / `QTD` is -16% from the weighted one

### 5. Mean versus median: when to use each
- **WHERE:** 4 tables, 9 numeric columns; the 660 Analysis benchmark
- **WHAT I RAN:** a rule per column (median or trimmed mean when skew > 1 or 1%+ outliers, otherwise the mean) and a Mean-vs-Median run of the app's own 660 benchmark (transform.calculate_table_660, block = all) over the last 12 complete months.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: median (or trimmed mean) (skew 23.5, 14.4% outliers)
  - `vendas_660.QUANTIDADE`: median (or trimmed mean) (skew 111.7, 6.6% outliers)
  - `carteira_pacientes.DIAS_ESTOQUE`: median (or trimmed mean) (skew 13.6, 10.2% outliers)
  - `painel.DIAS_SEM_VISITA_NUM`: median (or trimmed mean) (skew 1.7, 11.6% outliers)
  - `vendas_1015.PRODUTO_MG`: mean is fine (skew 0.5, 0.0% outliers)
  - `vendas_1015.QTD`: median (or trimmed mean) (skew 16.5, 5.5% outliers)
  - `vendas_1015.VALOR_REPRESENTANTE`: median (or trimmed mean) (skew 16.3, 1.4% outliers)
  - `vendas_1015.VALOR_VENDA`: median (or trimmed mean) (skew 16.1, 1.4% outliers)
  - `vendas_1015.VALOR_COMISSAO`: median (or trimmed mean) (skew 15.8, 0.9% outliers)
  - Quarter / Revenue (R$): classification changes in 3 of 12 months; benchmark differs by 5.5% on average
  - Quarter / Order Count: classification changes in 5 of 12 months; benchmark differs by 4.5% on average
  - Quarter / Units: classification changes in 2 of 12 months; benchmark differs by 2.3% on average
  - Quarter / New Patients: classification changes in 1 of 12 months; benchmark differs by 2.8% on average
  - Semester / Revenue (R$): classification changes in 1 of 12 months; benchmark differs by 2.9% on average
  - Semester / Order Count: classification changes in 2 of 12 months; benchmark differs by 3.3% on average
  - Semester / Units: classification changes in 0 of 12 months; benchmark differs by 1.1% on average
  - Semester / New Patients: classification changes in 1 of 12 months; benchmark differs by 1.8% on average
  - Year / Revenue (R$): classification changes in 0 of 12 months; benchmark differs by 1.8% on average
  - Year / Order Count: classification changes in 2 of 12 months; benchmark differs by 1.6% on average
  - Year / Units: classification changes in 1 of 12 months; benchmark differs by 0.7% on average
  - Year / New Patients: classification changes in 3 of 12 months; benchmark differs by 2.4% on average
  - Last 3 Years / Revenue (R$): classification changes in 3 of 12 months; benchmark differs by 2.0% on average
  - Last 3 Years / Order Count: classification changes in 3 of 12 months; benchmark differs by 4.3% on average
  - Last 3 Years / Units: classification changes in 4 of 12 months; benchmark differs by 4.0% on average
  - Last 3 Years / New Patients: classification changes in 1 of 12 months; benchmark differs by 1.7% on average
  - Historical / Revenue (R$): classification changes in 4 of 12 months; benchmark differs by 14.7% on average
  - Historical / Order Count: classification changes in 0 of 12 months; benchmark differs by 23.1% on average
  - Historical / Units: classification changes in 0 of 12 months; benchmark differs by 6.5% on average
  - Historical / New Patients: classification changes in 2 of 12 months; benchmark differs by 26.1% on average
- **WHAT IT MEANS FOR THE PROJECT:** Use the median (or a trimmed mean) to describe a typical row or to build a benchmark when data are skewed or have outliers. Use the mean when you need a total (mean x n = total) or the data are symmetric.
- **PROBLEMS OR SURPRISES:**
  - 38 of 240 month x window x metric checks change classification between Mean and Median
  - the latest month is partial and was left out of the app comparison

## TOP INSIGHTS

1. **Mean and median disagree a lot: the typical row is not the average row** - 9 of 9 numeric columns have a mean at least 20% away from their median. The widest: `painel.DIAS_SEM_VISITA_NUM` has median 30.00 but mean 170 (+467%), skew 1.7. Risk: Reporting the mean as 'the typical value' describes a row that almost nobody has. Fix: Say which question you answer: the median for a typical row, the mean for a total (mean x rows = total).
2. **Outliers move the mean far more than the median (robustness)** - Removing the Tukey outliers (14.4% of the values) moves the mean of `vendas_660.FATURAMENTO` by -64% but its median by only -7.3%. Its maximum is 840 times the median. Risk: One typo or one huge order changes the mean, so a benchmark or KPI built on it jumps for no business reason. Fix: Use a robust estimate (median or trimmed mean) for benchmarks, and inspect the largest rows before trusting any mean.
3. **An estimate from a sample is itself uncertain** - Drawing 400 random samples of 200 rows from `vendas_660.FATURAMENTO`, the sample mean ranges 2,940 to 6,129 (90% of draws) around the full-data 4,254, while the sample median stays between 1,390 and 1,690 around 1,500. Risk: With skewed data a small sample gives a mean that changes a lot from sample to sample, so two analysts get different answers. Fix: Report the estimate with its spread (a range or a bootstrap interval) and prefer the estimator that varies less.
4. **Weight: the plain average of a unit value ignores how much was sold** - In `vendas_660`, the average of `FATURAMENTO` / `QUANTIDADE` per row is 1,175, but weighting each row by `QUANTIDADE` gives 1,254 (-6%); the weighted mean equals total `FATURAMENTO` / total `QUANTIDADE` (1,254). The weighted median is 979 against a plain median of 695. Risk: A one-unit sale counts as much as a thousand-unit sale, so the 'average price' matches no real total. Fix: Weight by the quantity (np.average(..., weights=...)) whenever rows represent different amounts.
5. **Averaging averages treats a small group like a big one** - In `vendas_660`, the mean of the 68 `NOME_BLOCO` means of `FATURAMENTO` is 4,248, but the overall mean is 3,537 (+20%). Groups range from 1 to 7,372 rows. Risk: Each group counts once whatever its size, so tiny groups pull the 'overall' figure as much as the biggest ones. Fix: Weight group means by group size (the weighted mean of group means is the overall mean), or report both.
6. **The app's Mean / Median switch changes the benchmark and sometimes the verdict** - Over the last 12 complete months (10/2025 to 09/2026), switching 'Summary Measure' from Mean to Median changes the classification in 38 of 240 month x window x metric checks (16%). Worst case: Order Count, Quarter window, 42% of months. The benchmark itself differs by 26% on average for New Patients (Historical). Risk: The same month can read NEUTRAL under one measure and ABOVE under the other, so the verdict depends on a switch people may not notice. Fix: Pick the measure per question (median for 'normal', mean for 'total') and show which one a classification used.
7. **Count columns with a zero IQR make outlier rules degenerate** - 1 numeric column(s) have an interquartile range of 0 (e.g. `vendas_1015.QTD`, median 1.00), so the Tukey fence flags every different value as an outlier (5.5% here). Risk: An automatic outlier filter can delete legitimate larger counts. Fix: For such columns use a percentile cap (for example the 99th) or a trimmed mean instead of the 1.5 x IQR rule.
