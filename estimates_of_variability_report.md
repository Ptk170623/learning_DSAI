# RESULT REPORT - Estimates of variability

**PAGE:** "Estimates of variability" in the Streamlit app (sidebar navigation). Run: `streamlit run data_app_gestao.py`. Code: `variability_estimates.py` (analysis) + `page_estimates_of_variability` in `data_app_gestao.py` (UI). Only column names, counts, percentages and aggregates appear.

### 1. Variability and deviation
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** for every numeric column: the deviation of each value from the mean (value - mean), its sum, the largest deviation in standard deviations, and the coefficient of variation (SD / mean, my addition to compare columns in different units).
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: mean 4,254, SD 15,003, CV 353%, deviations add up to 3e-08 (about zero), largest deviation = 84 SD
  - `vendas_660.QUANTIDADE`: mean 3.39, SD 18.79, CV 554%, deviations add up to -1.8e-11 (about zero), largest deviation = 160 SD
  - `carteira_pacientes.DIAS_ESTOQUE`: mean 135, SD 185, CV 137%, deviations add up to -9.3e-10 (about zero), largest deviation = 48 SD
  - `painel.DIAS_SEM_VISITA_NUM`: mean 170, SD 260, CV 153%, deviations add up to -1.1e-10 (about zero), largest deviation = 3 SD
  - `vendas_1015.PRODUTO_MG`: mean 122, SD 52.65, CV 43%, deviations add up to -1.8e-12 (about zero), largest deviation = 1 SD
  - `vendas_1015.QTD`: mean 1.20, SD 2.19, CV 182%, deviations add up to -3.6e-15 (about zero), largest deviation = 18 SD
  - `vendas_1015.VALOR_REPRESENTANTE`: mean 802, SD 2,226, CV 277%, deviations add up to -1.1e-11 (about zero), largest deviation = 18 SD
  - `vendas_1015.VALOR_VENDA`: mean 993, SD 3,112, CV 313%, deviations add up to -7.3e-12 (about zero), largest deviation = 18 SD
  - `vendas_1015.VALOR_COMISSAO`: mean 55.74, SD 226, CV 406%, deviations add up to 0 (about zero), largest deviation = 17 SD
- **WHAT IT MEANS FOR THE PROJECT:** Variability is how spread out the values are. A deviation is the distance of one value from the centre. Deviations around the mean always add up to zero, so we square them (variance, SD) or take their absolute value (mean absolute deviation).
- **PROBLEMS OR SURPRISES:**
  - `vendas_660.FATURAMENTO`: one value sits 84 standard deviations from the mean
  - `vendas_660.QUANTIDADE`: one value sits 160 standard deviations from the mean
  - `carteira_pacientes.DIAS_ESTOQUE`: one value sits 48 standard deviations from the mean

### 2. Variance, standard deviation, degrees of freedom (n - 1), bias
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** 20,000 random samples of 10 rows per column; the variance of each sample computed with n and with n - 1, averaged and compared with the full-data variance.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: variance 2.251e+08; mean estimate with n -19%, with n - 1 -10% (theory for n: -10%); SD from n - 1 is -53% off
  - `vendas_660.QUANTIDADE`: variance 352.9; mean estimate with n -21%, with n - 1 -13% (theory for n: -10%); SD from n - 1 is -77% off
  - `carteira_pacientes.DIAS_ESTOQUE`: variance 3.412e+04; mean estimate with n -8%, with n - 1 +3% (theory for n: -10%); SD from n - 1 is -30% off
  - `painel.DIAS_SEM_VISITA_NUM`: variance 6.744e+04; mean estimate with n -9%, with n - 1 +1% (theory for n: -10%); SD from n - 1 is -6% off
  - `vendas_1015.PRODUTO_MG`: variance 2,764; mean estimate with n -10%, with n - 1 -0% (theory for n: -10%); SD from n - 1 is -2% off
  - `vendas_1015.QTD`: variance 4.791; mean estimate with n -7%, with n - 1 +3% (theory for n: -10%); SD from n - 1 is -72% off
  - `vendas_1015.VALOR_REPRESENTANTE`: variance 4.941e+06; mean estimate with n -6%, with n - 1 +4% (theory for n: -10%); SD from n - 1 is -66% off
  - `vendas_1015.VALOR_VENDA`: variance 9.658e+06; mean estimate with n -7%, with n - 1 +4% (theory for n: -10%); SD from n - 1 is -64% off
  - `vendas_1015.VALOR_COMISSAO`: variance 5.104e+04; mean estimate with n -11%, with n - 1 -1% (theory for n: -10%); SD from n - 1 is -62% off
