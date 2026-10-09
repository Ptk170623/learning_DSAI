"""Rectangular data and tidy data - generic analysis of every table the
project loads, built to practise these concepts: rectangular data, data
frame, feature, outcome, record, index, nonrectangular data structures,
data matrix, tidy data, silent error, dtype, duplicate key, wide and long.

No Streamlit dependency (same idea as transform.py / data_types_profile.py).
Nothing here knows a column name: decisions come from dtypes, counts,
uniqueness and the column-name TOKEN rules of data_types_profile.

PRIVACY: every result holds only column names, counts, percentages, formats
(a value's SHAPE such as "9-A", never the value) and aggregates. Raw rows and
the values of identifier / personal columns never leave analyze().
"""

from __future__ import annotations

import dataclasses
import itertools
import re
from dataclasses import dataclass

import numpy as np
import pandas as pd

import data_types_profile as dtp

# --- Tunable rules ----------------------------------------------------------------
KEY_MAX_MISSING_PCT = 5.0       # a column may take part in a composite key with up to this % missing
KEY_CANDIDATES = 12             # columns tried when searching for a unique key
KEY_MAX_SIZE = 3
FD_MIN_GROUPS = 20              # a dependency needs this many repeated key groups to count
FD_MIN_SHARE = 0.99
COMPOSITE_MIN_SHARE = 0.90
MULTIVALUE_MIN_SHARE_PCT = 2.0
PIVOT_MAX_LEVELS = 100
TARGET_TOKENS = {"CHURN", "TARGET", "LABEL", "OUTCOME", "RESULT", "RESULTADO", "CONVERTED"}
FANOUT_MIN_UNIQUE_PCT = 90.0    # only near-unique keys: the "looks like one row per entity" trap

ROLE_KEY, ROLE_FEATURE, ROLE_OUTCOME = "key", "feature", "outcome"


@dataclass
class TidyResult:
    shape: pd.DataFrame        # rectangular data / data frame / record / index
    roles: pd.DataFrame        # feature / outcome / key per column
    matrix: pd.DataFrame       # data matrix per table
    nonrect: pd.DataFrame      # nonrectangular findings inside the tables
    containers: pd.DataFrame   # nonrectangular containers in the project's code
    composite: pd.DataFrame    # several variables in one column
    dependencies: pd.DataFrame # one table mixing observational units
    wide: pd.DataFrame         # wide-format column groups
    pivot: pd.DataFrame        # long -> wide demonstration (summary)
    pivot_heat: pd.DataFrame   # filled / empty cells of that pivot (no labels)
    dtypes: pd.DataFrame       # stored types, memory
    fanout: pd.DataFrame       # silent error: merge on a non-unique key
    flags: pd.DataFrame        # silent error: comparing a flag with the wrong dtype
    dropped: pd.DataFrame      # silent error: groupby drops missing keys
    id_math: pd.DataFrame      # silent error: arithmetic on identifiers


# =============================================================================
# Helpers
# =============================================================================

def _non_float(s: pd.Series) -> bool:
    return not pd.api.types.is_float_dtype(s)


def find_key(df: pd.DataFrame) -> tuple[list[str] | None, int]:
    """(smallest set of columns that is unique per row, number of equally small
    alternatives) - or (None, 0). Floats are never keys; at most KEY_CANDIDATES
    columns (the most distinct ones, <= KEY_MAX_MISSING_PCT missing) are tried."""
    n = len(df)
    if n == 0:
        return None, 0
    stats = []
    for c in df.columns:
        s = df[c]
        if not _non_float(s) or 100 * s.isna().mean() > KEY_MAX_MISSING_PCT:
            continue
        stats.append((c, int(s.nunique(dropna=False))))
    stats.sort(key=lambda x: -x[1])
    top = stats[:KEY_CANDIDATES]
    distinct = dict(top)
    for size in range(1, KEY_MAX_SIZE + 1):
        found = []
        for combo in itertools.combinations([c for c, _ in top], size):
            if np.prod([distinct[c] for c in combo], dtype=float) < n:
                continue
            if not df.duplicated(subset=list(combo)).any():
                found.append(combo)
        if found:
            found.sort(key=lambda combo: np.prod([distinct[c] for c in combo], dtype=float))
            return list(found[0]), len(found)
    return None, 0


def _mask(value: str) -> str:
    value = re.sub(r"[A-Za-z]", "A", value)
    value = re.sub(r"\d", "9", value)
    return re.sub(r"A+", "A", re.sub(r"9+", "9", value))


def _stat(profile: dtp.Profile, table: str) -> dict[str, dtp.ColumnProfile]:
    return {c.column: c for c in profile.columns if c.table == table}


