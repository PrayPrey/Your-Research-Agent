"""
Main orchestration for H-E1: Partial Spearman Correlation Structure.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone

import numpy as np

from data_loader import DIMENSIONS, load_trustllm_scores, add_annotations, validate
from analysis import (
    AnalysisConfig,
    raw_spearman_matrix,
    ols_residualize,
    partial_spearman_matrix,
    partial_pearson_matrix,
    check_sign_divergence,
)
from clustering import (
    build_distance_matrix,
    run_clustering,
    build_mst,
    get_dendrogram_linkage,
)
from visualization import (
    plot_partial_corr_bar,
    plot_heatmap_comparison,
    plot_dendrogram,
    plot_scatter_confound,
)


def check_gate(significant_pairs: list) -> bool:
    return len(significant_pairs) >= 1


def serialize_results(results: dict, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True) if os.path.dirname(out_path) else None
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)


def run_experiment(trustllm_results_dir: str, output_dir: str) -> dict:
    cfg = AnalysisConfig()
    log_path = os.path.join(output_dir, "experiment.log")
    figures_dir = os.path.join(output_dir, "figures")
    os.makedirs(figures_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    log = logging.getLogger("h-e1")

    # ── 1. Load data ──────────────────────────────────────────────────
    log.info("Loading TrustLLM published scores...")
    scores_df = load_trustllm_scores(trustllm_results_dir)
    annotated_df = add_annotations(scores_df)

    log.info(f"Loaded {len(scores_df)} models × {len(DIMENSIONS)} dimensions")
    assert scores_df.shape == (16, 6), f"Unexpected shape: {scores_df.shape}"

    validation_report = validate(annotated_df)
    log.info(f"Validation: {validation_report}")

    covariates_df = annotated_df[["log10_params", "is_RLHF"]]

    # ── 2. Raw Spearman baseline ──────────────────────────────────────
    log.info("Computing raw Spearman matrix...")
    rho_raw, pval_raw = raw_spearman_matrix(scores_df)

    # ── 3. OLS residualization ────────────────────────────────────────
    log.info("Residualizing scores on [log10_params, is_RLHF]...")
    residuals_df = ols_residualize(scores_df, covariates_df)

    # ── 4. Partial Spearman ───────────────────────────────────────────
    log.info("Computing partial Spearman matrix (df=12)...")
    rho_partial, pval_partial, significant_pairs = partial_spearman_matrix(
        scores_df, covariates_df, alpha_bonferroni=cfg.bonferroni_alpha
    )

    log.info(f"Significant pairs (|ρ|>0.5, p<0.0033): {len(significant_pairs)}")
    for sp in significant_pairs:
        log.info(f"  {sp[0]} — {sp[1]}: ρ={sp[2]:.4f}, p={sp[3]:.4e}")

    # ── 5. Gate check ─────────────────────────────────────────────────
    gate_pass = check_gate(significant_pairs)
    gate_str = "PASS" if gate_pass else "FAIL"
    log.info(f"GATE: {gate_str} (MUST_WORK: ≥1 significant partial correlation)")

    # ── 6. Sensitivity check ─────────────────────────────────────────
    rho_pearson = partial_pearson_matrix(scores_df, covariates_df)
    sign_divergent = check_sign_divergence(rho_partial, rho_pearson)
    if sign_divergent:
        log.warning(f"Sign divergence Spearman vs Pearson at pairs: {sign_divergent}")

    # ── 7. Clustering ─────────────────────────────────────────────────
    log.info("Running hierarchical clustering (k=2, average linkage)...")
    dist_matrix = build_distance_matrix(rho_partial)
    cluster_labels, silhouette = run_clustering(dist_matrix, n_clusters=2)
    log.info(f"Silhouette score: {silhouette:.4f} (threshold: {cfg.silhouette_threshold})")

    # MST for H-E2 prerequisite
    mst = build_mst(rho_partial, DIMENSIONS)
    mst_edges = [(u, v, float(d["weight"])) for u, v, d in mst.edges(data=True)]

    # Dendrogram linkage
    linkage_matrix = get_dendrogram_linkage(dist_matrix)

    # ── 8. Visualizations ─────────────────────────────────────────────
    log.info("Generating figures...")

    plot_partial_corr_bar(
        rho_partial, pval_partial, DIMENSIONS,
        alpha=cfg.bonferroni_alpha,
        out_path=os.path.join(figures_dir, "01_bar.png"),
    )
    plot_heatmap_comparison(
        rho_raw, rho_partial, DIMENSIONS,
        out_path=os.path.join(figures_dir, "02_heatmaps.png"),
    )
    plot_dendrogram(
        linkage_matrix, DIMENSIONS,
        out_path=os.path.join(figures_dir, "03_dendrogram.png"),
    )

    # Pick top pair (highest |rho_partial|) for scatter, fallback to first pair
    upper = [(i, j) for i in range(6) for j in range(i + 1, 6)]
    top_pair_idx = max(upper, key=lambda ij: abs(rho_partial[ij[0], ij[1]]))
    top_pair = (DIMENSIONS[top_pair_idx[0]], DIMENSIONS[top_pair_idx[1]])
    plot_scatter_confound(
        annotated_df, residuals_df.copy().join(annotated_df[["is_RLHF"]]),
        dim_pair=top_pair,
        out_path=os.path.join(figures_dir, "04_scatter.png"),
    )

    log.info("Figures saved to " + figures_dir)

    # ── 9. Compile results ────────────────────────────────────────────
    results = {
        "hypothesis_id": "h-e1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_models": len(scores_df),
        "n_dimensions": len(DIMENSIONS),
        "gate_passed": gate_pass,
        "gate_type": "MUST_WORK",
        "significant_pairs": [
            {"dim_i": s[0], "dim_j": s[1], "rho": s[2], "pval": s[3]}
            for s in significant_pairs
        ],
        "n_significant_pairs": len(significant_pairs),
        "rho_partial": rho_partial.tolist(),
        "pval_partial": pval_partial.tolist(),
        "rho_raw": rho_raw.tolist(),
        "pval_raw": pval_raw.tolist(),
        "silhouette": silhouette,
        "silhouette_threshold": cfg.silhouette_threshold,
        "silhouette_pass": silhouette > cfg.silhouette_threshold,
        "cluster_labels": cluster_labels.tolist(),
        "dimensions": DIMENSIONS,
        "mst_edges": mst_edges,
        "sign_divergent_pairs": sign_divergent,
        "validation_report": validation_report,
        "df_residual": cfg.df_residual,
        "bonferroni_alpha": cfg.bonferroni_alpha,
        "rho_threshold": cfg.rho_threshold,
    }

    # ── 10. Write outputs ─────────────────────────────────────────────
    results_json_path = os.path.join(output_dir, "experiment_results_phase3.json")
    serialize_results(results, results_json_path)
    log.info(f"Results saved: {results_json_path}")

    # Append to experiment.log
    with open(log_path, "a") as f:
        f.write(f"\n[{datetime.now(timezone.utc).isoformat()}] GATE {gate_str}: "
                f"n_significant={len(significant_pairs)}, "
                f"silhouette={silhouette:.4f}\n")

    print(f"\n{'='*60}")
    print(f"H-E1 GATE RESULT: {gate_str}")
    print(f"  Significant pairs: {len(significant_pairs)} (need ≥1)")
    print(f"  Silhouette: {silhouette:.4f} (threshold: {cfg.silhouette_threshold})")
    print(f"{'='*60}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-E1 Partial Spearman Analysis")
    parser.add_argument("--results-dir", default="TrustLLM/results",
                        help="TrustLLM results directory containing per-model JSON score files")
    parser.add_argument("--output-dir", default=".",
                        help="Output directory for results and figures")
    args = parser.parse_args()

    results = run_experiment(args.results_dir, args.output_dir)
    sys.exit(0 if results["gate_passed"] else 1)
