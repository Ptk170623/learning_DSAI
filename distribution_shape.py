"""Frequency tables, histograms and density plots - generic analysis of the
numeric columns of every table the project loads, built to practise these
concepts: frequency table, bin, histogram, bin width and number of bins,
skewness, unimodal and multimodal (mode), density scale, density plot and
kernel density estimate (KDE), and bandwidth.

No Streamlit dependency (same idea as transform.py / data_types_profile.py).
Which columns are numeric, categorical or personal comes from
data_types_profile; no column name is hard-coded.

PRIVACY: every result holds only column names, counts, percentages and
aggregates (bin counts, density curves, skewness). Group labels are listed
only for non-personal categorical columns with few levels. Most frequent
values are listed only for numeric measure columns (never identifiers or
personal columns). No rows.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

import data_types_profile as dtp
import location_estimates as le

MIN_N = 30
BOOK_BINS = 10                      # the book's own example uses 10 equal-width bins
BIN_CHOICES = [5, 10, 20, 40, 80]
CENTRAL = (1, 99)                   # the "central" view keeps the 1st to 99th percentile
GRID_MIN, GRID_MAX = 160, 1200     # the grid has about 4 points per bandwidth, so the peaks are not lost between points
DISPLAY_POINTS = 240               # curves are stored thinned out to this many points
KDE_MAX_POINTS = 8_000
SEED = 20260101
SPIKE_PCT = 20.0                    # one value holding this share of the rows makes the column a "spike"
SKEW_LIMIT = 0.5
PEAK_MIN_REL = 0.05                 # a peak must reach 5% of the highest peak
DIP = 0.8                           # two peaks are separate when the valley between them is under 80% of the lower one
BANDWIDTH_FACTORS = [("too small (h / 4)", 0.25), ("Silverman rule (h)", 1.0), ("too large (h x 4)", 4.0)]
UNEQUAL_PERCENTILES = [0, 25, 50, 75, 90, 99, 100]
MIN_LEVELS, MAX_LEVELS = 2, 12
MIN_GROUP = 30
DISCRETE_DISTINCT = 30
HEAPING_STEPS = [1000, 500, 100, 50, 30, 10, 5]   # round numbers a value can be a multiple of
HEAPING_MIN_PCT, HEAPING_MIN_LIFT = 25.0, 10.0


@dataclass
class ShapeResult:
    columns: pd.DataFrame      # skewness, mode, shape label, KDE modes, one row per numeric column
    hist: pd.DataFrame         # histogram bins for several bin counts, over the full range and the central range
    bin_rules: pd.DataFrame    # how many bins each rule of thumb asks for
    top_values: pd.DataFrame   # the most frequent values of each column (the mode and its neighbours)
    unequal: pd.DataFrame      # a frequency table with bins of unequal width: count against density
    kde: pd.DataFrame          # density curves at three bandwidths
    bandwidth: pd.DataFrame    # bandwidth, number of modes per bandwidth, density mass outside the data
    mixtures: pd.DataFrame     # for multimodal columns: which category explains the second peak


# =============================================================================
# Estimators
# =============================================================================

def silverman_bandwidth(v: np.ndarray) -> float:
    """Silverman's rule of thumb: 0.9 x min(sd, IQR / 1.34) x n^(-1/5). 0 when the values do not vary."""
    if len(v) < 2:
        return 0.0
    sd = float(np.std(v, ddof=1))
    q1, q3 = np.percentile(v, [25, 75])
    spread = min(sd, (q3 - q1) / 1.34) if q3 > q1 else sd
    return 0.9 * spread * len(v) ** -0.2 if spread > 0 else 0.0


def kde_curve(sample: np.ndarray, h: float, grid: np.ndarray) -> np.ndarray:
    """Gaussian kernel density estimate at the grid points: the average of one bell curve of width h per value."""
    out = np.zeros(len(grid))
    step = 16
    for i in range(0, len(grid), step):
        g = grid[i:i + step, None]
        out[i:i + step] = np.exp(-0.5 * ((g - sample[None, :]) / h) ** 2).sum(axis=1)
    return out / (len(sample) * h * math.sqrt(2 * math.pi))


_erf = np.frompyfunc(math.erf, 1, 1)


def kde_mass_below(sample: np.ndarray, h: float, x: float) -> float:
    """Share of the estimated density that lies below x (each bell curve contributes its own normal CDF)."""
    z = (x - sample) / (h * math.sqrt(2))
    return float(np.mean(0.5 * (1 + _erf(z).astype(float))))


