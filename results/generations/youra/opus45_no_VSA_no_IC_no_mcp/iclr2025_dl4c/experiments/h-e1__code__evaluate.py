import json
import os
import matplotlib.pyplot as plt
import numpy as np
from config import CONFIG

def compute_pass_at_1(results: list[dict]) -> float:
    if not results:
        return 0.0
    return sum(1 for r in results if r["passed"]) / len(results)

def compute_pass_at_1_by_iteration(results: list[dict], max_k: int) -> dict[int, float]:
    stats = {}
    for k in range(1, max_k + 1):
        passed_by_k = sum(1 for r in results if r["passed"] and r["iterations_used"] <= k)
        stats[k] = passed_by_k / len(results) if results else 0.0
    return stats

def verify_mechanism_activation(results_exec: list[dict], results_random: list[dict]) -> dict:
    checks = {
        "feedback_differs": False,
        "exec_has_localization": False,
        "refinements_differ": False,
    }

    for r_exec, r_random in zip(results_exec, results_random):
        if r_exec["feedback_log"] and r_random["feedback_log"]:
            checks["feedback_differs"] = r_exec["feedback_log"][0] != r_random["feedback_log"][0]
            exec_fb = r_exec["feedback_log"][0].lower()
            checks["exec_has_localization"] = "line" in exec_fb or "error" in exec_fb
            checks["refinements_differ"] = r_exec["code"] != r_random["code"]
            if all(checks.values()):
                break
    return checks

def plot_gate_comparison(metrics: dict, out_path: str):
    fig, ax = plt.subplots(figsize=(10, 6))

    datasets = list(metrics.keys())
    x = np.arange(len(datasets))
    width = 0.35

    exec_scores = [metrics[d]["execution"] for d in datasets]
    random_scores = [metrics[d]["random"] for d in datasets]

    bars1 = ax.bar(x - width/2, exec_scores, width, label="Execution Feedback", color="#2196F3")
    bars2 = ax.bar(x + width/2, random_scores, width, label="Random Feedback", color="#FF9800")

    ax.set_ylabel("pass@1")
    ax.set_title("Execution vs Random Feedback: pass@1 Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(datasets)
    ax.legend()
    ax.set_ylim(0, 1)

    for bar in bars1 + bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.3f}', xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_iteration_progression(results_exec: list[dict], out_path: str):
    by_dataset = {}
    for r in results_exec:
        ds = r["dataset"]
        if ds not in by_dataset:
            by_dataset[ds] = []
        by_dataset[ds].append(r)

    fig, ax = plt.subplots(figsize=(8, 5))

    for ds, results in by_dataset.items():
        stats = compute_pass_at_1_by_iteration(results, CONFIG.max_iterations)
        iterations = list(stats.keys())
        rates = list(stats.values())
        ax.plot(iterations, rates, marker='o', label=ds)

    ax.set_xlabel("Iteration")
    ax.set_ylabel("pass@1")
    ax.set_title("pass@1 by Refinement Iteration (Execution Feedback)")
    ax.legend()
    ax.set_xticks(range(1, CONFIG.max_iterations + 1))
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def main():
    os.makedirs(CONFIG.figures_dir, exist_ok=True)

    with open(CONFIG.results_path) as f:
        all_results = json.load(f)

    # Split by dataset and feedback type
    by_dataset_type = {}
    for r in all_results:
        key = (r["dataset"], r["feedback_type"])
        if key not in by_dataset_type:
            by_dataset_type[key] = []
        by_dataset_type[key].append(r)

    # Compute pass@1
    metrics = {}
    for dataset in CONFIG.datasets:
        metrics[dataset] = {}
        for ftype in CONFIG.feedback_types:
            results = by_dataset_type.get((dataset, ftype), [])
            metrics[dataset][ftype] = compute_pass_at_1(results)

    print("\n=== RESULTS ===")
    for dataset, scores in metrics.items():
        print(f"\n{dataset}:")
        print(f"  Execution Feedback: {scores['execution']:.4f}")
        print(f"  Random Feedback:    {scores['random']:.4f}")
        delta = scores['execution'] - scores['random']
        print(f"  Delta:              {delta:+.4f}")

    # Gate check
    print("\n=== GATE CHECK ===")
    gate_passed = all(
        metrics[ds]["execution"] > metrics[ds]["random"]
        for ds in metrics
    )
    print(f"pass@1(exec) > pass@1(random) for all datasets: {'PASS' if gate_passed else 'FAIL'}")

    # Mechanism verification
    print("\n=== MECHANISM VERIFICATION ===")
    results_exec = [r for r in all_results if r["feedback_type"] == "execution"]
    results_random = [r for r in all_results if r["feedback_type"] == "random"]
    mech_checks = verify_mechanism_activation(results_exec, results_random)
    for check, passed in mech_checks.items():
        print(f"  {check}: {'PASS' if passed else 'FAIL'}")

    # Generate figures
    plot_gate_comparison(metrics, os.path.join(CONFIG.figures_dir, "gate_comparison.png"))
    plot_iteration_progression(results_exec, os.path.join(CONFIG.figures_dir, "iteration_progression.png"))

    print(f"\nFigures saved to {CONFIG.figures_dir}")

    # Summary for validation report
    summary = {
        "metrics": metrics,
        "gate_passed": gate_passed,
        "mechanism_checks": mech_checks,
    }
    with open("evaluation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()
