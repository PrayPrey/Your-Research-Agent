"""run_experiment.py — full h-m4 experiment orchestration."""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import numpy as np

from .config import (
    DELTA_ECE_THRESHOLD,
    M_PRIMARY,
    M_SENSITIVITY,
    MODEL_IDS,
    MODEL_SHORT_NAMES,
    N_BOOT,
    P1_MIN_PASSING,
    P2_MIN_PASSING,
    RESULTS_FILENAME,
    RESULTS_SCHEMA_VERSION,
    SEED,
    ExperimentConfig,
    FigureConfig,
)
from .data_loader import (
    align_model_data,
    load_confidence_scores,
    load_correctness,
    load_tier_assignments,
    make_holdout_split,
)
from .evaluate import (
    compute_delta_ece_bootstrap,
    compute_m_sensitivity,
    compute_null_baseline,
    compute_tier_ece,
    evaluate_gate,
    verify_mechanism_activated,
)
from .temperature_scaling import compute_post_T_metrics
from .visualize import FigureConfig, save_all_figures


def save_results(results: dict[str, Any], output_dir: str) -> None:
    """Save experiment results to delta_ece_results.json.

    Parameters
    ----------
    results : full results dict
    output_dir : directory to write into
    """
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, RESULTS_FILENAME)

    # Convert numpy types for JSON serialization
    def _convert(obj: Any) -> Any:
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_convert(x) for x in obj]
        return obj

    results_serializable = _convert(results)

    with open(out_path, "w") as f:
        json.dump(results_serializable, f, indent=2)

    print(f"Results saved to: {out_path}")