def find_modes(density: np.ndarray, grid: np.ndarray) -> list[tuple[float, float]]:
    """Peaks of a density curve as (position, height). A peak must reach 5% of the highest one and be separated from the
    next peak by a dip below 80% of the lower of the two; otherwise it is one hump."""
    d = np.asarray(density, dtype=float)
    if len(d) < 3 or d.max() <= 0:
        return []
    idx = [i for i in range(len(d)) if (i == 0 or d[i] > d[i - 1]) and (i == len(d) - 1 or d[i] >= d[i + 1])]
    idx = [i for i in idx if d[i] >= PEAK_MIN_REL * d.max()]
    changed = True
    while changed and len(idx) > 1:
        changed = False
        for a, b in zip(idx, idx[1:]):
            valley = d[a:b + 1].min()
            if valley >= DIP * min(d[a], d[b]):
                idx.remove(a if d[a] < d[b] else b)
                changed = True
                break
    return [(float(grid[i]), float(d[i])) for i in idx]


def heaping(v: np.ndarray) -> tuple[int | None, float, float]:
    """Round-number heaping: among the steps 5, 10, 30, 50, 100, 500, 1000, the one with the largest share of whole-number values that are
    multiples of it, provided that share is at least 25% and at least 10 times what chance gives (1 in step). Returns (step, share %, chance %)."""
    whole = v[np.isclose(v, np.round(v))]
    if len(whole) < MIN_N or len(whole) < 0.8 * len(v):
        return None, 0.0, 0.0
    best = (None, 0.0, 0.0)
    for step in HEAPING_STEPS:
        share = 100.0 * float(np.mean(np.round(whole) % step == 0))
        if share >= HEAPING_MIN_PCT and share >= HEAPING_MIN_LIFT * 100.0 / step and share > best[1]:
            best = (step, share, 100.0 / step)
    return best


def sturges_bins(n: int) -> int:
    return int(math.ceil(math.log2(n)) + 1)


def _bins_for_width(width: float, lo: float, hi: float) -> int | None:
    return None if not width or width <= 0 or hi <= lo else int(math.ceil((hi - lo) / width))


def _histogram(v: np.ndarray, lo: float, hi: float, bins: int) -> pd.DataFrame:
    counts, edges = np.histogram(v, bins=bins, range=(lo, hi))
    width = edges[1] - edges[0]
    n = max(len(v), 1)
    return pd.DataFrame({
        "bin_no": np.arange(1, bins + 1), "left": edges[:-1], "right": edges[1:], "count": counts,
        "pct": 100.0 * counts / n, "density": counts / (n * width) if width > 0 else np.nan,
    })


# =============================================================================
# Analysis
# =============================================================================

