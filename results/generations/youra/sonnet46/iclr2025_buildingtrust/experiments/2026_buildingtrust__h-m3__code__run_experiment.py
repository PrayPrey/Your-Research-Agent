"""
run_experiment.py — H-M3 Mechanism Discrimination
Orchestration entry point: full pipeline from data loading to report generation.
"""
import argparse
import logging
import os
import sys
from pathlib import Path

# Ensure h-m3/code is on path
_CODE_DIR = Path(__file__).parent.resolve()
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

from config import (
    H_E1_RESULTS_DIR,
    H_M3_RESULTS_DIR,
    H_M3_TRUTHFULQA_DIR,
    H_M3_FIGURES_DIR,
    H_M3_REPORT_PATH,
    H_M3_EXPERIMENT_RESULTS_JSON,
    VERIFICATION_STATE_PATH,
    SIZES,
    ALIGNMENTS,
    N_BOOTSTRAP,
    SEED,
    N_BINS,
    HF_MODEL_IDS,
    H1_RHO_THRESHOLD,
    H2_RHO_THRESHOLD,
    FIGURE_DPI,
)
from load_data import load_logprob_matrices, load_labels
from spearman_analysis import compute_all_spearman_results, assess_h1_h2_gate
from argmax_partition import compute_all_partition_results
from truthfulqa_analysis import compute_truthfulqa_ece_all_models, assess_h3_diagnostic
from mechanism_report import (
    determine_dominant_mechanism,
    write_validation_report,
    update_verification_state,
    save_experiment_results,
)
from visualization import generate_all_figures

import numpy as np
from scipy.special import softmax

# Add h-e1/code to path for compute_ece
_H_E1_CODE_DIR = str(_CODE_DIR.parent.parent / "h-e1" / "code")
if _H_E1_CODE_DIR not in sys.path:
    sys.path.insert(0, _H_E1_CODE_DIR)
from calibration_analysis import compute_ece  # noqa: E402


def _compute_mmlu_ece(logprob_matrices: dict, labels: dict, sizes: list, alignments: list, n_bins: int) -> dict:
    """Compute MMLU ECE for all 12 models."""
    ece_results = {}
    all_keys = [f"pythia-{s}-base" for s in sizes] + [
        f"pythia-{s}-{a}" for s in sizes for a in alignments
    ]
    for model_key in all_keys:
        lp = logprob_matrices.get(model_key)
        if lp is None:
            continue
        size = model_key.split("-")[1]
        base_key = f"pythia-{size}-base"
        y_true = labels.get(base_key)
        if y_true is None:
            continue
        n = min(lp.shape[0], len(y_true))
        probs = softmax(lp[:n], axis=1)
        ece = compute_ece(y_true[:n], probs, n_bins=n_bins)
        ece_results[model_key] = float(ece)
    return ece_results


