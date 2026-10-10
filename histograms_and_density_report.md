# RESULT REPORT - Frequency tables, histograms and density plots

**PAGE:** "Histograms and density" in the Streamlit app (sidebar navigation). Run: `streamlit run data_app_gestao.py`. Code: `distribution_shape.py` (analysis) + `page_histograms_and_density` in `data_app_gestao.py` (UI). Only column names, counts, percentages and aggregates appear.

### 1. Frequency table and bin
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** for every numeric column: the range cut into 10 equal-width bins (the book's example), counting the rows in each bin; the same over the central 1%-99% range.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: bin width 125,952, first bin holds 99.7% of the rows, fullest bin 99.7%, 2 of 10 bins empty; on the central range the fullest bin holds 87.8%
  - `vendas_660.QUANTIDADE`: bin width 300, first bin holds 100.0% of the rows, fullest bin 100.0%, 4 of 10 bins empty; on the central range the fullest bin holds 86.1%
  - `carteira_pacientes.DIAS_ESTOQUE`: bin width 900, first bin holds 99.4% of the rows, fullest bin 99.4%, 3 of 10 bins empty; on the central range the fullest bin holds 54.2%
  - `painel.DIAS_SEM_VISITA_NUM`: bin width 94.00, first bin holds 68.3% of the rows, fullest bin 68.3%, 0 of 10 bins empty; on the central range the fullest bin holds 68.8%
  - `vendas_1015.PRODUTO_MG`: bin width 15.00, first bin holds 13.8% of the rows, fullest bin 57.1%, 7 of 10 bins empty; on the central range the fullest bin holds 57.1%
  - `vendas_1015.QTD`: bin width 3.90, first bin holds 99.1% of the rows, fullest bin 99.1%, 6 of 10 bins empty; on the central range the fullest bin holds 95.6%
  - `vendas_1015.VALOR_REPRESENTANTE`: bin width 3,971, first bin holds 99.1% of the rows, fullest bin 99.1%, 6 of 10 bins empty; on the central range the fullest bin holds 56.4%
  - `vendas_1015.VALOR_VENDA`: bin width 5,560, first bin holds 99.1% of the rows, fullest bin 99.1%, 6 of 10 bins empty; on the central range the fullest bin holds 51.0%
  - `vendas_1015.VALOR_COMISSAO`: bin width 399, first bin holds 99.1% of the rows, fullest bin 99.1%, 6 of 10 bins empty; on the central range the fullest bin holds 68.9%
- **WHAT IT MEANS FOR THE PROJECT:** A frequency table divides the range into equal bins and counts the rows in each; empty bins are part of the table because they say where there are no values.
- **PROBLEMS OR SURPRISES:**
  - `vendas_1015.PRODUTO_MG`: 7 of 10 bins are empty over the full range
  - `vendas_1015.QTD`: 6 of 10 bins are empty over the full range
  - `vendas_1015.VALOR_REPRESENTANTE`: 6 of 10 bins are empty over the full range
  - `vendas_1015.VALOR_VENDA`: 6 of 10 bins are empty over the full range
  - `vendas_1015.VALOR_COMISSAO`: 6 of 10 bins are empty over the full range

### 2. Histogram
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** the frequency table drawn as contiguous bars, for 5, 10, 20, 40, 80 bins, over the full range and the central range.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: tallest bar over the full range holds 99.7% of the rows (10 bins); over the central range 87.8%
  - `vendas_660.QUANTIDADE`: tallest bar over the full range holds 100.0% of the rows (10 bins); over the central range 86.1%
  - `carteira_pacientes.DIAS_ESTOQUE`: tallest bar over the full range holds 99.4% of the rows (10 bins); over the central range 54.2%
  - `painel.DIAS_SEM_VISITA_NUM`: tallest bar over the full range holds 68.3% of the rows (10 bins); over the central range 68.8%
  - `vendas_1015.PRODUTO_MG`: tallest bar over the full range holds 57.1% of the rows (10 bins); over the central range 57.1%
  - `vendas_1015.QTD`: tallest bar over the full range holds 99.1% of the rows (10 bins); over the central range 95.6%
  - `vendas_1015.VALOR_REPRESENTANTE`: tallest bar over the full range holds 99.1% of the rows (10 bins); over the central range 56.4%
  - `vendas_1015.VALOR_VENDA`: tallest bar over the full range holds 99.1% of the rows (10 bins); over the central range 51.0%
  - `vendas_1015.VALOR_COMISSAO`: tallest bar over the full range holds 99.1% of the rows (10 bins); over the central range 68.9%
- **WHAT IT MEANS FOR THE PROJECT:** A histogram is the picture of the frequency table: bins on the x-axis, counts on the y-axis, bars touching, equal widths, empty bins drawn.
- **PROBLEMS OR SURPRISES:**
  - none found by these rules

### 3. Bin width and number of bins
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** Sturges (log2 n + 1), square root of n, Scott (3.49 x sd x n^(-1/3)) and Freedman-Diaconis (2 x IQR x n^(-1/3)) compared with the book's 10 bins. These rules are not in your books.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO` (n = 72,674): Sturges 18, sqrt 270, Scott 1004, Freedman-Diaconis 19,060 (central range: 789)
  - `vendas_660.QUANTIDADE` (n = 72,674): Sturges 18, sqrt 270, Scott 1910, Freedman-Diaconis 31,299 (central range: 302)
  - `carteira_pacientes.DIAS_ESTOQUE` (n = 44,144): Sturges 17, sqrt 211, Scott 494, Freedman-Diaconis 1,767 (central range: 174)
  - `painel.DIAS_SEM_VISITA_NUM` (n = 5,399): Sturges 14, sqrt 74, Scott 19, Freedman-Diaconis 37 (central range: 35)
  - `vendas_1015.PRODUTO_MG` (n = 347): Sturges 10, sqrt 19, Scott 6, Freedman-Diaconis 6 (central range: 6)
  - `vendas_1015.QTD` (n = 347): Sturges 10, sqrt 19, Scott 36, Freedman-Diaconis n/a (IQR 0) (central range: n/a)
  - `vendas_1015.VALOR_REPRESENTANTE` (n = 347): Sturges 10, sqrt 19, Scott 36, Freedman-Diaconis 285 (central range: 13)
  - `vendas_1015.VALOR_VENDA` (n = 347): Sturges 10, sqrt 19, Scott 36, Freedman-Diaconis 290 (central range: 15)
  - `vendas_1015.VALOR_COMISSAO` (n = 347): Sturges 10, sqrt 19, Scott 36, Freedman-Diaconis 166 (central range: 8)
- **WHAT IT MEANS FOR THE PROJECT:** Too few bins hide features, too many draw noise. The right number depends on n, on the spread and on the question; the rules are starting points.
- **PROBLEMS OR SURPRISES:**
  - `vendas_660.FATURAMENTO`: range = 913 x IQR, so the full-range rules ask for thousands of bins
  - `vendas_660.QUANTIDADE`: range = 1,500 x IQR, so the full-range rules ask for thousands of bins

### 4. Skewness
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** skewness (bias-corrected third standardised moment), Pearson's 3 x (mean - median) / sd, Bowley's quartile skewness, and the upper over lower spread around the median (the book's symmetry check).
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: skewness 23.49 (right (long tail of large values)), 84% of the rows below the mean, mean 4,254 vs median 1,500, upper / lower spread 839
  - `vendas_660.QUANTIDADE`: skewness 111.72 (right (long tail of large values)), 85% of the rows below the mean, mean 3.39 vs median 2.00, upper / lower spread 2,999
  - `carteira_pacientes.DIAS_ESTOQUE`: skewness 13.59 (right (long tail of large values)), 71% of the rows below the mean, mean 135 vs median 90.00, upper / lower spread 100
  - `painel.DIAS_SEM_VISITA_NUM`: skewness 1.66 (right (long tail of large values)), 72% of the rows below the mean, mean 170 vs median 30.00, upper / lower spread 31
  - `vendas_1015.PRODUTO_MG`: skewness 0.54 (right (long tail of large values)), 71% of the rows below the mean, mean 122 vs median 100, upper / lower spread 2
  - `vendas_1015.QTD`: skewness 16.48 (right (long tail of large values)), 95% of the rows below the mean, mean 1.20 vs median 1.00
  - `vendas_1015.VALOR_REPRESENTANTE`: skewness 16.26 (right (long tail of large values)), 68% of the rows below the mean, mean 802 vs median 510, upper / lower spread 180
  - `vendas_1015.VALOR_VENDA`: skewness 16.09 (right (long tail of large values)), 73% of the rows below the mean, mean 993 vs median 690, upper / lower spread 80
  - `vendas_1015.VALOR_COMISSAO`: skewness 15.80 (right (long tail of large values)), 71% of the rows below the mean, mean 55.74 vs median 15.30, upper / lower spread 604
- **WHAT IT MEANS FOR THE PROJECT:** Skewness tells whether the data lean to large or small values. The book says it is discovered through displays rather than measured; the number is a summary of what the histogram shows.
- **PROBLEMS OR SURPRISES:**
  - `vendas_660.FATURAMENTO`: skewness 23.5, one extreme tail
  - `vendas_660.QUANTIDADE`: skewness 111.7, one extreme tail
  - `carteira_pacientes.DIAS_ESTOQUE`: skewness 13.6, one extreme tail
  - `vendas_1015.QTD`: skewness 16.5, one extreme tail
  - `vendas_1015.VALOR_REPRESENTANTE`: skewness 16.3, one extreme tail
  - `vendas_1015.VALOR_VENDA`: skewness 16.1, one extreme tail
  - `vendas_1015.VALOR_COMISSAO`: skewness 15.8, one extreme tail

### 5. Unimodal and multimodal (mode)
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** the mode (most frequent value) and its share; the five most frequent values; the number of peaks of the kernel density (Silverman bandwidth; a peak needs a dip below 80% before the next one); the category that explains the second peak.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: mode 1,200 (7.7% of rows), top 5 values 24%; shape: multimodal (7 peaks); peaks at 0; 566.8; 1,221; 1,962; 3,139; 4,491; 6,017
  - `vendas_660.QUANTIDADE`: mode 1.00 (36.4% of rows), top 5 values 92%; shape: spike (one value holds 36% of the rows); peaks at 1; 2.005; 3.01; 4.015; 5.989
  - `carteira_pacientes.DIAS_ESTOQUE`: mode 60.00 (14.8% of rows), top 5 values 48%; shape: multimodal (8 peaks); peaks at 31.45; 60.04; 92.21; 149.4; 179.8; 226.2; 299.5; 449.6
  - `painel.DIAS_SEM_VISITA_NUM`: mode 3.00 (3.1% of rows), top 5 values 14%; shape: multimodal (4 peaks); peaks at 17.89; 344.4; 789.1; 873.5
  - `vendas_1015.PRODUTO_MG`: mode 100 (57.1% of rows), top 5 values 100%; shape: spike (one value holds 57% of the rows); peaks at 100; 200
  - `vendas_1015.QTD`: mode 1.00 (94.5% of rows), top 5 values 100%; shape: spike (one value holds 95% of the rows); peaks at 1
  - `vendas_1015.VALOR_REPRESENTANTE`: mode 510 (54.5% of rows), top 5 values 98%; shape: spike (one value holds 54% of the rows); peaks at 505.1; 999.8
  - `vendas_1015.VALOR_VENDA`: mode 690 (49.0% of rows), top 5 values 95%; shape: spike (one value holds 49% of the rows); peaks at 1; 690.9; 1,381
  - `vendas_1015.VALOR_COMISSAO`: mode 15.30 (54.5% of rows), top 5 values 98%; shape: spike (one value holds 54% of the rows); peaks at 14.72; 100.1
  - `vendas_660.FATURAMENTO`: 50% of the values are multiples of 50 (chance 2.0%): round-number heaping
  - `carteira_pacientes.DIAS_ESTOQUE`: 66% of the values are multiples of 30 (chance 3.3%): round-number heaping
  - `vendas_660.FATURAMENTO`: peak above 1,744 explained by `TIPO_REGISTRO`: `VENDA` 45% vs `DOACAO` 0%
  - `vendas_660.QUANTIDADE`: peak above 1.50 explained by `TIPO_REGISTRO`: `VENDA` 64% vs `DOACAO` 36%
  - `vendas_1015.PRODUTO_MG`: peak above 152 explained by `PRODUTO`: `Isolate Product 002` 100% vs `Isolate Product 036` 0%
  - `vendas_1015.VALOR_REPRESENTANTE`: peak above 763 explained by `PRODUTO`: `Isolate Product 002` 100% vs `Isolate Product 036` 0%
  - `vendas_1015.VALOR_VENDA`: peak above 1,053 explained by `PRODUTO`: `Isolate Product 002` 82% vs `Isolate Product 036` 0%
  - `vendas_1015.VALOR_COMISSAO`: peak above 61.64 explained by `PRODUTO`: `Isolate Product 002` 100% vs `Isolate Product 036` 0%
- **WHAT IT MEANS FOR THE PROJECT:** A mode is a peak of the distribution; the book mentions bimodal and trimodal distributions with the mode. Several peaks usually mean a mixture of groups.
- **PROBLEMS OR SURPRISES:**
  - `vendas_660.QUANTIDADE`: one value holds 36% of the rows
  - `vendas_1015.PRODUTO_MG`: one value holds 57% of the rows
  - `vendas_1015.QTD`: one value holds 95% of the rows
  - `vendas_1015.VALOR_REPRESENTANTE`: one value holds 54% of the rows
  - `vendas_1015.VALOR_VENDA`: one value holds 49% of the rows
  - `vendas_1015.VALOR_COMISSAO`: one value holds 54% of the rows

### 6. Density scale
- **WHERE:** every numeric column
- **WHAT I RAN:** the histogram divided by n x bin width, so that the bar areas add up to 1; and a frequency table cut at the 0, 25, 50, 75, 90, 99 and 100th percentiles (unequal widths) read by count and by density.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: bins 1 (0.00 to 1,098): count 17,968 (24.7%), width 1,098, density 0.000225
  - `vendas_660.FATURAMENTO`: bins 2 (1,098 to 1,500): count 18,049 (24.8%), width 402, density 0.000618
  - `vendas_660.FATURAMENTO`: bins 3 (1,500 to 2,477): count 18,488 (25.4%), width 977, density 0.00026
  - `vendas_660.FATURAMENTO`: bins 4 (2,477 to 6,900): count 10,849 (14.9%), width 4,423, density 3.38e-05
  - `vendas_660.FATURAMENTO`: bins 5 (6,900 to 52,275): count 6,593 (9.1%), width 45,375, density 2e-06
  - `vendas_660.FATURAMENTO`: bins 6 (52,275 to 1,259,522): count 727 (1.0%), width 1,207,247, density 8.29e-09
  - `vendas_660.QUANTIDADE`: bins 1 (1.00 to 2.00): count 26,475 (36.4%), width 1.00, density 0.364
  - `vendas_660.QUANTIDADE`: bins 2 (2.00 to 3.00): count 20,041 (27.6%), width 1.00, density 0.276
  - `vendas_660.QUANTIDADE`: bins 3 (3.00 to 5.00): count 18,503 (25.5%), width 2.00, density 0.127
  - `vendas_660.QUANTIDADE`: bins 4 (5.00 to 30.00): count 6,924 (9.5%), width 25.00, density 0.00381
  - `vendas_660.QUANTIDADE`: bins 5 (30.00 to 3,001): count 731 (1.0%), width 2,971, density 3.39e-06
  - `carteira_pacientes.DIAS_ESTOQUE`: bins 1 (1.00 to 60.00): count 10,094 (22.9%), width 59.00, density 0.00388
  - `carteira_pacientes.DIAS_ESTOQUE`: bins 2 (60.00 to 90.00): count 9,060 (20.5%), width 30.00, density 0.00684
  - `carteira_pacientes.DIAS_ESTOQUE`: bins 3 (90.00 to 150): count 12,184 (27.6%), width 60.00, density 0.0046
  - `carteira_pacientes.DIAS_ESTOQUE`: bins 4 (150 to 300): count 8,353 (18.9%), width 150, density 0.00126
  - `carteira_pacientes.DIAS_ESTOQUE`: bins 5 (300 to 900): count 3,954 (9.0%), width 600, density 0.000149
  - `carteira_pacientes.DIAS_ESTOQUE`: bins 6 (900 to 9,000): count 499 (1.1%), width 8,100, density 1.4e-06
  - `painel.DIAS_SEM_VISITA_NUM`: bins 1 (1.00 to 14.00): count 1,247 (23.1%), width 13.00, density 0.0178
  - `painel.DIAS_SEM_VISITA_NUM`: bins 2 (14.00 to 30.00): count 1,396 (25.9%), width 16.00, density 0.0162
  - `painel.DIAS_SEM_VISITA_NUM`: bins 3 (30.00 to 240): count 1,406 (26.0%), width 210, density 0.00124
  - `painel.DIAS_SEM_VISITA_NUM`: bins 4 (240 to 673): count 804 (14.9%), width 432, density 0.000344
  - `painel.DIAS_SEM_VISITA_NUM`: bins 5 (673 to 896): count 490 (9.1%), width 223, density 0.000407
  - `painel.DIAS_SEM_VISITA_NUM`: bins 6 (896 to 941): count 56 (1.0%), width 45.00, density 0.00023
  - `vendas_1015.PRODUTO_MG`: bins 1 (50.00 to 100): count 48 (13.8%), width 50.00, density 0.00277
  - `vendas_1015.PRODUTO_MG`: bins 2 (100 to 200): count 299 (86.2%), width 100, density 0.00862
  - `vendas_1015.QTD`: bins 1 (1.00 to 2.54): count 343 (98.8%), width 1.54, density 0.642
  - `vendas_1015.QTD`: bins 2 (2.54 to 40.00): count 4 (1.2%), width 37.46, density 0.000308
  - `vendas_1015.VALOR_REPRESENTANTE`: bins 1 (290 to 510): count 43 (12.4%), width 220, density 0.000563
  - `vendas_1015.VALOR_REPRESENTANTE`: bins 2 (510 to 1,000): count 194 (55.9%), width 490, density 0.00114
  - `vendas_1015.VALOR_REPRESENTANTE`: bins 3 (1,000 to 2,000): count 105 (30.3%), width 1,000, density 0.000303
  - `vendas_1015.VALOR_REPRESENTANTE`: bins 4 (2,000 to 40,000): count 5 (1.4%), width 38,000, density 3.79e-07
  - `vendas_1015.VALOR_VENDA`: bins 1 (1.00 to 690): count 80 (23.1%), width 689, density 0.000335
  - `vendas_1015.VALOR_VENDA`: bins 2 (690 to 1,365): count 180 (51.9%), width 675, density 0.000768
  - `vendas_1015.VALOR_VENDA`: bins 3 (1,365 to 1,390): count 8 (2.3%), width 25.00, density 0.000922
  - `vendas_1015.VALOR_VENDA`: bins 4 (1,390 to 2,743): count 75 (21.6%), width 1,353, density 0.00016
  - `vendas_1015.VALOR_VENDA`: bins 5 (2,743 to 55,600): count 4 (1.2%), width 52,857, density 2.18e-07
  - `vendas_1015.VALOR_COMISSAO`: bins 1 (8.70 to 15.30): count 43 (12.4%), width 6.60, density 0.0188
  - `vendas_1015.VALOR_COMISSAO`: bins 2 (15.30 to 100): count 203 (58.5%), width 84.70, density 0.00691
  - `vendas_1015.VALOR_COMISSAO`: bins 3 (100 to 200): count 96 (27.7%), width 100, density 0.00277
  - `vendas_1015.VALOR_COMISSAO`: bins 4 (200 to 4,000): count 5 (1.4%), width 3,800, density 3.79e-06
- **WHAT IT MEANS FOR THE PROJECT:** The density scale makes the area under the curve equal to 1, so the area between two points is the share of the rows in between. With equal bins it only rescales the y-axis; with unequal bins it is the only fair picture.
- **PROBLEMS OR SURPRISES:**
  - none found by these rules

### 7. Density plot, kernel density estimate (KDE) and bandwidth
- **WHERE:** 4 tables, 9 numeric columns
- **WHAT I RAN:** a Gaussian KDE (one bell curve of width h per value, averaged) over the central 1%-99% range, at h/4, h (Silverman 0.9 x min(sd, IQR/1.34) x n^(-1/5)) and 4h; peaks counted at each; the share of the area that lies below the smallest value of the column.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO`: h = 89.10; peaks 24 (h/4), 7 (h), 1 (4h); area under the curve 0.982; 1.8% of the area below the minimum (0.00)
  - `vendas_660.QUANTIDADE`: h = 0.14; peaks 5 (h/4), 5 (h), 1 (4h); area under the curve 0.819; 18.0% of the area below the minimum (1.00)
  - `carteira_pacientes.DIAS_ESTOQUE`: h = 7.14; peaks 19 (h/4), 8 (h), 2 (4h); area under the curve 0.990; 0.1% of the area below the minimum (1.00)
  - `painel.DIAS_SEM_VISITA_NUM`: h = 23.65; peaks 5 (h/4), 4 (h), 2 (4h); area under the curve 0.834; 15.8% of the area below the minimum (1.00)
  - `vendas_1015.PRODUTO_MG`: h = 14.71; peaks 3 (h/4), 2 (h), 1 (4h); area under the curve 0.785; 6.9% of the area below the minimum (50.00)
  - `vendas_1015.QTD`: h = 0.06; peaks 1 (h/4), 1 (h), 1 (4h); area under the curve 0.522; 47.8% of the area below the minimum (1.00)
  - `vendas_1015.VALOR_REPRESENTANTE`: h = 77.88; peaks 3 (h/4), 2 (h), 1 (4h); area under the curve 0.933; 6.4% of the area below the minimum (290)
  - `vendas_1015.VALOR_VENDA`: h = 124; peaks 4 (h/4), 3 (h), 1 (4h); area under the curve 0.945; 5.4% of the area below the minimum (1.00)
  - `vendas_1015.VALOR_COMISSAO`: h = 11.28; peaks 2 (h/4), 2 (h), 1 (4h); area under the curve 0.777; 22.0% of the area below the minimum (8.70)
- **WHAT IT MEANS FOR THE PROJECT:** A density plot is a smoothed histogram computed from the data with a kernel; the bandwidth controls the smoothing. The area under the whole curve is 1.
- **PROBLEMS OR SURPRISES:**
  - `vendas_660.QUANTIDADE`: 18.0% of the density lies below the minimum, at values that do not occur
  - `painel.DIAS_SEM_VISITA_NUM`: 15.8% of the density lies below the minimum, at values that do not occur
  - `vendas_1015.PRODUTO_MG`: 6.9% of the density lies below the minimum, at values that do not occur
  - `vendas_1015.QTD`: 47.8% of the density lies below the minimum, at values that do not occur
  - `vendas_1015.VALOR_REPRESENTANTE`: 6.4% of the density lies below the minimum, at values that do not occur
  - `vendas_1015.VALOR_VENDA`: 5.4% of the density lies below the minimum, at values that do not occur
  - `vendas_1015.VALOR_COMISSAO`: 22.0% of the density lies below the minimum, at values that do not occur

## TOP INSIGHTS

1. **Skewness: the data have one long right tail, and the mean follows it** - 9 of 9 numeric columns are right-skewed (skewness above 0.5). The strongest is `vendas_660.QUANTIDADE` with skewness 111.7: its mean (3.39) is above its median (2.00), 85% of the rows are below the mean, and the largest value is 2999 times as far above the median as the smallest is below it. Risk: A summary or a model that assumes a symmetric bell shape (mean, standard deviation) describes a row that most orders do not look like. Fix: Look at the shape first; for a skewed column report the median and percentiles, or work on a log scale.
2. **Ten equal bins over the full range hide the distribution** - For `vendas_660.QUANTIDADE` the book's 10 equal-width bins put 100.0% of the rows in the first bin and leave 4 of 10 bins empty, because the range is 1,500 times the IQR. On the central 1%-99% range the fullest bin holds 86% and 0 bins are empty. Risk: A histogram of the full range shows one tall bar and an empty axis: the shape, the modes and the business-relevant region are invisible. Fix: Draw the histogram of the central range (or on a log scale) and say how many values were left out.
3. **Bin width and number of bins: the rules of thumb disagree by orders of magnitude** - For `vendas_660.QUANTIDADE` (72,674 rows) Sturges asks for 18 bins, the square-root rule for 270, but the Freedman-Diaconis width (2 x IQR x n^(-1/3)) would need 31,299 bins over the full range, and 302 over the central range. Risk: The number of bins is a choice that changes the story: too few hides peaks, too many draws noise. Fix: Try several bin counts, and choose with the question (a few bins for the overall shape, more for peaks); never trust one default.
4. **The mode: a single value often holds a large share of the rows** - In `vendas_1015.QTD` the most frequent value is 1.00, held by 94.5% of the rows; its five most frequent values hold 100%. 6 of 9 columns have one value with at least 20% of the rows. In `carteira_pacientes.DIAS_ESTOQUE` 66% of the values are multiples of 30 (chance alone would give 3.3%): the values heap on round numbers, which is where the peaks of the density sit. Risk: A histogram or a density of such a column shows one huge spike (or a smoothed hump) and the average is a value that hardly occurs: prices, standard quantities and round numbers repeat. Fix: For columns with a few frequent values use a bar chart of the most frequent values; report the mode next to the median.
5. **Multimodal: more than one peak usually means a mix of two kinds of rows** - 8 of 9 columns have two or more peaks in their density (Silverman bandwidth), for example `carteira_pacientes.DIAS_ESTOQUE` with 8 (at 31.45; 60.04; 92.21; 149.4; 179.8; 226.2; 299.5; 449.6). The upper peak of `vendas_1015.VALOR_REPRESENTANTE` is explained by `PRODUTO`: 100% of `Isolate Product 002` rows lie above the valley (763) against 0% of `Isolate Product 036`. Risk: Averaging a mixture describes neither group; the mean sits in the valley where few rows are. Fix: Find the category that separates the peaks and analyse the groups apart.
6. **Density scale: with bins of unequal width, equal counts are not equal densities** - Cutting `painel.DIAS_SEM_VISITA_NUM` at its percentiles gives bins of very different width. 3 bins hold about the same share of the rows (23%, 26%, 26%), so as bars of counts they look alike; but bin 1 (1.00 to 14.00) is 14.4 times denser than bin 3 (30.00 to 240), because it is narrower. Risk: Plotting counts for unequal bins makes wide bins look as crowded as narrow ones and hides where the rows really concentrate. Fix: With unequal bins plot the density (count / (n x width)) so the area, not the height, is the share of rows; with equal bins counts and density have the same shape.
7. **Bandwidth: the number of peaks you see depends on the smoothing you choose** - For `vendas_660.FATURAMENTO` the density has 24 peaks with a bandwidth of h/4, 7 with the Silverman rule and 1 with 4h (h = 89.10). Risk: A too-small bandwidth invents peaks out of noise; a too-large one erases real ones. Both look equally convincing on a chart. Fix: Draw the density at two or three bandwidths and trust only the peaks that survive; compare with the histogram.
8. **A density curve invents values that cannot exist** - The kernel density of `vendas_1015.QTD` (6 distinct values, minimum 1.00) puts 47.8% of its area below that minimum, at values the column never takes. Risk: Smoothing counts and bounded quantities spreads probability onto impossible values (fractions of a unit, negative amounts). Fix: For counts and columns with few distinct values use a bar chart of the values instead of a density.
