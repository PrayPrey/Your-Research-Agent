"""
run_margin_analysis.py — H-M2 Pre-Softmax Logit Margin Inflation
Main orchestrator: 8-step pipeline from data loading to validation report.
"""
import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Add h-e1/code to sys.path
_CODE_DIR = Path(__file__).parent.resolve()
_H_E1_CODE_DIR = str(_CODE_DIR.parent.parent / "h-e1" / "code")
if _H_E1_CODE_DIR not in sys.path:
    sys.path.insert(0, _H_E1_CODE_DIR)

from config import (
    H_E1_CODE_DIR,
    H_E1_RESULTS_DIR,
    H_E1_VALIDATION_PATH,
    H_M2_RESULTS_DIR,
    H_M2_FIGURES_DIR,
    H_M2_REPORT_PATH,
    H_M2_EXPERIMENT_RESULTS_JSON,
    VERIFICATION_STATE_PATH,
    SIZES,
    ALIGNMENTS,
    N_ITEMS_EXPECTED,
    N_BOOTSTRAP,
    SEED,
    FIGURE_DPI,
)
from load_data import load_logprob_matrices
from margin_analysis import (
    compute_all_delta_margins,
    test_gradient_ordering,
    verify_mechanism_activated,
)
from gate_and_report import (
    evaluate_should_work_gate,
    generate_validation_report,
    write_gate_to_verification_state,
)
from visualization import generate_all_figures


