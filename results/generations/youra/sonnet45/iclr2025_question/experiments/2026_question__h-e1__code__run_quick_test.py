"""Quick test run for validation - 4 conditions × 3 seeds = 12 experiments."""

import torch
import pandas as pd
import json
from pathlib import Path

from config import ExperimentConfig
from data import load_dataset
from model import create_model
from train import set_seed_deterministic, train_model
from evaluate import evaluate_model, compute_variance_metrics, check_gate_condition
from visualize import generate_all_figures

# Quick test configuration - reduced seeds
config = ExperimentConfig()
config.seeds = list(range(3))  # Only 3 seeds for quick test
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Running quick test: {len(config.get_conditions())} conditions × {len(config.seeds)} seeds = {len(config.get_conditions()) * len(config.seeds)} experiments")
print(f"Device: {device}\n")

results = []
for dataset, architecture in config.get_conditions():
    for seed in config.seeds:
        set_seed_deterministic(seed)
        train_loader, test_loader = load_dataset(dataset, config.data_root, config.batch_size, seed)
        model = create_model(architecture).to(device)
        train_model(model, train_loader, config.epochs, config.lr, config.momentum, device)
        test_accuracy = evaluate_model(model, test_loader, device)
        
        results.append({
            "dataset": dataset,
            "architecture": architecture,
            "seed": seed,
            "test_accuracy": test_accuracy
        })
        print(f"✓ {dataset}, {architecture}, seed {seed}: {test_accuracy:.2f}%")

results_df = pd.DataFrame(results)

# Generate variance summary
variance_summary = {}
for (dataset, architecture), group in results_df.groupby(['dataset', 'architecture']):
    condition_name = f"{dataset}, {architecture}"
    accuracies = group['test_accuracy'].tolist()
    metrics = compute_variance_metrics(accuracies)
    variance_summary[condition_name] = metrics
    print(f"\n{condition_name}: variance = {metrics['variance']:.4f}%²")

# Check gate
gate_result = check_gate_condition(variance_summary, threshold=0.3)
print(f"\nGate Result: {gate_result['gate_result']}")
print(f"Conditions passed: {gate_result['conditions_passed']}/{gate_result['total_conditions']}")

# Save results
Path(config.results_dir).mkdir(parents=True, exist_ok=True)
results_df.to_csv(f"{config.results_dir}/experiment_logs.csv", index=False)
with open(f"{config.results_dir}/variance_summary.json", 'w') as f:
    json.dump(variance_summary, f, indent=2)
with open(f"{config.results_dir}/gate_result.json", 'w') as f:
    json.dump(gate_result, f, indent=2)

# Generate figures
try:
    generate_all_figures(results_df, variance_summary, threshold=0.3, figures_dir=config.figures_dir)
    print("\n✅ All outputs generated successfully")
except Exception as e:
    print(f"\n⚠ Figures generation failed: {e}")

print(f"\nFinal Gate: {gate_result['gate_result']}")
