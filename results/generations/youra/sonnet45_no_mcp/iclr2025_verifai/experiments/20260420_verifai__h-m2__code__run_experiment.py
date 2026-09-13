"""
h-m2 Main Experiment Script
Tests divergence-confidence link by subdividing h-m1 timeout group.
"""

import sys
import os
import json
import pickle
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add current directory and h-m1 to import path
# IMPORTANT: h-m1 must be added BEFORE current_dir so h-m2 modules take precedence
current_dir = os.path.dirname(os.path.abspath(__file__))
h_m1_path = Path(__file__).parent.parent.parent / "h-m1" / "code"
sys.path.insert(0, str(h_m1_path))  # Add h-m1 first (lower priority)
sys.path.insert(0, current_dir)      # Add h-m2 second (higher priority)

# h-m2 modules - use direct file imports for PoC
from experiment.tree_tracker import ExtendedTimeoutRunnerWithTree, SearchTree
from analysis.divergence_classifier import DivergenceClassifier
from analysis.timeout_subgroup_analyzer import TimeoutSubgroupAnalyzer
from visualization.divergence_visualizer import DivergenceComparisonVisualizer


def load_h_m1_results(h_m1_results_path: str) -> List[Dict[str, Any]]:
    """
    Load h-m1 experiment results from CSV file.

    Args:
        h_m1_results_path: Path to h-m1 results CSV

    Returns:
        List of experiment results with variance and outcome

    Raises:
        FileNotFoundError: If h-m1 results not found
    """
    results_path = Path(h_m1_results_path)

    if not results_path.exists():
        raise FileNotFoundError(
            f"h-m1 results not found at: {results_path}\n"
            f"Run h-m1 experiment first or provide correct path."
        )

    # Load CSV data
    df = pd.read_csv(results_path)

    # Convert to list of dicts
    h_m1_results = []
    for _, row in df.iterrows():
        h_m1_results.append({
            'theorem_id': row['theorem_id'],
            'variance': row['confidence_variance'],
            'outcome': 'timeout' if row['outcome'] == 1 else 'success',
            'execution_time': row['execution_time'],
            'status': row['status']
        })

    print(f"✓ Loaded {len(h_m1_results)} h-m1 results from CSV")

    return h_m1_results


def rerun_with_tree_tracking(
    h_m1_timeout_group: List[Dict],
    timeout_seconds: int = 300
) -> List[Dict[str, Any]]:
    """
    Re-run timeout group with search tree tracking enabled using real LeanDojo theorems.

    This loads actual theorems from LeanDojo Benchmark and re-runs proof search
    with tree tracking to capture divergence markers.

    Args:
        h_m1_timeout_group: Filtered timeout experiments from h-m1
        timeout_seconds: Timeout duration (same as h-m1)

    Returns:
        Extended results with real search tree data
    """
    print(f"🔄 Re-running {len(h_m1_timeout_group)} timeout experiments with tree tracking...")

    # Load LeanDojo configuration from h-m1
    from config import EXPERIMENT_CONFIG
    from data.loader import TheoremSampler

    # Initialize sampler with same config as h-m1
    sampler = TheoremSampler(
        repo_url=EXPERIMENT_CONFIG["repo_url"],
        commit_hash=EXPERIMENT_CONFIG["commit_hash"],
        sample_size=EXPERIMENT_CONFIG["sample_size"],
        seed=EXPERIMENT_CONFIG["random_seed"]
    )

    # Load benchmark and sample theorems
    print("Loading LeanDojo Benchmark for tree tracking...")
    try:
        benchmark = sampler.load_benchmark()
        theorems = sampler.sample_theorems(benchmark)
        print(f"✓ Loaded {len(theorems)} theorems from LeanDojo")

        # Create theorem lookup by ID
        theorem_map = {f"mock_theorem_{str(i).zfill(3)}": theorems[i] for i in range(len(theorems))}

    except Exception as e:
        print(f"ERROR loading LeanDojo: {e}")
        raise RuntimeError(
            f"Failed to load LeanDojo Benchmark. "
            f"Ensure lean-dojo is installed and configured correctly."
        )

    # Initialize runner with tree tracking
    runner = ExtendedTimeoutRunnerWithTree(timeout_seconds=timeout_seconds)
    extended_results = []

    for i, h_m1_result in enumerate(h_m1_timeout_group):
        theorem_id = h_m1_result['theorem_id']
        print(f"  [{i+1}/{len(h_m1_timeout_group)}] Re-running {theorem_id} with tree tracking...")

        # Get corresponding theorem from LeanDojo
        if theorem_id not in theorem_map:
            print(f"    WARNING: {theorem_id} not found in theorem map, skipping")
            continue

        theorem = theorem_map[theorem_id]

        # Run experiment with tree tracking
        try:
            result = runner.run_experiment(theorem)

            # Combine h-m1 variance with h-m2 tree data
            extended_result = {
                'theorem_id': theorem_id,
                'variance': h_m1_result['variance'],  # Reuse h-m1 variance for consistency
                'outcome': 'timeout',  # All are timeouts from h-m1
                'search_tree': result.get('search_tree'),  # Add: real tree tracking
                'proof_states': result.get('proof_states', []),
                'execution_time': result.get('execution_time', 0)
            }

            extended_results.append(extended_result)
            print(f"    ✓ Tree tracked: {len(result.get('proof_states', []))} states explored")

        except Exception as e:
            print(f"    ERROR running {theorem_id}: {e}")
            continue

    print(f"✓ Tree tracking completed for {len(extended_results)} timeouts")

    if len(extended_results) == 0:
        raise RuntimeError(
            "No timeout experiments successfully re-run with tree tracking. "
            "Check LeanDojo installation and theorem availability."
        )

    return extended_results