def run_experiment(cfg: ExperimentConfig) -> dict[str, Any]:
    """Run the full h-m4 difficulty-stratified ECE analysis.

    Parameters
    ----------
    cfg : ExperimentConfig with paths and hyperparameters

    Returns
    -------
    Full results dict including gate decisions, per-model metrics, and figure data.
    """
    print("=" * 60)
    print("h-m4: Difficulty-Stratified ECE Analysis")
    print("=" * 60)

    # --- Step 1: Load data ---
    print("\n[1/6] Loading data...")
    confidence_all = load_confidence_scores(cfg.hm3_results)
    tier_df = load_tier_assignments(cfg.hm2_results)

    # --- Step 2: Per-model alignment and computation ---
    print("\n[2/6] Aligning data and computing ECE metrics...")

    model_results: dict[str, dict[str, Any]] = {}
    model_eval_data: dict[str, dict[str, np.ndarray]] = {}
    bootstrap_samples: dict[str, np.ndarray] = {}
    m_sensitivity_results: dict[str, dict[int, float]] = {}
    post_T_results: dict[str, dict[str, Any]] = {}
    null_results: dict[str, dict[str, Any]] = {}

    for model_id in MODEL_IDS:
        model_short = MODEL_SHORT_NAMES[model_id]
        print(f"\n  Processing: {model_short}")

        # Load correctness for this model
        try:
            correctness = load_correctness(cfg.he1_results, model_short)
        except FileNotFoundError as e:
            print(f"    WARNING: {e}. Skipping model.")
            continue

        # Get confidence for this model
        if model_short not in confidence_all:
            print(f"    WARNING: No confidence scores for {model_short}. Skipping.")
            continue

        confidence = confidence_all[model_short]

        # Align data
        try:
            aligned = align_model_data(confidence, tier_df, correctness, model_short)
        except ValueError as e:
            print(f"    WARNING: {e}. Skipping model.")
            continue

        c_hard = aligned["c_hard"]
        y_hard = aligned["y_hard"]
        c_easy = aligned["c_easy"]
        y_easy = aligned["y_easy"]
        n_hard = aligned["n_hard"]
        n_easy = aligned["n_easy"]

        print(f"    n_hard={n_hard}, n_easy={n_easy}")

        # Holdout split
        eval_data, holdout_data = make_holdout_split(
            c_hard, y_hard, c_easy, y_easy,
            holdout_frac=0.2,
            seed=cfg.seed,
        )

        model_eval_data[model_short] = eval_data

        # Primary ECE metrics on eval split
        tier_ece = compute_tier_ece(
            eval_data["c_hard"], eval_data["y_hard"],
            eval_data["c_easy"], eval_data["y_easy"],
            M=cfg.m_primary,
        )

        # Bootstrap CI — collect samples for fig6
        delta_ece_obs, ci_lower, ci_upper, p_value, boot_deltas = compute_delta_ece_bootstrap(
            eval_data["c_hard"], eval_data["y_hard"],
            eval_data["c_easy"], eval_data["y_easy"],
            n_boot=cfg.n_boot,
            M=cfg.m_primary,
            seed=cfg.seed,
            return_samples=True,
        )

        bootstrap_samples[model_short] = boot_deltas

        # Per-model gate p1: delta >= threshold AND ci_lower > 0
        gate_p1 = (delta_ece_obs >= DELTA_ECE_THRESHOLD) and (ci_lower > 0)

        # Mechanism activation check
        mech_all, mech_indicators = verify_mechanism_activated(
            tier_ece["ece_hard"], tier_ece["ece_easy"],
            delta_ece_obs, n_hard, n_easy, ci_lower, ci_upper,
        )

        model_results[model_short] = {
            "model_short": model_short,
            "model_id": model_id,
            "n_hard": n_hard,
            "n_easy": n_easy,
            "ece_hard": tier_ece["ece_hard"],
            "ece_easy": tier_ece["ece_easy"],
            "delta_ece": delta_ece_obs,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "p_value": p_value,
            "gate_p1": gate_p1,
            "mechanism_activated": mech_all,
            "mechanism_indicators": mech_indicators,
        }

        print(f"    ECE_hard={tier_ece['ece_hard']:.4f}, ECE_easy={tier_ece['ece_easy']:.4f}")
        print(f"    Δ ECE={delta_ece_obs:.4f}, CI=[{ci_lower:.4f}, {ci_upper:.4f}], p={p_value:.4f}")
        print(f"    Gate P1: {'PASS' if gate_p1 else 'FAIL'}")

        # M sensitivity
        m_sens = compute_m_sensitivity(
            eval_data["c_hard"], eval_data["y_hard"],
            eval_data["c_easy"], eval_data["y_easy"],
            m_values=M_SENSITIVITY,
        )
        m_sensitivity_results[model_short] = m_sens

        # Null baseline
        null_res = compute_null_baseline(
            eval_data["c_hard"], eval_data["y_hard"],
            eval_data["c_easy"], eval_data["y_easy"],
            M=cfg.m_primary,
        )
        null_results[model_short] = null_res

        # Temperature scaling
        post_T = compute_post_T_metrics(
            eval_data, holdout_data,
            M=cfg.m_primary,
            n_boot=cfg.n_boot,
            seed=cfg.seed,
        )
        post_T_results[model_short] = post_T
        print(f"    T*={post_T['T_star']:.4f}, Post-T Δ ECE={post_T['post_T_delta_ece']:.4f}")
        print(f"    Gate P3: {'PASS' if post_T['gate_p3'] else 'FAIL'}")

    # --- Step 3: Primary gate (P1) ---
    print("\n[3/6] Evaluating primary gate (P1)...")
    gate_p1_pass, n_passing_p1 = evaluate_gate(
        model_results, threshold=DELTA_ECE_THRESHOLD, min_passing=P1_MIN_PASSING
    )
    print(f"  Gate P1: {n_passing_p1}/{len(model_results)} models pass → {'PASS' if gate_p1_pass else 'FAIL'}")

    # --- Step 4: Secondary gate (P2) bootstrap p-value ---
    print("\n[4/6] Evaluating secondary gate (P2)...")
    n_passing_p2 = sum(
        1 for res in model_results.values()
        if res.get("p_value", 1.0) < 0.05
    )
    gate_p2_pass = n_passing_p2 >= P2_MIN_PASSING
    print(f"  Gate P2: {n_passing_p2}/{len(model_results)} models pass → {'PASS' if gate_p2_pass else 'FAIL'}")

    # --- Step 5: Temperature gate (P3) ---
    print("\n[5/6] Evaluating temperature scaling gate (P3)...")
    n_passing_p3 = sum(1 for res in post_T_results.values() if res.get("gate_p3", False))
    gate_p3_pass = n_passing_p3 >= 2
    print(f"  Gate P3: {n_passing_p3}/{len(post_T_results)} models pass → {'PASS' if gate_p3_pass else 'FAIL'}")

    # Overall hypothesis decision
    hypothesis_supported = gate_p1_pass and gate_p2_pass

    print("\n" + "=" * 60)
    print(f"HYPOTHESIS H-M4: {'SUPPORTED' if hypothesis_supported else 'NOT SUPPORTED'}")
    print(f"  Gate P1 (Δ ECE ≥ 0.03, CI > 0): {'PASS' if gate_p1_pass else 'FAIL'}")
    print(f"  Gate P2 (bootstrap p < 0.05):    {'PASS' if gate_p2_pass else 'FAIL'}")
    print(f"  Gate P3 (post-T still holds):    {'PASS' if gate_p3_pass else 'FAIL'}")
    print("=" * 60)

    # --- Step 6: Figures ---
    print("\n[6/6] Generating figures...")
    fig_cfg = FigureConfig(figures_dir=cfg.figures_dir)

    # Extend model_results with ece values from null for fig4
    save_all_figures(
        model_results=model_results,
        model_eval_data=model_eval_data,
        post_T_results=post_T_results,
        null_results=null_results,
        m_sensitivity_results=m_sensitivity_results,
        bootstrap_samples=bootstrap_samples,
        fig_cfg=fig_cfg,
    )
    print(f"  Figures saved to: {cfg.figures_dir}/")

    # Build final results dict
    results = {
        "schema_version": RESULTS_SCHEMA_VERSION,
        "hypothesis": "h-m4",
        "hypothesis_supported": hypothesis_supported,
        "gate_p1": {"pass": gate_p1_pass, "n_passing": n_passing_p1},
        "gate_p2": {"pass": gate_p2_pass, "n_passing": n_passing_p2},
        "gate_p3": {"pass": gate_p3_pass, "n_passing": n_passing_p3},
        "config": {
            "seed": cfg.seed,
            "n_boot": cfg.n_boot,
            "m_primary": cfg.m_primary,
        },
        "model_results": model_results,
        "post_T_results": post_T_results,
        "null_results": null_results,
        "m_sensitivity_results": {
            model: {str(k): v for k, v in sens.items()}
            for model, sens in m_sensitivity_results.items()
        },
    }

    save_results(results, cfg.output_dir)
    return results


