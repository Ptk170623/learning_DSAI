# Study pack: practice results from the learning_DSAI project

One file for a tutor chat. It holds the five reports produced on the project's real (anonymized) data.
No code is needed: every number below came from running the analysis on the five tables
`vendas_660`, `tipo_venda`, `carteira_pacientes`, `painel` and `vendas_1015` (the `closeup` table is left out).

Part A covers: structured data, variable, observation, data type, numeric (continuous, discrete),
categorical (nominal, binary, ordinal), level, stored type vs. statistical type, identifier.
Part B covers: rectangular data, data frame, feature, outcome, record, index, nonrectangular structures,
data matrix, tidy data, silent error, dtype, duplicate key, wide and long.
Part C covers: estimate of location, sample, estimate, outlier, robust, mean, trimmed mean, median,
weight, weighted mean, weighted median, mean vs. median (when to use each).
Part D covers: variability, deviation, variance, standard deviation, mean absolute deviation, MAD (median
absolute deviation), range, order statistics, percentile, quartile, IQR, degrees of freedom and n - 1, bias,
robust, outlier.
Part E covers: percentile, median, quartiles (Q1, Q2, Q3), IQR, boxplot (box, median line), whisker and cap,
fences (lower and upper) and the 1.5 x IQR rule, outlier, robust (mean vs. median / IQR), comparing groups with
boxplots, quartile calculation (position and interpolation).
Part F covers: frequency table, bin, histogram, bin width and number of bins, skewness, unimodal and multimodal (mode),
density scale, density plot and kernel density estimate (KDE), bandwidth.

---

# PART A - Data types profile

# RESULT REPORT - Data types profile

**PAGE:** "Data types profile" in the Streamlit app (sidebar navigation). Run: `streamlit run data_app_gestao.py`. Code: `data_types_profile.py` (analysis) + `page_data_types_profile` in `data_app_gestao.py` (UI). Only counts, percentages and aggregates appear - no raw rows, no values of identifier / personal columns.

### 1. Structured data, variable, observation
- **WHERE:** 5 tables: vendas_660, tipo_venda, carteira_pacientes, painel, vendas_1015
- **WHAT I RAN:** profile_table() on every table loaded by transform._ler (shape, empty cells, duplicated rows).
- **WHAT IT SHOWED:**
  - vendas_660: 72,674 observations (rows) x 24 variables (columns), 7.6% empty cells, 0 fully duplicated rows
  - tipo_venda: 72,674 observations (rows) x 5 variables (columns), 0.6% empty cells, 0 fully duplicated rows
  - carteira_pacientes: 70,581 observations (rows) x 11 variables (columns), 13.0% empty cells, 0 fully duplicated rows
  - painel: 6,129 observations (rows) x 11 variables (columns), 7.7% empty cells, 0 fully duplicated rows
  - vendas_1015: 347 observations (rows) x 16 variables (columns), 4.5% empty cells, 29 fully duplicated rows
- **WHAT IT MEANS FOR THE PROJECT:** All 5 tables are structured data: a fixed set of named columns and one row per record. Together 222,405 rows and 67 columns. What one row stands for (its grain) is not declared in the data - it is read from the identifier columns (block 5).
- **PROBLEMS OR SURPRISES:**
  - vendas_1015 has 29 fully duplicated rows

### 2. Data type and stored vs. statistical type
- **WHERE:** every column of every table
- **WHAT I RAN:** dtype read per column, statistical type decided by rule (see the 'why' column), the two compared.
- **WHAT IT SHOWED:**
  - stored types: str x42, datetime64[us] x10, float64 x9, int64 x3, object x2, bool x1
  - statistical types: continuous x5, discrete x4, nominal x27, binary x7, identifier x11, other (date) x12, other (text) x1
- **WHAT IT MEANS FOR THE PROJECT:** The dtype says how a value is stored; the statistical type says what it means. Code that trusts the dtype is only right where the two agree.
- **PROBLEMS OR SURPRISES:**
  - 8 of 67 columns have a misleading stored type: date stored as text x1; flag stored as number x1; flag stored as text digits x3; ID / code stored as number x1; integers stored as float x1; date / period stored as number x1

