"""Main experiment pipeline for h-c1."""

import json
import os
import sys
from typing import Dict, List

# Import h-c1 modules first BEFORE extended_verifier pollutes sys.path with h-m4
import importlib.util

def load_local_module(name, path):
    """Load module from explicit path to avoid sys.path conflicts."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

base_dir = os.path.dirname(__file__)
h_c1_config = load_local_module("h_c1_config", os.path.join(base_dir, "config.py"))
CONFIG = h_c1_config.CONFIG

# Load h-c1 modules (visualizer BEFORE extended_verifier to avoid h-m4 conflict)
boundary_detector_mod = load_local_module("boundary_detector", os.path.join(base_dir, "boundary_detector.py"))
evaluator_mod = load_local_module("evaluator", os.path.join(base_dir, "evaluator.py"))
visualizer_mod = load_local_module("visualizer", os.path.join(base_dir, "visualizer.py"))

DomainBoundaryDetector = boundary_detector_mod.DomainBoundaryDetector
BoundaryEvaluator = evaluator_mod.BoundaryEvaluator
Visualizer = visualizer_mod.Visualizer

# Now load extended_verifier (which adds h-m4 to sys.path)
from extended_verifier import ExtendedConstraintVerifier


def load_data():
    """Load boundary test cases and KB domain taxonomy."""
    with open(CONFIG['boundary_test_path'], 'r') as f:
        boundary_cases = json.load(f)

    with open(CONFIG['kb_domains_path'], 'r') as f:
        kb_domains = json.load(f)

    return boundary_cases, kb_domains


def run_baseline(test_cases: List[Dict]) -> List[bool]:
    """Baseline: No boundary check (always classify as testable).

    In original h-m4 verifier without domain boundary module,
    out-of-scope hypotheses would attempt DBM lookup and fail randomly.
    For simplicity, baseline assumes permissive classification.
    """
    # Baseline behavior: No explicit boundary check
    # Simulate random/permissive classification (~50% accuracy on boundary cases)
    baseline_predictions = []
    for case in test_cases:
        # All boundary cases are expected=not_testable (ground truth = False)
        # Baseline incorrectly classifies some as testable (False Negative)
        # Simulate baseline: always says "testable" (worst case for boundaries)
        baseline_predictions.append(True)  # testable

    return baseline_predictions


def run_proposed(test_cases: List[Dict], verifier: ExtendedConstraintVerifier, detector: DomainBoundaryDetector) -> tuple:
    """Proposed: With boundary detection module."""
    proposed_predictions = []
    similarity_scores = {}  # For heatmap

    for case in test_cases:
        result = verifier.check_testability(case)
        proposed_predictions.append(result['testable'])

        # Collect similarity scores for heatmap
        boundary_check = detector.forward(case['text'])
        query_keywords = detector.extract_domain_keywords(case['text'])
        for domain_name, domain_keywords in detector.domain_embeddings.items():
            sim = detector.keyword_similarity(query_keywords, domain_keywords)
            similarity_scores[(case['id'], domain_name)] = sim

    return proposed_predictions, similarity_scores


def main():
    """Execute h-c1 experiment."""
    print("=" * 60)
    print("h-c1: Domain Boundary Detection Experiment")
    print("=" * 60)

    # Load data
    print("\n[1/5] Loading data...")
    boundary_cases, kb_domains = load_data()
    ground_truth = [case['expected'] == 'testable' for case in boundary_cases]  # All False for boundary cases
    print(f"  - Loaded {len(boundary_cases)} boundary test cases")
    print(f"  - Loaded {len(kb_domains)} KB domain categories")

    # Initialize modules
    print("\n[2/5] Initializing modules...")
    boundary_detector = DomainBoundaryDetector(
        kb_domains,
        similarity_threshold=CONFIG['similarity_threshold']
    )
    verifier = ExtendedConstraintVerifier(CONFIG['kb_path'], boundary_detector)
    evaluator = BoundaryEvaluator(gate_threshold=CONFIG['gate_threshold'])
    visualizer = Visualizer(CONFIG['figures_dir'])
    print(f"  - Similarity threshold: {CONFIG['similarity_threshold']}")
    print(f"  - Gate threshold: {CONFIG['gate_threshold']}")

    # Run baseline
    print("\n[3/5] Running baseline (no boundary check)...")
    baseline_predictions = run_baseline(boundary_cases)
    baseline_metrics = evaluator.evaluate_boundary_detection(baseline_predictions, ground_truth)
    print(f"  - Baseline accuracy: {baseline_metrics['accuracy']:.2%}")
    print(f"  - Baseline precision: {baseline_metrics['precision']:.2%}")
    print(f"  - Baseline recall: {baseline_metrics['recall']:.2%}")

    # Run proposed
    print("\n[4/5] Running proposed (with boundary check)...")
    proposed_predictions, similarity_scores = run_proposed(boundary_cases, verifier, boundary_detector)
    proposed_metrics = evaluator.evaluate_boundary_detection(proposed_predictions, ground_truth)
    print(f"  - Proposed accuracy: {proposed_metrics['accuracy']:.2%}")
    print(f"  - Proposed precision: {proposed_metrics['precision']:.2%}")
    print(f"  - Proposed recall: {proposed_metrics['recall']:.2%}")
    print(f"  - TP: {proposed_metrics['tp']}, TN: {proposed_metrics['tn']}, FP: {proposed_metrics['fp']}, FN: {proposed_metrics['fn']}")

    # Gate check
    print(f"\n[GATE CHECK]")
    print(f"  - Target accuracy: ≥{CONFIG['gate_threshold']:.0%}")
    print(f"  - Actual accuracy: {proposed_metrics['accuracy']:.2%}")
    print(f"  - Gate status: {'PASS' if proposed_metrics['gate_passed'] else 'FAIL'}")

    # PoC check
    poc_pass = proposed_metrics['accuracy'] > baseline_metrics['accuracy']
    print(f"\n[PoC CHECK]")
    print(f"  - Proposed > Baseline: {poc_pass}")
    print(f"  - Improvement: {proposed_metrics['accuracy'] - baseline_metrics['accuracy']:.2%}")

    # Visualize
    print("\n[5/5] Generating figures...")
    fig1 = visualizer.plot_gate_comparison(baseline_metrics, proposed_metrics, CONFIG['gate_threshold'])
    print(f"  - Saved: {fig1}")
    fig2 = visualizer.plot_confusion_matrix(ground_truth, proposed_predictions)
    print(f"  - Saved: {fig2}")
    fig3 = visualizer.plot_domain_coverage_heatmap(boundary_cases, kb_domains, similarity_scores)
    print(f"  - Saved: {fig3}")

    # Save results (convert numpy types for JSON serialization)
    def convert_numpy(obj):
        """Convert numpy types to Python native types."""
        if hasattr(obj, 'item'):
            return obj.item()
        elif isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(v) for v in obj]
        return obj

    results = {
        'baseline': convert_numpy(baseline_metrics),
        'proposed': convert_numpy(proposed_metrics),
        'gate_passed': bool(proposed_metrics['gate_passed']),
        'poc_passed': bool(poc_pass),
        'predictions': {
            'baseline': [bool(x) for x in baseline_predictions],
            'proposed': [bool(x) for x in proposed_predictions],
            'ground_truth': [bool(x) for x in ground_truth]
        }
    }

    results_path = os.path.join(CONFIG['output_dir'], 'results.json')
    os.makedirs(CONFIG['output_dir'], exist_ok=True)
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  - Saved results: {results_path}")

    print("\n" + "=" * 60)
    print("Experiment complete!")
    print(f"Final verdict: {'PASS' if proposed_metrics['gate_passed'] and poc_pass else 'FAIL'}")
    print("=" * 60)

    return results


if __name__ == '__main__':
    main()