def main(device: str = "cuda", smoke_test: bool = False) -> None:
    """Orchestrate full H-M3 experiment pipeline."""
    # Setup logging
    os.makedirs(H_M3_RESULTS_DIR, exist_ok=True)
    log_path = os.path.join(str(_CODE_DIR), "experiment.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path),
        ],
    )
    logger = logging.getLogger(__name__)
    logger.info("=== H-M3 Experiment Start === device=%s smoke_test=%s", device, smoke_test)

    sizes = SIZES[:2] if smoke_test else SIZES
    alignments = ALIGNMENTS

    # Step 1: Load MMLU logprob matrices
    logger.info("Step 1: Loading MMLU logprob matrices")
    logprob_matrices, exec_path = load_logprob_matrices(
        h_e1_results_dir=H_E1_RESULTS_DIR,
        h_m3_results_dir=H_M3_RESULTS_DIR,
        sizes=sizes,
        alignments=alignments,
        device=device,
    )
    logger.info("Loaded via %s: %d models", exec_path, len(logprob_matrices))

    # smoke_test: limit to first 100 items
    if smoke_test:
        logprob_matrices = {k: v[:100] for k, v in logprob_matrices.items()}
        logger.info("Smoke test: truncated to 100 items per model")

    # Step 2: Load labels
    logger.info("Step 2: Loading labels")
    labels = load_labels(H_E1_RESULTS_DIR, sizes)
    if smoke_test:
        labels = {k: v[:100] for k, v in labels.items()}

    # Step 3: Compute Spearman rho for all 9 pairs
    logger.info("Step 3: Computing Spearman rho")
    spearman_results = compute_all_spearman_results(logprob_matrices, sizes, alignments)

    # Step 4: Assess H1/H2 gate
    logger.info("Step 4: Assessing H1/H2 gate")
    spearman_gate = assess_h1_h2_gate(
        spearman_results, h1_threshold=H1_RHO_THRESHOLD, h2_threshold=H2_RHO_THRESHOLD
    )
    logger.info("Gate: gate_pass=%s n_h1_pass=%d n_h2_flag=%d",
                spearman_gate["gate_pass"], spearman_gate["n_h1_pass"], spearman_gate["n_h2_flag"])

    # Step 5: Compute shared/changed-argmax Brier partition
    logger.info("Step 5: Computing argmax partition + Brier subsets")
    n_boot = 10 if smoke_test else N_BOOTSTRAP
    partition_results = compute_all_partition_results(
        logprob_matrices, labels, sizes, alignments, n_bootstrap=n_boot, seed=SEED
    )

    # Step 6: Compute MMLU ECE (for H3 comparison)
    logger.info("Step 6: Computing MMLU ECE")
    mmlu_ece_results = _compute_mmlu_ece(logprob_matrices, labels, sizes, alignments, N_BINS)

    # Step 7: Run/load TruthfulQA MC1 ECE
    logger.info("Step 7: Computing TruthfulQA MC1 ECE")
    os.makedirs(H_M3_TRUTHFULQA_DIR, exist_ok=True)
    tqa_ece_results = compute_truthfulqa_ece_all_models(
        tqa_results_dir=H_M3_TRUTHFULQA_DIR,
        h_e1_results_dir=H_E1_RESULTS_DIR,
        sizes=sizes,
        alignments=alignments,
        hf_model_ids=HF_MODEL_IDS,
        device=device,
        n_bins=N_BINS,
        limit=5 if smoke_test else None,
    )

    # Assess H3 diagnostic
    h3_diagnostic = assess_h3_diagnostic(tqa_ece_results, mmlu_ece_results, sizes, alignments)
    logger.info("H3 diagnostic: h3_flag=%s", h3_diagnostic["h3_flag"])

    # Step 8: Determine dominant mechanism
    logger.info("Step 8: Determining dominant mechanism")
    mechanism_result = determine_dominant_mechanism(
        spearman_gate, partition_results, h3_diagnostic, sizes, alignments
    )
    logger.info("Dominant mechanism: %s", mechanism_result["dominant"])

    # Step 9: Generate 5 figures
    logger.info("Step 9: Generating figures")
    os.makedirs(H_M3_FIGURES_DIR, exist_ok=True)
    figure_paths = generate_all_figures(
        spearman_results=spearman_results,
        partition_results=partition_results,
        tqa_ece_results=tqa_ece_results,
        mmlu_ece_results=mmlu_ece_results,
        figures_dir=H_M3_FIGURES_DIR,
        dpi=FIGURE_DPI,
    )
    logger.info("Generated %d figures", len(figure_paths))

    # Step 10: Write validation report
    logger.info("Step 10: Writing validation report")
    write_validation_report(
        mechanism_result=mechanism_result,
        spearman_results=spearman_results,
        partition_results=partition_results,
        tqa_ece_results=tqa_ece_results,
        output_path=H_M3_REPORT_PATH,
    )

    # Step 11: Update verification_state.yaml
    logger.info("Step 11: Updating verification_state.yaml")
    key_metrics = {
        "mean_rho_min": min(
            (r["mean_rho"] for r in spearman_results.values()), default=float("nan")
        ),
        "cohens_d_shared_max": max(
            (abs(r.get("cohens_d_shared", 0.0)) for r in partition_results.values()), default=float("nan")
        ),
        "h3_flag": h3_diagnostic["h3_flag"],
    }
    update_verification_state(
        state_path=VERIFICATION_STATE_PATH,
        gate_pass=mechanism_result["gate_pass"],
        dominant_mechanism=mechanism_result["dominant"],
        key_metrics=key_metrics,
    )

    # Step 12: Save experiment results
    logger.info("Step 12: Saving experiment results JSON")
    all_results = {
        "spearman_results": {
            k: {
                "mean_rho": v["mean_rho"],
                "h1_pass": v["h1_pass"],
                "h2_flag": v["h2_flag"],
            }
            for k, v in spearman_results.items()
        },
        "spearman_gate": spearman_gate,
        "partition_results": {
            k: {kk: vv for kk, vv in v.items() if kk not in ("shared_mask", "changed_mask")}
            for k, v in partition_results.items()
        },
        "mmlu_ece_results": mmlu_ece_results,
        "tqa_ece_results": tqa_ece_results,
        "h3_diagnostic": h3_diagnostic,
        "mechanism_result": mechanism_result,
        "execution_path": exec_path,
        "figure_paths": figure_paths,
    }
    save_experiment_results(all_results, H_M3_EXPERIMENT_RESULTS_JSON)

    logger.info("=== H-M3 Experiment Complete === dominant=%s gate_pass=%s",
                mechanism_result["dominant"], mechanism_result["gate_pass"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-M3 Mechanism Discrimination Experiment")
    parser.add_argument("--device", default="cuda", help="Device for lm-eval (default: cuda)")
    parser.add_argument("--smoke-test", action="store_true", help="Run with limited data for testing")
    args = parser.parse_args()
    main(device=args.device, smoke_test=args.smoke_test)
