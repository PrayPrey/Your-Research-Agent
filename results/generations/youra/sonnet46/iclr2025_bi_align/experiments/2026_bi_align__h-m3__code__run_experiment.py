"""
run_experiment.py - h-m3 Within-Prompt Quality Probe orchestrator.

H-M3: Within-prompt Delta = cos(H_next, A_chosen) - cos(H_next, A_rejected) > 0
under >= 2/3 operationalizations (raw, length_matched, prompt_projected).
Gate: SHOULD_WORK - ops_passing >= 2 AND n_pairs_min >= 1000.
"""
import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np

# CRITICAL: Set thread limits before loading numpy-dependent libraries
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")

# Local module imports (statistics renamed to statistics_m3 to avoid shadowing stdlib)
from config import load_config, ExperimentConfig
from data_loader import split_chosen_rejected_by_tier, TIER_ORDER
from embedder import Embedder
from delta_probe import compute_all_deltas, OPERATIONALIZATIONS
from statistics_m3 import (
    bootstrap_delta_ci,
    ttest_delta,
    cohens_d_onesample,
    gate_evaluation_m3,
    check_model_consistency_m3,
    verify_mechanism_activated_m3,
)
from visualize import (
    plot_delta_distributions,
    plot_bootstrap_ci_by_op_and_model,
    plot_n_pairs_bar,
    plot_delta_by_tier,
    plot_delta_raw_vs_length_scatter,
    plot_model_op_heatmap,
)


