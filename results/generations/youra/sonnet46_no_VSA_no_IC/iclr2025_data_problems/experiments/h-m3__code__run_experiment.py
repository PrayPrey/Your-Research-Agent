#!/usr/bin/env python3
"""H-M3 Panel OLS Experiment Orchestrator."""
from __future__ import annotations
import argparse
import json
import logging
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# Ensure src/ on path
sys.path.insert(0, str(Path(__file__).parent))
import config as cfg
from src.data_loader import (
    load_h_e1_trajectories, load_eval_cache,
    build_panel_dataframe, verify_books3_variance,
)
from src.panel_builder import (
    drop_min_variance_domain, apply_pca_if_needed,
    verify_panel_quality, save_vif_diagnostics,
)
from src.panel_regression import (
    fit_benchmark_specific_models, fit_shared_beta_model,
    extract_focal_coefficients, save_panel_results,
)
from src.hypothesis_tests import (
    run_p1_p2_tests as test_p1_p2, run_lrt_all_pairs, apply_fdr_correction,
    evaluate_gate, save_gate_results,
)
from src.robustness import (
    run_subgroup_regressions, test_p4_spearman,
    run_permutation_null, run_r2_decomposition, save_robustness_results,
)
from src.visualization import generate_all_figures
from src.reporter import save_panel_summary, generate_results_markdown

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="H-M3 Panel OLS Experiment")
    p.add_argument("--config", type=str, default=None, help="YAML config override file")
    p.add_argument("--output-dir", type=str, default=None)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--n-permutations", type=int, default=None)
    p.add_argument("--no-resume", action="store_true", help="Ignore existing cache")
    p.add_argument("--skip-eval", action="store_true", help="Use existing cache only")
    p.add_argument("--skip-robustness", action="store_true", help="Skip permutation null (fast run)")
    p.add_argument("--model-sizes", nargs="+", default=None, help="Subset of model sizes")
    p.add_argument("--h-e1-dir", type=str, default=None, help="Path to H-E1 output")
    return p


