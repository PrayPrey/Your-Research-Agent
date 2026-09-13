"""
Main experiment runner for HalluConform: Calibration-Aware Conformal Prediction
for Hallucination Detection in LLMs.

Steps:
1. Load data (TriviaQA + MedMCQA)
2. Generate model outputs and extract internal signals (single forward pass)
3. Calibrate HalluConform and baselines on calibration split
4. Evaluate all methods on test split
5. Generate figures and save results
"""

import os
import sys
import json
import logging
import time
from datetime import datetime

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOG_FILE = os.path.join(OUTPUT_DIR, "log.txt")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def main():
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("HalluConform Experiment")
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)

    # ---- 1. Load data ----
    logger.info("\n[Step 1] Loading datasets...")
    from data import load_all_data, split_data
    all_samples = load_all_data(seed=42)
    cal_samples, test_samples = split_data(all_samples, cal_ratio=0.5, seed=42)
    logger.info(f"Calibration: {len(cal_samples)}, Test: {len(test_samples)}")

    # ---- 2. Load model and collect signals ----
    logger.info("\n[Step 2] Loading model and generating outputs with internal signals...")
    from model import get_model_and_tokenizer, collect_signals_for_dataset
    model, tokenizer = get_model_and_tokenizer()

    logger.info("Processing calibration set...")
    cal_results = collect_signals_for_dataset(cal_samples, model, tokenizer)
    logger.info("Processing test set...")
    test_results = collect_signals_for_dataset(test_samples, model, tokenizer)

    # Save raw signal data
    with open(os.path.join(OUTPUT_DIR, "cal_signals.json"), "w") as f:
        json.dump(cal_results, f, indent=2)
    with open(os.path.join(OUTPUT_DIR, "test_signals.json"), "w") as f:
        json.dump(test_results, f, indent=2)

    cal_accuracy = sum(r["correct"] for r in cal_results) / len(cal_results)
    test_accuracy = sum(r["correct"] for r in test_results) / len(test_results)
    logger.info(f"Calibration accuracy: {cal_accuracy:.3f}")
    logger.info(f"Test accuracy: {test_accuracy:.3f}")
    logger.info(f"Test hallucination rate: {1 - test_accuracy:.3f}")

    # ---- 3. Calibrate methods ----
    logger.info("\n[Step 3] Calibrating HalluConform and baseline methods...")
    from uncertainty import (
        HalluConform, EntropyThreshold, MaxProbThreshold, LengthNormalizedEntropy
    )

    # HalluConform (proposed method)
    hc = HalluConform(alpha=0.1, use_adaptive=True)
    hc.calibrate(cal_results)
    logger.info(f"HalluConform threshold: {hc.threshold_:.4f}")
    logger.info(f"Learned weights: {hc.weights_}")

    # Baselines
    entropy_baseline = EntropyThreshold()
    entropy_baseline.calibrate(cal_results)

    maxprob_baseline = MaxProbThreshold()
    maxprob_baseline.calibrate(cal_results)

    lne_baseline = LengthNormalizedEntropy()
    lne_baseline.calibrate(cal_results)

    # ---- 4. Evaluate all methods ----
    logger.info("\n[Step 4] Evaluating all methods on test set...")
    methods = {
        "HalluConform": hc,
        "EntropyThreshold": entropy_baseline,
        "MaxProbThreshold": maxprob_baseline,
        "LengthNormEntropy": lne_baseline,
    }

    all_metrics = {}
    all_preds = {}
    for name, method in methods.items():
        metrics, preds = method.evaluate(test_results)
        all_metrics[name] = metrics
        all_preds[name] = preds
        logger.info(
            f"  {name}: AUROC={metrics['auroc']:.3f}, AUPRC={metrics['auprc']:.3f}, "
            f"F1={metrics['f1']:.3f}, FPR={metrics['fpr']:.3f}, FNR={metrics['fnr']:.3f}"
        )

    # Coverage verification
    logger.info("\n[Step 5] Verifying conformal prediction coverage guarantees...")
    from evaluation import evaluate_coverage_by_alpha, evaluate_per_domain, compute_signal_importance
    coverage_data = evaluate_coverage_by_alpha(cal_results, test_results, hc)

    # Per-domain evaluation
    logger.info("\n[Step 6] Per-domain evaluation...")
    domain_metrics_by_method = {}
    for name, method in methods.items():
        preds = all_preds[name]
        domain_metrics_by_method[name] = evaluate_per_domain(test_results, preds)

    # Signal importance
    signal_importance = compute_signal_importance(hc)
    logger.info(f"Signal importance: {signal_importance}")

    # ---- 5. Save results ----
    logger.info("\n[Step 7] Saving results...")
    results = {
        "model": "Qwen/Qwen3-0.6B",
        "n_calibration": len(cal_results),
        "n_test": len(test_results),
        "cal_accuracy": cal_accuracy,
        "test_accuracy": test_accuracy,
        "test_hallucination_rate": 1 - test_accuracy,
        "method_metrics": all_metrics,
        "coverage_verification": coverage_data,
        "domain_metrics": domain_metrics_by_method,
        "signal_importance": signal_importance,
        "halluconform_threshold": float(hc.threshold_),
        "halluconform_weights": [float(w) for w in hc.weights_],
    }
    with open(os.path.join(OUTPUT_DIR, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {OUTPUT_DIR}/results.json")

    # ---- 6. Generate figures ----
    logger.info("\n[Step 8] Generating figures...")
    from visualization import (
        plot_nonconformity_distribution,
        plot_roc_curves,
        plot_pr_curves,
        plot_method_comparison,
        plot_coverage_verification,
        plot_domain_performance,
        plot_signal_importance,
        plot_fpr_fnr_comparison,
        plot_adaptive_threshold,
    )

    plot_nonconformity_distribution(
        cal_results, hc,
        os.path.join(OUTPUT_DIR, "nonconformity_distribution.png")
    )
    plot_roc_curves(
        all_preds, test_results,
        os.path.join(OUTPUT_DIR, "roc_curves.png")
    )
    plot_pr_curves(
        all_preds, test_results,
        os.path.join(OUTPUT_DIR, "pr_curves.png")
    )
    plot_method_comparison(
        all_metrics,
        os.path.join(OUTPUT_DIR, "method_comparison.png")
    )
    plot_coverage_verification(
        coverage_data,
        os.path.join(OUTPUT_DIR, "coverage_verification.png")
    )
    plot_domain_performance(
        domain_metrics_by_method,
        os.path.join(OUTPUT_DIR, "domain_performance.png")
    )
    plot_signal_importance(
        signal_importance,
        os.path.join(OUTPUT_DIR, "signal_importance.png")
    )
    plot_fpr_fnr_comparison(
        all_metrics,
        os.path.join(OUTPUT_DIR, "fpr_fnr_comparison.png")
    )
    plot_adaptive_threshold(
        test_results, hc,
        os.path.join(OUTPUT_DIR, "adaptive_threshold.png")
    )

    elapsed = time.time() - start_time
    logger.info(f"\nTotal runtime: {elapsed/60:.1f} minutes")
    logger.info("Experiment completed successfully.")
    logger.info(f"Outputs saved to: {OUTPUT_DIR}")

    # Print summary table
    logger.info("\n" + "=" * 70)
    logger.info("RESULTS SUMMARY")
    logger.info("=" * 70)
    logger.info(f"{'Method':<25} {'AUROC':>8} {'AUPRC':>8} {'F1':>8} {'FPR':>8} {'FNR':>8}")
    logger.info("-" * 70)
    for name, metrics in all_metrics.items():
        logger.info(
            f"{name:<25} {metrics['auroc']:>8.3f} {metrics['auprc']:>8.3f} "
            f"{metrics['f1']:>8.3f} {metrics['fpr']:>8.3f} {metrics['fnr']:>8.3f}"
        )
    logger.info("=" * 70)

    return results


if __name__ == "__main__":
    main()
