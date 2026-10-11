# Part B - Rectangular data and tidy data

**Status:** learned before this project, studied with flashcards. Recorded on 2026-10-11. Review pending.

**Books:** Practical Statistics for Data Scientists, Ch.1 'Rectangular Data' and 'Nonrectangular Data Structures', pp.4-7. Tidy data, wide/long, data matrix and silent errors are outside both books (Wickham, 'Tidy Data', 2014; pandas documentation).

## Concept map and where each concept shows up in the project

| # | Concept | In the project | Understood on |
|---|---|---|---|
| 1 | Rectangular data | Every table the app loads is one rectangle: a pandas DataFrame with the same columns on every row. |  Learned before (flashcards) |
| 2 | Data frame | All the calculations in `transform.py` take and return DataFrames. |  Learned before (flashcards) |
| 3 | Feature | Block, payment type, sale type, client effort and product are the features the pages filter and group by. |  Learned before (flashcards) |
| 4 | Outcome | The metric being measured (revenue, units, number of new patients) is the outcome of each 660 table. |  Learned before (flashcards) |
| 5 | Record | A sale line is identified by `ID_VENDA` + `PRODUTO` together; `ID_VENDA` alone repeats. The join with `tipo_venda` uses both columns. |  Learned before (flashcards) |
| 6 | Index | The month and doctor/product tables use an identifier (`crm_uf`, product) as the index of a pivot table, not the default 0, 1, 2. |  Learned before (flashcards) |
| 7 | Nonrectangular data structures | Not applied yet. |  Learned before (flashcards) |
| 8 | Data matrix | Not applied yet (no model is built in the app). |  Learned before (flashcards) |
| 9 | Tidy data | `tipo_venda` is kept as its own table, one row per sale line, and joined to the sales table instead of repeating its columns. |  Learned before (flashcards) |
| 10 | Silent error | Joins use the composite key so rows are not multiplied; flags are compared in their own stored type (see Part A). |  Learned before (flashcards) |
| 11 | Dtype | See Part A: `PRIMEIRA_CLIENTE` (text) against `MARCA_PROPRIA` (number). |  Learned before (flashcards) |
| 12 | Duplicate key | `ID_VENDA` is not unique on its own, which is why the merge keys are `ID_VENDA` and `PRODUTO`. |  Learned before (flashcards) |
| 13 | Wide and long | The stored tables are long (a row per sale line). The doctor and product tables are pivoted to wide, one column per month (`pivot_table` in `transform.py`). |  Learned before (flashcards) |

## Reviews

The part was learned before, so its review dates are not counted from a study day. The first review is proposed for 2026-11-10 (change it freely); fill in the next ones as they are scheduled and when they are done.

| # | Scheduled for | Done on | Notes |
|---|---|---|---|
| Review 1 | 2026-11-10 (proposed) | | |
| Review 2 | | | |
| Review 3 | | | |

## Still unclear

-

## Applied in the project (decided with the teacher)

-