def load_yaml_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run(args: argparse.Namespace) -> dict:
    # --- Load optional YAML override ---
    override = {}
    if args.config:
        override = load_yaml_config(args.config)

    output_dir = Path(args.output_dir or override.get("output_dir") or cfg.RESULTS_DIR)
    figures_dir = Path(override.get("figures_dir") or cfg.FIGURES_DIR)
    seed = args.seed or override.get("seed") or cfg.SEED
    n_permutations = args.n_permutations or override.get("n_permutations") or cfg.N_PERMUTATIONS
    resume = not args.no_resume
    model_sizes = args.model_sizes or override.get("model_sizes") or cfg.MODEL_SIZES
    benchmarks = override.get("benchmarks") or list(cfg.TASKS.keys())
    h_e1_dir = args.h_e1_dir or cfg.H_E1_EXPOSURE_DIR

    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    log.info(f"H-M3 Experiment: model_sizes={model_sizes}, benchmarks={benchmarks}")
    log.info(f"H-E1 dir: {h_e1_dir}, output: {output_dir}")

    # =========================================================================
    # PHASE 1: Load H-E1 trajectories
    # =========================================================================
    log.info("=== PHASE 1: Loading H-E1 trajectories ===")
    trajectories = load_h_e1_trajectories(
        h_e1_dir, model_sizes, cfg.CHECKPOINT_STEPS, cfg.PILE_DOMAINS
    )
    available_sizes = [s for s, v in trajectories.items() if v is not None]
    log.info(f"Available model sizes with H-E1 data: {available_sizes}")

    if not available_sizes:
        raise RuntimeError("No H-E1 trajectory data available. Run H-E1 first.")

    # =========================================================================
    # PHASE 2: Load or run evaluations
    # =========================================================================
    log.info("=== PHASE 2: Loading eval cache ===")
    eval_cache_dir = Path(cfg.EVAL_CACHE_DIR)
    eval_results = load_eval_cache(
        eval_cache_dir, available_sizes, cfg.CHECKPOINT_STEPS, cfg.TASKS
    )

    # Filter to sizes that have both H-E1 data and eval results
    usable_sizes = [s for s in available_sizes if eval_results.get(s)]
    log.info(f"Usable sizes (H-E1 + eval cache): {usable_sizes}")

    if len(usable_sizes) < 2:
        log.warning(f"Only {len(usable_sizes)} model size(s) with data — panel requires >=2 entities")
        if len(usable_sizes) == 0:
            raise RuntimeError("No usable model sizes. Run evaluations first (--skip-eval skips new evals).")

    # =========================================================================
    # PHASE 3: Build panel DataFrame
    # =========================================================================
    log.info("=== PHASE 3: Building panel DataFrame ===")
    panel_df = build_panel_dataframe(
        trajectories={s: trajectories[s] for s in usable_sizes},
        eval_results=eval_results,
        checkpoint_steps=cfg.CHECKPOINT_STEPS,
        pile_domains=cfg.PILE_DOMAINS,
        tasks=cfg.TASKS,
        model_params=cfg.MODEL_PARAMS,
        floor_threshold=cfg.FLOOR_THRESHOLD,
        min_valid_checkpoints=cfg.MIN_VALID_CHECKPOINTS,
    )
    log.info(f"Panel shape: {panel_df.shape}")

    # =========================================================================
    # PHASE 4: Panel quality verification
    # =========================================================================
    log.info("=== PHASE 4: Panel quality verification ===")
    domain_cols_full = [d for d in cfg.PILE_DOMAINS if d in panel_df.columns]
    panel_quality = verify_panel_quality(panel_df, domain_cols_full)
    books3_var = panel_quality.get("Books3", 0.0)
    log.info(f"Books3 within-variation: {books3_var:.4e}")

    # Drop min-variance domain (break sum-to-1)
    panel_df, dropped_domain, domain_cols = drop_min_variance_domain(panel_df, domain_cols_full)
    log.info(f"Dropped domain: '{dropped_domain}', remaining: {len(domain_cols)} columns")

    # =========================================================================
    # PHASE 5: VIF check and optional PCA
    # =========================================================================
    log.info("=== PHASE 5: VIF diagnostics ===")
    panel_df, regressor_cols, pca_loadings, original_domain_names = apply_pca_if_needed(
        panel_df, domain_cols, cfg.VIF_THRESHOLD, cfg.PCA_VARIANCE_RETAINED
    )
    pca_applied = pca_loadings is not None
    vif_info = {
        "pca_applied": pca_applied,
        "n_pca_components": len(regressor_cols) if pca_applied else None,
        "dropped_domain": dropped_domain,
        "max_vif": None,  # already computed inside apply_pca_if_needed
    }
    save_vif_diagnostics({}, pca_applied, len(regressor_cols) if pca_applied else None, output_dir)

    # =========================================================================
    # PHASE 6: Panel OLS — benchmark-specific models
    # =========================================================================
    log.info("=== PHASE 6: Panel OLS regression ===")
    benchmark_results = fit_benchmark_specific_models(
        panel_df, regressor_cols, benchmarks
    )

    shared_result = fit_shared_beta_model(panel_df, regressor_cols, benchmarks)

    focal_coeffs = extract_focal_coefficients(
        benchmark_results, regressor_cols, cfg.FOCAL_DOMAINS,
        pca_loadings, original_domain_names
    )
    save_panel_results(benchmark_results, shared_result, focal_coeffs, output_dir)

    # =========================================================================
    # PHASE 7: Hypothesis tests (P1, P2, P3)
    # =========================================================================
    log.info("=== PHASE 7: Hypothesis tests ===")
    p1_p2 = test_p1_p2(focal_coeffs)
    lrt_df = run_lrt_all_pairs(benchmark_results, panel_df, regressor_cols, benchmarks, len(regressor_cols))
    fdr = apply_fdr_correction(lrt_df)

    # =========================================================================
    # PHASE 8: Robustness analysis
    # =========================================================================
    p4 = {"passed": None, "median_rho": None}
    permutation = {}
    r2_decomp = {}

    if not args.skip_robustness:
        log.info("=== PHASE 8: Robustness analysis ===")
        subgroup_results = run_subgroup_regressions(panel_df, regressor_cols, benchmarks)
        p4 = test_p4_spearman(subgroup_results, regressor_cols, benchmarks)
        permutation = run_permutation_null(
            panel_df, regressor_cols, cfg.FOCAL_DOMAINS,
            n_permutations=n_permutations, seed=seed
        )
        r2_decomp = run_r2_decomposition(panel_df, regressor_cols, benchmarks)
        save_robustness_results(subgroup_results, p4, permutation, r2_decomp, output_dir)
    else:
        subgroup_results = {}
        log.info("Skipping robustness analysis (--skip-robustness)")

    # =========================================================================
    # PHASE 9: Gate evaluation
    # =========================================================================
    log.info("=== PHASE 9: Gate evaluation ===")
    gate = evaluate_gate(p1_p2, p1_p2, fdr, p4 if p4.get("passed") is not None else None)
    save_gate_results(p1_p2, fdr, gate, output_dir)

    # =========================================================================
    # PHASE 10: Visualization
    # =========================================================================
    log.info("=== PHASE 10: Generating figures ===")
    generate_all_figures(
        focal_coeffs=focal_coeffs,
        benchmark_results=benchmark_results,
        domain_cols=regressor_cols,
        r2_decomp=r2_decomp,
        permutation_results=permutation,
        subgroup_results=subgroup_results,
        focal_domains=cfg.FOCAL_DOMAINS,
        figures_dir=figures_dir,
    )

    # =========================================================================
    # PHASE 11: Reporting
    # =========================================================================
    log.info("=== PHASE 11: Generating reports ===")
    save_panel_summary(focal_coeffs, p1_p2, fdr, gate, p4, r2_decomp, vif_info, output_dir)
    generate_results_markdown(
        gate=gate, p1_p2=p1_p2, fdr=fdr, focal_coeffs=focal_coeffs,
        r2_decomp=r2_decomp, vif_info=vif_info,
        output_path=Path("docs/youra_research/h-m3/04_results_summary.md"),
    )

    # =========================================================================
    # Build experiment_results.json
    # =========================================================================
    results = {
        "status": "completed",
        "gate": gate,
        "p1_p2": p1_p2,
        "fdr": fdr,
        "p4": p4,
        "n_obs": int(panel_df.shape[0]),
        "n_entities": int(panel_df.index.get_level_values("model_size").nunique()),
        "books3_within_var": float(books3_var),
        "pca_applied": pca_applied,
    }
    with open("docs/youra_research/h-m3/experiment_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    log.info(f"=== H-M3 COMPLETE: {gate['status']} -> {gate['route']} ===")
    return results


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    run(args)
    print("EXPERIMENT COMPLETE (exit=0)")
