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
