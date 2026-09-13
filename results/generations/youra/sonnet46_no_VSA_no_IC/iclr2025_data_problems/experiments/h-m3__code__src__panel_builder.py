"""Panel construction: VIF diagnostics, domain column selection."""
from __future__ import annotations
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from statsmodels.stats.outliers_influence import variance_inflation_factor

log = logging.getLogger(__name__)


def drop_min_variance_domain(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
) -> tuple[pd.DataFrame, str, list[str]]:
    """
    Drop the least informative domain (min within-entity variance) to break sum-to-1 constraint.
    Returns (df_with_21_domains, dropped_domain, remaining_cols).
    """
    variances = {}
    for d in domain_cols:
        if d not in panel_df.columns:
            continue
        within = (
            panel_df[d]
            .groupby(level="model_size")
            .transform(lambda x: x - x.mean())
        )
        variances[d] = float(within.var())

    if not variances:
        raise ValueError("No domain columns found in panel_df")

    dropped = min(variances, key=variances.get)
    remaining = [d for d in domain_cols if d != dropped and d in panel_df.columns]
    log.info(f"Dropped domain (min within-var={variances[dropped]:.4e}): '{dropped}'")
    return panel_df, dropped, remaining


def compute_vif(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
) -> dict[str, float]:
    """Compute VIF for each domain column. Returns {domain: vif}."""
    X = panel_df[domain_cols].dropna().values
    if X.shape[0] < X.shape[1] + 1:
        log.warning("Insufficient rows for VIF computation")
        return {d: np.nan for d in domain_cols}

    vif_scores = {}
    for i, col in enumerate(domain_cols):
        try:
            v = variance_inflation_factor(X, i)
            vif_scores[col] = float(v)
        except Exception as e:
            log.warning(f"VIF failed for {col}: {e}")
            vif_scores[col] = np.nan

    max_vif = max((v for v in vif_scores.values() if not np.isnan(v)), default=0.0)
    log.info(f"VIF max: {max_vif:.2f}")
    return vif_scores


def apply_pca_if_needed(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    vif_threshold: float = 10.0,
    pca_variance_retained: float = 0.95,
) -> tuple[pd.DataFrame, list[str], np.ndarray | None, list[str] | None]:
    """
    Check VIF; apply PCA if max VIF > threshold.

    Returns:
        (panel_df_with_regressors, regressor_cols, pca_loadings_or_None, original_domain_names_or_None)
    """
    vif_scores = compute_vif(panel_df, domain_cols)
    max_vif = max((v for v in vif_scores.values() if not np.isnan(v)), default=0.0)

    if max_vif <= vif_threshold:
        log.info(f"VIF check passed (max={max_vif:.2f} <= {vif_threshold}). Using raw domain columns.")
        return panel_df, domain_cols, None, None

    log.warning(f"VIF check FAILED (max={max_vif:.2f} > {vif_threshold}). Applying PCA.")
    X = panel_df[domain_cols].values
    pca = PCA(n_components=pca_variance_retained, svd_solver="full")
    X_pca = pca.fit_transform(X)
    n_comp = X_pca.shape[1]
    pc_cols = [f"PC{i}" for i in range(n_comp)]

    pca_df = pd.DataFrame(X_pca, index=panel_df.index, columns=pc_cols)
    df_out = panel_df.drop(columns=domain_cols).join(pca_df)
    log.info(f"PCA applied: {n_comp} components retained ({pca.explained_variance_ratio_.sum()*100:.1f}% variance)")
    log.warning("P1/P2 will be interpreted via PCA loadings, not raw domain coefficients")

    return df_out, pc_cols, pca.components_, domain_cols


def verify_panel_quality(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    books3_col: str = "Books3",
    threshold: float = 1e-6,
) -> dict[str, float]:
    """
    Verify within-entity variation for all domain columns.
    Raises if Books3 within-variance is insufficient.
    """
    stats: dict[str, float] = {}
    for domain in domain_cols:
        if domain not in panel_df.columns:
            stats[domain] = 0.0
            continue
        within = (
            panel_df[domain]
            .groupby(level="model_size")
            .transform(lambda x: x - x.mean())
        )
        stats[domain] = float(within.var())

    low_var = [d for d, v in stats.items() if v < threshold]
    if low_var:
        log.warning(f"Low within-variation domains: {low_var}")

    books3_var = stats.get(books3_col, 0.0)
    if books3_var < threshold:
        raise ValueError(
            f"Books3 within-variation {books3_var:.2e} < {threshold} — "
            "H-M2 root cause: load full H-E1 output (not 600k-doc subsample)"
        )
    log.info(f"Panel quality check passed. Books3 within-var: {books3_var:.4e}")
    return stats


def save_vif_diagnostics(
    vif_scores: dict[str, float],
    pca_applied: bool,
    n_pca_components: int | None,
    output_dir: Path,
) -> None:
    payload = {
        "vif_scores": vif_scores,
        "max_vif": max((v for v in vif_scores.values() if not np.isnan(v)), default=0.0),
        "pca_applied": pca_applied,
        "n_pca_components": n_pca_components,
    }
    (output_dir / "vif_diagnostics.json").write_text(json.dumps(payload, indent=2))
    log.info(f"VIF diagnostics saved: pca_applied={pca_applied}")


if __name__ == "__main__":
    # self-check with synthetic data
    rng = np.random.default_rng(42)
    n = 60
    sizes = ["70m"] * 20 + ["1b"] * 20 + ["6.9b"] * 20
    steps = list(range(20)) * 3
    idx = pd.MultiIndex.from_arrays([sizes, steps], names=["model_size", "checkpoint"])
    domains = ["Wikipedia (en)", "Books3", "Github"]
    data = {d: rng.random(n) for d in domains}
    data["mmlu"] = rng.random(n)
    df = pd.DataFrame(data, index=idx)

    _, dropped, remaining = drop_min_variance_domain(df, domains)
    assert len(remaining) == 2, "Should drop 1 domain"
    stats = verify_panel_quality(df, remaining)
    assert "Books3" in stats or "Wikipedia (en)" in stats
    print("PASS: panel_builder self-check")
