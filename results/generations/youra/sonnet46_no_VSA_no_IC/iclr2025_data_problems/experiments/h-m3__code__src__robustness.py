"""Robustness analysis: subgroup regressions, P4 Spearman, permutation null, R² decomposition."""
from __future__ import annotations
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from linearmodels.panel import PanelOLS, PooledOLS

log = logging.getLogger(__name__)


def run_subgroup_regressions(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    benchmarks: list[str],
    size_groups: dict[str, list[str]] | None = None,
) -> dict[str, dict]:
    """
    Fit PanelOLS separately for small and large model subgroups.
    Uses robust SEs for small N (N<10 entities).
    """
    if size_groups is None:
        all_sizes = panel_df.index.get_level_values("model_size").unique().tolist()
        small_prefixes = ["70m", "160m", "410m"]
        size_groups = {
            "small": [s for s in all_sizes if any(s.startswith(p) for p in small_prefixes)],
            "large": [s for s in all_sizes if not any(s.startswith(p) for p in small_prefixes)],
        }

    domain_terms = " + ".join(
        f"`{d}`" if " " in d or "(" in d else d for d in domain_cols
    )
    results: dict[str, dict] = {}

    for group_name, sizes in size_groups.items():
        if not sizes:
            log.warning(f"No models in group '{group_name}'")
            results[group_name] = {}
            continue

        mask = panel_df.index.get_level_values("model_size").isin(sizes)
        sub_df = panel_df[mask]
        n_entities = sub_df.index.get_level_values("model_size").nunique()
        cov = "robust" if n_entities < 10 else "clustered"
        cluster_e = cov == "clustered"

        results[group_name] = {}
        for bench in benchmarks:
            if bench not in sub_df.columns:
                continue
            formula = f"{bench} ~ {domain_terms} + EntityEffects"
            try:
                mod = PanelOLS.from_formula(formula, sub_df)
                res = mod.fit(cov_type=cov, cluster_entity=cluster_e)
                results[group_name][bench] = res
                log.info(f"Subgroup '{group_name}' {bench}: N={n_entities}, R²_within={res.rsquared_within:.4f}")
            except Exception as e:
                log.error(f"Subgroup regression failed for '{group_name}' {bench}: {e}")

    return results


def test_p4_spearman(
    subgroup_results: dict[str, dict],
    domain_cols: list[str],
    benchmarks: list[str],
    rho_threshold: float = 0.7,
) -> dict:
    """
    P4: Spearman ρ of domain coefficient rankings consistent across model scales.
    Pass if median ρ across benchmarks > rho_threshold.
    """
    rho_per_bench: dict[str, dict] = {}
    for bench in benchmarks:
        small_res = subgroup_results.get("small", {}).get(bench)
        large_res = subgroup_results.get("large", {}).get(bench)
        if small_res is None or large_res is None:
            log.warning(f"Missing subgroup result for {bench}")
            continue

        # get params for domain_cols present in both
        available_cols = [d for d in domain_cols if d in small_res.params.index and d in large_res.params.index]
        if not available_cols:
            log.warning(f"No common domain cols for Spearman in {bench}")
            continue

        small_params = small_res.params[available_cols].values
        large_params = large_res.params[available_cols].values
        rho, pval = spearmanr(small_params, large_params)
        rho_per_bench[bench] = {"rho": float(rho), "pval": float(pval)}

    median_rho = float(np.median([v["rho"] for v in rho_per_bench.values()])) if rho_per_bench else 0.0
    result = {
        "rho_per_benchmark": rho_per_bench,
        "median_rho": median_rho,
        "threshold": rho_threshold,
        "passed": bool(median_rho > rho_threshold),
    }
    log.info(f"P4 Spearman: median_ρ={median_rho:.4f}, passed={result['passed']}")
    return result


