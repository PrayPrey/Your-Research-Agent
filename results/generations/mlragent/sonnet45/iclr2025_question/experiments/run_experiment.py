"""
Main experiment runner for Semantic Consistency Graph experiments.
"""

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

import config
from data import ConversationGenerator, save_dataset, load_dataset
from model import SCGDetector
from uncertainty import PerplexityBaseline, SelfCheckGPTBaseline, SemanticEmbeddingBaseline
from evaluation import (
    EvaluationMetrics, plot_model_comparison, plot_error_analysis,
    plot_hallucination_rate_by_domain
)
from utils import set_random_seed, save_results, Logger, split_dataset


def generate_or_load_dataset(logger):
    """Generate or load dataset."""
    dataset_path = os.path.join(config.DATA_DIR, "synthetic_conversations.json")

    if os.path.exists(dataset_path):
        logger.log(f"Loading existing dataset from {dataset_path}")
        dataset = load_dataset("synthetic_conversations.json")
    else:
        logger.log("Generating new dataset...")
        generator = ConversationGenerator()
        dataset = generator.generate_dataset(config.NUM_SYNTHETIC_CONVERSATIONS)
        save_dataset(dataset, "synthetic_conversations.json")

    logger.log(f"Dataset loaded: {len(dataset)} conversations")
    with_contradictions = sum(1 for d in dataset if d["annotation"]["has_contradiction"])
    logger.log(f"  - With contradictions: {with_contradictions}")
    logger.log(f"  - Without contradictions: {len(dataset) - with_contradictions}")

    return dataset


def evaluate_model(model, dataset, model_name, logger):
    """Evaluate a single model on the dataset."""
    logger.log(f"\nEvaluating {model_name}...")

    metrics_tracker = EvaluationMetrics()
    predictions = []

    for data in tqdm(dataset, desc=f"Evaluating {model_name}"):
        conversation = data["conversation"]
        true_label = data["annotation"]["has_contradiction"]

        # Get prediction
        try:
            prediction = model.predict(conversation)
            predicted_label = prediction["has_hallucination"]
            score = prediction["uncertainty_score"]
        except Exception as e:
            logger.log(f"Error in {model_name} prediction: {str(e)}")
            predicted_label = False
            score = 0.0
            prediction = {
                "has_hallucination": False,
                "uncertainty_score": 0.0,
                "num_contradictions": 0
            }

        metrics_tracker.add_prediction(true_label, predicted_label, score)
        predictions.append(prediction)

    # Compute metrics
    metrics = metrics_tracker.compute_metrics()
    logger.log(f"{model_name} Results:")
    logger.log(f"  Precision: {metrics['precision']:.4f}")
    logger.log(f"  Recall: {metrics['recall']:.4f}")
    logger.log(f"  F1 Score: {metrics['f1']:.4f}")
    logger.log(f"  Accuracy: {metrics['accuracy']:.4f}")
    logger.log(f"  AUC: {metrics['auc']:.4f}")

    return metrics, metrics_tracker, predictions


