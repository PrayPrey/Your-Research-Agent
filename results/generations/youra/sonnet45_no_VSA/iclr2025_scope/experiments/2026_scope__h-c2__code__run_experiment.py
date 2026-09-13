"""
Experiment Runner for H-C2
Runs baseline comparison and contract validation
"""

import json
import time
import numpy as np
from dataclasses import asdict
from typing import List, Dict, Any

from config import CONFIG
from test_cases import prepare_test_set
from framework_adapters import PyTorchAdapter
from contracts import dtype_preserved, shape_consistent, numerical_tolerance
from validator import ContractValidator


def run_baseline_validation(test_case) -> bool:
    """Run end-to-end baseline validation."""
    try:
        src_adapter = PyTorchAdapter(device=CONFIG["device"])
        tgt_adapter = PyTorchAdapter(device=CONFIG["device"])

        # Run inference on both models
        for test_input in test_case.test_inputs:
            src_output = src_adapter.run_inference(test_case.src_model, test_input)
            tgt_output = tgt_adapter.run_inference(test_case.tgt_model, test_input)

            # Compare outputs with tolerance
            if not np.allclose(src_output, tgt_output,
                              rtol=CONFIG["default_rtol"],
                              atol=CONFIG["default_atol"]):
                return True  # Defect detected

        return False  # No defect detected

    except Exception:
        return False  # Failed to detect


def run_h_c2_validation(test_case) -> Dict[str, Any]:
    """Run H-C2 contract validation."""
    src_adapter = PyTorchAdapter(device=CONFIG["device"])
    tgt_adapter = PyTorchAdapter(device=CONFIG["device"])

    # Select enabled contracts
    contracts = []
    if CONFIG["dtype_preservation_enabled"]:
        contracts.append(dtype_preserved)
    if CONFIG["shape_consistency_enabled"]:
        contracts.append(shape_consistent)
    if CONFIG["numerical_tolerance_enabled"]:
        contracts.append(numerical_tolerance)

    # Run validation
    validator = ContractValidator(timeout=CONFIG["timeout_per_model"])
    report = validator.validate_conversion(
        test_case.src_model,
        test_case.tgt_model,
        test_case.test_inputs,
        contracts,
        src_adapter,
        tgt_adapter
    )

    return {
        "detected": not report.passed,
        "validation_time": report.validation_time,
        "contract_results": report.contract_results,
        "defects": [asdict(d) for d in report.defects_detected]
    }


