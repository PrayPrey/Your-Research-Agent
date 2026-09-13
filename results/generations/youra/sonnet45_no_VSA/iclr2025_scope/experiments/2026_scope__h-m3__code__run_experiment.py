"""
Main experiment script for H-M3: Composition-Level Contract Validation
Demonstrates cross-library defect detection at import/setup time
"""
import torch
import json
import time
from datetime import datetime
from typing import Dict, List
from test_cases import load_all_test_cases, DefectTestCase
from composition_validator import (
    DeviceConsistencyViolation,
    DtypeConsistencyViolation,
    LayoutConsistencyViolation
)


def run_baseline(test_case: DefectTestCase) -> Dict:
    """Run test WITHOUT composition contracts (baseline).

    Returns:
        dict with 'detected', 'detection_stage', 'error_message'
    """
    try:
        result = test_case.setup_func()

        # No contract validation in baseline - defects only caught at runtime
        return {
            'detected': False,
            'detection_stage': 'none',
            'error_message': None
        }

    except (RuntimeError, TypeError, ValueError) as e:
        # Runtime detection (PyTorch's built-in checks)
        error_str = str(e)
        if 'device' in error_str.lower() or 'cuda' in error_str.lower():
            return {
                'detected': True,
                'detection_stage': 'runtime',
                'error_message': error_str[:200]
            }
        elif 'dtype' in error_str.lower() or 'type' in error_str.lower():
            return {
                'detected': True,
                'detection_stage': 'runtime',
                'error_message': error_str[:200]
            }
        else:
            return {
                'detected': True,
                'detection_stage': 'runtime',
                'error_message': error_str[:200]
            }

    except Exception as e:
        return {
            'detected': False,
            'detection_stage': 'none',
            'error_message': f"Unexpected: {str(e)[:100]}"
        }


def run_with_contracts(test_case: DefectTestCase) -> Dict:
    """Run test WITH composition contracts (proposed).

    Returns:
        dict with 'detected', 'detection_stage', 'detection_time', 'error_message'
    """
    start_time = time.time()

    try:
        result = test_case.setup_func()
        detection_time = time.time() - start_time

        # No violation detected
        return {
            'detected': False,
            'detection_stage': 'none',
            'detection_time': detection_time,
            'error_message': None
        }

    except (DeviceConsistencyViolation, DtypeConsistencyViolation, LayoutConsistencyViolation) as e:
        detection_time = time.time() - start_time

        # Contract violation detected at composition level
        return {
            'detected': True,
            'detection_stage': 'composition',  # Earlier than runtime
            'detection_time': detection_time,
            'error_message': str(e)[:200]
        }

    except (RuntimeError, TypeError, ValueError) as e:
        detection_time = time.time() - start_time

        # Fallback runtime detection
        return {
            'detected': True,
            'detection_stage': 'runtime',
            'detection_time': detection_time,
            'error_message': str(e)[:200]
        }

    except Exception as e:
        detection_time = time.time() - start_time

        return {
            'detected': False,
            'detection_stage': 'none',
            'detection_time': detection_time,
            'error_message': f"Unexpected: {str(e)[:100]}"
        }