def plot_uncertainty_distribution(all_predictions, dataset, save_path):
    """Plot uncertainty score distributions."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    models = list(all_predictions.keys())
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for idx, model in enumerate(models):
        predictions = all_predictions[model]

        # Separate scores by true label
        scores_with_contradiction = []
        scores_without_contradiction = []

        for i, data in enumerate(dataset):
            true_label = data["annotation"]["has_contradiction"]
            score = predictions[i]["uncertainty_score"]

            if true_label:
                scores_with_contradiction.append(score)
            else:
                scores_without_contradiction.append(score)

        # Plot histogram
        axes[idx].hist(scores_without_contradiction, bins=20, alpha=0.6,
                      label='No Contradiction', color='blue', edgecolor='black')
        axes[idx].hist(scores_with_contradiction, bins=20, alpha=0.6,
                      label='With Contradiction', color='red', edgecolor='black')

        axes[idx].set_xlabel('Uncertainty Score', fontsize=11)
        axes[idx].set_ylabel('Frequency', fontsize=11)
        axes[idx].set_title(f'{model}', fontsize=12, fontweight='bold')
        axes[idx].legend(fontsize=10)
        axes[idx].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_calibration_curves(all_predictions, dataset, save_path):
    """Plot calibration curves for each model."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    models = list(all_predictions.keys())

    for idx, model in enumerate(models):
        predictions = all_predictions[model]

        # Get scores and true labels
        scores = [p["uncertainty_score"] for p in predictions]
        true_labels = [int(d["annotation"]["has_contradiction"]) for d in dataset]

        # Bin predictions
        n_bins = 10
        bins = np.linspace(0, 1, n_bins + 1)
        bin_centers = (bins[:-1] + bins[1:]) / 2

        bin_freq = []
        bin_accuracy = []

        for i in range(n_bins):
            bin_mask = (scores >= bins[i]) & (scores < bins[i + 1])
            if bin_mask.sum() > 0:
                bin_freq.append(bin_mask.sum())
                bin_accuracy.append(np.array(true_labels)[bin_mask].mean())
            else:
                bin_freq.append(0)
                bin_accuracy.append(0)

        # Plot
        axes[idx].plot([0, 1], [0, 1], 'k--', label='Perfect Calibration', linewidth=2)
        axes[idx].scatter(bin_centers, bin_accuracy, s=np.array(bin_freq) * 3,
                         alpha=0.7, label='Actual', color='#1f77b4', edgecolors='black')
        axes[idx].plot(bin_centers, bin_accuracy, '-o', alpha=0.5, color='#1f77b4')

        axes[idx].set_xlabel('Predicted Uncertainty', fontsize=11)
        axes[idx].set_ylabel('Actual Contradiction Rate', fontsize=11)
        axes[idx].set_title(f'{model} - Calibration', fontsize=12, fontweight='bold')
        axes[idx].legend(fontsize=10)
        axes[idx].grid(alpha=0.3)
        axes[idx].set_xlim([0, 1])
        axes[idx].set_ylim([0, 1])

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_contradiction_detection_over_distance(all_predictions, dataset, save_path):
    """Plot detection accuracy vs temporal distance of contradictions."""
    models = list(all_predictions.keys())

    # Collect data
    distance_data = {model: {} for model in models}

    for i, data in enumerate(dataset):
        if not data["annotation"]["has_contradiction"]:
            continue

        distance = data["annotation"]["temporal_distance"]

        for model in models:
            detected = all_predictions[model][i]["has_hallucination"]

            if distance not in distance_data[model]:
                distance_data[model][distance] = []
            distance_data[model][distance].append(int(detected))

    # Compute detection rates
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for idx, model in enumerate(models):
        distances = sorted(distance_data[model].keys())
        rates = [np.mean(distance_data[model][d]) for d in distances]

        ax.plot(distances, rates, marker='o', linewidth=2, markersize=8,
               label=model, color=colors[idx % len(colors)])

    ax.set_xlabel('Temporal Distance (turns)', fontsize=12)
    ax.set_ylabel('Detection Rate', fontsize=12)
    ax.set_title('Contradiction Detection Rate vs Temporal Distance', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)
    ax.set_ylim([0, 1.05])

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def main():
    """Main experiment execution."""
    # Setup
    set_random_seed(config.RANDOM_SEED)
    logger = Logger(os.path.join(config.BASE_DIR, "log.txt"))

    logger.log("=" * 60)
    logger.log("Starting Semantic Consistency Graph Experiments")
    logger.log("=" * 60)
    logger.log(f"Device: {config.DEVICE}")
    logger.log(f"Random seed: {config.RANDOM_SEED}")

    # Generate or load dataset
    dataset = generate_or_load_dataset(logger)

    # Split dataset (we'll use test set for evaluation)
    train_data, val_data, test_data = split_dataset(
        dataset,
        config.TRAIN_SPLIT,
        config.VAL_SPLIT,
        config.TEST_SPLIT
    )
    logger.log(f"\nDataset split:")
    logger.log(f"  Train: {len(train_data)} conversations")
    logger.log(f"  Val: {len(val_data)} conversations")
    logger.log(f"  Test: {len(test_data)} conversations")

    # Use test data for evaluation
    eval_data = test_data

    # Initialize models
    logger.log("\n" + "=" * 60)
    logger.log("Initializing models...")
    logger.log("=" * 60)

    models = {
        "SCG (Proposed)": SCGDetector(),
        "Perplexity Baseline": PerplexityBaseline(),
        "SelfCheckGPT": SelfCheckGPTBaseline(),
        "Semantic Embedding": SemanticEmbeddingBaseline()
    }

    # Evaluate all models
    all_results = {}
    all_metrics_trackers = {}
    all_predictions = {}

    for model_name, model in models.items():
        logger.log("\n" + "=" * 60)
        metrics, tracker, predictions = evaluate_model(model, eval_data, model_name, logger)
        all_results[model_name] = metrics
        all_metrics_trackers[model_name] = tracker
        all_predictions[model_name] = predictions

    # Save results
    logger.log("\n" + "=" * 60)
    logger.log("Saving results...")
    logger.log("=" * 60)

    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    save_results(all_results, "metrics.json", config.RESULTS_DIR)

    # Generate visualizations
    logger.log("\nGenerating visualizations...")

    # Model comparison
    plot_model_comparison(
        all_results,
        os.path.join(config.RESULTS_DIR, "model_comparison.png")
    )
    logger.log("  - Model comparison plot saved")

    # Error analysis
    plot_error_analysis(
        all_results,
        os.path.join(config.RESULTS_DIR, "error_analysis.png")
    )
    logger.log("  - Error analysis plot saved")

    # ROC and PR curves for SCG
    scg_tracker = all_metrics_trackers["SCG (Proposed)"]
    scg_tracker.plot_roc_curve(
        os.path.join(config.RESULTS_DIR, "scg_roc_curve.png")
    )
    logger.log("  - ROC curve saved")

    scg_tracker.plot_precision_recall_curve(
        os.path.join(config.RESULTS_DIR, "scg_pr_curve.png")
    )
    logger.log("  - PR curve saved")

    scg_tracker.plot_confusion_matrix(
        os.path.join(config.RESULTS_DIR, "scg_confusion_matrix.png")
    )
    logger.log("  - Confusion matrix saved")

    # Uncertainty distribution
    plot_uncertainty_distribution(
        all_predictions,
        eval_data,
        os.path.join(config.RESULTS_DIR, "uncertainty_distribution.png")
    )
    logger.log("  - Uncertainty distribution saved")

    # Calibration curves
    plot_calibration_curves(
        all_predictions,
        eval_data,
        os.path.join(config.RESULTS_DIR, "calibration_curves.png")
    )
    logger.log("  - Calibration curves saved")

    # Temporal distance analysis
    plot_contradiction_detection_over_distance(
        all_predictions,
        eval_data,
        os.path.join(config.RESULTS_DIR, "temporal_distance_analysis.png")
    )
    logger.log("  - Temporal distance analysis saved")

    # Domain-specific analysis
    plot_hallucination_rate_by_domain(
        eval_data,
        all_predictions,
        os.path.join(config.RESULTS_DIR, "domain_analysis.png")
    )
    logger.log("  - Domain analysis saved")

    logger.log("\n" + "=" * 60)
    logger.log("Experiments completed successfully!")
    logger.log("=" * 60)

    # Print final summary
    logger.log("\n" + "=" * 60)
    logger.log("FINAL RESULTS SUMMARY")
    logger.log("=" * 60)

    for model_name, metrics in all_results.items():
        logger.log(f"\n{model_name}:")
        logger.log(f"  Precision: {metrics['precision']:.4f}")
        logger.log(f"  Recall: {metrics['recall']:.4f}")
        logger.log(f"  F1 Score: {metrics['f1']:.4f}")
        logger.log(f"  Accuracy: {metrics['accuracy']:.4f}")
        logger.log(f"  AUC: {metrics['auc']:.4f}")

    return all_results


if __name__ == "__main__":
    try:
        results = main()
        print("\nExperiment completed successfully!")
    except Exception as e:
        print(f"\nError in experiment: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
