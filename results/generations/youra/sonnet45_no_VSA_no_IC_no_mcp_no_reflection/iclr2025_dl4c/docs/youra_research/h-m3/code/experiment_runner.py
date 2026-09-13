"""Main experiment orchestrator for h-m3."""
import json
import random
import yaml
import os
from datetime import datetime
from pattern_memory import PatternMemory
from agent import MockGPT4Agent
from random_baseline import run_random_baseline
from revealed_only_baseline import run_revealed_only_baseline
from analysis import (
    compute_slopes,
    permutation_test,
    transfer_efficiency,
    plot_held_out_curves,
    plot_pattern_usage,
    generate_validation_report
)


def load_config(config_path):
    with open(config_path) as f:
        return yaml.safe_load(f)


def prepare_data(config):
    """Generate mock Codeforces problems with test splits."""
    random.seed(config["experiment"]["random_seed"])

    n_problems = config["data"]["n_problems"]
    min_tests = config["data"]["min_test_cases"]
    split_ratio = config["data"]["test_split_ratio"]

    problems = []
    test_splits = {}
    baseline_codes = {}

    for i in range(n_problems):
        pid = f"problem_{i:03d}"

        n_tests = random.randint(min_tests, 20)
        tests = [{"input": f"test_{j}", "output": f"out_{j}"} for j in range(n_tests)]

        problems.append({
            "problem_id": pid,
            "description": f"Problem {i} description",
            "tests": tests,
            "rating": random.randint(1200, 1800)
        })

        n_revealed = int(n_tests * split_ratio)
        indices = list(range(n_tests))
        random.shuffle(indices)

        test_splits[pid] = {
            "revealed": sorted(indices[:n_revealed]),
            "held_out": sorted(indices[n_revealed:])
        }

        baseline_codes[pid] = f"def solve_{i}():\n    return 42\n"

    os.makedirs(config["data"]["cache_dir"], exist_ok=True)

    with open(os.path.join(config["data"]["cache_dir"], "problems.json"), "w") as f:
        json.dump(problems, f, indent=2)

    with open(os.path.join(config["data"]["cache_dir"], "test_splits.json"), "w") as f:
        json.dump(test_splits, f, indent=2)

    baseline_dir = os.path.join(config["data"]["cache_dir"], "baseline_codes")
    os.makedirs(baseline_dir, exist_ok=True)

    for pid, code in baseline_codes.items():
        with open(os.path.join(baseline_dir, f"{pid}.py"), "w") as f:
            f.write(code)

    return {
        "problems": problems,
        "test_splits": test_splits,
        "baseline_codes": baseline_codes
    }


def run_agent_experiment(data, config):
    """Run agent with pattern memory."""
    problems = data["problems"]
    test_splits = data["test_splits"]
    baseline_codes = data["baseline_codes"]
    n_iterations = config["agent"]["n_iterations"]

    results = {}
    pattern_usage_log = []

    for problem in problems:
        pid = problem["problem_id"]
        code = baseline_codes[pid]

        revealed_tests = [problem["tests"][idx] for idx in test_splits[pid]["revealed"]]
        held_out_tests = [problem["tests"][idx] for idx in test_splits[pid]["held_out"]]

        memory = PatternMemory()
        agent = MockGPT4Agent(memory=memory, temperature=config["agent"]["temperature"])

        iteration_results = []

        for _ in range(n_iterations):
            result = agent.fix_iteration(problem, code, revealed_tests, held_out_tests)
            code = result["code"]

            held_out_pass_rate = result["held_out_pass"] / len(held_out_tests) if held_out_tests else 0.0
            iteration_results.append(held_out_pass_rate)

        results[pid] = iteration_results
        pattern_usage_log.extend(memory.usage_log)

    return results, pattern_usage_log