### 3. Numeric: continuous and discrete
- **WHERE:** `vendas_660.FATURAMENTO`, `vendas_660.QUANTIDADE`, `carteira_pacientes.DIAS_ESTOQUE`, `painel.DIAS_SEM_VISITA_NUM`, `vendas_1015.PRODUTO_MG`, `vendas_1015.QTD`, `vendas_1015.VALOR_REPRESENTANTE`, `vendas_1015.VALOR_VENDA` ...
- **WHAT I RAN:** numeric summary (quartiles, mean, zeros, skew) and a histogram per numeric column.
- **WHAT IT SHOWED:**
  - `vendas_660.FATURAMENTO` (continuous): median 1,500, range 0 to 1,259,522, 3% zeros, skew 23.5
  - `vendas_660.QUANTIDADE` (discrete): median 2, range 1 to 3,001, 0% zeros, skew 111.7
  - `carteira_pacientes.DIAS_ESTOQUE` (continuous): median 90, range 1 to 9,000, 0% zeros, skew 13.6
  - `painel.DIAS_SEM_VISITA_NUM` (discrete): median 30, range 1 to 941, 0% zeros, skew 1.7
  - `vendas_1015.PRODUTO_MG` (discrete): median 100, range 50 to 200, 0% zeros, skew 0.5
  - `vendas_1015.QTD` (discrete): median 1, range 1 to 40, 0% zeros, skew 16.5
  - `vendas_1015.VALOR_REPRESENTANTE` (continuous): median 510, range 290 to 40,000, 0% zeros, skew 16.3
  - `vendas_1015.VALOR_VENDA` (continuous): median 690, range 1 to 55,600, 0% zeros, skew 16.1
  - `vendas_1015.VALOR_COMISSAO` (continuous): median 15.30, range 8.70 to 4,000, 0% zeros, skew 15.8
- **WHAT IT MEANS FOR THE PROJECT:** Continuous measures (decimals, many values) can be averaged and binned; discrete counts (whole numbers) are summed and compared exactly, and are never fractional.
- **PROBLEMS OR SURPRISES:**
  - right-skewed (skew > 2): `vendas_660.FATURAMENTO`, `vendas_660.QUANTIDADE`, `carteira_pacientes.DIAS_ESTOQUE`, `vendas_1015.QTD`, `vendas_1015.VALOR_REPRESENTANTE`, `vendas_1015.VALOR_VENDA`, `vendas_1015.VALOR_COMISSAO` - mean is pulled up, prefer the median
  - `painel.DIAS_SEM_VISITA_NUM` is whole numbers stored as float

### 4. Categorical: nominal, binary, ordinal and level
- **WHERE:** 34 columns
- **WHAT I RAN:** level counts per categorical column (levels listed only for non-personal columns with <= 50 levels); ordinal order is an assumption and is shown.
- **WHAT IT SHOWED:**
  - nominal: 27 column(s)
  - binary: 7 column(s)
  - ordinal: 0 column(s)
  - `vendas_660.CLIENTE` (nominal): 22,131 levels, largest level 0.6%
  - `vendas_660.NOME_MEDICO` (nominal): 5,056 levels, largest level 1.7%
  - `vendas_660.NOME_BLOCO` (nominal): 68 levels, largest level 10.4%
  - `vendas_660.PRODUTO` (nominal): 492 levels, largest level 21.9%
  - `vendas_660.PRINCIPIO_ATIVO` (nominal): 226 levels, largest level 49.6%
  - `vendas_660.MARCA_PROPRIA` (binary): 2 levels, largest level 89.8%
  - `vendas_660.PRIMEIRA_CLIENTE` (binary): 2 levels, largest level 69.9%
  - `vendas_660.PRIMEIRA_MEDICO` (binary): 2 levels, largest level 93.4%
  - `vendas_660.ESFORCO_CLIENTE` (binary): 2 levels, largest level 55.5%
  - `vendas_660.TIPO_PAGAMENTO` (nominal): 3 levels, largest level 75.5%
  - `vendas_660.TIPO_REGISTRO` (nominal): 4 levels, largest level 97.1%
  - `vendas_660.VENDEDOR` (nominal): 73 levels, largest level 6.9%
- **WHAT IT MEANS FOR THE PROJECT:** A level is one distinct value of a categorical variable. Nominal levels have no order, binary has exactly two, ordinal levels have an order that must be stored explicitly.
- **PROBLEMS OR SURPRISES:**
  - more than 50 levels: `vendas_660.CLIENTE` (22,131), `vendas_660.NOME_MEDICO` (5,056), `vendas_660.NOME_BLOCO` (68), `vendas_660.PRODUTO` (492), `vendas_660.PRINCIPIO_ATIVO` (226), `vendas_660.VENDEDOR` (73), `vendas_660.BLOCO_NUM` (68), `tipo_venda.BLOCO_NUM` (68), `tipo_venda.PRODUTO` (492), `carteira_pacientes.PRODUTO` (440), `painel.CIDADE` (222), `painel.BAIRRO` (1,097), `vendas_1015.MEDICO` (110)

