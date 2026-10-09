"""Percentiles and boxplots - generic analysis of the numeric columns of every
table the project loads, built to practise these concepts: percentile, median,
quartiles (Q1, Q2, Q3), IQR, boxplot (box, median line), whisker and cap,
fences and the 1.5 x IQR rule, outlier, robust (mean vs. median / IQR),
comparing groups with boxplots, and quartile calculation (position and
interpolation).

No Streamlit dependency (same idea as transform.py / data_types_profile.py).
Which columns are numeric, categorical or personal comes from
data_types_profile; no column name is hard-coded.

PRIVACY: every result holds only column names, counts, percentages and
aggregates (percentiles, fences, whisker ends). Group labels are listed only
for non-personal categorical columns with few levels. No rows and no
identifier values.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

import data_types_profile as dtp
import location_estimates as le
import tidy_rectangular as tr

MIN_N = 30
PERCENTILES = [1, 5, 10, 25, 50, 75, 90, 95, 99]
FENCE = 1.5
FAR_FENCE = 3.0
QUARTILE_METHODS = ["linear", "lower", "higher", "midpoint", "nearest", "weibull"]
MIN_LEVELS, MAX_LEVELS = 2, 12
MAX_GROUP_COLUMNS = 2
SMALL_GROUP = 10
MIN_GROUP_FOR_FENCE_TEST = 30
FLAG_TOKENS = {"SUSPEITA", "SUSPECT", "OUTLIER", "ATIPICO", "ANOMALY", "ANOMALIA"}


@dataclass
class BoxplotResult:
    columns: pd.DataFrame      # percentiles, box, whiskers, fences, outliers per numeric column
    quartiles: pd.DataFrame    # how Q1, median and Q3 are located (position, interpolation) and how methods differ
    groups: pd.DataFrame       # one boxplot per level of a grouping column
    group_summary: pd.DataFrame  # per (table, measure, grouping): do the boxes overlap, do mean and median rank alike
    fence_flags: pd.DataFrame  # does a project flag reproduce a per-group Tukey fence?


# =============================================================================
# Estimators
# =============================================================================

def quartile_position(n: int, p: float) -> tuple[float, int, float]:
    """The default (linear) rule: position = (n - 1) * p on the sorted values,
    counted from 0. Returns (position, lower index, fraction toward the next value)."""
    pos = (n - 1) * p
    lo = int(math.floor(pos))
    return pos, lo, pos - lo


def box_stats(v: np.ndarray) -> dict:
    """Everything a boxplot draws, for one set of values."""
    q1, med, q3 = (float(x) for x in np.percentile(v, [25, 50, 75]))
    iqr = q3 - q1
    lo_f, hi_f = q1 - FENCE * iqr, q3 + FENCE * iqr
    inside = v[(v >= lo_f) & (v <= hi_f)]
    return {
        "n": len(v), "q1": q1, "median": med, "q3": q3, "iqr": iqr, "lower_fence": lo_f, "upper_fence": hi_f,
        "whisker_low": float(inside.min()) if len(inside) else q1, "whisker_high": float(inside.max()) if len(inside) else q3,
        "n_low": int((v < lo_f).sum()), "n_high": int((v > hi_f).sum()),
        "n_far": int(((v < q1 - FAR_FENCE * iqr) | (v > q3 + FAR_FENCE * iqr)).sum()),
    }


def _gap_pct(values: list[float], iqr: float) -> float | None:
    return None if iqr == 0 else 100.0 * (max(values) - min(values)) / iqr


# =============================================================================
# Analysis
# =============================================================================

def analyze(tables: dict[str, pd.DataFrame], profile: dtp.Profile) -> BoxplotResult:
    col_rows, quart_rows, group_rows, summary_rows, flag_rows = [], [], [], [], []

    for name, df in tables.items():
        cols = {c.column: c for c in profile.columns if c.table == name}
        for c in le._numeric_columns(profile, name):
            v = le._numeric(df, c.column)
            n = len(v)
            if n < MIN_N:
                continue
            b = box_stats(v)
            pct = dict(zip(PERCENTILES, np.percentile(v, PERCENTILES)))
            mean = float(v.mean())
            col_rows.append({
                "table": name, "column": c.column, "stat_type": c.stat_type, **{k: b[k] for k in b},
                **{f"p{p}": float(x) for p, x in pct.items()}, "min": float(v.min()), "max": float(v.max()), "mean": mean,
                "outlier_pct": 100.0 * (b["n_low"] + b["n_high"]) / n, "low_outlier_pct": 100.0 * b["n_low"] / n,
                "high_outlier_pct": 100.0 * b["n_high"] / n, "far_outlier_pct": 100.0 * b["n_far"] / n,
                "median_in_box": (b["median"] - b["q1"]) / b["iqr"] if b["iqr"] else None,
                "mean_vs_box": "above the box" if mean > b["q3"] else ("below the box" if mean < b["q1"] else "inside the box"),
                "whisker_vs_max": (b["whisker_high"] / float(v.max())) if v.max() else None,
                "degenerate": bool(b["iqr"] == 0),
            })

            # --- how the quartiles are located: position, neighbours, interpolation, and other methods
            s = np.sort(v)
            row = {"table": name, "column": c.column, "n": n}
            for label, p in (("q1", 0.25), ("median", 0.5), ("q3", 0.75)):
                pos, lo, frac = quartile_position(n, p)
                hi = min(lo + 1, n - 1)
                row[f"{label}_position"] = pos
                row[f"{label}_below"] = float(s[lo])
                row[f"{label}_above"] = float(s[hi])
                row[f"{label}_fraction"] = frac
                row[f"{label}_value"] = float(s[lo] + frac * (s[hi] - s[lo]))
            by_method = {m: np.percentile(v, [25, 75], method=m) for m in QUARTILE_METHODS}
            for m, (a, z) in by_method.items():
                row[f"q1_{m}"], row[f"q3_{m}"] = float(a), float(z)
            row["q1_method_gap_pct_iqr"] = _gap_pct([x[0] for x in by_method.values()], b["iqr"])
            row["q3_method_gap_pct_iqr"] = _gap_pct([x[1] for x in by_method.values()], b["iqr"])
            quart_rows.append(row)

        # --- comparing groups with boxplots
        outcomes = [c for c in cols.values() if c.stat_type in (dtp.CONTINUOUS, dtp.DISCRETE) and not c.personal
                    and tr._role(c)[0] == tr.ROLE_OUTCOME]
        groupers = [c for c in cols.values() if c.stat_type in (dtp.NOMINAL, dtp.ORDINAL, dtp.BINARY) and not c.personal
                    and MIN_LEVELS <= c.n_distinct <= MAX_LEVELS and c.missing_pct <= 10]
        groupers = sorted(groupers, key=lambda c: -c.n_distinct)[:MAX_GROUP_COLUMNS]
        for m_col, g_col in itertools.product(outcomes, groupers):
            frame = pd.DataFrame({"g": df[g_col.column].astype(str), "v": pd.to_numeric(df[m_col.column], errors="coerce")}).dropna()
            if len(frame) < MIN_N:
                continue
            rows = []
            for level, part in frame.groupby("g", sort=False):
                x = part["v"].to_numpy(dtype=float)
                b = box_stats(x)
                gap = None
                if len(x) >= 2:
                    methods = [np.percentile(x, [25, 75], method=mm) for mm in QUARTILE_METHODS]
                    gap = _gap_pct([mm[0] for mm in methods], b["iqr"])
                rows.append({
                    "table": name, "measure": m_col.column, "group_column": g_col.column, "level": str(level), **b,
                    "mean": float(x.mean()), "outlier_pct": 100.0 * (b["n_low"] + b["n_high"]) / len(x),
                    "q1_method_gap_pct_iqr": gap, "small": len(x) <= SMALL_GROUP,
                })
            g = pd.DataFrame(rows).sort_values("median").reset_index(drop=True)
            group_rows.append(g)
            # boxes overlap when their IQR intervals share any value
            pairs = list(itertools.combinations(range(len(g)), 2))
            overlap = [not (g.loc[i, "q3"] < g.loc[j, "q1"] or g.loc[j, "q3"] < g.loc[i, "q1"]) for i, j in pairs]
            ranks = (g["mean"].rank(), g["median"].rank())
            rank_corr = ranks[0].corr(ranks[1]) if len(g) >= 3 and ranks[0].std() > 0 and ranks[1].std() > 0 else None
            summary_rows.append({
                "table": name, "measure": m_col.column, "group_column": g_col.column, "levels": len(g), "rows": int(g["n"].sum()),
                "smallest_group": int(g["n"].min()), "largest_group": int(g["n"].max()),
                "boxes_overlap_pct": 100.0 * float(np.mean(overlap)) if overlap else None,
                "highest_median_over_lowest": float(g["median"].max() / g["median"].min()) if g["median"].min() > 0 else None,
                "rank_corr_mean_median": None if rank_corr is None or pd.isna(rank_corr) else float(rank_corr),
                "top_by_median": str(g.loc[g["median"].idxmax(), "level"]), "top_by_mean": str(g.loc[g["mean"].idxmax(), "level"]),
                "same_top": bool(g["median"].idxmax() == g["mean"].idxmax()),
            })

        # --- does a project flag reproduce a per-group Tukey fence?
        flags = [c for c in cols.values() if c.stat_type == dtp.BINARY and set(dtp.name_tokens(c.column)) & FLAG_TOKENS]
        numerics = le._numeric_columns(profile, name)
        cats = [c for c in cols.values() if c.stat_type in (dtp.NOMINAL, dtp.ORDINAL) and 3 <= c.n_distinct <= 1000 and c.missing_pct <= 10]
        for f, nc, gc in itertools.product(flags, numerics, cats):
            frame = pd.DataFrame({"flag": df[f.column], "g": df[gc.column], "v": pd.to_numeric(df[nc.column], errors="coerce")}).dropna()
            if len(frame) < MIN_N:
                continue
            flag_true = frame["flag"].map(lambda x: x is True or x == 1 or x == "1" or x == "true" or x == "True").to_numpy()
            above = np.zeros(len(frame), dtype=bool)
            usable = np.zeros(len(frame), dtype=bool)
            for _, part in frame.groupby("g", sort=False):
                if len(part) < MIN_GROUP_FOR_FENCE_TEST:
                    continue
                q1, q3 = np.percentile(part["v"], [25, 75])
                idx = frame.index.get_indexer(part.index)
                above[idx] = (part["v"].to_numpy() > q3 + FENCE * (q3 - q1))
                usable[idx] = True
            if not usable.any():
                continue
            a, fl = above[usable], flag_true[usable]
            both = int((a & fl).sum())
            flag_rows.append({
                "table": name, "flag": f.column, "numeric": nc.column, "grouped_by": gc.column, "rows_tested": int(usable.sum()),
                "flagged_pct": 100.0 * float(fl.mean()), "above_fence_pct": 100.0 * float(a.mean()), "both_pct": 100.0 * both / usable.sum(),
                "precision_pct": 100.0 * both / a.sum() if a.sum() else None, "recall_pct": 100.0 * both / fl.sum() if fl.sum() else None,
            })

    flags_df = pd.DataFrame(flag_rows)
    if not flags_df.empty:
        flags_df["f1"] = 2 * flags_df["precision_pct"].fillna(0) * flags_df["recall_pct"].fillna(0) / (flags_df["precision_pct"].fillna(0) + flags_df["recall_pct"].fillna(0)).replace(0, np.nan)
        flags_df = flags_df.sort_values("f1", ascending=False).reset_index(drop=True)
    return BoxplotResult(
        columns=pd.DataFrame(col_rows), quartiles=pd.DataFrame(quart_rows),
        groups=pd.concat(group_rows, ignore_index=True) if group_rows else pd.DataFrame(),
        group_summary=pd.DataFrame(summary_rows), fence_flags=flags_df,
    )


# =============================================================================
# Insights
# =============================================================================

@dataclass
class Insight:
    title: str
    finding: str
    risk: str
    fix: str


def _f(x: float) -> str:
    x = float(x)
    return f"{x:,.0f}" if abs(x) >= 100 else f"{x:,.2f}"


def build_insights(r: BoxplotResult) -> list[Insight]:
    out: list[Insight] = []
    c = r.columns
    if c.empty:
        return out

    n_above = int((c["mean_vs_box"] == "above the box").sum())
    w = c.assign(_d=(c["mean"] - c["q3"]) / c["iqr"].replace(0, np.nan)).sort_values("_d", ascending=False).iloc[0]
    big_cols = c.dropna(subset=["median_in_box"]).query("n >= 1000")
    skewed_box = (big_cols if not big_cols.empty else c.dropna(subset=["median_in_box"])).sort_values("median_in_box").iloc[0]
    out.append(Insight(
        "A boxplot shows skew before any statistic does: the mean falls outside the box",
        f"In {n_above} of {len(c)} numeric columns the mean sits above Q3, outside the box. `{w['table']}.{w['column']}` has Q1 {_f(w['q1'])}, "
        f"median {_f(w['median'])}, Q3 {_f(w['q3'])} but mean {_f(w['mean'])}. The median line in `{skewed_box['table']}.{skewed_box['column']}` sits "
        f"{100 * skewed_box['median_in_box']:.0f}% of the way up its box (50% would be symmetric).",
        "A summary built on the mean describes a value that most rows do not reach.",
        "Look at the boxplot first; if the median line is off-centre or the mean is outside the box, report the median and the IQR.",
    ))

    o = c.sort_values("outlier_pct", ascending=False).iloc[0]
    out.append(Insight(
        "The 1.5 x IQR fences flag many rows, and 'outlier' does not mean 'error'",
        f"For `{o['table']}.{o['column']}` the fences are {_f(o['lower_fence'])} and {_f(o['upper_fence'])}; {o['outlier_pct']:.1f}% of its values fall outside, "
        f"{o['far_outlier_pct']:.1f}% even beyond the stricter 3 x IQR fences. Across all columns the share outside the 1.5 fences runs from "
        f"{c['outlier_pct'].min():.1f}% to {c['outlier_pct'].max():.1f}%.",
        "Deleting every flagged row would remove legitimate large orders along with the typos.",
        "Treat the fences as a prompt to inspect, then decide: correct, keep, or analyse separately.",
    ))

    wh = c.dropna(subset=["whisker_vs_max"]).sort_values("whisker_vs_max")
    if not wh.empty:
        x = wh.iloc[0]
        out.append(Insight(
            "Whiskers are not the minimum and maximum",
            f"In `{x['table']}.{x['column']}` the upper whisker ends at {_f(x['whisker_high'])} (the largest value inside the fence) while the maximum is "
            f"{_f(x['max'])}: the whisker reaches {100 * x['whisker_vs_max']:.2f}% of it. The values beyond are drawn as separate points.",
            "Reading the whisker as the range understates how far the data really go.",
            "State which whisker rule a chart uses (Tukey 1.5 x IQR here; others use min/max or the 5th and 95th percentiles).",
        ))

    q = r.quartiles
    g = r.groups
    if not q.empty:
        big = q["q1_method_gap_pct_iqr"].dropna()
        txt = f"For the full columns the six quartile methods differ by at most {big.max():.2f}% of the IQR"
        if not g.empty and g["q1_method_gap_pct_iqr"].notna().any():
            small = g[g["small"] & g["q1_method_gap_pct_iqr"].notna()]
            if not small.empty:
                s = small.sort_values("q1_method_gap_pct_iqr", ascending=False).iloc[0]
                txt += (f", but for groups of {SMALL_GROUP} rows or fewer they differ by up to {s['q1_method_gap_pct_iqr']:.0f}% of the IQR "
                        f"(`{s['table']}.{s['measure']}` by `{s['group_column']}`, group of {int(s['n'])} rows)")
        out.append(Insight(
            "Quartile calculation: the method matters only for small groups",
            txt + ". Q1 sits at position (n - 1) x 0.25 in the sorted values; when that is not a whole number, Q1 is interpolated between two neighbours.",
            "Two tools (pandas, Excel, R) can print different quartiles for the same small group.",
            "State the method (pandas and numpy use linear interpolation by default) and avoid quartiles for groups of a handful of rows.",
        ))

    gs = r.group_summary
    if not gs.empty:
        ov = gs.dropna(subset=["boxes_overlap_pct"]).sort_values("boxes_overlap_pct", ascending=False).iloc[0]
        out.append(Insight(
            "Comparing groups: overlapping boxes mean the groups are not clearly different",
            f"Comparing `{ov['measure']}` in `{ov['table']}` by `{ov['group_column']}` ({int(ov['levels'])} groups), {ov['boxes_overlap_pct']:.0f}% of the pairs of boxes overlap"
            + (f"; the highest median is {ov['highest_median_over_lowest']:.1f} times the lowest." if ov["highest_median_over_lowest"] else ".")
            + f" Over all {len(gs)} comparisons, boxes overlap in {gs['boxes_overlap_pct'].mean():.0f}% of the pairs on average.",
            "Reading a difference of medians without the boxes can make normal variation look like a real effect.",
            "Compare groups with their boxes (spread) and group sizes, not with a single number each.",
        ))
        diff = gs[~gs["same_top"]]
        rc = gs.dropna(subset=["rank_corr_mean_median"]).sort_values(["same_top", "rank_corr_mean_median"])
        if not rc.empty:
            x = rc.iloc[0]
            out.append(Insight(
                "Robust ranking: groups ordered by mean and by median can disagree",
                f"For `{x['measure']}` in `{x['table']}` by `{x['group_column']}`, the rank correlation between the group means and the group medians is only "
                f"{x['rank_corr_mean_median']:.2f}; the top group is `{x['top_by_mean']}` by mean and `{x['top_by_median']}` by median. "
                f"The top group differs in {len(diff)} of {len(gs)} comparisons.",
                "'Best group' depends on the estimate, so a ranking can change with one outlier.",
                "Rank by a robust estimate (median) and show the boxes next to it.",
            ))

    fl = r.fence_flags
    if not fl.empty:
        b = fl.iloc[0]
        agree = ("closely matches" if (b["f1"] or 0) >= 60 else "does not reproduce")
        out.append(Insight(
            "The project already uses a Tukey fence upstream: does it match?",
            f"The flag `{b['table']}.{b['flag']}` ({b['flagged_pct']:.1f}% of rows) {agree} an upper 1.5 x IQR fence of `{b['numeric']}` computed per `{b['grouped_by']}` "
            f"(above the fence: {b['above_fence_pct']:.1f}% of rows; both: {b['both_pct']:.1f}%; precision {b['precision_pct']:.0f}%, recall {b['recall_pct']:.0f}%).",
            "If the flag is built from another quantity (the README says posologia), its fences cannot be checked from these tables.",
            "Document which column and which grouping each flag uses, so the fence can be audited.",
        ))

    deg = c[c["degenerate"]]
    if len(deg):
        d = deg.iloc[0]
        out.append(Insight(
            "A zero IQR collapses the box",
            f"{len(deg)} column(s) have Q1 = Q3 (for example `{d['table']}.{d['column']}`, both {_f(d['q1'])}), so the box is a line and the fences sit at the same value: "
            f"every different value ({d['outlier_pct']:.1f}% here) is an outlier.",
            "A boxplot of a count column with many ties looks like an error and the 1.5 x IQR rule flags valid counts.",
            "For tied or count data show percentiles, a histogram or a bar chart of the counts instead.",
        ))
    return out[:8]


# =============================================================================
# Result report (paste-ready markdown)
# =============================================================================

def _block(title: str, where: str, ran: str, showed: list[str], means: str, problems: list[str]) -> str:
    lines = [f"### {title}", f"- **WHERE:** {where}", f"- **WHAT I RAN:** {ran}", "- **WHAT IT SHOWED:**"]
    lines += [f"  - {x}" for x in (showed or ["nothing of this kind in the data"])]
    lines += [f"- **WHAT IT MEANS FOR THE PROJECT:** {means}", "- **PROBLEMS OR SURPRISES:**"]
    lines += [f"  - {x}" for x in ([p for p in problems if p] or ["none found by these rules"])]
    return "\n".join(lines)


def build_report(r: BoxplotResult, insights: list[Insight]) -> str:
    c, q, g, gs, fl = r.columns, r.quartiles, r.groups, r.group_summary, r.fence_flags
    where = f"{c['table'].nunique()} tables, {len(c)} numeric columns"
    ref = lambda x: f"`{x.table}.{x.column}`"  # noqa: E731
    out = [
        "# RESULT REPORT - Percentiles and boxplots",
        '**PAGE:** "Percentiles and boxplots" in the Streamlit app (sidebar navigation). Run: `streamlit run data_app_gestao.py`. '
        "Code: `boxplot_percentiles.py` (analysis) + `page_percentiles_and_boxplots` in `data_app_gestao.py` (UI). "
        "Only column names, counts, percentages and aggregates appear.",
    ]
    out.append(_block(
        "1. Percentile, median, quartiles (Q1, Q2, Q3), IQR", where,
        f"percentiles {', '.join(str(p) for p in PERCENTILES)} for every numeric column; Q1, the median (Q2) and Q3 split the sorted rows in four equal groups; IQR = Q3 - Q1.",
        [f"{ref(x)}: p1 {_f(x.p1)}, Q1 {_f(x.q1)}, median {_f(x.median)}, Q3 {_f(x.q3)}, p99 {_f(x.p99)}; IQR {_f(x.iqr)}" for x in c.itertuples()],
        "A percentile is the value below which that share of rows falls. The median is the 50th percentile (Q2); Q1 and Q3 are the 25th and 75th; the IQR is the width of the middle half "
        "of the data.",
        [f"{ref(x)}: Q1 = Q3, the IQR is 0" for x in c.itertuples() if x.degenerate],
    ))
    out.append(_block(
        "2. Quartile calculation (position and interpolation)", where,
        "for each column: the position of Q1, the median and Q3 in the sorted values ((n - 1) x p, counted from 0), the two neighbours, the fraction between them, "
        "and Q1 / Q3 under six methods (linear, lower, higher, midpoint, nearest, weibull).",
        [f"{ref(x)} (n = {x.n:,}): Q1 position {x.q1_position:,.2f} -> between values {_f(x.q1_below)} and {_f(x.q1_above)}, fraction {x.q1_fraction:.2f} -> Q1 {_f(x.q1_value)}; "
         f"the six methods differ by {x.q1_method_gap_pct_iqr:.2f}% of the IQR" if x.q1_method_gap_pct_iqr is not None else
         f"{ref(x)} (n = {x.n:,}): Q1 position {x.q1_position:,.2f}, the IQR is 0 so the methods cannot be compared" for x in q.itertuples()]
        + ([f"groups of {SMALL_GROUP} rows or fewer: the six methods differ by up to {g[g['small']]['q1_method_gap_pct_iqr'].max():.0f}% of the IQR" ]
           if not g.empty and g["small"].any() and g[g["small"]]["q1_method_gap_pct_iqr"].notna().any() else []),
        "pandas and numpy interpolate linearly by default: position (n - 1) x p, then a weighted average of the two neighbouring sorted values. For large n every method gives almost the same "
        "quartile; for small groups they differ.",
        [],
    ))
    out.append(_block(
        "3. Boxplot (box, median line), whisker and cap, fences and the 1.5 x IQR rule", where,
        "box = Q1 to Q3 with the median line; fences = Q1 - 1.5 x IQR and Q3 + 1.5 x IQR; each whisker ends (cap) at the most extreme value still inside its fence; values outside are drawn as points.",
        [f"{ref(x)}: box {_f(x.q1)} to {_f(x.q3)}, median {_f(x.median)} ({100 * x.median_in_box:.0f}% up the box), fences {_f(x.lower_fence)} / {_f(x.upper_fence)}, "
         f"whiskers {_f(x.whisker_low)} / {_f(x.whisker_high)}, mean {x.mean_vs_box}" if x.median_in_box is not None else
         f"{ref(x)}: box collapsed to {_f(x.q1)} (IQR 0), fences {_f(x.lower_fence)} / {_f(x.upper_fence)}, mean {x.mean_vs_box}" for x in c.itertuples()],
        "A boxplot draws five numbers and the outliers. Off-centre median lines and long whiskers show skew; the whisker is not the maximum.",
        [f"{ref(x)}: the maximum ({_f(x.max)}) is {x.max / x.whisker_high:,.1f} times the upper whisker" for x in c.itertuples()
         if x.whisker_high and x.max / x.whisker_high >= 5],
    ))
    out.append(_block(
        "4. Outlier and robust (mean vs. median / IQR)", where,
        "outliers = values beyond the 1.5 x IQR fences (and beyond 3 x IQR as 'far out'); the position of the mean relative to the box.",
        [f"{ref(x)}: {x.outlier_pct:.1f}% outside the fences ({x.low_outlier_pct:.1f}% low, {x.high_outlier_pct:.1f}% high), {x.far_outlier_pct:.1f}% beyond 3 x IQR; mean {x.mean_vs_box}"
         for x in c.itertuples()],
        "Outliers are values far from the rest; they may be errors or real extremes. Robust summaries (median, IQR) ignore them, the mean does not - when the mean is outside the box, the "
        "difference is large.",
        [f"{(c['mean_vs_box'] == 'above the box').sum()} of {len(c)} columns have the mean above the box"],
    ))
    out.append(_block(
        "5. Comparing groups with boxplots", ", ".join(sorted(set(gs["table"]))) if not gs.empty else "-",
        "a boxplot of the first outcome measure for each level of up to two non-personal categorical columns (2 to 12 levels) per table; whether the boxes overlap; whether groups rank "
        "the same by mean and by median.",
        [f"`{x.table}`: `{x.measure}` by `{x.group_column}` ({x.levels} groups, {x.rows:,} rows, group sizes {x.smallest_group} to {x.largest_group}): boxes overlap in "
         f"{x.boxes_overlap_pct:.0f}% of pairs; highest median / lowest median = "
         f"{x.highest_median_over_lowest:.1f}; rank correlation mean vs median "
         f"{('%.2f' % x.rank_corr_mean_median) if x.rank_corr_mean_median is not None else 'n/a'}; top group by mean `{x.top_by_mean}`, by median `{x.top_by_median}`"
         if x.boxes_overlap_pct is not None and x.highest_median_over_lowest else
         f"`{x.table}`: `{x.measure}` by `{x.group_column}` ({x.levels} groups)" for x in gs.itertuples()],
        "Putting boxes side by side compares the whole distributions: centre (median line), spread (box) and extremes (whiskers). Overlapping boxes mean differences of medians are small "
        "next to the natural spread.",
        [f"`{x.table}` `{x.measure}` by `{x.group_column}`: top group differs by mean (`{x.top_by_mean}`) and by median (`{x.top_by_median}`)" for x in gs.itertuples() if not x.same_top],
    ))
    out.append(_block(
        "6. The project's own Tukey fence", "tables with a binary column named like a suspicion / outlier flag",
        "for each such flag, the upper 1.5 x IQR fence of each numeric column within each category (groups of 30+ rows), compared with the flag (precision, recall).",
        [f"`{x.table}.{x.flag}` vs upper fence of `{x.numeric}` per `{x.grouped_by}`: flagged {x.flagged_pct:.1f}%, above fence {x.above_fence_pct:.1f}%, both {x.both_pct:.1f}% "
         f"(precision {x.precision_pct:.0f}%, recall {x.recall_pct:.0f}%)" if x.precision_pct is not None and x.recall_pct is not None else
         f"`{x.table}.{x.flag}` vs `{x.numeric}` per `{x.grouped_by}`: flagged {x.flagged_pct:.1f}%, above fence {x.above_fence_pct:.1f}%" for x in fl.head(5).itertuples()],
        "The README says the churn page excludes patients flagged by a single upper Tukey fence computed upstream per product. This checks whether the stored tables contain the quantity it was "
        "computed from.",
        ["no flag reproduces a Tukey fence of a numeric column in these tables" if fl.empty or (fl["f1"].fillna(0).max() < 60) else ""],
    ))
    top = "\n".join(f"{n}. **{x.title}** - {x.finding} Risk: {x.risk} Fix: {x.fix}" for n, x in enumerate(insights, 1))
    return "\n\n".join(out) + "\n\n## TOP INSIGHTS\n\n" + top + "\n"
