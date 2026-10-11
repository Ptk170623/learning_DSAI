# Part A - Data types

**Status:** learned before this project, studied with flashcards. Recorded on 2026-10-11. Review pending.

**Books:** Practical Statistics for Data Scientists, Ch.1 'Elements of Structured Data', pp.2-4 (p.3 on data typing). Morettin & Bussab, Ch.2 §2.1 'Tipos de Variáveis', p.9.

## Concept map and where each concept shows up in the project

| # | Concept | In the project | Understood on |
|---|---|---|---|
| 1 | Structured data | All the project's data is tables read from Supabase (`vendas_660`, `tipo_venda`, `carteira_pacientes`, `painel`, `closeup`, `vendas_1015`) by `transform._ler`. |  Learned before (flashcards) |
| 2 | Variable (column) | Columns are stored in snake_case in Supabase and renamed back to their original names (`_REVERSE_RENAME` in `transform.py`). |  Learned before (flashcards) |
| 3 | Observation (row) | One row of `vendas_660` is one product line of one sale; the app counts and sums these rows. |  Learned before (flashcards) |
| 4 | Data type | Not applied yet. |  Learned before (flashcards) |
| 5 | Numeric (continuous, discrete) | Revenue (`FATURAMENTO`) is continuous and quantity (`QUANTIDADE`) discrete; the 660 metrics sum or average them. |  Learned before (flashcards) |
| 6 | Categorical (nominal, binary, ordinal) | `TIPO_REGISTRO`, `TIPO_PAGAMENTO` (the Payment Type filter), `TIPO_VENDA` (sale type) are nominal. `MARCA_PROPRIA` and `PRIMEIRA_CLIENTE` are binary flags. Client effort (Outside Panel / Never Visited / Visited / Visited Recently) is a category derived from a number, days without a visit, with a 90-day cutoff. |  Learned before (flashcards) |
| 7 | Level | The options of the Payment Type and Client Effort filters are the levels of those variables. |  Learned before (flashcards) |
| 8 | Stored type vs. statistical type | `PRIMEIRA_CLIENTE` is stored as text and compared with `"1"` (new patients); `MARCA_PROPRIA` is stored as a number and compared with `1` (`transform.py`, 660 base). Each flag is compared in its own type; comparing with the other type would return zero rows with no error. |  Learned before (flashcards) |
| 9 | Identifier | `ID_VENDA`, `ID_CLIENTE` and `CRM-UF` are used as keys and counted with `nunique` (distinct new patients), never averaged. |  Learned before (flashcards) |

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