- **WHAT IT MEANS FOR THE PROJECT:** The sample variance divides by n - 1 (the degrees of freedom: one is used up by estimating the mean). Dividing by n makes small samples look less variable than the data are: that is bias. The standard deviation is the square root, in the original units.
- **PROBLEMS OR SURPRISES:**
  - `vendas_660.FATURAMENTO`: the estimates are noisy because the column is very skewed; more draws are needed to see the theory
  - `vendas_660.QUANTIDADE`: the estimates are noisy because the column is very skewed; more draws are needed to see the theory

### 3. Mean absolute deviation and MAD (median absolute deviation)
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** mean absolute deviation, MAD (median of |value - median|), the scaled MAD (x 1.4826, comparable with a SD) and the SD / scaled MAD ratio.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: SD 15,003, mean absolute deviation 4,641, MAD 542, scaled MAD 804, SD / scaled MAD = 18.7
  - `vendas_660.QUANTIDADE`: SD 18.79, mean absolute deviation 2.68, MAD 1.00, scaled MAD 1.48, SD / scaled MAD = 12.7
  - `carteira_pacientes.DIAS_ESTOQUE`: SD 185, mean absolute deviation 93.69, MAD 40.00, scaled MAD 59.30, SD / scaled MAD = 3.1
  - `painel.DIAS_SEM_VISITA_NUM`: SD 260, mean absolute deviation 203, MAD 23.00, scaled MAD 34.10, SD / scaled MAD = 7.6
  - `vendas_1015.PRODUTO_MG`: SD 52.65, mean absolute deviation 45.30, MAD 0.00, scaled MAD 0.00, SD / scaled MAD = nan
  - `vendas_1015.QTD`: SD 2.19, mean absolute deviation 0.39, MAD 0.00, scaled MAD 0.00, SD / scaled MAD = nan
  - `vendas_1015.VALOR_REPRESENTANTE`: SD 2,226, mean absolute deviation 452, MAD 0.00, scaled MAD 0.00, SD / scaled MAD = nan
  - `vendas_1015.VALOR_VENDA`: SD 3,112, mean absolute deviation 661, MAD 108, scaled MAD 160, SD / scaled MAD = 19.4
  - `vendas_1015.VALOR_COMISSAO`: SD 226, mean absolute deviation 58.04, MAD 0.00, scaled MAD 0.00, SD / scaled MAD = nan
- **WHAT IT MEANS FOR THE PROJECT:** The mean absolute deviation uses the mean, so outliers still pull it. The MAD uses medians twice and barely moves: it is the robust partner of the SD (book, chapter 1, 'Estimates of Variability').
- **PROBLEMS OR SURPRISES:**
  - `vendas_1015.PRODUTO_MG`: MAD is 0, more than half the rows share one value
  - `vendas_1015.QTD`: MAD is 0, more than half the rows share one value
  - `vendas_1015.VALOR_REPRESENTANTE`: MAD is 0, more than half the rows share one value
  - `vendas_1015.VALOR_COMISSAO`: MAD is 0, more than half the rows share one value

### 4. Range, order statistics, percentile, quartile, IQR
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** sorted values (order statistics): minimum, percentiles 1, 5, 25 (Q1), 50, 75 (Q3), 95, 99, maximum; the range and the IQR (Q3 - Q1).
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: min 0.00, Q1 1,098, median 1,500, Q3 2,477, p99 52,275, max 1,259,522; IQR 1,379, range = 913 x IQR
  - `vendas_660.QUANTIDADE`: min 1.00, Q1 1.00, median 2.00, Q3 3.00, p99 30.00, max 3,001; IQR 2.00, range = 1,500 x IQR
  - `carteira_pacientes.DIAS_ESTOQUE`: min 1.00, Q1 60.00, median 90.00, Q3 150, p99 900, max 9,000; IQR 90.00, range = 100 x IQR
  - `painel.DIAS_SEM_VISITA_NUM`: min 1.00, Q1 14.00, median 30.00, Q3 240, p99 896, max 941; IQR 226, range = 4 x IQR
  - `vendas_1015.PRODUTO_MG`: min 50.00, Q1 100, median 100, Q3 200, p99 200, max 200; IQR 100, range = 2 x IQR
  - `vendas_1015.QTD`: min 1.00, Q1 1.00, median 1.00, Q3 1.00, p99 2.54, max 40.00; IQR 0.00, range = nan x IQR
  - `vendas_1015.VALOR_REPRESENTANTE`: min 290, Q1 510, median 510, Q3 1,000, p99 2,000, max 40,000; IQR 490, range = 81 x IQR
  - `vendas_1015.VALOR_VENDA`: min 1.00, Q1 690, median 690, Q3 1,365, p99 2,743, max 55,600; IQR 675, range = 82 x IQR
  - `vendas_1015.VALOR_COMISSAO`: min 8.70, Q1 15.30, median 15.30, Q3 100, p99 200, max 4,000; IQR 84.70, range = 47 x IQR
