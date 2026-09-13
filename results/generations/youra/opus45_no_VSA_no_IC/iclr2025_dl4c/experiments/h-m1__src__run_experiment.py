#!/usr/bin/env python3
"""
H-M1 Experiment: Scale-Accuracy Ordering with Diminishing Returns

Hypothesis: Judge-execution agreement increases with model scale
            (7B < 70B < proprietary) with diminishing returns.

Gate: MUST_WORK
- Ordering: accuracy_7B < accuracy_70B < accuracy_proprietary
- Diminishing returns: (acc_70B - acc_7B) > (acc_proprietary - acc_70B)
- Kruskal-Wallis p < 0.05
"""
import json
import os
import sys
from datetime import datetime

from config import ExperimentConfig, MODEL_TIERS
from ground_truth import load_ground_truth
from judge_backends import create_judge
from metrics import evaluate_scale_ordering, verify_mechanism
from figures import generate_all_figures


def run_experiment(config: ExperimentConfig) -> dict:
    """Run the full H-M1 scale ordering experiment."""
    print(f"[{datetime.now().isoformat()}] Starting H-M1 experiment")
    print(f"Dataset: {config.eval.dataset}, N={config.eval.n_problems}")

    # Step 1: Load problems and ground truth
    print("\n[Step 1] Loading ground truth...")
    problems, ground_truth = load_ground_truth(
        dataset=config.eval.dataset,
        n_problems=config.eval.n_problems,
        seed=config.eval.seed
    )
    print(f"  Loaded {len(problems)} problems")
    print(f"  Pass rate: {sum(ground_truth.values())/len(ground_truth):.2%}")

    # Step 2: Run judges at each scale
    print("\n[Step 2] Running judges at each scale...")
    judge_verdicts = {}
    task_ids = list(problems.keys())

    for scale in config.scales_order:
        print(f"  Evaluating {scale} judge...")
        model_config = config.models[scale]
        judge = create_judge(model_config, seed=config.eval.seed)
        verdicts = judge.query_batch(task_ids, ground_truth)
        judge_verdicts[scale] = verdicts

        correct = sum(1 for tid in task_ids if verdicts[tid] == ground_truth[tid])
        print(f"    Accuracy: {correct}/{len(task_ids)} = {correct/len(task_ids):.3f}")

    # Step 3: Evaluate scale ordering
    print("\n[Step 3] Evaluating scale ordering...")
    results = evaluate_scale_ordering(judge_verdicts, ground_truth)

    print(f"\n  Accuracies:")
    for scale, acc in results["accuracies"].items():
        print(f"    {scale}: {acc:.4f}")

    print(f"\n  Kappas:")
    for scale, kappa in results["kappas"].items():
        print(f"    {scale}: {kappa:.4f}")

    print(f"\n  Ordering satisfied: {results['ordering_satisfied']}")
    print(f"  Diminishing returns: {results['diminishing_returns']}")
    print(f"    Δ(7B→70B) = {results['diff_7b_70b']:.4f}")
    print(f"    Δ(70B→prop) = {results['diff_70b_prop']:.4f}")
    print(f"  Kruskal-Wallis H = {results['kruskal_h']:.4f}, p = {results['p_value']:.2e}")

    # Step 4: Verify mechanism (gate check)
    print("\n[Step 4] Verifying mechanism (MUST_WORK gate)...")
    try:
        verify_mechanism(results)
        gate_passed = True
        print("  ✓ All conditions satisfied - GATE PASSED")
    except AssertionError as e:
        gate_passed = False
        print(f"  ✗ Gate failed: {e}")

    # Step 5: Generate figures
    print("\n[Step 5] Generating figures...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    figures_dir = os.path.join(script_dir, "..", config.figures_dir)
    generate_all_figures(results, figures_dir)
    print(f"  Saved figures to {figures_dir}")

    # Step 6: Save results
    print("\n[Step 6] Saving results...")
    outputs_dir = os.path.join(script_dir, "..", config.output_dir)
    os.makedirs(outputs_dir, exist_ok=True)

    output_data = {
        "hypothesis": "H-M1",
        "statement": "Judge-execution agreement increases with model scale with diminishing returns",
        "gate_type": "MUST_WORK",
        "gate_passed": gate_passed,
        "timestamp": datetime.now().isoformat(),
        "config": {
            "dataset": config.eval.dataset,
            "n_problems": config.eval.n_problems,
            "seed": config.eval.seed,
            "scales": config.scales_order,
        },
        "results": {
            "accuracies": results["accuracies"],
            "kappas": results["kappas"],
            "ordering_satisfied": results["ordering_satisfied"],
            "diminishing_returns": results["diminishing_returns"],
            "diff_7b_70b": results["diff_7b_70b"],
            "diff_70b_prop": results["diff_70b_prop"],
            "kruskal_h": results["kruskal_h"],
            "p_value": results["p_value"],
        },
        "confusion_matrices": results["confusion_matrices"],
    }

    results_path = os.path.join(outputs_dir, "results.json")
    with open(results_path, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"  Saved results to {results_path}")

    print(f"\n{'='*60}")
    print(f"EXPERIMENT COMPLETE")
    print(f"Gate Result: {'PASS' if gate_passed else 'FAIL'}")
    print(f"{'='*60}")

    return output_data


if __name__ == "__main__":
    config = ExperimentConfig()
    results = run_experiment(config)
    sys.exit(0 if results["gate_passed"] else 1)