### 5. Identifier
- **WHERE:** `vendas_660.ID_VENDA`, `vendas_660.ID_CLIENTE`, `vendas_660.ID_MEDICO`, `vendas_660.CRM - UF`, `tipo_venda.ID_VENDA`, `carteira_pacientes.ID_PACIENTE`, `carteira_pacientes.ID_VENDA`, `carteira_pacientes.ID_MEDICO`, `carteira_pacientes.ID_FUNCIONARIO`, `painel.CRM - UF` ...
- **WHAT I RAN:** unique %, repeated values and stored type of every identifier column (values never shown).
- **WHAT IT SHOWED:**
  - `vendas_660.ID_VENDA`: 97.6% unique, 1,755 repeated, stored str (key-like name)
  - `vendas_660.ID_CLIENTE`: 30.5% unique, 50,543 repeated, stored str (key-like name)
  - `vendas_660.ID_MEDICO`: 7.2% unique, 66,418 repeated, stored str (key-like name)
  - `vendas_660.CRM - UF`: 7.1% unique, 65,781 repeated, stored str (key-like name)
  - `tipo_venda.ID_VENDA`: 97.6% unique, 1,755 repeated, stored str (key-like name)
  - `carteira_pacientes.ID_PACIENTE`: 30.2% unique, 49,292 repeated, stored str (key-like name)
  - `carteira_pacientes.ID_VENDA`: 97.9% unique, 1,497 repeated, stored str (key-like name)
  - `carteira_pacientes.ID_MEDICO`: 7.1% unique, 64,617 repeated, stored str (key-like name)
  - `carteira_pacientes.ID_FUNCIONARIO`: 0.0% unique, 68,530 repeated, stored float64 (key-like name)
  - `painel.CRM - UF`: 98.3% unique, 102 repeated, stored str (key-like name)
  - `vendas_1015.CRM_UF`: 31.7% unique, 237 repeated, stored str (key-like name)
- **WHAT IT MEANS FOR THE PROJECT:** Identifiers name things; they are not quantities. Repeats mean a row is not one entity, so count distinct IDs and join on unique keys.
- **PROBLEMS OR SURPRISES:**
  - `carteira_pacientes.ID_FUNCIONARIO` is stored as a number, so it can be averaged
  - `vendas_660.ID_VENDA` is 97.6% unique but repeats (1,755 repeats) - a row is not one entity
  - `tipo_venda.ID_VENDA` is 97.6% unique but repeats (1,755 repeats) - a row is not one entity
  - `carteira_pacientes.ID_VENDA` is 97.9% unique but repeats (1,497 repeats) - a row is not one entity
  - `painel.CRM - UF` is 98.3% unique but repeats (102 repeats) - a row is not one entity
  - 7 other identifier column(s) repeat by design (foreign keys to a client / doctor / employee / patient)

