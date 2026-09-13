"""Main experiment pipeline for H-E1."""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from config import CONFIG
from data.prepare_subsets import C4SubsetSampler
from metrics.quality import QualityMetricsComputer
from metrics.density import InformationDensityComputer
from analysis.correlate import correlate_all_components, check_gate, save_results
import pandas as pd
import json

def load_texts(subset_path: str):
    """Load texts from JSONL."""
    texts = []
    with open(subset_path, 'r') as f:
        for line in f:
            sample = json.loads(line)
            texts.append(sample["text"])
    return texts

def main():
    """Full experiment pipeline."""
    print("=== H-E1 Quality Metrics Correlation Study ===")

    # Create output directories
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    os.makedirs(CONFIG["data_dir"], exist_ok=True)
    os.makedirs(CONFIG["plots_dir"], exist_ok=True)

    # Step 1: Generate subsets
    print("\n[1/5] Generating C4 subsets...")
    sampler = C4SubsetSampler(
        output_dir=CONFIG["data_dir"],
        subset_size_gb=CONFIG["subset_size_gb"],
        seed=CONFIG["seed"]
    )
    subset_paths = sampler.generate_all_subsets()
    print(f"Generated {len(subset_paths)} subsets")

    # Step 2: Compute quality metrics
    print("\n[2/5] Computing quality metrics...")
    qm_computer = QualityMetricsComputer(
        model_name=CONFIG["perplexity_model"],
        device=CONFIG["device"]
    )
    quality_metrics = []
    for i, path in enumerate(subset_paths):
        print(f"  Processing subset {i+1}/{len(subset_paths)}...")
        metrics = qm_computer.compute_all(path)
        quality_metrics.append(metrics)

    # Step 3: Compute information density
    print("\n[3/5] Computing information density...")
    id_computer = InformationDensityComputer(
        embedder_name=CONFIG["embedder_model"]
    )
    density_scores = []
    for i, path in enumerate(subset_paths):
        print(f"  Processing subset {i+1}/{len(subset_paths)}...")
        texts = load_texts(path)
        density = id_computer.compute_combined_density(texts)
        density_scores.append(density)

    # Step 4: Build metrics DataFrame
    print("\n[4/5] Running correlation analysis...")
    metrics_df = pd.DataFrame(quality_metrics)
    metrics_df['info_density'] = density_scores
    metrics_df.to_csv(os.path.join(CONFIG["output_dir"], 'metrics_results.csv'), index=False)

    # Step 5: Correlation analysis
    correlation_results = correlate_all_components(metrics_df)
    save_results(correlation_results, os.path.join(CONFIG["output_dir"], 'correlation_results.csv'))

    # Gate decision
    print("\n[5/5] Gate decision...")
    gate = check_gate(
        correlation_results,
        r_threshold=CONFIG["correlation_threshold_r"],
        p_threshold=CONFIG["significance_threshold_p"]
    )

    print("\n=== Results ===")
    print(correlation_results)
    print(f"\nGate Decision: {gate}")

    # Save gate decision
    with open(os.path.join(CONFIG["output_dir"], 'gate_decision.txt'), 'w') as f:
        f.write(f"Gate: {gate}\n\n")
        f.write(correlation_results.to_string())

if __name__ == "__main__":
    main()