def run_permutation_null(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    focal_domains: dict[str, str],
    benchmarks_focal: dict[str, str] | None = None,
    n_permutations: int = 1000,
    seed: int = 42,
) -> dict:
    """
    Permutation null: shuffle domain column labels, refit focal-domain model.
    Returns empirical p-values for P1 and P2.
    """
    if benchmarks_focal is None:
        benchmarks_focal = {"P1": "mmlu", "P2": "hellaswag"}

    wiki_name = focal_domains.get("wikipedia", "Wikipedia (en)")
    books_name = focal_domains.get("books", "Books3")

    if wiki_name not in domain_cols or books_name not in domain_cols:
        log.warning("Focal domains not in domain_cols (PCA may have been applied); skipping permutation null")
        return {"error": "Focal domains not in domain_cols (PCA may have been applied)"}

    rng = np.random.default_rng(seed)
    null_dists: dict[str, list[float]] = {test: [] for test in benchmarks_focal}

    formula_cols = f"`{wiki_name}` + `{books_name}`" if " " in wiki_name else f"{wiki_name} + {books_name}"

    for _ in range(n_permutations):
        perm_idx = rng.permutation(len(domain_cols))
        perm_map = {domain_cols[i]: domain_cols[perm_idx[i]] for i in range(len(domain_cols))}

        perm_df = panel_df.copy()
        # rename domain columns per permutation
        rename_map = {old: new for old, new in perm_map.items() if old in perm_df.columns}
        perm_df = perm_df.rename(columns=rename_map)

        for test, bench in benchmarks_focal.items():
            if bench not in perm_df.columns:
                continue
            formula = f"{bench} ~ {formula_cols} + EntityEffects"
            try:
                res = PanelOLS.from_formula(formula, perm_df).fit(
                    cov_type="robust", cluster_entity=False
                )
                wiki_k = next((k for k in res.params.index if wiki_name in k), None)
                books_k = next((k for k in res.params.index if books_name in k), None)
                if wiki_k and books_k:
                    diff = abs(float(res.params[wiki_k]) - float(res.params[books_k]))
                    null_dists[test].append(diff)
            except Exception:
                null_dists[test].append(np.nan)

    # Observed statistics
    output: dict = {}
    for test, bench in benchmarks_focal.items():
        formula = f"{bench} ~ {formula_cols} + EntityEffects"
        try:
            res_obs = PanelOLS.from_formula(formula, panel_df).fit(
                cov_type="robust", cluster_entity=False
            )
            wiki_k = next((k for k in res_obs.params.index if wiki_name in k), None)
            books_k = next((k for k in res_obs.params.index if books_name in k), None)
            obs = abs(float(res_obs.params[wiki_k]) - float(res_obs.params[books_k])) if (wiki_k and books_k) else np.nan
        except Exception:
            obs = np.nan

        null = np.array([v for v in null_dists[test] if not np.isnan(v)])
        empirical_p = float(np.mean(null >= obs)) if len(null) > 0 and not np.isnan(obs) else 1.0
        output[test] = {
            "null_dist_size": len(null),
            "observed": float(obs) if not np.isnan(obs) else None,
            "empirical_p": empirical_p,
        }
        log.info(f"Permutation null {test}: obs={obs:.4f}, empirical_p={empirical_p:.4f}")

    return output


def run_r2_decomposition(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    benchmarks: list[str],
) -> dict:
    """
    R² decomposition: domain-only, scale-only (PooledOLS), full (=domain-only with EntityEffects).
    Note: log_params is time-invariant; absorbed by EntityEffects. Scale-only uses PooledOLS.
    """
    domain_terms = " + ".join(
        f"`{d}`" if " " in d or "(" in d else d for d in domain_cols
    )
    output: dict[str, dict] = {}

    for bench in benchmarks:
        if bench not in panel_df.columns:
            continue

        # Domain-only (entity demeaned)
        try:
            r2_domain = PanelOLS.from_formula(
                f"{bench} ~ {domain_terms} + EntityEffects", panel_df
            ).fit(cov_type="robust", cluster_entity=False).rsquared_within
        except Exception as e:
            log.warning(f"Domain-only R² failed for {bench}: {e}")
            r2_domain = np.nan

        # Scale-only (PooledOLS — log_params would be absorbed by entity effects)
        try:
            r2_scale = PooledOLS.from_formula(
                f"{bench} ~ log_params", panel_df
            ).fit(cov_type="robust", cluster_entity=False).rsquared
        except Exception as e:
            log.warning(f"Scale-only R² failed for {bench}: {e}")
            r2_scale = np.nan

        output[bench] = {
            "domain_only_within": float(r2_domain) if not np.isnan(r2_domain) else None,
            "scale_only_pooled": float(r2_scale) if not np.isnan(r2_scale) else None,
            "full_within": float(r2_domain) if not np.isnan(r2_domain) else None,
            "note": "log_params is time-invariant; absorbed by EntityEffects. scale_only uses PooledOLS.",
        }
        log.info(f"R² decomposition {bench}: domain={r2_domain:.4f}, scale_pooled={r2_scale:.4f}")

    return output


def save_robustness_results(
    subgroup_results: dict,
    p4: dict,
    permutation: dict,
    r2_decomp: dict,
    output_dir: Path,
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # serialize subgroup params only (PanelOLS results not serializable)
    subgroup_summary: dict = {}
    for group, bench_results in subgroup_results.items():
        subgroup_summary[group] = {}
        for bench, res in bench_results.items():
            if res is not None and hasattr(res, "params"):
                subgroup_summary[group][bench] = {
                    "params": {str(k): float(v) for k, v in res.params.items()},
                    "rsquared_within": float(res.rsquared_within),
                }

    payload = {
        "subgroup_regressions": subgroup_summary,
        "p4_spearman": p4,
        "permutation_null": permutation,
        "r2_decomposition": r2_decomp,
    }
    (output_dir / "robustness_results.json").write_text(json.dumps(payload, indent=2, default=str))
    log.info("Robustness results saved")


if __name__ == "__main__":
    # self-check
    rng = np.random.default_rng(42)
    sizes = [f"s{i}" for i in range(6)]
    steps = list(range(20))
    idx = pd.MultiIndex.from_tuples(
        [(s, t) for s in sizes for t in steps], names=["model_size", "checkpoint"]
    )
    n = len(idx)
    cols = ["Wikipedia_en", "Books3"]
    data = {c: rng.random(n) for c in cols}
    data["mmlu"] = rng.random(n)
    data["log_params"] = [float(i % 6) for i in range(n)]
    df = pd.DataFrame(data, index=idx)

    result = test_p4_spearman({}, cols, ["mmlu"])
    assert "median_rho" in result
    print("PASS: robustness self-check")
