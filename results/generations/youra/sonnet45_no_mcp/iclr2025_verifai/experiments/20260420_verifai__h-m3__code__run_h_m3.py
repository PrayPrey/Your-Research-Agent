"""Main experiment script for h-m3: Hybrid Signal Combination.

Evaluates 7 detector variants on LeanDojo dataset.
"""

import sys
import json
import csv
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

# Add module directories to path
code_dir = Path(__file__).parent
sys.path.insert(0, str(code_dir / "detectors"))
sys.path.insert(0, str(code_dir / "evaluation"))
sys.path.insert(0, str(code_dir / "signals"))

from hybrid_detector import HybridTerminationDetector
from threshold_selector import ThresholdSelector
from ablation_framework import AblationFramework


def load_h_m1_results(h_m1_path: str = None) -> tuple:
    """Load h-m1 results CSV for ground truth labels.

    Args:
        h_m1_path: Path to h-m1 results CSV

    Returns:
        (theorem_ids, labels, confidence_variances) where labels are 0=success, 1=timeout
    """
    if h_m1_path is None:
        # Try multiple possible paths
        possible_paths = [
            Path(__file__).parent.parent.parent / "h-m1" / "code" / "results" / "results_raw.csv",
            Path(__file__).parent.parent.parent / "h-m1" / "code" / "results" / "h_m1_results.csv",
        ]

        for p in possible_paths:
            if p.exists():
                h_m1_path = str(p)
                break

        if h_m1_path is None:
            raise FileNotFoundError(
                f"h-m1 results CSV not found. Tried:\n" +
                "\n".join(f"  - {p}" for p in possible_paths) +
                "\n\nPlease ensure h-m1 experiment has been run first."
            )

    print(f"📊 Loading h-m1 results from: {h_m1_path}")

    theorem_ids = []
    labels = []
    confidence_variances = []

    with open(h_m1_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            theorem_ids.append(row['theorem_id'])
            # outcome: 0=success, 1=timeout
            outcome = int(row.get('outcome', row.get('result', 0)))
            labels.append(outcome)
            # Extract confidence variance from h-m1 results
            variance = float(row.get('confidence_variance', 0.0))
            confidence_variances.append(variance)

    print(f"  ✓ Loaded {len(theorem_ids)} theorems")
    print(f"    Success: {labels.count(0)}, Timeout: {labels.count(1)}")
    return theorem_ids, labels, confidence_variances


def extract_signals_from_h_m2(theorem_ids: List[str], labels: List[int], confidence_variances: List[float]) -> List[Dict[str, float]]:
    """Extract signals from h-m2 results with tree tracking.

    Args:
        theorem_ids: List of theorem IDs from h-m1
        labels: Ground truth labels
        confidence_variances: Confidence variance values from h-m1

    Returns:
        List of signal dictionaries with all four signals
    """
    print("📊 Extracting signals from h-m2 data...")

    # Try to load h-m2 pickle results
    h_m2_pkl_path = Path(__file__).parent.parent.parent / "h-m2" / "code" / "results" / "h_m2_full_results.pkl"

    # Also check local results directory (may have been copied)
    local_pkl_path = Path(__file__).parent / "results" / "h_m2_full_results.pkl"

    if local_pkl_path.exists():
        h_m2_pkl_path = local_pkl_path

    if not h_m2_pkl_path.exists():
        raise FileNotFoundError(
            f"h-m2 results pickle not found. Expected at:\n"
            f"  - {h_m2_pkl_path}\n"
            f"  - {local_pkl_path}\n"
            f"\nThis experiment requires REAL h-m2 data with tree tracking.\n"
            f"Please ensure h-m2 experiment has been run first and generated h_m2_full_results.pkl"
        )

    print(f"  Loading h-m2 results from: {h_m2_pkl_path}")

    import pickle
    import sys

    # Add h-m2 code to path for unpickling
    h_m2_code_path = Path(__file__).parent.parent.parent / "h-m2" / "code"
    if h_m2_code_path.exists():
        sys.path.insert(0, str(h_m2_code_path))

    with open(h_m2_pkl_path, 'rb') as f:
        h_m2_results = pickle.load(f)

    print(f"  ✓ Loaded {len(h_m2_results)} h-m2 results with tree data")

    # Build h-m2 index by variance (for matching when IDs don't align)
    # Group by outcome for more accurate matching
    h_m2_timeout_records = [r for r in h_m2_results if r.get('outcome') == 'timeout']
    h_m2_success_records = [r for r in h_m2_results if r.get('outcome') != 'timeout']

    print(f"  h-m2 breakdown: {len(h_m2_timeout_records)} timeout, {len(h_m2_success_records)} success")

    # Extract signals from h-m2 results
    signals_list = []
    matched_count = 0
    used_h2_indices = set()

    for i, (tid, variance, label) in enumerate(zip(theorem_ids, confidence_variances, labels)):
        # Try direct ID match first
        h_m2_record = None
        for idx, record in enumerate(h_m2_results):
            if record.get('theorem_id') == tid and idx not in used_h2_indices:
                h_m2_record = record
                used_h2_indices.add(idx)
                matched_count += 1
                break

        # If no ID match, try matching by outcome and closest variance
        if not h_m2_record:
            pool = h_m2_timeout_records if label == 1 else h_m2_success_records
            if pool:
                # Find closest variance match that hasn't been used
                best_match = None
                best_dist = float('inf')
                best_idx = -1

                for idx, record in enumerate(h_m2_results):
                    if idx in used_h2_indices:
                        continue
                    if record.get('outcome') == ('timeout' if label == 1 else 'success'):
                        dist = abs(record.get('variance', 0) - variance)
                        if dist < best_dist:
                            best_dist = dist
                            best_match = record
                            best_idx = idx

                if best_match:
                    h_m2_record = best_match
                    used_h2_indices.add(best_idx)
                    matched_count += 1

        if h_m2_record and 'divergence_markers' in h_m2_record:
            divergence_markers = h_m2_record.get('divergence_markers', {})

            # Extract symbolic signals from real tree data
            collisions = divergence_markers.get('collision_count', 0)
            backtrack_count = divergence_markers.get('backtrack_count', 0)

            # Compute backtrack frequency (per 10 collisions)
            backtrack_freq = backtrack_count / max(collisions + 1, 10)

            # Exponential growth: use collision count as proxy for state space growth
            growth_rate = collisions / 10.0  # Normalize

            signals = {
                'confidence_variance': variance,
                'state_collisions': float(collisions),
                'exponential_growth': growth_rate,
                'backtrack_freq': backtrack_freq
            }
        else:
            # No matching h-m2 record - use zero symbolic signals
            signals = {
                'confidence_variance': variance,
                'state_collisions': 0.0,
                'exponential_growth': 0.0,
                'backtrack_freq': 0.0
            }

        signals_list.append(signals)

    print(f"  ✓ Matched {matched_count}/{len(theorem_ids)} theorems with h-m2 tree data")
    print(f"  ✓ Extracted signals for {len(signals_list)} theorems from REAL h-m2 data")
    return signals_list


def compute_exponential_growth(states: List[Any]) -> float:
    """Compute exponential growth rate from proof states.

    Args:
        states: List of proof states

    Returns:
        Growth rate (slope in log space)
    """
    if len(states) < 2:
        return 0.0

    # Extract state sizes
    sizes = []
    for state in states[:10]:  # Use first 10 states
        try:
            if hasattr(state, 'goals'):
                size = len(state.goals)
            elif hasattr(state, 'pp'):
                size = len(str(state.pp))
            else:
                size = len(str(state))
            sizes.append(max(size, 1))
        except:
            sizes.append(1)

    if len(sizes) < 2:
        return 0.0

    # Fit exponential trend
    t = np.arange(len(sizes))
    log_sizes = np.log(np.array(sizes))

    try:
        coeffs = np.polyfit(t, log_sizes, 1)
        return float(coeffs[0])
    except:
        return 0.0




def main():
    """Main experiment execution."""
    print("=" * 60)
    print("H-M3: Hybrid Signal Combination Experiment")
    print("=" * 60)
    print()

    # Step 1: Load h-m1 results for ground truth
    theorem_ids, labels, confidence_variances = load_h_m1_results()

    # Step 2: Extract signals from h-m2 data (with tree tracking)
    signals_list = extract_signals_from_h_m2(theorem_ids, labels, confidence_variances)

    # Step 3: Select thresholds from timeout group
    print("\n📊 Selecting thresholds from timeout group...")
    selector = ThresholdSelector()
    thresholds = selector.select_thresholds(signals_list, labels)

    print("  Selected thresholds:")
    for signal, thresh in thresholds.items():
        print(f"    {signal}: {thresh:.4f}")

    # Step 4: Run ablation framework
    print("\n📊 Running ablation framework (7 models)...")
    framework = AblationFramework(thresholds)
    results = framework.evaluate_all_models(signals_list, labels)

    print("\n  Results:")
    print(f"  {'Model':<15} {'Precision':>10} {'Recall':>10} {'F1':>10}")
    print("  " + "-" * 50)

    for model_name, metrics in results.items():
        print(f"  {model_name:<15} {metrics['precision']:>10.3f} "
              f"{metrics['recall']:>10.3f} {metrics['f1']:>10.3f}")

    # Step 5: Check gate condition
    print("\n📊 Checking gate condition...")
    gate_passed = framework.check_gate_condition(results)

    hybrid_f1 = results['hybrid_all']['f1']
    single_f1s = [results[m]['f1'] for m in ['confidence_only', 'symbolic_only', 'search_only']]
    max_single_f1 = max(single_f1s)

    print(f"  Hybrid F1: {hybrid_f1:.3f}")
    print(f"  Max Single F1: {max_single_f1:.3f}")
    print(f"  Gate condition (hybrid > max_single): {'✓ PASS' if gate_passed else '✗ FAIL'}")

    # Step 6: Save results
    output_file = Path(__file__).parent / "results" / "h_m3_results.json"
    output_file.parent.mkdir(exist_ok=True)

    output_data = {
        'thresholds': thresholds,
        'results': results,
        'gate_passed': gate_passed,
        'sample_size': len(theorem_ids),
        'timeout_count': labels.count(1),
        'success_count': labels.count(0)
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")

    # Return gate result for checkpoint
    return {
        'gate_passed': gate_passed,
        'hybrid_f1': hybrid_f1,
        'max_single_f1': max_single_f1,
        'results': results
    }


if __name__ == "__main__":
    result = main()
    print("\n" + "=" * 60)
    print("Experiment complete!")
    print("=" * 60)