def main():
    """Run full experiment."""
    print("=" * 80)
    print("H-C2 Cross-Framework Contract Validation Experiment")
    print("=" * 80)

    # Prepare test set
    print("\n[1/4] Preparing test set...")
    _, test_cases = prepare_test_set(
        num_samples=CONFIG["synthetic_samples"],
        train_ratio=CONFIG["train_test_split"],
        seed=CONFIG["seed"]
    )
    print(f"  Test set size: {len(test_cases)}")

    # Count defect types
    defect_counts = {}
    for tc in test_cases:
        dt = tc.defect_type or "valid"
        defect_counts[dt] = defect_counts.get(dt, 0) + 1
    print(f"  Defect distribution: {defect_counts}")

    # Run experiments
    print("\n[2/4] Running baseline validation...")
    results = []
    baseline_start = time.time()

    for i, test_case in enumerate(test_cases):
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{len(test_cases)}")

        # Baseline
        baseline_detected = run_baseline_validation(test_case)

        # H-C2
        h_c2_result = run_h_c2_validation(test_case)

        results.append({
            "test_id": test_case.case_id,
            "framework_pair": f"{test_case.source_framework}→{test_case.target_framework}",
            "defect_type": test_case.defect_type,
            "ground_truth": test_case.ground_truth_label,
            "baseline_detected": baseline_detected,
            "h_c2_detected": h_c2_result["detected"],
            "h_c2_validation_time": h_c2_result["validation_time"],
            "contract_results": h_c2_result["contract_results"],
            "defects": h_c2_result["defects"]
        })

    baseline_time = time.time() - baseline_start
    print(f"  Baseline execution time: {baseline_time:.2f}s")

    # Calculate metrics
    print("\n[3/4] Calculating metrics...")
    total_tests = len(results)
    total_defects = sum(1 for r in results if r["ground_truth"] == "defect")
    total_valid = sum(1 for r in results if r["ground_truth"] == "valid")

    # Detection rates
    baseline_tp = sum(1 for r in results if r["ground_truth"] == "defect" and r["baseline_detected"])
    h_c2_tp = sum(1 for r in results if r["ground_truth"] == "defect" and r["h_c2_detected"])

    baseline_detection_rate = baseline_tp / total_defects if total_defects > 0 else 0.0
    h_c2_detection_rate = h_c2_tp / total_defects if total_defects > 0 else 0.0

    # False positive rates
    baseline_fp = sum(1 for r in results if r["ground_truth"] == "valid" and r["baseline_detected"])
    h_c2_fp = sum(1 for r in results if r["ground_truth"] == "valid" and r["h_c2_detected"])

    baseline_fpr = baseline_fp / total_valid if total_valid > 0 else 0.0
    h_c2_fpr = h_c2_fp / total_valid if total_valid > 0 else 0.0

    # Precision and F1
    h_c2_precision = h_c2_tp / (h_c2_tp + h_c2_fp) if (h_c2_tp + h_c2_fp) > 0 else 0.0
    h_c2_recall = h_c2_detection_rate
    h_c2_f1 = 2 * (h_c2_precision * h_c2_recall) / (h_c2_precision + h_c2_recall) if (h_c2_precision + h_c2_recall) > 0 else 0.0

    # Validation time statistics
    h_c2_times = [r["h_c2_validation_time"] for r in results]
    avg_validation_time = np.mean(h_c2_times)
    median_validation_time = np.median(h_c2_times)
    p95_validation_time = np.percentile(h_c2_times, 95)

    # Per-contract detection
    contract_detections = {}
    for contract_name in ["dtype_preserved", "shape_consistent", "numerical_tolerance"]:
        contract_tp = sum(1 for r in results
                         if r["ground_truth"] == "defect"
                         and contract_name in r["contract_results"]
                         and not r["contract_results"][contract_name]["passed"])
        contract_detections[contract_name] = contract_tp / total_defects if total_defects > 0 else 0.0

    # Save results
    print("\n[4/4] Saving results...")
    output = {
        "experiment_id": "h-c2-poc",
        "config": CONFIG,
        "test_results": results,
        "summary": {
            "total_tests": total_tests,
            "total_defects": total_defects,
            "total_valid": total_valid,
            "baseline_detection_rate": baseline_detection_rate,
            "h_c2_detection_rate": h_c2_detection_rate,
            "baseline_fpr": baseline_fpr,
            "h_c2_fpr": h_c2_fpr,
            "h_c2_precision": h_c2_precision,
            "h_c2_recall": h_c2_recall,
            "h_c2_f1_score": h_c2_f1,
            "avg_validation_time": avg_validation_time,
            "median_validation_time": median_validation_time,
            "p95_validation_time": p95_validation_time,
            "per_contract_detection": contract_detections
        }
    }

    with open(CONFIG["results_path"], "w") as f:
        json.dump(output, f, indent=2)

    print(f"  Results saved to: {CONFIG['results_path']}")

    # Print summary
    print("\n" + "=" * 80)
    print("EXPERIMENT RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests} ({total_defects} defects, {total_valid} valid)")
    print(f"\nDetection Rates:")
    print(f"  Baseline: {baseline_detection_rate:.1%} ({baseline_tp}/{total_defects})")
    print(f"  H-C2:     {h_c2_detection_rate:.1%} ({h_c2_tp}/{total_defects})")
    print(f"  Improvement: {(h_c2_detection_rate - baseline_detection_rate)*100:.1f}pp")
    print(f"\nFalse Positive Rates:")
    print(f"  Baseline: {baseline_fpr:.1%} ({baseline_fp}/{total_valid})")
    print(f"  H-C2:     {h_c2_fpr:.1%} ({h_c2_fp}/{total_valid})")
    print(f"\nH-C2 Quality Metrics:")
    print(f"  Precision: {h_c2_precision:.1%}")
    print(f"  Recall:    {h_c2_recall:.1%}")
    print(f"  F1 Score:  {h_c2_f1:.3f}")
    print(f"\nValidation Time:")
    print(f"  Mean:   {avg_validation_time:.3f}s")
    print(f"  Median: {median_validation_time:.3f}s")
    print(f"  P95:    {p95_validation_time:.3f}s")
    print(f"\nPer-Contract Detection:")
    for contract_name, rate in contract_detections.items():
        print(f"  {contract_name}: {rate:.1%}")

    # Gate verdict
    print("\n" + "=" * 80)
    print("SHOULD_WORK GATE EVALUATION")
    print("=" * 80)
    gate_passed = (
        h_c2_detection_rate >= CONFIG["detection_rate_threshold"]
        and h_c2_fpr < CONFIG["false_positive_threshold"]
        and avg_validation_time < 5.0
    )

    print(f"Detection Rate: {h_c2_detection_rate:.1%} (threshold: {CONFIG['detection_rate_threshold']:.0%}) - {'✓ PASS' if h_c2_detection_rate >= CONFIG['detection_rate_threshold'] else '✗ FAIL'}")
    print(f"False Positive Rate: {h_c2_fpr:.1%} (threshold: <{CONFIG['false_positive_threshold']:.0%}) - {'✓ PASS' if h_c2_fpr < CONFIG['false_positive_threshold'] else '✗ FAIL'}")
    print(f"Validation Time: {avg_validation_time:.3f}s (threshold: <5s) - {'✓ PASS' if avg_validation_time < 5.0 else '✗ FAIL'}")

    if gate_passed:
        print("\n🎉 SHOULD_WORK GATE: PASS")
    else:
        if h_c2_detection_rate >= 0.50:
            print("\n⚠️  SHOULD_WORK GATE: PARTIAL PASS (50-70% detection)")
        else:
            print("\n❌ SHOULD_WORK GATE: FAIL")

    return 0


if __name__ == "__main__":
    exit(main())
