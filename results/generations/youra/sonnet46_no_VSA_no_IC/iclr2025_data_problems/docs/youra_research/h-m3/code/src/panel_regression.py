"""Panel OLS regression: benchmark-specific models and shared-beta null model."""
from __future__ import annotations
import json
import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS

log = logging.getLogger(__name__)


def fit_benchmark_specific_models(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    benchmarks: list[str],
    cov_type: str = "clustered",
    cluster_entity: bool = True,
) -> dict:
    """
    Fit 4 separate PanelOLS regressions (one per benchmark) with EntityEffects.

    Note: N=16 clusters is borderline for clustered inference (rule of thumb >=30).
    Document this limitation.
    """
    results = {}

    # Rename domain cols to formula-safe names (formulaic doesn't support backtick quoting)
    safe_map = {
        d: d.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
        for d in domain_cols
    }
    safe_df = panel_df.copy()
    for orig, safe in safe_map.items():
        if orig != safe:
            safe_df[safe] = safe_df[orig]
    safe_domain_cols = [safe_map[d] for d in domain_cols]
    reverse_map = {v: k for k, v in safe_map.items()}

    domain_terms = " + ".join(safe_domain_cols)

    for benchmark in benchmarks:
        if benchmark not in panel_df.columns:
            raise ValueError(f"Benchmark '{benchmark}' not in panel_df columns")

        n_entities = panel_df.index.get_level_values("model_size").nunique()
        actual_cov = cov_type if n_entities >= 10 else "robust"
        actual_cluster = cluster_entity if actual_cov == "clustered" else False
        if actual_cov != cov_type:
            log.warning(f"N={n_entities} entities < 10; switching to robust SEs for {benchmark}")

        formula = f"{benchmark} ~ {domain_terms} + EntityEffects"
        try:
            mod = PanelOLS.from_formula(formula, safe_df, check_rank=False)
            res = mod.fit(cov_type=actual_cov, cluster_entity=actual_cluster, drop_absorbed=True)
        except Exception as panel_err:
            # ponytail: EntityEffects absorbs everything when N*T < n_regressors;
            # fall back to PooledOLS so pipeline runs on small panels (validated gate = UNDERPOWERED)
            from linearmodels.panel import PooledOLS
            log.warning(
                f"PanelOLS failed for {benchmark} (N={n_entities}): {type(panel_err).__name__}. "
                "Falling back to PooledOLS."
            )
            pool_formula = f"{benchmark} ~ {domain_terms}"
            try:
                mod = PooledOLS.from_formula(pool_formula, safe_df, check_rank=False)
                res = mod.fit(cov_type=actual_cov, cluster_entity=actual_cluster)
            except Exception as e2:
                log.error(f"PooledOLS also failed for {benchmark}: {e2}")
                raise

        # sanity: at least one domain |β| > 1 SE
        if not (res.params.abs() > res.std_errors).any():
            warnings.warn(f"No domain coefficient exceeds its SE for {benchmark}")

        # critical: Wikipedia and Books3 SEs must be finite
        focal_check_safe = [safe_map.get(d, d) for d in ["Wikipedia (en)", "Books3"] if d in safe_map or d in safe_domain_cols]
        for focal_safe in focal_check_safe:
            focal = reverse_map.get(focal_safe, focal_safe)
            focal_key = next((k for k in res.params.index if focal_safe in k), None)
            if focal_key and np.isnan(res.std_errors[focal_key]):
                raise ValueError(f"Clustered SE is NaN for {focal} in {benchmark}")

        results[benchmark] = res
        try:
            n_ent = res.entity_info.total
            n_time = res.time_info.total
        except Exception:
            n_ent = n_entities
            n_time = len(panel_df) // n_entities
        log.info(
            f"PanelOLS {benchmark}: N={n_ent}, T≈{n_time}, "
            f"R²_within={res.rsquared_within:.4f}"
        )

    return results


def fit_shared_beta_model(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    benchmarks: list[str],
) -> object:
    """
    Fit shared-β null model via stacked OLS with benchmark + model-size dummies.
    Returns statsmodels OLSResults with .llf for LRT.
    """
    frames = []
    for bench in benchmarks:
        sub = panel_df[domain_cols + [bench, "log_params"]].copy()
        sub = sub.rename(columns={bench: "score"})
        sub["benchmark"] = bench
        sub["model_size"] = sub.index.get_level_values("model_size")
        frames.append(sub.reset_index(drop=True))

    stacked = pd.concat(frames, ignore_index=True)

    # rename domain cols to be formula-safe
    safe_map = {d: d.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
                for d in domain_cols}
    for orig, safe in safe_map.items():
        stacked[safe] = stacked[orig]
    safe_domain_cols = list(safe_map.values())

    bench_dummies = pd.get_dummies(stacked["benchmark"], drop_first=True, prefix="bench")
    size_dummies = pd.get_dummies(stacked["model_size"], drop_first=True, prefix="size")

    X = pd.concat([stacked[safe_domain_cols], bench_dummies, size_dummies], axis=1)
    X = sm.add_constant(X)
    y = stacked["score"]

    result = sm.OLS(y.astype(float), X.astype(float)).fit()
    log.info(f"Shared-β model: N={int(result.nobs)}, llf={result.llf:.4f}")
    return result


