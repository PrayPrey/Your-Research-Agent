"""H-M2: Domain Exposure-Benchmark Correlation Analysis."""
from __future__ import annotations
import argparse
import json
import logging
import sys
from pathlib import Path
import numpy as np

# Allow imports from code/ directory
sys.path.insert(0, str(Path(__file__).parent))

import config
from src.data_loader import load_exposure_arrays, verify_coverage, apply_floor_filter
from src.evaluator import load_scores_array, batch_evaluate_model
from src.correlation_analysis import compute_spearman_matrix, extract_focal_correlations
from src.statistical_test import verify_mechanism_activated, run_all_tests
from src.visualization import (
    fig1_gate_metrics_bar,
    fig2_domain_benchmark_heatmap,
    fig3_trajectories,
    fig4_fisher_forest,
    fig5_floor_filter_diagnostic,
)
from src.reporter import (
    save_correlation_matrix,
    save_gate_summary,
    save_fisher_tests,
    write_results_summary,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def load_or_fetch_scores(model_size: str, device: str, skip_eval: bool) -> dict[str, np.ndarray]:
    """Load cached scores; run evaluation if cache incomplete and skip_eval=False."""
    scores = load_scores_array(model_size)

    has_nan = any(np.any(np.isnan(v)) for v in scores.values())
    if has_nan and not skip_eval:
        logger.info(f"[{model_size}] cache incomplete, running evaluation...")
        batch_evaluate_model(model_size, device=device)
        scores = load_scores_array(model_size)
    elif has_nan:
        logger.warning(f"[{model_size}] cache incomplete and skip_eval=True, using NaN-filled scores")

    return scores


def main(model_sizes: list[str], device: str, skip_eval: bool) -> None:
    Path(config.RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.FIGURES_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.EVAL_CACHE_DIR).mkdir(parents=True, exist_ok=True)

    # ── 1. Load exposure arrays and benchmark scores ──────────────────────────
    exposure_raw: dict[str, np.ndarray] = {}
    scores_raw: dict[str, dict[str, np.ndarray]] = {}

    for ms in model_sizes:
        logger.info(f"Loading H-E1 exposure for {ms}...")
        exp = load_exposure_arrays(ms)
        verify_coverage(exp, ms)
        exposure_raw[ms] = exp
        scores_raw[ms] = load_or_fetch_scores(ms, device, skip_eval)

    # ── 2. Floor filter ───────────────────────────────────────────────────────
    exposure_filtered: dict[str, np.ndarray] = {}
    scores_filtered: dict[str, dict[str, np.ndarray]] = {}
    valid_masks: dict[str, np.ndarray] = {}
    valid_steps: dict[str, list[int]] = {}
    steps_arr = np.array(config.CHECKPOINT_STEPS)

    for ms in model_sizes:
        exp_f, sc_f, mask = apply_floor_filter(exposure_raw[ms], scores_raw[ms])
        exposure_filtered[ms] = exp_f
        scores_filtered[ms] = sc_f
        valid_masks[ms] = mask
        valid_steps[ms] = list(steps_arr[mask])
        logger.info(f"[{ms}] floor filter: {mask.sum()} / 154 checkpoints kept")

    # ── 3. Correlation analysis ───────────────────────────────────────────────
    matrices: dict = {}
    for ms in model_sizes:
        logger.info(f"[{ms}] computing Spearman matrix (22 domains x 2 benchmarks)...")
        matrices[ms] = compute_spearman_matrix(
            exposure_filtered[ms],
            scores_filtered[ms],
        )

    focal_corr = extract_focal_correlations(matrices)

    # ── 4. Statistical tests ──────────────────────────────────────────────────
    test_results = run_all_tests(focal_corr, matrices)
    mechanism_activated, indicators = verify_mechanism_activated(matrices)

    logger.info(f"Mechanism activated: {mechanism_activated}")
    logger.info(f"Indicators: {indicators}")

    # ── 5. Figures ────────────────────────────────────────────────────────────
    figs_dir = Path(config.FIGURES_DIR)
    fig1_gate_metrics_bar(focal_corr, str(figs_dir / "fig1_gate_metrics.png"))
    fig2_domain_benchmark_heatmap(matrices, str(figs_dir / "fig2_domain_heatmap.png"))
    fig3_trajectories(exposure_filtered, scores_filtered, valid_steps, str(figs_dir / "fig3_trajectories.png"))
    fig4_fisher_forest(test_results, focal_corr, str(figs_dir / "fig4_fisher_forest.png"))
    fig5_floor_filter_diagnostic(valid_masks, scores_raw, str(figs_dir / "fig5_floor_diagnostic.png"))
    logger.info("Figures saved.")

    # ── 6. Save outputs ───────────────────────────────────────────────────────
    results_dir = Path(config.RESULTS_DIR)
    save_correlation_matrix(matrices, str(results_dir / "correlation_matrix.json"))
    save_gate_summary(mechanism_activated, indicators, str(results_dir / "gate_summary.json"))
    save_fisher_tests(test_results, str(results_dir / "fisher_tests.json"))
    write_results_summary(indicators, matrices, test_results,
                          "docs/youra_research/h-m2/04_results_summary.md")

    # ── 7. experiment_results.json ────────────────────────────────────────────
    experiment_results = {
        "hypothesis_id": "h-m2",
        "mechanism_activated": mechanism_activated,
        "indicators": indicators,
        "focal_correlations": {
            ms: {
                "rho_wiki_mmlu": focal_corr["rho_wiki_mmlu"][ms],
                "rho_wiki_hellaswag": focal_corr["rho_wiki_hellaswag"][ms],
                "rho_books_hellaswag": focal_corr["rho_books_hellaswag"][ms],
                "rho_books_mmlu": focal_corr["rho_books_mmlu"][ms],
                "n_valid": focal_corr["n_valid"][ms],
            }
            for ms in model_sizes
        },
        "fisher_tests": {
            ms: {
                "p1": test_results[ms]["p1"],
                "p2": test_results[ms]["p2"],
            }
            for ms in model_sizes
        },
        "floor_filter": {
            ms: {"n_valid": int(valid_masks[ms].sum()), "n_total": 154}
            for ms in model_sizes
        },
    }
    Path("docs/youra_research/h-m2/experiment_results.json").write_text(
        json.dumps(experiment_results, indent=2)
    )
    logger.info("experiment_results.json saved.")
    logger.info("Pipeline complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-M2: Domain Exposure-Benchmark Correlation")
    parser.add_argument("--model-sizes", nargs="+", default=config.MODEL_SIZES)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--skip-eval", action="store_true",
                        help="Skip lm-eval; use cached scores only (NaN if missing)")
    args = parser.parse_args()
    main(args.model_sizes, args.device, args.skip_eval)
