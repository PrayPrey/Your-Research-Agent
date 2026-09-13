"""P1/P2/P3/P4 hypothesis tests: Wald z-test, LRT, FDR correction."""
from __future__ import annotations
import json
import logging
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2, norm
from statsmodels.stats.multitest import multipletests

log = logging.getLogger(__name__)


def run_p1_p2_tests(
    focal_coeffs: dict[str, dict[str, dict]],
    alpha: float = 0.05,
) -> dict:
    """
    P1: β_Wikipedia > β_Books3 for MMLU (one-tailed Wald z-test)
    P2: β_Books3 > β_Wikipedia for HellaSwag (one-tailed)

    Note: N=16 clusters borderline for clustered SE normality; document.
    """
    def wald_z_one_tailed(beta1: float, se1: float, beta2: float, se2: float):
        z = (beta1 - beta2) / np.sqrt(se1 ** 2 + se2 ** 2)
        p = 1.0 - norm.cdf(z)
        return float(z), float(p)

    wiki = "Wikipedia (en)"
    books = "Books3"

    mmlu = focal_coeffs.get("mmlu", {})
    beta_wiki_mmlu = mmlu.get(wiki, {}).get("beta", np.nan)
    se_wiki_mmlu = mmlu.get(wiki, {}).get("se", np.nan)
    beta_books_mmlu = mmlu.get(books, {}).get("beta", np.nan)
    se_books_mmlu = mmlu.get(books, {}).get("se", np.nan)
    z1, p1 = wald_z_one_tailed(beta_wiki_mmlu, se_wiki_mmlu, beta_books_mmlu, se_books_mmlu)

    hs = focal_coeffs.get("hellaswag", {})
    beta_books_hs = hs.get(books, {}).get("beta", np.nan)
    se_books_hs = hs.get(books, {}).get("se", np.nan)
    beta_wiki_hs = hs.get(wiki, {}).get("beta", np.nan)
    se_wiki_hs = hs.get(wiki, {}).get("se", np.nan)
    z2, p2 = wald_z_one_tailed(beta_books_hs, se_books_hs, beta_wiki_hs, se_wiki_hs)

    result = {
        "P1": {
            "direction": bool(beta_wiki_mmlu > beta_books_mmlu),
            "z": z1,
            "p_one_tailed": p1,
            "passed": bool(not np.isnan(beta_wiki_mmlu) and beta_wiki_mmlu > beta_books_mmlu and p1 < alpha),
            "beta_wiki_mmlu": float(beta_wiki_mmlu) if not np.isnan(beta_wiki_mmlu) else None,
            "beta_books_mmlu": float(beta_books_mmlu) if not np.isnan(beta_books_mmlu) else None,
            "alpha": alpha,
        },
        "P2": {
            "direction": bool(beta_books_hs > beta_wiki_hs),
            "z": z2,
            "p_one_tailed": p2,
            "passed": bool(not np.isnan(beta_books_hs) and beta_books_hs > beta_wiki_hs and p2 < alpha),
            "beta_books_hs": float(beta_books_hs) if not np.isnan(beta_books_hs) else None,
            "beta_wiki_hs": float(beta_wiki_hs) if not np.isnan(beta_wiki_hs) else None,
            "alpha": alpha,
        },
    }
    log.info(f"P1: direction={result['P1']['direction']}, p={p1:.4f}, passed={result['P1']['passed']}")
    log.info(f"P2: direction={result['P2']['direction']}, p={p2:.4f}, passed={result['P2']['passed']}")
    return result


def _get_loglik_from_panel_result(res) -> float:
    """Extract log-likelihood from PanelOLS result."""
    if hasattr(res, "loglik"):
        try:
            return float(res.loglik)
        except Exception:
            pass
    n = res.nobs
    rss = float((res.resids ** 2).sum())
    return -n / 2 * (1 + np.log(2 * np.pi * rss / n))


def _fit_pair_shared_ll(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    b1: str,
    b2: str,
) -> float:
    """Fit pair-specific shared-beta OLS and return log-likelihood."""
    import statsmodels.api as sm

    frames = []
    for bench in [b1, b2]:
        sub = panel_df[domain_cols + [bench, "log_params"]].copy()
        sub = sub.rename(columns={bench: "score"})
        sub["benchmark"] = bench
        sub["model_size"] = sub.index.get_level_values("model_size")
        frames.append(sub.reset_index(drop=True))

    stacked = pd.concat(frames, ignore_index=True)
    safe_map = {d: d.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
                for d in domain_cols}
    for orig, safe in safe_map.items():
        stacked[safe] = stacked[orig]
    safe_cols = list(safe_map.values())

    bench_dummies = pd.get_dummies(stacked["benchmark"], drop_first=True, prefix="bench")
    size_dummies = pd.get_dummies(stacked["model_size"], drop_first=True, prefix="size")
    X = pd.concat([stacked[safe_cols], bench_dummies, size_dummies], axis=1)
    X = sm.add_constant(X)
    y = stacked["score"]
    return sm.OLS(y.astype(float), X.astype(float)).fit().llf


