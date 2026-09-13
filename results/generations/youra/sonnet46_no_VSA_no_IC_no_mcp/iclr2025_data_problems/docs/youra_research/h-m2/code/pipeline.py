"""End-to-end pipeline orchestrator for H-M2."""
from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import asdict
from pathlib import Path

logger = logging.getLogger(__name__)


def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """
    Verify mechanism activation indicators per 02c spec.
    Returns (activated: bool, indicators: dict).
    """
    from config import BENCHMARKS

    scores = results.get("scores", {})
    stats = results.get("stats", [])

    indicators = {
        "checkpoints_loaded": all(
            f"pile_{sz}" in scores and f"deduped_{sz}" in scores
            for sz in ["1b", "6.9b"]
        ),
        "scores_computed": all(
            len(scores.get("pile_1b", {}).get(bench, [])) >= 500
            for bench in BENCHMARKS
        ),
        "pile_higher_on_any": any(s.differential > 0 for s in stats),
        "effect_measurable": any(s.p_corrected < 0.0125 for s in stats),
    }

    activated = (
        indicators["checkpoints_loaded"]
        and indicators["scores_computed"]
        and indicators["pile_higher_on_any"]
    )
    return activated, indicators


def evaluate_gate(stats: list, corrected_alpha: float = 0.0125) -> dict:
    """Evaluate SHOULD_WORK gate: ≥1 benchmark p < corrected_alpha."""
    n_significant = sum(1 for s in stats if s.p_corrected < corrected_alpha)
    n_pile_higher = sum(1 for s in stats if s.differential > 0)

    # Primary: ≥2 benchmarks significant; SHOULD_WORK: ≥1 sufficient for PASS
    if n_significant >= 2:
        result = "PASS"
        satisfied = True
    elif n_significant >= 1:
        result = "PASS"  # SHOULD_WORK gate: ≥1 is sufficient
        satisfied = True
    elif n_pile_higher >= 2:
        result = "PARTIAL"
        satisfied = False
    else:
        result = "FAIL"
        satisfied = False

    return {
        "result": result,
        "satisfied": satisfied,
        "n_significant": n_significant,
        "n_pile_higher": n_pile_higher,
        "reasoning": (
            f"n_significant={n_significant}/8 benchmarks×model_sizes at p<{corrected_alpha}; "
            f"n_pile_higher={n_pile_higher}/8 (Pile > deduped direction)"
        ),
    }


def run_pipeline(
    stages: list[str] | None = None,
    skip_stages: list[str] | None = None,
    resume: bool = True,
    device: str = "cuda",
    dry_run: bool = False,
    dry_run_items: int = 50,
) -> dict:
    """
    Full pipeline with checkpoint/resume.

    Stages:
    1. load_benchmarks
    2. score_models
    3. run_stats
    4. run_ablations
    5. generate_figures
    """
    from config import BENCHMARKS, MODEL_CONFIGS, K_VALUES, CHECKPOINT_DIR, FIGURES_DIR, CORRECTED_ALPHA
    from benchmark_loader import load_all_benchmarks
    from mink_scorer import score_all_models
    from statistical_tester import run_all_tests, compute_spearman_cross_hypothesis
    from ablation_runner import run_k_sensitivity
    from visualizer import generate_all_figures

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    all_stages = ["load_benchmarks", "score_models", "run_stats", "run_ablations", "generate_figures"]
    active = [s for s in (stages or all_stages) if s not in (skip_stages or [])]

    results: dict = {}

    if "load_benchmarks" in active:
        logger.info("Stage: load_benchmarks")
        max_items = dry_run_items if dry_run else None
        results["benchmark_items"] = load_all_benchmarks(
            benchmarks=BENCHMARKS,
            max_items_per_benchmark=max_items,
        )

    if "score_models" in active:
        logger.info("Stage: score_models")
        benchmark_items = results.get("benchmark_items") or load_all_benchmarks(
            max_items_per_benchmark=dry_run_items if dry_run else None
        )
        model_configs = MODEL_CONFIGS
        if dry_run:
            # Only 1B models for dry run
            model_configs = {k: v for k, v in MODEL_CONFIGS.items() if "6.9b" not in k}

        results["scores"] = score_all_models(
            model_configs,
            benchmark_items,
            K_VALUES,
            CHECKPOINT_DIR,
            device,
        )

    if "run_stats" in active:
        logger.info("Stage: run_stats")
        results["stats"] = run_all_tests(results["scores"], corrected_alpha=CORRECTED_ALPHA)
        results["spearman"] = compute_spearman_cross_hypothesis(
            results["stats"],
            hm1_results_path=Path("docs/youra_research/h-m1/dry_run_result.json"),
        )

    if "run_ablations" in active:
        logger.info("Stage: run_ablations")
        benchmark_items = results.get("benchmark_items") or load_all_benchmarks(
            max_items_per_benchmark=500
        )
        results["ablations"] = run_k_sensitivity(
            benchmark_items,
            device=device,
            max_items=dry_run_items if dry_run else 500,
        )

    if "generate_figures" in active:
        logger.info("Stage: generate_figures")
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        results["figures"] = generate_all_figures(
            results.get("scores", {}),
            results.get("stats", []),
            results.get("ablations", {}),
            FIGURES_DIR,
            hm1_results_path=Path("docs/youra_research/h-m1/dry_run_result.json"),
        )

    # Gate evaluation
    stats = results.get("stats", [])
    gate = evaluate_gate(stats, CORRECTED_ALPHA)
    results["gate"] = gate

    # Mechanism check
    activated, indicators = verify_mechanism_activated(results)
    results["mechanism"] = {"activated": activated, "indicators": indicators}

    logger.info(f"Gate result: {gate['result']} (n_significant={gate['n_significant']})")
    logger.info(f"Mechanism activated: {activated}")

    return results


def save_experiment_results(results: dict, output_path: Path) -> None:
    """Serialize results to JSON for downstream phases."""
    stats = results.get("stats", [])
    spearman = results.get("spearman")
    gate = results.get("gate", {})
    mechanism = results.get("mechanism", {})

    serializable_stats = []
    for s in stats:
        serializable_stats.append({
            "benchmark": s.benchmark,
            "model_size": s.model_size,
            "mean_pile": s.mean_pile,
            "mean_deduped": s.mean_deduped,
            "differential": s.differential,
            "t_statistic": s.t_statistic,
            "p_value": s.p_value,
            "p_corrected": s.p_corrected,
            "wilcoxon_p": s.wilcoxon_p,
            "cohens_d": s.cohens_d,
            "significant": s.significant,
        })

    output = {
        "hypothesis_id": "h-m2",
        "gate": gate,
        "mechanism": mechanism,
        "stats": serializable_stats,
        "spearman": {
            "rho": spearman.rho if spearman else None,
            "p_value": spearman.p_value if spearman else None,
            "hm1_benchmark_order": spearman.hm1_benchmark_order if spearman else [],
            "hm2_benchmark_order": spearman.hm2_benchmark_order if spearman else [],
        } if spearman else None,
        "ablations": {str(k): v for k, v in results.get("ablations", {}).items()},
        "figures": results.get("figures", []),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(output, indent=2))
    os.replace(tmp, output_path)
    logger.info(f"Experiment results saved: {output_path}")
