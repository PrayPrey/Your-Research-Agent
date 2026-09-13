"""
Main experiment runner for the Mutual Calibration Framework (MCF).
Implements the full experimental pipeline including:
- Data loading and preprocessing
- Model training for all conditions (Baseline, Transparency+, MCF-Static, MCF-Full)
- Evaluation with simulated human-AI collaboration
- Results aggregation and visualization
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset, random_split
from sklearn.datasets import make_classification
from typing import Dict, List, Tuple


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""
    def default(self, obj):
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    MODEL_CONFIG, TRAINING_CONFIG, LOSS_WEIGHTS,
    EXPERIMENT_CONFIG, SEED, DEVICE, RESULTS_DIR, FIGURES_DIR
)
from models import (
    MutualCalibrationFramework, MCFStatic, BaselineAI, TransparencyPlusAI
)
from human_simulator import HumanBehaviorSimulator, SimulatedUser
from training import MCFTrainer, BaselineTrainer
from evaluation import compute_all_metrics, ExperimentTracker
from visualization import generate_all_figures, plot_expertise_comparison


# Setup logging
def setup_logging(log_path: str):
    """Configure logging to file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def create_synthetic_dataset(
    n_samples: int = 5000,
    n_features: int = 50,
    n_classes: int = 10,
    n_informative: int = 30,
    class_sep: float = 1.0,
    seed: int = 42
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Create synthetic classification dataset for experiments.
    Mimics a realistic task like image classification or medical diagnosis.
    """
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=n_informative,
        n_redundant=10,
        n_clusters_per_class=2,
        n_classes=n_classes,
        class_sep=class_sep,
        flip_y=0.05,  # 5% label noise
        random_state=seed
    )

    # Normalize features
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long)


def compute_task_difficulty(
    X: torch.Tensor,
    y: torch.Tensor,
    model: torch.nn.Module,
    device: str
) -> torch.Tensor:
    """
    Estimate task difficulty based on model uncertainty.
    Higher values = harder samples.
    """
    model.eval()
    with torch.no_grad():
        X_dev = X.to(device)
        if hasattr(model, 'ai_module'):
            probs, conf, _ = model.ai_module(X_dev)
        elif isinstance(model, (BaselineAI, TransparencyPlusAI)):
            if isinstance(model, TransparencyPlusAI):
                probs, conf, _ = model(X_dev)
            else:
                probs, conf = model(X_dev)
        else:
            probs, conf, _ = model.ai_module(X_dev)

        # Difficulty = 1 - confidence (more uncertain = harder)
        difficulty = 1 - conf.squeeze(-1)
    return difficulty.cpu()


def train_and_evaluate_model(
    model_name: str,
    model: torch.nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    test_loader: DataLoader,
    human_simulator: HumanBehaviorSimulator,
    users: Dict[str, List[SimulatedUser]],
    device: str,
    logger: logging.Logger,
    is_mcf: bool = False
) -> Tuple[Dict, Dict]:
    """
    Train model and evaluate on test set with simulated human collaboration.
    """
    logger.info(f"Training {model_name}...")

    # Training
    if is_mcf:
        trainer = MCFTrainer(
            model=model,
            loss_weights=LOSS_WEIGHTS,
            learning_rate=TRAINING_CONFIG["learning_rate"],
            weight_decay=TRAINING_CONFIG["weight_decay"],
            device=device
        )
        # Use intermediate user for training
        train_user = users["intermediate"][0]
        history = trainer.fit(
            train_loader, val_loader,
            epochs=TRAINING_CONFIG["epochs"],
            patience=TRAINING_CONFIG["patience"],
            human_simulator=human_simulator,
            user=train_user
        )
    else:
        trainer = BaselineTrainer(
            model=model,
            learning_rate=TRAINING_CONFIG["learning_rate"],
            weight_decay=TRAINING_CONFIG["weight_decay"],
            device=device
        )
        history = trainer.fit(
            train_loader, val_loader,
            epochs=TRAINING_CONFIG["epochs"],
            patience=TRAINING_CONFIG["patience"]
        )

    # Evaluation across expertise levels
    model.eval()
    results_by_expertise = {}

    for expertise_level in ["novice", "intermediate", "expert"]:
        logger.info(f"  Evaluating with {expertise_level} users...")
        level_results = []

        for user in users[expertise_level]:
            user_metrics = evaluate_with_user(
                model, test_loader, human_simulator, user, device, model_name
            )
            level_results.append(user_metrics)

        # Aggregate results for this expertise level
        aggregated = {}
        for metric in level_results[0].keys():
            values = [r[metric] for r in level_results]
            aggregated[metric] = {
                "mean": np.mean(values),
                "std": np.std(values)
            }
        results_by_expertise[expertise_level] = aggregated

    return history, results_by_expertise


def evaluate_with_user(
    model: torch.nn.Module,
    test_loader: DataLoader,
    human_simulator: HumanBehaviorSimulator,
    user: SimulatedUser,
    device: str,
    model_name: str
) -> Dict[str, float]:
    """
    Evaluate model with a specific simulated user.
    """
    all_ai_preds = []
    all_ai_confs = []
    all_deferences = []
    all_human_decisions = []
    all_human_only = []
    all_true_labels = []
    all_predictions = []

    model.eval()
    with torch.no_grad():
        for batch in test_loader:
            x, y = batch[0].to(device), batch[1].to(device)

            # Get model outputs
            if isinstance(model, MutualCalibrationFramework):
                outputs = model(x)
                predictions = outputs["predictions"]
                confidence = outputs["confidence"].squeeze(-1)
                deference = outputs["deference"].squeeze(-1)
                rec = model.get_recommendation(x)
                recommendation_type = rec["recommendation_type"]
            elif isinstance(model, MCFStatic):
                outputs = model(x)
                predictions = outputs["predictions"]
                confidence = outputs["confidence"].squeeze(-1)
                deference = outputs["deference"].squeeze(-1)
                recommendation_type = None
            elif isinstance(model, TransparencyPlusAI):
                predictions, confidence, importance = model(x)
                confidence = confidence.squeeze(-1)
                deference = None
                recommendation_type = None
            else:  # BaselineAI
                predictions, confidence = model(x)
                confidence = confidence.squeeze(-1)
                deference = None
                recommendation_type = None

            ai_preds = predictions.argmax(dim=1)

            # Human-only decision
            human_only = human_simulator.simulate_human_only_decision(user, y.cpu())

            # Collaborative decision
            human_decisions, _ = human_simulator.simulate_collaborative_decision(
                user, y.cpu(), ai_preds.cpu(), confidence.cpu(),
                deference.cpu() if deference is not None else None,
                recommendation_type
            )

            all_ai_preds.append(ai_preds.cpu())
            all_ai_confs.append(confidence.cpu())
            if deference is not None:
                all_deferences.append(deference.cpu())
            all_human_decisions.append(human_decisions)
            all_human_only.append(human_only)
            all_true_labels.append(y.cpu())
            all_predictions.append(predictions.cpu())

    # Concatenate all batches
    all_ai_preds = torch.cat(all_ai_preds)
    all_ai_confs = torch.cat(all_ai_confs)
    all_human_decisions = torch.cat(all_human_decisions)
    all_human_only = torch.cat(all_human_only)
    all_true_labels = torch.cat(all_true_labels)
    all_predictions = torch.cat(all_predictions)

    if all_deferences:
        all_deferences = torch.cat(all_deferences)
    else:
        all_deferences = None

    # Compute all metrics
    metrics = compute_all_metrics(
        all_ai_preds, all_ai_confs, all_deferences,
        all_human_decisions, all_human_only, all_true_labels,
        all_predictions
    )

    return metrics


def run_experiments(args):
    """Main experiment pipeline."""
    # Setup
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    log_path = os.path.join(RESULTS_DIR, "log.txt")
    logger = setup_logging(log_path)

    logger.info("=" * 60)
    logger.info("Mutual Calibration Framework (MCF) Experiments")
    logger.info("=" * 60)
    logger.info(f"Device: {DEVICE}")
    logger.info(f"Seed: {SEED}")
    logger.info(f"Model Config: {MODEL_CONFIG}")
    logger.info(f"Training Config: {TRAINING_CONFIG}")
    logger.info(f"Loss Weights: {LOSS_WEIGHTS}")

    set_seed(SEED)

    # Create dataset
    logger.info("\nCreating synthetic dataset...")
    X, y = create_synthetic_dataset(
        n_samples=args.n_samples,
        n_features=args.n_features,
        n_classes=args.n_classes,
        seed=SEED
    )
    logger.info(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features, {args.n_classes} classes")

    # Split data
    dataset = TensorDataset(X, y)
    train_size = int(0.7 * len(dataset))
    val_size = int(0.15 * len(dataset))
    test_size = len(dataset) - train_size - val_size

    train_dataset, val_dataset, test_dataset = random_split(
        dataset, [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(SEED)
    )

    train_loader = DataLoader(train_dataset, batch_size=TRAINING_CONFIG["batch_size"], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=TRAINING_CONFIG["batch_size"])
    test_loader = DataLoader(test_dataset, batch_size=TRAINING_CONFIG["batch_size"])

    logger.info(f"Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")

    # Create human simulator and users
    logger.info("\nCreating simulated users...")
    human_simulator = HumanBehaviorSimulator(
        num_classes=args.n_classes,
        seed=SEED
    )

    users = {
        "novice": [human_simulator.create_user(i, "novice") for i in range(args.users_per_level)],
        "intermediate": [human_simulator.create_user(i + 100, "intermediate") for i in range(args.users_per_level)],
        "expert": [human_simulator.create_user(i + 200, "expert") for i in range(args.users_per_level)]
    }

    # Define models to train
    models_config = {
        "Baseline": BaselineAI(
            input_dim=args.n_features,
            hidden_dim=MODEL_CONFIG["hidden_dim"],
            num_classes=args.n_classes,
            dropout=MODEL_CONFIG["dropout"]
        ),
        "Transparency+": TransparencyPlusAI(
            input_dim=args.n_features,
            hidden_dim=MODEL_CONFIG["hidden_dim"],
            num_classes=args.n_classes,
            dropout=MODEL_CONFIG["dropout"]
        ),
        "MCF-Static": MCFStatic(
            input_dim=args.n_features,
            num_classes=args.n_classes,
            config=MODEL_CONFIG
        ),
        "MCF-Full": MutualCalibrationFramework(
            input_dim=args.n_features,
            num_classes=args.n_classes,
            config=MODEL_CONFIG
        )
    }

    # Train and evaluate all models
    all_histories = {}
    all_results = {}
    tracker = ExperimentTracker()

    for model_name, model in models_config.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Training and evaluating: {model_name}")
        logger.info(f"{'='*60}")

        is_mcf = model_name in ["MCF-Static", "MCF-Full"]

        history, results = train_and_evaluate_model(
            model_name, model, train_loader, val_loader, test_loader,
            human_simulator, users, DEVICE, logger, is_mcf=is_mcf
        )

        all_histories[model_name] = history
        all_results[model_name] = results

        # Add to tracker
        for expertise_level, metrics in results.items():
            for metric_name, value in metrics.items():
                tracker.add_result(model_name, expertise_level, {metric_name: value["mean"]})

        # Log key metrics
        for level in ["novice", "intermediate", "expert"]:
            arr = results[level].get("rel_appropriate_reliance_rate", {}).get("mean", 0)
            acc = results[level].get("perf_collaborative_accuracy", {}).get("mean", 0)
            logger.info(f"  {level}: ARR={arr:.3f}, Collab Acc={acc:.3f}")

    # Aggregate results
    logger.info("\n" + "=" * 60)
    logger.info("Results Summary")
    logger.info("=" * 60)

    # Flatten results for visualization
    flat_results = {}
    for model_name, results in all_results.items():
        # Aggregate across expertise levels
        model_metrics = {}
        for metric_name in results["novice"].keys():
            values = [results[level][metric_name]["mean"] for level in ["novice", "intermediate", "expert"]]
            model_metrics[metric_name] = {
                "mean": np.mean(values),
                "std": np.std(values)
            }
        flat_results[model_name] = model_metrics

    # Generate figures
    logger.info("\nGenerating figures...")
    generate_all_figures(all_histories, flat_results, FIGURES_DIR)

    # Generate expertise-level comparison figures
    detailed_results = {}
    for model_name, results in all_results.items():
        for level, metrics in results.items():
            key = f"{model_name}_{level}"
            detailed_results[key] = metrics

    # Plot ARR by expertise
    plot_expertise_comparison(
        detailed_results,
        "rel_appropriate_reliance_rate",
        os.path.join(FIGURES_DIR, "arr_by_expertise.png"),
        title="Appropriate Reliance Rate by Expertise Level"
    )

    # Plot collaborative accuracy by expertise
    plot_expertise_comparison(
        detailed_results,
        "perf_collaborative_accuracy",
        os.path.join(FIGURES_DIR, "accuracy_by_expertise.png"),
        title="Collaborative Accuracy by Expertise Level"
    )

    # Plot over-reliance by expertise
    plot_expertise_comparison(
        detailed_results,
        "rel_over_reliance_rate",
        os.path.join(FIGURES_DIR, "over_reliance_by_expertise.png"),
        title="Over-Reliance Rate by Expertise Level"
    )

    # Save results to JSON
    results_json = {
        "experiment_config": {
            "n_samples": args.n_samples,
            "n_features": args.n_features,
            "n_classes": args.n_classes,
            "users_per_level": args.users_per_level,
            "model_config": MODEL_CONFIG,
            "training_config": TRAINING_CONFIG,
            "loss_weights": LOSS_WEIGHTS,
            "seed": SEED
        },
        "results": {
            model_name: {
                level: {k: v for k, v in metrics.items()}
                for level, metrics in results.items()
            }
            for model_name, results in all_results.items()
        },
        "aggregated_results": flat_results
    }

    with open(os.path.join(RESULTS_DIR, "results.json"), "w") as f:
        json.dump(results_json, f, indent=2, cls=NumpyEncoder)

    # Create results summary CSV
    summary_data = []
    for model_name, results in all_results.items():
        for level in ["novice", "intermediate", "expert"]:
            row = {
                "model": model_name,
                "expertise": level,
                "ai_accuracy": results[level].get("perf_ai_accuracy", {}).get("mean", 0),
                "collaborative_accuracy": results[level].get("perf_collaborative_accuracy", {}).get("mean", 0),
                "appropriate_reliance_rate": results[level].get("rel_appropriate_reliance_rate", {}).get("mean", 0),
                "over_reliance_rate": results[level].get("rel_over_reliance_rate", {}).get("mean", 0),
                "under_reliance_rate": results[level].get("rel_under_reliance_rate", {}).get("mean", 0),
                "override_rate": results[level].get("agency_override_rate", {}).get("mean", 0),
                "unique_contribution": results[level].get("agency_unique_contribution_rate", {}).get("mean", 0)
            }
            summary_data.append(row)

    df = pd.DataFrame(summary_data)
    df.to_csv(os.path.join(RESULTS_DIR, "results_summary.csv"), index=False)

    logger.info("\nExperiment completed successfully!")
    logger.info(f"Results saved to {RESULTS_DIR}")

    return all_results, all_histories


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MCF experiments")
    parser.add_argument("--n_samples", type=int, default=5000, help="Number of samples")
    parser.add_argument("--n_features", type=int, default=50, help="Number of features")
    parser.add_argument("--n_classes", type=int, default=10, help="Number of classes")
    parser.add_argument("--users_per_level", type=int, default=10, help="Users per expertise level")

    args = parser.parse_args()
    run_experiments(args)