def analyze(tables: dict[str, pd.DataFrame], profile: dtp.Profile) -> ShapeResult:
    rng = np.random.default_rng(SEED)
    col_rows, hist_frames, rule_rows, top_rows, unequal_rows, kde_frames, bw_rows, mix_rows = [], [], [], [], [], [], [], []

    for name, df in tables.items():
        cols = {c.column: c for c in profile.columns if c.table == name}
        groupers = [c for c in cols.values() if c.stat_type in (dtp.NOMINAL, dtp.ORDINAL, dtp.BINARY) and not c.personal
                    and MIN_LEVELS <= c.n_distinct <= MAX_LEVELS and c.missing_pct <= 10]
        for c in le._numeric_columns(profile, name):
            v = le._numeric(df, c.column)
            n = len(v)
            if n < MIN_N:
                continue
            ref = {"table": name, "column": c.column}
            vmin, vmax = float(v.min()), float(v.max())
            q1, med, q3 = (float(x) for x in np.percentile(v, [25, 50, 75]))
            mean, sd = float(v.mean()), float(v.std(ddof=1))
            p_lo, p_hi = (float(x) for x in np.percentile(v, CENTRAL))
            central = v[(v >= p_lo) & (v <= p_hi)]
            vc = pd.Series(v).value_counts()
            mode_value, mode_pct = float(vc.index[0]), 100.0 * float(vc.iloc[0]) / n
            distinct = int(len(vc))
            discrete_like = c.stat_type == dtp.DISCRETE or distinct <= DISCRETE_DISTINCT

            # --- skewness ----------------------------------------------------------------------
            skew = float(pd.Series(v).skew())
            skew_central = float(pd.Series(central).skew()) if len(central) > 3 and central.std() > 0 else None
            direction = "right (long tail of large values)" if skew > SKEW_LIMIT else ("left (long tail of small values)" if skew < -SKEW_LIMIT else "roughly symmetric")

            # --- histograms: every bin count, over the full range and over the central range ----------
            if vmax > vmin:
                for view, data, lo, hi in (("full range", v, vmin, vmax), ("central 1%-99%", central, p_lo, p_hi)):
                    if hi <= lo or len(data) < MIN_N:
                        continue
                    for bins in BIN_CHOICES:
                        h = _histogram(data, lo, hi, bins)
                        hist_frames.append(h.assign(**ref, view=view, bins=bins, width=(hi - lo) / bins, n_in_view=len(data)))
            full10 = _histogram(v, vmin, vmax, BOOK_BINS) if vmax > vmin else pd.DataFrame({"count": [n], "pct": [100.0]})
            cent10 = _histogram(central, p_lo, p_hi, BOOK_BINS) if p_hi > p_lo else None

            # --- bin rules of thumb -------------------------------------------------------------------
            iqr = q3 - q1
            n_cent = len(central)
            fd_full = _bins_for_width(2 * iqr * n ** (-1 / 3), vmin, vmax) if iqr > 0 else None
            fd_cent = _bins_for_width(2 * iqr * n_cent ** (-1 / 3), p_lo, p_hi) if iqr > 0 and n_cent else None
            scott_full = _bins_for_width(3.49 * sd * n ** (-1 / 3), vmin, vmax) if sd > 0 else None
            rule_rows.append({
                **ref, "n": n, "range_over_iqr": (vmax - vmin) / iqr if iqr > 0 else None,
                "sturges_bins": sturges_bins(n), "sqrt_bins": int(math.ceil(math.sqrt(n))), "scott_bins": scott_full, "fd_bins": fd_full, "fd_bins_central": fd_cent,
                "fd_width": 2 * iqr * n ** (-1 / 3) if iqr > 0 else None,
                "book_bins": BOOK_BINS, "book_width": (vmax - vmin) / BOOK_BINS,
                "book_first_bin_pct": float(full10["pct"].iloc[0]), "book_fullest_bin_pct": float(full10["pct"].max()),
                "book_empty_bins": int((full10["count"] == 0).sum()) if "bin_no" in full10 else 0,
                "central_empty_bins": int((cent10["count"] == 0).sum()) if cent10 is not None else None,
                "central_fullest_bin_pct": float(cent10["pct"].max()) if cent10 is not None else None,
            })

            # --- most frequent values (the mode) ----------------------------------------------------------
            for rank, (val, cnt) in enumerate(vc.head(5).items(), start=1):
                top_rows.append({**ref, "rank": rank, "value": float(val), "count": int(cnt), "pct": 100.0 * cnt / n})
            top5 = float(100.0 * vc.head(5).sum() / n)
            h_step, h_share, h_chance = heaping(v) if not discrete_like else (None, 0.0, 0.0)

            # --- a frequency table with unequal bins: count against density --------------------------------
            edges = np.unique(np.percentile(v, UNEQUAL_PERCENTILES))
            if len(edges) >= 3:
                counts, e = np.histogram(v, bins=edges)
                for i, (cnt, lo, hi) in enumerate(zip(counts, e[:-1], e[1:]), start=1):
                    w = float(hi - lo)
                    unequal_rows.append({**ref, "bin_no": i, "left": float(lo), "right": float(hi), "width": w, "count": int(cnt), "pct": 100.0 * cnt / n,
                                         "density": cnt / (n * w) if w > 0 else None})

            # --- kernel density estimate at three bandwidths ----------------------------------------------------
            kde_modes, peaks_txt, h0 = None, "", 0.0
            if p_hi > p_lo and n_cent >= MIN_N:
                sample = central if n_cent <= KDE_MAX_POINTS else rng.choice(central, KDE_MAX_POINTS, replace=False)
                h0 = silverman_bandwidth(central)
                if h0 > 0:
                    grid = np.linspace(p_lo, p_hi, int(min(GRID_MAX, max(GRID_MIN, math.ceil(4 * (p_hi - p_lo) / h0)))))
                    keep = np.unique(np.linspace(0, len(grid) - 1, min(DISPLAY_POINTS, len(grid))).round().astype(int))
                    curves, modes_at = {}, {}
                    for label, f in BANDWIDTH_FACTORS:
                        dens = kde_curve(sample, h0 * f, grid)
                        curves[label] = dens
                        modes_at[label] = find_modes(dens, grid)
                        kde_frames.append(pd.DataFrame({**ref, "bandwidth": label, "x": grid[keep], "density": dens[keep]}))
                    main = modes_at["Silverman rule (h)"]
                    kde_modes = len(main)
                    peaks_txt = "; ".join(f"{p:,.4g}" for p, _ in main)
                    area = float(np.trapezoid(curves["Silverman rule (h)"], grid)) if hasattr(np, "trapezoid") else float(np.trapz(curves["Silverman rule (h)"], grid))
                    bw_rows.append({
                        **ref, "bandwidth_h": h0, "bandwidth_pct_of_central_range": 100.0 * h0 / (p_hi - p_lo), "modes_small": len(modes_at["too small (h / 4)"]),
                        "modes_rule": kde_modes, "modes_large": len(modes_at["too large (h x 4)"]),
                        "area_under_curve": area, "mass_below_minimum_pct": 100.0 * kde_mass_below(sample, h0, vmin), "minimum": vmin,
                        "discrete_like": discrete_like, "distinct": distinct,
                    })
                    # --- multimodal: which category explains the second peak? ------------------------------------
                    if kde_modes >= 2:
                        top2 = sorted(main, key=lambda t: -t[1])[:2]
                        a, b = sorted(p for p, _ in top2)
                        between = (grid >= a) & (grid <= b)
                        valley = float(grid[between][np.argmin(curves["Silverman rule (h)"][between])])
                        best = None
                        for g in groupers:
                            frame = pd.DataFrame({"g": df[g.column].astype(str), "v": pd.to_numeric(df[c.column], errors="coerce")}).dropna()
                            parts = [(str(level), len(p), 100.0 * float((p["v"] > valley).mean())) for level, p in frame.groupby("g", sort=False) if len(p) >= MIN_GROUP]
                            if len(parts) < 2:
                                continue
                            spread = max(x[2] for x in parts) - min(x[2] for x in parts)
                            if best is None or spread > best["spread_pct_points"]:
                                hi_p, lo_p = max(parts, key=lambda x: x[2]), min(parts, key=lambda x: x[2])
                                best = {**ref, "valley": valley, "lower_peak": a, "upper_peak": b, "grouped_by": g.column, "levels": len(parts),
                                        "top_level": hi_p[0], "top_level_rows": hi_p[1], "top_level_above_pct": hi_p[2],
                                        "bottom_level": lo_p[0], "bottom_level_rows": lo_p[1], "bottom_level_above_pct": lo_p[2], "spread_pct_points": spread,
                                        "overall_above_pct": 100.0 * float((frame["v"] > valley).mean())}
                        if best is not None:
                            mix_rows.append(best)

            if mode_pct >= SPIKE_PCT:
                shape = f"spike (one value holds {mode_pct:.0f}% of the rows)"
            elif kde_modes is None:
                shape = "n/a"
            else:
                shape = "unimodal" if kde_modes == 1 else ("bimodal" if kde_modes == 2 else f"multimodal ({kde_modes} peaks)")
            col_rows.append({
                **ref, "stat_type": c.stat_type, "n": n, "distinct": distinct, "min": vmin, "max": vmax, "mean": mean, "median": med, "std": sd, "q1": q1, "q3": q3,
                "skew": skew, "skew_central": skew_central, "pearson_skew": 3 * (mean - med) / sd if sd > 0 else None,
                "bowley_skew": (q3 + q1 - 2 * med) / iqr if iqr > 0 else None,
                "lower_spread": med - vmin, "upper_spread": vmax - med, "upper_over_lower": (vmax - med) / (med - vmin) if med > vmin else None,
                "below_mean_pct": 100.0 * float((v < mean).mean()), "direction": direction,
                "mode_value": mode_value, "mode_pct": mode_pct, "top5_pct": top5, "zero_pct": 100.0 * float((v == 0).mean()),
                "heaping_step": h_step, "heaping_pct": h_share, "heaping_chance_pct": h_chance,
                "kde_modes": kde_modes, "kde_peaks": peaks_txt, "shape": shape, "discrete_like": discrete_like,
                "central_low": p_lo, "central_high": p_hi,
            })

    return ShapeResult(
        columns=pd.DataFrame(col_rows), hist=pd.concat(hist_frames, ignore_index=True) if hist_frames else pd.DataFrame(),
        bin_rules=pd.DataFrame(rule_rows), top_values=pd.DataFrame(top_rows), unequal=pd.DataFrame(unequal_rows),
        kde=pd.concat(kde_frames, ignore_index=True) if kde_frames else pd.DataFrame(), bandwidth=pd.DataFrame(bw_rows), mixtures=pd.DataFrame(mix_rows),
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


def build_insights(r: ShapeResult) -> list[Insight]:
    out: list[Insight] = []
    c, rules, bw, mix, un = r.columns, r.bin_rules, r.bandwidth, r.mixtures, r.unequal
    if c.empty:
        return out

    right = c[c["skew"] > SKEW_LIMIT]
    w = c.sort_values("skew", ascending=False).iloc[0]
    out.append(Insight(
        "Skewness: the data have one long right tail, and the mean follows it",
        f"{len(right)} of {len(c)} numeric columns are right-skewed (skewness above {SKEW_LIMIT}). The strongest is `{w['table']}.{w['column']}` with skewness {w['skew']:.1f}: "
        f"its mean ({_f(w['mean'])}) is above its median ({_f(w['median'])}), {w['below_mean_pct']:.0f}% of the rows are below the mean, and the largest value is {w['upper_over_lower']:.0f} times as far above the median as the smallest is below it."
        if w["upper_over_lower"] else
        f"{len(right)} of {len(c)} numeric columns are right-skewed. The strongest is `{w['table']}.{w['column']}` with skewness {w['skew']:.1f}.",
        "A summary or a model that assumes a symmetric bell shape (mean, standard deviation) describes a row that most orders do not look like.",
        "Look at the shape first; for a skewed column report the median and percentiles, or work on a log scale.",
    ))

    if not rules.empty:
        x = rules.sort_values("book_first_bin_pct", ascending=False).iloc[0]
        out.append(Insight(
            "Ten equal bins over the full range hide the distribution",
            f"For `{x['table']}.{x['column']}` the book's 10 equal-width bins put {x['book_first_bin_pct']:.1f}% of the rows in the first bin and leave {int(x['book_empty_bins'])} of 10 bins empty, because the range is "
            f"{x['range_over_iqr']:,.0f} times the IQR. On the central 1%-99% range the fullest bin holds {x['central_fullest_bin_pct']:.0f}% and {int(x['central_empty_bins'])} bins are empty."
            if pd.notna(x["range_over_iqr"]) and pd.notna(x["central_fullest_bin_pct"]) else
            f"For `{x['table']}.{x['column']}` the first of 10 equal bins holds {x['book_first_bin_pct']:.1f}% of the rows.",
            "A histogram of the full range shows one tall bar and an empty axis: the shape, the modes and the business-relevant region are invisible.",
            "Draw the histogram of the central range (or on a log scale) and say how many values were left out.",
        ))
        d = rules.dropna(subset=["fd_bins"]).sort_values("fd_bins", ascending=False)
        if not d.empty:
            y = d.iloc[0]
            out.append(Insight(
                "Bin width and number of bins: the rules of thumb disagree by orders of magnitude",
                f"For `{y['table']}.{y['column']}` ({int(y['n']):,} rows) Sturges asks for {int(y['sturges_bins'])} bins, the square-root rule for {int(y['sqrt_bins'])}, but the Freedman-Diaconis width "
                f"(2 x IQR x n^(-1/3)) would need {int(y['fd_bins']):,} bins over the full range, and {int(y['fd_bins_central']):,} over the central range." if pd.notna(y["fd_bins_central"]) else
                f"For `{y['table']}.{y['column']}` Sturges asks for {int(y['sturges_bins'])} bins and Freedman-Diaconis for {int(y['fd_bins']):,}.",
                "The number of bins is a choice that changes the story: too few hides peaks, too many draws noise.",
                "Try several bin counts, and choose with the question (a few bins for the overall shape, more for peaks); never trust one default.",
            ))

    spikes = c[c["mode_pct"] >= SPIKE_PCT]
    z = c.sort_values("mode_pct", ascending=False).iloc[0]
    out.append(Insight(
        "The mode: a single value often holds a large share of the rows",
        f"In `{z['table']}.{z['column']}` the most frequent value is {_f(z['mode_value'])}, held by {z['mode_pct']:.1f}% of the rows; its five most frequent values hold {z['top5_pct']:.0f}%. "
        f"{len(spikes)} of {len(c)} columns have one value with at least {SPIKE_PCT:.0f}% of the rows."
        + ("".join(f" In `{k['table']}.{k['column']}` {k['heaping_pct']:.0f}% of the values are multiples of {int(k['heaping_step'])} (chance alone would give {k['heaping_chance_pct']:.1f}%): the values heap on round numbers, which is where the peaks of the density sit."
                   for _, k in c[c["heaping_step"].notna()].sort_values("heaping_pct", ascending=False).head(1).iterrows())),
        "A histogram or a density of such a column shows one huge spike (or a smoothed hump) and the average is a value that hardly occurs: prices, standard quantities and round numbers repeat.",
        "For columns with a few frequent values use a bar chart of the most frequent values; report the mode next to the median.",
    ))

    multi = c[c["kde_modes"].fillna(0) >= 2]
    if not multi.empty:
        m = multi.sort_values("kde_modes", ascending=False).iloc[0]
        txt = (f"{len(multi)} of {len(c)} columns have two or more peaks in their density (Silverman bandwidth), for example `{m['table']}.{m['column']}` with {int(m['kde_modes'])} (at {m['kde_peaks']}).")
        if not mix.empty:
            q = mix.sort_values("spread_pct_points", ascending=False).iloc[0]
            txt += (f" The upper peak of `{q['table']}.{q['column']}` is explained by `{q['grouped_by']}`: {q['top_level_above_pct']:.0f}% of `{q['top_level']}` rows lie above the valley ({_f(q['valley'])}) "
                    f"against {q['bottom_level_above_pct']:.0f}% of `{q['bottom_level']}`.")
        out.append(Insight(
            "Multimodal: more than one peak usually means a mix of two kinds of rows",
            txt, "Averaging a mixture describes neither group; the mean sits in the valley where few rows are.",
            "Find the category that separates the peaks and analyse the groups apart.",
        ))

    if not un.empty:
        best = None
        for (t, col), g in un.groupby(["table", "column"]):
            mid = g[(g["pct"] >= 15) & g["density"].notna() & (g["density"] > 0)]
            if len(mid) >= 3:
                ratio = float(mid["density"].max() / mid["density"].min())
                if best is None or ratio > best[0]:
                    best = (ratio, t, col, mid)
        if best is not None:
            ratio, t, col, mid = best
            hi, lo = mid.loc[mid["density"].idxmax()], mid.loc[mid["density"].idxmin()]
            shares = ", ".join(f"{p:.0f}%" for p in mid["pct"])
            out.append(Insight(
                "Density scale: with bins of unequal width, equal counts are not equal densities",
                f"Cutting `{t}.{col}` at its percentiles gives bins of very different width. {len(mid)} bins hold about the same share of the rows ({shares}), so as bars of counts they look alike; "
                f"but bin {int(hi['bin_no'])} ({_f(hi['left'])} to {_f(hi['right'])}) is {ratio:.1f} times denser than bin {int(lo['bin_no'])} ({_f(lo['left'])} to {_f(lo['right'])}), because it is narrower.",
                "Plotting counts for unequal bins makes wide bins look as crowded as narrow ones and hides where the rows really concentrate.",
                "With unequal bins plot the density (count / (n x width)) so the area, not the height, is the share of rows; with equal bins counts and density have the same shape.",
            ))

    if not bw.empty:
        b = bw.sort_values("modes_small", ascending=False).iloc[0]
        txt = (f"For `{b['table']}.{b['column']}` the density has {int(b['modes_small'])} peaks with a bandwidth of h/4, {int(b['modes_rule'])} with the Silverman rule and {int(b['modes_large'])} with 4h "
               f"(h = {_f(b['bandwidth_h'])}).")
        out.append(Insight(
            "Bandwidth: the number of peaks you see depends on the smoothing you choose",
            txt, "A too-small bandwidth invents peaks out of noise; a too-large one erases real ones. Both look equally convincing on a chart.",
            "Draw the density at two or three bandwidths and trust only the peaks that survive; compare with the histogram.",
        ))
        leak = bw[bw["discrete_like"]].sort_values("mass_below_minimum_pct", ascending=False)
        if not leak.empty and leak.iloc[0]["mass_below_minimum_pct"] >= 1:
            k = leak.iloc[0]
            out.append(Insight(
                "A density curve invents values that cannot exist",
                f"The kernel density of `{k['table']}.{k['column']}` ({int(k['distinct'])} distinct values, minimum {_f(k['minimum'])}) puts {k['mass_below_minimum_pct']:.1f}% of its area below that minimum, "
                f"at values the column never takes.",
                "Smoothing counts and bounded quantities spreads probability onto impossible values (fractions of a unit, negative amounts).",
                "For counts and columns with few distinct values use a bar chart of the values instead of a density.",
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


def build_report(r: ShapeResult, insights: list[Insight]) -> str:
    c, rules, top, un, bw, mix, hist = r.columns, r.bin_rules, r.top_values, r.unequal, r.bandwidth, r.mixtures, r.hist
    where = f"{c['table'].nunique()} tables, {len(c)} numeric columns"
    ref = lambda x: f"`{x.table}.{x.column}`"  # noqa: E731
    out = [
        "# RESULT REPORT - Frequency tables, histograms and density plots",
        '**PAGE:** "Histograms and density" in the Streamlit app (sidebar navigation). Run: `streamlit run data_app_gestao.py`. '
        "Code: `distribution_shape.py` (analysis) + `page_histograms_and_density` in `data_app_gestao.py` (UI). "
        "Only column names, counts, percentages and aggregates appear.",
    ]
    book10 = rules.set_index(["table", "column"]) if not rules.empty else rules
    out.append(_block(
        "1. Frequency table and bin", where,
        f"for every numeric column: the range cut into {BOOK_BINS} equal-width bins (the book's example), counting the rows in each bin; the same over the central {CENTRAL[0]}%-{CENTRAL[1]}% range.",
        [f"{ref(x)}: bin width {_f(x.book_width)}, first bin holds {x.book_first_bin_pct:.1f}% of the rows, fullest bin {x.book_fullest_bin_pct:.1f}%, {x.book_empty_bins} of {x.book_bins} bins empty; "
         f"on the central range the fullest bin holds {x.central_fullest_bin_pct:.1f}%" if pd.notna(x.central_fullest_bin_pct) else
         f"{ref(x)}: bin width {_f(x.book_width)}, first bin holds {x.book_first_bin_pct:.1f}% of the rows, {x.book_empty_bins} of {x.book_bins} bins empty" for x in rules.itertuples()],
        "A frequency table divides the range into equal bins and counts the rows in each; empty bins are part of the table because they say where there are no values.",
        [f"{ref(x)}: {x.book_empty_bins} of {x.book_bins} bins are empty over the full range" for x in rules.itertuples() if x.book_empty_bins >= 5],
    ))
    out.append(_block(
        "2. Histogram", where,
        f"the frequency table drawn as contiguous bars, for {', '.join(str(b) for b in BIN_CHOICES)} bins, over the full range and the central range.",
        [f"{ref(x)}: tallest bar over the full range holds {x.book_fullest_bin_pct:.1f}% of the rows (10 bins); over the central range {x.central_fullest_bin_pct:.1f}%" if pd.notna(x.central_fullest_bin_pct)
         else f"{ref(x)}: tallest bar holds {x.book_fullest_bin_pct:.1f}% (10 bins)" for x in rules.itertuples()],
        "A histogram is the picture of the frequency table: bins on the x-axis, counts on the y-axis, bars touching, equal widths, empty bins drawn.",
        [],
    ))
    out.append(_block(
        "3. Bin width and number of bins", where,
        "Sturges (log2 n + 1), square root of n, Scott (3.49 x sd x n^(-1/3)) and Freedman-Diaconis (2 x IQR x n^(-1/3)) compared with the book's 10 bins. These rules are not in your books.",
        [f"{ref(x)} (n = {x.n:,}): Sturges {x.sturges_bins}, sqrt {x.sqrt_bins}, Scott {x.scott_bins if pd.notna(x.scott_bins) else 'n/a'}, Freedman-Diaconis "
         f"{(f'{int(x.fd_bins):,}') if pd.notna(x.fd_bins) else 'n/a (IQR 0)'} (central range: {(f'{int(x.fd_bins_central):,}') if pd.notna(x.fd_bins_central) else 'n/a'})" for x in rules.itertuples()],
        "Too few bins hide features, too many draw noise. The right number depends on n, on the spread and on the question; the rules are starting points.",
        [f"{ref(x)}: range = {x.range_over_iqr:,.0f} x IQR, so the full-range rules ask for thousands of bins" for x in rules.itertuples() if pd.notna(x.range_over_iqr) and x.range_over_iqr >= 100],
    ))
    out.append(_block(
        "4. Skewness", where,
        "skewness (bias-corrected third standardised moment), Pearson's 3 x (mean - median) / sd, Bowley's quartile skewness, and the upper over lower spread around the median (the book's symmetry check).",
        [f"{ref(x)}: skewness {x.skew:.2f} ({x.direction}), {x.below_mean_pct:.0f}% of the rows below the mean, mean {_f(x.mean)} vs median {_f(x.median)}"
         + (f", upper / lower spread {x.upper_over_lower:,.0f}" if pd.notna(x.upper_over_lower) else "") for x in c.itertuples()],
        "Skewness tells whether the data lean to large or small values. The book says it is discovered through displays rather than measured; the number is a summary of what the histogram shows.",
        [f"{ref(x)}: skewness {x.skew:.1f}, one extreme tail" for x in c.itertuples() if abs(x.skew) >= 10],
    ))
    out.append(_block(
        "5. Unimodal and multimodal (mode)", where,
        "the mode (most frequent value) and its share; the five most frequent values; the number of peaks of the kernel density (Silverman bandwidth; a peak needs a dip below 80% before the next one); "
        "the category that explains the second peak.",
        [f"{ref(x)}: mode {_f(x.mode_value)} ({x.mode_pct:.1f}% of rows), top 5 values {x.top5_pct:.0f}%; shape: {x.shape}" + (f"; peaks at {x.kde_peaks}" if x.kde_peaks else "") for x in c.itertuples()]
        + [f"{ref(x)}: {x.heaping_pct:.0f}% of the values are multiples of {int(x.heaping_step)} (chance {x.heaping_chance_pct:.1f}%): round-number heaping" for x in c.itertuples() if pd.notna(x.heaping_step)]
        + [f"{ref(x)}: peak above {_f(x.valley)} explained by `{x.grouped_by}`: `{x.top_level}` {x.top_level_above_pct:.0f}% vs `{x.bottom_level}` {x.bottom_level_above_pct:.0f}%" for x in mix.itertuples()],
        "A mode is a peak of the distribution; the book mentions bimodal and trimodal distributions with the mode. Several peaks usually mean a mixture of groups.",
        [f"{ref(x)}: one value holds {x.mode_pct:.0f}% of the rows" for x in c.itertuples() if x.mode_pct >= SPIKE_PCT],
    ))
    out.append(_block(
        "6. Density scale", "every numeric column",
        "the histogram divided by n x bin width, so that the bar areas add up to 1; and a frequency table cut at the 0, 25, 50, 75, 90, 99 and 100th percentiles (unequal widths) read by count and by density.",
        [f"{ref(x)}: bins {x.bin_no} ({_f(x.left)} to {_f(x.right)}): count {x.count:,} ({x.pct:.1f}%), width {_f(x.width)}, density {x.density:.3g}" for x in un.itertuples()][:40],
        "The density scale makes the area under the curve equal to 1, so the area between two points is the share of the rows in between. With equal bins it only rescales the y-axis; with unequal bins it is the only fair picture.",
        [],
    ))
    out.append(_block(
        "7. Density plot, kernel density estimate (KDE) and bandwidth", where,
        "a Gaussian KDE (one bell curve of width h per value, averaged) over the central 1%-99% range, at h/4, h (Silverman 0.9 x min(sd, IQR/1.34) x n^(-1/5)) and 4h; peaks counted at each; the share of the area that lies below the smallest value of the column.",
        [f"{ref(x)}: h = {_f(x.bandwidth_h)}; peaks {x.modes_small} (h/4), {x.modes_rule} (h), {x.modes_large} (4h); area under the curve {x.area_under_curve:.3f}; {x.mass_below_minimum_pct:.1f}% of the area below the minimum ({_f(x.minimum)})"
         for x in bw.itertuples()],
        "A density plot is a smoothed histogram computed from the data with a kernel; the bandwidth controls the smoothing. The area under the whole curve is 1.",
        [f"{ref(x)}: {x.mass_below_minimum_pct:.1f}% of the density lies below the minimum, at values that do not occur" for x in bw.itertuples() if x.mass_below_minimum_pct >= 5],
    ))
    top_ins = "\n".join(f"{n}. **{x.title}** - {x.finding} Risk: {x.risk} Fix: {x.fix}" for n, x in enumerate(insights, 1))
    return "\n\n".join(out) + "\n\n## TOP INSIGHTS\n\n" + top_ins + "\n"
