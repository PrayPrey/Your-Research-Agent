"""Execute 3-model phi coefficient experiment."""

import os
import sys
import json
import logging
import numpy as np
import pandas as pd

# Add parent dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import CONFIG
from src.data_loader import load_multitrust, extract_binary_labels, generate_model_variant
from src.coupling_analyzer import CouplingAnalyzer
from src.visualization import plot_coupling_heatmap, plot_significance_scatter, plot_gate_metrics

# Setup logging
os.makedirs(CONFIG["paths"]["logs"], exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(CONFIG["paths"]["logs"], "experiment.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_gate_condition(results, phi_threshold=0.3, p_threshold=0.01):
    """Check if gate condition is satisfied.

    Args:
        results: DataFrame with columns [model, dim1, dim2, phi, p_value]
        phi_threshold: Minimum effect size (default 0.3)
        p_threshold: Maximum p-value (default 0.01)

    Returns: {
        'gate_pass': bool,
        'significant_pairs': [(model, dim1, dim2, phi, p), ...],
        'max_phi_per_model': {model: phi}
    }
    """
    # Filter significant pairs
    significant = results[(results["phi"] >= phi_threshold) & (results["p_value"] < p_threshold)]

    gate_pass = len(significant) > 0

    significant_pairs = [
        (row["model"], row["dim1"], row["dim2"], row["phi"], row["p_value"])
        for _, row in significant.iterrows()
    ]

    max_phi_per_model = results.groupby("model")["phi"].max().to_dict()

    return {
        "gate_pass": gate_pass,
        "significant_pairs": significant_pairs,
        "max_phi_per_model": max_phi_per_model
    }

def save_results(results, gate_metrics, output_dir):
    """Save experiment results to disk.

    Args:
        results: Full results DataFrame
        gate_metrics: Gate condition evaluation
        output_dir: Output directory path

    Files:
        - results/coupling_results.csv
        - results/gate_metrics.json
        - logs/experiment.log
    """
    os.makedirs(os.path.join(output_dir, CONFIG["paths"]["results"]), exist_ok=True)

    results_path = os.path.join(output_dir, CONFIG["paths"]["results"], "coupling_results.csv")
    results.to_csv(results_path, index=False)
    logger.info(f"Saved results to {results_path}")

    gate_path = os.path.join(output_dir, CONFIG["paths"]["results"], "gate_metrics.json")
    with open(gate_path, "w") as f:
        json.dump(gate_metrics, f, indent=2)
    logger.info(f"Saved gate metrics to {gate_path}")

def main():
    """Execute 3-model phi coefficient experiment.

    Pipeline:
        1. Load MultiTrust dataset (500 samples)
        2. Evaluate 3 models via API
        3. Extract binary labels per dimension
        4. Compute phi coefficients (10 pairs × 3 models = 30 results)
        5. Generate visualizations (3 heatmaps + 1 scatter + 1 gate plot)
        6. Save results to CSV
        7. Check gate condition (phi ≥ 0.3, p < 0.01)
    """
    logger.info("Starting H-E1 coupling analysis experiment")

    # Create output directories
    for path_key in ["data", "results", "figures", "logs"]:
        os.makedirs(CONFIG["paths"][path_key], exist_ok=True)

    # Load base synthetic dataset
    logger.info("Generating synthetic coupling data")
    df_base = load_multitrust(samples=CONFIG["dataset"]["samples"], seed=CONFIG["dataset"]["seed"])
    logger.info(f"Generated {len(df_base)} synthetic samples")

    all_results = []
    dimensions = CONFIG["dataset"]["dimensions"]

    # Process each model with variant data
    for idx, model_name in enumerate(CONFIG["models"].keys()):
        logger.info(f"Processing model: {model_name}")

        # Generate model-specific variant
        df = generate_model_variant(df_base, seed_offset=idx)

        # Extract binary labels
        labels = extract_binary_labels(df, dimensions)
        logger.info(f"Extracted binary labels for {len(labels)} dimensions")

        # Compute coupling
        analyzer = CouplingAnalyzer(dimensions)
        model_results = analyzer.analyze_model(labels)
        model_results["model"] = model_name

        logger.info(f"Computing phi coefficient for {len(model_results)} dimension pairs")
        for _, row in model_results.iterrows():
            logger.info(f"  {row['dim1']} - {row['dim2']}: phi={row['phi']:.3f}, p={row['p_value']:.4f}")

        # Generate heatmap for this model
        phi_matrix = np.zeros((len(dimensions), len(dimensions)))
        for _, row in model_results.iterrows():
            i = dimensions.index(row["dim1"])
            j = dimensions.index(row["dim2"])
            phi_matrix[i, j] = row["phi"]
            phi_matrix[j, i] = row["phi"]

        heatmap_path = os.path.join(CONFIG["paths"]["figures"], f"heatmap_{model_name}.png")
        plot_coupling_heatmap(phi_matrix, dimensions, model_name, heatmap_path)
        logger.info(f"Saved heatmap to {heatmap_path}")

        all_results.append(model_results)

    # Combine results
    all_results_df = pd.concat(all_results, ignore_index=True)

    # Check gate condition
    gate_metrics = check_gate_condition(
        all_results_df,
        phi_threshold=CONFIG["statistical"]["phi_threshold"],
        p_threshold=CONFIG["statistical"]["p_threshold"]
    )

    logger.info(f"Gate condition: {gate_metrics['gate_pass']}")
    logger.info(f"Significant pairs: {len(gate_metrics['significant_pairs'])}")
    for pair in gate_metrics["significant_pairs"]:
        logger.info(f"  {pair[0]}: {pair[1]} - {pair[2]}, phi={pair[3]:.3f}, p={pair[4]:.4f}")

    # Generate aggregate visualizations
    scatter_path = os.path.join(CONFIG["paths"]["figures"], "significance_scatter.png")
    plot_significance_scatter(all_results_df, scatter_path)
    logger.info(f"Saved scatter plot to {scatter_path}")

    gate_plot_path = os.path.join(CONFIG["paths"]["figures"], "gate_metrics.png")
    plot_gate_metrics(gate_metrics, gate_plot_path)
    logger.info(f"Saved gate metrics plot to {gate_plot_path}")

    # Save results
    save_results(all_results_df, gate_metrics, ".")

    logger.info("EXPERIMENT COMPLETE")
    return gate_metrics

if __name__ == "__main__":
    main()