## MISMATCH LIST (column, stored type -> statistical type, why)
- `vendas_660.DATA_ORCAMENTO`: str -> other (date), date stored as text (text that matches a date pattern (>= 98%))
- `vendas_660.MARCA_PROPRIA`: float64 -> binary, flag stored as number (exactly 2 distinct values)
- `vendas_660.PRIMEIRA_CLIENTE`: str -> binary, flag stored as text digits (exactly 2 distinct values (digits))
- `vendas_660.PRIMEIRA_MEDICO`: str -> binary, flag stored as text digits (exactly 2 distinct values (digits))
- `vendas_660.ESFORCO_CLIENTE`: str -> binary, flag stored as text digits (exactly 2 distinct values (digits))
- `carteira_pacientes.ID_FUNCIONARIO`: float64 -> identifier, ID / code stored as number (key-like name)
- `painel.DIAS_SEM_VISITA_NUM`: float64 -> discrete, integers stored as float (whole numbers, name suggests a count)
- `vendas_1015.PERIODO_ORIGEM_ESPECIALISTA_FARMA`: float64 -> other (date), date / period stored as number (integer values shaped like YYYYMM calendar codes)
## TOP INSIGHTS
1. **Stored type misleads in many columns** - 8 of 67 columns (12%) have a stored type that misleads: 1 date stored as text; 1 flag stored as number; 3 flag stored as text digits; 1 ID / code stored as number; 1 integers stored as float; 1 date / period stored as number. Risk: Code that trusts the dtype (sum, mean, sort, ==, joins) silently computes the wrong thing on these columns. Fix: Cast each one at the loading boundary (transform._ler) to its statistical type: string for IDs/codes, boolean for flags, datetime for dates, numeric for numbers.
2. **Identifiers / codes stored as numbers** - 1 column(s) hold IDs or codes as numbers: `carteira_pacientes.ID_FUNCIONARIO`. Risk: An ID can be averaged, summed or binned like a measure, and numeric IDs lose leading zeros and become float when a value is missing. Fix: Store them as string/category and exclude them from numeric summaries.
3. **Binary flags not stored as booleans** - 4 of 7 binary columns are numbers or digit-text: `vendas_660.MARCA_PROPRIA`, `vendas_660.PRIMEIRA_CLIENTE`, `vendas_660.PRIMEIRA_MEDICO`, `vendas_660.ESFORCO_CLIENTE`. Risk: A flag can be averaged or summed as if it were a quantity, and flag columns of the same kind end up in different types (int 1 vs text "1"), so a comparison with the wrong type silently matches nothing. Fix: Convert to boolean (or one agreed type) once, at load time, and compare against True/False.
4. **Dates not stored as dates** - 2 of 12 date columns are text or numbers (period codes like 202607): `vendas_660.DATA_ORCAMENTO`, `vendas_1015.PERIODO_ORIGEM_ESPECIALISTA_FARMA`. Risk: No date arithmetic or month grouping; text sorts wrongly if formats differ, and a period code stored as a float can be averaged or shown as 202,608.2. Fix: Parse to datetime in the loader (as _DATE_COLUMNS already does for known dates); turn YYYYMM codes into the first day of the month.
5. **Row-level identifiers that still repeat** - 4 identifier column(s) are 90%+ unique yet repeat: `vendas_660.ID_VENDA`, `tipo_venda.ID_VENDA`, `carteira_pacientes.ID_VENDA`, `painel.CRM - UF` - e.g. `vendas_660.ID_VENDA` is 97.6% unique with 1,755 repeats (one value up to 12 times). The other 7 identifier column(s) repeat by design (they point to a client, doctor or employee shared by many rows). Risk: A row is not one entity: counting rows instead of distinct IDs overstates, and a merge on this key alone fans out and inflates totals. Fix: Count distinct IDs; join on the composite key that is unique (and assert uniqueness after merging).
6. **Fully duplicated rows** - 1 of 5 tables contain exact duplicate rows; worst: `vendas_1015` with 29 of 347 rows (8.4%). Risk: Observations are counted (and their values summed) more than once, inflating totals and counts. Fix: Check whether the repeat is a real second event; if not, drop exact duplicates in the loader and add a row key so the grain is explicit.
7. **Extreme right-skew and outliers in numeric columns** - 6 numeric column(s) have a maximum over 50x their median and skew above 5; e.g. `vendas_660.QUANTIDADE` median 2.00, mean 3.39, max 3,001; `vendas_660.FATURAMENTO` median 1,500, mean 4,254, max 1,259,522; `vendas_1015.VALOR_COMISSAO` median 15.30, mean 55.74, max 4,000. Risk: A handful of rows dominate sums and means (or are entry errors, such as days of stock measured in decades), so averages and charts describe the outliers, not the typical row. Fix: Inspect the largest rows, report median / trimmed mean next to the mean, and use a log scale.
8. **Columns with a lot of missing data** - 8 column(s) are 20%+ missing, worst: `vendas_660.TIPO_FONTE` (88%). Risk: Averages and rates cover only the filled rows; a blank can mean 'none' or 'unknown'. Fix: Document what blank means per column and fill it explicitly (as the project does with '(not informed)').

---

# PART B - Rectangular data and tidy data

# RESULT REPORT - Rectangular data and tidy data

**PAGE:** "Rectangular data and tidy data" in the Streamlit app (sidebar navigation). Run: `streamlit run data_app_gestao.py`. Code: `tidy_rectangular.py` (analysis) + `page_rectangular_tidy` in `data_app_gestao.py` (UI). Only counts, percentages, formats and aggregates appear - no raw rows or identifier values.

### 1. Rectangular data, data frame, record, index
- **WHERE:** 5 tables: vendas_660, tipo_venda, carteira_pacientes, painel, vendas_1015
- **WHAT I RAN:** shape, index type, key search (smallest unique column set, up to 3 columns), empty cells, duplicated rows.
- **WHAT IT SHOWED:**
  - vendas_660: 72,674 records x 24 columns, index RangeIndex (default 0..n-1, no meaning), unique key: ID_VENDA, PRODUTO, 7.6% empty cells, 0 duplicated rows
  - tipo_venda: 72,674 records x 5 columns, index RangeIndex (default 0..n-1, no meaning), unique key: ID_VENDA, PRODUTO, 0.6% empty cells, 0 duplicated rows
  - carteira_pacientes: 70,581 records x 11 columns, index RangeIndex (default 0..n-1, no meaning), unique key: ID_VENDA, PRODUTO, 13.0% empty cells, 0 duplicated rows
  - painel: 6,129 records x 11 columns, index RangeIndex (default 0..n-1, no meaning), unique key: NOME_MEDICO, NOME_BLOCO (4 equally small alternatives), 7.7% empty cells, 0 duplicated rows
  - vendas_1015: 347 records x 16 columns, index RangeIndex (default 0..n-1, no meaning), unique key: NONE found, 4.5% empty cells, 29 duplicated rows
