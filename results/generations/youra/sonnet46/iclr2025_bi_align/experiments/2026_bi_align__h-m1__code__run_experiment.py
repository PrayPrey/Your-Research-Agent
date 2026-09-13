"""
run_experiment.py - Multi-model × multi-tier orchestrator for h-m1.

Tests RLHF tier monotonicity of semantic accommodation (C_sem) across
3 SBERT models × 3 RLHF tiers. Gate: >= 2/3 models show J-T p < 0.05 AND d >= 0.1.
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

# Local module imports
from data_loader import split_by_tier
from embedder import Embedder
from controls import build_random_control, build_topic_control
from accommodation import compute_tier_csem_matrix, aggregate_model_results
from statistics import (
    bootstrap_c_sem,
    jonckheere_terpstra_test,
    bonferroni_mannwhitney,
    bootstrap_cohens_d_all_pairs,
    ks_test_tier_distributions,
    compute_ipw_csem,
    check_model_consistency,
    verify_mechanism_activated_m1,
)
from visualize import (
    plot_tier_csem_bars,
    plot_tier_monotonicity_lines,
    plot_cohend_heatmap,
    plot_tier_violin,
    plot_bootstrap_kde_tiers,
    plot_ipw_comparison,
    plot_ks_summary,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

HYPOTHESIS_ID = "h-m1"
TIER_ORDER = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]
TIER_SLUGS = {
    "helpful-base": "base",
    "helpful-rejection-sampled": "rs",
    "helpful-online": "online",
}

MODEL_CONFIGS = [
    {"name": "all-MiniLM-L6-v2", "slug": "minilm", "role": "primary"},
    {"name": "paraphrase-MiniLM-L6-v2", "slug": "paraphrase", "role": "robustness1"},
    {"name": "all-mpnet-base-v2", "slug": "mpnet", "role": "robustness2"},
]


def run_tier_experiment(config: Dict) -> Dict:
    """Main experiment entry point: 3-model × 3-tier nested loop.

    Args:
        config: dict with keys: cache_dir, output_dir, embeddings_dir,
                figures_dir, dry_run (bool), n_samples_dry_run (int)

    Returns:
        all_model_results: {model_slug: {tier_results, jt, pairwise, consistency}}
    """
    cache_dir = config.get("cache_dir", ".data_cache/datasets/hh-rlhf")
    embeddings_dir = config.get("embeddings_dir", "embeddings")
    dry_run = config.get("dry_run", False)
    n_dry = config.get("n_samples_dry_run", 500)

    # Step 1: Load data per tier
    logger.info("Step 1: Loading tier data...")
    tier_pairs = split_by_tier(cache_dir)

    if dry_run:
        logger.info(f"DRY RUN: Truncating each tier to {n_dry} pairs")
        for tier in TIER_ORDER:
            for key in ["h_next", "a_actual", "h_prompt", "token_counts", "jaccard_overlaps"]:
                tier_pairs[tier][key] = tier_pairs[tier][key][:n_dry]

    logger.info("Tier sizes:")
    for tier in TIER_ORDER:
        logger.info(f"  {tier}: {len(tier_pairs[tier]['h_next'])} pairs")

    # Step 2: KS test on prompt embeddings (pre-IPW trigger detection)
    # Run with primary model embeddings
    logger.info("Step 2: KS test on tier prompt distributions...")
    primary_embedder = Embedder(
        model_name=MODEL_CONFIGS[0]["name"],
        cache_dir=embeddings_dir
    )
    tier_prompt_embeddings = {}
    for tier in TIER_ORDER:
        n = len(tier_pairs[tier]["h_prompt"])
        tier_prompt_embeddings[tier] = primary_embedder.encode_tier(
            tier_pairs[tier]["h_prompt"], prefix="ks_p",
            tier=tier, n_pairs=n
        )

    ks_results = ks_test_tier_distributions(tier_prompt_embeddings, TIER_ORDER)
    ipw_triggered = any(v["ipw_triggered"] for v in ks_results.values())
    logger.info(f"KS test complete. IPW triggered: {ipw_triggered}")

    # Step 3: Multi-model loop
    logger.info("Step 3: Running 3-model × 3-tier analysis...")
    all_model_results = {}
    experiment_log_buffer = []

    for model_cfg in MODEL_CONFIGS:
        slug = model_cfg["slug"]
        logger.info(f"  Model: {model_cfg['name']} ({slug})")

        embedder = Embedder(
            model_name=model_cfg["name"],
            cache_dir=embeddings_dir
        )

        # Compute C_sem per tier
        tier_results = compute_tier_csem_matrix(
            tier_pairs, embedder,
            controls_fn_random=build_random_control,
            controls_fn_topic=build_topic_control,
        )

        # Collect FR-E3 log messages for mechanism verification
        for tier in TIER_ORDER:
            if tier in tier_results:
                c_sem = tier_results[tier]["c_sem"]
                log_msg = f"Tier {tier} C_sem computed: {c_sem:.4f}"
                experiment_log_buffer.append(log_msg)
                logger.info(log_msg)

        # Bootstrap CI per tier
        for tier in TIER_ORDER:
            if tier not in tier_results:
                continue
            tr = tier_results[tier]
            c_sem, ci = bootstrap_c_sem(
                tr["raw_cos_actual"], tr["raw_cos_random"],
                n_bootstrap=1000, seed=42
            )
            tier_results[tier]["c_sem"] = c_sem
            tier_results[tier]["c_sem_ci"] = ci

        # J-T test
        jt = jonckheere_terpstra_test(tier_results, TIER_ORDER)
        logger.info(f"  J-T test: stat={jt['jt_statistic']:.2f}, p={jt['jt_pvalue']:.4f}")

        # Bonferroni Mann-Whitney pairwise
        pairwise = bonferroni_mannwhitney(tier_results, TIER_ORDER)

        all_model_results[slug] = {
            "tier_results": tier_results,
            "jt": jt,
            "pairwise": pairwise,
        }

    # Step 4: Model consistency gate
    logger.info("Step 4: Checking model consistency...")
    consistency = check_model_consistency(all_model_results)
    logger.info(f"Consistency: {consistency['consistent_count']}/3 models pass gate")

    # Step 5: Cross-model Cohen's d
    pairwise_all = bootstrap_cohens_d_all_pairs({}, all_model_results, n=1000, seed=42)

    # Step 6: IPW correction if triggered
    ipw_csem = {}
    if ipw_triggered:
        logger.info("Step 6: Computing IPW-corrected C_sem (KS triggered)...")
        primary_tier_results = all_model_results[MODEL_CONFIGS[0]["slug"]]["tier_results"]
        ipw_csem = compute_ipw_csem(primary_tier_results, tier_prompt_embeddings)

    # Step 7: Mechanism verification
    experiment_log = "\n".join(experiment_log_buffer)
    mechanism = verify_mechanism_activated_m1(all_model_results, experiment_log)
    logger.info(f"Mechanism activated: {mechanism[0]}")

    return {
        "all_model_results": all_model_results,
        "consistency": consistency,
        "pairwise_all": pairwise_all,
        "ks_results": ks_results,
        "ipw_csem": ipw_csem,
        "mechanism": mechanism,
        "experiment_log": experiment_log,
    }


def run_dry_run(config: Dict, n_per_tier: int = 500) -> Dict:
    """Fast pre-flight check with truncated data.

    Args:
        config: Full experiment config dict.
        n_per_tier: Number of pairs per tier to use (default 500).

    Returns:
        Same structure as run_tier_experiment().
    """
    dry_config = {**config, "dry_run": True, "n_samples_dry_run": n_per_tier}
    return run_tier_experiment(dry_config)


def evaluate_gate(all_model_results: Dict) -> Dict:
    """Evaluate MUST_WORK gate: >= 2/3 models pass J-T + Cohen's d.

    Args:
        all_model_results: {model_slug: {jt, pairwise, tier_results}}

    Returns:
        {gate_passed, consistent_count, consistent_models, details}
    """
    consistency = check_model_consistency(all_model_results)

    # Per-model details for report
    details = {}
    for slug, model_data in all_model_results.items():
        jt = model_data.get("jt", {})
        pairwise = model_data.get("pairwise", {})
        max_d = max(
            (abs(v.get("cohen_d", 0.0)) for v in pairwise.values()),
            default=0.0,
        )
        details[slug] = {
            "jt_pvalue": jt.get("jt_pvalue", 1.0),
            "max_cohen_d": max_d,
            "passes": slug in consistency["consistent_models"],
        }

    return {
        "gate_passed": consistency["gate_passed"],
        "consistent_count": consistency["consistent_count"],
        "consistent_models": consistency["consistent_models"],
        "details": details,
    }


def generate_validation_report(
    results: Dict,
    gate: Dict,
    output_path: str,
) -> None:
    """Generate 04_validation.md validation report (FR-E5).

    Args:
        results: Full experiment results from run_tier_experiment().
        gate: Gate evaluation from evaluate_gate().
        output_path: Output path for 04_validation.md.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    gate_passed = gate.get("gate_passed", False)
    gate_verdict = "PASS" if gate_passed else "FAIL"
    all_model_results = results.get("all_model_results", {})
    consistency = results.get("consistency", gate)
    mechanism = results.get("mechanism", (False, {}))
    mechanism_activated, indicators = mechanism if isinstance(mechanism, tuple) else (False, {})
    ks_results = results.get("ks_results", {})
    ipw_csem = results.get("ipw_csem", {})

    lines = [
        f"# Phase 4 Validation Report: {HYPOTHESIS_ID}",
        f"",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Hypothesis:** H-M1 — Tier-Monotonic C_sem Scaling",
        f"**Gate Type:** MUST_WORK",
        f"",
        f"## Gate Result: {gate_verdict}",
        f"",
        f"**Consistent models:** {consistency.get('consistent_count', 0)}/3 "
        f"(required: >=2)",
        f"**Models passing gate:** {', '.join(consistency.get('consistent_models', []))}",
        f"",
        f"## C_sem per Tier per Model",
        f"",
        f"| Model | T1: Base | T2: RS | T3: Online | J-T p-value |",
        f"|-------|----------|--------|------------|-------------|",
    ]

    for slug, model_data in all_model_results.items():
        tier_results = model_data.get("tier_results", {})
        jt = model_data.get("jt", {})
        t1 = tier_results.get("helpful-base", {}).get("c_sem", 0.0)
        t2 = tier_results.get("helpful-rejection-sampled", {}).get("c_sem", 0.0)
        t3 = tier_results.get("helpful-online", {}).get("c_sem", 0.0)
        jtp = jt.get("jt_pvalue", 1.0)
        lines.append(f"| {slug} | {t1:.4f} | {t2:.4f} | {t3:.4f} | {jtp:.4f} |")

    lines += [
        f"",
        f"## Cohen's d: Tier Pair Comparisons",
        f"",
        f"| Model | T1 vs T2 | T2 vs T3 | T1 vs T3 |",
        f"|-------|----------|----------|----------|",
    ]

    for slug, model_data in all_model_results.items():
        pairwise = model_data.get("pairwise", {})
        d12 = pairwise.get("helpful-base_vs_helpful-rejection-sampled", {}).get("cohen_d", 0.0)
        d23 = pairwise.get("helpful-rejection-sampled_vs_helpful-online", {}).get("cohen_d", 0.0)
        d13 = pairwise.get("helpful-base_vs_helpful-online", {}).get("cohen_d", 0.0)
        lines.append(f"| {slug} | {d12:.4f} | {d23:.4f} | {d13:.4f} |")

    lines += [
        f"",
        f"## Model Consistency Summary",
        f"",
    ]

    gate_details = gate.get("details", {})
    for slug, detail in gate_details.items():
        status = "✓ PASS" if detail.get("passes") else "✗ FAIL"
        lines.append(
            f"- **{slug}**: {status} "
            f"(J-T p={detail.get('jt_pvalue', 1.0):.4f}, "
            f"max d={detail.get('max_cohen_d', 0.0):.4f})"
        )

    lines += [
        f"",
        f"## Mechanism Activation Indicators",
        f"",
    ]

    indicator_labels = {
        "tier_logs_found": "FR-E3 tier logs found",
        "all_tiers_have_pairs": "All tiers have >= 1000 pairs",
        "csem_differs_across_tiers": "C_sem differs across tiers",
        "jt_computed": "J-T test computed",
        "all_models_ran": "All 3 models executed",
    }

    for key, label in indicator_labels.items():
        val = indicators.get(key, False)
        icon = "✓" if val else "✗"
        lines.append(f"- {icon} **{label}**: {val}")

    lines += [
        f"",
        f"**All activated:** {mechanism_activated}",
        f"",
        f"## KS Test Results (Covariate Shift)",
        f"",
    ]

    if ks_results:
        lines.append("| Tier Pair | KS Stat | KS p-value | IPW Triggered |")
        lines.append("|-----------|---------|------------|---------------|")
        for pk, v in ks_results.items():
            short_pk = pk.replace("helpful-", "").replace("-", " ")
            lines.append(
                f"| {short_pk} | {v['ks_statistic']:.4f} | "
                f"{v['ks_pvalue']:.4f} | {v['ipw_triggered']} |"
            )
    else:
        lines.append("*(KS test not computed)*")

    if ipw_csem:
        lines += [
            f"",
            f"## IPW-Adjusted C_sem (Covariate Shift Correction)",
            f"",
        ]
        for tier, val in ipw_csem.items():
            lines.append(f"- **{tier}**: {val:.4f}")

    lines += [
        f"",
        f"## Key Findings",
        f"",
    ]

    # Auto-generate key findings
    if gate_passed:
        lines.append(
            f"- RLHF tier quality monotonically predicts C_sem in "
            f"{consistency.get('consistent_count', 0)}/3 SBERT models"
        )
        # Find primary model results for specific numbers
        if "minilm" in all_model_results:
            tr = all_model_results["minilm"]["tier_results"]
            t1 = tr.get("helpful-base", {}).get("c_sem", 0.0)
            t3 = tr.get("helpful-online", {}).get("c_sem", 0.0)
            jtp = all_model_results["minilm"]["jt"].get("jt_pvalue", 1.0)
            lines.append(
                f"- Primary model (MiniLM): C_sem increases from {t1:.4f} (Base) to {t3:.4f} (Online)"
            )
            lines.append(f"- Jonckheere-Terpstra p={jtp:.4f} (primary model)")
        lines.append("- MUST_WORK gate PASSED: tier monotonicity of semantic accommodation confirmed")
    else:
        lines.append(f"- Only {consistency.get('consistent_count', 0)}/3 models show monotonic C_sem increase")
        lines.append("- MUST_WORK gate FAILED: tier monotonicity not confirmed")

    lines += [
        f"",
        f"---",
        f"*Generated by Phase 4 Coder-Validator workflow*",
    ]

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Validation report saved: {output_path}")


