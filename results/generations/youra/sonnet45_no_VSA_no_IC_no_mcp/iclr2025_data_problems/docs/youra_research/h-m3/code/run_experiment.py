"""Main experiment runner for h-m3."""
import yaml
import json
from pathlib import Path
import sys


def load_config(config_path: str = "config/experiment_config.yaml") -> dict:
    """Load experiment config."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def save_timings(timings: dict, path: str) -> None:
    """Save timing logs."""
    with open(path, "w") as f:
        yaml.dump(timings, f)
    print(f"✓ Saved timings to {path}")


def run_full_experiment():
    """Run complete h-m3 experiment pipeline."""
    print("=" * 80)
    print("H-M3: EMBEDDING-STAGE MISMATCH EXPERIMENT")
    print("=" * 80)

    config = load_config()

    # Step 1: Load dataset
    print("\n[1/6] Loading dataset...")
    from load_data import load_and_format_dolly
    dataset, texts = load_and_format_dolly(config["dataset"]["cache_dir"])

    # Step 2: Generate embeddings
    print("\n[2/6] Generating embeddings...")
    from embed_corpus import generate_all_embeddings
    embedding_results = generate_all_embeddings(texts, config)

    # Step 3: k-center greedy selection
    print("\n[3/6] Running k-center greedy selection...")
    from k_center_greedy import select_all_subsets
    selection_results = select_all_subsets(config)

    # Aggregate timings
    timings = {}
    for stage in ["early", "mid", "late"]:
        embed_time = embedding_results[stage]["time"]
        # Avg selection time across k values
        selection_times = [
            selection_results[f"{stage}_k{k}"]["time"]
            for k in config["dataset"]["subset_sizes"]
        ]
        avg_selection_time = sum(selection_times) / len(selection_times)

        timings[stage] = embed_time + avg_selection_time

    save_timings(timings, "data/timing_logs.yaml")

    # Step 4: Fine-tune models
    print("\n[4/6] Fine-tuning models...")
    from train import train_all_conditions
    train_results = train_all_conditions(config)

    # Step 5: Evaluate models
    print("\n[5/6] Evaluating models...")
    from evaluate import evaluate_all_models
    scores_df = evaluate_all_models(config)

    # Step 6: Analyze results
    print("\n[6/6] Analyzing results...")
    from analyze import analyze_results
    metrics = analyze_results(config, timings)

    # Final summary
    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)
    print(f"\nGate result: {metrics['gate_result']}")
    print(f"  Stage-mismatch penalty: {metrics['stage_mismatch_penalty']:.4f} (≥0.02: {metrics['pass_penalty']})")
    print(f"  Quality bound: {metrics['quality_bound']:.4f} (≤0.01: {metrics['pass_quality']})")
    print(f"  Cost ratio: {metrics['cost_ratio']:.2f}x (≥3.0: {metrics['pass_speed']})")

    # Save gate result
    gate_result_path = "results/gate_check.yaml"
    with open(gate_result_path, "w") as f:
        yaml.dump({
            "gate": metrics["gate_result"],
            "criteria": {
                "stage_mismatch_penalty": {
                    "value": float(metrics["stage_mismatch_penalty"]),
                    "threshold": config["success_criteria"]["stage_mismatch_penalty_threshold"],
                    "pass": bool(metrics["pass_penalty"])
                },
                "quality_bound": {
                    "value": float(metrics["quality_bound"]),
                    "threshold": config["success_criteria"]["quality_bound_threshold"],
                    "pass": bool(metrics["pass_quality"])
                },
                "cost_ratio": {
                    "value": float(metrics["cost_ratio"]),
                    "threshold": config["success_criteria"]["speed_advantage_threshold"],
                    "pass": bool(metrics["pass_speed"])
                }
            }
        }, f)
    print(f"\n✓ Saved gate check to {gate_result_path}")

    return metrics


if __name__ == "__main__":
    try:
        metrics = run_full_experiment()
        sys.exit(0 if metrics["gate_result"] == "PASS" else 1)
    except Exception as e:
        print(f"\n❌ Experiment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