- **WHAT IT MEANS FOR THE PROJECT:** Every table is rectangular: the same columns on every row, one record per row, held as a pandas data frame. A record is whatever the key says one row is - not necessarily the sale, client or doctor.
- **PROBLEMS OR SURPRISES:**
  - vendas_1015: no unique key found - rows can repeat
  - vendas_660: record = ID_VENDA, PRODUTO (a single ID is not enough)
  - tipo_venda: record = ID_VENDA, PRODUTO (a single ID is not enough)
  - carteira_pacientes: record = ID_VENDA, PRODUTO (a single ID is not enough)
  - painel: record = NOME_MEDICO, NOME_BLOCO (a single ID is not enough)
  - carteira_pacientes: 1.1% of rows are more than half empty

### 2. Feature and outcome
- **WHERE:** every column of every table
- **WHAT I RAN:** role per column: key (identifier), outcome (money / count measures, target-like flags), feature (the rest).
- **WHAT IT SHOWED:**
  - carteira_pacientes: 5 features, 2 outcome candidates, 4 keys
  - painel: 9 features, 1 outcome candidates, 1 keys
  - tipo_venda: 4 features, 0 outcome candidates, 1 keys
  - vendas_1015: 11 features, 4 outcome candidates, 1 keys
  - vendas_660: 18 features, 2 outcome candidates, 4 keys
  - outcome candidates: `vendas_660.FATURAMENTO`, `vendas_660.QUANTIDADE`, `carteira_pacientes.DIAS_ESTOQUE`, `carteira_pacientes.CHURN`, `painel.DIAS_SEM_VISITA_NUM`, `vendas_1015.QTD`, `vendas_1015.VALOR_REPRESENTANTE`, `vendas_1015.VALOR_VENDA`, `vendas_1015.VALOR_COMISSAO`
- **WHAT IT MEANS FOR THE PROJECT:** Features describe the record; outcomes are what you want to explain or total. This split is an assumption: it depends on the question, so the page shows it as assumed.
- **PROBLEMS OR SURPRISES:**
  - no outcome candidate found in tipo_venda

### 3. Nonrectangular structures and data matrix
- **WHERE:** vendas_660, tipo_venda, carteira_pacientes, painel, vendas_1015
- **WHAT I RAN:** numeric sub-matrix per table (size, gaps, rows lost by dropna), one-hot width, cells holding lists or several values, and the containers defined in transform.py.
- **WHAT IT SHOWED:**
  - vendas_660: numeric matrix 72,674 x 2, 0.0% empty, dropna would lose 0.0% of rows; with one-hot categoricals: 28,137 columns (2,044.8 M cells)
  - tipo_venda: numeric matrix 72,674 x 0, 0.0% empty, dropna would lose 0.0% of rows; with one-hot categoricals: 569 columns (41.4 M cells)
  - carteira_pacientes: numeric matrix 70,581 x 1, 37.5% empty, dropna would lose 37.5% of rows; with one-hot categoricals: 445 columns (31.4 M cells)
  - painel: numeric matrix 6,129 x 1, 11.9% empty, dropna would lose 11.9% of rows; with one-hot categoricals: 1,510 columns (9.3 M cells)
  - vendas_1015: numeric matrix 347 x 5, 0.0% empty, dropna would lose 0.0% of rows; with one-hot categoricals: 181 columns (0.1 M cells)
  - Data660: 4 data frames in one object (sales, sales_by_sale_type, sales_by_doctor, sales_by_product)
  - DataChurns: 1 data frame in one object (patients)
  - DataDoctorPotential: 4 data frames in one object (px_doctor, px_product, revenue_1015, panel)
- **WHAT IT MEANS FOR THE PROJECT:** A data matrix is the all-numeric table models use; categoricals must be encoded and gaps handled first. The project bundles several frames per analysis in dataclasses (nonrectangular as a whole) and reads rows from Supabase as a list of dicts before they become a frame.
- **PROBLEMS OR SURPRISES:**
  - none found by these rules