def _fit_pair_shared_ols(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    b1: str,
    b2: str,
) -> float:
    """Fit pair-specific shared-β OLS and return log-likelihood."""
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


def _get_loglik(res) -> float:
    """Extract log-likelihood from PanelOLS result via OLS approximation."""
    if hasattr(res, "loglik"):
        try:
            return float(res.loglik)
        except Exception:
            pass
    # Fallback: compute from residuals (PanelOLS doesn't always expose loglik)
    n = res.nobs
    rss = float((res.resids ** 2).sum())
    return -n / 2 * (1 + np.log(2 * np.pi * rss / n))


def extract_focal_coefficients(
    results: dict,
    domain_cols: list[str],
    focal_domains: dict[str, str],
    pca_loadings: np.ndarray | None = None,
    original_domain_names: list[str] | None = None,
) -> dict[str, dict[str, dict]]:
    """Extract β and SE for focal domains (Wikipedia, Books3) per benchmark."""
    def _to_safe(name: str) -> str:
        return name.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")

    output: dict[str, dict[str, dict]] = {}
    for bench, res in results.items():
        output[bench] = {}
        for key, domain_name in focal_domains.items():
            safe_name = _to_safe(domain_name)
            param_key = next(
                (k for k in res.params.index if safe_name == k or domain_name in k),
                None
            )
            if param_key is not None:
                output[bench][domain_name] = {
                    "beta": float(res.params[param_key]),
                    "se": float(res.std_errors[param_key]),
                    "pca_approx": False,
                }
            elif pca_loadings is not None and original_domain_names is not None:
                try:
                    domain_idx = original_domain_names.index(domain_name)
                    pc_idx = int(np.argmax(np.abs(pca_loadings[:, domain_idx])))
                    pc_col = f"PC{pc_idx}"
                    output[bench][domain_name] = {
                        "beta": float(res.params[pc_col]),
                        "se": float(res.std_errors[pc_col]),
                        "pca_approx": True,
                        "dominant_pc": pc_col,
                        "loading": float(pca_loadings[pc_idx, domain_idx]),
                    }
                except Exception:
                    output[bench][domain_name] = {"beta": np.nan, "se": np.nan, "pca_approx": False}
            else:
                output[bench][domain_name] = {"beta": np.nan, "se": np.nan, "pca_approx": False}

    return output


def save_panel_results(
    results: dict,
    shared_result,
    focal_coeffs: dict,
    output_dir: Path,
) -> None:
    """Serialize panel regression results to JSON."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for bench, res in results.items():
        payload = {
            "benchmark": bench,
            "n_obs": int(res.nobs),
            "rsquared_within": float(res.rsquared_within),
            "rsquared_between": float(res.rsquared_between),
            "loglik": _get_loglik(res),
            "params": {str(k): float(v) for k, v in res.params.items()},
            "std_errors": {str(k): float(v) for k, v in res.std_errors.items()},
            "pvalues": {str(k): float(v) for k, v in res.pvalues.items()},
        }
        (output_dir / f"panel_results_{bench}.json").write_text(json.dumps(payload, indent=2))

    shared_payload = {
        "loglik": float(shared_result.llf),
        "nobs": int(shared_result.nobs),
        "df_resid": float(shared_result.df_resid),
    }
    (output_dir / "panel_results_shared_beta.json").write_text(json.dumps(shared_payload, indent=2))
    (output_dir / "focal_coefficients.json").write_text(json.dumps(focal_coeffs, indent=2))
    log.info(f"Panel results saved to {output_dir}")


if __name__ == "__main__":
    # self-check with synthetic panel data
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    rng = np.random.default_rng(42)
    sizes = [f"model_{i}" for i in range(5)]
    steps = list(range(30))
    idx = pd.MultiIndex.from_tuples(
        [(s, t) for s in sizes for t in steps],
        names=["model_size", "checkpoint"]
    )
    n = len(idx)
    domain_cols = ["Wikipedia_en", "Books3", "Github"]
    data = {d: rng.random(n) for d in domain_cols}
    for bench in ["mmlu", "hellaswag"]:
        data[bench] = rng.random(n)
    data["log_params"] = [float(i % 5) for i in range(n)]
    df = pd.DataFrame(data, index=idx)

    results = fit_benchmark_specific_models(df, domain_cols, ["mmlu", "hellaswag"])
    assert "mmlu" in results and "hellaswag" in results
    print("PASS: panel_regression self-check")
