# Part A - Data types

**Status:** concepts mapped; not learned yet with the chat-based method.

**Books:** Practical Statistics for Data Scientists, Ch.1 'Elements of Structured Data', pp.2-4 (p.3 on data typing). Morettin & Bussab, Ch.2 §2.1 'Tipos de Variáveis', p.9.

## Concept map and where each concept shows up in the project

| # | Concept | In the project | Understood on |
|---|---|---|---|
| 1 | Structured data | All the project's data is tables read from Supabase (`vendas_660`, `tipo_venda`, `carteira_pacientes`, `painel`, `closeup`, `vendas_1015`) by `transform._ler`. | |
| 2 | Variable (column) | Columns are stored in snake_case in Supabase and renamed back to their original names (`_REVERSE_RENAME` in `transform.py`). | |
| 3 | Observation (row) | One row of `vendas_660` is one product line of one sale; the app counts and sums these rows. | |
| 4 | Data type | Not applied yet. | |
| 5 | Numeric (continuous, discrete) | Revenue (`FATURAMENTO`) is continuous and quantity (`QUANTIDADE`) discrete; the 660 metrics sum or average them. | |
| 6 | Categorical (nominal, binary, ordinal) | `TIPO_REGISTRO`, `TIPO_PAGAMENTO` (the Payment Type filter), `TIPO_VENDA` (sale type) are nominal. `MARCA_PROPRIA` and `PRIMEIRA_CLIENTE` are binary flags. Client effort (Outside Panel / Never Visited / Visited / Visited Recently) is a category derived from a number, days without a visit, with a 90-day cutoff. | |
| 7 | Level | The options of the Payment Type and Client Effort filters are the levels of those variables. | |
| 8 | Stored type vs. statistical type | `PRIMEIRA_CLIENTE` is stored as text and compared with `"1"` (new patients); `MARCA_PROPRIA` is stored as a number and compared with `1` (`transform.py`, 660 base). Each flag is compared in its own type; comparing with the other type would return zero rows with no error. | |
| 9 | Identifier | `ID_VENDA`, `ID_CLIENTE` and `CRM-UF` are used as keys and counted with `nunique` (distinct new patients), never averaged. | |

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
