"""Data types profile - generic column-by-column profile of every table the
project loads (see transform._ler / transform._REVERSE_RENAME), built to
practise these concepts: structured data, variable (column), observation
(row), data type, numeric (continuous / discrete), categorical (nominal /
binary / ordinal), level, stored type vs. statistical type, identifier.

No Streamlit dependency (same idea as transform.py - testable on its own).
Nothing here knows a column name: every decision comes from the column's
dtype, its values (counts / uniqueness / distinct values) or a NAME TOKEN
rule (KEY_TOKENS, COUNT_TOKENS, ... below - word fragments, not columns).

PRIVACY: the profile holds only column names, counts, percentages and
aggregates. Levels (value -> count) are kept ONLY for categorical columns
that are not personal-looking (see is_personal) and have at most
MAX_LEVELS_SHOWN levels. Raw rows, and the values of identifier / personal
columns, never leave profile_table().
"""

from __future__ import annotations

import re
import warnings
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

# --- Statistical types (the page's vocabulary) --------------------------------
CONTINUOUS = "continuous"
DISCRETE = "discrete"
NOMINAL = "nominal"
BINARY = "binary"
ORDINAL = "ordinal"
IDENTIFIER = "identifier"
OTHER_DATE = "other (date)"
OTHER_TEXT = "other (text)"
STAT_TYPES = [CONTINUOUS, DISCRETE, NOMINAL, BINARY, ORDINAL, IDENTIFIER, OTHER_DATE, OTHER_TEXT]

# --- Mismatch kinds (stored type misleads) ------------------------------------
MM_NUMBERS_AS_TEXT = "numbers stored as text"
MM_ID_AS_NUMBER = "ID / code stored as number"
MM_FLAG_AS_NUMBER = "flag stored as number"
MM_FLAG_AS_TEXT = "flag stored as text digits"
MM_DATE_AS_TEXT = "date stored as text"
MM_DATE_AS_NUMBER = "date / period stored as number"
MM_INT_AS_FLOAT = "integers stored as float"

# --- Tunable rules --------------------------------------------------------------
MIN_ROWS_FOR_UNIQUE = 20      # "unique per row" needs at least this many non-null values
NUMERIC_TEXT_SHARE = 0.98     # text counts as "numbers stored as text" above this share
DATE_TEXT_SHARE = 0.98        # ... and as "dates stored as text" above this share
MAX_ORDINAL_LEVELS = 12
MANY_DISTINCT = 50            # integers with more distinct values than this, and no count-like name -> continuous
FREE_TEXT_MIN_LEVELS = 50     # text with more levels than this AND mostly-distinct values -> other (text)
FREE_TEXT_MIN_RATIO = 0.5
MAX_LEVELS_SHOWN = 50         # levels are listed only up to this many
HIST_BINS = 30

# --- Name-token rules (word fragments, split on non-alphanumerics) -------------
KEY_TOKENS = {"ID", "IDS", "COD", "CODIGO", "CODE", "KEY", "CHAVE", "UUID", "GUID", "SKU", "CPF", "CNPJ", "CRM"}
CODE_TOKENS = {"COD", "CODIGO", "CODE", "CEP", "ZIP", "BLOCO", "BLOCK"}
NUMBERED_SUFFIXES = {"NUM", "NUMERO", "NR", "NO"}
COUNT_TOKENS = {"QTD", "QTDE", "QTY", "QUANT", "QUANTIDADE", "QUANTITY", "DIAS", "DAYS", "PX", "UNIDADES",
                "UNITS", "COUNT", "CONTAGEM"}
MEASURE_TOKENS = {"VALOR", "VALUE", "PRECO", "PRICE", "FATURAMENTO", "REVENUE", "COMISSAO", "COMMISSION",
                  "CUSTO", "COST", "AMOUNT"}
ORDINAL_TOKENS = {"CATEGORIA", "CATEGORY", "NIVEL", "LEVEL", "CLASSE", "CLASS", "FAIXA", "GRAU", "TIER",
                  "RANK", "SCORE", "PORTE", "ESTAGIO", "STAGE", "SEVERIDADE", "SEVERITY"}
# Strong personal tokens: the column holds names / personal registrations -> never show values or levels.
PERSONAL_TOKENS = {"CPF", "CNPJ", "CRM", "EMAIL", "TELEFONE", "PHONE", "ENDERECO", "ADDRESS",
                   "BAIRRO", "CADASTRO"}
# Entity tokens: personal only when the column's levels are LABELS naming that entity (a client / doctor /
# vendor as text) - not when it is a 0/1 flag or an ordinal category ABOUT the entity.
ENTITY_TOKENS = {"CLIENTE", "CLIENT", "PACIENTE", "PATIENT", "MEDICO", "DOCTOR", "VENDEDOR", "VENDOR",
                 "FUNCIONARIO", "EMPLOYEE"}
# Known ordered scales (casefolded, accents removed) - a column whose levels all
# belong to ONE of these is flagged ordinal and shown in this order.
ORDINAL_SCALES = [
    ["low", "medium", "high"], ["baixo", "medio", "alto"], ["small", "medium", "large"],
    ["pequeno", "medio", "grande"], ["never", "rarely", "sometimes", "often", "always"],
    ["bronze", "silver", "gold", "platinum"],
]

