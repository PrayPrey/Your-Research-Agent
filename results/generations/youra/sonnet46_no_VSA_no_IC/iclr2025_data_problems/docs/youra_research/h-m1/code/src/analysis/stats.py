"""Welch ANOVA, eta-sq, Tukey HSD, gate evaluation."""
from __future__ import annotations

import numpy as np
import pandas as pd
import scipy.stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def welch_anova(
    domain_scores: dict[str, list[float]],
    proxy_name: str = "proxy",
) -> dict:
    """One-way Welch's ANOVA across all domains for one proxy metric."""
    groups = list(domain_scores.values())

    F, p_value = scipy.stats.f_oneway(*groups)

    rows = []
    for domain, scores in domain_scores.items():
        for score in scores:
            rows.append({"domain": domain, proxy_name: score})
    df = pd.DataFrame(rows)

    # sanitize proxy_name for formula (replace spaces/special chars)
    safe_name = proxy_name.replace(" ", "_").replace("-", "_")
    if safe_name != proxy_name:
        df = df.rename(columns={proxy_name: safe_name})
        proxy_name = safe_name

    model = ols(f"{proxy_name} ~ C(domain)", data=df).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    ss_between = anova_table["sum_sq"]["C(domain)"]
    ss_total = float(anova_table["sum_sq"].sum())
    eta_squared = float(ss_between / ss_total) if ss_total > 0 else 0.0

    return {
        "F": float(F),
        "p_value": float(p_value),
        "eta_squared": eta_squared,
        "n_groups": len(groups),
        "significant": bool(p_value < 0.05),
    }


def tukey_hsd(
    domain_scores: dict[str, list[float]],
    alpha: float = 0.05,
) -> object:
    """Tukey HSD post-hoc pairwise comparisons for one proxy metric."""
    endog = []
    groups = []
    for domain, scores in domain_scores.items():
        endog.extend(scores)
        groups.extend([domain] * len(scores))

    return pairwise_tukeyhsd(
        endog=np.array(endog),
        groups=np.array(groups),
        alpha=alpha,
    )


def get_pair_result(tukey_result, group1: str, group2: str) -> dict:
    """Extract result for a specific domain pair from Tukey HSD results."""
    data = tukey_result._results_table.data
    df = pd.DataFrame(data[1:], columns=data[0])
    mask = (
        ((df["group1"] == group1) & (df["group2"] == group2)) |
        ((df["group1"] == group2) & (df["group2"] == group1))
    )
    row = df[mask]
    if row.empty:
        return {"reject": None, "meandiff": None, "p_adj": None}
    return {
        "reject": bool(row["reject"].iloc[0]),
        "meandiff": float(row["meandiff"].iloc[0]),
        "p_adj": float(row["p-adj"].iloc[0]),
    }


def domain_summary_stats(
    domain_scores: dict[str, dict[str, list[float]]],
) -> pd.DataFrame:
    """Per-domain summary statistics for all proxy metrics."""
    rows = []
    for domain, proxies in domain_scores.items():
        for proxy, scores in proxies.items():
            arr = np.array(scores)
            n = len(arr)
            if n == 0:
                continue
            mean = float(arr.mean())
            std = float(arr.std(ddof=1)) if n > 1 else 0.0
            sem = scipy.stats.sem(arr) if n > 1 else 0.0
            if n > 1:
                ci = scipy.stats.t.interval(0.95, df=n - 1, loc=mean, scale=sem)
            else:
                ci = (mean, mean)
            rows.append({
                "domain": domain,
                "proxy": proxy,
                "mean": mean,
                "std": std,
                "ci_lower": float(ci[0]),
                "ci_upper": float(ci[1]),
                "n": n,
            })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    entity_order = (
        df[df["proxy"] == "entity_density"]
        .sort_values("mean", ascending=False)["domain"]
        .tolist()
    )
    df["domain_order"] = df["domain"].map(
        {d: i for i, d in enumerate(entity_order)}
    )
    return df.sort_values(["domain_order", "proxy"]).drop(columns="domain_order")


def evaluate_gate(
    domain_scores: dict[str, dict[str, list[float]]],
    anova_results: dict[str, dict],
    tukey_results: dict[str, object],
    wiki_domain: str = "Wikipedia (en)",
    books_domain: str = "BookCorpus2",
) -> dict:
    """Evaluate H-M1 gate criteria."""

    def mean_score(domain: str, proxy: str) -> float:
        scores = domain_scores.get(domain, {}).get(proxy, [])
        return float(np.mean(scores)) if scores else float("nan")

    wiki_entity = mean_score(wiki_domain, "entity_density")
    books_entity = mean_score(books_domain, "entity_density")
    wiki_coherence = mean_score(wiki_domain, "narrative_coherence")
    books_coherence = mean_score(books_domain, "narrative_coherence")

    # Also try Bibliotik as fallback for books
    if np.isnan(books_entity) or books_entity == 0:
        books_domain_alt = "Bibliotik"
        books_entity_alt = mean_score(books_domain_alt, "entity_density")
        books_coherence_alt = mean_score(books_domain_alt, "narrative_coherence")
        if not np.isnan(books_entity_alt):
            books_entity = books_entity_alt
            books_coherence = books_coherence_alt
            books_domain = books_domain_alt

    entity_anova = anova_results.get("entity_density", {})
    coherence_anova = anova_results.get("narrative_coherence", {})

    entity_tukey = get_pair_result(
        tukey_results["entity_density"], wiki_domain, books_domain
    )
    coherence_tukey = get_pair_result(
        tukey_results["narrative_coherence"], books_domain, wiki_domain
    )

    crit1 = (
        wiki_entity > books_entity
        and entity_anova.get("p_value", 1.0) < 0.05
        and entity_anova.get("eta_squared", 0.0) > 0.1
    )

    crit2 = (
        books_coherence > wiki_coherence
        and coherence_anova.get("p_value", 1.0) < 0.05
    )

    gate_pass = crit1 and crit2

    return {
        "gate_pass": gate_pass,
        "books_domain_used": books_domain,
        "criterion_1_entity_density": {
            "wiki_mean": wiki_entity,
            "books_mean": books_entity,
            "direction_correct": wiki_entity > books_entity,
            "p_value": entity_anova.get("p_value"),
            "eta_squared": entity_anova.get("eta_squared"),
            "tukey_reject": entity_tukey.get("reject"),
            "pass": crit1,
        },
        "criterion_2_narrative_coherence": {
            "books_mean": books_coherence,
            "wiki_mean": wiki_coherence,
            "direction_correct": books_coherence > wiki_coherence,
            "p_value": coherence_anova.get("p_value"),
            "tukey_reject": coherence_tukey.get("reject"),
            "pass": crit2,
        },
    }


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    scores = {
        "A": rng.normal(0.1, 0.02, 100).tolist(),
        "B": rng.normal(0.05, 0.02, 100).tolist(),
        "C": rng.normal(0.08, 0.02, 100).tolist(),
    }
    result = welch_anova(scores, proxy_name="entity_density")
    assert result["p_value"] < 0.05
    assert 0 < result["eta_squared"] <= 1
    print("L-5-1 self-check PASS")
