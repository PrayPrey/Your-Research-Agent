#!/usr/bin/env python3
"""H-M1 main analysis entry point."""
import logging
import os
import sys

# Setup logging before any imports
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    # 1. Load config
    from config import (
        H_E1_CODE_PATH, H_E1_RESULTS_DIR, RESULTS_DIR, FIGURES_DIR,
        SEED, N_BINS, CLEAN_ECE_H_E1, DELTA_ECE_H_E1, SPLITS, SPLIT_FILE_MAP
    )

    # Inject h-e1 code path for shared utilities
    if H_E1_CODE_PATH not in sys.path:
        sys.path.insert(0, H_E1_CODE_PATH)
    try:
        from evaluation.ece import compute_ece  # noqa: F401
        from results.storage import write_json, write_gate_result  # noqa: F401
        logger.info("H-E1 imports verified from: %s", H_E1_CODE_PATH)
    except ImportError as e:
        logger.error("H-E1 import failed: %s. Check H_E1_CODE_PATH.", e)
        sys.exit(1)

    # Create output dirs
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    # 2. Load H-E1 caches
    from cache_loader import load_all_caches, verify_cache_integrity
    try:
        caches = load_all_caches(H_E1_RESULTS_DIR, SPLITS, SPLIT_FILE_MAP)
    except FileNotFoundError as e:
        logger.error("[FALLBACK] Cache missing: %s. Re-run H-E1 first.", e)
        sys.exit(1)

    # 3. Verify cache integrity
    verify_cache_integrity(caches, expected_counts={
        "advglue_mnli": 121, "anli_r1": 200,
        "anli_r2": 200, "anli_r3": 200, "mnli": 200
    })

    # 4. Build strata + preservation rates
    from stratifier import build_strata, compute_preservation_rate
    strata = {}
    preservation_rates = {}
    for split, cache in caches.items():
        n = len(cache["conf"])
        strata[split] = build_strata(split, n)
        preservation_rates[split] = compute_preservation_rate(strata[split])
        logger.info("[%s] preservation_rate=%.3f n=%d", split, preservation_rates[split], n)

    # 5. ECE analysis
    from ece_analyzer import run_all_strata, check_anli_gradient
    stratum_results = run_all_strata(caches, clean_ece=CLEAN_ECE_H_E1, n_bins=N_BINS)
    gradient_ok = check_anli_gradient(stratum_results)
    logger.info("ANLI gradient check: %s", gradient_ok)

    # 6. Ablations
    import numpy as np
    from ablations import ablation_criterion_sensitivity, ablation_bin_count, ablation_task_scope

    abl_criterion = ablation_criterion_sensitivity(caches, clean_ece=CLEAN_ECE_H_E1, n_bins=N_BINS)
    logger.info("Ablation criterion sensitivity: %s", abl_criterion)

    adv_cache = caches["advglue_mnli"]
    adv_mask = strata["advglue_mnli"]["high_pres_all"]
    abl_bins = ablation_bin_count(adv_cache, mask=adv_mask, bin_counts=(10, 15, 20))
    logger.info("Ablation bin count: %s", abl_bins)

    abl_scope = ablation_task_scope(caches, clean_ece=CLEAN_ECE_H_E1, n_bins=N_BINS)
    logger.info("Ablation task scope: %s", abl_scope)

    # 7. Gate verification
    from gate_verifier import verify_gate
    pres_rate = preservation_rates.get("advglue_mnli", 0.0)
    adv_ece = stratum_results["advglue_mnli"]["ece"]
    gate_passed, indicators = verify_gate(
        preservation_rate=pres_rate,
        stratum_ece=adv_ece,
        clean_ece=CLEAN_ECE_H_E1,
        h_e1_delta=DELTA_ECE_H_E1,
    )
    logger.info("Gate result: passed=%s indicators=%s", gate_passed, indicators)

    if not gate_passed:
        logger.warning(
            "[PIVOT] Gate FAIL — restricting ΔECE claim to AdvGLUE human-verified subset only"
        )

    # 8. Write gate report
    from results_writer import write_gate_report, write_main_results, write_ablation_results
    write_gate_report(passed=gate_passed, indicators=indicators, out_dir=RESULTS_DIR)

    # 9. Visualizations
    from visualizer import (
        plot_preservation_rate, plot_stratum_ece,
        plot_anli_gradient, plot_reliability_diagrams
    )
    plot_preservation_rate(
        preservation_rates,
        out_path=f"{FIGURES_DIR}/preservation_rate_by_benchmark.png"
    )
    plot_stratum_ece(
        stratum_results,
        out_path=f"{FIGURES_DIR}/stratum_ece_comparison.png",
        clean_ece=CLEAN_ECE_H_E1
    )
    plot_anli_gradient(stratum_results, out_path=f"{FIGURES_DIR}/anli_gradient.png")
    plot_reliability_diagrams(
        caches, strata,
        out_path=f"{FIGURES_DIR}/reliability_diagrams.png",
        n_bins=N_BINS
    )

    # 10. Write results
    write_main_results(stratum_results, out_dir=RESULTS_DIR)
    write_ablation_results(
        {"criterion": abl_criterion, "bin_count": abl_bins, "task_scope": abl_scope},
        out_dir=RESULTS_DIR,
    )
    logger.info("[DONE] H-M1 analysis complete. gate_passed=%s", gate_passed)

    # Summary print for experiment.log detection
    print(f"Label preservation rate: {pres_rate:.4f}")
    print(f"High-preservation stratum ECE (advglue_mnli): {adv_ece:.4f}")
    print(f"ΔECE: {adv_ece - CLEAN_ECE_H_E1:.4f}")
    print(f"ANLI gradient check: {gradient_ok}")
    print(f"Gate passed: {gate_passed}")
    for sp, res in stratum_results.items():
        print(f"  {sp}: ECE={res['ece']:.4f} ΔECE={res['delta_ece']:.4f} n={res['n']}")
    print("EXPERIMENT COMPLETE (H-M1 analysis)")


if __name__ == "__main__":
    main()
