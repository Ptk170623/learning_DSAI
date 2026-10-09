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