- **WHAT IT MEANS FOR THE PROJECT:** Order statistics are the data sorted from smallest to largest. A percentile is the value below which that share of rows falls; quartiles split the data in four; the IQR is the width of the middle half. The range uses only the two extreme rows.
- **PROBLEMS OR SURPRISES:**
  - `vendas_660.FATURAMENTO`: the maximum is 24 times the 99th percentile
  - `vendas_660.QUANTIDADE`: the maximum is 100 times the 99th percentile
  - `carteira_pacientes.DIAS_ESTOQUE`: the maximum is 10 times the 99th percentile
  - `vendas_1015.QTD`: the maximum is 16 times the 99th percentile
  - `vendas_1015.VALOR_REPRESENTANTE`: the maximum is 20 times the 99th percentile
  - `vendas_1015.VALOR_VENDA`: the maximum is 20 times the 99th percentile
  - `vendas_1015.VALOR_COMISSAO`: the maximum is 20 times the 99th percentile

### 5. Robust and outlier
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** three outlier rules (more than 3 SD from the mean; 1.5 x IQR beyond the quartiles; MAD-based modified z-score above 3.5) and the change of SD, IQR and MAD after the Tukey outliers are removed.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: outliers by 3-SD rule 1.1%, Tukey 14.4%, MAD rule 15.6%; without the Tukey outliers SD -94%, IQR -28%, MAD -9%
  - `vendas_660.QUANTIDADE`: outliers by 3-SD rule 0.3%, Tukey 6.6%, MAD rule 6.3%; without the Tukey outliers SD -94%, IQR +0%, MAD +0%
  - `carteira_pacientes.DIAS_ESTOQUE`: outliers by 3-SD rule 1.4%, Tukey 10.2%, MAD rule 10.1%; without the Tukey outliers SD -69%, IQR -22%, MAD -25%
  - `painel.DIAS_SEM_VISITA_NUM`: outliers by 3-SD rule 0.0%, Tukey 11.6%, MAD rule 28.5%; without the Tukey outliers SD -48%, IQR -74%, MAD -17%
  - `vendas_1015.PRODUTO_MG`: outliers by 3-SD rule 0.0%, Tukey 0.0%, MAD rule 0.0%; without the Tukey outliers SD +0%, IQR +0%, MAD +nan%
  - `vendas_1015.QTD`: outliers by 3-SD rule 0.6%, Tukey 5.5%, MAD rule 0.0%; without the Tukey outliers SD -100%, IQR +nan%, MAD +nan%
  - `vendas_1015.VALOR_REPRESENTANTE`: outliers by 3-SD rule 0.6%, Tukey 1.4%, MAD rule 0.0%; without the Tukey outliers SD -88%, IQR +0%, MAD +nan%
  - `vendas_1015.VALOR_VENDA`: outliers by 3-SD rule 0.6%, Tukey 1.4%, MAD rule 37.2%; without the Tukey outliers SD -86%, IQR -2%, MAD -7%
  - `vendas_1015.VALOR_COMISSAO`: outliers by 3-SD rule 0.6%, Tukey 0.9%, MAD rule 0.0%; without the Tukey outliers SD -82%, IQR +0%, MAD +nan%
- **WHAT IT MEANS FOR THE PROJECT:** An estimate is robust when a few outliers barely move it: the IQR and the MAD are robust, the SD, the variance and the range are not.
- **PROBLEMS OR SURPRISES:**
  - `vendas_660.FATURAMENTO`: the 3-SD rule flags 1.1% but the Tukey rule 14.4% (masking)
  - `vendas_660.QUANTIDADE`: the 3-SD rule flags 0.3% but the Tukey rule 6.6% (masking)
  - `carteira_pacientes.DIAS_ESTOQUE`: the 3-SD rule flags 1.4% but the Tukey rule 10.2% (masking)
  - `painel.DIAS_SEM_VISITA_NUM`: the 3-SD rule flags 0.0% but the Tukey rule 11.6% (masking)
  - `vendas_1015.QTD`: the 3-SD rule flags 0.6% but the Tukey rule 5.5% (masking)