def main() -> int:
    """Execute experiment: baseline vs proposed comparison."""
    print("=" * 80)
    print("H-M3: Composition-Level Contract Validation Experiment")
    print("=" * 80)
    print()

    # GPU status check
    if torch.cuda.is_available():
        print(f"✓ CUDA available: {torch.cuda.device_count()} device(s)")
        print(f"  Primary device: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠ CUDA not available - some tests will be skipped")
    print()

    # Load test cases
    test_cases = load_all_test_cases()
    print(f"Loaded {len(test_cases)} test cases")
    print()

    results = {
        "experiment_id": "h-m3-poc",
        "timestamp": datetime.now().isoformat(),
        "gpu_available": torch.cuda.is_available(),
        "test_results": [],
        "summary": {}
    }

    # Run tests
    for idx, test_case in enumerate(test_cases, 1):
        print(f"Test {idx}/{len(test_cases)}: {test_case.defect_id}")
        print(f"  Category: {test_case.category}")
        print(f"  Description: {test_case.description}")
        print("-" * 80)

        # Skip tests that require CUDA if not available
        if 'cuda' in test_case.description.lower() and not torch.cuda.is_available():
            print("  ⊘ SKIPPED (requires CUDA)\n")
            results["test_results"].append({
                "test_id": test_case.defect_id,
                "category": test_case.category,
                "skipped": True,
                "reason": "CUDA not available"
            })
            continue

        # Run baseline (no contracts)
        print("  Running baseline (no contracts)...")
        try:
            baseline_result = run_baseline(test_case)
        except Exception as e:
            # Skip test if baseline itself fails unexpectedly
            print(f"  ⚠ Baseline execution failed: {str(e)[:100]}")
            baseline_result = {'detected': False, 'detection_stage': 'error', 'error_message': str(e)[:100]}

        # Run with contracts
        print("  Running with composition contracts...")
        try:
            proposed_result = run_with_contracts(test_case)
        except Exception as e:
            print(f"  ⚠ Contract execution failed: {str(e)[:100]}")
            proposed_result = {'detected': False, 'detection_stage': 'error', 'detection_time': 0, 'error_message': str(e)[:100]}

        # Compare results
        baseline_detected = baseline_result.get('detected', False)
        proposed_detected = proposed_result.get('detected', False)
        proposed_stage = proposed_result.get('detection_stage', 'none')
        detection_time = proposed_result.get('detection_time', 0)

        # Determine outcome
        if test_case.expected_violation == "none":
            # Control test - should pass
            if not proposed_detected:
                outcome = "✓ PASS (no false positive)"
            else:
                outcome = "✗ FAIL (false positive)"
        else:
            # Defect test - should detect
            if proposed_detected and proposed_stage == 'composition':
                outcome = "✓ DETECTED at composition stage"
            elif proposed_detected and proposed_stage == 'runtime':
                outcome = "⚠ DETECTED at runtime (late)"
            else:
                outcome = "✗ NOT DETECTED"

        print(f"  Baseline: {'detected' if baseline_detected else 'not detected'} "
              f"({baseline_result.get('detection_stage', 'none')})")
        print(f"  Proposed: {'detected' if proposed_detected else 'not detected'} "
              f"({proposed_stage}, {detection_time:.4f}s)")
        print(f"  Result: {outcome}")
        print()

        # Store result
        results["test_results"].append({
            "test_id": test_case.defect_id,
            "category": test_case.category,
            "description": test_case.description,
            "expected_violation": test_case.expected_violation,
            "baseline_detected": baseline_detected,
            "baseline_stage": baseline_result.get('detection_stage', 'none'),
            "proposed_detected": proposed_detected,
            "proposed_stage": proposed_stage,
            "detection_time": detection_time,
            "outcome": outcome,
            "source_issue": test_case.source_issue
        })

    # Calculate summary statistics
    completed_tests = [r for r in results["test_results"] if not r.get('skipped', False)]
    defect_tests = [r for r in completed_tests if r['expected_violation'] != 'none']
    control_tests = [r for r in completed_tests if r['expected_violation'] == 'none']

    # Detection metrics
    total_defects = len(defect_tests)
    detected_by_baseline = len([r for r in defect_tests if r['baseline_detected']])
    detected_by_proposed = len([r for r in defect_tests if r['proposed_detected']])
    detected_at_composition = len([r for r in defect_tests if r['proposed_stage'] == 'composition'])

    # False positives
    false_positives = len([r for r in control_tests if r['proposed_detected']])

    # Rates
    baseline_detection_rate = (detected_by_baseline / total_defects * 100) if total_defects > 0 else 0
    proposed_detection_rate = (detected_by_proposed / total_defects * 100) if total_defects > 0 else 0
    composition_detection_rate = (detected_at_composition / total_defects * 100) if total_defects > 0 else 0
    false_positive_rate = (false_positives / len(control_tests) * 100) if control_tests else 0

    results["summary"] = {
        "total_tests": len(test_cases),
        "completed_tests": len(completed_tests),
        "skipped_tests": len(test_cases) - len(completed_tests),
        "total_defects": total_defects,
        "detected_by_baseline": detected_by_baseline,
        "detected_by_proposed": detected_by_proposed,
        "detected_at_composition": detected_at_composition,
        "baseline_detection_rate": baseline_detection_rate,
        "proposed_detection_rate": proposed_detection_rate,
        "composition_detection_rate": composition_detection_rate,
        "false_positives": false_positives,
        "false_positive_rate": false_positive_rate,
        "avg_detection_time": sum(r.get('detection_time', 0) for r in defect_tests) / len(defect_tests) if defect_tests else 0
    }

    # Print summary
    print("=" * 80)
    print("EXPERIMENT SUMMARY")
    print("=" * 80)
    print(f"Total tests: {len(test_cases)} ({len(completed_tests)} completed, {len(test_cases) - len(completed_tests)} skipped)")
    print(f"Total defects: {total_defects}")
    print()
    print("Detection Rates:")
    print(f"  Baseline (runtime):       {detected_by_baseline}/{total_defects} ({baseline_detection_rate:.1f}%)")
    print(f"  Proposed (any stage):     {detected_by_proposed}/{total_defects} ({proposed_detection_rate:.1f}%)")
    print(f"  Proposed (composition):   {detected_at_composition}/{total_defects} ({composition_detection_rate:.1f}%)")
    print()
    print(f"False Positive Rate: {false_positives}/{len(control_tests)} ({false_positive_rate:.1f}%)")
    print(f"Average Detection Time: {results['summary']['avg_detection_time']:.4f}s")
    print()

    # Save results
    with open('experiment_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("✓ Results saved to experiment_results.json")
    print()

    # Gate decision (SHOULD_WORK: ≥60% detection rate)
    gate_threshold = 60.0
    if composition_detection_rate >= gate_threshold:
        print(f"✓ SHOULD_WORK GATE: PASS (composition detection rate {composition_detection_rate:.1f}% >= {gate_threshold}%)")
        return 0
    else:
        print(f"⚠ SHOULD_WORK GATE: PARTIAL (composition detection rate {composition_detection_rate:.1f}% < {gate_threshold}%)")
        print("  Note: SHOULD_WORK gate allows continuation with limitation documentation")
        return 0  # SHOULD_WORK doesn't block


if __name__ == "__main__":
    exit(main())
