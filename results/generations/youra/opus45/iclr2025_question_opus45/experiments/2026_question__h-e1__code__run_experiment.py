"""End-to-end experiment runner for h-e1 SEDP validation."""

import os
import sys
from pathlib import Path

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import ExperimentConfig
from data_pipeline import DataPipeline
from evaluate import (
    compute_metrics,
    plot_gate_metrics,
    plot_roc_curves,
    plot_scatter,
    save_results,
)
from se_labels import SELabelGenerator
from similarity_features import SimilarityFeatureExtractor
from train import train_sedp, train_sep


def run(config: ExperimentConfig) -> dict:
    """Run full SEDP experiment pipeline.

    Returns:
        dict with 'sep', 'sedp' metrics and 'gate_pass' boolean
    """
    print("=" * 60)
    print("H-E1 SEDP Existence Validation Experiment")
    print("=" * 60)

    # Ensure directories exist
    Path(config.cache_dir).mkdir(parents=True, exist_ok=True)
    Path(config.figures_dir).mkdir(parents=True, exist_ok=True)

    # Step 1: Load dataset
    print("\n[Step 1/7] Loading dataset...")
    pipeline = DataPipeline(config)
    train_qs, test_qs = pipeline.load_dataset()

    # Step 2: Generate responses and extract hidden states
    print("\n[Step 2/7] Generating responses (train)...")
    hidden_train, responses_train = pipeline.load_or_generate(train_qs, "train")
    print(f"Train hidden states shape: {hidden_train.shape}")

    print("\n[Step 3/7] Generating responses (test)...")
    hidden_test, responses_test = pipeline.load_or_generate(test_qs, "test")
    print(f"Test hidden states shape: {hidden_test.shape}")

    # Step 4: Compute SE labels
    print("\n[Step 4/7] Computing SE labels...")
    se_generator = SELabelGenerator(config)
    se_cont_train, se_bin_train = se_generator.load_or_compute(responses_train, "train")
    se_cont_test, se_bin_test = se_generator.load_or_compute(responses_test, "test")

    # Step 5: Extract similarity features
    print("\n[Step 5/7] Extracting similarity features...")
    sim_extractor = SimilarityFeatureExtractor(config)
    sim_train = sim_extractor.load_or_extract(responses_train, "train")
    sim_test = sim_extractor.load_or_extract(responses_test, "test")

    # Step 6: Train probes
    print("\n[Step 6/7] Training probes...")
    sep_model = train_sep(config, hidden_train, se_bin_train)
    sedp_model = train_sedp(config, hidden_train, sim_train, se_bin_train)

    # Step 7: Evaluate
    print("\n[Step 7/7] Evaluating...")
    sep_proba = sep_model.predict_proba(hidden_test)
    sedp_proba = sedp_model.predict_proba(hidden_test, sim_test)

    sep_metrics = compute_metrics(sep_proba, se_cont_test, se_bin_test)
    sedp_metrics = compute_metrics(sedp_proba, se_cont_test, se_bin_test)

    print("\nSEP Metrics:", sep_metrics)
    print("SEDP Metrics:", sedp_metrics)

    # Gate check
    gate_pass = sedp_metrics["spearman_rho"] >= config.rho_threshold

    print("\n" + "=" * 60)
    print(f"GATE CHECK: SEDP rho = {sedp_metrics['spearman_rho']:.4f} "
          f"{'≥' if gate_pass else '<'} {config.rho_threshold}")
    print(f"GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")
    print("=" * 60)

    # Generate figures
    print("\nGenerating figures...")
    plot_gate_metrics(
        sep_metrics,
        sedp_metrics,
        os.path.join(config.figures_dir, "gate_metrics.png"),
    )
    plot_scatter(
        sep_proba,
        sedp_proba,
        se_cont_test,
        os.path.join(config.figures_dir, "scatter.png"),
    )
    plot_roc_curves(
        sep_proba,
        sedp_proba,
        se_bin_test,
        os.path.join(config.figures_dir, "roc_curves.png"),
    )

    # Save results
    save_results(sep_metrics, sedp_metrics, config.results_path, gate_pass)

    return {
        "sep": sep_metrics,
        "sedp": sedp_metrics,
        "gate_pass": gate_pass,
    }


if __name__ == "__main__":
    config = ExperimentConfig()
    results = run(config)
    print("\nExperiment complete!")
    print(f"Results saved to {config.results_path}")