### 4. Tidy data
- **WHERE:** vendas_660, tipo_venda, carteira_pacientes, painel, vendas_1015
- **WHAT I RAN:** rule 1 (a variable per column): composite-format columns and wide column groups; rule 2 (an observation per row): key / duplicate checks; rule 3 (a table per unit): functional dependencies from identifier columns.
- **WHAT IT SHOWED:**
  - `vendas_660.ID_VENDA` (97.6% unique) determines 18 columns: DATA_VENDA, DATA_ORCAMENTO, DATA_ENTREGA, ID_CLIENTE, CLIENTE, ID_MEDICO, NOME_MEDICO, NOME_BLOCO, PRIMEIRA_CLIENTE, PRIMEIRA_MEDICO, ESFORCO_CLIENTE, TIPO_PAGAMENTO, TIPO_REGISTRO, ULTIMO_CONTATO, VENDEDOR, TIPO_FONTE, CRM - UF, BLOCO_NUM
  - `vendas_660.ID_CLIENTE` (30.5% unique) determines 1 column: CLIENTE
  - `vendas_660.ID_MEDICO` (7.2% unique) determines 4 columns: NOME_MEDICO, NOME_BLOCO, CRM - UF, BLOCO_NUM
  - `vendas_660.CRM - UF` (7.1% unique) determines 4 columns: ID_MEDICO, NOME_MEDICO, NOME_BLOCO, BLOCO_NUM
  - `tipo_venda.ID_VENDA` (97.6% unique) determines 3 columns: DATA_VENDA, BLOCO_NUM, TIPO_VENDA
  - `carteira_pacientes.ID_VENDA` (97.9% unique) determines 6 columns: ID_PACIENTE, DATA_VENDA, DATA_ENTREGA, ID_MEDICO, ID_FUNCIONARIO, CHURN
  - `carteira_pacientes.ID_MEDICO` (7.1% unique) determines 1 column: ID_FUNCIONARIO
  - `painel.CRM - UF` (98.3% unique) determines 1 column: NOME_MEDICO
  - `vendas_1015.CRM_UF` (31.7% unique) determines 4 columns: MEDICO, CADASTRO, BLOCO, BLOCO_NUM
- **WHAT IT MEANS FOR THE PROJECT:** A table is tidy when each variable is a column, each observation a row and each unit its own table. Repeated attributes of clients, doctors or products inside a sales table are the typical break.
- **PROBLEMS OR SURPRISES:**
  - 9 identifier columns carry attributes of another unit

### 5. Wide and long
- **WHERE:** vendas_660, tipo_venda, carteira_pacientes, painel, vendas_1015
- **WHAT I RAN:** wide-format column groups (same stem + period/number suffix) and a long-to-wide pivot (category x month) of the first outcome measure.
- **WHAT IT SHOWED:**
  - vendas_660: pivot of `FATURAMENTO` by `NOME_BLOCO` x month of `DATA_VENDA` = 68 x 121 (8,228 cells), 4,519 filled, 45% empty
  - painel: pivot of `DIAS_SEM_VISITA_NUM` by `NOME_BLOCO` x month of `DT_INCLUSAO` = 45 x 32 (1,440 cells), 610 filled, 58% empty
  - vendas_1015: pivot of `QTD` by `BLOCO` x month of `DATA` = 27 x 7 (189 cells), 65 filled, 66% empty
- **WHAT IT MEANS FOR THE PROJECT:** The stored tables are long (a row per event); the app pivots to wide month matrices to compute benchmarks. Wide is convenient for maths but hides gaps.
- **PROBLEMS OR SURPRISES:**
  - no wide-format columns in the stored tables

### 6. Dtype and duplicate key
- **WHERE:** vendas_660, tipo_venda, carteira_pacientes, painel, vendas_1015
- **WHAT I RAN:** dtype counts and memory per table, potential saving from category dtype, columns whose dtype misleads (from data_types_profile), duplicate-key counts of identifier columns.
- **WHAT IT SHOWED:**
  - vendas_660: 26.7 MB, category dtype could save 19.2 MB (72%)
  - tipo_venda: 6.2 MB, category dtype could save 4.3 MB (70%)
  - carteira_pacientes: 13.4 MB, category dtype could save 4.0 MB (30%)
  - painel: 1.0 MB, category dtype could save 0.6 MB (58%)
  - vendas_1015: 0.1 MB, category dtype could save 0.0 MB (56%)
  - `vendas_660.ID_VENDA`: 1,755 repeats, 97.6% unique
  - `tipo_venda.ID_VENDA`: 1,755 repeats, 97.6% unique
  - `carteira_pacientes.ID_VENDA`: 1,497 repeats, 97.9% unique
  - `painel.CRM - UF`: 102 repeats, 98.3% unique