def setup_logging(log_file: Optional[str] = None) -> None:
    """Configure logging to both console and file."""
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True)
        handlers.append(logging.FileHandler(log_file, mode="w"))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        --config  Path to config.yaml (default: None → use dataclass defaults)
        --dry-run Override config.dry_run=True (runs on n_samples_dry_run samples)
        --model   Run single model only (default: all 3 models from config)
    """
    parser = argparse.ArgumentParser(description="h-m3 Within-Prompt Quality Probe experiment")
    parser.add_argument("--config", type=str, default=None, help="Path to config.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Run on small subset for sanity check")
    parser.add_argument("--model", type=str, default=None,
                        help="Run single model (e.g., all-MiniLM-L6-v2)")
    return parser.parse_args()


def run_single_model(
    model_name: str,
    tier_cr_pairs: Dict,
    config: ExperimentConfig,
) -> Dict:
    """Full pipeline for one SBERT model.

    Args:
        model_name: Model name (e.g., 'all-MiniLM-L6-v2').
        tier_cr_pairs: {tier: {h_next, a_chosen, a_rejected, h_prompt, ..., n_pairs}}
        config: ExperimentConfig instance.

    Returns:
        {tier_results, op_stats, gate_result, gate_dict}
    """
    logger = logging.getLogger(__name__)
    logger.info(f"[h-m3] Running model: {model_name}")

    embedder = Embedder(model_name, cache_dir=config.cache.embeddings_dir)

    tier_results = {}
    all_op_stats = {}
    all_delta_arrays = {op: [] for op in OPERATIONALIZATIONS}

    for tier in TIER_ORDER:
        if tier not in tier_cr_pairs:
            logger.warning(f"Tier {tier} not found in tier_cr_pairs, skipping")
            continue

        pairs = tier_cr_pairs[tier]
        n_pairs = pairs["n_pairs"]

        # Apply dry-run subsampling
        if config.dry_run and n_pairs > config.n_samples_dry_run:
            logger.info(f"Dry-run: subsampling {config.n_samples_dry_run} from {n_pairs} pairs")
            idx = np.random.default_rng(42).choice(n_pairs, size=config.n_samples_dry_run, replace=False)
            pairs_subset = {
                k: [v[i] for i in idx] if isinstance(v, list) else v
                for k, v in pairs.items()
                if k != "n_pairs"
            }
            pairs_subset["n_pairs"] = config.n_samples_dry_run
            pairs = pairs_subset
            n_pairs = config.n_samples_dry_run

        # Compute all 3 delta operationalizations
        deltas = compute_all_deltas(pairs, embedder, tier)

        # Per-op statistics
        op_stats = {}
        for op, delta_arr in deltas.items():
            mean_d, ci_lo, ci_hi = bootstrap_delta_ci(
                delta_arr, config.stats.n_bootstrap, config.stats.seed
            )
            ttest = ttest_delta(delta_arr)
            d_eff = cohens_d_onesample(delta_arr)
            op_stats[op] = {
                "mean_delta": mean_d,
                "ci_lower": ci_lo,
                "ci_upper": ci_hi,
                "ttest": ttest,
                "cohen_d": d_eff,
                "n_pairs": int(n_pairs),
            }
            all_delta_arrays[op].append(delta_arr)

        # Per-tier gate evaluation
        gate = gate_evaluation_m3(op_stats, config.stats.min_n_pairs)

        tier_results[tier] = {
            "delta_arrays": {op: deltas[op].tolist() for op in OPERATIONALIZATIONS if op in deltas},
            "op_stats": op_stats,
            "gate": gate,
            "n_pairs": int(n_pairs),
        }
        all_op_stats[tier] = op_stats

        logger.info(
            f"[h-m3] {model_name} | Tier {tier}: "
            f"ops_passing={gate['ops_passing']}/3, gate={gate['gate_result']}, "
            f"n_pairs={n_pairs}"
        )

    # Aggregate op_stats across all tiers (use last tier for simplicity, or aggregate)
    # Use the last evaluated tier's op_stats for top-level gate
    final_op_stats = {}
    if all_op_stats:
        # Average stats across tiers for overall model assessment
        for op in OPERATIONALIZATIONS:
            mean_deltas = [
                all_op_stats[tier][op]["mean_delta"]
                for tier in all_op_stats if op in all_op_stats[tier]
            ]
            ci_lowers = [
                all_op_stats[tier][op]["ci_lower"]
                for tier in all_op_stats if op in all_op_stats[tier]
            ]
            ci_uppers = [
                all_op_stats[tier][op]["ci_upper"]
                for tier in all_op_stats if op in all_op_stats[tier]
            ]
            n_pairs_list = [
                all_op_stats[tier][op]["n_pairs"]
                for tier in all_op_stats if op in all_op_stats[tier]
            ]
            final_op_stats[op] = {
                "mean_delta": float(np.mean(mean_deltas)) if mean_deltas else 0.0,
                "ci_lower": float(np.mean(ci_lowers)) if ci_lowers else 0.0,
                "ci_upper": float(np.mean(ci_uppers)) if ci_uppers else 0.0,
                "n_pairs": int(np.min(n_pairs_list)) if n_pairs_list else 0,
            }

    final_gate = gate_evaluation_m3(final_op_stats, config.stats.min_n_pairs)

    return {
        "tier_results": tier_results,
        "op_results": final_op_stats,
        "gate": final_gate,
        "gate_result": final_gate["gate_result"],
    }


def main() -> None:
    """3-model orchestrator: load → parse pairs → 3-model loop → gate → figures → save."""
    args = parse_args()

    # Load config
    config = load_config(args.config)
    if args.dry_run:
        config.dry_run = True

    # Set up output directories
    results_dir = config.output_dir
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(config.figures.figures_dir, exist_ok=True)

    # Set up logging
    log_file = os.path.join(results_dir, "experiment.log")
    setup_logging(log_file)
    logger = logging.getLogger(__name__)
    log_buffer = []

    class BufferingHandler(logging.Handler):
        def emit(self, record):
            log_buffer.append(self.format(record))

    buf_handler = BufferingHandler()
    buf_handler.setFormatter(logging.Formatter("%(message)s"))
    logging.getLogger().addHandler(buf_handler)

    logger.info(f"[h-m3] Starting experiment. hypothesis_id={config.hypothesis_id}")
    logger.info(f"[h-m3] Config: dry_run={config.dry_run}, n_samples_dry_run={config.n_samples_dry_run}")
    logger.info(f"[h-m3] Output dir: {results_dir}")
    logger.info(f"[h-m3] Embeddings cache: {config.cache.embeddings_dir}")

    # Load chosen/rejected pairs by tier
    logger.info("[h-m3] Loading chosen/rejected pairs from HH-RLHF...")
    tier_cr_pairs = split_chosen_rejected_by_tier(config.cache.cache_dir)

    # Log N_pairs per tier
    tier_n_pairs = {tier: pairs["n_pairs"] for tier, pairs in tier_cr_pairs.items()}
    for tier, n in tier_n_pairs.items():
        logger.info(f"[h-m3] Tier {tier}: {n} pairs")

    # Check auto-demote condition
    min_n = min(tier_n_pairs.values()) if tier_n_pairs else 0
    if min_n < config.stats.min_n_pairs:
        logger.warning(
            f"[h-m3] AUTO-DEMOTE: min N_pairs={min_n} < threshold={config.stats.min_n_pairs}. "
            f"Gate will auto-fail for tiers below threshold."
        )

    # Determine models to run
    models = [args.model] if args.model else config.cache.models
    logger.info(f"[h-m3] Running {len(models)} models: {models}")

    # 3-model loop
    all_model_results = {}
    for model_name in models:
        try:
            result = run_single_model(model_name, tier_cr_pairs, config)
            # Use model slug for key
            model_slug = (
                model_name.replace("all-MiniLM-L6-v2", "minilm")
                          .replace("paraphrase-MiniLM-L6-v2", "paraphrase")
                          .replace("all-mpnet-base-v2", "mpnet")
            )
            all_model_results[model_slug] = result
            logger.info(
                f"[h-m3] Model {model_slug} gate: {result['gate_result']}, "
                f"ops_passing={result['gate']['ops_passing']}"
            )
        except Exception as e:
            logger.error(f"[h-m3] Model {model_name} failed: {e}", exc_info=True)

    if not all_model_results:
        logger.error("[h-m3] No models completed successfully. Exiting.")
        sys.exit(1)

    # Cross-model consistency check
    experiment_log_str = "\n".join(log_buffer)
    consistency = check_model_consistency_m3(all_model_results)
    logger.info(
        f"[h-m3] Model consistency: {consistency['models_consistent']}/3 consistent, "
        f"gate_passed={consistency['gate_passed']}"
    )

    # Mechanism verification
    activated, indicators = verify_mechanism_activated_m3(all_model_results, experiment_log_str)
    logger.info(f"[h-m3] Mechanism activated: {activated}")
    for ind_name, ind_val in indicators.items():
        logger.info(f"  {ind_name}: {ind_val}")

    # Overall gate result
    all_gates_passed = [
        r["gate"]["gate_passed"] for r in all_model_results.values()
    ]
    n_models_gate_passed = sum(all_gates_passed)
    overall_gate = "PASS" if n_models_gate_passed >= 2 else "FAIL"
    logger.info(f"[h-m3] FINAL GATE: {overall_gate} ({n_models_gate_passed}/{len(all_model_results)} models pass)")

    # ──────────────────────────────────────────────────────────────────────────
    # Generate 6 figures
    # ──────────────────────────────────────────────────────────────────────────
    figures_dir = config.figures.figures_dir
    os.makedirs(figures_dir, exist_ok=True)

    try:
        # Use first model's data for distributions
        first_model = next(iter(all_model_results))
        first_result = all_model_results[first_model]

        # Collect delta arrays from first tier of first model for violin
        first_tier_deltas = {}
        for tier in TIER_ORDER:
            if tier in first_result.get("tier_results", {}):
                tier_data = first_result["tier_results"][tier]
                for op in OPERATIONALIZATIONS:
                    if op not in first_tier_deltas:
                        first_tier_deltas[op] = np.array(tier_data["delta_arrays"].get(op, []))
                    else:
                        first_tier_deltas[op] = np.concatenate([
                            first_tier_deltas[op],
                            np.array(tier_data["delta_arrays"].get(op, []))
                        ])

        # Fig 1: Delta distributions (violin)
        fig1_path = os.path.join(figures_dir, "fig1_delta_distributions.png")
        plot_delta_distributions(first_tier_deltas, fig1_path)
        logger.info(f"[h-m3] Fig 1 saved: {fig1_path}")

        # Fig 2: Bootstrap CI by op and model
        all_model_op_stats = {
            model: result.get("op_results", {})
            for model, result in all_model_results.items()
        }
        fig2_path = os.path.join(figures_dir, "fig2_bootstrap_ci_by_op_model.png")
        plot_bootstrap_ci_by_op_and_model(all_model_op_stats, fig2_path)
        logger.info(f"[h-m3] Fig 2 saved: {fig2_path}")

        # Fig 3: N_pairs bar
        fig3_path = os.path.join(figures_dir, "fig3_n_pairs_bar.png")
        plot_n_pairs_bar(tier_n_pairs, config.stats.min_n_pairs, fig3_path)
        logger.info(f"[h-m3] Fig 3 saved: {fig3_path}")

        # Fig 4: Delta by tier
        delta_by_tier_op = {}
        for tier in TIER_ORDER:
            if tier in first_result.get("tier_results", {}):
                delta_by_tier_op[tier] = {
                    op: np.array(first_result["tier_results"][tier]["delta_arrays"].get(op, []))
                    for op in OPERATIONALIZATIONS
                }
        fig4_path = os.path.join(figures_dir, "fig4_delta_by_tier.png")
        plot_delta_by_tier(delta_by_tier_op, TIER_ORDER, fig4_path)
        logger.info(f"[h-m3] Fig 4 saved: {fig4_path}")

        # Fig 5: Raw vs length scatter
        if len(first_tier_deltas.get("raw", [])) > 0 and len(first_tier_deltas.get("length_matched", [])) > 0:
            fig5_path = os.path.join(figures_dir, "fig5_raw_vs_length_scatter.png")
            plot_delta_raw_vs_length_scatter(
                first_tier_deltas["raw"], first_tier_deltas["length_matched"], fig5_path
            )
            logger.info(f"[h-m3] Fig 5 saved: {fig5_path}")

        # Fig 6: Model x op heatmap
        summary_matrix = {
            model: {op: result.get("op_results", {}).get(op, {}).get("mean_delta", 0.0)
                    for op in OPERATIONALIZATIONS}
            for model, result in all_model_results.items()
        }
        fig6_path = os.path.join(figures_dir, "fig6_model_op_heatmap.png")
        plot_model_op_heatmap(summary_matrix, list(all_model_results.keys()), fig6_path)
        logger.info(f"[h-m3] Fig 6 saved: {fig6_path}")

    except Exception as e:
        logger.warning(f"[h-m3] Figure generation failed (non-fatal): {e}", exc_info=True)

    # ──────────────────────────────────────────────────────────────────────────
    # Save delta_results.json
    # ──────────────────────────────────────────────────────────────────────────
    os.makedirs(results_dir, exist_ok=True)
    results_path = os.path.join(results_dir, "delta_results.json")

    # Prepare JSON-serializable results (strip ndarray delta_arrays)
    json_results = {}
    for model_slug, result in all_model_results.items():
        json_results[model_slug] = {
            "gate_result": result["gate_result"],
            "gate": result["gate"],
            "op_results": result["op_results"],
            "tier_results": {
                tier: {
                    "op_stats": tr_data["op_stats"],
                    "gate": tr_data["gate"],
                    "n_pairs": tr_data["n_pairs"],
                    # delta_arrays omitted (too large for JSON)
                }
                for tier, tr_data in result.get("tier_results", {}).items()
            },
        }

    output = {
        "hypothesis_id": config.hypothesis_id,
        "timestamp": datetime.now().isoformat(),
        "dry_run": config.dry_run,
        "overall_gate": overall_gate,
        "n_models_gate_passed": n_models_gate_passed,
        "model_results": json_results,
        "model_consistency": consistency,
        "mechanism_activated": activated,
        "mechanism_indicators": indicators,
        "tier_n_pairs": tier_n_pairs,
    }

    with open(results_path, "w") as f:
        json.dump(output, f, indent=2)
    logger.info(f"[h-m3] Results saved: {results_path}")

    # Summary print
    print("\n" + "=" * 70)
    print(f"H-M3 EXPERIMENT COMPLETE")
    print("=" * 70)
    print(f"Gate: {overall_gate} ({n_models_gate_passed}/{len(all_model_results)} models)")
    print(f"Mechanism activated: {activated}")
    for k, v in indicators.items():
        print(f"  {k}: {v}")
    print(f"Results: {results_path}")
    print("=" * 70)

    # Return exit code based on gate result (0=PASS, 1=FAIL for CI)
    sys.exit(0 if overall_gate == "PASS" else 1)


if __name__ == "__main__":
    main()
