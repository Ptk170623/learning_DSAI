# da_learn

A practice copy, in English, of the "gestao" Streamlit data app from the
`analise_representante` project (`classificacao_vendas/data_app_gestao.py`)
— built to study the analysis logic on data that is **safe to look at**:
every identifying field (client, representative, doctor, product, block)
is replaced by a generated fake value before anything here ever touches
it. All the real numbers (revenue, units, PX, dates) stay exact — only
names/IDs change.

Only three sections were ported (the rest of the original app was left
out on purpose):

- **660 Analysis** — own-brand sales vs. a retroactive benchmark window,
  classified by % deviation, plus its "By Sale Type" / "By Doctor" / "By
  Product" / "Churns in the Month" sub-sections.
- **Rises and Drops** — the biggest deviations of 660 Analysis, ranked,
  across every block at once.
- **Rep Block Performance** — "Doctor Potential" only: market potential
  (Closeup) crossed with internal visit effort and 1015 revenue result.

A fourth page, **Data types profile**, is a study page about the data
itself rather than the sales analysis: it loops over every table the app
loads and classifies each column (stored type vs. statistical type —
identifier, binary, nominal, ordinal, discrete, continuous, date), flags the
columns whose stored type misleads, and generates insights plus a
paste-ready result report. Only column names, counts and aggregates are
shown — never raw rows or the values of identifier / personal columns. Its
logic lives in `data_types_profile.py` (no Streamlit dependency); charts use
Altair, which ships with Streamlit.

## How it fits together

```
bases_cprata/*.parquet (REAL data, outside this project, THIS machine only)
        |
        v
anonymize/anonymize_data.py --upload-supabase   <-- run this first, on this machine
        |
        +--> data/*.parquet              (anonymized, local copy)
        +--> data/_MAPPING_PRIVATE.xlsx  (real -> fake mapping — NEVER share this)
        +--> Supabase (6 tables, snake_case columns — see anonymize/schema.sql)
        |
        v
transform.py  (all calculation logic — reads the 6 tables straight FROM SUPABASE,
                paginated past PostgREST's 1000-row cap, cached per table for the
                life of the running process — see _TABLE_CACHE/clear_cache())
        |
        v
data_app_gestao.py  (Streamlit UI — reads only transform.py; runs anywhere
                      with the Supabase credentials, not just this machine)
```

`anonymize_data.py` is the only file that ever touches the real
`bases_cprata/` bases, and it only runs on **this** machine (the one with
access to them). Everything downstream — `transform.py`,
`data_app_gestao.py` — reads the **anonymized Supabase project** instead,
which is why the app can run (and be edited) from a different machine:
copy `transform.py`/`data_app_gestao.py` there (e.g. via git) and point
its `key\da_learn\.env` at the same Supabase project.

**Performance note:** reading from Supabase instead of a local file is
meaningfully slower — the first open of a page typically takes 30s-2min+
(closeup alone is ~265k rows, paginated 1,000 at a time; `vendas_660`
~72k). `_TABLE_CACHE` avoids re-fetching the SAME table twice within one
run (660 Analysis and Churns both need `vendas_660`, for example), and
`data_app_gestao.py`'s `@st.cache_data(ttl=600)` avoids re-fetching on
every widget interaction — but the very first load of each page still
pays the full network cost. If your Supabase project's **Project
Settings → API Settings → "Max Rows"** is raised above the 1,000 default,
fewer, bigger pages are needed and it gets noticeably faster (this script
can't change that setting itself — it's per-project, in the dashboard).

## Setup

```
pip install -r requirements.txt
py anonymize/anonymize_data.py --upload-supabase
streamlit run data_app_gestao.py
```

The first command needs read access to
`C:\Users\PatrickdaSilvaLessa.AzureAD\bases_cprata\*_formatted.parquet`
(the real bases produced by the separate `limpeza_bases` project) — so it
only runs on this machine. Re-run it whenever those bases change; it is
deterministic (same real data always produces the same fake data, see
`SEED` in the script) but not reversible from the fake values alone. Note
it has **no de-duplication** against what's already in Supabase — running
`--upload-supabase` again inserts another full copy rather than replacing
the old one (no primary key enforces uniqueness, by design — see
`anonymize/schema.sql`); if you need to re-upload, clear the 6 tables in
the Supabase SQL editor first (`truncate vendas_660, tipo_venda,
carteira_pacientes, painel, closeup, vendas_1015;`).

**`data/_MAPPING_PRIVATE.xlsx` is the only file that can turn fake values
back into real client/doctor/representative identities. Never commit it,
share it, or upload it anywhere.** `.gitignore` already excludes it (and,
by default, the anonymized `data/*.parquet` files too — see the comment
there if you want to commit a snapshot of the practice data instead; they
are only a local-only leftover now, not read by the app anymore).