def run_experiment(config: Dict) -> Dict:
    """Full experiment pipeline (non-dry-run).

    Args:
        config: Full experiment config dict.

    Returns:
        Combined results dict with gate evaluation.
    """
    results = run_tier_experiment(config)
    gate = evaluate_gate(results["all_model_results"])
    results["gate"] = gate

    # Save validation report
    output_dir = config.get("output_dir", "outputs")
    os.makedirs(output_dir, exist_ok=True)
    report_path = config.get("report_path") or os.path.join(output_dir, "04_validation.md")
    generate_validation_report(results, gate, report_path)

    # Save experiment results JSON
    results_path = os.path.join(output_dir, "experiment_results.json")
    save_results_json(results, results_path)

    # Generate all visualization figures
    figures_dir = config.get("figures_dir", "figures")
    generate_all_figures(results, figures_dir)

    return results


def save_results_json(results: Dict, output_path: str) -> None:
    """Save experiment results to JSON (serializes non-serializable arrays)."""
    def _convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        raise TypeError(f"Not serializable: {type(obj)}")

    # Build serializable results (exclude raw arrays from JSON)
    serializable = {}
    for key, val in results.items():
        if key == "all_model_results":
            model_out = {}
            for slug, model_data in val.items():
                model_out[slug] = {
                    "jt": model_data.get("jt", {}),
                    "tier_csem": {
                        t: {"c_sem": tr.get("c_sem", 0.0), "n_pairs": tr.get("n_pairs", 0)}
                        for t, tr in model_data.get("tier_results", {}).items()
                    },
                }
            serializable[key] = model_out
        elif key == "mechanism":
            act, ind = val if isinstance(val, tuple) else (False, {})
            serializable[key] = {"activated": act, "indicators": ind}
        elif isinstance(val, dict):
            serializable[key] = val
        elif isinstance(val, (bool, int, float, str)):
            serializable[key] = val

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, default=_convert)
    logger.info(f"Results saved: {output_path}")


