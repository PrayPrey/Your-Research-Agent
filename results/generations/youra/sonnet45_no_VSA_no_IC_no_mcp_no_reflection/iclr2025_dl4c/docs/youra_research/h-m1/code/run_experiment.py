#!/usr/bin/env python3
"""Main experiment runner for h-m1."""

import sys
from pathlib import Path
import json

# Add code dir to path
sys.path.insert(0, str(Path(__file__).parent))

from config import EXPERIMENT_CONFIG, validate_config
from mock_agent import MockDebugAgent, generate_mock_problems
from clustering import clustering_coefficient, permutation_test, evaluate_gate
from visualizer import plot_clustering_comparison, plot_error_distribution, save_sessions_summary
from utils import ErrorType


def main():
    """Run full h-m1 experiment."""

    print("=" * 60)
    print("h-m1: Error Clustering Experiment")
    print("=" * 60)

    # Validate config
    validate_config(EXPERIMENT_CONFIG)
    print("\nConfig validated")

    # Setup paths
    base_path = Path(__file__).parent.parent
    figures_path = base_path / "figures"
    results_path = base_path / "results"
    data_path = base_path / "data"

    figures_path.mkdir(parents=True, exist_ok=True)
    results_path.mkdir(parents=True, exist_ok=True)
    data_path.mkdir(parents=True, exist_ok=True)

    # Generate mock problems
    print(f"\nGenerating {EXPERIMENT_CONFIG['num_problems']} mock problems...")
    problems = generate_mock_problems(
        count=EXPERIMENT_CONFIG['num_problems'],
        min_tests=EXPERIMENT_CONFIG['min_test_cases'],
        seed=EXPERIMENT_CONFIG['random_seed']
    )
    print(f"  Generated {len(problems)} problems")
    print(f"  Avg test cases: {sum(len(p.test_cases) for p in problems) / len(problems):.1f}")

    # Run debugging sessions (agent with clustering behavior)
    print("\nRunning debugging sessions (agent with clustering)...")
    agent = MockDebugAgent(
        seed=EXPERIMENT_CONFIG['random_seed'],
        clustering_strength=0.5  # Moderate clustering
    )

    sessions = []
    for i, problem in enumerate(problems):
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{len(problems)}")
        session = agent.run_debug_session(problem, max_iterations=EXPERIMENT_CONFIG['max_iterations'])
        sessions.append(session)

    print(f"  Completed {len(sessions)} sessions")

    # Collect error labels and fix sequences
    print("\nCollecting error labels and fix sequences...")
    all_fix_sequence = []
    error_labels = {}

    for session in sessions:
        all_fix_sequence.extend(session.fix_sequence)
        for failure in session.failures:
            if failure.error_type:
                error_labels[failure.test_id] = failure.error_type

    print(f"  Total fixes: {len(all_fix_sequence)}")
    print(f"  Unique tests: {len(set(all_fix_sequence))}")
    print(f"  Error labels: {len(error_labels)}")

    # Clustering analysis (agent)
    print("\nComputing clustering coefficient (agent)...")
    agent_coeff, p_value = permutation_test(
        all_fix_sequence,
        error_labels,
        n_permutations=EXPERIMENT_CONFIG['num_permutations'],
        seed=EXPERIMENT_CONFIG['random_seed']
    )
    print(f"  Agent clustering coefficient: {agent_coeff:.3f}")
    print(f"  p-value: {p_value:.4f}")

    # Random baseline
    print("\nComputing random baseline...")
    import random
    rng = random.Random(EXPERIMENT_CONFIG['random_seed'] + 1)
    random_sequence = all_fix_sequence.copy()
    rng.shuffle(random_sequence)
    random_coeff = clustering_coefficient(random_sequence, error_labels)
    print(f"  Random clustering coefficient: {random_coeff:.3f}")

    # Gate evaluation
    print("\nEvaluating MUST_WORK gate...")
    gate_result = evaluate_gate(
        agent_coeff,
        p_value,
        clustering_threshold=EXPERIMENT_CONFIG['clustering_threshold'],
        p_threshold=EXPERIMENT_CONFIG['p_value_threshold']
    )

    print(f"  Clustering threshold: {gate_result['clustering_threshold']}")
    print(f"  p-value threshold: {gate_result['p_threshold']}")
    print(f"  Agent coefficient: {gate_result['clustering_agent']:.3f}")
    print(f"  Gate decision: {gate_result['decision']}")

    # Generate visualizations
    print("\nGenerating visualizations...")
    plot_clustering_comparison(
        agent_coeff,
        random_coeff,
        p_value,
        figures_path / "clustering_comparison.txt"
    )
    print("  Saved clustering_comparison.txt")

    plot_error_distribution(
        error_labels,
        figures_path / "error_distribution.txt"
    )
    print("  Saved error_distribution.txt")

    save_sessions_summary(
        sessions,
        results_path / "sessions_summary.json"
    )
    print("  Saved sessions_summary.json")

    # Save final results
    final_results = {
        "hypothesis_id": "h-m1",
        "gate_type": "MUST_WORK",
        "metrics": {
            "clustering_agent": float(agent_coeff),
            "clustering_random": float(random_coeff),
            "p_value": float(p_value),
            "num_problems": len(problems),
            "num_sessions": len(sessions),
            "total_fixes": len(all_fix_sequence),
            "unique_tests": len(set(all_fix_sequence))
        },
        "gate_evaluation": {
            "clustering_agent": float(gate_result["clustering_agent"]),
            "p_value": float(gate_result["p_value"]),
            "clustering_threshold": float(gate_result["clustering_threshold"]),
            "p_threshold": float(gate_result["p_threshold"]),
            "gate_pass": bool(gate_result["gate_pass"]),
            "decision": gate_result["decision"]
        },
        "config": {k: v for k, v in EXPERIMENT_CONFIG.items() if isinstance(v, (int, float, str, list))}
    }

    results_file = results_path / "final_results.json"
    with open(results_file, 'w') as f:
        json.dump(final_results, f, indent=2)
    print(f"  Saved {results_file}")

    # Summary
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Agent clustering coefficient: {agent_coeff:.3f}")
    print(f"Random baseline: {random_coeff:.3f}")
    print(f"p-value: {p_value:.4f}")
    print(f"Gate: {gate_result['decision']}")
    print("=" * 60)

    return gate_result['gate_pass']


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
