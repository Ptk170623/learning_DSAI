# Study pack: practice results from the learning_DSAI project

One file for a tutor chat. It holds the two reports produced on the project's real (anonymized) data.
No code is needed: every number below came from running the analysis on the five tables
`vendas_660`, `tipo_venda`, `carteira_pacientes`, `painel` and `vendas_1015` (the `closeup` table is left out).

Part A covers: structured data, variable, observation, data type, numeric (continuous, discrete),
categorical (nominal, binary, ordinal), level, stored type vs. statistical type, identifier.
Part B covers: rectangular data, data frame, feature, outcome, record, index, nonrectangular structures,
data matrix, tidy data, silent error, dtype, duplicate key, wide and long.

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
