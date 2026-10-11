"""Builds the flat tables behind the "Sales Data Insights" dashboard.

Reads the project's tables through transform._ler (Supabase) and writes one JSON
file per table into an output folder (default: insights/out/). Every file is a list
of flat rows (numbers and text only). Only aggregates are written: counts, shares,
medians, spreads. No client, doctor or patient is named and no row is copied.

Usage:  python insights/build_report_data.py [output_folder]

The concepts used come from Parts A to D of learning/: data types and keys (A, B),
mean vs. median and weighted means (C), deviation, spread, percentiles and IQR (D).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import transform  # noqa: E402

TABLES = ["vendas_660", "tipo_venda", "carteira_pacientes", "painel", "vendas_1015"]
PAYMENTS = ["RECURSO PROPRIO", "JUDICIAL", "DESCONHECIDO"]
ALL = "All"
MAD_SCALE = 1.4826
TOP_PRODUCTS = 15
TOP_BLOCKS = 15


# ------------------------------------------------------------------ helpers
def clean(v):
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return float(f"{float(v):.6g}")
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v


def rows(df: pd.DataFrame) -> list[dict]:
    return [{k: clean(v) for k, v in r.items()} for r in df.to_dict("records")]


def mad_pct(x: pd.Series) -> float | None:
    med = float(x.median())
    return None if med == 0 else 100.0 * MAD_SCALE * float((x - med).abs().median()) / med


def n0(x: float) -> str:
    return f"{x:,.0f}"


def pct(x: float, d: int = 0) -> str:
    return f"{x:.{d}f}%"


# ------------------------------------------------------------------ load
def load() -> dict[str, pd.DataFrame]:
    return {n: transform._ler(n) for n in TABLES}


def sale_lines(t: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """One row per sale line: the sales table joined to its sale type on the composite key (ID_VENDA + PRODUTO)."""
    v, tv = t["vendas_660"], t["tipo_venda"][["ID_VENDA", "PRODUTO", "TIPO_VENDA"]]
    s = v[v["TIPO_REGISTRO"] == "VENDA"].merge(tv, on=["ID_VENDA", "PRODUTO"], how="left")
    s["year"] = s["DATA_VENDA"].dt.year
    s["month"] = s["DATA_VENDA"].dt.to_period("M")
    s["PRODUTO"] = s["PRODUTO"].fillna("(no product)")
    return s


# ------------------------------------------------------------------ cubes with segmenters
def yearly(s: pd.DataFrame, last_year: int, partial_from: pd.Timestamp) -> list[dict]:
    out = []
    sale_types = [ALL] + sorted(s["TIPO_VENDA"].dropna().unique())
    for pay in [ALL] + PAYMENTS:
        sp = s if pay == ALL else s[s["TIPO_PAGAMENTO"] == pay]
        for st in sale_types:
            d = sp if st == ALL else sp[sp["TIPO_VENDA"] == st]
            for year, g in d[d["year"] >= 2017].groupby("year"):
                f = g["FATURAMENTO"]
                units = g["QUANTIDADE"].sum()
                out.append({
                    "year": int(year), "payment": pay, "sale_type": st, "lines": len(g), "revenue": f.sum(), "clients": g["ID_CLIENTE"].nunique(),
                    "mean_ticket": f.mean(), "median_ticket": f.median(), "q1": f.quantile(0.25), "q3": f.quantile(0.75),
                    "units": int(units), "price_per_unit": f.sum() / units if units else None, "partial": bool(year == last_year and partial_from.year == last_year),
                })
    return out


def monthly(s: pd.DataFrame, last_complete: pd.Period) -> list[dict]:
    out = []
    sale_types = [ALL] + sorted(s["TIPO_VENDA"].dropna().unique())
    s = s[(s["month"] <= last_complete) & (s["year"] >= 2017)]
    for pay in [ALL] + PAYMENTS:
        sp = s if pay == ALL else s[s["TIPO_PAGAMENTO"] == pay]
        for st in sale_types:
            d = sp if st == ALL else sp[sp["TIPO_VENDA"] == st]
            for m, g in d.groupby("month"):
                out.append({"month": str(m), "payment": pay, "sale_type": st, "lines": len(g), "revenue": g["FATURAMENTO"].sum(), "median_ticket": g["FATURAMENTO"].median()})
    return out


# ------------------------------------------------------------------ products and concentration
def products(s: pd.DataFrame, last_complete: pd.Period) -> list[dict]:
    recent = s[(s["month"] > last_complete - 12) & (s["month"] <= last_complete)]
    prior = s[(s["month"] > last_complete - 24) & (s["month"] <= last_complete - 12)]
    total = recent["FATURAMENTO"].sum()
    prior_rev = prior.groupby("PRODUTO")["FATURAMENTO"].sum()
    top = recent.groupby("PRODUTO")["FATURAMENTO"].sum().sort_values(ascending=False)
    out, cum = [], 0.0
    for rank, (name, rev) in enumerate(top.head(TOP_PRODUCTS).items(), 1):
        g = recent[recent["PRODUTO"] == name]
        f = g["FATURAMENTO"]
        units = g["QUANTIDADE"].sum()
        unit_prices = (g["FATURAMENTO"] / g["QUANTIDADE"]).replace([np.inf, -np.inf], np.nan).dropna()
        cum += rev
        q1, q3 = f.quantile(0.25), f.quantile(0.75)
        out.append({
            "rank": rank, "product": name, "lines": len(g), "revenue": rev, "share_pct": 100 * rev / total, "cum_share_pct": 100 * cum / total,
            "median_ticket": f.median(), "mean_ticket": f.mean(), "q1": q1, "q3": q3, "iqr_over_median_pct": 100 * (q3 - q1) / f.median() if f.median() else None,
            "units": int(units), "price_weighted": rev / units if units else None, "price_plain_mean": unit_prices.mean() if len(unit_prices) else None,
            "revenue_prior_12m": float(prior_rev.get(name, 0.0)), "change_pct": 100 * (rev / prior_rev[name] - 1) if prior_rev.get(name, 0) > 0 else None,
        })
    return out


def concentration(s: pd.DataFrame, last_complete: pd.Period) -> list[dict]:
    recent = s[(s["month"] > last_complete - 12) & (s["month"] <= last_complete)]
    out = []
    for entity, key in (("Products", "PRODUTO"), ("Clients", "ID_CLIENTE"), ("Sale lines", None)):
        vals = (recent.groupby(key)["FATURAMENTO"].sum() if key else recent["FATURAMENTO"]).sort_values(ascending=False).to_numpy()
        cum = np.cumsum(vals) / vals.sum()
        n = len(vals)
        for p in [0, 1, 2, 3, 5, 7.5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            k = int(math.ceil(n * p / 100))
            out.append({"entity": entity, "top_pct": p, "cum_share_pct": 0.0 if k == 0 else 100 * float(cum[k - 1]), "count": n})
    return out


# ------------------------------------------------------------------ variability
def classify(dev_pct: float) -> str:
    return transform.classify_deviation(100 + dev_pct, 100.0)


def bands(s: pd.DataFrame, last_complete: pd.Period) -> list[dict]:
    m = s[(s["month"] <= last_complete)].groupby("month")["FATURAMENTO"].sum()
    out = []
    for month in m.index[-24:]:
        prev = m[(m.index < month)].tail(12)
        bench_mean, bench_med = float(prev.mean()), float(prev.median())
        dev = 100 * (float(m[month]) / bench_mean - 1)
        robust_spread = MAD_SCALE * float((prev - bench_med).abs().median())
        z = (float(m[month]) - bench_med) / robust_spread if robust_spread else None
        out.append({"month": str(month), "revenue": float(m[month]), "benchmark_mean": bench_mean, "benchmark_median": bench_med, "deviation_pct": dev,
                    "fixed_band": classify(dev), "robust_z": z, "robust_flag": "unusual" if z is not None and abs(z) > 2 else "normal",
                    "normal_swing_pct": 100 * robust_spread / bench_med})
    return out


def volatility(s: pd.DataFrame, last_complete: pd.Period) -> list[dict]:
    d = s[(s["month"] > last_complete - 24) & (s["month"] <= last_complete)]
    months = pd.period_range(last_complete - 23, last_complete, freq="M")
    out = []

    def add(kind: str, label: str, g: pd.DataFrame):
        m = g.groupby("month")["FATURAMENTO"].sum().reindex(months, fill_value=0.0)
        active = int((m > 0).sum())
        if active < 18 or m.mean() == 0:
            return
        out.append({"kind": kind, "group": label, "months_active": active, "mean_revenue": m.mean(), "median_revenue": m.median(), "cv_pct": 100 * m.std() / m.mean(),
                    "mad_pct": mad_pct(m), "max_over_median": float(m.max() / m.median()) if m.median() else None, "share_pct": 100 * g["FATURAMENTO"].sum() / d["FATURAMENTO"].sum()})

    add("All sales", ALL, d)
    for pay in PAYMENTS:
        add("Payment type", pay, d[d["TIPO_PAGAMENTO"] == pay])
    for st in sorted(d["TIPO_VENDA"].dropna().unique()):
        add("Sale type", st, d[d["TIPO_VENDA"] == st])
    top_blocks = d.groupby("BLOCO_NUM")["FATURAMENTO"].sum().sort_values(ascending=False).head(TOP_BLOCKS).index
    for b in top_blocks:
        add("Block", f"Block {b}", d[d["BLOCO_NUM"] == b])
    return out


def seasonality(s: pd.DataFrame, last_complete: pd.Period) -> list[dict]:
    m = s[(s["month"] <= last_complete)].groupby("month")["FATURAMENTO"].sum()
    m = m[m.index >= pd.Period("2019-01", "M")]
    trend = m.rolling(12, center=True).mean()
    ratio = (m / trend).dropna()
    ratio = ratio[(ratio.index.year >= 2020)]
    out = []
    for cal in range(1, 13):
        r = ratio[ratio.index.month == cal]
        if len(r):
            out.append({"calendar_month": cal, "typical_index": float(r.median()), "lowest_index": float(r.min()), "highest_index": float(r.max()), "years": len(r)})
    return out


# ------------------------------------------------------------------ doctors and patients
def visits(painel: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    d = painel["DIAS_SEM_VISITA_NUM"]
    known = d.dropna()
    edges = [(0, 30, "up to 30 days"), (30, 90, "31 to 90 days"), (90, 180, "91 to 180 days"), (180, 365, "181 to 365 days"), (365, 1e9, "over a year")]
    buckets = [{"order": i, "bucket": lab, "doctors": int(((known > lo) & (known <= hi)).sum()), "share_pct": 100 * float(((known > lo) & (known <= hi)).sum()) / len(d)} for i, (lo, hi, lab) in enumerate(edges)]
    buckets.append({"order": len(edges), "bucket": "no visit recorded", "doctors": int(d.isna().sum()), "share_pct": 100 * float(d.isna().mean())})
    groups = []
    for kind, col in (("State", "ESTADO"), ("Specialty", "ESPECIALIDADE")):
        for name, g in painel.groupby(col):
            x = g["DIAS_SEM_VISITA_NUM"].dropna()
            if len(x) < 40:
                continue
            groups.append({"kind": kind, "group": str(name), "doctors": len(g), "median_days": x.median(), "q1": x.quantile(0.25), "q3": x.quantile(0.75), "over_90_pct": 100 * float((x > 90).mean())})
    return buckets, groups


def churn(t: dict[str, pd.DataFrame]) -> list[dict]:
    cp, v, tv = t["carteira_pacientes"], t["vendas_660"], t["tipo_venda"]
    keys = ["ID_VENDA", "PRODUTO"]
    c = cp[cp["CHURN"].notna() & (cp["POSOLOGIA_SUSPEITA"] != True)].copy()  # noqa: E712
    c = c[c["DATA_VENDA"] >= "2024-01-01"]
    c["CHURN"] = c["CHURN"].astype(bool)
    c = c.merge(v[keys + ["TIPO_PAGAMENTO"]].drop_duplicates(keys), on=keys, how="left").merge(tv[keys + ["TIPO_VENDA"]].drop_duplicates(keys), on=keys, how="left")
    out = [{"kind": "All", "group": ALL, "patients_lines": len(c), "churn_pct": 100 * float(c["CHURN"].mean()), "median_stock_days": c["DIAS_ESTOQUE"].median()}]
    for kind, col in (("Payment type", "TIPO_PAGAMENTO"), ("Sale type", "TIPO_VENDA")):
        for name, g in c.groupby(col, dropna=True):
            if len(g) >= 100:
                out.append({"kind": kind, "group": str(name), "patients_lines": len(g), "churn_pct": 100 * float(g["CHURN"].mean()), "median_stock_days": g["DIAS_ESTOQUE"].median()})
    return out


# ------------------------------------------------------------------ data health
def health(t: dict[str, pd.DataFrame], s: pd.DataFrame, last_complete: pd.Period) -> tuple[list[dict], list[dict]]:
    v, tv, cp, pn, v15 = t["vendas_660"], t["tipo_venda"], t["carteira_pacientes"], t["painel"], t["vendas_1015"]
    today = pd.Timestamp.today().normalize()
    out = []

    def add(area, table, column, finding, count, share, severity, why, action):
        out.append({"area": area, "table": table, "column": column, "finding": finding, "count": int(count), "share_pct": None if share is None else float(share), "severity": severity, "why": why, "action": action})

    n = len(v)
    early = int((v["DATA_ENTREGA"] < "2016-01-01").sum())
    future = int((v["DATA_ENTREGA"] > today + pd.Timedelta(days=365)).sum())
    before = int((v["DATA_ENTREGA"] < v["DATA_VENDA"]).sum())
    add("Dates", "vendas_660", "DATA_ENTREGA", f"{before:,} lines are delivered before they were sold, {early} has a delivery year before 2016 and {future} more than a year ahead.", before + early + future, 100 * (before + early + future) / n, "Medium",
        "Any delay or lead-time calculation built on these dates will include impossible values.", "Exclude or correct impossible dates before measuring delivery time.")
    far = int((cp["DATA_RUPTURA"] > today + pd.Timedelta(days=5 * 365)).sum())
    extreme = int((cp["DIAS_ESTOQUE"] > 1000).sum())
    add("Dates", "carteira_pacientes", "DATA_RUPTURA / DIAS_ESTOQUE", f"{far} stock-out dates fall more than 5 years ahead, and {extreme} lines have more than 1,000 days of stock (the maximum is {n0(cp['DIAS_ESTOQUE'].max())}).", far + extreme, 100 * (far + extreme) / len(cp), "Medium",
        "A few extreme values stretch averages of stock days; the median ignores them.", "Report stock days with the median and the quartiles, and review the extreme lines at the source.")
    add("Types", "vendas_660", "DATA_ORCAMENTO", "The quote date is stored as text, not as a date.", n, 100.0, "Low", "Sorting or subtracting such a column gives wrong results with no error.", "Convert to a date type when it is loaded.")
    add("Types", "vendas_660", "PRIMEIRA_CLIENTE / PRIMEIRA_MEDICO / ESFORCO_CLIENTE / MARCA_PROPRIA",
        "Four yes/no flags are stored in two different ways: three as the text '0' and '1', and MARCA_PROPRIA as a decimal number with some empty cells.", n, 100.0, "Medium",
        "Comparing a flag with the wrong type (text '1' against number 1) returns zero rows and raises no error.", "Compare each flag in its own type, or convert all of them to true/false once, on load.")
    unk = s[s["TIPO_PAGAMENTO"] == "DESCONHECIDO"]
    share_by_year = (s.assign(u=s["TIPO_PAGAMENTO"] == "DESCONHECIDO").groupby("year")["u"].mean() * 100)
    until = int(share_by_year[share_by_year >= 99].index.max()) if (share_by_year >= 99).any() else None
    later = share_by_year[share_by_year.index > (until or 0) + 1]
    add("Completeness", "vendas_660", "TIPO_PAGAMENTO", f"{len(unk):,} sale lines have payment type 'unknown': every line up to {until}, {pct(share_by_year.get((until or 0) + 1, 0))} the year after, and at most {pct(later.max(), 1)} of the lines in any year since.", len(unk), 100 * len(unk) / len(s), "High",
        "Years before the payment type was recorded cannot be split by payment type, so trends by payment type only start in the later years.", "Compare payment types only from the first year where unknown is close to zero.")
    recent = s[(s["month"] > last_complete - 12) & (s["month"] <= last_complete)]
    nao = recent[recent["TIPO_VENDA"].isin(["NAO_INFORMADO", "Sem Classificacao"])]
    add("Completeness", "tipo_venda", "TIPO_VENDA", f"In the last 12 months, {len(nao):,} sale lines ({pct(100 * len(nao) / len(recent))}) are 'not informed' or 'without classification', worth {pct(100 * nao['FATURAMENTO'].sum() / recent['FATURAMENTO'].sum())} of revenue.",
        len(nao), 100 * len(nao) / len(recent), "Medium", "That part of revenue cannot be assigned to a sale type, so shares by sale type are understated.", "Find out why these lines are not classified and whether a rule can classify them.")
    nonsale = v[v["TIPO_REGISTRO"] != "VENDA"]
    add("Types", "vendas_660", "TIPO_REGISTRO", f"{len(nonsale):,} rows are donations, quotes or other records (revenue {n0(nonsale['FATURAMENTO'].sum())}); only 'VENDA' rows are sales.", len(nonsale), 100 * len(nonsale) / n, "Medium",
        "Averages and counts that include them are pulled down, because their revenue is zero.", "Always filter to sale rows first (the app does).")
    dup_id = n - v["ID_VENDA"].nunique()
    add("Keys", "vendas_660", "ID_VENDA", f"The sale ID repeats on {dup_id:,} rows (a sale with several products); sale ID + product is unique. The join with the sale type table matches every row once.", dup_id, 100 * dup_id / n, "Low",
        "Joining on the sale ID alone would multiply rows and inflate revenue.", "Keep joining on sale ID + product.")
    for tbl, df, col in (("vendas_660", v, "TIPO_FONTE"), ("vendas_660", v, "ULTIMO_CONTATO"), ("carteira_pacientes", cp, "DIAS_ESTOQUE"), ("painel", pn, "DIAS_SEM_VISITA_NUM")):
        e = df[col].isna().mean()
        add("Completeness", tbl, col, f"{pct(100 * e)} of the values are empty.", int(df[col].isna().sum()), 100 * e, "Medium" if e > 0.3 else "Low",
            "Statistics on this column describe only the rows that have a value, which may not be typical.", "State how many rows each figure is based on.")
    y16 = s[s["year"] == 2016]
    add("Coverage", "vendas_660", "DATA_VENDA", f"The data starts in 2016, but 2016 has only {len(y16)} sale lines with zero revenue; real activity starts in 2017.", len(y16), None, "Low", "Year-by-year comparisons that include 2016 are misleading.", "Start every trend in 2017.")
    add("Coverage", "vendas_1015", "DATA", f"The 1015 table covers only {v15['DATA'].min().date()} to {v15['DATA'].max().date()} and has {int(v15.duplicated().sum())} fully duplicated rows.", int(v15.duplicated().sum()), 100 * v15.duplicated().mean(), "Low",
        "Totals from this table would count some rows twice.", "Drop exact duplicates, and say the period it covers.")
    empty = []
    for tbl, df in t.items():
        for col in df.columns:
            e = float(df[col].isna().mean() * 100)
            if e >= 5:
                empty.append({"table": tbl, "column": col, "empty_pct": e, "stored_type": str(df[col].dtype)})
    empty.sort(key=lambda r: -r["empty_pct"])
    return out, empty


# ------------------------------------------------------------------ headline figures and written insights
def build_insights(s, yr, mo, prod, conc, bands_, vol, seas, vis_b, vis_g, ch, last_complete) -> list[dict]:
    ins = []

    def add(tab, title, finding, evidence, action):
        ins.append({"n": len(ins) + 1, "tab": tab, "title": title, "finding": finding, "evidence": evidence, "action": action})

    k = kpis(s, last_complete, s["DATA_VENDA"].max())[0]
    word = "below" if k["change_pct"] < 0 else "above"
    in_step = (k["change_pct"] < 0) == (k["lines_change_pct"] < 0) and abs(k["change_pct"] - k["lines_change_pct"]) < 3
    add("typical", f"Revenue is {abs(k['change_pct']):.0f}% {word} a year ago" + (", in step with the number of sale lines" if in_step else ", and the mix of orders explains it"),
        f"The last 12 months made {n0(k['last_12m_revenue'])}, {pct(k['change_pct'], 1)} against the 12 months before. The number of sale lines changed by {pct(k['lines_change_pct'], 1)} and the median line is {n0(k['median_ticket'])}.",
        "Revenue moved by about as much as the number of lines, so the typical order did not change." if in_step else "Lines and revenue moved by different amounts, so the mix of small and large orders changed.",
        "Compare the number of lines and the large orders (court-ordered and institutional) before reading a revenue change as a change in demand.")
    y = pd.DataFrame(yr)
    allrows = y[(y["payment"] == ALL) & (y["sale_type"] == ALL)].set_index("year")
    cal = [int(c) for c in allrows.index if c >= 2022 and not allrows.loc[c, "partial"]]
    c0, c1 = cal[-2], cal[-1]
    add("typical", "The typical sale is stable; the average follows a few large orders",
        f"In {c0} and {c1} the median sale line was {n0(allrows.loc[c0, 'median_ticket'])} and {n0(allrows.loc[c1, 'median_ticket'])}, while the mean was {n0(allrows.loc[c0, 'mean_ticket'])} and {n0(allrows.loc[c1, 'mean_ticket'])}.",
        "The mean is pulled up by the few very large orders; the median follows the usual order.", "Use the median (and the quartiles) to describe a normal sale, and the mean only when you need a total.")
    p = y[(y["sale_type"] == ALL) & (y["year"] == c1)].set_index("payment")
    if "JUDICIAL" in p.index and "RECURSO PROPRIO" in p.index:
        jl, rl = p.loc["JUDICIAL", "lines"], p.loc["RECURSO PROPRIO", "lines"]
        jr, rr = p.loc["JUDICIAL", "revenue"], p.loc["RECURSO PROPRIO", "revenue"]
        add("typical", "Court-ordered sales are few and large",
            f"In {c1}, judicial sales were {pct(100 * jl / (jl + rl))} of the lines but {pct(100 * jr / (jr + rr))} of the revenue. Their median line is {n0(p.loc['JUDICIAL', 'median_ticket'])}, against {n0(p.loc['RECURSO PROPRIO', 'median_ticket'])} for own-funds sales.",
            "Two kinds of sale with very different sizes sit in the same totals.", "Report them separately; a single average describes neither.")
    st = y[(y["payment"] == ALL) & (y["year"] == c1) & (y["sale_type"] != ALL)].sort_values("revenue", ascending=False)
    if len(st):
        tot = st["revenue"].sum()
        big = st.sort_values("median_ticket", ascending=False).iloc[0]
        add("typical", "A handful of institutional orders weigh a fifth of revenue",
            f"The sale type '{big['sale_type']}' had {n0(big['lines'])} lines in {c1} with a median of {n0(big['median_ticket'])} each, and made {pct(100 * big['revenue'] / tot)} of revenue.", "A few lines carry a large share, so one lost or late order moves the month.", "Track these orders one by one, and keep them out of 'typical' figures.")
    cc = pd.DataFrame(conc)
    prc = cc[(cc["entity"] == "Products") & (cc["top_pct"] == 10)].iloc[0]
    clc = cc[(cc["entity"] == "Clients") & (cc["top_pct"] == 1)].iloc[0]
    lnc = cc[(cc["entity"] == "Sale lines") & (cc["top_pct"] == 1)].iloc[0]
    add("typical", "Revenue is concentrated in a few products, clients and lines",
        f"In the last 12 months the top 10% of products made {pct(prc['cum_share_pct'])} of revenue, the top 1% of clients {pct(clc['cum_share_pct'])} and the top 1% of sale lines {pct(lnc['cum_share_pct'])}.", "The business depends on few items; averages across all products hide this.", "Segment by the top products and the top clients before comparing anything.")
    pr = pd.DataFrame(prod)
    gap = pr.assign(g=(pr["price_plain_mean"] / pr["price_weighted"] - 1) * 100).sort_values("g", ascending=False).iloc[0]
    add("typical", "A plain average price is not the price paid per unit",
        f"For {gap['product']}, the plain average of line prices is {n0(gap['price_plain_mean'])} per unit, but weighting by units gives {n0(gap['price_weighted'])}, a gap of {pct(gap['g'])}.", "Small orders and large orders do not count the same in the weighted price.", "Quote a price per unit as total revenue divided by total units.")
    b = pd.DataFrame(bands_)
    non_neutral = int((b["fixed_band"] != "NEUTRAL").sum())
    unusual = int((b["robust_flag"] == "unusual").sum())
    sw = float(b["normal_swing_pct"].median())
    add("variation", "A fixed band calls most months 'not neutral'; the data's own spread does not",
        f"Over the last {len(b)} months, the app's fixed ±10% band would call {non_neutral} months not neutral. Judged against each month's own history (a robust spread of about ±{sw:.0f}%), only {unusual} are unusual.",
        "Monthly revenue normally swings more than 10%, so a fixed band flags normal months.", "Size the neutral band from the metric's own spread (MAD or IQR) instead of a fixed percentage.")
    v = pd.DataFrame(vol)
    tot = v[v["kind"] == "All sales"].iloc[0]
    add("variation", "Total revenue got steadier",
        f"Over the last 24 months, monthly revenue varied by {pct(tot['cv_pct'])} around its mean (coefficient of variation), against {pct(100 * v_all_cv(s, last_complete))} since 2019.", "Growth years inflate the spread; the recent months are calmer.", "Judge the current months against the recent history, not the whole history.")
    seg = v[v["kind"].isin(["Payment type", "Sale type", "Block"])].sort_values("cv_pct", ascending=False)
    hi, lo = seg.iloc[0], seg.iloc[-1]
    add("variation", "Some segments swing far more than others",
        f"{hi['kind']} '{hi['group']}' varies by {pct(hi['cv_pct'])} month to month and reaches {hi['max_over_median']:.1f} times its median month; '{lo['group']}' varies by only {pct(lo['cv_pct'])}.", "The same percentage deviation means different things for a steady and a volatile segment.", "Read a deviation against the segment's own spread.")
    sd = pd.DataFrame(seas)
    top, bot = sd.sort_values("typical_index", ascending=False).iloc[0], sd.sort_values("typical_index").iloc[0]
    names = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    add("variation", "There is a seasonal rhythm",
        f"After removing the yearly trend, {names[int(bot['calendar_month'])]} is the weakest month (typically {pct(100 * bot['typical_index'])} of its trend) and {names[int(top['calendar_month'])]} the strongest ({pct(100 * top['typical_index'])}).", "Comparing one month with the previous one mixes season with performance.", "Compare a month with the same month of earlier years.")
    vb = pd.DataFrame(vis_b)
    over90 = 100 * float(vb[vb["order"].isin([2, 3, 4])]["doctors"].sum()) / float(vb[vb["order"] < 5]["doctors"].sum())
    vg = pd.DataFrame(vis_g)
    st_ = vg[vg["kind"] == "State"].sort_values("median_days")
    add("people", "Visit coverage is uneven across states",
        f"{pct(over90)} of the doctors with a recorded visit were last visited more than 90 days ago. The median is {n0(st_.iloc[0]['median_days'])} days in {st_.iloc[0]['group']} but {n0(st_.iloc[-1]['median_days'])} days in {st_.iloc[-1]['group']}.",
        "A national median hides regions that are barely covered.", "Plan visits by state, starting with the states whose median is above 90 days.")
    c = pd.DataFrame(ch)
    pay = c[c["kind"] == "Payment type"].sort_values("churn_pct", ascending=False)
    sty = c[(c["kind"] == "Sale type") & (c["patients_lines"] >= 1000)].sort_values("churn_pct", ascending=False)
    if len(pay) >= 2 and len(sty) >= 2:
        add("people", "Churn differs a lot by payment type and by sale type",
            f"Among sales since 2024, {pct(pay.iloc[0]['churn_pct'], 1)} of '{pay.iloc[0]['group']}' lines are churn, against {pct(pay.iloc[-1]['churn_pct'], 1)} for '{pay.iloc[-1]['group']}'. By sale type it runs from {pct(sty.iloc[0]['churn_pct'], 1)} ('{sty.iloc[0]['group']}') to {pct(sty.iloc[-1]['churn_pct'], 1)} ('{sty.iloc[-1]['group']}').",
            "One overall churn rate mixes patients with very different behaviour.", "Follow churn separately by payment type and by sale type.")
    return ins


def v_all_cv(s: pd.DataFrame, last_complete: pd.Period) -> float:
    m = s[(s["month"] >= pd.Period("2019-01", "M")) & (s["month"] <= last_complete)].groupby("month")["FATURAMENTO"].sum()
    return float(m.std() / m.mean())


def kpis(s: pd.DataFrame, last_complete: pd.Period, last_date: pd.Timestamp) -> list[dict]:
    recent = s[(s["month"] > last_complete - 12) & (s["month"] <= last_complete)]
    prior = s[(s["month"] > last_complete - 24) & (s["month"] <= last_complete - 12)]
    return [{
        "last_12m_revenue": recent["FATURAMENTO"].sum(), "prior_12m_revenue": prior["FATURAMENTO"].sum(), "change_pct": 100 * (recent["FATURAMENTO"].sum() / prior["FATURAMENTO"].sum() - 1),
        "last_12m_lines": len(recent), "prior_12m_lines": len(prior), "lines_change_pct": 100 * (len(recent) / len(prior) - 1), "median_ticket": recent["FATURAMENTO"].median(), "mean_ticket": recent["FATURAMENTO"].mean(), "clients": recent["ID_CLIENTE"].nunique(), "products": recent["PRODUTO"].nunique(),
        "first_month": "2017-01", "last_complete_month": str(last_complete), "last_sale_date": str(last_date.date()), "total_lines": len(s),
    }]


# ------------------------------------------------------------------ main
def main(out_dir: Path) -> None:
    t = load()
    s = sale_lines(t)
    last_date = s["DATA_VENDA"].max()
    last_complete = last_date.to_period("M") - 1 if last_date.day < last_date.days_in_month else last_date.to_period("M")
    yr = yearly(s, last_date.year, last_date)
    mo = monthly(s, last_complete)
    prod = products(s, last_complete)
    conc = concentration(s, last_complete)
    bands_ = bands(s, last_complete)
    vol = volatility(s, last_complete)
    seas = seasonality(s, last_complete)
    vis_b, vis_g = visits(t["painel"])
    ch = churn(t)
    issues, empty = health(t, s, last_complete)
    ins = build_insights(s, yr, mo, prod, conc, bands_, vol, seas, vis_b, vis_g, ch, last_complete)
    files = {"kpis": kpis(s, last_complete, last_date), "yearly": yr, "monthly": mo, "products": prod, "concentration": conc, "bands": bands_, "volatility": vol, "seasonality": seas,
             "visit_buckets": vis_b, "visit_groups": vis_g, "churn": ch, "health": issues, "empty_cells": empty, "insights": ins}
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        data = [{k: clean(v) for k, v in r.items()} for r in data]
        (out_dir / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False))
        print(f"{name}: {len(data)} rows, {(out_dir / f'{name}.json').stat().st_size:,} bytes")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "out")
