"""Estimates of location - generic analysis of the numeric columns of every
table the project loads, built to practise these concepts: estimate of
location, sample, estimate, outlier, robust, mean, trimmed mean, median,
weight, weighted mean, weighted median, and mean versus median.

No Streamlit dependency (same idea as transform.py / data_types_profile.py).
Which columns are numeric comes from data_types_profile (no column name is
hard-coded); weights and "money" columns are found by name TOKENS only.

PRIVACY: every result holds only column names, counts, percentages and
aggregates (means, medians, spreads). No rows and no identifier values.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

import data_types_profile as dtp

TRIM = 0.10                    # trimmed mean drops this share at each end
SAMPLE_SIZE = 200              # size of each random sample in the sampling demo
SAMPLE_DRAWS = 400             # how many samples are drawn
MIN_N = 30
OUTLIER_SHARE_MEDIAN = 1.0     # % of Tukey outliers above which the median is suggested
SKEW_LIMIT = 1.0
WEIGHT_TOKENS = {"QTD", "QTDE", "QTY", "QUANT", "QUANTIDADE", "QUANTITY", "UNITS", "UNIDADES", "PX"}
SEED = 42


@dataclass
class LocationResult:
    estimates: pd.DataFrame   # mean / median / trimmed mean / outliers / robustness / advice per numeric column
    sampling: pd.DataFrame    # how much the sample mean and sample median move between samples
    weights: pd.DataFrame     # unweighted vs weighted mean and median of a unit value
    groups: pd.DataFrame      # mean of group means vs the overall mean (group size as weight)
    app: pd.DataFrame         # the app's own Mean / Median choice on the 660 benchmark (latest complete month)
    app_summary: pd.DataFrame # ... and how often it changes the classification over 12 months


# =============================================================================
# Estimators
# =============================================================================

def trimmed_mean(values: np.ndarray, trim: float = TRIM) -> float:
    v = np.sort(values)
    k = int(trim * len(v))
    return float(v[k:len(v) - k].mean()) if len(v) - 2 * k > 0 else float(v.mean())


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    return float(np.average(values, weights=weights))


def weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    """Value at which the cumulative weight first reaches half the total."""
    order = np.argsort(values, kind="stable")
    v, w = values[order], weights[order]
    cum = np.cumsum(w)
    return float(v[np.searchsorted(cum, cum[-1] / 2.0)])


def _pct(a: float, b: float) -> float | None:
    return None if b == 0 or np.isnan(b) else 100.0 * (a - b) / abs(b)


def _numeric(df: pd.DataFrame, column: str) -> np.ndarray:
    v = pd.to_numeric(df[column], errors="coerce").dropna().to_numpy(dtype=float)
    return v[np.isfinite(v)]


def _numeric_columns(profile: dtp.Profile, table: str) -> list[dtp.ColumnProfile]:
    return [c for c in profile.columns if c.table == table and c.stat_type in (dtp.CONTINUOUS, dtp.DISCRETE)
            and not c.personal]


# =============================================================================
# Analysis
# =============================================================================

def analyze(tables: dict[str, pd.DataFrame], profile: dtp.Profile, sales_data=None) -> LocationResult:
    rng = np.random.default_rng(SEED)
    est_rows, samp_rows, weight_rows, group_rows = [], [], [], []

    for name, df in tables.items():
        for c in _numeric_columns(profile, name):
            v = _numeric(df, c.column)
            if len(v) < MIN_N:
                continue
            q1, med, q3 = np.percentile(v, [25, 50, 75])
            iqr = q3 - q1
            lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            outside = (v < lo) | (v > hi)
            clean = v[~outside]
            mean = float(v.mean())
            skew = float(pd.Series(v).skew())
            outlier_pct = 100.0 * float(outside.mean())
            row = {
                "table": name, "column": c.column, "stat_type": c.stat_type, "n": len(v),
                "mean": mean, "median": float(med), "trimmed_mean": trimmed_mean(v),
                "min": float(v.min()), "max": float(v.max()), "skew": skew,
                "mean_vs_median_pct": _pct(mean, float(med)), "trimmed_vs_mean_pct": _pct(trimmed_mean(v), mean),
                "outlier_pct": outlier_pct, "degenerate_iqr": bool(iqr == 0),
                "max_over_median": float(v.max() / med) if med else None,
                "mean_shift_pct": _pct(float(clean.mean()), mean) if len(clean) else None,
                "median_shift_pct": _pct(float(np.median(clean)), float(med)) if len(clean) else None,
            }
            heavy = outlier_pct >= OUTLIER_SHARE_MEDIAN or abs(skew) > SKEW_LIMIT
            row["advice"] = "median (or trimmed mean)" if heavy else "mean is fine"
            row["advice_why"] = (
                f"skew {skew:.1f}, {outlier_pct:.1f}% outliers" if heavy else f"skew {skew:.1f}, {outlier_pct:.1f}% outliers")
            est_rows.append(row)

            # --- sampling: how much does an estimate move from one sample to the next?
            size = min(SAMPLE_SIZE, max(MIN_N, len(v) // 5))
            idx = rng.integers(0, len(v), size=(SAMPLE_DRAWS, size))
            draws = v[idx]
            means, medians = draws.mean(axis=1), np.median(draws, axis=1)
            samp_rows.append({
                "table": name, "column": c.column, "sample_size": size, "draws": SAMPLE_DRAWS,
                "population_mean": mean, "population_median": float(med),
                "mean_spread_pct": _pct_spread(means, mean), "median_spread_pct": _pct_spread(medians, float(med)),
                "mean_range_low": float(np.percentile(means, 5)), "mean_range_high": float(np.percentile(means, 95)),
                "median_range_low": float(np.percentile(medians, 5)), "median_range_high": float(np.percentile(medians, 95)),
            })

        # --- weights: a unit value (money / quantity), plain versus weighted by the quantity
        cols = {c.column: c for c in profile.columns if c.table == name}
        money = [c for c, p in cols.items() if p.stat_type in (dtp.CONTINUOUS, dtp.DISCRETE)
                 and set(dtp.name_tokens(c)) & dtp.MEASURE_TOKENS]
        weight_cols = [c for c, p in cols.items() if p.stat_type in (dtp.CONTINUOUS, dtp.DISCRETE)
                       and set(dtp.name_tokens(c)) & WEIGHT_TOKENS]
        for m in money:
            for w in weight_cols:
                pair = pd.DataFrame({"m": pd.to_numeric(df[m], errors="coerce"), "w": pd.to_numeric(df[w], errors="coerce")}).dropna()
                pair = pair[(pair["w"] > 0) & (pair["m"] >= 0)]
                if len(pair) < MIN_N:
                    continue
                unit = (pair["m"] / pair["w"]).to_numpy()
                wts = pair["w"].to_numpy(dtype=float)
                um, uw = float(unit.mean()), weighted_mean(unit, wts)
                weight_rows.append({
                    "table": name, "value": m, "weight": w, "n": len(pair),
                    "unit_mean": um, "unit_weighted_mean": uw, "mean_gap_pct": _pct(um, uw),
                    "unit_median": float(np.median(unit)), "unit_weighted_median": weighted_median(unit, wts),
                    "median_gap_pct": _pct(float(np.median(unit)), weighted_median(unit, wts)),
                    "total_ratio_check": float(pair["m"].sum() / pair["w"].sum()),
                })

        # --- weights as group sizes: mean of group means vs the overall mean
        measure = next((c for c in money if cols[c].stat_type in (dtp.CONTINUOUS, dtp.DISCRETE)), None)
        cats = [c for c, p in cols.items() if p.stat_type in (dtp.NOMINAL, dtp.ORDINAL) and 3 <= p.n_distinct <= 100
                and p.missing_pct <= 10 and not p.personal]
        if measure and cats:
            cat = max(cats, key=lambda x: cols[x].n_distinct)
            g = pd.DataFrame({"g": df[cat], "v": pd.to_numeric(df[measure], errors="coerce")}).dropna()
            grp = g.groupby("g")["v"].agg(["mean", "median", "size"])
            overall_mean, overall_median = float(g["v"].mean()), float(g["v"].median())
            group_rows.append({
                "table": name, "group_column": cat, "measure": measure, "groups": len(grp),
                "overall_mean": overall_mean, "mean_of_group_means": float(grp["mean"].mean()),
                "weighted_mean_of_groups": weighted_mean(grp["mean"].to_numpy(), grp["size"].to_numpy(dtype=float)),
                "gap_pct": _pct(float(grp["mean"].mean()), overall_mean),
                "overall_median": overall_median, "median_of_group_medians": float(grp["median"].median()),
                "median_gap_pct": _pct(float(grp["median"].median()), overall_median),
                "smallest_group": int(grp["size"].min()), "largest_group": int(grp["size"].max()),
            })

    app_detail, app_summary = _app_effect(sales_data)
    return LocationResult(
        estimates=pd.DataFrame(est_rows), sampling=pd.DataFrame(samp_rows), weights=pd.DataFrame(weight_rows),
        groups=pd.DataFrame(group_rows), app=app_detail, app_summary=app_summary,
    )


def _pct_spread(estimates: np.ndarray, centre: float) -> float | None:
    """Standard deviation of the estimates across samples, as % of the full-data value."""
    return None if centre == 0 else 100.0 * float(estimates.std()) / abs(centre)


def _complete_months(sales_data, transform) -> list[pd.Timestamp]:
    """Months of the 660 series without the last one when it is clearly partial
    (fewer than half the orders of the median of the 3 months before it)."""
    monthly = sales_data.sales.groupby("month")["order_count"].sum().sort_index()
    months = list(monthly.index)
    if len(months) >= 4 and monthly.iloc[-1] < 0.5 * float(monthly.iloc[-4:-1].median()):
        months = months[:-1]
    return months


def _app_effect(sales_data) -> tuple[pd.DataFrame, pd.DataFrame]:
    """What the app's own "Summary Measure" (Mean or Median) does to the 660
    benchmark (block = all). Uses transform.calculate_table_660 as it is.
    Returns (detail for the latest complete month, summary over the last 12
    complete months: how often the classification changes)."""
    detail_cols = ["window", "metric", "current", "mean_benchmark", "median_benchmark", "benchmark_gap_pct",
                   "class_mean", "class_median", "flips"]
    sum_cols = ["window", "metric", "months_tested", "flips", "flip_pct", "avg_abs_gap_pct"]
    empty = (pd.DataFrame(columns=detail_cols), pd.DataFrame(columns=sum_cols))
    if sales_data is None:
        return empty
    import transform
    months = _complete_months(sales_data, transform)
    if not months:
        return empty
    tested = months[-12:]
    rows = []
    for month in tested:
        for window in transform.BENCHMARK_WINDOWS:
            a = transform.calculate_table_660(sales_data, None, "All", "All", month, window, "Mean")
            b = transform.calculate_table_660(sales_data, None, "All", "All", month, window, "Median")
            for x, y in zip(a.itertuples(), b.itertuples()):
                rows.append({
                    "month": month, "window": window, "metric": transform.NAME_METRIC[x.metric], "current": x.current_value,
                    "mean_benchmark": x.benchmark, "median_benchmark": y.benchmark,
                    "benchmark_gap_pct": _pct(x.benchmark, y.benchmark) if x.benchmark is not None and y.benchmark is not None else None,
                    "class_mean": x.classification, "class_median": y.classification, "flips": x.classification != y.classification,
                })
    allr = pd.DataFrame(rows)
    detail = allr[allr["month"] == tested[-1]][detail_cols].reset_index(drop=True)
    summary = (allr.assign(_abs=allr["benchmark_gap_pct"].abs())
               .groupby(["window", "metric"], sort=False)
               .agg(months_tested=("flips", "size"), flips=("flips", "sum"), avg_abs_gap_pct=("_abs", "mean")).reset_index())
    summary["flip_pct"] = 100.0 * summary["flips"] / summary["months_tested"]
    detail.attrs["month"] = tested[-1]
    detail.attrs["partial_month_skipped"] = (months[-1] != sales_data.sales["month"].max()) if len(months) else False
    summary.attrs["first_month"], summary.attrs["last_month"] = tested[0], tested[-1]
    return detail, summary[sum_cols]


# =============================================================================
# Insights
# =============================================================================

@dataclass
class Insight:
    title: str
    finding: str
    risk: str
    fix: str


def build_insights(r: LocationResult) -> list[Insight]:
    out: list[Insight] = []
    e = r.estimates
    if e.empty:
        return out

    gap = e.assign(_g=e["mean_vs_median_pct"].abs()).sort_values("_g", ascending=False)
    top = gap.iloc[0]
    n_gap = int((e["mean_vs_median_pct"].abs() >= 20).sum())
    out.append(Insight(
        "Mean and median disagree a lot: the typical row is not the average row",
        f"{n_gap} of {len(e)} numeric columns have a mean at least 20% away from their median. The widest: "
        f"`{top['table']}.{top['column']}` has median {_f(top['median'])} but mean {_f(top['mean'])} "
        f"({top['mean_vs_median_pct']:+.0f}%), skew {top['skew']:.1f}.",
        "Reporting the mean as 'the typical value' describes a row that almost nobody has.",
        "Say which question you answer: the median for a typical row, the mean for a total (mean x rows = total).",
    ))

    rob = e.dropna(subset=["mean_shift_pct", "median_shift_pct"])
    rob = rob.assign(_d=(rob["mean_shift_pct"].abs() - rob["median_shift_pct"].abs())).sort_values("_d", ascending=False)
    if not rob.empty:
        w = rob.iloc[0]
        out.append(Insight(
            "Outliers move the mean far more than the median (robustness)",
            f"Removing the Tukey outliers ({w['outlier_pct']:.1f}% of the values) moves the mean of "
            f"`{w['table']}.{w['column']}` by {w['mean_shift_pct']:+.0f}% but its median by only {w['median_shift_pct']:+.1f}%. "
            f"Its maximum is {w['max_over_median']:,.0f} times the median.",
            "One typo or one huge order changes the mean, so a benchmark or KPI built on it jumps for no business reason.",
            "Use a robust estimate (median or trimmed mean) for benchmarks, and inspect the largest rows before trusting any mean.",
        ))

    sp = r.sampling
    if not sp.empty:
        sp = sp.assign(_r=sp["mean_spread_pct"] / sp["median_spread_pct"].replace(0, np.nan)).dropna(subset=["_r"]).sort_values(["sample_size", "_r"], ascending=False)
        if not sp.empty:
            s = sp.iloc[0]
            out.append(Insight(
                "An estimate from a sample is itself uncertain",
                f"Drawing {int(s['draws'])} random samples of {int(s['sample_size'])} rows from `{s['table']}.{s['column']}`, "
                f"the sample mean ranges {_f(s['mean_range_low'])} to {_f(s['mean_range_high'])} (90% of draws) around the full-data "
                f"{_f(s['population_mean'])}, while the sample median stays between {_f(s['median_range_low'])} and "
                f"{_f(s['median_range_high'])} around {_f(s['population_median'])}.",
                "With skewed data a small sample gives a mean that changes a lot from sample to sample, so two analysts get different answers.",
                "Report the estimate with its spread (a range or a bootstrap interval) and prefer the estimator that varies less.",
            ))

    if not r.weights.empty:
        w = r.weights.assign(_g=r.weights[["mean_gap_pct", "median_gap_pct"]].abs().max(axis=1)).sort_values("_g", ascending=False).iloc[0]
        out.append(Insight(
            "Weight: the plain average of a unit value ignores how much was sold",
            f"In `{w['table']}`, the average of `{w['value']}` / `{w['weight']}` per row is {_f(w['unit_mean'])}, but weighting each row "
            f"by `{w['weight']}` gives {_f(w['unit_weighted_mean'])} ({w['mean_gap_pct']:+.0f}%); the weighted mean equals total "
            f"`{w['value']}` / total `{w['weight']}` ({_f(w['total_ratio_check'])}). The weighted median is {_f(w['unit_weighted_median'])} "
            f"against a plain median of {_f(w['unit_median'])}.",
            "A one-unit sale counts as much as a thousand-unit sale, so the 'average price' matches no real total.",
            "Weight by the quantity (np.average(..., weights=...)) whenever rows represent different amounts.",
        ))

    if not r.groups.empty:
        g = r.groups.sort_values("largest_group", ascending=False).iloc[0]   # the biggest table matters most
        out.append(Insight(
            "Averaging averages treats a small group like a big one",
            f"In `{g['table']}`, the mean of the {int(g['groups'])} `{g['group_column']}` means of `{g['measure']}` is "
            f"{_f(g['mean_of_group_means'])}, but the overall mean is {_f(g['overall_mean'])} ({g['gap_pct']:+.0f}%). Groups range from "
            f"{int(g['smallest_group']):,} to {int(g['largest_group']):,} rows.",
            "Each group counts once whatever its size, so tiny groups pull the 'overall' figure as much as the biggest ones.",
            "Weight group means by group size (the weighted mean of group means is the overall mean), or report both.",
        ))

    if not r.app_summary.empty:
        s = r.app_summary
        total_flips, total = int(s["flips"].sum()), int(s["months_tested"].sum())
        worst = s.sort_values("flip_pct", ascending=False).iloc[0]
        gap = s.sort_values("avg_abs_gap_pct", ascending=False).iloc[0]
        out.append(Insight(
            "The app's Mean / Median switch changes the benchmark and sometimes the verdict",
            f"Over the last {int(s['months_tested'].max())} complete months ({s.attrs['first_month']:%m/%Y} to {s.attrs['last_month']:%m/%Y}), "
            f"switching 'Summary Measure' from Mean to Median changes the classification in {total_flips} of {total} month x window x metric "
            f"checks ({100 * total_flips / total:.0f}%). Worst case: {worst['metric']}, {worst['window']} window, {worst['flip_pct']:.0f}% of months. "
            f"The benchmark itself differs by {gap['avg_abs_gap_pct']:.0f}% on average for {gap['metric']} ({gap['window']}).",
            "The same month can read NEUTRAL under one measure and ABOVE under the other, so the verdict depends on a switch people may not notice.",
            "Pick the measure per question (median for 'normal', mean for 'total') and show which one a classification used.",
        ))

    deg = e[e["degenerate_iqr"]]
    if len(deg):
        out.append(Insight(
            "Count columns with a zero IQR make outlier rules degenerate",
            f"{len(deg)} numeric column(s) have an interquartile range of 0 (e.g. `{deg.iloc[0]['table']}.{deg.iloc[0]['column']}`, "
            f"median {_f(deg.iloc[0]['median'])}), so the Tukey fence flags every different value as an outlier "
            f"({deg.iloc[0]['outlier_pct']:.1f}% here).",
            "An automatic outlier filter can delete legitimate larger counts.",
            "For such columns use a percentile cap (for example the 99th) or a trimmed mean instead of the 1.5 x IQR rule.",
        ))
    return out[:8]


def _f(x: float) -> str:
    x = float(x)
    return f"{x:,.0f}" if abs(x) >= 100 else f"{x:,.2f}"


# =============================================================================
# Result report (paste-ready markdown)
# =============================================================================

def _block(title: str, where: str, ran: str, showed: list[str], means: str, problems: list[str]) -> str:
    lines = [f"### {title}", f"- **WHERE:** {where}", f"- **WHAT I RAN:** {ran}", "- **WHAT IT SHOWED:**"]
    lines += [f"  - {x}" for x in (showed or ["nothing of this kind in the data"])]
    lines += [f"- **WHAT IT MEANS FOR THE PROJECT:** {means}", "- **PROBLEMS OR SURPRISES:**"]
    lines += [f"  - {x}" for x in ([p for p in problems if p] or ["none found by these rules"])]
    return "\n".join(lines)


def build_report(r: LocationResult, insights: list[Insight]) -> str:
    e = r.estimates
    where = f"{e['table'].nunique()} tables, {len(e)} numeric columns"
    out = [
        "# RESULT REPORT - Estimates of location",
        '**PAGE:** "Estimates of location" in the Streamlit app (sidebar navigation). Run: `streamlit run data_app_gestao.py`. '
        "Code: `location_estimates.py` (analysis) + `page_estimates_of_location` in `data_app_gestao.py` (UI). "
        "Only column names, counts, percentages and aggregates appear.",
    ]
    out.append(_block(
        "1. Estimate of location, sample, estimate", where,
        f"{SAMPLE_DRAWS} random samples of up to {SAMPLE_SIZE} rows per numeric column; for each, the sample mean and median.",
        [f"`{x.table}.{x.column}`: full-data mean {_f(x.population_mean)}, median {_f(x.population_median)}; across samples the mean "
         f"varies by {x.mean_spread_pct:.1f}% and the median by {x.median_spread_pct:.1f}% (std as % of the full-data value)"
         for x in r.sampling.itertuples() if x.mean_spread_pct is not None and x.median_spread_pct is not None],
        "An estimate of location is one number that stands for a column's centre. A different sample gives a different "
        "estimate, so every estimate carries uncertainty. The tables here hold the data the project has; treating them as a "
        "sample of the business means any figure is an estimate.",
        [f"`{x.table}.{x.column}`: the sample mean varies {x.mean_spread_pct / x.median_spread_pct:.1f}x more than the sample median"
         for x in r.sampling.itertuples() if x.median_spread_pct and x.mean_spread_pct and x.mean_spread_pct / x.median_spread_pct >= 2][:6],
    ))
    out.append(_block(
        "2. Mean, median, trimmed mean", where,
        f"mean, median and {int(TRIM * 100)}% trimmed mean (drop the lowest and highest {int(TRIM * 100)}%), plus skew, for every numeric column.",
        [f"`{x.table}.{x.column}` ({x.stat_type}, n={x.n:,}): mean {_f(x.mean)}, median {_f(x.median)}, trimmed mean {_f(x.trimmed_mean)}, "
         f"mean vs median {x.mean_vs_median_pct:+.0f}%, skew {x.skew:.1f}" for x in e.itertuples() if x.mean_vs_median_pct is not None],
        "The three estimates answer slightly different questions: the mean is the total shared equally, the median is the middle "
        "row, the trimmed mean is an average that ignores the extremes.",
        [f"`{x.table}.{x.column}`: mean is {x.mean_vs_median_pct:+.0f}% from the median" for x in e.itertuples()
         if x.mean_vs_median_pct is not None and abs(x.mean_vs_median_pct) >= 20],
    ))
    rob = e.dropna(subset=["mean_shift_pct", "median_shift_pct"])
    out.append(_block(
        "3. Outlier and robust", where,
        "Tukey fences (1.5 x IQR); recompute mean and median without the outliers and compare how far each moved.",
        [f"`{x.table}.{x.column}`: {x.outlier_pct:.1f}% outliers (max = {x.max_over_median:,.0f} x median); without them the mean "
         f"moves {x.mean_shift_pct:+.0f}% and the median {x.median_shift_pct:+.1f}%" for x in rob.itertuples() if x.max_over_median],
        "An outlier is a value far from the rest. An estimate is robust when a few outliers barely move it: the median and "
        "the trimmed mean are robust, the mean is not.",
        [f"`{x.table}.{x.column}`: IQR is 0, the outlier rule is degenerate ({x.outlier_pct:.1f}% flagged)" for x in e.itertuples() if x.degenerate_iqr],
    ))
    out.append(_block(
        "4. Weight, weighted mean, weighted median", ", ".join(sorted(set(r.weights["table"]) | set(r.groups["table"]))) or "-",
        "a unit value (money / quantity) averaged plainly and with the quantity as weight; group means averaged plainly and weighted by group size.",
        [f"`{x.table}`: `{x.value}` / `{x.weight}`: mean {_f(x.unit_mean)} vs weighted mean {_f(x.unit_weighted_mean)} ({x.mean_gap_pct:+.0f}%); "
         f"median {_f(x.unit_median)} vs weighted median {_f(x.unit_weighted_median)}" for x in r.weights.itertuples()]
        + [f"`{x.table}`: mean of {x.groups} `{x.group_column}` means of `{x.measure}` = {_f(x.mean_of_group_means)} vs overall mean "
           f"{_f(x.overall_mean)} ({x.gap_pct:+.0f}%); weighted by group size = {_f(x.weighted_mean_of_groups)}" for x in r.groups.itertuples()],
        "A weight says how much each value counts. The weighted mean of a unit value is total value / total quantity, which "
        "reconciles with the accounting totals; the plain mean does not.",
        [f"`{x.table}`: the plain mean of `{x.value}` / `{x.weight}` is {x.mean_gap_pct:+.0f}% from the weighted one" for x in r.weights.itertuples()
         if x.mean_gap_pct is not None and abs(x.mean_gap_pct) >= 10],
    ))
    a, s = r.app, r.app_summary
    out.append(_block(
        "5. Mean versus median: when to use each", where + "; the 660 Analysis benchmark",
        "a rule per column (median or trimmed mean when skew > 1 or 1%+ outliers, otherwise the mean) and a Mean-vs-Median run of the app's own "
        "660 benchmark (transform.calculate_table_660, block = all) over the last 12 complete months.",
        [f"`{x.table}.{x.column}`: {x.advice} ({x.advice_why})" for x in e.itertuples()]
        + [f"{x.window} / {x.metric}: classification changes in {int(x.flips)} of {int(x.months_tested)} months; benchmark differs by "
           f"{x.avg_abs_gap_pct:.1f}% on average" for x in s.itertuples()],
        "Use the median (or a trimmed mean) to describe a typical row or to build a benchmark when data are skewed or have outliers. "
        "Use the mean when you need a total (mean x n = total) or the data are symmetric.",
        [f"{int(s['flips'].sum())} of {int(s['months_tested'].sum())} month x window x metric checks change classification between Mean and Median" if len(s) else "",
         "the latest month is partial and was left out of the app comparison" if len(a) and a.attrs.get("partial_month_skipped") else ""],
    ))
    top = "\n".join(f"{n}. **{x.title}** - {x.finding} Risk: {x.risk} Fix: {x.fix}" for n, x in enumerate(insights, 1))
    return "\n\n".join(out) + "\n\n## TOP INSIGHTS\n\n" + top + "\n"