def main():
    """
    Main h-m2 experiment orchestration.

    Steps:
    1. Load h-m1 results
    2. Re-run timeout group with tree tracking
    3. Classify each timeout (divergent vs difficult)
    4. Analyze variance by divergence
    5. Generate visualizations
    6. Save results and evaluate gate
    """
    print("=" * 70)
    print("h-m2 Experiment: Divergence-Confidence Link")
    print("=" * 70)

    # Configuration
    h_m1_results_path = Path(__file__).parent.parent.parent / "h-m1" / "code" / "results" / "results_raw.csv"
    output_dir = Path(__file__).parent / "results"
    figures_dir = Path(__file__).parent.parent / "figures"
    output_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)

    # Step 1: Load h-m1 results (REAL data from CSV)
    h_m1_results = load_h_m1_results(h_m1_results_path)

    # Filter timeout group
    timeout_group = [r for r in h_m1_results if r["outcome"] == "timeout"]
    print(f"📊 h-m1 timeout group: {len(timeout_group)} experiments")

    # Step 2: Re-run with tree tracking
    timeout_with_trees = rerun_with_tree_tracking(timeout_group)

    # Step 3: Classify divergence
    print("\n🔍 Classifying divergence...")
    classifier = DivergenceClassifier(collision_threshold=2, backtrack_threshold=5)

    for result in timeout_with_trees:
        is_divergent, markers = classifier.classify_timeout(
            result["search_tree"],
            result.get("proof_states", [])
        )
        result["is_divergent"] = is_divergent
        result["divergence_markers"] = markers

    divergent_count = sum(1 for r in timeout_with_trees if r["is_divergent"])
    difficult_count = len(timeout_with_trees) - divergent_count

    print(f"  Divergent: {divergent_count}")
    print(f"  Difficult: {difficult_count}")

    # Step 4: Analyze variance by divergence
    print("\n📈 Analyzing subgroup variance...")
    analyzer = TimeoutSubgroupAnalyzer()
    analysis_result = analyzer.analyze_variance_by_divergence(timeout_with_trees)

    print(f"  Divergent group: mean_var={analysis_result['divergent_group']['mean_variance']:.4f}")
    print(f"  Difficult group: mean_var={analysis_result['difficult_group']['mean_variance']:.4f}")

    # Step 5: Visualizations
    print("\n📊 Generating visualizations...")
    viz = DivergenceComparisonVisualizer(str(figures_dir))

    viz.plot_timeout_subgroup_comparison_bar(
        analysis_result["divergent_group"],
        analysis_result["difficult_group"]
    )

    viz.plot_variance_by_divergence_boxplot(
        analysis_result["divergent_group"]["variances"],
        analysis_result["difficult_group"]["variances"]
    )

    viz.plot_divergence_marker_scatter(timeout_with_trees)

    viz.plot_divergence_classification_pie(divergent_count, difficult_count)

    # Step 6: Save results
    print("\n💾 Saving results...")
    results_json = {
        "metadata": {
            "hypothesis_id": "h-m2",
            "date": datetime.now().isoformat(),
            "sample_size": len(timeout_with_trees)
        },
        "gate": {
            "type": "SHOULD_WORK",
            "condition": "mean_variance(divergent) > mean_variance(difficult)",
            "satisfied": analysis_result["gate_satisfied"]
        },
        "results": {
            "divergent_group": analysis_result["divergent_group"],
            "difficult_group": analysis_result["difficult_group"]
        }
    }

    with open(output_dir / "h_m2_results.json", "w") as f:
        json.dump(results_json, f, indent=2)

    # Save full results with trees (pickle)
    with open(output_dir / "h_m2_full_results.pkl", "wb") as f:
        pickle.dump(timeout_with_trees, f)

    print(f"✓ Results saved to: {output_dir}")

    # Step 7: Gate evaluation
    print("\n" + "=" * 70)
    print("GATE EVALUATION")
    print("=" * 70)
    print(f"Gate Type: SHOULD_WORK")
    print(f"Condition: Divergent timeouts show higher variance than difficult timeouts")
    print(f"")
    print(f"Mean Variance (Divergent): {analysis_result['divergent_group']['mean_variance']:.4f}")
    print(f"Mean Variance (Difficult): {analysis_result['difficult_group']['mean_variance']:.4f}")
    print(f"")
    print(f"Gate Result: {'✅ PASS' if analysis_result['gate_satisfied'] else '❌ FAIL'}")
    print("=" * 70)

    return analysis_result["gate_satisfied"]


if __name__ == "__main__":
    gate_passed = main()
    sys.exit(0 if gate_passed else 1)