## Sending the anonymized data to Supabase

`anonymize/anonymize_data.py --upload-supabase` pushes the anonymized
tables to Supabase, reading `DA_LEARN_SUPABASE_URL`/`DA_LEARN_SUPABASE_KEY`
— the same credentials `transform.py` uses to read them back.

**The script only INSERTs rows — it never creates a table.** Supabase
(PostgREST) requires the table to already exist. Before the first upload,
run `anonymize/schema.sql` once in your Supabase project's SQL editor (it
is six `create table if not exists` statements, one per base — safe to
re-run). Column names there are lowercase snake_case (`crm_uf`,
`id_venda`, ...) rather than the original mixed-case/spaced names the
anonymized parquet files use (`"CRM - UF"`) — `anonymize_data.py` renames
every column to match (see `COLUMN_RENAME` in the script) right before
sending each row, so the two stay in sync automatically as long as you
don't edit one side without the other.

**Where to put the two credential values:** copy `.env.example` to
`C:\Users\PatrickdaSilvaLessa.AzureAD\key\da_learn\.env` (a vault folder
OUTSIDE this project — same idea as `data_base/secrets.toml` for the rest
of `analise_representante`) and fill in the real ones there.
`anonymize_data.py` loads that exact path automatically (via
`python-dotenv`, see `CAMINHO_ENV` in the script) without ever printing or
logging it — never put the real values in a copy of `.env.example` kept
inside this project. If you'd rather not have a file at all, you can
instead set a **Windows user environment variable**
(`[Environment]::SetEnvironmentVariable("DA_LEARN_SUPABASE_KEY", "...",
"User")` in PowerShell, once) — the script reads whichever is set, that
`.env` or an already-set environment variable; an existing environment
variable is never overwritten by `.env`. Either way, treat this key the
same as the `SUPABASE_KEY` already sitting in `data_base/secrets.toml` —
readable by anyone with access to your Windows account, never meant to
leave this machine except through the app's own code.

**This is a separate Supabase project from the one
`classificacao_medicos_painel` uses for real representative data** — do
not point these variables at that project without deciding, first, that
mixing fake practice data into it is actually what you want. `transform.py`
(the app's data layer) reads from this same project and these same
credentials — a `service_role` key is required (not `anon`/`public`),
since the tables have RLS enabled with no policies by default; an `anon`
key would get `new row violates row-level security policy` on insert and
an empty result on read.

## What is intentionally different from the original app

- **Sale type (`TIPO_VENDA`) comes pre-computed** from `tipo_venda.parquet`
  (a base added upstream, in `limpeza_bases`, since 2026-10-05) instead of
  being recalculated here. Its categories are therefore the **upstream**
  ones (Acquisition/Retention/Late Repurchase/Win-back Inactive 2/Win-back
  Inactive 3/Unclassified/Government Health Dept/Legal/Not Classified) —
  more granular than the older 4-bucket scheme `classificacao_vendas`
  used to compute by itself.
- **Churns in the Month reads `carteira_pacientes.parquet`'s pre-computed
  `CHURN`/`DATA_RUPTURA`/`POSOLOGIA_SUSPEITA`** instead of re-deriving the
  stock-rupture projection. Only **one** posologia-outlier tier exists
  upstream (a single Tukey fence), not the original two (1.5x/3x IQR) —
  the page shows one churn count, not two.
- **Effort is classified locally**, from `painel.parquet`'s
  `DIAS_SEM_VISITA_NUM` column (Outside Panel / Never Visited / Visited /
  Visited Recently, 90-day cutoff) — this app never reads
  `classificacao_medicos_painel`'s Supabase project. **Reason stays blank**
  for every doctor for now — there is no local source for it yet.
- Doctor and sale/product rows are grouped **only by CRM-UF** (never by
  block or exact name spelling) — the same doctor can move between
  blocks, or have their name recorded slightly differently, over time;
  grouping by those too would split one real doctor into disconnected
  rows. A "Blocks" column (comma-joined) replaces a single "Block" column
  wherever this applies.

## Files

- `anonymize/anonymize_data.py` — reads the real bases, generates
  `data/*.parquet` + `data/_MAPPING_PRIVATE.xlsx`, optionally uploads to
  Supabase (`--upload-supabase`).
- `anonymize/schema.sql` — run once in the Supabase SQL editor before the
  first upload; defines the 6 tables (snake_case columns).
- `transform.py` — all calculation logic, including the Supabase fetch/
  pagination/column-rename-back/cache (`_ler`, `_TABLE_CACHE`,
  `clear_cache()`) — no Streamlit dependency, testable on its own.
- `data_types_profile.py` — column classification, insights and report for
  the Data types profile page (pure pandas, testable on its own).
- `data_app_gestao.py` — the Streamlit UI (4 pages).