def main() -> None:
    """CLI entry point for h-m4 experiment."""
    parser = argparse.ArgumentParser(
        description="h-m4: Difficulty-Stratified ECE Analysis"
    )
    parser.add_argument(
        "--hm3-results",
        default="../h-m3/results",
        help="Path to h-m3 results directory (default: ../h-m3/results)",
    )
    parser.add_argument(
        "--hm2-results",
        default="../h-m2/results",
        help="Path to h-m2 results directory (default: ../h-m2/results)",
    )
    parser.add_argument(
        "--he1-results",
        default="../h-e1/results",
        help="Path to h-e1 results directory (default: ../h-e1/results)",
    )
    parser.add_argument(
        "--output-dir",
        default="results",
        help="Output directory for results JSON (default: results)",
    )
    parser.add_argument(
        "--figures-dir",
        default="figures",
        help="Output directory for figures (default: figures)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
        help=f"Random seed (default: {SEED})",
    )
    parser.add_argument(
        "--n-boot",
        type=int,
        default=N_BOOT,
        help=f"Number of bootstrap iterations (default: {N_BOOT})",
    )
    parser.add_argument(
        "--m-primary",
        type=int,
        default=M_PRIMARY,
        help=f"Primary number of ECE bins (default: {M_PRIMARY})",
    )

    args = parser.parse_args()

    cfg = ExperimentConfig(
        hm3_results=args.hm3_results,
        hm2_results=args.hm2_results,
        he1_results=args.he1_results,
        output_dir=args.output_dir,
        figures_dir=args.figures_dir,
        seed=args.seed,
        n_boot=args.n_boot,
        m_primary=args.m_primary,
    )

    results = run_experiment(cfg)
    supported = results.get("hypothesis_supported", False)
    sys.exit(0 if supported else 1)


if __name__ == "__main__":
    main()
