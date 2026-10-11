# da_learn

A practice project, in English, for learning data analysis and statistics on a
sales-management Streamlit app. The app is the project; the learning notes live
next to it in `learning/`.

## The app

Three sections:

- **660 Analysis** — own-brand sales vs. a retroactive benchmark window,
  classified by % deviation, plus its "By Sale Type" / "By Doctor" / "By
  Product" / "Churns in the Month" sub-sections.
- **Rises and Drops** — the biggest deviations of 660 Analysis, ranked,
  across every block at once.
- **Rep Block Performance** — "Doctor Potential" only: market potential
  (Closeup) crossed with internal visit effort and 1015 revenue result.

## The learning notes

`learning/` has one file per part of the study plan. Each one holds the concept
map of the part, where each concept shows up (or will be applied) in this
project, and the dates of the reviews, scheduled and done. See
[`learning/README.md`](learning/README.md) for the index and how it is used.

The two reference books are in the repository root:

- `Practical_Statistics_for_Data_Scientists.pdf`
- `Book_EstatBas-Morettin-Bussab.PDF`

## How it fits together

```
Supabase (6 tables, snake_case columns)
        |
        v
transform.py  (all calculation logic — reads the 6 tables straight from
               Supabase, paginated past PostgREST's 1000-row cap, cached per
               table for the life of the running process — see
               _TABLE_CACHE / clear_cache())
        |
        v
data_app_gestao.py  (Streamlit UI — reads only transform.py)
```

`transform.py` has no Streamlit dependency and can be tested on its own.

**Performance note:** reading from Supabase is slower than reading a local file.
The first open of a page typically takes 30s–2min+ (the Closeup table alone is
~265k rows, fetched 1,000 at a time). `_TABLE_CACHE` avoids fetching the same
table twice in one run, and `@st.cache_data(ttl=600)` avoids re-fetching on every
widget interaction. Raising **Project Settings → API Settings → "Max Rows"** in
Supabase above the 1,000 default makes it noticeably faster.

## Setup

```
pip install -r requirements.txt
streamlit run data_app_gestao.py
```

The app needs two settings, `DA_LEARN_SUPABASE_URL` and `DA_LEARN_SUPABASE_KEY`,
read from environment variables or from a local `.env` file kept outside the
repository (see `.env.example` and `transform.py`). A `service_role` key is
required, not `anon`/`public`: the tables have row-level security enabled with no
policies. Never commit real credentials.

## Design choices of the app

- **Sale type (`TIPO_VENDA`) comes pre-computed** from the `tipo_venda` table
  instead of being recalculated. Its categories are Acquisition / Retention /
  Late Repurchase / Win-back Inactive 2 / Win-back Inactive 3 / Unclassified /
  Government Health Dept / Legal / Not Classified.
- **Churns in the Month reads the pre-computed** `CHURN`, `DATA_RUPTURA` and
  `POSOLOGIA_SUSPEITA` columns of `carteira_pacientes` instead of re-deriving the
  stock-rupture projection. There is a single posologia-outlier tier (one Tukey
  fence), so the page shows one churn count.
- **Effort is classified locally**, from the `DIAS_SEM_VISITA_NUM` column of
  `painel` (Outside Panel / Never Visited / Visited / Visited Recently, 90-day
  cutoff). **Reason stays blank** for every doctor for now: there is no source
  for it yet.
- Doctor and sale/product rows are grouped **only by CRM-UF** (never by block or
  exact name spelling): the same doctor can move between blocks, or have their
  name recorded slightly differently, over time, and grouping by those too would
  split one doctor into disconnected rows. A "Blocks" column (comma-joined)
  replaces a single "Block" column wherever this applies.

## Files

- `transform.py` — all calculation logic, including the Supabase fetch /
  pagination / column-rename-back / cache (`_ler`, `_TABLE_CACHE`,
  `clear_cache()`).
- `data_app_gestao.py` — the Streamlit UI (3 pages).
- `learning/` — study notes, one file per part.
- `insights/` — analyses that use what was learned, built into a report artifact (see its README).
- `requirements.txt`, `.env.example`.