_DATE_PATTERN = re.compile(r"^\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})")


# =============================================================================
# Result containers
# =============================================================================

@dataclass
class ColumnProfile:
    table: str
    column: str
    stored_type: str          # dtype exactly as pandas holds it
    stored_family: str        # integer / float / boolean / text / datetime / mixed / empty
    stat_type: str
    why: str
    mismatch_kind: str | None
    n_rows: int
    n_missing: int
    n_distinct: int
    unique_pct: float         # distinct / non-null, in %
    duplicates: int           # non-null values beyond the first occurrence (non-null - distinct)
    personal: bool
    detail: dict = field(default_factory=dict)

    @property
    def missing_pct(self) -> float:
        return 100.0 * self.n_missing / self.n_rows if self.n_rows else 0.0


@dataclass
class TableProfile:
    table: str
    n_rows: int
    n_columns: int
    missing_cells_pct: float
    duplicate_rows: int


@dataclass
class Profile:
    tables: list[TableProfile]
    columns: list[ColumnProfile]

    def inventory(self) -> pd.DataFrame:
        """One row per column - the table the page displays and filters."""
        return pd.DataFrame([{
            "table": c.table, "column": c.column, "stored_type": c.stored_type, "stat_type": c.stat_type,
            "why": c.why, "mismatch": c.mismatch_kind is not None, "mismatch_kind": c.mismatch_kind or "",
            "missing_pct": c.missing_pct, "n_distinct": c.n_distinct, "unique_pct": c.unique_pct,
            "duplicates": c.duplicates, "personal": c.personal,
        } for c in self.columns])

    def get(self, table: str, column: str) -> ColumnProfile:
        return next(c for c in self.columns if c.table == table and c.column == column)


# =============================================================================
# Helpers
# =============================================================================

def name_tokens(column: str) -> list[str]:
    return [t for t in re.split(r"[^A-Za-z0-9]+", str(column).upper()) if t]


def _fold(text: str) -> str:
    import unicodedata
    return unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode().casefold().strip()


def stored_family(s: pd.Series) -> str:
    """Coarse family of how the column is STORED, also looking inside
    `object` columns (a bool column with a missing value is object, not
    bool; Supabase JSON can also land numbers in object columns)."""
    if pd.api.types.is_bool_dtype(s):
        return "boolean"
    if pd.api.types.is_datetime64_any_dtype(s):
        return "datetime"
    if pd.api.types.is_integer_dtype(s):
        return "integer"
    if pd.api.types.is_float_dtype(s):
        return "float"
    inferred = pd.api.types.infer_dtype(s, skipna=True)
    return {
        "string": "text", "boolean": "boolean", "integer": "integer", "floating": "float",
        "mixed-integer-float": "float", "decimal": "float", "empty": "empty",
        "datetime": "datetime", "datetime64": "datetime", "date": "datetime",
    }.get(inferred, "mixed")


def _numeric_values(s: pd.Series, family: str) -> pd.Series | None:
    """Non-null numeric values of the column, or None when it is not numeric.
    Text counts as numeric when >= NUMERIC_TEXT_SHARE of it parses."""
    nn = s.dropna()
    if family in ("integer", "float"):
        return pd.to_numeric(nn, errors="coerce").dropna()
    if family in ("text", "mixed") and len(nn):
        parsed = pd.to_numeric(nn.astype(str).str.strip(), errors="coerce")
        if parsed.notna().mean() >= NUMERIC_TEXT_SHARE:
            return parsed.dropna()
    return None


