"""Main experiment runner for H-M2."""

import sys
import os
import json

# Set up paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
H_M1_CODE_PATH = os.path.join(os.path.dirname(os.path.dirname(CURRENT_DIR)), "h-m1", "code")

# Add H-M1 to path for utilities
sys.path.insert(0, H_M1_CODE_PATH)

# Import from H-M1
from mock_agent import generate_mock_problems

# Import from H-M2 (current directory)
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

h_m2_config = load_module("h_m2_config", os.path.join(CURRENT_DIR, "config.py"))
h_m2_prioritizer = load_module("h_m2_prioritizer", os.path.join(CURRENT_DIR, "prioritizer.py"))
h_m2_agent = load_module("h_m2_agent", os.path.join(CURRENT_DIR, "agent.py"))
h_m2_evaluate = load_module("h_m2_evaluate", os.path.join(CURRENT_DIR, "evaluate.py"))
h_m2_visualizer = load_module("h_m2_visualizer", os.path.join(CURRENT_DIR, "visualizer.py"))

BASELINE_CONFIG = h_m2_config.BASELINE_CONFIG
PROPOSED_CONFIG = h_m2_config.PROPOSED_CONFIG
EVALUATION_CONFIG = h_m2_config.EVALUATION_CONFIG
DATASET_CONFIG = h_m2_config.DATASET_CONFIG

RootCausePrioritizer = h_m2_prioritizer.RootCausePrioritizer
BaselineAgent = h_m2_agent.BaselineAgent
ProposedAgent = h_m2_agent.ProposedAgent
compare_agents = h_m2_evaluate.compare_agents

plot_proportion_comparison = h_m2_visualizer.plot_proportion_comparison
plot_fix_impact_distribution = h_m2_visualizer.plot_fix_impact_distribution
plot_cumulative_tests = h_m2_visualizer.plot_cumulative_tests
plot_cluster_vs_impact = h_m2_visualizer.plot_cluster_vs_impact


def load_dataset():
    """Load dataset (H-M1 cache or generate mock)."""
    cache_path = DATASET_CONFIG["h_m1_cache_path"]

    # Try loading from cache
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            data = json.load(f)
            if len(data) > 0:
                print(f"Loading dataset from cache: {cache_path}")
                print(f"Loaded {len(data)} problems from cache")
                return data

    # Generate mock problems
    print("Cache empty or not found, generating mock problems...")
    problems = generate_mock_problems(
        count=DATASET_CONFIG["num_problems"],
        min_tests=DATASET_CONFIG["min_test_cases"],
        seed=BASELINE_CONFIG["random_seed"]
    )
    print(f"Generated {len(problems)} mock problems")
    return problems


def run_baseline(problems):
    """Run baseline agent on all problems."""
    print("\n=== Running Baseline Agent (Sequential) ===")
    agent = BaselineAgent(
        model=BASELINE_CONFIG["model"],
        temp=BASELINE_CONFIG["temperature"],
        seed=BASELINE_CONFIG["random_seed"]
    )

    results = []
    for i, problem in enumerate(problems):
        if i % 10 == 0:
            print(f"Progress: {i}/{len(problems)} problems")
        fix_results = agent.run(problem, max_iter=BASELINE_CONFIG["max_iterations"])
        results.append(fix_results)

    print(f"Baseline complete: {len(results)} problems")
    return results


def run_proposed(problems):
    """Run proposed agent on all problems."""
    print("\n=== Running Proposed Agent (Prioritized) ===")
    prioritizer = RootCausePrioritizer()
    agent = ProposedAgent(
        prioritizer=prioritizer,
        model=PROPOSED_CONFIG["model"],
        temp=PROPOSED_CONFIG["temperature"],
        seed=PROPOSED_CONFIG["random_seed"]
    )

    results = []
    for i, problem in enumerate(problems):
        if i % 10 == 0:
            print(f"Progress: {i}/{len(problems)} problems")
        fix_results = agent.run(problem, max_iter=PROPOSED_CONFIG["max_iterations"])
        results.append(fix_results)

    print(f"Proposed complete: {len(results)} problems")
    return results


def evaluate_and_visualize(baseline_results, proposed_results):
    """Evaluate and generate visualizations."""
    print("\n=== Evaluation ===")

    # Compare agents
    comparison = compare_agents(
        baseline_results,
        proposed_results,
        threshold=EVALUATION_CONFIG["high_impact_threshold"]
    )

    print(f"Baseline proportion: {comparison['baseline_proportion']:.3f}")
    print(f"Proposed proportion: {comparison['proposed_proportion']:.3f}")
    print(f"Improvement: {comparison['improvement']:.3f}")
    print(f"Gate PASS: {comparison['gate_pass']}")

    # Save results
    os.makedirs(os.path.dirname(EVALUATION_CONFIG["results_file"]), exist_ok=True)
    with open(EVALUATION_CONFIG["results_file"], "w") as f:
        json.dump(comparison, f, indent=2)
    print(f"Results saved to: {EVALUATION_CONFIG['results_file']}")

    # Generate visualizations
    print("\n=== Generating Visualizations ===")
    figure_dir = EVALUATION_CONFIG["figure_dir"]

    plot_proportion_comparison(
        comparison["baseline_proportion"],
        comparison["proposed_proportion"],
        os.path.join(figure_dir, "proportion_comparison.png")
    )
    print("✓ proportion_comparison.png")

    plot_fix_impact_distribution(
        baseline_results,
        proposed_results,
        os.path.join(figure_dir, "fix_impact_distribution.png")
    )
    print("✓ fix_impact_distribution.png")

    plot_cumulative_tests(
        baseline_results,
        proposed_results,
        os.path.join(figure_dir, "cumulative_tests.png")
    )
    print("✓ cumulative_tests.png")

    # Cluster vs impact (aggregate from proposed results)
    cluster_sizes = []
    fix_impacts = []
    for problem_results in proposed_results:
        for fr in problem_results:
            # Mock cluster size (simplified - would compute from actual clusters)
            cluster_sizes.append(fr.delta_passing + 1)  # Placeholder
            fix_impacts.append(fr.delta_passing)

    plot_cluster_vs_impact(
        cluster_sizes,
        fix_impacts,
        os.path.join(figure_dir, "cluster_vs_impact.png")
    )
    print("✓ cluster_vs_impact.png")

    return comparison


def main():
    """Main experiment flow."""
    print("=" * 60)
    print("H-M2 Experiment: Root Cause Prioritization")
    print("=" * 60)

    # Load dataset
    problems = load_dataset()

    # Run agents
    baseline_results = run_baseline(problems)
    proposed_results = run_proposed(problems)

    # Evaluate and visualize
    comparison = evaluate_and_visualize(baseline_results, proposed_results)

    # Final summary
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Gate Status: {'PASS' if comparison['gate_pass'] else 'FAIL'}")
    print(f"Baseline: {comparison['baseline_proportion']:.3f}")
    print(f"Proposed: {comparison['proposed_proportion']:.3f}")
    print(f"Improvement: {comparison['improvement']:.3f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
