#!/usr/bin/env python3
"""
SVAD Drift Detection Experiment Runner
Hypothesis h-e1: Drift detection classifier validation
"""

import os
import sys
import json
import logging
import torch
import numpy as np
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import get_default_config
from src.data_loader import DatasetPairLoader
from src.feature_extractor import FeatureExtractor
from src.svad_classifier import SVADDriftClassifier
from src.evaluator import ClassificationEvaluator
from src.visualizer import (
    plot_gate_metrics,
    plot_confusion_matrix,
    plot_drift_scores,
    plot_per_dataset_performance
)


def setup_logging(log_path: str):
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )


def main():
    """Main experiment loop."""

    # Load configuration
    config = get_default_config()

    # Setup directories
    base_dir = Path(__file__).parent
    config.data_root = str(base_dir / "data")
    config.output_dir = str(base_dir / "output")
    config.figures_dir = str(base_dir.parent / "figures")

    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    # Setup logging
    log_path = str(base_dir.parent / "experiment.log")
    setup_logging(log_path)

    logging.info("="*80)
    logging.info("SVAD Drift Detection Experiment - Hypothesis h-e1")
    logging.info("="*80)
    logging.info(f"Configuration: {config}")

    # Set random seeds
    torch.manual_seed(config.seed)
    np.random.seed(config.seed)

    # Check device
    device = config.device if torch.cuda.is_available() else "cpu"
    logging.info(f"Using device: {device}")

    # Initialize components
    logging.info("\n[1/6] Initializing components...")
    data_loader = DatasetPairLoader(config.data_root)
    evaluator = ClassificationEvaluator()

    # Load all dataset pairs
    logging.info("\n[2/6] Loading dataset pairs...")
    all_pairs = data_loader.get_all_pairs()
    logging.info(f"Loaded {len(all_pairs)} dataset pairs")

    if len(all_pairs) == 0:
        logging.error("No dataset pairs loaded! Exiting.")
        return

    # Process each dataset pair
    logging.info("\n[3/6] Processing dataset pairs...")

    dataset_names = []
    results_list = []

    for i, (dataset_name, v_old, v_new, true_label) in enumerate(all_pairs):
        logging.info(f"\n--- [{i+1}/{len(all_pairs)}] Processing: {dataset_name} ---")
        logging.info(f"  True label: {true_label}")
        logging.info(f"  v_old shape: {v_old.shape}, v_new shape: {v_new.shape}")

        dataset_names.append(dataset_name)

        try:
            # Determine modality and feature extractor
            if len(v_old.shape) == 4:  # Vision data [N, C, H, W]
                model_type = "resnet50"
            else:  # NLP data [N, seq_len]
                model_type = "bert-base"

            logging.info(f"  Using {model_type} feature extractor")

            # Extract features
            extractor = FeatureExtractor(model_type=model_type, device=device)

            logging.info("  Extracting features from v_old...")
            feat_old = extractor.extract_features(v_old, batch_size=config.batch_size)

            logging.info("  Extracting features from v_new...")
            feat_new = extractor.extract_features(v_new, batch_size=config.batch_size)

            logging.info(f"  Feature dimensions: {feat_old.shape}")

            # Classify with SVAD
            logging.info("  Running SVAD drift classification...")
            classifier = SVADDriftClassifier(
                n_pca_components=config.n_pca_components,
                thresholds=config.thresholds
            )

            classifier.fit_reference(feat_old)
            pred_label, scores = classifier.classify_version_change(feat_new)

            logging.info(f"  Predicted label: {pred_label}")
            logging.info(f"  Drift scores: KS={scores['ks_score']:.4f}, MMD={scores['mmd_score']:.4f}, Max={scores['max_score']:.4f}")

            # Store result
            evaluator.add_prediction(true_label, pred_label, scores)

            results_list.append({
                'dataset': dataset_name,
                'true_label': true_label,
                'pred_label': pred_label,
                'correct': true_label == pred_label,
                'scores': scores
            })

            # Clean up
            del extractor
            torch.cuda.empty_cache()

        except Exception as e:
            logging.error(f"  Error processing {dataset_name}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Compute metrics
    logging.info("\n[4/6] Computing evaluation metrics...")
    metrics = evaluator.compute_metrics()
    confusion_mat = evaluator.get_confusion_matrix()

    logging.info("\nMetrics:")
    for key, value in metrics.items():
        logging.info(f"  {key}: {value:.4f}")

    logging.info(f"\nConfusion Matrix:\n{confusion_mat}")

    # Check gate condition
    logging.info("\n[5/6] Checking gate condition...")
    gate_passed, gate_metrics = evaluator.check_gate_condition(
        target_precision=config.target_precision,
        target_recall=config.target_recall
    )

    logging.info(f"  Gate passed: {gate_passed}")
    logging.info(f"  Precision (MAJOR): {gate_metrics['precision_major']:.4f} (target: {gate_metrics['target_precision']:.4f})")
    logging.info(f"  Recall (MAJOR): {gate_metrics['recall_major']:.4f} (target: {gate_metrics['target_recall']:.4f})")

    # Generate visualizations
    logging.info("\n[6/6] Generating visualizations...")

    plot_gate_metrics(
        metrics,
        str(Path(config.figures_dir) / "gate_metrics.png"),
        target_precision=config.target_precision,
        target_recall=config.target_recall
    )
    logging.info("  ✓ gate_metrics.png")

    plot_confusion_matrix(
        confusion_mat,
        str(Path(config.figures_dir) / "confusion_matrix.png")
    )
    logging.info("  ✓ confusion_matrix.png")

    plot_drift_scores(
        results_list,
        str(Path(config.figures_dir) / "drift_scores.png")
    )
    logging.info("  ✓ drift_scores.png")

    plot_per_dataset_performance(
        results_list,
        dataset_names,
        str(Path(config.figures_dir) / "per_dataset_performance.png")
    )
    logging.info("  ✓ per_dataset_performance.png")

    # Save results to JSON
    results_output = {
        "hypothesis_id": "h-e1",
        "experiment_name": "SVAD Drift Detection Classifier",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "n_pca_components": config.n_pca_components,
            "thresholds": config.thresholds,
            "seed": config.seed
        },
        "metrics": metrics,
        "gate_condition": {
            "passed": gate_passed,
            "precision_major": gate_metrics['precision_major'],
            "recall_major": gate_metrics['recall_major'],
            "target_precision": gate_metrics['target_precision'],
            "target_recall": gate_metrics['target_recall']
        },
        "confusion_matrix": confusion_mat.tolist(),
        "per_dataset_results": results_list,
        "total_datasets": len(all_pairs),
        "successful_classifications": len(results_list)
    }

    results_path = str(base_dir.parent / "04_results.json")
    with open(results_path, 'w') as f:
        json.dump(results_output, f, indent=2)

    logging.info(f"\n✓ Results saved to: {results_path}")

    # Final summary
    logging.info("\n" + "="*80)
    logging.info("EXPERIMENT COMPLETE")
    logging.info("="*80)
    logging.info(f"Overall Accuracy: {metrics.get('accuracy', 0):.2%}")
    logging.info(f"Gate Passed: {'✓ YES' if gate_passed else '✗ NO'}")
    logging.info("="*80)


if __name__ == "__main__":
    main()