def main(smoke_test: bool = False, device: str = "cuda") -> dict:
    """8-step H-M2 pipeline.

    1. Load logprob matrices (Path A -> Path B fallback)
    2. Validate all shapes == (N_ITEMS_EXPECTED, 4)
    3. compute_all_delta_margins (9 pairs, bootstrap n=1000, seed=42)
    4. test_gradient_ordering (Wilcoxon PPO>=DPO, DPO>SFT)
    5. verify_mechanism_activated
    6. evaluate_should_work_gate
    7. generate_all_figures
    8. generate_validation_report + write_gate_to_verification_state + save experiment_results.json

    Returns:
        {gate_result, delta_results, figure_paths, execution_path}
    """
    start_time = datetime.now(timezone.utc)
    logger.info("=" * 60)
    logger.info("H-M2: Pre-Softmax Logit Margin Inflation Analysis")
    logger.info("smoke_test=%s, device=%s", smoke_test, device)
    logger.info("=" * 60)

    # Create output directories
    os.makedirs(H_M2_RESULTS_DIR, exist_ok=True)
    os.makedirs(H_M2_FIGURES_DIR, exist_ok=True)

    # Setup file logging
    log_dir = str(_CODE_DIR)
    log_path = os.path.join(log_dir, "experiment.log")
    file_handler = logging.FileHandler(log_path, mode="a")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    )
    logging.getLogger().addHandler(file_handler)
    logger.info("Logging to: %s", log_path)

    # ── Step 1: Load logprob matrices ─────────────────────────────────────────
    logger.info("[Step 1] Loading logprob matrices...")
    logprob_matrices, execution_path = load_logprob_matrices(
        h_e1_results_dir=H_E1_RESULTS_DIR,
        h_m2_results_dir=H_M2_RESULTS_DIR,
        sizes=SIZES,
        alignments=ALIGNMENTS,
        device=device,
    )
    logger.info("Execution path: %s, loaded %d models", execution_path, len(logprob_matrices))

    # ── Step 2: Validate shapes ───────────────────────────────────────────────
    logger.info("[Step 2] Validating shapes...")
    expected_n = 10 if smoke_test else N_ITEMS_EXPECTED

    if smoke_test:
        # Subsample for smoke test
        logger.info("Smoke test mode: subsampling to %d items", expected_n)
        logprob_matrices = {
            k: v[:expected_n] for k, v in logprob_matrices.items()
        }

    shape_errors = []
    for model_key, matrix in logprob_matrices.items():
        if matrix.shape != (expected_n, 4):
            shape_errors.append(
                f"{model_key}: got {matrix.shape}, expected ({expected_n}, 4)"
            )

    if shape_errors:
        if not smoke_test:
            raise ValueError(f"Shape validation failed:\n" + "\n".join(shape_errors))
        else:
            logger.warning("Shape warnings (smoke test):\n%s", "\n".join(shape_errors))

    logger.info("Shape validation passed: %d models, each (%d, 4)", len(logprob_matrices), expected_n)

    # ── Step 3: Compute all delta margins ─────────────────────────────────────
    logger.info("[Step 3] Computing delta margins for all 9 pairs...")
    delta_results = compute_all_delta_margins(
        logprob_matrices=logprob_matrices,
        sizes=SIZES,
        alignments=ALIGNMENTS,
        n_bootstrap=N_BOOTSTRAP,
        seed=SEED,
    )
    logger.info("Delta margins computed for %d pairs", len(delta_results))

    # ── Step 4: Gradient ordering test ────────────────────────────────────────
    logger.info("[Step 4] Testing gradient ordering (Wilcoxon)...")
    delta_ppo = [delta_results.get(f"ppo_{s}", (0, 0, 0))[0] for s in SIZES]
    delta_dpo = [delta_results.get(f"dpo_{s}", (0, 0, 0))[0] for s in SIZES]
    delta_sft = [delta_results.get(f"sft_{s}", (0, 0, 0))[0] for s in SIZES]

    ordering_stats = test_gradient_ordering(delta_ppo, delta_dpo, delta_sft)
    logger.info("Ordering stats: %s", ordering_stats)

    # ── Step 5: Verify mechanism activated ────────────────────────────────────
    logger.info("[Step 5] Verifying mechanism activation...")
    mechanism_verified, indicators = verify_mechanism_activated(delta_results)
    logger.info(
        "Mechanism verified: %s, indicators: %s", mechanism_verified, indicators
    )

    # ── Step 6: Evaluate gate ─────────────────────────────────────────────────
    logger.info("[Step 6] Evaluating SHOULD_WORK gate...")
    gate_result, failed_checks, exploration_notes = evaluate_should_work_gate(delta_results)
    logger.info("Gate result: %s", gate_result)
    if failed_checks:
        logger.warning("Failed checks: %s", failed_checks)

    # ── Step 7: Generate figures ──────────────────────────────────────────────
    logger.info("[Step 7] Generating figures...")
    figure_paths = generate_all_figures(
        delta_results=delta_results,
        logprob_matrices=logprob_matrices,
        h_e1_validation_path=H_E1_VALIDATION_PATH,
        figures_dir=H_M2_FIGURES_DIR,
        dpi=FIGURE_DPI,
    )
    logger.info("Figures generated: %d", len(figure_paths))

    # ── Step 8: Generate report, update state, save results ──────────────────
    logger.info("[Step 8] Generating validation report...")

    report_path = generate_validation_report(
        delta_results=delta_results,
        ordering_stats=ordering_stats,
        gate_result=gate_result,
        failed_checks=failed_checks,
        exploration_notes=exploration_notes,
        execution_path=execution_path,
        figure_paths=figure_paths,
        mechanism_indicators=indicators,
        output_path=H_M2_REPORT_PATH,
    )
    logger.info("Validation report written: %s", report_path)

    # Update verification_state.yaml
    if not smoke_test:
        logger.info("Updating verification_state.yaml...")
        write_gate_to_verification_state(
            gate_result=gate_result,
            delta_results=delta_results,
            gate_report_path=report_path,
            verification_state_path=VERIFICATION_STATE_PATH,
        )
        logger.info("verification_state.yaml updated")
    else:
        logger.info("Smoke test: skipping verification_state.yaml update")

    # Save experiment_results.json
    end_time = datetime.now(timezone.utc)
    duration_seconds = (end_time - start_time).total_seconds()

    experiment_results = {
        "hypothesis_id": "h-m2",
        "gate_type": "SHOULD_WORK",
        "gate_result": gate_result,
        "execution_path": execution_path,
        "smoke_test": smoke_test,
        "n_models": len(logprob_matrices),
        "n_items": expected_n,
        "delta_results": {
            k: {"delta_mean": v[0], "ci_lower": v[1], "ci_upper": v[2]}
            for k, v in delta_results.items()
        },
        "ordering_stats": ordering_stats,
        "mechanism_indicators": indicators,
        "gate_result_details": {
            "failed_checks": failed_checks,
            "exploration_notes": exploration_notes,
        },
        "figure_paths": figure_paths,
        "validation_report": report_path,
        "started_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "duration_seconds": duration_seconds,
    }

    os.makedirs(os.path.dirname(H_M2_EXPERIMENT_RESULTS_JSON), exist_ok=True)
    with open(H_M2_EXPERIMENT_RESULTS_JSON, "w") as f:
        json.dump(experiment_results, f, indent=2, default=str)
    logger.info("experiment_results.json saved: %s", H_M2_EXPERIMENT_RESULTS_JSON)

    logger.info("=" * 60)
    logger.info("H-M2 PIPELINE COMPLETE")
    logger.info("Gate: %s", gate_result)
    logger.info("Duration: %.1f seconds", duration_seconds)
    logger.info("=" * 60)

    return {
        "gate_result": gate_result,
        "delta_results": delta_results,
        "figure_paths": figure_paths,
        "execution_path": execution_path,
        "ordering_stats": ordering_stats,
        "mechanism_indicators": indicators,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="H-M2: Pre-Softmax Logit Margin Inflation Analysis"
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run on 10 items only for fast validation",
    )
    parser.add_argument(
        "--device",
        default="cuda",
        help="Device for lm-eval Path B (default: cuda)",
    )
    args = parser.parse_args()

    results = main(smoke_test=args.smoke_test, device=args.device)
    sys.exit(0 if results["gate_result"] == "PASS" else 1)