- **WHAT IT MEANS FOR THE PROJECT:** The dtype decides what operations mean; a duplicate key decides how many rows a join returns.
- **PROBLEMS OR SURPRISES:**
  - `vendas_660.DATA_ORCAMENTO`: str -> other (date) (date stored as text)
  - `vendas_660.MARCA_PROPRIA`: float64 -> binary (flag stored as number)
  - `vendas_660.PRIMEIRA_CLIENTE`: str -> binary (flag stored as text digits)
  - `vendas_660.PRIMEIRA_MEDICO`: str -> binary (flag stored as text digits)
  - `vendas_660.ESFORCO_CLIENTE`: str -> binary (flag stored as text digits)
  - `carteira_pacientes.ID_FUNCIONARIO`: float64 -> identifier (ID / code stored as number)
  - `painel.DIAS_SEM_VISITA_NUM`: float64 -> discrete (integers stored as float)
  - `vendas_1015.PERIODO_ORIGEM_ESPECIALISTA_FARMA`: float64 -> other (date) (date / period stored as number)

### 7. Silent error
- **WHERE:** vendas_660, tipo_venda, carteira_pacientes, painel, vendas_1015
- **WHAT I RAN:** four checks that run without any error in pandas: merge fan-out, flag comparisons with the wrong dtype, groupby dropping missing keys, arithmetic on identifiers.
- **WHAT IT SHOWED:**
  - merge `vendas_660` with `tipo_venda` on `ID_VENDA` only: 76,742 rows instead of 72,674 (+5.60%), FATURAMENTO +3.92%
  - merge `carteira_pacientes` with `tipo_venda` on `ID_VENDA` only: 73,701 rows instead of 70,581 (+4.42%), DIAS_ESTOQUE +3.30%
  - merge `carteira_pacientes` with `vendas_660` on `ID_VENDA` only: 73,701 rows instead of 70,581 (+4.42%), DIAS_ESTOQUE +3.30%
  - merge `vendas_660` with `carteira_pacientes` on `ID_VENDA` only: 75,794 rows instead of 72,674 (+4.29%), FATURAMENTO +3.92%
  - merge `vendas_660` with `painel` on `CRM - UF` only: 73,487 rows instead of 72,674 (+1.12%), FATURAMENTO +1.26%
  - `vendas_660.MARCA_PROPRIA` (float64): `== 1` -> 64,766 rows, `== "1"` -> 0 rows, `== True` -> 64,766
  - `vendas_660.PRIMEIRA_CLIENTE` (str): `== 1` -> 0 rows, `== "1"` -> 21,858 rows, `== True` -> 0
  - `vendas_660.PRIMEIRA_MEDICO` (str): `== 1` -> 0 rows, `== "1"` -> 4,773 rows, `== True` -> 0
  - `vendas_660.ESFORCO_CLIENTE` (str): `== 1` -> 0 rows, `== "1"` -> 40,357 rows, `== True` -> 0
  - `carteira_pacientes.POSOLOGIA_SUSPEITA` (object): `== 1` -> 4,183 rows, `== "1"` -> 0 rows, `== True` -> 4,183
  - `carteira_pacientes.CHURN` (object): `== 1` -> 8,303 rows, `== "1"` -> 0 rows, `== True` -> 8,303
  - `vendas_1015.LINHA_VALIDA_VALOR_UNITARIO` (bool): `== 1` -> 210 rows, `== "1"` -> 0 rows, `== True` -> 210
  - groupby on `vendas_660.NOME_BLOCO` drops 1,504 rows (2.1%) and 18.6% of `FATURAMENTO`
  - groupby on `vendas_660.BLOCO_NUM` drops 1,504 rows (2.1%) and 18.6% of `FATURAMENTO`
  - groupby on `vendas_1015.BLOCO` drops 6 rows (1.7%) and 10.8% of `QTD`
  - groupby on `vendas_1015.BLOCO_NUM` drops 6 rows (1.7%) and 10.8% of `QTD`
  - groupby on `vendas_660.DATA_ENTREGA` drops 8,426 rows (11.6%) and 18.6% of `FATURAMENTO`
  - groupby on `vendas_660.ULTIMO_CONTATO` drops 51,044 rows (70.2%) and 75.5% of `FATURAMENTO`
  - groupby on `vendas_660.MARCA_PROPRIA` drops 549 rows (0.8%) and 2.3% of `FATURAMENTO`
  - groupby on `tipo_venda.BLOCO_NUM` drops 1,504 rows (2.1%)
  - ... and 8 more grouping-style columns with missing values (see the page)
  - `carteira_pacientes.ID_FUNCIONARIO` (float64) can be averaged: 68,538 values
- **WHAT IT MEANS FOR THE PROJECT:** A silent error returns a plausible number without any warning. Each line above is a real way for this project's data to produce one.
- **PROBLEMS OR SURPRISES:**
  - 5 merge(s) on a non-unique key change the row count
  - 16 grouping column(s) lose rows to missing keys