### 6. Deviation in the project: the 660 Analysis bands
- **WHERE:** vendas_660 monthly metrics; transform.calculate_table_660
- **WHAT I RAN:** the monthly series of each 660 metric (all blocks) over the last 24 complete months: SD, CV, scaled MAD, IQR against the median, and how the app's own function classified each month against the Year (mean) benchmark.
- **WHAT IT SHOWED:**
  - Revenue (R$): month-to-month CV 19%, robust spread 19% of the median, IQR 26% of the median; NEUTRAL in 42% of months, slightly above/below 42%, above/below/much 17%
  - Order Count: month-to-month CV 11%, robust spread 12% of the median, IQR 14% of the median; NEUTRAL in 67% of months, slightly above/below 29%, above/below/much 4%
  - Units: month-to-month CV 12%, robust spread 12% of the median, IQR 17% of the median; NEUTRAL in 46% of months, slightly above/below 54%, above/below/much 0%
  - New Patients: month-to-month CV 22%, robust spread 27% of the median, IQR 33% of the median; NEUTRAL in 21% of months, slightly above/below 67%, above/below/much 12%
- **WHAT IT MEANS FOR THE PROJECT:** The app calls a month NEUTRAL when its % deviation from the benchmark is within 10%, then 25%, 40%. Those bands are fixed; the real variability of each metric decides how often a normal month falls outside them.
- **PROBLEMS OR SURPRISES:**
  - Revenue (R$): only 42% of months are NEUTRAL
  - Units: only 46% of months are NEUTRAL
  - New Patients: only 21% of months are NEUTRAL

## TOP INSIGHTS

1. **The standard deviation and the MAD describe different spreads** - For `vendas_1015.VALOR_VENDA` the standard deviation is 3,112 but the scaled MAD (median absolute deviation) is only 160: the SD is 19.4 times larger. For a bell-shaped column the two would be about equal; 5 of the 5 columns with a non-zero MAD have an SD more than twice their MAD. Risk: Quoting only the SD describes the few huge values, not the spread of the typical row. Fix: Report a robust spread (MAD or IQR) next to the SD, and say which one you used.
2. **Outliers inflate the SD far more than the IQR (robustness)** - Removing the Tukey outliers (6.6% of the values) cuts the SD of `vendas_660.QUANTIDADE` by 94% but its IQR by only 0% and its MAD by 0%. Risk: One bad record changes the SD, so control limits and thresholds built on it move for no business reason. Fix: Use the IQR or the MAD for limits and benchmarks, and inspect the largest rows before trusting an SD.
3. **The 3-standard-deviation rule hides outliers (masking)** - In `vendas_660.FATURAMENTO` the rule 'more than 3 SD from the mean' flags 1.1% of the values, the Tukey rule (1.5 x IQR) flags 14.4% and the MAD-based modified z-score flags 15.6%. The outliers themselves inflate the SD, so they hide inside it. Risk: An automatic outlier filter based on the SD misses the very values it should catch. Fix: Prefer a rule built on robust spread (IQR or MAD) and review what each rule flags.
4. **Dividing by n underestimates the variance; n - 1 fixes it on average (bias)** - Drawing 20,000 samples of 10 rows from every column, the variance computed with n is on average -9% from the full-data variance (median across columns; theory says -10%), while n - 1 gives +1%. The n - 1 estimate is unbiased for the variance, but the SD (its square root) still comes out low (-62% median): a little from the square root, a lot from skew, because samples of 10 rows seldom contain the extreme values. Risk: A small sample always looks less variable than the data really are, so intervals and limits come out too tight. Fix: Use the sample variance (ddof=1, pandas default) on samples; use ddof=0 only when you hold the whole population.
5. **The range depends on two values only** - `vendas_660.QUANTIDADE` spans 1.00 to 3,001 (range 3,000), which is 1,500 times its IQR (2.00). The 99th percentile is 30.00, so the maximum is 100 times larger than 99% of the data. Risk: A range or a min/max chart is dominated by the single most extreme row. Fix: Show percentiles (p5, p25, p50, p75, p95) or the IQR instead of the range.
6. **The app's fixed deviation bands ignore how variable each metric really is** - For the last 24 complete months, New Patients varies from month to month by 22% (SD / mean; robust spread 27% of the median) and only 21% of its months are NEUTRAL (within +/-10% of the Year benchmark). Across metrics the NEUTRAL share runs from 21% to 67%. Risk: A metric with high natural variability is called 'ABOVE' or 'BELOW' most months by chance, so the labels lose meaning. Fix: Size the bands from each metric's own spread (for example a multiple of its MAD) instead of fixed percentages.
7. **A spread of zero breaks the robust rules** - 4 column(s) have an IQR or a MAD of 0 (for example `vendas_1015.PRODUTO_MG`, median 100): more than half of the rows share the same value, so those robust scales cannot rescale or detect outliers. Risk: Dividing by a zero scale gives infinities, or flags every different value. Fix: For such count columns use percentile caps (the 95th or 99th) or work on a transformed scale.
