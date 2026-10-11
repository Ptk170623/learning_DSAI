# Part B - Rectangular data and tidy data

**Status:** concepts mapped; not learned yet with the chat-based method.

**Books:** Practical Statistics for Data Scientists, Ch.1 'Rectangular Data' and 'Nonrectangular Data Structures', pp.4-7. Tidy data, wide/long, data matrix and silent errors are outside both books (Wickham, 'Tidy Data', 2014; pandas documentation).

## Concept map and where each concept shows up in the project

| # | Concept | In the project | Understood on |
|---|---|---|---|
| 1 | Rectangular data | Every table the app loads is one rectangle: a pandas DataFrame with the same columns on every row. | |
| 2 | Data frame | All the calculations in `transform.py` take and return DataFrames. | |
| 3 | Feature | Block, payment type, sale type, client effort and product are the features the pages filter and group by. | |
| 4 | Outcome | The metric being measured (revenue, units, number of new patients) is the outcome of each 660 table. | |
| 5 | Record | A sale line is identified by `ID_VENDA` + `PRODUTO` together; `ID_VENDA` alone repeats. The join with `tipo_venda` uses both columns. | |
| 6 | Index | The month and doctor/product tables use an identifier (`crm_uf`, product) as the index of a pivot table, not the default 0, 1, 2. | |
| 7 | Nonrectangular data structures | Not applied yet. | |
| 8 | Data matrix | Not applied yet (no model is built in the app). | |
| 9 | Tidy data | `tipo_venda` is kept as its own table, one row per sale line, and joined to the sales table instead of repeating its columns. | |
| 10 | Silent error | Joins use the composite key so rows are not multiplied; flags are compared in their own stored type (see Part A). | |
| 11 | Dtype | See Part A: `PRIMEIRA_CLIENTE` (text) against `MARCA_PROPRIA` (number). | |
| 12 | Duplicate key | `ID_VENDA` is not unique on its own, which is why the merge keys are `ID_VENDA` and `PRODUTO`. | |
| 13 | Wide and long | The stored tables are long (a row per sale line). The doctor and product tables are pivoted to wide, one column per month (`pivot_table` in `transform.py`). | |

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