## TOP INSIGHTS

1. **The record is not the entity: keys are composite or missing** - 4 table(s) need a composite key (e.g. `vendas_660`: ID_VENDA, PRODUTO); 1 table(s) have no unique key at all (e.g. `vendas_1015` with 29 fully duplicated rows). Every table has a default index (RangeIndex), so the index carries no meaning. Risk: Counting rows as if each were a sale, client or doctor overstates; duplicated records double-count. Fix: Name the grain of every table (its key), assert uniqueness on load and keep the key as a column or the index.
2. **Silent error: merging on a near-unique key fans rows out** - Merging `vendas_660` with `tipo_venda` on `ID_VENDA` alone returns 76,742 rows instead of 72,674 (+4,068, 5.60%), inflating `FATURAMENTO` by 3.92%. Merging on the composite key (ID_VENDA, PRODUTO) keeps the row count. Risk: pandas raises no error: totals grow quietly and every downstream sum is wrong. Fix: Merge on the full key, pass validate="one_to_one" or "many_to_one", and compare row counts before and after.
3. **Silent error: a flag compared with the wrong dtype matches nothing** - The 7 binary columns are stored in different dtypes. `vendas_660.MARCA_PROPRIA` (float64): `== 1` finds 64,766 rows but `== "1"` finds 0. `vendas_660.PRIMEIRA_CLIENTE` (str): `== "1"` finds 21,858 rows but `== 1` finds 0. Risk: A filter written for the other dtype returns zero rows and pandas raises nothing. Fix: Store every flag as boolean and compare with True / False, or cast once at load time.
4. **Silent error: groupby drops rows whose key is missing** - 16 grouping-style columns contain missing values; grouping by `vendas_660.NOME_BLOCO` drops 1,504 rows (2.1%) and 18.6% of `FATURAMENTO` from the result. Risk: Group totals no longer add up to the table total, and nothing says why. Fix: Fill missing keys with an explicit label before grouping (as transform.py does with '(not informed)') or use dropna=False.
5. **Tidy rule broken: one table mixes several observational units** - 9 identifier column(s) fix other columns; e.g. in `vendas_660`, `ID_VENDA` determines 18 other column(s) (DATA_VENDA, DATA_ORCAMENTO, DATA_ENTREGA, ID_CLIENTE, CLIENTE, ID_MEDICO, NOME_MEDICO, NOME_BLOCO, PRIMEIRA_CLIENTE, PRIMEIRA_MEDICO, ESFORCO_CLIENTE, TIPO_PAGAMENTO, TIPO_REGISTRO, ULTIMO_CONTATO, VENDEDOR, TIPO_FONTE, CRM - UF, BLOCO_NUM) for 99%+ of its repeated values, so those are attributes of another unit repeated on every row. Risk: Attribute columns are stored once per row: they can disagree after an edit and make joins and counts wrong. Fix: Split the repeated attributes into their own table (one row per entity) and join them back when needed.
6. **Long versus wide: the wide shape is mostly empty** - `vendas_660` pivoted by `NOME_BLOCO` x month of `DATA_VENDA` is 68 x 121 = 8,228 cells, but only 4,519 hold data (45% empty). Risk: Missing months become NaN: means over a row ignore them, sums treat them as zero only if filled, and rolling windows quietly change length. Fix: Keep the data long and tidy, pivot only for the calculation, and fill gaps explicitly (0 or NaN) on purpose.
7. **Dtype: text stored as str is heavy and easy to misuse** - The 5 tables use 47 MB; storing their low-cardinality text columns as category would save about 28 MB (59%). 8 column(s) also carry a dtype that misleads (flags as text or float, an ID as float, dates as text or numbers). Risk: Memory grows with every copy, and a misleading dtype is what makes the silent errors above possible. Fix: Convert at the loading boundary (transform._ler): category for repeated text, boolean for flags, datetime for dates.
8. **Data matrix: missing numbers cost whole rows** - The numeric part of `carteira_pacientes` (1 column) has 37.5% empty cells, yet dropping every row with any gap would lose 37.5% of its 70,581 rows. One-hot encoding its categorical columns would widen the matrix to 445 columns (only 4 extra if you encode just the columns with 50 levels or fewer). Risk: A model or matrix routine that drops incomplete rows (or fills with 0) changes the sample without telling you. Fix: Decide per column whether a gap means 'none', 'unknown' or 'not applicable' before building any matrix.


---

# PART C - Estimates of location

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


---

# PART D - Estimates of variability

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


---

# PART E - Percentiles and boxplots

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

---

# PART F - Histograms and density

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
