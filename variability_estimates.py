"""Estimates of variability - generic analysis of the numeric columns of every
table the project loads, built to practise these concepts: variability,
deviation, variance, standard deviation, mean absolute deviation, MAD (median
absolute deviation), range, order statistics, percentile, quartile, IQR,
degrees of freedom and n - 1, bias, robust, outlier.

No Streamlit dependency (same idea as transform.py / data_types_profile.py).
Which columns are numeric comes from data_types_profile; no column name is
hard-coded.

PRIVACY: every result holds only column names, counts, percentages and
aggregates (spreads, percentiles). No rows and no identifier values.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

import data_types_profile as dtp
import location_estimates as le

MIN_N = 30
SEED = 7
BIAS_SAMPLE_SIZE = 10           # tiny samples make the n versus n - 1 difference visible
BIAS_DRAWS = 20000
MAD_SCALE = 1.4826              # makes MAD comparable to a standard deviation (for a normal curve)
IQR_SCALE = 1.349               # same idea for the IQR
Z_LIMIT = 3.0                   # the classic "more than 3 standard deviations" rule
MADZ_LIMIT = 3.5                # the usual cut-off for the MAD-based modified z-score
QUANTILE_POINTS = [0, 1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100]
APP_MONTHS = 24


@dataclass
class VariabilityResult:
    spread: pd.DataFrame      # SD, variance, MAD, range, quartiles, robustness and outlier rules per numeric column
    bias: pd.DataFrame        # variance estimated with n versus n - 1 on small samples
    quantiles: pd.DataFrame   # order statistics: the value at each percentile (table, column, p, value)
    app: pd.DataFrame         # month-to-month variability of the app's 660 metrics against its deviation bands


def _pct(a: float, b: float) -> float | None:
    return None if b == 0 or np.isnan(b) else 100.0 * (a - b) / abs(b)


def _sd(v: np.ndarray) -> float:
    return float(v.std(ddof=1)) if len(v) > 1 else 0.0


def _mad(v: np.ndarray) -> float:
    return float(np.median(np.abs(v - np.median(v))))


def analyze(tables: dict[str, pd.DataFrame], profile: dtp.Profile, sales_data=None) -> VariabilityResult:
    rng = np.random.default_rng(SEED)
    spread_rows, bias_rows, quant_rows = [], [], []
    for name, df in tables.items():
        for c in le._numeric_columns(profile, name):
            v = le._numeric(df, c.column)
            if len(v) < MIN_N:
                continue
            n = len(v)
            mean, med = float(v.mean()), float(np.median(v))
            sd, var = _sd(v), float(v.var(ddof=1))
            dev = v - mean
            q = np.percentile(v, QUANTILE_POINTS)
            p = dict(zip(QUANTILE_POINTS, q))
            q1, q3 = float(np.percentile(v, 25)), float(np.percentile(v, 75))
            iqr, mad = q3 - q1, _mad(v)
            lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            tukey = (v < lo) | (v > hi)
            clean = v[~tukey]
            z_out = np.abs(dev) > Z_LIMIT * sd if sd else np.zeros(n, dtype=bool)
            madz_out = np.abs(0.6745 * (v - med) / mad) > MADZ_LIMIT if mad else np.zeros(n, dtype=bool)
            row = {
                "table": name, "column": c.column, "stat_type": c.stat_type, "n": n,
                "mean": mean, "sd": sd, "variance": var, "cv_pct": 100.0 * sd / abs(mean) if mean else None,
                "sum_of_deviations": float(dev.sum()), "sum_dev_relative": float(abs(dev.sum()) / (n * sd)) if sd else 0.0,
                "largest_deviation_in_sd": float(np.abs(dev).max() / sd) if sd else 0.0,
                "mean_abs_dev": float(np.abs(dev).mean()), "mad": mad, "mad_scaled": MAD_SCALE * mad,
                "sd_over_mad_scaled": sd / (MAD_SCALE * mad) if mad else None,
                "min": float(v.min()), "max": float(v.max()), "range": float(v.max() - v.min()),
                "q1": q1, "median": med, "q3": q3, "iqr": iqr, "iqr_scaled": iqr / IQR_SCALE,
                "sd_over_iqr_scaled": sd / (iqr / IQR_SCALE) if iqr else None,
                "range_over_iqr": float((v.max() - v.min()) / iqr) if iqr else None,
                "p1": float(p[1]), "p5": float(p[5]), "p95": float(p[95]), "p99": float(p[99]),
                "max_over_p99": float(v.max() / p[99]) if p[99] else None,
                "outlier_z_pct": 100.0 * float(z_out.mean()), "outlier_tukey_pct": 100.0 * float(tukey.mean()),
                "outlier_madz_pct": 100.0 * float(madz_out.mean()),
                "sd_shift_pct": _pct(_sd(clean), sd) if len(clean) > 1 else None,
                "iqr_shift_pct": _pct(float(np.percentile(clean, 75) - np.percentile(clean, 25)), iqr) if len(clean) > 1 else None,
                "mad_shift_pct": _pct(_mad(clean), mad) if len(clean) > 1 else None,
                "degenerate": bool(iqr == 0 or mad == 0),
            }
            spread_rows.append(row)
            for pt, val in zip(QUANTILE_POINTS, q):
                quant_rows.append({"table": name, "column": c.column, "p": pt, "value": float(val)})

            # --- bias: variance of many tiny samples, dividing by n versus by n - 1
            k = BIAS_SAMPLE_SIZE
            draws = v[rng.integers(0, n, size=(BIAS_DRAWS, k))]
            pop_var = float(v.var(ddof=0))
            v0, v1 = draws.var(axis=1, ddof=0), draws.var(axis=1, ddof=1)
            bias_rows.append({
                "table": name, "column": c.column, "sample_size": k, "draws": BIAS_DRAWS, "population_variance": pop_var,
                "mean_variance_n": float(v0.mean()), "mean_variance_n_minus_1": float(v1.mean()),
                "bias_n_pct": _pct(float(v0.mean()), pop_var), "bias_n_minus_1_pct": _pct(float(v1.mean()), pop_var),
                "theory_bias_n_pct": -100.0 / k,
                "mean_sd_n_minus_1": float(np.sqrt(v1).mean()), "population_sd": float(np.sqrt(pop_var)),
                "sd_bias_pct": _pct(float(np.sqrt(v1).mean()), float(np.sqrt(pop_var))),
            })
    return VariabilityResult(
        spread=pd.DataFrame(spread_rows), bias=pd.DataFrame(bias_rows), quantiles=pd.DataFrame(quant_rows),
        app=_app_variability(sales_data),
    )


def _app_variability(sales_data) -> pd.DataFrame:
    """The app classifies a month by its % deviation from a benchmark with fixed
    bands (NEUTRAL within 10%, then 25%, 40%). Here: how variable the monthly
    series really are, and how often the app's own function (transform.
    calculate_table_660, block = all, Year window, Mean) calls a month NEUTRAL."""
    cols = ["metric", "months", "mean", "sd", "cv_pct", "median", "mad_scaled_pct", "iqr_pct", "share_neutral_pct",
            "share_slight_pct", "share_strong_pct"]
    if sales_data is None:
        return pd.DataFrame(columns=cols)
    import transform
    months = le._complete_months(sales_data, transform)[-APP_MONTHS:]
    if len(months) < 6:
        return pd.DataFrame(columns=cols)
    monthly = sales_data.sales.groupby("month")[transform.METRICS].sum().reindex(months)
    classes = {m: [] for m in transform.METRICS}
    for month in months:
        t = transform.calculate_table_660(sales_data, None, "All", "All", month, "Year", "Mean")
        for x in t.itertuples():
            classes[x.metric].append(x.classification)
    rows = []
    for metric in transform.METRICS:
        s = monthly[metric].dropna().to_numpy(dtype=float)
        cl = pd.Series(classes[metric])
        med = float(np.median(s))
        rows.append({
            "metric": transform.NAME_METRIC[metric], "months": len(s), "mean": float(s.mean()), "sd": _sd(s),
            "cv_pct": 100.0 * _sd(s) / abs(float(s.mean())) if s.mean() else None, "median": med,
            "mad_scaled_pct": 100.0 * MAD_SCALE * _mad(s) / abs(med) if med else None,
            "iqr_pct": 100.0 * float(np.percentile(s, 75) - np.percentile(s, 25)) / abs(med) if med else None,
            "share_neutral_pct": 100.0 * float((cl == "NEUTRAL").mean()),
            "share_slight_pct": 100.0 * float(cl.str.startswith("SLIGHTLY").mean()),
            "share_strong_pct": 100.0 * float((~cl.isin(["NEUTRAL"]) & ~cl.str.startswith("SLIGHTLY") & (cl != "NO HISTORY")).mean()),
        })
    out = pd.DataFrame(rows, columns=cols)
    out.attrs["first_month"], out.attrs["last_month"] = months[0], months[-1]
    return out


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


def build_insights(r: VariabilityResult) -> list[Insight]:
    out: list[Insight] = []
    s = r.spread
    if s.empty:
        return out

    d = s.dropna(subset=["sd_over_mad_scaled"]).sort_values("sd_over_mad_scaled", ascending=False)
    if not d.empty:
        w = d.iloc[0]
        out.append(Insight(
            "The standard deviation and the MAD describe different spreads",
            f"For `{w['table']}.{w['column']}` the standard deviation is {_f(w['sd'])} but the scaled MAD (median absolute deviation) is only "
            f"{_f(w['mad_scaled'])}: the SD is {w['sd_over_mad_scaled']:.1f} times larger. For a bell-shaped column the two would be about equal; "
            f"{int((d['sd_over_mad_scaled'] > 2).sum())} of the {len(d)} columns with a non-zero MAD have an SD more than twice their MAD.",
            "Quoting only the SD describes the few huge values, not the spread of the typical row.",
            "Report a robust spread (MAD or IQR) next to the SD, and say which one you used.",
        ))

    rb = s.dropna(subset=["sd_shift_pct", "iqr_shift_pct"]).assign(_d=lambda x: x["sd_shift_pct"].abs() - x["iqr_shift_pct"].abs()).sort_values("_d", ascending=False)
    if not rb.empty:
        w = rb.iloc[0]
        out.append(Insight(
            "Outliers inflate the SD far more than the IQR (robustness)",
            f"Removing the Tukey outliers ({w['outlier_tukey_pct']:.1f}% of the values) cuts the SD of `{w['table']}.{w['column']}` by "
            f"{abs(w['sd_shift_pct']):.0f}% but its IQR by only {abs(w['iqr_shift_pct']):.0f}% and its MAD by {abs(w['mad_shift_pct']):.0f}%.",
            "One bad record changes the SD, so control limits and thresholds built on it move for no business reason.",
            "Use the IQR or the MAD for limits and benchmarks, and inspect the largest rows before trusting an SD.",
        ))

    mk = s.assign(_g=s["outlier_tukey_pct"] - s["outlier_z_pct"]).sort_values("_g", ascending=False).iloc[0]
    out.append(Insight(
        "The 3-standard-deviation rule hides outliers (masking)",
        f"In `{mk['table']}.{mk['column']}` the rule 'more than 3 SD from the mean' flags {mk['outlier_z_pct']:.1f}% of the values, the Tukey rule "
        f"(1.5 x IQR) flags {mk['outlier_tukey_pct']:.1f}% and the MAD-based modified z-score flags {mk['outlier_madz_pct']:.1f}%. The outliers "
        "themselves inflate the SD, so they hide inside it.",
        "An automatic outlier filter based on the SD misses the very values it should catch.",
        "Prefer a rule built on robust spread (IQR or MAD) and review what each rule flags.",
    ))

    b = r.bias
    if not b.empty:
        mean_b0, mean_b1 = float(b["bias_n_pct"].median()), float(b["bias_n_minus_1_pct"].median())
        w = b.iloc[0]
        out.append(Insight(
            "Dividing by n underestimates the variance; n - 1 fixes it on average (bias)",
            f"Drawing {int(w['draws']):,} samples of {int(w['sample_size'])} rows from every column, the variance computed with n is on average "
            f"{mean_b0:+.0f}% from the full-data variance (median across columns; theory says {w['theory_bias_n_pct']:+.0f}%), while n - 1 "
            f"gives {mean_b1:+.0f}%. The n - 1 estimate is unbiased for the variance, but the SD (its square root) still comes out low "
            f"({b['sd_bias_pct'].median():+.0f}% median): a little from the square root, a lot from skew, because samples of "
            f"{int(w['sample_size'])} rows seldom contain the extreme values.",
            "A small sample always looks less variable than the data really are, so intervals and limits come out too tight.",
            "Use the sample variance (ddof=1, pandas default) on samples; use ddof=0 only when you hold the whole population.",
        ))

    rg = s.dropna(subset=["range_over_iqr"]).sort_values("range_over_iqr", ascending=False)
    if not rg.empty:
        w = rg.iloc[0]
        out.append(Insight(
            "The range depends on two values only",
            f"`{w['table']}.{w['column']}` spans {_f(w['min'])} to {_f(w['max'])} (range {_f(w['range'])}), which is {w['range_over_iqr']:,.0f} times its IQR "
            f"({_f(w['iqr'])}). The 99th percentile is {_f(w['p99'])}, so the maximum is {w['max_over_p99']:.0f} times larger than 99% of the data.",
            "A range or a min/max chart is dominated by the single most extreme row.",
            "Show percentiles (p5, p25, p50, p75, p95) or the IQR instead of the range.",
        ))

    a = r.app
    if not a.empty:
        w = a.sort_values("share_neutral_pct").iloc[0]
        out.append(Insight(
            "The app's fixed deviation bands ignore how variable each metric really is",
            f"For the last {int(a['months'].max())} complete months, {w['metric']} varies from month to month by {w['cv_pct']:.0f}% (SD / mean; "
            f"robust spread {w['mad_scaled_pct']:.0f}% of the median) and only {w['share_neutral_pct']:.0f}% of its months are NEUTRAL (within +/-10% "
            f"of the Year benchmark). Across metrics the NEUTRAL share runs from {a['share_neutral_pct'].min():.0f}% to {a['share_neutral_pct'].max():.0f}%.",
            "A metric with high natural variability is called 'ABOVE' or 'BELOW' most months by chance, so the labels lose meaning.",
            "Size the bands from each metric's own spread (for example a multiple of its MAD) instead of fixed percentages.",
        ))

    deg = s[s["degenerate"]]
    if len(deg):
        w = deg.iloc[0]
        out.append(Insight(
            "A spread of zero breaks the robust rules",
            f"{len(deg)} column(s) have an IQR or a MAD of 0 (for example `{w['table']}.{w['column']}`, median {_f(w['median'])}): more than half "
            "of the rows share the same value, so those robust scales cannot rescale or detect outliers.",
            "Dividing by a zero scale gives infinities, or flags every different value.",
            "For such count columns use percentile caps (the 95th or 99th) or work on a transformed scale.",
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


def build_report(r: VariabilityResult, insights: list[Insight]) -> str:
    s, b, a = r.spread, r.bias, r.app
    where = f"{s['table'].nunique()} tables, {len(s)} numeric columns"
    ref = lambda x: f"`{x.table}.{x.column}`"  # noqa: E731
    out = [
        "# RESULT REPORT - Estimates of variability",
        '**PAGE:** "Estimates of variability" in the Streamlit app (sidebar navigation). Run: `streamlit run data_app_gestao.py`. '
        "Code: `variability_estimates.py` (analysis) + `page_estimates_of_variability` in `data_app_gestao.py` (UI). "
        "Only column names, counts, percentages and aggregates appear.",
    ]
    out.append(_block(
        "1. Variability and deviation", where,
        "for every numeric column: the deviation of each value from the mean (value - mean), its sum, the largest deviation in standard "
        "deviations, and the coefficient of variation (SD / mean, my addition to compare columns in different units).",
        [f"{ref(x)}: mean {_f(x.mean)}, SD {_f(x.sd)}, CV {x.cv_pct:.0f}%, deviations add up to {x.sum_of_deviations:,.2g} (about zero), "
         f"largest deviation = {x.largest_deviation_in_sd:.0f} SD" for x in s.itertuples() if x.cv_pct is not None],
        "Variability is how spread out the values are. A deviation is the distance of one value from the centre. Deviations around the "
        "mean always add up to zero, so we square them (variance, SD) or take their absolute value (mean absolute deviation).",
        [f"{ref(x)}: one value sits {x.largest_deviation_in_sd:.0f} standard deviations from the mean" for x in s.itertuples() if x.largest_deviation_in_sd >= 20],
    ))
    out.append(_block(
        "2. Variance, standard deviation, degrees of freedom (n - 1), bias", where,
        f"{BIAS_DRAWS:,} random samples of {BIAS_SAMPLE_SIZE} rows per column; the variance of each sample computed with n and with n - 1, "
        "averaged and compared with the full-data variance.",
        [f"{ref(x)}: variance {x.population_variance:,.4g}; mean estimate with n {x.bias_n_pct:+.0f}%, with n - 1 {x.bias_n_minus_1_pct:+.0f}% "
         f"(theory for n: {x.theory_bias_n_pct:+.0f}%); SD from n - 1 is {x.sd_bias_pct:+.0f}% off" for x in b.itertuples()],
        "The sample variance divides by n - 1 (the degrees of freedom: one is used up by estimating the mean). Dividing by n makes small "
        "samples look less variable than the data are: that is bias. The standard deviation is the square root, in the original units.",
        [f"{ref(x)}: the estimates are noisy because the column is very skewed; more draws are needed to see the theory" for x in b.itertuples()
         if abs(x.bias_n_minus_1_pct) > 10],
    ))
    out.append(_block(
        "3. Mean absolute deviation and MAD (median absolute deviation)", where,
        "mean absolute deviation, MAD (median of |value - median|), the scaled MAD (x 1.4826, comparable with a SD) and the SD / scaled MAD ratio.",
        [f"{ref(x)}: SD {_f(x.sd)}, mean absolute deviation {_f(x.mean_abs_dev)}, MAD {_f(x.mad)}, scaled MAD {_f(x.mad_scaled)}"
         + (f", SD / scaled MAD = {x.sd_over_mad_scaled:.1f}" if x.sd_over_mad_scaled else ", MAD = 0") for x in s.itertuples()],
        "The mean absolute deviation uses the mean, so outliers still pull it. The MAD uses medians twice and barely moves: it is the robust "
        "partner of the SD (book, chapter 1, 'Estimates of Variability').",
        [f"{ref(x)}: MAD is 0, more than half the rows share one value" for x in s.itertuples() if x.mad == 0],
    ))
    out.append(_block(
        "4. Range, order statistics, percentile, quartile, IQR", where,
        "sorted values (order statistics): minimum, percentiles 1, 5, 25 (Q1), 50, 75 (Q3), 95, 99, maximum; the range and the IQR (Q3 - Q1).",
        [f"{ref(x)}: min {_f(x.min)}, Q1 {_f(x.q1)}, median {_f(x.median)}, Q3 {_f(x.q3)}, p99 {_f(x.p99)}, max {_f(x.max)}; IQR {_f(x.iqr)}"
         + (f", range = {x.range_over_iqr:,.0f} x IQR" if x.range_over_iqr else "") for x in s.itertuples()],
        "Order statistics are the data sorted from smallest to largest. A percentile is the value below which that share of rows falls; "
        "quartiles split the data in four; the IQR is the width of the middle half. The range uses only the two extreme rows.",
        [f"{ref(x)}: the maximum is {x.max_over_p99:.0f} times the 99th percentile" for x in s.itertuples() if x.max_over_p99 and x.max_over_p99 >= 10],
    ))
    out.append(_block(
        "5. Robust and outlier", where,
        "three outlier rules (more than 3 SD from the mean; 1.5 x IQR beyond the quartiles; MAD-based modified z-score above 3.5) and the "
        "change of SD, IQR and MAD after the Tukey outliers are removed.",
        [f"{ref(x)}: outliers by 3-SD rule {x.outlier_z_pct:.1f}%, Tukey {x.outlier_tukey_pct:.1f}%, MAD rule {x.outlier_madz_pct:.1f}%; "
         f"without the Tukey outliers SD {x.sd_shift_pct:+.0f}%, IQR {x.iqr_shift_pct:+.0f}%, MAD {x.mad_shift_pct:+.0f}%"
         for x in s.itertuples() if x.sd_shift_pct is not None and x.iqr_shift_pct is not None and x.mad_shift_pct is not None],
        "An estimate is robust when a few outliers barely move it: the IQR and the MAD are robust, the SD, the variance and the range are not.",
        [f"{ref(x)}: the 3-SD rule flags {x.outlier_z_pct:.1f}% but the Tukey rule {x.outlier_tukey_pct:.1f}% (masking)" for x in s.itertuples()
         if x.outlier_tukey_pct - x.outlier_z_pct >= 3],
    ))
    out.append(_block(
        "6. Deviation in the project: the 660 Analysis bands", "vendas_660 monthly metrics; transform.calculate_table_660",
        f"the monthly series of each 660 metric (all blocks) over the last {a['months'].max() if len(a) else 0} complete months: SD, CV, scaled MAD, IQR "
        "against the median, and how the app's own function classified each month against the Year (mean) benchmark.",
        [f"{x.metric}: month-to-month CV {x.cv_pct:.0f}%, robust spread {x.mad_scaled_pct:.0f}% of the median, IQR {x.iqr_pct:.0f}% of the median; "
         f"NEUTRAL in {x.share_neutral_pct:.0f}% of months, slightly above/below {x.share_slight_pct:.0f}%, above/below/much {x.share_strong_pct:.0f}%"
         for x in a.itertuples()],
        "The app calls a month NEUTRAL when its % deviation from the benchmark is within 10%, then 25%, 40%. Those bands are fixed; the real "
        "variability of each metric decides how often a normal month falls outside them.",
        [f"{x.metric}: only {x.share_neutral_pct:.0f}% of months are NEUTRAL" for x in a.itertuples() if x.share_neutral_pct < 50],
    ))
    top = "\n".join(f"{n}. **{x.title}** - {x.finding} Risk: {x.risk} Fix: {x.fix}" for n, x in enumerate(insights, 1))
    return "\n\n".join(out) + "\n\n## TOP INSIGHTS\n\n" + top + "\n"
