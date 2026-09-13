from __future__ import annotations

import logging
import sys
from pathlib import Path

from scipy.stats import spearmanr

import config as C
from data_loader import load_score_matrix, load_score_matrix_t07
from analyzers import (
    compute_internal_consistency,
    compute_partial_corr_bca,
    compute_confound_magnitude,
    compute_discriminant_validity,
    compute_decoding_invariance,
    evaluate_gate,
)
from visualizer import (
    plot_gate_bar,
    plot_raw_vs_partial,
    plot_ece_brier_scatter,
    plot_discriminant_validity,
    plot_decoding_invariance,
)
from reporter import write_results_json, write_validation_md

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def main() -> dict:
    """Orchestrate full H-M1 pipeline. Returns gate_eval dict."""
    Path(C.RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    Path(C.FIGURES_DIR).mkdir(parents=True, exist_ok=True)

    # 1. Load data
    log.info("Loading score matrix from %s", C.SCORE_MATRIX_PATH)
    df_greedy = load_score_matrix(C.SCORE_MATRIX_PATH)
    log.info("Loaded %d models", len(df_greedy))

    df_t07 = load_score_matrix_t07(C.SCORE_MATRIX_T07_PATH)
    if len(df_t07) == 0:
        log.warning("T=0.7 score matrix not found — decoding invariance test will be skipped")
    else:
        log.info("Loaded T=0.7 score matrix (%d models)", len(df_t07))

    # 2. Statistical analyses
    log.info("Computing ECE-Brier internal consistency...")
    internal_result = compute_internal_consistency(
        df_greedy, C.INTERNAL_X, C.INTERNAL_Y, C.N_BOOTSTRAP, C.BOOTSTRAP_SEED
    )
    log.info("  rho(ECE, Brier) = %.4f [%s]",
             internal_result["rho"], "PASS" if internal_result["passes_threshold"] else "FAIL")

    log.info("Computing primary partial correlation (PRIMARY GATE)...")
    primary_result = compute_partial_corr_bca(
        df_greedy, C.PRIMARY_X, C.PRIMARY_Y, C.COVARIATE, C.N_BOOTSTRAP, C.BOOTSTRAP_SEED
    )
    log.info("  partial_rho(ECE, TruthfulQA%% | MMLU) = %.4f  CI=[%.4f, %.4f]  [%s]",
             primary_result["rho_partial"],
             primary_result["bca_ci_low"],
             primary_result["bca_ci_high"],
             "PASS" if primary_result["passes_threshold"] else "FAIL")

    raw_rho = float(spearmanr(df_greedy[C.PRIMARY_X], df_greedy[C.PRIMARY_Y]).statistic)
    log.info("  raw_rho(ECE, TruthfulQA%%) = %.4f", raw_rho)

    confound_result = compute_confound_magnitude(raw_rho, primary_result["rho_partial"])
    log.info("  survival_fraction = %.4f  (%s)",
             confound_result.get("survival_fraction", float("nan")),
             confound_result.get("interpretation", ""))

    log.info("Computing discriminant validity...")
    discriminant_result = compute_discriminant_validity(
        df_greedy, C.PRIMARY_X, C.DISCRIMINANT_Y, C.COVARIATE, C.N_BOOTSTRAP, C.BOOTSTRAP_SEED
    )
    log.info("  partial_rho(ECE, HumanEval | MMLU) = %.4f [%s]",
             discriminant_result["rho_partial"],
             "PASS" if discriminant_result["passes_threshold"] else "FAIL")

    log.info("Computing decoding invariance...")
    invariance_result = compute_decoding_invariance(
        df_greedy, df_t07, C.PRIMARY_X, C.PRIMARY_Y, C.COVARIATE, C.N_BOOTSTRAP, C.BOOTSTRAP_SEED
    )
    if invariance_result["skipped"]:
        log.info("  Decoding invariance: SKIPPED")
    else:
        log.info("  T=0.7 partial_rho = %.4f [%s]",
                 invariance_result["rho_t07"],
                 "PASS" if invariance_result["passes_threshold"] else "FAIL")

    # 3. Gate evaluation
    gate_pass = evaluate_gate(primary_result, C.PRIMARY_THRESHOLD)
    log.info("=" * 60)
    log.info("PRIMARY GATE (MUST_WORK): %s", "PASS" if gate_pass else "FAIL")
    log.info("  partial_rho = %.4f  threshold = %.2f  ci_excludes_zero = %s",
             primary_result["rho_partial"], C.PRIMARY_THRESHOLD,
             primary_result["ci_excludes_zero"])
    log.info("=" * 60)

    # 4. Visualization
    figures_dir = Path(C.FIGURES_DIR)
    log.info("Generating figures...")
    plot_gate_bar(primary_result, C.PRIMARY_THRESHOLD, figures_dir)
    plot_raw_vs_partial(raw_rho, primary_result["rho_partial"], confound_result, figures_dir)
    plot_ece_brier_scatter(df_greedy, internal_result, figures_dir)
    plot_discriminant_validity(primary_result, discriminant_result, figures_dir)
    plot_decoding_invariance(invariance_result, figures_dir)
    log.info("5 figures saved to %s", C.FIGURES_DIR)

    # 5. Report
    results_path = Path(C.RESULTS_DIR) / "hm1_results.json"
    validation_path = Path(__file__).parent.parent / "04_validation.md"

    write_results_json(
        internal_result, primary_result, confound_result,
        discriminant_result, invariance_result, gate_pass, results_path
    )
    write_validation_md(
        internal_result, primary_result, confound_result,
        discriminant_result, invariance_result, gate_pass, validation_path
    )
    log.info("Results written to %s", results_path)
    log.info("Validation report written to %s", validation_path)

    return {
        "PASS": gate_pass,
        "primary_result": primary_result,
        "internal_result": internal_result,
        "confound_result": confound_result,
        "discriminant_result": discriminant_result,
        "invariance_result": invariance_result,
    }


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result["PASS"] else 1)
