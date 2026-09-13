import json
import os
import sys
import torch
import random
import numpy as np

from model import CheckpointLoader
from data import GLUELoader
from evaluate import ZeroShotEvaluator
from visualize import plot_gate_metrics, generate_performance_table
import config


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def validate_memory(loader: CheckpointLoader, threshold_gb: float) -> bool:
    stats = loader.get_memory_stats()
    peak = stats["peak_gb"]
    return peak < threshold_gb


def validate_gates(results: dict, loader: CheckpointLoader) -> dict:
    gates = {
        "checkpoint_loads": "mnli" in results,
        "memory_ok": validate_memory(loader, config.MEMORY_LIMIT_GB),
        "mnli_acc": results["mnli"]["accuracy"] > results["mnli"]["baseline"],
        "qqp_acc": results["qqp"]["accuracy"] > results["qqp"]["baseline"],
        "sst2_acc": results["sst2"]["accuracy"] > results["sst2"]["baseline"]
    }
    return gates


def save_results(results: dict, output_path: str):
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)


def run_experiment(hypothesis_folder: str):
    set_seed(config.RANDOM_SEED)

    config.OUTPUT_DIR = hypothesis_folder
    config.FIGURES_DIR = os.path.join(hypothesis_folder, "figures")
    os.makedirs(config.FIGURES_DIR, exist_ok=True)

    print(f"Loading checkpoint: {config.CHECKPOINT_NAME}")
    loader = CheckpointLoader(config.CHECKPOINT_NAME, config.DEVICE, config.DTYPE)
    model = loader.load_model()
    tokenizer = loader.load_tokenizer()

    print(f"Memory stats: {loader.get_memory_stats()}")

    print("Loading GLUE datasets")
    data_loader = GLUELoader(config.GLUE_TASKS)

    print("Running zero-shot evaluation")
    evaluator = ZeroShotEvaluator(model, tokenizer, config.DEVICE)

    results = {}
    MAX_SAMPLES = 100  # Sample subset for quick PoC validation
    for task in config.GLUE_TASKS:
        print(f"\nEvaluating {task}")
        dataset = data_loader.load_task(task)
        results[task] = evaluator.evaluate_task(dataset, task, max_samples=MAX_SAMPLES)
        print(f"{task} accuracy: {results[task]['accuracy']:.3f} (baseline: {results[task]['baseline']:.3f})")

    gates = validate_gates(results, loader)
    results["gates"] = gates
    results["memory_stats"] = loader.get_memory_stats()

    print("\nGate validation:")
    for gate, passed in gates.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {gate}: {status}")

    output_path = os.path.join(hypothesis_folder, "results.json")
    save_results(results, output_path)
    print(f"\nResults saved to {output_path}")

    print("Generating visualizations")
    plot_gate_metrics(results, config.FIGURES_DIR)
    generate_performance_table(results, config.FIGURES_DIR)
    print(f"Figures saved to {config.FIGURES_DIR}")

    all_passed = all(gates.values())
    print(f"\nMUST_WORK gate: {'PASS' if all_passed else 'FAIL'}")

    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        hypothesis_folder = sys.argv[1]
    else:
        hypothesis_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    results = run_experiment(hypothesis_folder)
    sys.exit(0 if all(results["gates"].values()) else 1)
