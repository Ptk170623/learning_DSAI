# Statistics in Practice: lessons (text version of the artifact)

Chapter 1 of *Practical Statistics for Data Scientists* (Bruce, Bruce & Gedeck), taught on the project's real, anonymized data. Same content as the lessons at the top of each tab of the artifact: for each concept, what the book says (with printed page numbers), the real numbers, why it matters for the business, and the insight. Concepts that are not in the two books are labelled 'Outside your two books'.

## A. Elements of structured data
*Practical Statistics, Chapter 1, pp.2-4*

### A1 - Structured data and its types

**Concepts:** Structured data; Variable (column); Observation (row); Data type; Numeric; Continuous; Discrete; Categorical; Nominal; Binary; Ordinal; Level

**Source:** Practical Statistics, Ch.1, 'Elements of Structured Data', pp.2-4 | Morettin & Bussab, Ch.2, §2.1 'Tipos de Variáveis', p.9

**What the book says**
- Raw data such as images, text and clicks must be turned into a structured form before statistics can be applied to it. The commonest structured form is a table of rows and columns.
- There are two basic types. Numeric data is continuous (any value in an interval, such as a duration) or discrete (integers, such as counts). Categorical data takes a fixed set of values; binary is the special case with two values, and ordinal is categorical with an explicit order.
- The type matters because it decides the right chart, the right summary and how the software computes with the variable.
- *Note: Variable, observation and level are not defined as boxed terms in these pages. Here: a variable is a column, an observation is a row, and a level is one distinct value of a categorical variable (my wording).*

**In your data**
- tables: **5**
- observations (rows): **222,405**
- variables (columns): **67**
- numeric columns: **9**
- *Chart: Columns by statistical type.* Orange: the stored type (dtype) misleads about that type, see the next lesson.

**Why it matters for the business:** Only 9 of the 67 columns are quantities you can average. The other 58 are labels, flags, identifiers and dates: they should be counted, grouped or placed in time, never averaged.

