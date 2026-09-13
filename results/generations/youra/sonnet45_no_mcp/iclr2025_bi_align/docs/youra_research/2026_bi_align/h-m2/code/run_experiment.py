#!/usr/bin/env python3
"""
Main experiment runner for H-M2: Embedding Space Clustering Analysis
Task: task-016 - Experiment orchestration
"""

import yaml
import json
import numpy as np
import torch
from pathlib import Path
from datetime import datetime
import logging
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data.loader import load_hh_rlhf_harmless, extract_response_pairs
from embeddings.extractor import RoBERTaEmbeddingExtractor
from analysis.pca import apply_pca, compute_variance_explained
from analysis.manova import compute_manova_effect_size, baseline_random_separation, gate_decision
from visualization.plots import (
    plot_gate_metrics_comparison,
    plot_pca_scatter,
    plot_effect_size_distribution,
    plot_variance_explained,
    plot_distance_heatmap
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml"):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def run_h_m2_experiment(config_path: str = "config.yaml"):
    """
    Main experiment orchestration.

    Pipeline:
    1. Load HH-RLHF harmless subset
    2. Extract RoBERTa embeddings (chosen + rejected)
    3. Save embeddings to disk (checkpoint)
    4. Apply PCA for visualization
    5. Compute MANOVA effect size
    6. Compute random baseline
    7. Generate visualizations
    8. Return gate decision
    """
    logger.info("="*60)
    logger.info("H-M2 Experiment: Embedding Space Clustering Analysis")
    logger.info("="*60)

    # Load configuration
    config = load_config(config_path)

    # Set random seed
    seed = config["experiment"]["seed"]
    torch.manual_seed(seed)
    np.random.seed(seed)
    logger.info(f"Random seed set to {seed}")

    # Create output directories
    Path(config["outputs"]["data_dir"]).mkdir(parents=True, exist_ok=True)
    Path(config["outputs"]["figures_dir"]).mkdir(parents=True, exist_ok=True)

    # 1. Load dataset
    logger.info("\n" + "="*60)
    logger.info("Step 1: Loading HH-RLHF dataset")
    logger.info("="*60)

    dataset = load_hh_rlhf_harmless(
        dataset_name=config["dataset"]["name"],
        split=config["dataset"]["split"],
        cache_dir=config["dataset"]["cache_dir"]
    )

    max_samples = config["dataset"]["max_samples"]
    chosen_texts, rejected_texts = extract_response_pairs(dataset, max_samples=max_samples)

    logger.info(f"Loaded {len(chosen_texts)} chosen and {len(rejected_texts)} rejected responses")

    # 2. Extract embeddings
    logger.info("\n" + "="*60)
    logger.info("Step 2: Extracting RoBERTa embeddings")
    logger.info("="*60)

    device = config["embedding"]["device"]
    model_name = config["embedding"]["model_name"]
    batch_size = config["embedding"]["batch_size"]
    checkpoint_dir = config["embedding"]["checkpoint_path"]

    extractor = RoBERTaEmbeddingExtractor(model_name=model_name, device=device)

    chosen_emb, rejected_emb = extractor.extract_embeddings(
        chosen_texts,
        rejected_texts,
        batch_size=batch_size,
        checkpoint_dir=checkpoint_dir
    )

    logger.info(f"Embeddings extracted: chosen {chosen_emb.shape}, rejected {rejected_emb.shape}")

    # 3. Apply PCA
    logger.info("\n" + "="*60)
    logger.info("Step 3: Applying PCA dimensionality reduction")
    logger.info("="*60)

    n_viz = config["pca"]["n_components_viz"]
    n_variance = config["pca"]["n_components_variance"]

    # Fit PCA on combined data
    all_emb = np.vstack([chosen_emb, rejected_emb])
    _, pca_model = apply_pca(all_emb, n_components=min(n_variance, all_emb.shape[1]))

    # Transform to 2D for visualization
    chosen_2d = pca_model.transform(chosen_emb)[:, :n_viz]
    rejected_2d = pca_model.transform(rejected_emb)[:, :n_viz]

    # Compute cumulative variance
    cumulative_variance = compute_variance_explained(pca_model, n_variance)

    logger.info(f"PCA 2D variance explained: {cumulative_variance[1]:.3f}")

    # 4. Compute MANOVA effect size
    logger.info("\n" + "="*60)
    logger.info("Step 4: Computing MANOVA effect size")
    logger.info("="*60)

    manova_results = compute_manova_effect_size(chosen_emb, rejected_emb)
    cohens_d = manova_results['cohens_d']

    logger.info(f"Proposed method Cohen's d: {cohens_d:.3f}")

    # 5. Compute random baseline
    logger.info("\n" + "="*60)
    logger.info("Step 5: Computing random baseline")
    logger.info("="*60)

    baseline_trials = config["manova"]["baseline_trials"]
    baseline_seed = config["manova"]["random_seed"]

    baseline_ds = baseline_random_separation(
        all_emb,
        n_trials=baseline_trials,
        seed=baseline_seed
    )
    baseline_d = np.mean(baseline_ds)

    logger.info(f"Random baseline Cohen's d: {baseline_d:.3f}")

    # 6. Gate decision
    logger.info("\n" + "="*60)
    logger.info("Step 6: Gate decision")
    logger.info("="*60)

    primary_threshold = config["gates"]["primary_threshold"]
    secondary_threshold = config["gates"]["secondary_threshold"]

    decision, gate_details = gate_decision(
        cohens_d,
        baseline_d,
        primary_threshold,
        secondary_threshold
    )

    logger.info(f"Gate decision: {decision}")

    # 7. Generate visualizations
    logger.info("\n" + "="*60)
    logger.info("Step 7: Generating visualizations")
    logger.info("="*60)

    figures_dir = Path(config["outputs"]["figures_dir"])

    # Task-011: Gate metrics comparison
    plot_gate_metrics_comparison(
        cohens_d,
        baseline_d,
        primary_threshold,
        str(figures_dir / config["outputs"]["gate_metrics_figure"])
    )

    # Task-012: PCA scatter
    plot_pca_scatter(
        chosen_2d,
        rejected_2d,
        (pca_model.explained_variance_ratio_[0], pca_model.explained_variance_ratio_[1]),
        str(figures_dir / config["outputs"]["pca_scatter_figure"])
    )

    # Task-013: Effect size distribution
    mean_chosen = np.mean(chosen_emb, axis=0)
    mean_rejected = np.mean(rejected_emb, axis=0)
    var_chosen = np.var(chosen_emb, axis=0, ddof=1)
    var_rejected = np.var(rejected_emb, axis=0, ddof=1)
    pooled_std = np.sqrt((var_chosen + var_rejected) / 2)
    per_dim_d = (mean_chosen - mean_rejected) / (pooled_std + 1e-8)

    plot_effect_size_distribution(
        per_dim_d,
        str(figures_dir / config["outputs"]["effect_size_distribution_figure"])
    )

    # Task-014: Variance explained
    plot_variance_explained(
        cumulative_variance,
        str(figures_dir / config["outputs"]["variance_explained_figure"])
    )

    # Task-015: Distance heatmap
    sample_size = 100
    chosen_sample = chosen_emb[:sample_size]
    rejected_sample = rejected_emb[:sample_size]

    plot_distance_heatmap(
        chosen_sample,
        rejected_sample,
        str(figures_dir / config["outputs"]["distance_heatmap_figure"])
    )

    logger.info("All visualizations generated successfully")

    # 8. Save results
    logger.info("\n" + "="*60)
    logger.info("Step 8: Saving results")
    logger.info("="*60)

    results = {
        "experiment": {
            "hypothesis_id": config["experiment"]["hypothesis_id"],
            "timestamp": datetime.now().isoformat(),
            "seed": seed
        },
        "dataset": {
            "name": config["dataset"]["name"],
            "n_samples": len(chosen_texts)
        },
        "metrics": {
            "cohens_d": float(cohens_d),
            "baseline_d_mean": float(baseline_d),
            "baseline_d_std": float(np.std(baseline_ds)),
            "mean_separation": float(manova_results['mean_separation']),
            "f_statistic": float(manova_results['f_statistic']),
            "p_value": float(manova_results['p_value']),
            "pca_variance_2d": float(cumulative_variance[1])
        },
        "gate": {
            "decision": decision,
            "primary_threshold": primary_threshold,
            "secondary_threshold": secondary_threshold,
            "meets_primary": gate_details['meets_primary'],
            "meets_secondary": gate_details['meets_secondary'],
            "exceeds_baseline": gate_details['exceeds_baseline']
        }
    }

    results_file = Path(config["outputs"]["results_file"])
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"Results saved to {results_file}")

    # Summary
    logger.info("\n" + "="*60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info("="*60)
    logger.info(f"Cohen's d (proposed): {cohens_d:.3f}")
    logger.info(f"Cohen's d (baseline): {baseline_d:.3f}")
    logger.info(f"Gate decision: {decision}")
    logger.info("="*60)

    return results


if __name__ == "__main__":
    import sys
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    results = run_h_m2_experiment(config_path)

    # Exit with code based on gate decision
    sys.exit(0 if results["gate"]["decision"] == "PASS" else 1)