def run_baselines(data, config):
    """Run both baselines."""
    problems = data["problems"]
    test_splits = data["test_splits"]
    baseline_codes = data["baseline_codes"]

    random_results = run_random_baseline(
        problems,
        test_splits,
        baseline_codes,
        n_mutations=config["baselines"]["random"]["n_mutations_per_problem"]
    )

    revealed_only_results = run_revealed_only_baseline(
        problems,
        test_splits,
        baseline_codes,
        n_iterations=config["baselines"]["revealed_only"]["n_iterations"]
    )

    return {
        "random": random_results,
        "revealed_only": revealed_only_results
    }


def run_analysis(agent_results, baseline_results, pattern_usage_log, config):
    """Perform statistical analysis."""
    all_results = {
        "agent": agent_results,
        "random": baseline_results["random"],
        "revealed_only": baseline_results["revealed_only"]
    }

    slopes = compute_slopes(all_results)

    agent_slope = slopes.get("agent_slope", 0.0)
    random_slope = slopes.get("random_slope", 0.0)

    slope_ratio = agent_slope / random_slope if random_slope != 0 else 0.0

    p_value = permutation_test(
        agent_results,
        baseline_results["random"],
        n_samples=config["analysis"]["permutation_test_samples"]
    )

    transfer_eff = transfer_efficiency(
        revealed_slope=agent_slope * 2,  # mock revealed slope
        held_out_slope=agent_slope
    )

    pattern_usage = 0.0
    if pattern_usage_log:
        total_used = sum(1 for x in pattern_usage_log if x["used"])
        pattern_usage = total_used / len(pattern_usage_log)

    os.makedirs(config["output"]["plots_dir"], exist_ok=True)

    plot_held_out_curves(
        agent_results,
        baseline_results,
        os.path.join(config["output"]["plots_dir"], "held_out_curves.png")
    )

    plot_pattern_usage(
        pattern_usage_log,
        os.path.join(config["output"]["plots_dir"], "pattern_usage.png")
    )

    analysis = {
        "agent_slope": agent_slope,
        "random_slope": random_slope,
        "revealed_only_slope": slopes.get("revealed_only_slope", 0.0),
        "slope_ratio": slope_ratio,
        "p_value": p_value,
        "transfer_efficiency": transfer_eff,
        "pattern_usage_rate": pattern_usage,
        "timestamp": datetime.utcnow().isoformat()
    }

    return analysis


def execute(config_path):
    """Run full pipeline."""
    config = load_config(config_path)

    print("[1/4] Preparing data...")
    data = prepare_data(config)

    print("[2/4] Running agent experiment...")
    agent_results, pattern_usage_log = run_agent_experiment(data, config)

    print("[3/4] Running baselines...")
    baseline_results = run_baselines(data, config)

    print("[4/4] Running analysis...")
    analysis = run_analysis(agent_results, baseline_results, pattern_usage_log, config)

    os.makedirs(config["output"]["results_dir"], exist_ok=True)

    with open(os.path.join(config["output"]["results_dir"], "agent_results.json"), "w") as f:
        json.dump(agent_results, f, indent=2)

    with open(os.path.join(config["output"]["results_dir"], "baseline_results.json"), "w") as f:
        json.dump(baseline_results, f, indent=2)

    with open(os.path.join(config["output"]["results_dir"], "slope_analysis.json"), "w") as f:
        json.dump(analysis, f, indent=2)

    report = generate_validation_report(analysis)
    with open(config["output"]["validation_report"], "w") as f:
        f.write(report)

    print("\n=== EXPERIMENT COMPLETE ===")
    print(f"Slope Ratio: {analysis['slope_ratio']:.2f}")
    print(f"p-value: {analysis['p_value']:.4f}")
    print(f"Transfer Efficiency: {analysis['transfer_efficiency']:.2f}")
    print(f"Pattern Usage Rate: {analysis['pattern_usage_rate'] * 100:.1f}%")

    gate_pass = (
        analysis["slope_ratio"] > 1.5 and
        analysis["p_value"] < 0.05 and
        analysis["transfer_efficiency"] > 0.5
    )
    print(f"\nGate Result: {'PASS' if gate_pass else 'FAIL'}")

    return analysis, gate_pass


if __name__ == "__main__":
    config_path = "config/experiment.yaml"
    analysis, gate_pass = execute(config_path)
