#!/usr/bin/env python3
"""H-M2 Full Experiment: 7-variant training, evaluation, gate check."""
import json
import argparse
from pathlib import Path
from datetime import datetime

from config import VARIANTS, EvalConfig
from train_variants import run_all
from evaluate import evaluate_all
from aggregate import compute_gate, results_table
from visualize import generate_all_plots
from data import load_ifeval_split


def run_full_experiment(
    output_dir: Path,
    max_steps: int = 100,
    skip_training: bool = False
):
    """Run complete H-M2 experiment."""
    output_dir.mkdir(parents=True, exist_ok=True)
    start_time = datetime.now()

    print("=" * 60)
    print("H-M2: 7-Variant IFEval Gate Experiment")
    print(f"Output: {output_dir}")
    print(f"Max PPO steps per variant: {max_steps}")
    print("=" * 60)

    # Stage 1: Training
    if skip_training:
        print("\n[Stage 1] Skipping training (--skip-training)")
        run_results_path = output_dir / "run_results.json"
        if run_results_path.exists():
            with open(run_results_path) as f:
                run_results = json.load(f)
        else:
            print("ERROR: No run_results.json found. Cannot skip training.")
            return None
    else:
        print("\n[Stage 1] Training 7 variants...")
        run_results = run_all(VARIANTS, output_dir, max_steps=max_steps)
        with open(output_dir / "run_results.json", "w") as f:
            json.dump(run_results, f, indent=2)
        print(f"Training results saved.")

    # Stage 2: Evaluation
    print("\n[Stage 2] Evaluating on held-out IFEval test split...")
    _, ifeval_test = load_ifeval_split(seed=1)
    print(f"Test set size: {len(ifeval_test)}")

    eval_results = evaluate_all(run_results, ifeval_test)
    with open(output_dir / "eval_results.json", "w") as f:
        json.dump(eval_results, f, indent=2)

    # Stage 3: Gate computation
    print("\n[Stage 3] Computing gate...")
    gate = compute_gate(eval_results)
    with open(output_dir / "gate_result.json", "w") as f:
        json.dump(gate, f, indent=2)

    print("\n" + "=" * 60)
    print("GATE RESULT:")
    print(f"  Baseline max (B1/B2/B3): {gate.get('baseline_max', 'N/A'):.1%}" if gate.get('baseline_max') else "  Baseline max: N/A")
    print(f"  Best treatment: {gate.get('best_ti', 'N/A')} @ {gate.get('best_ti_score', 0):.1%}" if gate.get('best_ti') else "  Best treatment: N/A")
    print(f"  Delta: {gate.get('delta_pp', 0):.1%} (need ≥2pp)")
    print(f"  GATE {'PASSED' if gate.get('gate_passed') else 'FAILED'}")
    print("=" * 60)

    # Stage 4: Results table
    df = results_table(eval_results)
    df.to_csv(output_dir / "results.csv", index=False)
    print("\nResults Table:")
    print(df.to_string(index=False))

    # Stage 5: Visualization
    print("\n[Stage 5] Generating plots...")
    figures_dir = output_dir / "figures"
    generate_all_plots(eval_results, gate, figures_dir)

    # Summary
    elapsed = datetime.now() - start_time
    print(f"\nExperiment completed in {elapsed}")

    return {
        "gate": gate,
        "eval_results": eval_results,
        "elapsed_seconds": elapsed.total_seconds(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, default="outputs")
    parser.add_argument("--max-steps", type=int, default=100)
    parser.add_argument("--skip-training", action="store_true")
    args = parser.parse_args()

    output_dir = Path(__file__).parent / args.output_dir
    result = run_full_experiment(output_dir, args.max_steps, args.skip_training)

    if result:
        print("\n=== FINAL VERDICT ===")
        if result["gate"].get("gate_passed"):
            print("✓ H-M2 VALIDATED: Bidirectional models improve IFEval by ≥2pp")
        else:
            print("✗ H-M2 NOT VALIDATED: No treatment exceeded baseline + 2pp")