def run_lrt_all_pairs(
    benchmark_results: dict,
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    benchmarks: list[str],
    n_domain_cols: int,
) -> pd.DataFrame:
    """
    Run LRT for all 6 pairwise benchmark comparisons.
    lr_stat = 2*(LL_b1 + LL_b2 - LL_shared_pair), df = n_domain_cols.
    """
    rows = []
    for b1, b2 in combinations(benchmarks, 2):
        ll_b1 = _get_loglik_from_panel_result(benchmark_results[b1])
        ll_b2 = _get_loglik_from_panel_result(benchmark_results[b2])
        try:
            ll_shared = _fit_pair_shared_ll(panel_df, domain_cols, b1, b2)
        except Exception as e:
            log.warning(f"Shared-β LL failed for {b1} vs {b2}: {e}")
            ll_shared = ll_b1 + ll_b2 - 1.0  # conservative: lr_stat=2

        lr_stat = 2.0 * (ll_b1 + ll_b2 - ll_shared)
        df = n_domain_cols
        p_value = float(chi2.sf(max(lr_stat, 0.0), df))
        rows.append({
            "pair": f"{b1}_vs_{b2}",
            "b1": b1, "b2": b2,
            "lr_stat": float(lr_stat),
            "df": df,
            "p_value": p_value,
        })
        log.info(f"LRT {b1} vs {b2}: lr_stat={lr_stat:.4f}, p={p_value:.4f}")

    return pd.DataFrame(rows).set_index("pair")


def apply_fdr_correction(
    lrt_df: pd.DataFrame,
    alpha: float = 0.05,
) -> dict:
    """BH FDR correction on 6 LRT p-values. P3 passes if >=2 pairs significant."""
    pvals = lrt_df["p_value"].values
    reject, pvals_corrected, _, _ = multipletests(pvals, alpha=alpha, method="fdr_bh")
    result = {
        "reject": reject.tolist(),
        "pvals_corrected": pvals_corrected.tolist(),
        "n_significant": int(reject.sum()),
        "p3_passed": bool(reject.sum() >= 2),
        "pairs": lrt_df.index.tolist(),
        "alpha": alpha,
    }
    log.info(f"FDR correction: {result['n_significant']}/6 pairs significant, P3={'PASS' if result['p3_passed'] else 'FAIL'}")
    return result


def evaluate_gate(
    p1_result: dict,
    p2_result: dict,
    fdr_result: dict,
    p4_result: dict | None = None,
) -> dict:
    """
    SHOULD_WORK gate routing:
        PRIMARY_PASS: P1 AND P2 -> PASS
        SECONDARY_PASS: P3 -> PASS (with note)
        MINIMUM_PASS: P1 OR P2 -> EXPLORE
        ALL_FAIL -> PIVOT
    """
    p1 = p1_result["P1"]["passed"]
    p2 = p2_result["P2"]["passed"]
    p3 = fdr_result["p3_passed"]
    p4 = p4_result.get("passed", False) if p4_result else None

    if p1 and p2:
        route = "PASS"
        status = "PRIMARY_PASS"
    elif p3:
        route = "PASS"
        status = "SECONDARY_PASS"
    elif p1 or p2:
        route = "EXPLORE"
        status = "MINIMUM_PASS"
    else:
        route = "PIVOT"
        status = "ALL_FAIL"

    result = {
        "gate_type": "SHOULD_WORK",
        "status": status,
        "route": route,
        "P1_passed": p1,
        "P2_passed": p2,
        "P3_passed": p3,
        "P4_passed": p4,
        "n_lrt_significant": fdr_result["n_significant"],
    }
    log.info(f"Gate: {status} -> {route}")
    return result


def save_gate_results(
    p1_p2: dict,
    fdr: dict,
    gate: dict,
    output_dir: Path,
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "gate_summary.json").write_text(json.dumps({
        "p1_p2": p1_p2,
        "fdr": fdr,
        "gate": gate,
    }, indent=2))
    log.info("Gate results saved")


if __name__ == "__main__":
    # self-check (not a pytest test)
    focal = {
        "mmlu": {
            "Wikipedia (en)": {"beta": 0.5, "se": 0.1},
            "Books3": {"beta": 0.2, "se": 0.1},
        },
        "hellaswag": {
            "Wikipedia (en)": {"beta": 0.1, "se": 0.1},
            "Books3": {"beta": 0.4, "se": 0.1},
        },
    }
    result = run_p1_p2_tests(focal)
    assert result["P1"]["direction"] is True
    assert result["P2"]["direction"] is True
    print("PASS: hypothesis_tests self-check")