**Insight:** The tables are mostly categorical: 27 nominal columns. They differ a lot in their number of levels: `PRODUTO` has 492 levels and `TIPO_PAGAMENTO` only 3. The second works as a filter as it is (the app's 'Payment Type' segmenter); the first has to be grouped before it fits in a chart.

**Watch out:** Do not trust a column's type from its name or from how it looks: a column of 0 and 1 is binary, not a quantity, and the next lesson shows how it can be stored.

### A2 - Stored type versus statistical type, and the identifier

**Concepts:** Stored type vs. statistical type; Dtype; Identifier

**Source:** Practical Statistics, Ch.1, 'Elements of Structured Data', p.3 (data typing as a signal to the software)

**What the book says**
- The book says that data typing is a signal telling the software how to process a variable: charts, models and computations behave according to it. It also warns that software can change types behind your back, for example R's read.csv turns text into categories and rejects new values (p.3); pandas does not convert automatically, but you can declare a column categorical.
- *Note: 'Stored type vs. statistical type' and 'identifier' are not terms of the book. Stored type = the dtype the software holds. Statistical type = what the variable really is. An identifier names a thing and is not a quantity (my definitions, outside your books).*

**In your data**
- columns whose stored type misleads: **8 of 67**
- flag stored as text digits: **3**
- ID / code stored as number: **1**
- date / period stored as number: **1**
- date stored as text: **1**
- identifier columns: **11**
- *Chart: Stored type (rows) against statistical type (columns).* Each cell counts columns. An integer or float dtype under 'identifier' or 'binary' is a mismatch.

**Why it matters for the business:** The 'New Patients' metric of the 660 Analysis depends on `PRIMEIRA_CLIENTE == "1"`. That flag is stored as text: comparing it with the number 1 finds 0 rows, comparing it with the text "1" finds 21,858. `MARCA_PROPRIA` is the opposite: stored as a number, `== 1` finds 64,766 and `== "1"` finds 0. The app works because each flag is compared in its own dtype; a change of type at the source would zero a KPI with no error.

**Insight:** 4 identifier columns look like one-per-row keys (90% or more unique) yet repeat: `ID_VENDA` is 97.6% unique with 1,755 repeats. And `ID_FUNCIONARIO` is stored as a float with 8 distinct values, so 68,538 of its values could be averaged: an average of employee numbers means nothing.

**Watch out:** Treat flags and IDs as text or boolean, never as numbers you could add up.

## B. Rectangular data, nonrectangular structures and tidy data
*Practical Statistics, Chapter 1, pp.4-7 (tidy data, wide/long, data matrix and silent errors are outside your books)*

### B1 - Rectangular data, record, feature, outcome and index

**Concepts:** Rectangular data; Data frame; Record; Feature; Outcome; Index

**Source:** Practical Statistics, Ch.1, 'Rectangular Data', pp.4-6 and 'Data Frames and Indexes', p.6

**What the book says**
- Rectangular data is a two-dimensional table with rows as records (cases) and columns as features (variables); the data frame is its format in R and Python. Many projects predict an outcome (also called response or target) from the features.
- A database table has an index, essentially a row number. In pandas, an automatic integer index is created from the order of the rows.
- Terminology differs between fields: computer scientists use 'sample' for one row, statisticians use it for a collection of rows.
- *Note: Which columns are features and which are outcomes depends on the question you ask. Here they are assumed from the type and the name (measures and a target-like flag as outcomes).*

**In your data**
- vendas_660: records x columns: **72,674 x 24**
- tipo_venda: records x columns: **72,674 x 5**
- carteira_pacientes: records x columns: **70,581 x 11**
- painel: records x columns: **6,129 x 11**
- vendas_1015: records x columns: **347 x 16**
- record of vendas_660: **ID_VENDA, PRODUTO**
- *Chart: Columns by role.* Roles are assumed. Keys are identifiers; outcomes are measures and flags to total or predict.

**Why it matters for the business:** In `vendas_660` one row is not one sale: it is a sale line, identified by `ID_VENDA, PRODUTO`. `ID_VENDA` alone repeats up to 12 times, so counting rows would overstate orders. The project already counts distinct `ID_VENDA` for its 'Order Count' metric.

**Insight:** Every table has the default 0..n-1 index, which says nothing about the record. And `vendas_1015` has no unique key at all: 29 of its 347 rows (8.4%) are exact duplicates. If they are not real repeat events, its revenue columns are overstated.

**Watch out:** Decide what one row stands for before counting anything: the key, not the table name, defines the record.

### B2 - Nonrectangular data structures

**Concepts:** Nonrectangular data structures

**Source:** Practical Statistics, Ch.1, 'Nonrectangular Data Structures', pp.6-7

**What the book says**
- Besides the table, the book names three other structures. Time series: successive measurements of the same variable. Spatial data: objects with coordinates, or small units of space with a value. Graph (network) data: entities and the relationships between them.
- The book focuses on rectangular data because it is the building block of predictive modelling.
- *Note: In my first analysis I called the project's Python objects that bundle several tables 'nonrectangular'. That is not the book's meaning; those are only bundles of rectangles.*

**In your data**
- monthly time series: **121 months**
- first month: **10/2016**
- last month (partial): **10/2026**
- doctors, clients, links: **5,116, 22,131, 22,774**
- *Chart: Monthly revenue of own-brand sales (all blocks).* A time series built from the table: one point per month. The last month is partial.

**Why it matters for the business:** The 660 Analysis does not read rows: it groups the table into a monthly series per block and compares the chosen month with a benchmark made from the months before it. The unit of the analysis is the month, not the sale.

**Insight:** Time series: yes (121 months). Spatial: no, the tables only hold place names (`ESTADO`, `CIDADE`), no coordinates. Graph: implicit. The sales rows link 5,116 doctors to 22,131 patients through 22,774 distinct pairs; most doctors have 1 patient, but one has 469.

**Watch out:** The newest month in the data is partial, so it must not be compared with a full benchmark.

### B3 - Tidy data and the duplicate key

**Concepts:** Tidy data; Duplicate key

**Source:** Outside your two books: Wickham, 'Tidy Data' (Journal of Statistical Software, 2014)

**What the book says**
- Not covered in your two books. The standard rules: each variable is a column; each observation is a row; each type of observational unit is its own table.
- A duplicate key is a key that repeats: a join on it returns more rows than the table you started with.
- *Note: Both definitions come from outside your books. The check used here: when one identifier fixes the values of other columns, those columns describe another unit repeated on every row.*

**In your data**
- columns fixed by ID_VENDA (vendas_660): **18**
- ID_VENDA repeats: **1,755**
- sale lines per doctor, on average: **14.2**
- *Chart: Columns that one identifier fixes (same table).* A high number means that table also stores another unit (a sale, a client, a doctor) on every row.

**Why it matters for the business:** In `vendas_660` the doctor's name, block and registration, and the client's name, are copied onto every sale line: a doctor appears on about 14 lines. A rename or a change of block would have to be applied everywhere and can leave rows that disagree. A doctor table and a client table would hold each fact once.

**Insight:** `ID_VENDA` fixes 18 other columns (dates, client, doctor, block, payment type...) for 99% or more of its repeated values: sale-level data lives on every line of the sale. Two tables, sale and sale line, would be the tidy shape. The key that works today is the pair `ID_VENDA, PRODUTO`.

**Watch out:** This is a design judgment, not an error: the flat table is convenient for the app, as long as everyone knows what a row is.

### B4 - Wide and long

**Concepts:** Wide and long

**Source:** Outside your two books: Wickham, 'Tidy Data', 2014; pandas pivot_table

**What the book says**
- Not covered in your two books (the book only mentions the pivot_table method for cross-tabulations, p.40). Long: one row per event or per measurement. Wide: one column per period or category. Pivoting turns long into wide.
- *Note: The stored tables are long: a row per sale line. The app pivots them into wide month matrices to compute its benchmarks.*

**In your data**
- wide shape (blocks x months): **68 x 121**
- cells: **8,228**
- cells with data: **4,519**
- empty cells: **45%**
- *Chart: The wide table: revenue by block (rows) and month (columns).* Blue: the block sold something that month. Grey: no sale, an empty cell. Labels are hidden.

**Why it matters for the business:** In the benchmark code a month with no data counts as 0 (`reindex(...).fillna(0)`). So in a block that sells only some months, the mean or median of the benchmark window is dragged down by those zeros, and the same month looks stronger against it.

**Insight:** The wide table of blocks by month is 45% empty: 3,709 of 8,228 cells have no sale. Long data hides this because absent rows are simply not there; wide data forces a choice (0 or missing) on every empty cell.

**Watch out:** The choice 'empty means zero' is a business decision (no sales) that the pivot makes silently.

### B5 - From table to data matrix

**Concepts:** Data matrix

**Source:** Outside your two books: design (data) matrix of regression and machine learning

**What the book says**
- Not covered in your two books under this name. A data matrix is the all-numeric version of a table that models and matrix routines use: categorical columns must be encoded (one-hot: a 0/1 column per level) and gaps must be handled first.
- *Note: Counted here without building any model: how many numeric columns a table offers, how wide the encoded matrix would be, and how many rows a model would lose to gaps.*

**In your data**
- vendas_660 numeric columns: **2**
- vendas_660 one-hot columns (all categoricals): **28,135**
- carteira_pacientes rows lost by dropna: **37.5%**
- *Chart: Rows lost if every row with a missing number is dropped.* Share of each table's rows removed by dropna on its numeric columns.

**Why it matters for the business:** A model on the numeric columns of `carteira_pacientes` would silently lose 37.5% of its 70,581 rows. Those are rows with no stock-rupture figure, so the model would learn from a different group of patients than the one it will be used on.

**Insight:** One-hot encoding every categorical column of `vendas_660` would give 28,135 columns, most of them from high-cardinality columns such as names and products; with only the columns of 50 levels or fewer it is 21.

**Watch out:** Decide what a missing number means ('none', 'unknown', 'not applicable') before dropping or filling it.

### B6 - Silent errors

**Concepts:** Silent error; Dtype; Duplicate key

**Source:** Outside your two books: pandas behaviour (merge, groupby, comparison of dtypes)

**What the book says**
- Not covered in your two books. A silent error is a wrong or empty result with no error and no warning. Three of them can be measured in these tables: a merge on a key that is not unique, a flag compared with the wrong dtype, and a groupby that drops rows whose key is missing.
- *Note: Each check is run on the real tables without changing anything.*

**In your data**
- merge vendas_660 + tipo_venda on ID_VENDA only: **+5.6% rows**
- FATURAMENTO inflated: **+3.92%**
- rows without NOME_BLOCO: **2.1%**
- FATURAMENTO in those rows: **18.6%**
- *Chart: Merging on the near-unique key alone.* Extra rows and extra measure created by a merge on ID_VENDA alone (pandas raises no error).

**Why it matters for the business:** A code comment in transform.py records that the app merges sales with the sale-type table on `[ID_VENDA, PRODUTO]` and not on `ID_VENDA` alone (a bug caught early); the check shows why: the shortcut would add 4,068 rows and inflate revenue by 3.92%, with nothing to warn anyone.

**Insight:** Rows with no `NOME_BLOCO` are only 2.1% of the table but carry 18.6% of `FATURAMENTO`. A plain groupby by block would drop them from every block total. The app avoids it by filling missing blocks with '(not informed)'.

**Watch out:** After any merge, compare the row count before and after; after any groupby, compare the group totals with the table total.

## C. Estimates of location
*Practical Statistics, Chapter 1, pp.7-13*

### C1 - Mean, trimmed mean and median

**Concepts:** Estimate of location; Mean; Trimmed mean; Median

**Source:** Practical Statistics, Ch.1, 'Estimates of Location', pp.7-12 | Morettin & Bussab, §3.1 'Medidas de Posição', p.35

**What the book says**
- An estimate of location is a 'typical value' for a variable. The mean is the sum divided by the count. The trimmed mean drops a fixed number of the lowest and highest values first (10% at each end is a common choice). The median is the middle value of the sorted data: half the values are above it and half below.
- The mean is easy to compute but sensitive to extreme values. In the book's state-population example the mean (6.16 million) is larger than the trimmed mean (4.78 million), which is larger than the median (4.44 million), because a few very large states pull the mean up.

**In your data**
- FATURAMENTO: rows: **72,674**
- mean: **4,253.67**
- trimmed mean (10%): **1,921.46**
- median: **1,500.00**
- *Chart: Mean, trimmed mean and median of every numeric column.* Same order as the book's example: the mean sits furthest right when the data are skewed. Axis compressed (symmetric log).

**Why it matters for the business:** The 'average ticket' reported from `FATURAMENTO` depends on the estimate: the mean is 4,254, the trimmed mean 1,921 and the median 1,500. A manager who reads 'average revenue per line is 4,254' is describing a line that most orders never reach.

**Insight:** The mean is 184% above the median in `FATURAMENTO`. In all 9 numeric columns the mean is at least 20% away from the median, the same pattern as the book's states, only stronger.

**Watch out:** The mean is the right estimate when you need a total (mean x rows = total); it is the wrong one for 'typical'.

### C2 - Outlier and robust

**Concepts:** Outlier; Robust

**Source:** Practical Statistics, Ch.1, 'Median and Robust Estimates' and 'Outliers', pp.10-11 | Morettin & Bussab, §3.3, p.43 (the median is 'resistente')

**What the book says**
- An outlier is a value very distant from the others. Being an outlier does not make a value wrong (Bill Gates in a neighbourhood income average), but outliers are often data errors, such as mixed units, and are worth investigating.
- An estimate is robust (resistant) when it is not influenced by outliers. The median is robust; so is a trimmed mean, which the book calls a compromise between the median and the mean.

**In your data**
- FATURAMENTO: outliers (beyond 1.5 x IQR): **14.4%**
- mean after removing them: **-64%**
- median after removing them: **-7.3%**
- largest value / median: **840 x**
- *Chart: How much each estimate moves when the outliers are removed.* Absolute change in %. A robust estimate barely moves.

**Why it matters for the business:** One `FATURAMENTO` value is 840 times the median (1,259,522 against 1,500). Whether it is a legitimate large order or a typing error, it changes the mean by 64% alone with the other outliers, and any benchmark or KPI built on that mean moves for reasons that have nothing to do with business.

**Insight:** `DIAS_ESTOQUE` (days of stock) reaches 9,000 days, about 25 years: that one looks like a data error, not a real patient. It is exactly what the book means by 'worthy of further investigation'.

**Watch out:** Do not delete outliers automatically: investigate first, then correct, keep or analyse them separately.

### C3 - Weight, weighted mean and weighted median

**Concepts:** Weight; Weighted mean; Weighted median

**Source:** Practical Statistics, Ch.1, 'Mean' (weighted mean), p.10, and 'Median and Robust Estimates' (weighted median), p.11; example p.12-13

**What the book says**
- A weighted mean multiplies each value by a weight and divides by the sum of the weights. Two main reasons: some values are intrinsically more variable and deserve less weight, or the data do not represent the groups equally and underrepresented groups need more weight.
- The weighted median is the value at which the weights of the lower and upper halves are equal. In the book's example the average murder rate for the country needs weights, because the states have very different populations.

**In your data**
- plain mean of FATURAMENTO/QUANTIDADE: **1,175.39**
- weighted mean: **1,253.62**
- plain median: **695.00**
- weighted median: **979.13**
- *Chart: vendas_660: revenue per unit (FATURAMENTO / QUANTIDADE), plain and weighted.* Weighted by the quantity of each line.

**Why it matters for the business:** The price per unit is only meaningful weighted: the weighted mean (1,253.62) is exactly total FATURAMENTO divided by total QUANTIDADE, so it reconciles with the accounting total, while the plain mean (1,175.39) counts a one-unit line like a line of hundreds. The weighted median (979.13) is 29% away from the plain median.

**Insight:** Averaging block averages is the same trap: the mean of the 68 block means of `FATURAMENTO` is 4,247.86, but the overall mean is 3,536.56 (+20%), because blocks range from 1 to 7,372 rows. Weighting each block by its size gives back 3,536.56.

**Watch out:** Any average of averages needs weights, otherwise a one-row group counts as much as a 7,000-row group.

### C4 - Sample and estimate

**Concepts:** Sample; Estimate

**Source:** Practical Statistics, Ch.1, box 'Metrics and Estimates', p.9, and box 'Terminology Differences', p.6

**What the book says**
- Statisticians use 'estimate' for a value calculated from the data at hand, to distinguish it from the true value in the whole population; data scientists tend to say 'metric'. Accounting for uncertainty is at the heart of statistics.
- A 'sample' to a statistician is a collection of rows from a population (not a single row, as for computer scientists).
- *Note: To see what an estimate's uncertainty looks like, 400 random samples were drawn from each column and the sample mean and sample median were computed for each.*

**In your data**
- FATURAMENTO full-data mean: **4,254**
- sample mean, range of 90% of 200-row samples: **2,940 to 6,129**
- full-data median: **1,500**
- sample median, same samples: **1,390 to 1,690**
- *Chart: How much an estimate moves from one random sample to the next.* Standard deviation of the estimate across samples, as % of the full-data value.

**Why it matters for the business:** Any dashboard fed by a sample reports an estimate, not the truth. For `FATURAMENTO` two analysts with different 200-row samples would see a mean anywhere between 2,940 and 6,129, while their medians would agree within 1,390 to 1,690.

**Insight:** With skewed data the sample mean moves 3.4 times more than the sample median. Not always: for `DIAS_SEM_VISITA_NUM` the sample median moves slightly more than the sample mean, so robust does not always mean steadier.

**Watch out:** Report an estimate with its spread (a range or an interval), not as a single exact number.

### C5 - Mean versus median: when to use each

**Concepts:** Mean vs. median: when to use each

**Source:** Practical Statistics, Ch.1, 'Key Ideas', p.13; 'Median and Robust Estimates', p.10

**What the book says**
- The book's key ideas: the basic metric for location is the mean, but it can be sensitive to extreme values (outliers). Other metrics, the median and the trimmed mean, are less sensitive to outliers and unusual distributions and hence are more robust.
- *Note: The decision rule is mine, not the book's: median (or trimmed mean) when skew is above 1 or 1% of the values are outliers; otherwise the mean. And the mean when you need a total, since mean x rows = total.*

**In your data**
- columns where the median is advised: **8 of 9**
- app checks where Mean and Median disagree: **38 of 240 (16%)**
- worst case: **Order Count, Quarter: 42% of months**
- *Chart: 660 Analysis: share of months where the Mean/Median switch changes the classification.* Last 12 complete months, all blocks, the project's own function run with Mean and with Median.

**Why it matters for the business:** The 660 Analysis lets the user choose 'Mean' or 'Median' as the summary measure of the benchmark. The same month gets a different label ('NEUTRAL' or 'SLIGHTLY ABOVE', for instance) in 16% of the 240 checks. The choice is not cosmetic: it decides which blocks and months get flagged for action.

**Insight:** Reading the book's rule on this project: median for the money and quantity columns (skewed, with outliers), mean only where totals are needed. For monthly metrics the two are closer (2.8% apart on the median), but the labels still flip in the most sensitive windows.

**Watch out:** Always show which measure a classification used.

## D. Estimates of variability
*Practical Statistics, Chapter 1, pp.13-19*

### D1 - Deviation, variance, standard deviation, degrees of freedom and bias

**Concepts:** Variability; Deviation; Variance; Standard deviation; Degrees of freedom and n minus 1; Bias

**Source:** Practical Statistics, Ch.1, 'Estimates of Variability' and 'Standard Deviation and Related Estimates', pp.13-16 | Morettin & Bussab, §3.2 'Medidas de Dispersão', p.37

**What the book says**
- Variability (dispersion) says whether values are tightly clustered or spread out. A deviation is the difference between an observed value and the estimate of location. Deviations around the mean add up to exactly zero, so averaging them tells nothing; we take absolute values or squares.
- The variance is the sum of squared deviations divided by n - 1; the standard deviation is its square root, in the original units. Dividing by n would underestimate the true variance (a biased estimate); n - 1 degrees of freedom, because one is used up by estimating the mean, makes it unbiased. The book adds that for large n this hardly matters.

**In your data**
- FATURAMENTO mean: **4,253.67**
- standard deviation: **15,003.20**
- sum of deviations: **3.0e-08 (zero)**
- largest value, in SDs from the mean: **84**
- *Chart: Bias of the variance estimate in samples of 10 rows.* Average estimate against the full-data variance. Dividing by n sits near -10%, n - 1 near 0%.

**Why it matters for the business:** The standard deviation of `FATURAMENTO` is 15,003, 353% of its mean: the revenue of a line is very unpredictable. Any control limit or forecast range built from it is wide because of a few extreme lines, not because the typical line is that variable.

**Insight:** The book says n versus n - 1 rarely matters. For 10-row samples it does: dividing by n underestimates the variance by 9% (theory: 10%) and n - 1 brings it to +1% (median across columns). So the small groups of this project (a block with 7 or 15 lines) deserve n - 1. The standard deviation itself still comes out low (-62% median): the square root and skew, since small samples seldom contain the extreme values.

**Watch out:** pandas' .std() already divides by n - 1; NumPy's np.std divides by n unless you pass ddof=1.

### D2 - Mean absolute deviation and the MAD

**Concepts:** Mean absolute deviation; MAD (median absolute deviation)

**Source:** Practical Statistics, Ch.1, 'Standard Deviation and Related Estimates', pp.14-16 | Morettin & Bussab, §3.2 'Medidas de Dispersão', p.37

**What the book says**
- The mean absolute deviation is the average of the absolute deviations from the mean. The MAD is the median of the absolute deviations from the median: like the median, it is not influenced by extreme values. Multiplying it by 1.4826 puts it on the scale of a standard deviation for a normal distribution.
- The three are not equivalent: the standard deviation is always larger than the mean absolute deviation, which is larger than the MAD. The book's state-population example has a standard deviation almost twice the MAD, 'not surprising since the standard deviation is sensitive to outliers'.

**In your data**
- FATURAMENTO: standard deviation: **15,003**
- mean absolute deviation: **4,641**
- scaled MAD: **804**
- SD / scaled MAD: **18.7**
- *Chart: Standard deviation divided by the scaled MAD.* About 1 for bell-shaped data. The book's example is about 2. Columns with a MAD of 0 are left out.

**Why it matters for the business:** If a report quotes only the standard deviation of `FATURAMENTO` (15,003), it describes a spread that exists because of a few lines. The MAD says the typical line is within about 804 of the median. Two different stories about the same column.

**Insight:** The ratio is 18.7 for `FATURAMENTO` and 19.4 for `vendas_1015.VALOR_VENDA`: ten times the book's example. Four of the nine numeric columns have a MAD of 0, because more than half of their rows share one value (counts and prices).

**Watch out:** When the MAD is 0, it cannot be used to scale or to flag anything: use percentiles.

### D3 - Range, order statistics, percentile, quartile and IQR

**Concepts:** Range; Order statistics; Percentile; Quartiles (Q1, Q2, Q3); IQR (interquartile range)

**Source:** Practical Statistics, Ch.1, 'Estimates Based on Percentiles', pp.16-18 | Morettin & Bussab, §3.3 'Quantis Empíricos', p.41

**What the book says**
- Order statistics are metrics based on the sorted data. The range (largest minus smallest) is useful to spot outliers, but extremely sensitive to them. A percentile is the value such that P percent of the values are at or below it; the median is the 50th percentile; quartiles are the 25th, 50th and 75th.
- The interquartile range (IQR) is the 75th percentile minus the 25th: the width of the middle half of the data. It avoids the sensitivity of the range to outliers.

**In your data**
- QUANTIDADE: smallest to largest: **1 to 3,001**
- range / IQR: **1,500 x**
- 99th percentile: **30**
- largest / 99th percentile: **100 x**
- *Chart: Range divided by the IQR.* How many middle-half widths the whole range spans. Axis compressed.

**Why it matters for the business:** Quoting `QUANTIDADE` as '1 to 3,001 units' tells nobody anything: 99% of the lines are 30 units or fewer, and the IQR is 2. A single 3,001-unit line makes the range 1,500 times the IQR.

**Insight:** The IQR is reliable where the range is not: its value is 2 for `QUANTIDADE` whether or not that extreme line is in the data. Percentiles (here p5, p25, p50, p75, p95, p99) are the better way to describe both the centre and the tail.

**Watch out:** Read 'p99 versus maximum': if they are far apart, the maximum is telling you about one row, not about the distribution.

### D4 - Variability in the app: the deviation bands

**Concepts:** Variability; Deviation; MAD (median absolute deviation)

**Source:** The project's transform.classify_deviation (bands of 10%, 25%, 40%)

**What the book says**
- Applying the book's idea to the project: variability decides how far a value must be from the centre before it means something. The app uses fixed bands instead (NEUTRAL within 10% of the benchmark, SLIGHTLY within 25%, then 40%).
- *Note: Spread of the monthly series of each 660 metric (all blocks) over the last 24 complete months, and how often the app's own function calls a month NEUTRAL against the Year benchmark.*

**In your data**
- Revenue (R$): month-to-month CV: **19%**
- Order Count: month-to-month CV: **11%**
- Units: month-to-month CV: **12%**
- New Patients: month-to-month CV: **22%**
- *Chart: How the app classifies the last 24 complete months.* Share of months in each band, Year window, Mean benchmark.

**Why it matters for the business:** For New Patients only 21% of months are NEUTRAL, because the metric naturally moves 22% from month to month: most months look 'good' or 'bad' by chance. For Order Count it is 67%.

**Insight:** A band of the same 10% is tight for a volatile metric and loose for a steady one. Bands sized from each metric's own spread (for example a multiple of its MAD) would make labels comparable across metrics.

**Watch out:** A flagged month is not necessarily an event: check the metric's normal month-to-month spread first.

## E. Exploring the data distribution: percentiles and boxplots
*Practical Statistics, Chapter 1, pp.19-26*

### E1 - Percentile and quartile calculation: position and interpolation

**Concepts:** Percentile; Quartiles (Q1, Q2, Q3); Quartile calculation (position and interpolation)

**Source:** Practical Statistics, Ch.1, box 'Percentile: Precise Definition', p.17, and the IQR example, p.17 | Morettin & Bussab, §3.3, Example 3.5, pp.42-43

**What the book says**
- The book's example {3,1,5,3,6,7,2,9}, sorted {1,2,3,3,5,6,7,9}, gives a 25th percentile of 2.5 and a 75th of 6.5, an IQR of 4. It warns that software can differ slightly, and that the percentile is a weighted average of two neighbouring sorted values with different choices of the weight; R offers nine ways, NumPy at the time of writing only one: linear interpolation.
- Morettin & Bussab take the quartile as the median of each half of the sorted data (example 3.5: q1 = (3+5)/2 = 4, q3 = (11+12)/2 = 11.5) and note the difficulty of defining other quantiles.
- *Note: Discovery on running it: NumPy's default (linear) does NOT reproduce the book's 2.5 and 6.5. It gives 2.75 and 6.25. The midpoint method does reproduce them.*

**In your data**
- book example, linear (pandas default): **Q1 2.75, Q3 6.25**
- book example, midpoint: **Q1 2.5, Q3 6.5**
- FATURAMENTO Q1 position (n - 1) x 0.25: **18,168.25**
- neighbours there: **1,098 and 1,098**
- *Chart: The book's own example under six quartile methods.* Data {3,1,5,3,6,7,2,9}. Position = (n - 1) x p on the sorted values counted from 0, then the method picks or blends the neighbours.
- *Chart: Real groups: how much Q1 changes with the method.* Spread of Q1 across the six methods, as % of the group's IQR, for the smallest real groups.

**Why it matters for the business:** Two tools can print different quartiles for the same small group, so a rule like 'flag anything above Q3 + 1.5 IQR' would flag different rows depending on the tool. For large groups it does not matter: the six methods differ by at most 4.44% of the IQR for whole columns.

**Insight:** For `FATURAMENTO` Q1 sits at position 18,168.25, between two equal values (1,098 and 1,098), so there is nothing to interpolate. The method only bites for small groups: for a group of 7 rows the quartile can move by up to 90% of the IQR.

**Watch out:** State the method (pandas, numpy, Excel and R do not all agree) and avoid quartiles for groups of a handful of rows.

### E2 - The boxplot: box, median line, whiskers, caps and fences

**Concepts:** Boxplot (box, median line); Whisker and cap; Fences (lower and upper) and the 1.5 × IQR rule; Outlier; Robust (mean vs. median/IQR)

**Source:** Practical Statistics, Ch.1, 'Percentiles and Boxplots', pp.20-21 | Morettin & Bussab, §3.4 'Box Plots', pp.47-50

**What the book says**
- A boxplot (Tukey) shows the box from the 25th to the 75th percentile with the median as a line, and whiskers (dashed lines) that extend to the furthest point within 1.5 times the IQR of the box. Data beyond the whiskers is drawn as single points, often considered outliers.
- Morettin & Bussab give the fences as LI = q1 - 1.5 dq and LS = q3 + 1.5 dq and justify them with the normal curve: the fences sit at +/-2.698, so about 99.3% of normal data falls inside and only about 0.7% is flagged. They call points outside 'pontos exteriores': they may or may not be outliers.

**In your data**
- FATURAMENTO: box (Q1 to Q3): **1,098 to 2,477**
- median line: **1,500 (29% up the box)**
- fences: **-970 and 4,545**
- upper whisker ends at: **4,538**
- outside the fences: **14.4% (a normal curve: 0.7%)**
- *Chart: Boxplot of every numeric column.* Blue box: Q1 to Q3. Orange: median. Grey whisker and cap. Dashed red: fences. Green cross: the mean. Red diamond: the largest value. Axis compressed.

**Why it matters for the business:** For `FATURAMENTO` the mean (4,254) falls outside the box (above Q3 = 2,477), a quick visual signal that the average describes a line most orders never reach. The mean is outside the box in 3 of 9 columns.

**Insight:** A normal curve would put about 0.7% of the values outside the fences. `FATURAMENTO` has 14.4%, about 21 times that; 10.4% is even beyond 3 x IQR. The data are far from a bell curve, so the 1.5 x IQR rule is a prompt to look, not a verdict. The upper whisker stops at 4,538 while the largest value is 1,259,522.

**Watch out:** A zero IQR collapses the box into a line (as in a count column where most values are 1); then use percentiles or a bar chart.

### E3 - Comparing groups with boxplots

**Concepts:** Comparing groups with boxplots

**Source:** Practical Statistics, Ch.1, 'Key Ideas' (boxplots in side-by-side displays), p.26; Morettin & Bussab, §3.4, p.47

**What the book says**
- The book notes that boxplots are often used in side-by-side displays to compare distributions. Each box shows the centre (median line), the spread (box height) and the extremes (whiskers and points) of its group on one shared axis.

**In your data**
- comparison: **FATURAMENTO by TIPO_PAGAMENTO (3 groups)**
- highest / lowest median: **3.8 x**
- pairs of boxes that overlap: **100%**
- top group by median / by mean: **JUDICIAL / JUDICIAL**
- *Chart: Revenue per line by payment type.* One box per group, sorted by median. The label gives the group size. Axis compressed.

**Why it matters for the business:** Payment types differ by up to 3.8 times in their median revenue per line, yet all 3 boxes overlap: the groups are not clearly separate, so a ranking by one number would exaggerate the difference. Comparing the groups also needs their sizes (7,231 to 54,875 rows).

**Insight:** By record type (`TIPO_REGISTRO`) the picture is different: three of the 4 types have a revenue of exactly 0. They are not sales at all, so averaging revenue across them would drag every figure down. Over all 12 comparisons of this kind, boxes overlap in 67% of the pairs on average.

**Watch out:** Overlapping boxes mean the difference is small next to the natural spread; show the boxes, not just the medians.

### E4 - A boxplot fence already in the project

**Concepts:** Fences (lower and upper) and the 1.5 × IQR rule; Outlier

**Source:** The project's README (the churn section excludes a flagged outlier tier) and transform.calculate_churns_in_month

**What the book says**
- The book describes the 1.5 x IQR rule as a convention for flagging outliers in boxplots. The project's README says its Churns section excludes patients flagged as a posologia outlier by 'a single upper Tukey fence computed upstream per product'.
- *Note: This tests the claim on the stored tables: is `POSOLOGIA_SUSPEITA` the same as 'above Q3 + 1.5 x IQR of `DIAS_ESTOQUE`, computed inside each product'?*

**In your data**
- rows tested: **44,113**
- flagged as suspect: **9.5%**
- above the product's upper fence: **9.5%**
- precision / recall: **100% / 100%**
- *Chart: The flag against the per-product upper fence.* Share of rows flagged, above the fence, and both.

**Why it matters for the business:** The churn count the app shows excludes 9.5% of rows because of this flag. It is now verified: the flag is exactly a boxplot fence of days of stock within each product, so a patient is excluded when their stock days are unusually long for that product.

**Insight:** `POSOLOGIA_SUSPEITA` equals the upper Tukey fence of `DIAS_ESTOQUE` per `PRODUTO` with 100% precision and 100% recall: the rule is reproducible from the tables. It also means the outliers it removes are exactly those the boxplot would draw as points.

**Watch out:** This is a data-driven rule: a product with few rows has an unstable fence (the test only used products with 30 or more rows).

## F. Exploring the data distribution: frequency tables, histograms and density
*Practical Statistics, Chapter 1, pp.21-26 (mode, unimodal/multimodal, bandwidth and the bin rules are only touched on or outside your books)*

### F1 - Frequency table, bin and histogram

**Concepts:** Frequency table; Bin; Histogram

**Source:** Practical Statistics, Ch.1, 'Frequency Tables and Histograms', pp.22-23 (and Key Terms, p.21) | Morettin & Bussab, Ch.2, §2.2 'Distribuições de Frequências', pp.12-14, and §2.3 'Gráficos' (histograma), p.18

**What the book says**
- A frequency table divides the range of a variable into equally spaced segments and tells how many values fall within each segment (Practical Statistics, p.22). The book's example cuts the state populations into 10 bins: the range (36.7 million) divided by 10 gives bins 3.67 million wide, and the first bin alone holds 24 states.
- The book insists on keeping the empty bins: 'the fact that there are no values in those bins is useful information'. A histogram is the picture of the frequency table: bins on the x-axis, counts on the y-axis, equal widths, bars touching, empty bins drawn (p.23).
- Morettin & Bussab do the same for a continuous variable, calling the bins 'classes' written a ⊢ b (a included, b excluded). Grouping loses some information: you no longer see the individual values, only the class (p.13).
- *Note: 'Bin' is the word of Practical Statistics; Morettin & Bussab say 'classe'. Same thing: one segment of the range.*

**In your data**
- rows of revenue (FATURAMENTO): **72,674**
- 10 bins: width of each: **125,952**
- 10 bins: rows in the first bin: **99.7%**
- 10 bins: empty bins: **2 of 10**
- central range, 40 bins: fullest bin: **42.3%**
- *Chart: The book's recipe on your revenue: 10 equal bins over the full range.* Share of the rows in each bin. One bar holds almost everything; the other nine are too small to see (two are exactly empty).
- *Chart: The same variable on its central 1%-99% range, 40 bins.* Dropping the top 1% of the values (727 rows, up to 1,259,522) makes the shape visible.

**Why it matters for the business:** A sales line is worth a median of 1,500, but the largest is 1,259,522. Cut into 10 equal bins, 99.7% of the lines fall in the first bin (0 to 125,952) and the table says almost nothing about the lines a manager deals with every day. The frequency table needs the range chosen with care, not just divided by 10.

**Insight:** The frequency table is only as informative as its range. With the full range, the 2 empty bins say 'no revenue between 755,713 and 1,133,570' (true, and itself a finding: a few giant lines stretch the axis). On the central range the lines spread over 40 bins, with at most 42.3% of the rows in any bin.

**Watch out:** Equal-width bins are a convention, not a law of the data: always say which range and how many bins a table or histogram uses.

### F2 - Bin width and number of bins

**Concepts:** Bin width and number of bins

**Source:** Practical Statistics, Ch.1, p.23 ('the number of bins is up to the user'; 'experiment with different bin sizes') | Morettin & Bussab, Ch.2, §2.2, p.13 (5 to 15 classes of equal width) and Ch.2 §2.6 'Problema 10', p.27 (unequal classes)

**What the book says**
- Practical Statistics says the number of bins (or, equivalently, the bin size) is up to the user. It is useful to experiment with different bin sizes: if they are too large, important features of the distribution can be obscured; if too small, the result is too granular and the bigger picture is lost (p.23).
- Morettin & Bussab give the same warning and a rule of thumb: the choice of the intervals is arbitrary, a small number of classes loses information and a large number defeats the purpose of summarising; normally 5 to 15 classes of equal width are suggested (p.13).
- *Note: Sturges, square-root, Scott and Freedman-Diaconis are not in your two books; they are common rules of thumb that turn n and the spread into a number of bins (outside your books). They are starting points, not answers.*

**In your data**
- DIAS_ESTOQUE rows: **44,144**
- Sturges' rule: **17 bins**
- square-root rule: **211 bins**
- Freedman-Diaconis, full range: **1,767 bins**
- Freedman-Diaconis, central range: **174 bins**
- *Chart: Days of stock (DIAS_ESTOQUE), central range, 5 bins.* Too few bins: a smooth decline, every feature hidden.
- *Chart: The same, 20 bins.* Some structure appears.
- *Chart: The same, 80 bins.* Now each round number of days stands out as its own bar.
- *Chart: Number of bins each rule asks for, per numeric column.* Where the range is hundreds of times the IQR, the rules that use the range ask for thousands of bins.

**Why it matters for the business:** With 5 bins the days of stock of a treatment look like a smooth decline. With 80 bins they show the real planning units: 66% of the values are multiples of 30 days (chance alone would give 3.3%). A replenishment rule built on the smooth picture ('average stock 135 days') would miss that the values come in standard durations.

**Insight:** No single bin count is right: Sturges asks for 17 bins, the square-root rule for 211, and Freedman-Diaconis for 1,767 over the full range (it is driven by the IQR, so the 9,000-day maximum forces thousands of narrow bins) but 174 on the central range. The question decides: a few bins for the overall shape, many for peaks.

**Watch out:** Try at least three bin counts before drawing a conclusion; a feature that appears at only one bin count is probably noise.

### F3 - Skewness

**Concepts:** Skewness

**Source:** Practical Statistics, Ch.1, 'Statistical Moments' (box), p.24 | Morettin & Bussab, Ch.3, §3.4 (symmetry from the five numbers), p.45, and §3.5 'Gráficos de Simetria', p.51

**What the book says**
- In statistical theory location and variability are the first and second moments of a distribution; the third and fourth are skewness and kurtosis. Skewness refers to whether the data is skewed to larger or smaller values (p.24). The book adds that, generally, metrics are not used to measure skewness: it is discovered through visual displays such as the boxplot and the histogram.
- Morettin & Bussab test symmetry with the five numbers (smallest, Q1, median, Q3, largest): in a symmetric distribution the median is about as far from the smallest as from the largest, and from Q1 as from Q3 (p.45). If the quantiles on the right are farther from the median than those on the left, the data are skewed to the right; this typically happens with positive data (p.51).
- *Note: The skewness number used here is the standard third-moment coefficient (pandas' skew); 0 means symmetric, positive means a long right tail. It is a summary of what the histogram shows, not a replacement for it.*

**In your data**
- right-skewed columns: **9 of 9**
- FATURAMENTO skewness: **23.5**
- FATURAMENTO mean / median: **4,254 / 1,500**
- rows below the mean (FATURAMENTO): **84%**
- FATURAMENTO: upper / lower spread: **839**
- *Chart: Revenue per line, central 1%-99%, with the median and the mean.* The median sits at the foot of the peak; the mean is dragged to the right by the long tail.
- *Chart: Skewness of every numeric column.* Blue: all rows. Orange: only the central 1%-99%. Compressed axis. Every column leans right; most of the number comes from the top 1% of the rows.

**Why it matters for the business:** For revenue per line the mean (4,254) is 2.8 times the median (1,500) and 84% of the lines are below it. 'Average revenue per line' is therefore a value that most lines never reach: a target or a bonus built on it will look unreachable, while the median describes the typical line.

**Insight:** All 9 numeric columns lean right, as money and quantities do. The skewness number itself is fragile: for revenue it is 23.5 on all rows and 4.6 once the top 1% (727 lines) is set aside; for quantity it falls from 112 to 4.4. A handful of lines produce most of the 'skewness', which is why the book prefers to look at the picture.

**Watch out:** Do not average a right-skewed column and call it typical; if you must use the mean (for a total), say that a few large values drive it.

### F4 - Mode, unimodal and multimodal

**Concepts:** Mode; Unimodal; Bimodal; Multimodal

**Source:** Morettin & Bussab, Ch.3, §3.1 'Medidas de Posição' (moda, bimodal, trimodal), p.35 | Practical Statistics, Ch.1, histogram and density plot figures, pp.23-25 (peaks are read from them)

**What the book says**
- Morettin & Bussab define the mode as the most frequent value of the observations. In some cases there is more than one mode, and the distribution can be bimodal, trimodal and so on (p.35).
- Practical Statistics does not define the mode; it shows distributions through the histogram and the density plot, where peaks are seen at a glance (pp.23-25).
- *Note: Outside your two books: the words 'unimodal' and 'multimodal', and my rule for counting peaks: a peak of the density curve must reach 5% of the highest peak, and two peaks count as separate only if the dip between them is deeper than 20%.*

**In your data**
- DIAS_ESTOQUE: most frequent value: **60 days (14.8%)**
- its five most frequent values: **48%**
- peaks of its density: **8**
- multiples of 30 days: **66% (chance 3.3%)**
- columns with 2+ peaks: **8 of 9**
- *Chart: Days of stock: histogram (80 bins) and density curve.* Most peaks of the curve sit on or near a round number of days.
- *Chart: Days of stock: the five most frequent values.* Share of the rows that hold exactly this value of days.
- *Chart: Revenue: share of rows above the valley between its two main peaks, by record type.* The valley sits at 1,744; the peaks at 1,221 and 1,962. The record type that never goes above it holds the zero-revenue rows.

**Why it matters for the business:** Days of stock is not a smooth quantity: 66% of the values are multiples of 30 days, and the single most frequent value is 60 days (14.8% of the rows). The values come in standard durations, so a planner should talk about 'the 30, 60 and 90-day groups' rather than an average of 135 days that almost nobody has.

**Insight:** 6 of 9 numeric columns have one value holding at least 20% of the rows (for the quantity per line in the small sales table, 95% of the rows are exactly 1 unit), and 8 have two or more peaks. When a second peak appears, look for a category that explains it: in revenue, the DOACAO records never rise above the valley (100% of them have revenue exactly 0, which is the peak at zero) while 45% of the VENDA records do.

**Watch out:** A mode is only a peak of what you chose to plot: with the wrong bins or bandwidth, modes appear or disappear (see the last two lessons).

### F5 - Density scale

**Concepts:** Density scale

**Source:** Practical Statistics, Ch.1, 'Density Plots and Estimates', p.25 (y-axis as proportion; area under the curve = 1) | Morettin & Bussab, Ch.2, §2.3, p.18 (densidade de frequência fi/Δi; area = 1) and 'Problema 10', p.27 (classes of unequal width)

**What the book says**
- Practical Statistics: a key distinction from the histogram is the scale of the y-axis. A density plot corresponds to plotting the histogram as a proportion rather than counts. The total area under the density curve is 1, and instead of counts in bins you calculate areas under the curve between two points, which give the proportion of the distribution lying between them (p.25).
- Morettin & Bussab build the histogram so that the area of each rectangle is proportional to the frequency: the height is fi/Δi (frequency divided by the class width), the 'densidade de frequência', and the total area is 1 (p.18). Their Problem 10 shows why this matters when classes have different widths: a superficial look at the counts suggests a peak that disappears once you divide by the width (p.27).
- *Note: With equal bins, counts and density have exactly the same shape; only the y-axis units change. The density scale is essential when bins have unequal widths.*

**In your data**
- painel: DIAS_SEM_VISITA_NUM rows: **5,399**
- bin 1 density: **1.78% of rows per day**
- bin 3 density: **0.12% of rows per day**
- denser: **14.4 x**
- equal bins: sum of bar areas: **1.000**
- *Chart: Days without a visit, cut at its percentiles: bars as counts.* Bins 1 to 3 each hold about the same share of the rows (23%, 26%, 26%), so they look alike.
- *Chart: The same bins as density (% of rows per day).* Area, not height, is the share of the rows. Bin 1 (1 to 14 days) is 14.4 times denser than bin 3 (30 to 240 days).

**Why it matters for the business:** Days without a visit measures how long each row of the panel has gone without being visited. 49% of the rows were visited in the last 30 days and 25% have gone more than 240 days. Read as counts, the wide 30 to 240 day bin looks as big as the first two; read as density, the rows are far more concentrated in the first month.

**Insight:** Counts are honest only when bins are equal. With unequal bins, three bars with the same share (23%, 26%, 26%) hide a 14-fold difference in density. For equal bins the two scales agree: the 10 bars of the 10-bin histogram of this column have areas that add up to 1.000.

**Watch out:** When a chart has bars of different widths, check whether the height is a count or a density before comparing bars.

### F6 - Density plot and kernel density estimate (KDE)

**Concepts:** Density plot; Kernel density estimate (KDE)

**Source:** Practical Statistics, Ch.1, Key Terms p.21 and 'Density Plots and Estimates', pp.24-26 | Morettin & Bussab, Ch.2, 'Problema 12' (histograma alisado), pp.28-29

**What the book says**
- A density plot shows the distribution of the data values as a continuous line; it can be thought of as a smoothed histogram, although it is typically computed directly from the data through a kernel density estimate (p.24). The book draws the estimate over a histogram (Figure 1-4) and notes that for many data science problems it suffices to use the base functions of the software (p.26).
- Morettin & Bussab describe the same idea as a limit: with enough observations, shrinking the class widths makes the histogram less irregular until it becomes a smooth curve (the 'histograma alisado'); where the curve is higher there is a greater density of observations (p.29).
- *Note: Outside your two books: how a kernel density estimate is computed. Put one small bell curve (a Gaussian 'kernel') on every value and average them; the width of the bells is the bandwidth. It is drawn here on the central 1%-99% range.*

**In your data**
- FATURAMENTO: bandwidth h: **89.10**
- area under the curve (plotted range): **0.982**
- density below the minimum (0): **1.8%**
- columns with density below their minimum: **8 of 9**
- *Chart: Revenue per line: histogram as density, and the kernel density estimate.* Grey bars: histogram (40 bins) on the density scale. Line: the smooth estimate. Their areas both add up to about 1.
- *Chart: Share of the density that falls below the smallest value the column ever takes.* Columns with few distinct values or counts. A smooth curve gives probability to values that cannot exist.

**Why it matters for the business:** A smooth revenue curve is easier to read than 40 bars, and it overlays groups well, but it is an estimate, not the data: it says 1.8% of sales lines have negative revenue, which never happens (the minimum is 0.00). For the quantity per line in the small sales table it says 48% of the lines are below 1 unit.

**Insight:** A density curve is a good display for a measured, continuous quantity (revenue, days) and a poor one for counts and columns with few distinct values: it smears the bars of 1, 2, 3 units into hills and spills probability beyond the possible range. For those columns, a bar chart of the values is the honest picture.

**Watch out:** Always read a density plot together with the range of the data: the curve extends where there are no rows.

### F7 - Bandwidth

**Concepts:** Bandwidth

**Source:** Practical Statistics, Ch.1, p.25 (bw_method controls the smoothness of the density curve) and 'Further Reading' on kernels and bandwidth, p.26

**What the book says**
- The book shows that pandas' density method takes an argument (bw_method) 'to control the smoothness of the density curve' (p.25) and points to a resource on the effect of choosing different kernels and bandwidth on kernel density estimates (p.26). It does not define bandwidth beyond this.
- *Note: Outside your two books: the definition and the rule below. The bandwidth is the width of the bell curve placed on every value. Silverman's rule of thumb sets it to 0.9 x min(standard deviation, IQR / 1.34) x n^(-1/5). 'h / 4' and '4 x h' are only here to show what happens when it is too small or too large.*

**In your data**
- DIAS_ESTOQUE: Silverman bandwidth h: **7.14 days**
- peaks with h / 4: **19**
- peaks with h: **8**
- peaks with 4 x h: **2**
- *Chart: Days of stock: the same data at three bandwidths.* Orange: h / 4 (too small, jagged). Blue: Silverman h. Green: 4 x h (too large, one hump). Grey bars: histogram, 40 bins.
- *Chart: Number of peaks of every numeric column at the three bandwidths.* The same data give very different numbers of peaks depending on the smoothing.

**Why it matters for the business:** How many standard stock durations does the business really have? With a small bandwidth the density of days of stock has 19 peaks, with the rule of thumb 8, with a large one 2. The honest answer comes from the histogram with 80 bins (round numbers of days) and not from the curve alone.

**Insight:** The bandwidth plays for the density the role the number of bins plays for the histogram: too small invents peaks out of noise, too large erases real ones. Both look equally smooth on a chart. A peak you can trust survives two or three bandwidths and shows up in the histogram too.

**Watch out:** Never report a number of peaks without the bandwidth (or bin count) behind it.