def generate_all_figures(results: Dict, figures_dir: str) -> None:
    """Generate all 7 tier-comparison visualization figures.

    Args:
        results: Full experiment results dict.
        figures_dir: Directory to save figures.
    """
    all_model_results = results.get("all_model_results", {})
    ks_results = results.get("ks_results", {})
    ipw_csem = results.get("ipw_csem", {})
    consistency = results.get("consistency", {})

    try:
        # 1. Tier C_sem bars (FR-V1 MANDATORY)
        plot_tier_csem_bars(all_model_results, figures_dir)
        logger.info("Generated: tier_csem_bars.png")
    except Exception as e:
        logger.warning(f"Failed tier_csem_bars: {e}")

    try:
        # 2. Monotonicity lines
        plot_tier_monotonicity_lines(all_model_results, figures_dir)
        logger.info("Generated: tier_monotonicity_lines.png")
    except Exception as e:
        logger.warning(f"Failed tier_monotonicity_lines: {e}")

    try:
        # 3. Cohen's d heatmap
        pairwise_by_model = {
            slug: model_data.get("pairwise", {})
            for slug, model_data in all_model_results.items()
        }
        plot_cohend_heatmap(pairwise_by_model, figures_dir)
        logger.info("Generated: cohend_heatmap.png")
    except Exception as e:
        logger.warning(f"Failed cohend_heatmap: {e}")

    # Use primary model for per-tier plots
    primary_slug = MODEL_CONFIGS[0]["slug"]
    if primary_slug in all_model_results:
        primary_tier_results = all_model_results[primary_slug].get("tier_results", {})

        try:
            # 4. Violin plot
            plot_tier_violin(primary_tier_results, primary_slug, figures_dir)
            logger.info("Generated: tier_violin.png")
        except Exception as e:
            logger.warning(f"Failed tier_violin: {e}")

        try:
            # 5. Bootstrap KDE
            plot_bootstrap_kde_tiers(primary_tier_results, primary_slug, figures_dir)
            logger.info("Generated: bootstrap_kde_tiers.png")
        except Exception as e:
            logger.warning(f"Failed bootstrap_kde_tiers: {e}")

    try:
        # 6. IPW comparison (only if triggered)
        if ipw_csem:
            primary_tier_results = all_model_results.get(primary_slug, {}).get("tier_results", {})
            raw_csem = {t: tr.get("c_sem", 0.0) for t, tr in primary_tier_results.items()}
            plot_ipw_comparison(raw_csem, ipw_csem, figures_dir)
            logger.info("Generated: ipw_comparison.png")
    except Exception as e:
        logger.warning(f"Failed ipw_comparison: {e}")

    try:
        # 7. KS summary
        if ks_results:
            plot_ks_summary(ks_results, figures_dir)
            logger.info("Generated: ks_summary.png")
    except Exception as e:
        logger.warning(f"Failed ks_summary: {e}")