def _role(c: dtp.ColumnProfile) -> tuple[str, str]:
    tokens = set(dtp.name_tokens(c.column))
    if c.stat_type == dtp.IDENTIFIER:
        return ROLE_KEY, "identifier: names a thing, not a predictor"
    if c.stat_type in (dtp.CONTINUOUS, dtp.DISCRETE) and tokens & (dtp.MEASURE_TOKENS | dtp.COUNT_TOKENS):
        return ROLE_OUTCOME, "measured amount or count (assumed outcome)"
    if c.stat_type == dtp.BINARY and tokens & TARGET_TOKENS:
        return ROLE_OUTCOME, "target-like flag (assumed outcome)"
    return ROLE_FEATURE, "describes the record (assumed feature)"


# =============================================================================
# Analysis
# =============================================================================

def analyze(tables: dict[str, pd.DataFrame], profile: dtp.Profile) -> TidyResult:
    shape_rows, role_rows, matrix_rows, nonrect_rows, comp_rows = [], [], [], [], []
    fd_rows, wide_rows, pivot_rows, heat_frames, dtype_rows = [], [], [], [], []
    flag_rows, drop_rows, idmath_rows = [], [], []
    outcome_of: dict[str, str | None] = {}

    for name, df in tables.items():
        cols = _stat(profile, name)
        n = len(df)
        key, n_alt = find_key(df)
        miss = df.isna()
        shape_rows.append({
            "table": name, "rows": n, "columns": df.shape[1], "index_type": type(df.index).__name__,
            "index_default": isinstance(df.index, pd.RangeIndex) and df.index.start == 0,
            "memory_mb": df.memory_usage(deep=True).sum() / 1e6,
            "missing_cells_pct": 100 * float(miss.to_numpy().mean()) if n else 0.0,
            "rows_over_half_missing_pct": 100 * float((miss.mean(axis=1) > 0.5).mean()) if n else 0.0,
            "empty_columns": int(miss.all().sum()) if n else 0,
            "duplicate_rows": int(df.duplicated().sum()) if n else 0,
            "key": ", ".join(key) if key else "", "key_alternatives": n_alt,
        })

        # --- feature / outcome / key
        roles = {c: _role(cols[c]) for c in df.columns}
        for c, (role, why) in roles.items():
            role_rows.append({"table": name, "column": c, "role": role, "stat_type": cols[c].stat_type, "why": why})
        outcomes = [c for c, (r, _) in roles.items() if r == ROLE_OUTCOME]
        outcome_of[name] = next((c for c in outcomes if cols[c].stat_type in (dtp.CONTINUOUS, dtp.DISCRETE)), None)

        # --- data matrix
        numeric = [c for c in df.columns if cols[c].stat_type in (dtp.CONTINUOUS, dtp.DISCRETE)]
        cats = [c for c in df.columns if cols[c].stat_type in (dtp.NOMINAL, dtp.ORDINAL, dtp.BINARY)]
        onehot = int(sum(cols[c].n_distinct for c in cats))
        onehot_low = int(sum(cols[c].n_distinct for c in cats if cols[c].n_distinct <= dtp.MAX_LEVELS_SHOWN))
        num_part = df[numeric].apply(pd.to_numeric, errors="coerce") if numeric else pd.DataFrame(index=df.index)
        matrix_rows.append({
            "table": name, "rows": n, "numeric_columns": len(numeric), "categorical_columns": len(cats),
            "onehot_width": onehot, "onehot_width_low": onehot_low, "matrix_columns": len(numeric) + onehot,
            "matrix_cells_m": n * (len(numeric) + onehot) / 1e6,
            "numeric_missing_pct": 100 * float(num_part.isna().to_numpy().mean()) if numeric and n else 0.0,
            "rows_lost_by_dropna_pct": 100 * float(num_part.isna().any(axis=1).mean()) if numeric and n else 0.0,
            "other_columns": df.shape[1] - len(numeric) - len(cats),
        })

        # --- nonrectangular signs inside the cells
        for c in df.columns:
            s = df[c].dropna()
            if s.empty or cols[c].stored_family not in ("text", "mixed"):
                continue
            head = s.iloc[:2000]
            nested = head.map(lambda v: isinstance(v, (list, dict, tuple, set))).mean() * 100
            if nested > 0:
                nonrect_rows.append({"table": name, "column": c, "kind": "nested cell (list / dict)", "share_pct": nested})
                continue
            txt = s.astype(str)
            multi = float(txt.str.contains(r"[;|]|,\s", regex=True).mean()) * 100
            if multi >= MULTIVALUE_MIN_SHARE_PCT:
                nonrect_rows.append({"table": name, "column": c, "kind": "several values in one cell", "share_pct": multi})

        # --- several variables in one column (tidy rule 1)
        for c in df.columns:
            if cols[c].stored_family != "text" or cols[c].stat_type == dtp.OTHER_DATE:
                continue
            s = df[c].dropna()
            if s.empty:
                continue
            sample = s.iloc[:: max(1, len(s) // 20000)].astype(str)
            masks = sample.map(_mask)
            top = masks.value_counts()
            share = float(top.iloc[0]) / len(masks)
            m = top.index[0]
            if share >= COMPOSITE_MIN_SHARE and re.search(r"[-/|;:.]", m) and len(re.findall(r"[A9]", m)) >= 2:
                parts = sample[masks == m].str.split(r"[-/|;:.]", expand=True)
                varying = int((parts.nunique(dropna=True) >= 2).sum())
                if varying >= 2:   # a constant prefix such as "CLI-" is not a second variable
                    comp_rows.append({"table": name, "column": c, "format": m, "share_pct": 100 * share,
                                      "parts": varying})

        # --- one table per observational unit (tidy rule 3): functional dependencies
        determinants = [c for c in df.columns if cols[c].stat_type == dtp.IDENTIFIER and 2 <= cols[c].n_distinct
                        and cols[c].unique_pct < 100]
        deps_ok = [c for c in df.columns if cols[c].stat_type not in (dtp.CONTINUOUS, dtp.DISCRETE)]
        for a in determinants:
            size = df.groupby(a, sort=False).size()
            repeated = size[size >= 2].index
            if len(repeated) < FD_MIN_GROUPS:
                continue
            sub = df[df[a].isin(repeated)]
            dependents = []
            for b in deps_ok:
                if b == a:
                    continue
                per_group = sub.groupby(a, sort=False)[b].nunique(dropna=True)
                if float((per_group <= 1).mean()) >= FD_MIN_SHARE and sub[b].notna().any():
                    dependents.append(b)
            if dependents:
                fd_rows.append({"table": name, "determinant": a, "unique_pct": cols[a].unique_pct,
                                "repeated_groups": int(len(repeated)), "n_dependents": len(dependents),
                                "dependents": ", ".join(dependents)})

        # --- wide format: column names that repeat a stem with a period / number suffix
        groups: dict[str, list[str]] = {}
        for c in df.columns:
            m = re.match(r"^(.*?)[_\- ]?((?:19|20)\d{2}[_\-]?\d{0,2}|\d{1,3})$", str(c))
            if m and m.group(1):
                groups.setdefault(m.group(1).upper(), []).append(c)
        for stem, members in groups.items():
            if len(members) >= 3 and len({str(df[c].dtype) for c in members}) == 1:
                wide_rows.append({"table": name, "stem": stem, "columns": len(members)})

        # --- long -> wide demonstration
        dates = sorted((c for c in df.columns if cols[c].stored_family == "datetime"), key=lambda c: cols[c].n_missing)
        cat_cands = [c for c in df.columns if cols[c].stat_type in (dtp.NOMINAL, dtp.ORDINAL)
                     and 3 <= cols[c].n_distinct <= PIVOT_MAX_LEVELS and cols[c].missing_pct <= 10]
        cat_cands.sort(key=lambda c: (cols[c].personal, -cols[c].n_distinct))
        measure = outcome_of[name]
        if dates and cat_cands and measure:
            d, cat = dates[0], cat_cands[0]
            work = pd.DataFrame({"cat": df[cat], "month": df[d].dt.to_period("M"), "v": pd.to_numeric(df[measure], errors="coerce")})
            piv = work.pivot_table(index="cat", columns="month", values="v", aggfunc="sum")
            cells = piv.shape[0] * piv.shape[1]
            filled = int(piv.notna().sum().sum())
            pivot_rows.append({
                "table": name, "category": cat, "period": d, "measure": measure, "long_rows": filled,
                "wide_rows": piv.shape[0], "wide_columns": piv.shape[1], "wide_cells": cells,
                "empty_pct": 100 * (1 - filled / cells) if cells else 0.0,
            })
            heat = piv.notna().reset_index(drop=True)
            heat.columns = [p.to_timestamp() for p in heat.columns]
            long_heat = heat.stack().rename("filled").reset_index()
            long_heat.columns = ["row", "month", "filled"]
            long_heat["table"] = name
            heat_frames.append(long_heat)

        # --- dtypes and memory
        before = int(df.memory_usage(deep=True).sum())
        saving = 0
        for c in df.columns:
            s = df[c]
            if cols[c].stored_family == "text" and cols[c].n_distinct and cols[c].unique_pct < 50:
                saving += int(s.memory_usage(deep=True) - s.astype("category").memory_usage(deep=True))
        dtype_rows.append({
            "table": name, "memory_mb": before / 1e6, "category_saving_mb": max(saving, 0) / 1e6,
            "saving_pct": 100 * max(saving, 0) / before if before else 0.0,
            **{f"dtype:{k}": v for k, v in df.dtypes.astype(str).value_counts().items()},
        })

        # --- silent error: a flag compared with the wrong dtype
        for c in df.columns:
            if cols[c].stat_type != dtp.BINARY:
                continue
            s = df[c]
            row = {"table": name, "column": c, "stored_type": cols[c].stored_type, "rows": n,
                   "match_int_1": int((s == 1).sum()), "match_text_1": int((s == "1").sum()),
                   "match_true": int((s == True).sum())}  # noqa: E712 - comparing on purpose
            flag_rows.append(row)

        # --- silent error: groupby(dropna=True) drops rows whose key is missing
        for c in df.columns:
            if cols[c].stat_type in (dtp.NOMINAL, dtp.ORDINAL, dtp.BINARY, dtp.OTHER_DATE) and cols[c].n_missing \
                    and (cols[c].n_distinct <= 200 or cols[c].stat_type == dtp.OTHER_DATE):
                lost = None
                if measure:
                    v = pd.to_numeric(df[measure], errors="coerce")
                    total = float(v.sum())
                    lost = 100 * float(v[df[c].isna()].sum()) / total if total else 0.0
                drop_rows.append({"table": name, "column": c, "rows_dropped": cols[c].n_missing, "rows_dropped_pct": cols[c].missing_pct,
                                  "outcome": measure or "", "outcome_lost_pct": lost})

        # --- silent error: arithmetic on identifiers
        for c in df.columns:
            if cols[c].stat_type == dtp.IDENTIFIER and cols[c].stored_family in ("integer", "float"):
                idmath_rows.append({"table": name, "column": c, "stored_type": cols[c].stored_type,
                                    "values_averaged": n - cols[c].n_missing})

    # --- silent error: merge on a non-unique key (needs two tables)
    fan_rows = []
    for left, right in itertools.permutations(tables, 2):
        lcols, rcols = _stat(profile, left), _stat(profile, right)
        shared = [c for c in lcols if c in rcols and lcols[c].stat_type == dtp.IDENTIFIER and rcols[c].stat_type == dtp.IDENTIFIER
                  and rcols[c].unique_pct >= FANOUT_MIN_UNIQUE_PCT and rcols[c].duplicates > 0]
        for c in shared:
            L, R = tables[left], tables[right]
            counts = R[c].value_counts()
            factor = L[c].map(counts).fillna(1).clip(lower=1)
            after = int(factor.sum())
            measure = outcome_of.get(left)
            infl = None
            if measure:
                v = pd.to_numeric(L[measure], errors="coerce").fillna(0)
                total = float(v.sum())
                infl = 100 * (float((v * factor).sum()) / total - 1) if total else 0.0
            common = [x for x in L.columns if x in R.columns and _non_float(R[x])]
            safe, _ = find_key(R[common]) if common else (None, 0)
            fan_rows.append({
                "left": left, "right": right, "key": c, "left_rows": len(L), "rows_after": after,
                "extra_rows": after - len(L), "extra_pct": 100 * (after - len(L)) / len(L) if len(L) else 0.0,
                "measure": measure or "", "measure_inflation_pct": infl,
                "safe_key": ", ".join(safe) if safe and set(safe) <= set(common) and c in safe else "",
            })

    fanout = pd.DataFrame(fan_rows)
    if not fanout.empty:   # the mirror merge of a pair adds nothing when the other direction carries a measure
        pairs = {(x.left, x.right, x.key) for x in fanout.itertuples() if x.measure}
        mirrored = pd.Series([(a, b, k) in pairs for a, b, k in zip(fanout["right"], fanout["left"], fanout["key"])], index=fanout.index)
        fanout = fanout[~((fanout["measure"] == "") & mirrored)]
        fanout = fanout.sort_values("extra_pct", ascending=False).reset_index(drop=True)
    heat_all = pd.concat(heat_frames, ignore_index=True) if heat_frames else pd.DataFrame(columns=["row", "month", "filled", "table"])
    containers = pd.DataFrame(_code_containers())
    return TidyResult(
        shape=pd.DataFrame(shape_rows), roles=pd.DataFrame(role_rows), matrix=pd.DataFrame(matrix_rows),
        nonrect=pd.DataFrame(nonrect_rows, columns=["table", "column", "kind", "share_pct"]), containers=containers,
        composite=pd.DataFrame(comp_rows, columns=["table", "column", "format", "share_pct", "parts"]),
        dependencies=pd.DataFrame(fd_rows, columns=["table", "determinant", "unique_pct", "repeated_groups", "n_dependents", "dependents"]),
        wide=pd.DataFrame(wide_rows, columns=["table", "stem", "columns"]),
        pivot=pd.DataFrame(pivot_rows), pivot_heat=heat_all, dtypes=pd.DataFrame(dtype_rows).fillna(0),
        fanout=fanout, flags=pd.DataFrame(flag_rows), dropped=pd.DataFrame(drop_rows),
        id_math=pd.DataFrame(idmath_rows, columns=["table", "column", "stored_type", "values_averaged"]),
    )


def _code_containers() -> list[dict]:
    """Nonrectangular structures the PROJECT's own code builds (read from
    transform.py's dataclasses): several data frames bundled in one object."""
    try:
        import transform
    except Exception:  # pragma: no cover - the page also works without it
        return []
    rows = []
    for name, obj in vars(transform).items():
        if isinstance(obj, type) and dataclasses.is_dataclass(obj) and obj.__module__ == transform.__name__:
            hints = [f for f in dataclasses.fields(obj) if "DataFrame" in str(f.type)]
            others = [f.name for f in dataclasses.fields(obj) if "DataFrame" not in str(f.type)]
            if not hints:
                continue
            rows.append({"container": name, "data_frames": len(hints), "other_fields": ", ".join(others),
                         "frames": ", ".join(f.name for f in hints)})
    return rows


# =============================================================================
# Insights
# =============================================================================

@dataclass
class Insight:
    title: str
    finding: str
    risk: str
    fix: str


def build_insights(r: TidyResult, mismatch_cols: list | None = None) -> list[Insight]:
    mismatch_cols = mismatch_cols or []
    out: list[Insight] = []
    sh = r.shape
    if sh.empty:
        return out
    worst_mat = r.matrix.sort_values("rows_lost_by_dropna_pct", ascending=False).iloc[0]
    no_key = sh[sh["key"] == ""]
    comp_key = sh[sh["key"].str.contains(",")]

    if len(no_key) or len(comp_key):
        parts = []
        if len(comp_key):
            ex = comp_key.iloc[0]
            parts.append(f"{len(comp_key)} table(s) need a composite key (e.g. `{ex['table']}`: {ex['key']})")
        if len(no_key):
            ex = no_key.iloc[0]
            parts.append(f"{len(no_key)} table(s) have no unique key at all (e.g. `{ex['table']}` with "
                         f"{int(ex['duplicate_rows']):,} fully duplicated rows)")
        out.append(Insight(
            "The record is not the entity: keys are composite or missing",
            "; ".join(parts) + f". Every table has a default index ({', '.join(sh['index_type'].unique())}), "
            "so the index carries no meaning.",
            "Counting rows as if each were a sale, client or doctor overstates; duplicated records double-count.",
            "Name the grain of every table (its key), assert uniqueness on load and keep the key as a column or the index.",
        ))

    if not r.fanout.empty:
        w = r.fanout.assign(_m=r.fanout["measure_inflation_pct"].fillna(-1)).sort_values(["extra_pct", "_m"], ascending=False).iloc[0]
        infl = f", inflating `{w['measure']}` by {w['measure_inflation_pct']:.2f}%" if w["measure"] and pd.notna(w["measure_inflation_pct"]) else ""
        out.append(Insight(
            "Silent error: merging on a near-unique key fans rows out",
            f"Merging `{w['left']}` with `{w['right']}` on `{w['key']}` alone returns {int(w['rows_after']):,} rows "
            f"instead of {int(w['left_rows']):,} (+{int(w['extra_rows']):,}, {w['extra_pct']:.2f}%){infl}. "
            + (f"Merging on the composite key ({w['safe_key']}) keeps the row count." if w["safe_key"] else ""),
            "pandas raises no error: totals grow quietly and every downstream sum is wrong.",
            "Merge on the full key, pass validate=\"one_to_one\" or \"many_to_one\", and compare row counts before and after.",
        ))

    if not r.flags.empty:
        fl = r.flags
        only_int = fl[(fl["match_int_1"] > 0) & (fl["match_text_1"] == 0)]
        only_txt = fl[(fl["match_text_1"] > 0) & (fl["match_int_1"] == 0)]
        if len(only_int) and len(only_txt):
            a, b = only_int.iloc[0], only_txt.iloc[0]
            out.append(Insight(
                "Silent error: a flag compared with the wrong dtype matches nothing",
                f"The {len(fl)} binary columns are stored in different dtypes. `{a['table']}.{a['column']}` ({a['stored_type']}): "
                f"`== 1` finds {int(a['match_int_1']):,} rows but `== \"1\"` finds 0. `{b['table']}.{b['column']}` ({b['stored_type']}): "
                f"`== \"1\"` finds {int(b['match_text_1']):,} rows but `== 1` finds 0.",
                "A filter written for the other dtype returns zero rows and pandas raises nothing.",
                "Store every flag as boolean and compare with True / False, or cast once at load time.",
            ))

    if not r.dropped.empty:
        gap = r.dropped.assign(_gap=r.dropped["outcome_lost_pct"].fillna(0) - r.dropped["rows_dropped_pct"])
        d = gap.sort_values("_gap", ascending=False).iloc[0]   # the loss that weighs most more than its row share
        lost = f" and {d['outcome_lost_pct']:.1f}% of `{d['outcome']}`" if d["outcome"] and pd.notna(d["outcome_lost_pct"]) else ""
        out.append(Insight(
            "Silent error: groupby drops rows whose key is missing",
            f"{len(r.dropped)} grouping-style columns contain missing values; grouping by `{d['table']}.{d['column']}` "
            f"drops {int(d['rows_dropped']):,} rows ({d['rows_dropped_pct']:.1f}%){lost} from the result.",
            "Group totals no longer add up to the table total, and nothing says why.",
            "Fill missing keys with an explicit label before grouping (as transform.py does with '(not informed)') or use dropna=False.",
        ))

    if not r.dependencies.empty:
        d = r.dependencies.sort_values("n_dependents", ascending=False).iloc[0]
        out.append(Insight(
            "Tidy rule broken: one table mixes several observational units",
            f"{len(r.dependencies)} identifier column(s) fix other columns; e.g. in `{d['table']}`, `{d['determinant']}` "
            f"determines {int(d['n_dependents'])} other column(s) ({d['dependents']}) for 99%+ of its repeated values, so "
            "those are attributes of another unit repeated on every row.",
            "Attribute columns are stored once per row: they can disagree after an edit and make joins and counts wrong.",
            "Split the repeated attributes into their own table (one row per entity) and join them back when needed.",
        ))

    if not r.composite.empty:
        c = r.composite.iloc[0]
        out.append(Insight(
            "Tidy rule broken: several variables in one column",
            f"{len(r.composite)} column(s) hold values with a fixed multi-part format; e.g. `{c['table']}.{c['column']}` "
            f"follows the shape `{c['format']}` in {c['share_pct']:.1f}% of its values ({c['parts']} parts).",
            "Filtering or joining on one part needs string slicing, and a malformed value breaks it silently.",
            "Split it into one column per variable (e.g. number and state) at load time.",
        ))

    if not r.pivot.empty:
        p = r.pivot.sort_values("wide_cells", ascending=False).iloc[0]   # the largest table is the one that matters
        out.append(Insight(
            "Long versus wide: the wide shape is mostly empty",
            f"`{p['table']}` pivoted by `{p['category']}` x month of `{p['period']}` is {int(p['wide_rows'])} x "
            f"{int(p['wide_columns'])} = {int(p['wide_cells']):,} cells, but only {int(p['long_rows']):,} hold data "
            f"({p['empty_pct']:.0f}% empty).",
            "Missing months become NaN: means over a row ignore them, sums treat them as zero only if filled, and "
            "rolling windows quietly change length.",
            "Keep the data long and tidy, pivot only for the calculation, and fill gaps explicitly (0 or NaN) on purpose.",
        ))

    dt = r.dtypes
    out.append(Insight(
        "Dtype: text stored as str is heavy and easy to misuse",
        f"The {len(dt)} tables use {dt['memory_mb'].sum():,.0f} MB; storing their low-cardinality text columns as category "
        f"would save about {dt['category_saving_mb'].sum():,.0f} MB ({100 * dt['category_saving_mb'].sum() / dt['memory_mb'].sum():.0f}%). "
        f"{len(mismatch_cols)} column(s) also carry a dtype that misleads (flags as text or float, an ID as float, dates as text or numbers).",
        "Memory grows with every copy, and a misleading dtype is what makes the silent errors above possible.",
        "Convert at the loading boundary (transform._ler): category for repeated text, boolean for flags, datetime for dates.",
    ))
    out.append(Insight(
        "Data matrix: missing numbers cost whole rows",
        f"The numeric part of `{worst_mat['table']}` ({_n(int(worst_mat['numeric_columns']), 'column')}) has "
        f"{worst_mat['numeric_missing_pct']:.1f}% empty cells, yet dropping every row with any gap would lose "
        f"{worst_mat['rows_lost_by_dropna_pct']:.1f}% of its {int(worst_mat['rows']):,} rows. One-hot encoding its "
        f"categorical columns would widen the matrix to {int(worst_mat['matrix_columns']):,} columns "
        f"(only {int(worst_mat['onehot_width_low']):,} extra if you encode just the columns with {dtp.MAX_LEVELS_SHOWN} levels or fewer).",
        "A model or matrix routine that drops incomplete rows (or fills with 0) changes the sample without telling you.",
        "Decide per column whether a gap means 'none', 'unknown' or 'not applicable' before building any matrix.",
    ))
    return out[:8]


# =============================================================================
# Result report (paste-ready markdown)
# =============================================================================

def _n(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def _block(title: str, where: str, ran: str, showed: list[str], means: str, problems: list[str]) -> str:
    lines = [f"### {title}", f"- **WHERE:** {where}", f"- **WHAT I RAN:** {ran}", "- **WHAT IT SHOWED:**"]
    lines += [f"  - {x}" for x in (showed or ["nothing of this kind in the data"])]
    lines += [f"- **WHAT IT MEANS FOR THE PROJECT:** {means}", "- **PROBLEMS OR SURPRISES:**"]
    lines += [f"  - {x}" for x in ([p for p in problems if p] or ["none found by these rules"])]
    return "\n".join(lines)


def build_report(r: TidyResult, insights: list[Insight], profile: dtp.Profile) -> str:
    sh, names = r.shape, list(r.shape["table"])
    out = [
        "# RESULT REPORT - Rectangular data and tidy data",
        '**PAGE:** "Rectangular data and tidy data" in the Streamlit app (sidebar navigation). Run: '
        "`streamlit run data_app_gestao.py`. Code: `tidy_rectangular.py` (analysis) + `page_rectangular_tidy` in "
        "`data_app_gestao.py` (UI). Only counts, percentages, formats and aggregates appear - no raw rows or identifier values.",
    ]
    out.append(_block(
        "1. Rectangular data, data frame, record, index", f"{len(names)} tables: {', '.join(names)}",
        "shape, index type, key search (smallest unique column set, up to 3 columns), empty cells, duplicated rows.",
        [f"{x.table}: {x.rows:,} records x {x.columns} columns, index {x.index_type}"
         f"{' (default 0..n-1, no meaning)' if x.index_default else ''}, unique key: "
         f"{x.key if x.key else 'NONE found'}"
         f"{f' ({x.key_alternatives} equally small alternatives)' if x.key_alternatives > 1 else ''}, "
         f"{x.missing_cells_pct:.1f}% empty cells, {x.duplicate_rows:,} duplicated rows" for x in sh.itertuples()],
        "Every table is rectangular: the same columns on every row, one record per row, held as a pandas data frame. "
        "A record is whatever the key says one row is - not necessarily the sale, client or doctor.",
        [f"{x.table}: no unique key found - rows can repeat" for x in sh.itertuples() if not x.key]
        + [f"{x.table}: record = {x.key} (a single ID is not enough)" for x in sh.itertuples() if "," in x.key]
        + [f"{x.table}: {x.rows_over_half_missing_pct:.1f}% of rows are more than half empty" for x in sh.itertuples()
           if x.rows_over_half_missing_pct >= 1],
    ))
    roles = r.roles.groupby(["table", "role"]).size().unstack(fill_value=0)
    showed = [f"{t}: {int(row.get('feature', 0))} features, {int(row.get('outcome', 0))} outcome candidates, "
              f"{int(row.get('key', 0))} keys" for t, row in roles.iterrows()]
    outs = r.roles[r.roles["role"] == ROLE_OUTCOME]
    out.append(_block(
        "2. Feature and outcome", "every column of every table",
        "role per column: key (identifier), outcome (money / count measures, target-like flags), feature (the rest).",
        showed + [f"outcome candidates: {', '.join(f'`{x.table}.{x.column}`' for x in outs.itertuples())}"],
        "Features describe the record; outcomes are what you want to explain or total. This split is an assumption: "
        "it depends on the question, so the page shows it as assumed.",
        ["no outcome candidate found in " + ", ".join(set(names) - set(outs["table"]))] if set(names) - set(outs["table"]) else [],
    ))
    mx = r.matrix
    out.append(_block(
        "3. Nonrectangular structures and data matrix", ", ".join(names),
        "numeric sub-matrix per table (size, gaps, rows lost by dropna), one-hot width, cells holding lists or several "
        "values, and the containers defined in transform.py.",
        [f"{x.table}: numeric matrix {x.rows:,} x {x.numeric_columns}, {x.numeric_missing_pct:.1f}% empty, dropna would lose "
         f"{x.rows_lost_by_dropna_pct:.1f}% of rows; with one-hot categoricals: {x.matrix_columns:,} columns "
         f"({x.matrix_cells_m:,.1f} M cells)" for x in mx.itertuples()]
        + [f"{x.container}: {_n(x.data_frames, 'data frame')} in one object ({x.frames})" for x in r.containers.itertuples()],
        "A data matrix is the all-numeric table models use; categoricals must be encoded and gaps handled first. The "
        "project bundles several frames per analysis in dataclasses (nonrectangular as a whole) and reads rows from "
        "Supabase as a list of dicts before they become a frame.",
        [f"`{x.table}.{x.column}`: {x.kind} in {x.share_pct:.1f}% of cells" for x in r.nonrect.itertuples()],
    ))
    out.append(_block(
        "4. Tidy data", ", ".join(names),
        "rule 1 (a variable per column): composite-format columns and wide column groups; rule 2 (an observation per "
        "row): key / duplicate checks; rule 3 (a table per unit): functional dependencies from identifier columns.",
        [f"`{x.table}.{x.column}` has the shape `{x.format}` in {x.share_pct:.1f}% of values ({x.parts} variables in one column)"
         for x in r.composite.itertuples()]
        + [f"`{x.table}.{x.determinant}` ({x.unique_pct:.1f}% unique) determines {_n(x.n_dependents, 'column')}: {x.dependents}"
           for x in r.dependencies.itertuples()],
        "A table is tidy when each variable is a column, each observation a row and each unit its own table. Repeated "
        "attributes of clients, doctors or products inside a sales table are the typical break.",
        [f"{_n(len(r.dependencies), 'identifier column')} carry attributes of another unit" if len(r.dependencies) else "",
         f"{len(r.composite)} composite column(s)" if len(r.composite) else ""],
    ))
    out.append(_block(
        "5. Wide and long", ", ".join(names),
        "wide-format column groups (same stem + period/number suffix) and a long-to-wide pivot (category x month) of the "
        "first outcome measure.",
        [f"{x.table}: pivot of `{x.measure}` by `{x.category}` x month of `{x.period}` = {x.wide_rows} x {x.wide_columns} "
         f"({x.wide_cells:,} cells), {x.long_rows:,} filled, {x.empty_pct:.0f}% empty" for x in r.pivot.itertuples()]
        + [f"{x.table}: {x.columns} wide-format columns share the stem `{x.stem}`" for x in r.wide.itertuples()],
        "The stored tables are long (a row per event); the app pivots to wide month matrices to compute benchmarks. "
        "Wide is convenient for maths but hides gaps.",
        ([f"{len(r.wide)} wide-format column group(s) in the stored tables"] if len(r.wide) else [])
        or ["no wide-format columns in the stored tables"],
    ))
    dt = r.dtypes
    mm = [c for c in profile.columns if c.mismatch_kind]
    out.append(_block(
        "6. Dtype and duplicate key", ", ".join(names),
        "dtype counts and memory per table, potential saving from category dtype, columns whose dtype misleads "
        "(from data_types_profile), duplicate-key counts of identifier columns.",
        [f"{x.table}: {x.memory_mb:,.1f} MB, category dtype could save {x.category_saving_mb:,.1f} MB ({x.saving_pct:.0f}%)"
         for x in dt.itertuples()]
        + [f"`{c.table}.{c.column}`: {c.duplicates:,} repeats, {c.unique_pct:.1f}% unique" for c in profile.columns
           if c.stat_type == dtp.IDENTIFIER and c.unique_pct >= FANOUT_MIN_UNIQUE_PCT and c.duplicates],
        "The dtype decides what operations mean; a duplicate key decides how many rows a join returns.",
        [f"`{c.table}.{c.column}`: {c.stored_type} -> {c.stat_type} ({c.mismatch_kind})" for c in mm],
    ))
    fl, fo = r.flags, r.fanout
    showed = [f"merge `{x.left}` with `{x.right}` on `{x.key}` only: {x.rows_after:,} rows instead of {x.left_rows:,} "
              f"(+{x.extra_pct:.2f}%){f', {x.measure} +{x.measure_inflation_pct:.2f}%' if x.measure and pd.notna(x.measure_inflation_pct) else ''}"
              for x in fo.itertuples()]
    showed += [f"`{x.table}.{x.column}` ({x.stored_type}): `== 1` -> {x.match_int_1:,} rows, `== \"1\"` -> {x.match_text_1:,} rows, "
               f"`== True` -> {x.match_true:,}" for x in fl.itertuples()]
    top_drop = r.dropped.assign(_gap=r.dropped["outcome_lost_pct"].fillna(0) - r.dropped["rows_dropped_pct"]).sort_values("_gap", ascending=False).head(8)
    showed += [f"groupby on `{x.table}.{x.column}` drops {x.rows_dropped:,} rows ({x.rows_dropped_pct:.1f}%)"
               + (f" and {x.outcome_lost_pct:.1f}% of `{x.outcome}`" if x.outcome and pd.notna(x.outcome_lost_pct) else "")
               for x in top_drop.itertuples()]
    if len(r.dropped) > len(top_drop):
        showed.append(f"... and {len(r.dropped) - len(top_drop)} more grouping-style columns with missing values (see the page)")
    showed += [f"`{x.table}.{x.column}` ({x.stored_type}) can be averaged: {x.values_averaged:,} values" for x in r.id_math.itertuples()]
    out.append(_block(
        "7. Silent error", ", ".join(names),
        "four checks that run without any error in pandas: merge fan-out, flag comparisons with the wrong dtype, "
        "groupby dropping missing keys, arithmetic on identifiers.",
        showed,
        "A silent error returns a plausible number without any warning. Each line above is a real way for this project's "
        "data to produce one.",
        [f"{len(fo)} merge(s) on a non-unique key change the row count" if len(fo) else "",
         f"{len(r.dropped)} grouping column(s) lose rows to missing keys" if len(r.dropped) else ""],
    ))
    top = "\n".join(f"{n}. **{x.title}** - {x.finding} Risk: {x.risk} Fix: {x.fix}" for n, x in enumerate(insights, 1))
    return "\n\n".join(out) + "\n\n## TOP INSIGHTS\n\n" + top + "\n"
