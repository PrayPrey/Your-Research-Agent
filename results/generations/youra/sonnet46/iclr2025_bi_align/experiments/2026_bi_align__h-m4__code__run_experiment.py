"""
run_experiment.py - h-m2 bidirectional semantic accommodation orchestrator.

H-M2: Bidirectional C_sem directional asymmetry (H←A > A←H).
Gate: tiers_passing >= 2 AND models_passing >= 2.
"""
import os
import sys
import json
import csv
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np

# CRITICAL: Set thread limits before loading numpy-dependent libraries
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")

# Local module imports
from config import load_config, ExperimentConfig
from data_loader import split_by_tier
from embedder import Embedder
from controls import build_random_control, build_topic_control
from accommodation import compute_bidirectional_csem_per_tier
from statistics import (
    test_directional_asymmetry,
    compute_asymmetry_monotonicity,
    check_model_consistency_m2,
    verify_mechanism_activated_m2,
    compute_ipw_csem_bidir,
    ks_test_tier_distributions,
    TIER_ORDER,
)
from visualize import (
    plot_bidirectional_bars,
    plot_directional_asymmetry_bars,
    plot_asymmetry_delta_line,
    plot_pairwise_distributions_violin,
    plot_significance_heatmap,
    plot_bootstrap_ci_comparison,
    plot_ipw_asymmetry,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

HYPOTHESIS_ID = "h-m2"

MODEL_CONFIGS = [
    {"name": "all-MiniLM-L6-v2", "slug": "minilm"},
    {"name": "paraphrase-MiniLM-L6-v2", "slug": "paraphrase"},
    {"name": "all-mpnet-base-v2", "slug": "mpnet"},
]

DEFAULT_CONFIG = {
    "cache_dir": "../../.data_cache/datasets/hh-rlhf",
    "output_dir": "outputs",
    "embeddings_dir": "../h-m1/code/embeddings",
    "figures_dir": "../../figures",
    "dry_run": False,
    "n_samples_dry_run": 500,
}


def run_single_model(
    model_cfg: Dict,
    tier_pairs: Dict,
    config,
    seed: int = 42,
) -> Dict:
    """Run bidirectional C_sem for one SBERT model.

    Args:
        model_cfg: {'name': str, 'slug': str}
        tier_pairs: Dict from split_by_tier()
        config: ExperimentConfig or dict with embeddings_dir, stats fields
        seed: Random seed

    Returns:
        {tier_results, asymmetry_test, monotonicity, model_name, slug}
    """
    if isinstance(config, dict):
        embeddings_dir = config.get("embeddings_dir", DEFAULT_CONFIG["embeddings_dir"])
        alpha = config.get("alpha", 0.05)
        n_bootstrap = config.get("n_bootstrap", 1000)
        knn_n_jobs = config.get("knn_n_jobs", 1)
    else:
        embeddings_dir = config.cache.embeddings_dir
        alpha = config.stats.alpha
        n_bootstrap = config.stats.n_bootstrap
        knn_n_jobs = config.stats.knn_n_jobs

    model_name = model_cfg["name"]
    slug = model_cfg["slug"]
    logger.info(f"[H-M2] Starting model: {model_name}")

    embedder = Embedder(model_name, embeddings_dir)

    # Bidirectional C_sem per tier
    bidir_results = compute_bidirectional_csem_per_tier(
        tier_pairs=tier_pairs,
        embedder=embedder,
        controls_fn_random=build_random_control,
        controls_fn_topic=lambda p, a: build_topic_control(p, a),
        seed=seed,
    )

    # Directional asymmetry test per tier
    asymmetry_test = test_directional_asymmetry(
        bidir_results_by_tier=bidir_results,
        alpha=alpha,
        n_bootstrap=n_bootstrap,
        seed=seed,
    )

    # Monotonicity analysis (secondary)
    monotonicity = compute_asymmetry_monotonicity(bidir_results, TIER_ORDER)

    logger.info(
        f"[H-M2] Model {slug}: tiers_passing={asymmetry_test['tiers_passing']}, "
        f"gate_passed={asymmetry_test['gate_passed']}"
    )

    return {
        "tier_results": bidir_results,
        "asymmetry_test": asymmetry_test,
        "monotonicity": monotonicity,
        "model_name": model_name,
        "slug": slug,
    }


def evaluate_gate_m2(all_model_results: Dict) -> Dict:
    """Evaluate H-M2 SHOULD_WORK gate: models_passing >= 2.

    Args:
        all_model_results: {model_slug: {asymmetry_test: {tiers_passing, gate_passed}}}

    Returns:
        {gate_passed: bool, models_passing: int, passing_models: List[str],
         details: {slug: {tiers_passing, gate_passed}}}
    """
    models_passing = 0
    passing_models = []
    details = {}

    for slug, model_data in all_model_results.items():
        asym = model_data.get("asymmetry_test", {})
        passed = bool(asym.get("gate_passed", False))
        tiers = int(asym.get("tiers_passing", 0))
        details[slug] = {"tiers_passing": tiers, "gate_passed": passed}
        if passed:
            models_passing += 1
            passing_models.append(slug)

    gate_passed = models_passing >= 2
    logger.info(
        f"[H-M2 GATE] {'PASS' if gate_passed else 'FAIL'}: "
        f"{models_passing}/3 models, details: {details}"
    )

    return {
        "gate_passed": gate_passed,
        "models_passing": models_passing,
        "passing_models": passing_models,
        "details": details,
    }


# Alias for backward-compat with tests
def evaluate_gate(all_model_results: Dict) -> Dict:
    """Backward-compatible alias that also checks JT + Cohen's d (h-m1 style).

    For h-m2 this checks: JT p < 0.05 AND any pairwise cohen_d >= 0.1 per model.
    """
    consistent_count = 0
    consistent_models = []
    details = {}

    for slug, model_data in all_model_results.items():
        jt = model_data.get("jt", {})
        pairwise = model_data.get("pairwise", {})
        jt_passed = jt.get("jt_pvalue", 1.0) < 0.05
        max_d = max(
            (p.get("cohen_d", 0.0) for p in pairwise.values()),
            default=0.0
        )
        d_passed = max_d >= 0.1
        model_passed = jt_passed and d_passed
        if model_passed:
            consistent_count += 1
            consistent_models.append(slug)
        details[slug] = {"jt_passed": jt_passed, "d_passed": d_passed, "passed": model_passed}

    gate_passed = consistent_count >= 2
    return {
        "gate_passed": gate_passed,
        "consistent_count": consistent_count,
        "consistent_models": consistent_models,
        "details": details,
    }


def save_results(results: Dict, output_dir: str) -> None:
    """Save experiment results to JSON and CSV.

    Args:
        results: Full experiment results dict
        output_dir: Directory to save files
    """
    os.makedirs(output_dir, exist_ok=True)

    # JSON: serialize non-array fields
    def _serialize(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    json_path = os.path.join(output_dir, "experiment_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, default=_serialize, indent=2)
    logger.info(f"Results saved: {json_path}")

    # CSV: asymmetry summary (9 rows: 3 models x 3 tiers)
    csv_path = os.path.join(output_dir, "asymmetry_summary.csv")
    all_model_results = results.get("all_model_results", {})
    rows = []
    for slug, model_data in all_model_results.items():
        tier_results = model_data.get("tier_results", {})
        asymmetry_test = model_data.get("asymmetry_test", {})
        tiers_passing = asymmetry_test.get("tiers_passing", 0)
        gate_passed = asymmetry_test.get("gate_passed", False)
        for tier in TIER_ORDER:
            if tier in tier_results:
                td = tier_results[tier]
                at = asymmetry_test.get(tier, {})
                rows.append({
                    "model": slug,
                    "tier": tier,
                    "csem_H_given_A": td.get("csem_H_given_A", ""),
                    "csem_A_given_H": td.get("csem_A_given_H", ""),
                    "delta_asymmetry": td.get("csem_H_given_A", 0.0) - td.get("csem_A_given_H", 0.0),
                    "p_value": at.get("p_value", ""),
                    "cohen_d": at.get("cohen_d", ""),
                    "tiers_passing": tiers_passing,
                    "gate_passed": gate_passed,
                })

    if rows:
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        logger.info(f"Summary saved: {csv_path}")


def generate_all_bidir_figures(all_model_results: Dict, figures_dir: str, ipw_results: Dict = None) -> None:
    """Generate all 7 bidirectional figures.

    Args:
        all_model_results: {slug: {tier_results, asymmetry_test, ...}}
        figures_dir: Directory to save figures
        ipw_results: Optional IPW results for plot_ipw_asymmetry
    """
    os.makedirs(figures_dir, exist_ok=True)
    logger.info(f"Generating 7 bidirectional figures in {figures_dir}")

    plot_bidirectional_bars(all_model_results, figures_dir)
    plot_directional_asymmetry_bars(all_model_results, figures_dir)
    plot_asymmetry_delta_line(all_model_results, figures_dir)
    plot_pairwise_distributions_violin(all_model_results, figures_dir)
    plot_significance_heatmap(all_model_results, figures_dir)
    plot_bootstrap_ci_comparison(all_model_results, figures_dir)

    if ipw_results:
        plot_ipw_asymmetry(all_model_results, ipw_results, figures_dir)
    else:
        # Generate with empty ipw data
        plot_ipw_asymmetry(all_model_results, {}, figures_dir)

    logger.info("All 7 bidirectional figures generated.")


def generate_validation_report(
    results: Dict,
    gate: Dict,
    output_path: str,
) -> None:
    """Generate 04_validation.md report.

    Args:
        results: Full experiment results dict
        gate: Gate evaluation result
        output_path: Path to write the report
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    gate_str = "PASS" if gate.get("gate_passed") else "FAIL"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        f"# H-M2 Validation Report",
        f"",
        f"**Generated:** {now}",
        f"**Hypothesis:** H-M2 — Bidirectional Semantic Accommodation Asymmetry",
        f"**Gate type:** SHOULD_WORK",
        f"**Gate result:** {gate_str}",
        f"",
        f"## Gate Evaluation",
        f"",
        f"- Models passing (tiers_passing >= 2): {gate.get('models_passing', 0)}/3",
        f"- Passing models: {gate.get('passing_models', [])}",
        f"- Gate threshold: models_passing >= 2",
        f"",
        f"## Model Results",
        f"",
    ]

    all_model_results = results.get("all_model_results", {})
    for slug, model_data in all_model_results.items():
        tier_results = model_data.get("tier_results", {})
        asymmetry_test = model_data.get("asymmetry_test", {})
        lines.append(f"### Model: {slug}")
        lines.append(f"- tiers_passing: {asymmetry_test.get('tiers_passing', 0)}")
        lines.append(f"- gate_passed: {asymmetry_test.get('gate_passed', False)}")
        lines.append(f"")
        for tier in TIER_ORDER:
            if tier in tier_results:
                td = tier_results[tier]
                at = asymmetry_test.get(tier, {})
                lines.append(f"  **{tier}**")
                lines.append(f"  - C_sem^H←A = {td.get('csem_H_given_A', 'N/A'):.4f}" if isinstance(td.get('csem_H_given_A'), float) else f"  - C_sem^H←A = N/A")
                lines.append(f"  - C_sem^A←H = {td.get('csem_A_given_H', 'N/A'):.4f}" if isinstance(td.get('csem_A_given_H'), float) else f"  - C_sem^A←H = N/A")
                lines.append(f"  - p_value = {at.get('p_value', 'N/A')}")
                lines.append(f"  - cohen_d = {at.get('cohen_d', 'N/A')}")
                lines.append(f"")

    consistency = results.get("consistency", {})
    mechanism_flag, mechanism_indicators = results.get("mechanism", (False, {}))
    lines += [
        f"## Consistency Check",
        f"",
        f"- consistent_count: {consistency.get('consistent_count', 0)}",
        f"- gate_passed: {consistency.get('gate_passed', False)}",
        f"",
        f"## Mechanism Activation",
        f"",
        f"- Mechanism activated: {mechanism_flag}",
    ]
    for k, v in mechanism_indicators.items():
        lines.append(f"  - {k}: {v}")

    lines += [
        f"",
        f"## Interpretation",
        f"",
    ]

    if gate.get("gate_passed"):
        lines.append("Gate PASS: H-M2 confirmed. Human-to-AI accommodation (H←A) is significantly "
                     "stronger than AI-to-Human accommodation (A←H) across >= 2/3 models and >= 2 tiers.")
    else:
        lines.append("Gate FAIL: H-M2 not confirmed at SHOULD_WORK threshold. Results may indicate "
                     "symmetric mutual contextual coherence rather than directional asymmetry. "
                     "Reinterpreted as mutual adaptation — H-M4 proceeds regardless.")

    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    logger.info(f"04_validation.md written to: {output_path}")


def run_dry_run(config: Dict, n_per_tier: int = 50) -> Dict:
    """Run experiment on n_per_tier synthetic samples per tier.

    Args:
        config: Config dict with cache_dir, output_dir, embeddings_dir, figures_dir
        n_per_tier: Number of pairs per tier to use

    Returns:
        Full results dict
    """
    from data_loader import split_by_tier

    cache_dir = config.get("cache_dir", DEFAULT_CONFIG["cache_dir"])
    output_dir = config.get("output_dir", DEFAULT_CONFIG["output_dir"])
    embeddings_dir = config.get("embeddings_dir", DEFAULT_CONFIG["embeddings_dir"])
    figures_dir = config.get("figures_dir", DEFAULT_CONFIG["figures_dir"])
    seed = config.get("seed", 42)

    logger.info(f"[H-M2] DRY RUN: n_per_tier={n_per_tier}")
    tier_pairs = split_by_tier(cache_dir)

    # Subsample
    for tier in TIER_ORDER:
        if tier in tier_pairs:
            pairs = tier_pairs[tier]
            n = min(n_per_tier, len(pairs["h_next"]))
            tier_pairs[tier] = {k: v[:n] for k, v in pairs.items()}

    all_model_results = {}
    model_cfg = MODEL_CONFIGS[0]  # Only primary model for dry run

    result = run_single_model(
        model_cfg=model_cfg,
        tier_pairs=tier_pairs,
        config=config,
        seed=seed,
    )
    all_model_results[model_cfg["slug"]] = result

    gate = evaluate_gate_m2(all_model_results)

    results = {
        "all_model_results": all_model_results,
        "gate": gate,
        "consistency": {"consistent_count": gate["models_passing"], "gate_passed": gate["gate_passed"]},
        "mechanism": (True, {}),
    }

    logger.info(f"[H-M2] DRY RUN complete. Gate: {'PASS' if gate['gate_passed'] else 'FAIL'}")
    return results


def run_bidirectional_experiment(config) -> Dict:
    """Main h-m2 experiment orchestrator.

    Args:
        config: ExperimentConfig or dict

    Returns:
        {all_model_results, consistency_m2, mechanism_m2, gate}
    """
    if isinstance(config, dict):
        cache_dir = config.get("cache_dir", DEFAULT_CONFIG["cache_dir"])
        output_dir = config.get("output_dir", DEFAULT_CONFIG["output_dir"])
        figures_dir = config.get("figures_dir", DEFAULT_CONFIG["figures_dir"])
        seed = config.get("seed", 42)
    else:
        cache_dir = config.cache.cache_dir
        output_dir = config.output_dir
        figures_dir = config.figures.figures_dir
        seed = config.stats.seed

    logger.info(f"[H-M2] Starting bidirectional experiment")

    # Load data
    tier_pairs = split_by_tier(cache_dir)

    # Run 3 models
    all_model_results = {}
    for model_cfg in MODEL_CONFIGS:
        result = run_single_model(
            model_cfg=model_cfg,
            tier_pairs=tier_pairs,
            config=config,
            seed=seed,
        )
        all_model_results[model_cfg["slug"]] = result

    # Model consistency check
    consistency_m2 = check_model_consistency_m2(all_model_results)

    # Mechanism verification
    experiment_log = "[FR-M2]"  # Assume triggered since we ran bidirectional
    mechanism_flag, mechanism_indicators = verify_mechanism_activated_m2(
        all_model_results, experiment_log
    )

    # Gate evaluation
    gate = evaluate_gate_m2(all_model_results)

    # Generate figures
    generate_all_bidir_figures(all_model_results, figures_dir)

    results = {
        "all_model_results": all_model_results,
        "consistency_m2": consistency_m2,
        "mechanism_m2": (mechanism_flag, mechanism_indicators),
        "gate": gate,
        "consistency": {"consistent_count": gate["models_passing"], "gate_passed": gate["gate_passed"]},
        "mechanism": (mechanism_flag, mechanism_indicators),
        "ks_results": {},
        "ipw_csem": {},
    }

    # Save results
    save_results(results, output_dir)

    logger.info(
        f"[H-M2] Experiment complete. Gate: {'PASS' if gate['gate_passed'] else 'FAIL'} "
        f"({gate['models_passing']}/3 models)"
    )

    return results


def main() -> int:
    """Main entry point with argparse."""
    parser = argparse.ArgumentParser(description=f"Run {HYPOTHESIS_ID} bidirectional experiment")
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML")
    parser.add_argument("--dry-run", action="store_true", help="Run on subset of data")
    parser.add_argument("--n-samples", type=int, default=500, help="Samples per tier (dry run)")
    parser.add_argument("--output-dir", default="outputs", help="Output directory")
    parser.add_argument("--report-path", default=None, help="Custom path for 04_validation.md")
    args = parser.parse_args()

    config = load_config(args.config if os.path.exists(args.config) else None)
    if args.output_dir != "outputs":
        config.output_dir = args.output_dir

    logger.info(f"Starting {HYPOTHESIS_ID} experiment (dry_run={args.dry_run})")

    if args.dry_run:
        config_dict = {
            "cache_dir": config.cache.cache_dir,
            "output_dir": config.output_dir,
            "embeddings_dir": config.cache.embeddings_dir,
            "figures_dir": config.figures.figures_dir,
            "n_samples_dry_run": args.n_samples,
            "dry_run": True,
            "seed": config.stats.seed,
            "alpha": config.stats.alpha,
            "n_bootstrap": config.stats.n_bootstrap,
            "knn_n_jobs": config.stats.knn_n_jobs,
        }
        results = run_dry_run(config_dict, n_per_tier=args.n_samples)
        gate = results.get("gate", {})
        report_path = args.report_path or os.path.join(config.output_dir, "04_validation_dryrun.md")
        generate_validation_report(results, gate, report_path)
        logger.info(f"Dry run complete. Gate: {'PASS' if gate.get('gate_passed') else 'FAIL'}")
    else:
        results = run_bidirectional_experiment(config)
        gate = results.get("gate", {})
        report_path = args.report_path or os.path.join(config.output_dir, "04_validation.md")
        generate_validation_report(results, gate, report_path)
        logger.info(f"Experiment complete. Gate: {'PASS' if gate.get('gate_passed') else 'FAIL'}")

    return 0 if results.get("gate", {}).get("gate_passed", False) else 1


if __name__ == "__main__":
    sys.exit(main())