def main():
    """CLI entry point for run_experiment.py."""
    parser = argparse.ArgumentParser(description="H-M1 Tier Monotonicity Experiment")
    parser.add_argument(
        "--cache-dir",
        default=".data_cache/datasets/hh-rlhf",
        help="HuggingFace datasets cache directory",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Output directory for results and reports",
    )
    parser.add_argument(
        "--embeddings-dir",
        default="embeddings",
        help="Embeddings cache directory",
    )
    parser.add_argument(
        "--figures-dir",
        default="../figures",
        help="Figures output directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run with reduced data subset for fast validation",
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=500,
        help="Samples per tier for dry run",
    )
    parser.add_argument(
        "--report-path",
        default=None,
        help="Custom path for 04_validation.md (default: output_dir/04_validation.md)",
    )
    args = parser.parse_args()

    config = {
        "cache_dir": args.cache_dir,
        "output_dir": args.output_dir,
        "embeddings_dir": args.embeddings_dir,
        "figures_dir": args.figures_dir,
        "dry_run": args.dry_run,
        "n_samples_dry_run": args.n_samples,
        "report_path": args.report_path,
    }

    logger.info(f"Starting {HYPOTHESIS_ID} experiment (dry_run={args.dry_run})")

    if args.dry_run:
        results = run_dry_run(config, n_per_tier=args.n_samples)
        gate = evaluate_gate(results["all_model_results"])
        results["gate"] = gate
        report_path = config.get("report_path") or os.path.join(args.output_dir, "04_validation_dryrun.md")
        generate_validation_report(results, gate, report_path)
        logger.info(f"Dry run complete. Gate: {'PASS' if gate['gate_passed'] else 'FAIL'}")
    else:
        results = run_experiment(config)
        gate = results.get("gate", {})
        logger.info(f"Experiment complete. Gate: {'PASS' if gate.get('gate_passed') else 'FAIL'}")

    return 0 if results.get("gate", {}).get("gate_passed", False) else 1


if __name__ == "__main__":
    sys.exit(main())