def _looks_like_date_text(s: pd.Series, family: str) -> bool:
    if family != "text":
        return False
    nn = s.dropna()
    if nn.empty:
        return False
    sample = nn.iloc[:: max(1, len(nn) // 2000)].astype(str)
    return sample.map(lambda v: bool(_DATE_PATTERN.match(v))).mean() >= DATE_TEXT_SHARE


def _period_code_kind(numbers: pd.Series) -> str | None:
    """"YYYYMM" / "YYYYMMDD" when every value is an integer shaped like one of
    those calendar codes (valid year range and month/day), else None."""
    if numbers.empty or not (numbers % 1 == 0).all():
        return None
    v = numbers.astype("int64")
    if v.between(190001, 299912).all() and v.mod(100).between(1, 12).all():
        return "YYYYMM"
    if v.between(19000101, 29991231).all() and (v // 100 % 100).between(1, 12).all() and v.mod(100).between(1, 31).all():
        return "YYYYMMDD"
    return None


def is_personal(column: str, stat_type: str, labels: bool = True) -> bool:
    """Columns whose values (or levels) must never be shown. `labels` = the
    column's values are text labels (not 0/1 digits or booleans)."""
    tokens = set(name_tokens(column))
    return (
        stat_type in (IDENTIFIER, OTHER_TEXT)
        or tokens in ({"NOME"}, {"NAME"})   # a bare "name" column; NOME_BLOCO / PER_NOME are not people
        or bool(tokens & PERSONAL_TOKENS)
        or (labels and stat_type != ORDINAL and bool(tokens & ENTITY_TOKENS))
    )


def natural_order(levels: list) -> list:
    """Numeric-aware order: numbers by value, other text alphabetically."""
    def key(level):
        text = str(level)
        match = re.match(r"^\s*(-?\d+(?:\.\d+)?)", text)
        return (0, float(match.group(1)), text) if match else (1, 0.0, _fold(text))
    return sorted(levels, key=key)


def _ordinal_order(levels: list, tokens: set[str]) -> list | None:
    """The assumed order of an ordinal column, or None if it is not ordinal."""
    if not (3 <= len(levels) <= MAX_ORDINAL_LEVELS):
        return None
    folded = {_fold(level): level for level in levels}
    for scale in ORDINAL_SCALES:
        if set(folded) <= set(scale):
            return [folded[k] for k in scale if k in folded]
    if tokens & ORDINAL_TOKENS:
        return natural_order(levels)
    return None


# =============================================================================
# Column classification
# =============================================================================

def classify_column(column: str, s: pd.Series) -> tuple[str, str, str | None]:
    """(statistical type, why, mismatch kind) for one column. Rules, in order:
    empty -> date -> identifier -> binary -> numeric (ordinal / code /
    discrete / continuous) -> text (ordinal / free text / nominal)."""
    family = stored_family(s)
    nn = s.dropna()
    n_nn = len(nn)
    if n_nn == 0:
        return OTHER_TEXT, "all values missing", None
    tokens_list = name_tokens(column)
    tokens = set(tokens_list)
    n_distinct = nn.nunique()

    if family == "datetime":
        return OTHER_DATE, "datetime dtype", None
    if _looks_like_date_text(s, family):
        return OTHER_DATE, f"text that matches a date pattern (>= {NUMERIC_TEXT_SHARE:.0%})", MM_DATE_AS_TEXT

    numbers = _numeric_values(s, family)
    is_numeric_dtype = family in ("integer", "float")
    integer_valued = numbers is not None and bool((numbers % 1 == 0).all())

    # --- identifier: key-like name, or unique per row (integer-like / text values only)
    key_name = bool(tokens & KEY_TOKENS)
    unique_per_row = (
        n_nn >= MIN_ROWS_FOR_UNIQUE and n_distinct == n_nn
        and family != "boolean" and (numbers is None or integer_valued)
    )
    if (key_name or unique_per_row) and family != "boolean":
        reasons = []
        if unique_per_row:
            reasons.append("unique per row")
        if key_name:
            reasons.append("key-like name")
        mismatch = MM_ID_AS_NUMBER if is_numeric_dtype else None
        return IDENTIFIER, " + ".join(reasons), mismatch

    # --- binary: exactly 2 distinct values
    if family == "boolean" or n_distinct == 2:
        if family == "boolean":
            return BINARY, "boolean dtype", None
        if is_numeric_dtype:
            return BINARY, "exactly 2 distinct values", MM_FLAG_AS_NUMBER
        if numbers is not None:
            return BINARY, "exactly 2 distinct values (digits)", MM_FLAG_AS_TEXT
        return BINARY, "exactly 2 distinct values", None

    # --- numeric values (stored as numbers, or as text that parses)
    if numbers is not None:
        period = _period_code_kind(numbers)
        if period and not tokens & COUNT_TOKENS:
            return OTHER_DATE, f"integer values shaped like {period} calendar codes", MM_DATE_AS_NUMBER
        text_mismatch = None if is_numeric_dtype else MM_NUMBERS_AS_TEXT
        levels = sorted(numbers.unique().tolist())
        if integer_valued and (tokens & ORDINAL_TOKENS) and 3 <= len(levels) <= MAX_ORDINAL_LEVELS:
            return ORDINAL, "integer levels + ordered-scale name (assumed)", text_mismatch
        if integer_valued and not (tokens & COUNT_TOKENS) and (
            (tokens & CODE_TOKENS)
            or (tokens_list[-1:] and tokens_list[-1] in NUMBERED_SUFFIXES and n_distinct <= MANY_DISTINCT)
        ):
            kind = MM_ID_AS_NUMBER if is_numeric_dtype else None
            return NOMINAL, f"numeric code, not a quantity ({n_distinct} levels)", kind
        if tokens & MEASURE_TOKENS and not tokens & COUNT_TOKENS:
            return CONTINUOUS, f"measured amount (money-like name), {n_distinct:,} distinct values", text_mismatch
        float_as_int = family == "float" and integer_valued
        float_mismatch = MM_INT_AS_FLOAT if float_as_int else None
        if integer_valued and ((tokens & COUNT_TOKENS) or n_distinct <= MANY_DISTINCT):
            why = "whole numbers, name suggests a count" if tokens & COUNT_TOKENS else \
                f"whole numbers, few values ({n_distinct})"
            return DISCRETE, why, text_mismatch or float_mismatch
        if integer_valued:
            return CONTINUOUS, f"measured, many values ({n_distinct}), whole numbers only", text_mismatch or float_mismatch
        return CONTINUOUS, f"decimals, {n_distinct:,} distinct values", text_mismatch

    # --- text categories
    levels = nn.unique().tolist()
    order = _ordinal_order(levels, tokens)
    if order is not None:
        return ORDINAL, "ordered-scale levels (assumed)", None
    if n_distinct > FREE_TEXT_MIN_LEVELS and n_distinct / n_nn > FREE_TEXT_MIN_RATIO:
        return OTHER_TEXT, f"free-text-like: {n_distinct:,} distinct in {n_nn:,}", None
    if n_distinct == 1:
        return NOMINAL, "single level (constant)", None
    return NOMINAL, f"text categories, {n_distinct:,} levels, no natural order", None


# =============================================================================
# Column detail (aggregates only)
# =============================================================================

def _numeric_detail(numbers: pd.Series, discrete: bool) -> dict:
    values = numbers.to_numpy(dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {}
    q1, median, q3 = np.percentile(values, [25, 50, 75])
    skew = float(pd.Series(values).skew()) if values.size > 2 else 0.0
    stats = {
        "min": float(values.min()), "q1": float(q1), "median": float(median), "mean": float(values.mean()),
        "q3": float(q3), "max": float(values.max()), "zeros_pct": 100.0 * float((values == 0).mean()),
        "negative_pct": 100.0 * float((values < 0).mean()), "skew": 0.0 if np.isnan(skew) else skew,
    }
    distinct = np.unique(values)
    if discrete and distinct.size <= HIST_BINS:
        counts = [int((values == v).sum()) for v in distinct]
        bins = pd.DataFrame({"label": [f"{v:g}" for v in distinct], "start": distinct, "end": distinct, "count": counts})
    else:
        counts, edges = np.histogram(values, bins=HIST_BINS)
        bins = pd.DataFrame({
            "label": [f"{edges[i]:g} - {edges[i + 1]:g}" for i in range(len(counts))],
            "start": edges[:-1], "end": edges[1:], "count": counts,
        })
    return {"kind": "numeric", "stats": stats, "bins": bins}


def _levels_detail(s: pd.Series, column: str, stat_type: str, personal: bool) -> dict:
    nn = s.dropna()
    counts = nn.astype(str).value_counts()
    n_levels = int(counts.size)
    largest_pct = 100.0 * float(counts.iloc[0]) / len(nn) if len(nn) else 0.0
    detail = {"kind": "levels", "n_levels": n_levels, "largest_level_pct": largest_pct, "levels": None, "order": None}
    if personal:
        detail["hidden_reason"] = "personal-looking column - levels not shown"
        return detail
    if n_levels > MAX_LEVELS_SHOWN:
        detail["hidden_reason"] = f"{n_levels:,} levels - too many to list"
        return detail
    counts.index = counts.index.map(str)
    order = None
    if stat_type == ORDINAL:
        order = [str(x) for x in (_ordinal_order(list(counts.index), set(name_tokens(column)))
                                 or natural_order(list(counts.index)))]
        counts = counts.reindex(order)
    elif stat_type == BINARY:
        counts = counts.reindex(natural_order(list(counts.index)))
    table = pd.DataFrame({"level": counts.index, "count": counts.to_numpy()})
    table["pct"] = 100.0 * table["count"] / len(nn)
    detail["levels"] = table
    detail["order"] = order
    return detail


def _identifier_detail(nn: pd.Series) -> dict:
    repeats = nn.value_counts()
    return {
        "kind": "identifier", "values_repeated": int((repeats > 1).sum()),
        "max_repeat": int(repeats.iloc[0]) if len(repeats) else 0,
    }


def _date_detail(s: pd.Series) -> dict:
    if not pd.api.types.is_datetime64_any_dtype(s):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            s = pd.to_datetime(s, errors="coerce")
    nn = s.dropna()
    if nn.empty:
        return {"kind": "date"}
    return {
        "kind": "date", "min": nn.min(), "max": nn.max(), "span_days": int((nn.max() - nn.min()).days),
        "n_months": int(nn.dt.to_period("M").nunique()),
    }


# =============================================================================
# Profiling
# =============================================================================

def profile_column(table: str, column: str, s: pd.Series) -> ColumnProfile:
    family = stored_family(s)
    stat_type, why, mismatch = classify_column(column, s)
    nn = s.dropna()
    n_nn = len(nn)
    n_distinct = int(nn.nunique()) if n_nn else 0
    personal = is_personal(column, stat_type, labels=family == 'text' and _numeric_values(s, family) is None)
    profile = ColumnProfile(
        table=table, column=str(column), stored_type=str(s.dtype), stored_family=family,
        stat_type=stat_type, why=why, mismatch_kind=mismatch, n_rows=len(s), n_missing=len(s) - n_nn,
        n_distinct=n_distinct, unique_pct=100.0 * n_distinct / n_nn if n_nn else 0.0,
        duplicates=n_nn - n_distinct, personal=personal,
    )
    if n_nn == 0:
        return profile
    if stat_type in (CONTINUOUS, DISCRETE):
        numbers = _numeric_values(s, family)
        if numbers is not None and not personal:
            profile.detail = _numeric_detail(numbers, discrete=stat_type == DISCRETE)
    elif stat_type in (NOMINAL, BINARY, ORDINAL):
        profile.detail = _levels_detail(s, str(column), stat_type, personal)
    elif stat_type == IDENTIFIER:
        profile.detail = _identifier_detail(nn)
    elif stat_type == OTHER_DATE:
        profile.detail = _date_detail(s)
    else:
        profile.detail = {"kind": "text"}
    return profile


def profile_table(name: str, df: pd.DataFrame) -> tuple[TableProfile, list[ColumnProfile]]:
    columns = [profile_column(name, str(c), df[c]) for c in df.columns]
    n_cells = df.shape[0] * df.shape[1]
    table = TableProfile(
        table=name, n_rows=len(df), n_columns=df.shape[1],
        missing_cells_pct=100.0 * float(df.isna().sum().sum()) / n_cells if n_cells else 0.0,
        duplicate_rows=int(df.duplicated().sum()) if len(df) else 0,
    )
    return table, columns


def profile_tables(tables: dict[str, pd.DataFrame]) -> Profile:
    table_profiles, columns = [], []
    for name, df in tables.items():
        table_profile, column_profiles = profile_table(name, df)
        table_profiles.append(table_profile)
        columns.extend(column_profiles)
    return Profile(table_profiles, columns)


# =============================================================================
# Insights (5-8 findings, each with numbers, a risk and a fix)
# =============================================================================

@dataclass
class Insight:
    title: str
    finding: str
    risk: str
    fix: str


def _num(x: float) -> str:
    return f"{x:,.0f}" if abs(x) >= 100 else f"{x:,.2f}"


def _names(columns: list[ColumnProfile], limit: int = 6) -> str:
    items = [f"`{c.table}.{c.column}`" for c in columns]
    return ", ".join(items[:limit]) + (f" and {len(items) - limit} more" if len(items) > limit else "")


def build_insights(profile: Profile) -> list[Insight]:
    cols = profile.columns
    total = len(cols)
    insights: list[Insight] = []
    if not total:
        return insights

    mism = [c for c in cols if c.mismatch_kind]
    by_kind: dict[str, list[ColumnProfile]] = {}
    for c in mism:
        by_kind.setdefault(c.mismatch_kind, []).append(c)

    insights.append(Insight(
        "Stored type misleads in many columns" if mism else "Stored types match the statistical types",
        f"{len(mism)} of {total} columns ({100 * len(mism) / total:.0f}%) have a stored type that misleads"
        + (": " + "; ".join(f"{len(v)} {k}" for k, v in by_kind.items()) + "." if mism else "."),
        "Code that trusts the dtype (sum, mean, sort, ==, joins) silently computes the wrong thing "
        "on these columns." if mism else "No dtype-driven mistakes were found by these rules.",
        "Cast each one at the loading boundary (transform._ler) to its statistical type: string for "
        "IDs/codes, boolean for flags, datetime for dates, numeric for numbers." if mism else "Keep the check on new data.",
    ))

    ids_num = by_kind.get(MM_ID_AS_NUMBER, [])
    if ids_num:
        insights.append(Insight(
            "Identifiers / codes stored as numbers",
            f"{len(ids_num)} column(s) hold IDs or codes as numbers: {_names(ids_num)}.",
            "An ID can be averaged, summed or binned like a measure, and numeric IDs lose leading "
            "zeros and become float when a value is missing.",
            "Store them as string/category and exclude them from numeric summaries.",
        ))

    flags = by_kind.get(MM_FLAG_AS_NUMBER, []) + by_kind.get(MM_FLAG_AS_TEXT, [])
    binary_all = [c for c in cols if c.stat_type == BINARY]
    if flags:
        insights.append(Insight(
            "Binary flags not stored as booleans",
            f"{len(flags)} of {len(binary_all)} binary columns are numbers or digit-text: {_names(flags)}.",
            "A flag can be averaged or summed as if it were a quantity, and flag columns of the same "
            "kind end up in different types (int 1 vs text \"1\"), so a comparison with the wrong type "
            "silently matches nothing.",
            "Convert to boolean (or one agreed type) once, at load time, and compare against True/False.",
        ))

    text_nums = by_kind.get(MM_NUMBERS_AS_TEXT, [])
    if text_nums:
        insights.append(Insight(
            "Numbers stored as text",
            f"{len(text_nums)} column(s) are text but {NUMERIC_TEXT_SHARE:.0%}+ of their values parse as "
            f"numbers: {_names(text_nums)}.",
            "Sorting is alphabetical (\"10\" < \"9\"), sums fail or concatenate, and charts treat them as categories.",
            "Convert with pd.to_numeric(errors=\"coerce\") and check how many values become missing.",
        ))

    date_bad = by_kind.get(MM_DATE_AS_TEXT, []) + by_kind.get(MM_DATE_AS_NUMBER, [])
    n_dates = sum(1 for c in cols if c.stat_type == OTHER_DATE)
    if date_bad:
        insights.append(Insight(
            "Dates not stored as dates",
            f"{len(date_bad)} of {n_dates} date columns are text or numbers (period codes like 202607): {_names(date_bad)}.",
            "No date arithmetic or month grouping; text sorts wrongly if formats differ, and a period code "
            "stored as a float can be averaged or shown as 202,608.2.",
            "Parse to datetime in the loader (as _DATE_COLUMNS already does for known dates); turn YYYYMM codes "
            "into the first day of the month.",
        ))

    id_cols = [c for c in cols if c.stat_type == IDENTIFIER]
    near_unique = [c for c in id_cols if c.unique_pct >= 90 and c.duplicates > 0]
    foreign = [c for c in id_cols if c.unique_pct < 90 and c.duplicates > 0]
    if near_unique:
        worst = max(near_unique, key=lambda c: c.duplicates)
        insights.append(Insight(
            "Row-level identifiers that still repeat",
            f"{len(near_unique)} identifier column(s) are 90%+ unique yet repeat: {_names(near_unique)} - e.g. "
            f"`{worst.table}.{worst.column}` is {worst.unique_pct:.1f}% unique with {worst.duplicates:,} repeats "
            f"(one value up to {worst.detail.get('max_repeat', 0):,} times). The other {len(foreign)} identifier "
            "column(s) repeat by design (they point to a client, doctor or employee shared by many rows).",
            "A row is not one entity: counting rows instead of distinct IDs overstates, and a merge on this key "
            "alone fans out and inflates totals.",
            "Count distinct IDs; join on the composite key that is unique (and assert uniqueness after merging).",
        ))
    elif id_cols:
        insights.append(Insight(
            "Identifiers are consistent",
            f"{len(id_cols)} identifier columns; none that should be one-per-row repeats.",
            "Low risk inside each table.", "Still validate uniqueness before joining.",
        ))

    duplicated = [tp for tp in profile.tables if tp.duplicate_rows]
    if duplicated:
        worst = max(duplicated, key=lambda tp: tp.duplicate_rows / max(tp.n_rows, 1))
        insights.append(Insight(
            "Fully duplicated rows",
            f"{len(duplicated)} of {len(profile.tables)} tables contain exact duplicate rows; worst: `{worst.table}` "
            f"with {worst.duplicate_rows:,} of {worst.n_rows:,} rows ({100 * worst.duplicate_rows / worst.n_rows:.1f}%).",
            "Observations are counted (and their values summed) more than once, inflating totals and counts.",
            "Check whether the repeat is a real second event; if not, drop exact duplicates in the loader and "
            "add a row key so the grain is explicit.",
        ))

    numeric_cols = [c for c in cols if c.detail.get("stats") and c.stat_type in (CONTINUOUS, DISCRETE)]
    extreme = sorted(
        (c for c in numeric_cols if c.detail["stats"]["median"] > 0 and c.detail["stats"]["skew"] > 5
         and c.detail["stats"]["max"] > 50 * c.detail["stats"]["median"]),
        key=lambda c: -c.detail["stats"]["max"] / c.detail["stats"]["median"],
    )
    if extreme:
        top = extreme[:3]
        insights.append(Insight(
            "Extreme right-skew and outliers in numeric columns",
            f"{len(extreme)} numeric column(s) have a maximum over 50x their median and skew above 5; e.g. "
            + "; ".join(f"`{c.table}.{c.column}` median {_num(c.detail['stats']['median'])}, mean "
                        f"{_num(c.detail['stats']['mean'])}, max {_num(c.detail['stats']['max'])}" for c in top) + ".",
            "A handful of rows dominate sums and means (or are entry errors, such as days of stock measured in "
            "decades), so averages and charts describe the outliers, not the typical row.",
            "Inspect the largest rows, report median / trimmed mean next to the mean, and use a log scale.",
        ))

    sparse = sorted((c for c in cols if c.missing_pct >= 20), key=lambda c: -c.missing_pct)
    if sparse:
        insights.append(Insight(
            "Columns with a lot of missing data",
            f"{len(sparse)} column(s) are 20%+ missing, worst: `{sparse[0].table}.{sparse[0].column}` "
            f"({sparse[0].missing_pct:.0f}%).",
            "Averages and rates cover only the filled rows; a blank can mean 'none' or 'unknown'.",
            "Document what blank means per column and fill it explicitly (as the project does with '(not informed)').",
        ))

    float_ints = by_kind.get(MM_INT_AS_FLOAT, [])
    if float_ints:
        insights.append(Insight(
            "Integers promoted to float",
            f"{len(float_ints)} column(s) contain only whole numbers but are stored as float "
            f"(typically because missing values rule out int64): {_names(float_ints)}.",
            "Counts show as 3.0, exact comparisons and joins on them become fragile.",
            "Use pandas nullable Int64 for counts that can be missing.",
        ))

    inconsistent = _cross_table_type_conflicts(cols)
    if inconsistent:
        name, items = inconsistent[0]
        insights.append(Insight(
            "Same column name, different stored type across tables",
            f"{len(inconsistent)} column name(s) appear with different stored types in different tables "
            f"(e.g. `{name}`: " + ", ".join(f"{t}={d}" for t, d in items) + ").",
            "Merging on it can fail or silently match nothing; the same variable behaves differently by table.",
            "Agree one type per shared column and cast in the loader before any merge.",
        ))

    high_card = sorted((c for c in cols if c.stat_type == NOMINAL and c.n_distinct > MAX_LEVELS_SHOWN), key=lambda c: -c.n_distinct)
    if high_card:
        insights.append(Insight(
            "Nominal columns with very many levels",
            f"{len(high_card)} nominal column(s) have more than {MAX_LEVELS_SHOWN} levels, most: "
            f"`{high_card[0].table}.{high_card[0].column}` ({high_card[0].n_distinct:,}).",
            "Charts and one-hot encodings explode, small levels are noisy, and spelling variants split one level in two.",
            "Group rare levels, standardise spelling and key on a code instead of the label.",
        ))

    ordinals = [c for c in cols if c.stat_type == ORDINAL]
    if ordinals:
        insights.append(Insight(
            "Ordinal order is an assumption",
            f"{len(ordinals)} column(s) were classified ordinal from name/levels only: {_names(ordinals)}.",
            "Text sorts alphabetically, so charts and comparisons use the wrong order, and the assumed order may be wrong.",
            "Confirm the order with the data owner, then store as an ordered pandas Categorical.",
        ))

    return insights[:8]


def _cross_table_type_conflicts(cols: list[ColumnProfile]) -> list[tuple[str, list[tuple[str, str]]]]:
    groups: dict[str, list[ColumnProfile]] = {}
    for c in cols:
        groups.setdefault(c.column.upper(), []).append(c)
    conflicts = []
    for name, items in groups.items():
        if len({c.stored_type for c in items}) > 1:
            conflicts.append((name, [(c.table, c.stored_type) for c in items]))
    return sorted(conflicts, key=lambda x: -len(x[1]))


# =============================================================================
# Result report (paste-ready markdown, generated from the profile)
# =============================================================================

def _block(title: str, where: str, ran: str, showed: list[str], means: str, problems: list[str]) -> str:
    lines = [f"### {title}", f"- **WHERE:** {where}", f"- **WHAT I RAN:** {ran}", "- **WHAT IT SHOWED:**"]
    lines += [f"  - {x}" for x in (showed or ["nothing of this kind in the data"])]
    lines += [f"- **WHAT IT MEANS FOR THE PROJECT:** {means}", "- **PROBLEMS OR SURPRISES:**"]
    lines += [f"  - {x}" for x in (problems or ["none found by these rules"])]
    return "\n".join(lines)


def _fmt(x: float) -> str:
    return f"{x:,.0f}" if abs(x) >= 1000 or float(x).is_integer() else f"{x:,.2f}"


def build_report(profile: Profile, insights: list[Insight], page_hint: str = "streamlit run data_app_gestao.py") -> str:
    cols = profile.columns
    names = [t.table for t in profile.tables]
    by = lambda *kinds: [c for c in cols if c.stat_type in kinds]  # noqa: E731
    ref = lambda c: f"`{c.table}.{c.column}`"  # noqa: E731
    out = [
        "# RESULT REPORT - Data types profile",
        f"**PAGE:** \"Data types profile\" in the Streamlit app (sidebar navigation). Run: `{page_hint}`. "
        "Code: `data_types_profile.py` (analysis) + `page_data_types_profile` in `data_app_gestao.py` (UI). "
        "Only counts, percentages and aggregates appear - no raw rows, no values of identifier / personal columns.",
    ]

    # 1. structured data, variable, observation
    shown = [f"{t.table}: {t.n_rows:,} observations (rows) x {t.n_columns} variables (columns), "
             f"{t.missing_cells_pct:.1f}% empty cells, {t.duplicate_rows:,} fully duplicated rows" for t in profile.tables]
    problems = [f"{t.table} has {t.duplicate_rows:,} fully duplicated rows" for t in profile.tables if t.duplicate_rows]
    out.append(_block(
        "1. Structured data, variable, observation", f"{len(names)} tables: {', '.join(names)}",
        "profile_table() on every table loaded by transform._ler (shape, empty cells, duplicated rows).", shown,
        f"All {len(names)} tables are structured data: a fixed set of named columns and one row per record. "
        f"Together {sum(t.n_rows for t in profile.tables):,} rows and {sum(t.n_columns for t in profile.tables)} columns. "
        "What one row stands for (its grain) is not declared in the data - it is read from the identifier columns (block 5).",
        problems,
    ))

    # 2. data type, stored vs statistical
    inv = profile.inventory()
    stored = inv["stored_type"].value_counts()
    mism = [c for c in cols if c.mismatch_kind]
    kinds: dict[str, int] = {}
    for c in mism:
        kinds[c.mismatch_kind] = kinds.get(c.mismatch_kind, 0) + 1
    out.append(_block(
        "2. Data type and stored vs. statistical type", "every column of every table",
        "dtype read per column, statistical type decided by rule (see the 'why' column), the two compared.",
        ["stored types: " + ", ".join(f"{k} x{v}" for k, v in stored.items()),
         "statistical types: " + ", ".join(f"{k} x{n}" for k in STAT_TYPES if (n := len(by(k))))],
        "The dtype says how a value is stored; the statistical type says what it means. Code that trusts the dtype "
        "is only right where the two agree.",
        [f"{len(mism)} of {len(cols)} columns have a misleading stored type: "
         + "; ".join(f"{k} x{v}" for k, v in kinds.items())] if mism else [],
    ))

    # 3. numeric
    numeric = by(CONTINUOUS, DISCRETE)
    shown = []
    for c in numeric:
        st = c.detail.get("stats")
        if st:
            shown.append(f"{ref(c)} ({c.stat_type}): median {_fmt(st['median'])}, range {_fmt(st['min'])} to "
                         f"{_fmt(st['max'])}, {st['zeros_pct']:.0f}% zeros, skew {st['skew']:.1f}")
    skewed = [c for c in numeric if c.detail.get("stats", {}).get("skew", 0) > 2]
    zeros = [c for c in numeric if c.detail.get("stats", {}).get("zeros_pct", 0) >= 30]
    out.append(_block(
        "3. Numeric: continuous and discrete", ", ".join(ref(c) for c in numeric[:8]) + (" ..." if len(numeric) > 8 else ""),
        "numeric summary (quartiles, mean, zeros, skew) and a histogram per numeric column.", shown,
        "Continuous measures (decimals, many values) can be averaged and binned; discrete counts (whole numbers) "
        "are summed and compared exactly, and are never fractional.",
        ([f"right-skewed (skew > 2): {', '.join(ref(c) for c in skewed)} - mean is pulled up, prefer the median"] if skewed else [])
        + ([f"30%+ zeros: {', '.join(ref(c) for c in zeros)}"] if zeros else [])
        + [f"{ref(c)} is whole numbers stored as float" for c in numeric if c.mismatch_kind == MM_INT_AS_FLOAT]
        + [f"{ref(c)} is numbers stored as text" for c in numeric if c.mismatch_kind == MM_NUMBERS_AS_TEXT],
    ) if numeric else _block("3. Numeric: continuous and discrete", "-", "-", [], "-", []))

    # 4. categorical
    cat = by(NOMINAL, BINARY, ORDINAL)
    shown = [f"{k}: {len(by(k))} column(s)" for k in (NOMINAL, BINARY, ORDINAL)]
    shown += [f"{ref(c)} ({c.stat_type}): {c.n_distinct:,} levels, largest level {c.detail.get('largest_level_pct', 0):.1f}%"
              for c in cat[:12]]
    for c in by(ORDINAL):
        order = c.detail.get("order")
        shown.append(f"{ref(c)} assumed order: {' < '.join(order)}" if order else f"{ref(c)} assumed ordinal (order not listed)")
    constant = [c for c in cat if c.n_distinct == 1]
    many = [c for c in by(NOMINAL) if c.n_distinct > MAX_LEVELS_SHOWN]
    out.append(_block(
        "4. Categorical: nominal, binary, ordinal and level", f"{len(cat)} columns",
        "level counts per categorical column (levels listed only for non-personal columns with <= "
        f"{MAX_LEVELS_SHOWN} levels); ordinal order is an assumption and is shown.", shown,
        "A level is one distinct value of a categorical variable. Nominal levels have no order, binary has exactly two, "
        "ordinal levels have an order that must be stored explicitly.",
        ([f"constant (1 level): {', '.join(ref(c) for c in constant)}"] if constant else [])
        + ([f"more than {MAX_LEVELS_SHOWN} levels: {', '.join(f'{ref(c)} ({c.n_distinct:,})' for c in many)}"] if many else [])
        + ([f"{len(by(ORDINAL))} ordinal column(s) rest on an assumed order - confirm with the data owner"] if by(ORDINAL) else []),
    ))

    # 5. identifier
    ids = by(IDENTIFIER)
    shown = [f"{ref(c)}: {c.unique_pct:.1f}% unique, {c.duplicates:,} repeated, stored {c.stored_type} ({c.why})" for c in ids]
    out.append(_block(
        "5. Identifier", ", ".join(ref(c) for c in ids[:10]) + (" ..." if len(ids) > 10 else "") if ids else "-",
        "unique %, repeated values and stored type of every identifier column (values never shown).", shown,
        "Identifiers name things; they are not quantities. Repeats mean a row is not one entity, so count distinct IDs "
        "and join on unique keys.",
        [f"{ref(c)} is stored as a number, so it can be averaged" for c in ids if c.mismatch_kind == MM_ID_AS_NUMBER]
        + [f"{ref(c)} is {c.unique_pct:.1f}% unique but repeats ({c.duplicates:,} repeats) - a row is not one entity"
           for c in ids if c.unique_pct >= 90 and c.duplicates]
        + ([f"{len(fk)} other identifier column(s) repeat by design (foreign keys to a client / doctor / employee / patient)"]
           if (fk := [c for c in ids if c.unique_pct < 90 and c.duplicates]) else []),
    ) if ids else _block("5. Identifier", "-", "-", [], "-", []))

    out.append("## MISMATCH LIST (column, stored type -> statistical type, why)")
    out += [f"- {ref(c)}: {c.stored_type} -> {c.stat_type}, {c.mismatch_kind} ({c.why})" for c in mism] or ["- none found"]
    out.append("## TOP INSIGHTS")
    out += [f"{i}. **{x.title}** - {x.finding} Risk: {x.risk} Fix: {x.fix}" for i, x in enumerate(insights, 1)]
    return "\n\n".join(out[:2]) + "\n\n" + "\n\n".join(out[2:7]) + "\n\n" + "\n".join(out[7:])
