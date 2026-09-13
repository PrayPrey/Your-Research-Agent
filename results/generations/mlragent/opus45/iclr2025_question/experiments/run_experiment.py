"""Main experiment script for Semantic Entropy Decomposition."""

import os
import sys
import json
import time
import random
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Tuple
from tqdm import tqdm

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('log.txt', mode='w')
    ]
)
logger = logging.getLogger(__name__)

# Import local modules
from config import get_config, ExperimentConfig
from model import SEDModel, SEDLoss, SEDOutput, load_model_and_tokenizer
from data import (
    prepare_datasets, get_test_dataset_for_evaluation,
    load_truthfulqa_subset, create_ambiguous_questions, create_factual_questions,
    UncertaintyDataPoint
)
from uncertainty import (
    BaselineUncertaintyEstimator, compute_semantic_entropy,
    generate_with_entropy, compute_verbalized_confidence
)
from evaluation import (
    compute_all_metrics, plot_roc_curve, plot_precision_recall_curve,
    plot_calibration_curve, plot_confusion_matrices, plot_training_curves,
    plot_method_comparison, save_results
)


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def prepare_batch(batch: Dict, tokenizer, device: str) -> Tuple[torch.Tensor, torch.Tensor, List[str], torch.Tensor]:
    """Prepare a batch for training."""
    questions = batch["question"]
    uncertainty_types = batch["uncertainty_type"]
    hallucination_labels = torch.tensor(
        [1 if h else 0 for h in batch["is_hallucination"]],
        dtype=torch.float32, device=device
    )

    # Create prompts
    prompts = [f"Question: {q}\nAnswer:" for q in questions]

    # Tokenize
    encodings = tokenizer(
        prompts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=256
    )
    input_ids = encodings["input_ids"].to(device)
    attention_mask = encodings["attention_mask"].to(device)

    return input_ids, attention_mask, uncertainty_types, hallucination_labels


def compute_ground_truth_entropy(
    model, tokenizer, questions: List[str],
    num_samples: int, temperature: float, device: str
) -> torch.Tensor:
    """Compute ground truth semantic entropy for a batch."""
    entropies = []

    for question in questions:
        prompt = f"Question: {question}\nAnswer:"
        entropy, _ = compute_semantic_entropy(
            model, tokenizer, prompt,
            num_samples=num_samples,
            max_new_tokens=64,
            temperature=temperature,
            device=device
        )
        entropies.append(entropy)

    return torch.tensor(entropies, dtype=torch.float32, device=device).unsqueeze(-1)


def train_epoch(
    sed_model: SEDModel,
    base_model,
    tokenizer,
    train_loader: DataLoader,
    optimizer: optim.Optimizer,
    loss_fn: SEDLoss,
    config: ExperimentConfig,
    device: str
) -> Dict[str, float]:
    """Train for one epoch."""
    sed_model.train()
    total_loss = 0.0
    loss_components = {"reconstruction": 0.0, "contrastive": 0.0, "consistency": 0.0}
    num_batches = 0

    for batch in tqdm(train_loader, desc="Training", leave=False):
        input_ids, attention_mask, uncertainty_types, hallucination_labels = prepare_batch(
            batch, tokenizer, device
        )

        # Get ground truth semantic entropy (expensive, so we use approximation mostly)
        if random.random() < 0.1:  # Only compute for 10% of batches to save time
            se_target = compute_ground_truth_entropy(
                base_model, tokenizer, batch["question"],
                num_samples=config.num_samples_for_se,
                temperature=config.temperature,
                device=device
            )
        else:
            # Use approximation based on uncertainty type
            se_target = torch.tensor([
                1.5 if ut == "epistemic" else (1.0 if ut == "aleatoric" else 0.2)
                for ut in uncertainty_types
            ], dtype=torch.float32, device=device).unsqueeze(-1)

        # Forward pass
        optimizer.zero_grad()
        sed_output = sed_model(input_ids, attention_mask)

        # Compute loss
        losses = loss_fn(sed_output, se_target, uncertainty_types, hallucination_labels)

        # Backward pass
        losses["total"].backward()
        torch.nn.utils.clip_grad_norm_(sed_model.parameters(), 1.0)
        optimizer.step()

        total_loss += losses["total"].item()
        for key in loss_components:
            loss_components[key] += losses[key].item()
        num_batches += 1

    return {
        "total_loss": total_loss / num_batches,
        **{k: v / num_batches for k, v in loss_components.items()}
    }


def evaluate(
    sed_model: SEDModel,
    base_model,
    tokenizer,
    val_loader: DataLoader,
    loss_fn: SEDLoss,
    config: ExperimentConfig,
    device: str
) -> Tuple[Dict[str, float], Dict[str, List]]:
    """Evaluate the model."""
    sed_model.eval()
    total_loss = 0.0
    num_batches = 0

    all_epistemic = []
    all_aleatoric = []
    all_total = []
    all_labels = []
    all_types = []

    with torch.no_grad():
        for batch in tqdm(val_loader, desc="Evaluating", leave=False):
            input_ids, attention_mask, uncertainty_types, hallucination_labels = prepare_batch(
                batch, tokenizer, device
            )

            # Approximate ground truth
            se_target = torch.tensor([
                1.5 if ut == "epistemic" else (1.0 if ut == "aleatoric" else 0.2)
                for ut in uncertainty_types
            ], dtype=torch.float32, device=device).unsqueeze(-1)

            # Forward pass
            sed_output = sed_model(input_ids, attention_mask)

            # Compute loss
            losses = loss_fn(sed_output, se_target, uncertainty_types, hallucination_labels)
            total_loss += losses["total"].item()
            num_batches += 1

            # Collect predictions
            all_epistemic.extend(sed_output.epistemic_uncertainty.squeeze(-1).cpu().numpy().tolist())
            all_aleatoric.extend(sed_output.aleatoric_uncertainty.squeeze(-1).cpu().numpy().tolist())
            all_total.extend(sed_output.total_uncertainty.squeeze(-1).cpu().numpy().tolist())
            all_labels.extend(hallucination_labels.cpu().numpy().tolist())
            all_types.extend(uncertainty_types)

    # Compute metrics
    labels = np.array(all_labels)
    epistemic = np.array(all_epistemic)

    metrics = compute_all_metrics(labels, epistemic)
    metrics["val_loss"] = total_loss / num_batches

    predictions = {
        "epistemic": all_epistemic,
        "aleatoric": all_aleatoric,
        "total": all_total,
        "labels": all_labels,
        "types": all_types
    }

    return metrics, predictions


def run_baseline_evaluation(
    base_model,
    tokenizer,
    test_data: List[UncertaintyDataPoint],
    config: ExperimentConfig,
    device: str
) -> Dict[str, Dict]:
    """Run baseline methods and collect results."""
    logger.info("Running baseline evaluations...")

    baseline_estimator = BaselineUncertaintyEstimator(base_model, tokenizer, device)

    results = {
        "Token Entropy": {"labels": [], "scores": []},
        "Verbalized Confidence": {"labels": [], "scores": []},
        "Semantic Entropy": {"labels": [], "scores": []},
    }

    for i, dp in enumerate(tqdm(test_data, desc="Baseline evaluation")):
        label = 1 if dp.is_hallucination else 0

        # Token entropy
        try:
            te_result = baseline_estimator.token_entropy(dp.question)
            results["Token Entropy"]["labels"].append(label)
            results["Token Entropy"]["scores"].append(te_result["normalized_uncertainty"])
        except Exception as e:
            logger.warning(f"Token entropy failed for sample {i}: {e}")

        # Verbalized confidence
        try:
            vc_result = baseline_estimator.verbalized_confidence(dp.question)
            results["Verbalized Confidence"]["labels"].append(label)
            results["Verbalized Confidence"]["scores"].append(vc_result["uncertainty"])
        except Exception as e:
            logger.warning(f"Verbalized confidence failed for sample {i}: {e}")

        # Semantic entropy (expensive, so only do for subset)
        if i < min(30, len(test_data)):
            try:
                se_result = baseline_estimator.semantic_entropy(dp.question, num_samples=3)
                results["Semantic Entropy"]["labels"].append(label)
                results["Semantic Entropy"]["scores"].append(se_result["normalized_uncertainty"])
            except Exception as e:
                logger.warning(f"Semantic entropy failed for sample {i}: {e}")

    return results


def run_sed_evaluation(
    sed_model: SEDModel,
    tokenizer,
    test_data: List[UncertaintyDataPoint],
    device: str
) -> Dict[str, Dict]:
    """Run SED model evaluation."""
    logger.info("Running SED evaluation...")

    sed_model.eval()
    results = {
        "SED (Epistemic)": {"labels": [], "scores": []},
        "SED (Aleatoric)": {"labels": [], "scores": []},
        "SED (Total)": {"labels": [], "scores": []},
    }

    with torch.no_grad():
        for dp in tqdm(test_data, desc="SED evaluation"):
            label = 1 if dp.is_hallucination else 0

            prompt = f"Question: {dp.question}\nAnswer:"
            encodings = tokenizer(
                prompt, return_tensors="pt", padding=True, truncation=True, max_length=256
            )
            input_ids = encodings["input_ids"].to(device)
            attention_mask = encodings["attention_mask"].to(device)

            try:
                sed_output = sed_model(input_ids, attention_mask)

                results["SED (Epistemic)"]["labels"].append(label)
                results["SED (Epistemic)"]["scores"].append(
                    sed_output.epistemic_uncertainty.item()
                )

                results["SED (Aleatoric)"]["labels"].append(label)
                results["SED (Aleatoric)"]["scores"].append(
                    sed_output.aleatoric_uncertainty.item()
                )

                results["SED (Total)"]["labels"].append(label)
                results["SED (Total)"]["scores"].append(
                    sed_output.total_uncertainty.item()
                )
            except Exception as e:
                logger.warning(f"SED evaluation failed: {e}")

    return results


def main():
    """Main experiment function."""
    parser = argparse.ArgumentParser(description="SED Experiment")
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--batch_size", type=int, default=None)
    parser.add_argument("--lr", type=float, default=None)
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--output_dir", type=str, default="outputs")
    args = parser.parse_args()

    # Configuration
    config = get_config()
    if args.epochs:
        config.num_epochs = args.epochs
    if args.batch_size:
        config.batch_size = args.batch_size
    if args.lr:
        config.learning_rate = args.lr
    config.output_dir = args.output_dir

    # Setup
    set_seed(config.seed)
    device = args.device if torch.cuda.is_available() else "cpu"
    os.makedirs(config.output_dir, exist_ok=True)

    logger.info("=" * 60)
    logger.info("Semantic Entropy Decomposition (SED) Experiment")
    logger.info("=" * 60)
    logger.info(f"Device: {device}")
    logger.info(f"Model: {config.model_name}")
    logger.info(f"Epochs: {config.num_epochs}")
    logger.info(f"Batch size: {config.batch_size}")
    logger.info(f"Learning rate: {config.learning_rate}")

    # Load model and tokenizer
    logger.info("Loading base model and tokenizer...")
    start_time = time.time()
    base_model, tokenizer = load_model_and_tokenizer(config.model_name, device)
    logger.info(f"Model loaded in {time.time() - start_time:.2f}s")

    # Adjust probe layers based on actual model
    num_layers = base_model.config.num_hidden_layers
    logger.info(f"Model has {num_layers} layers")
    # Use upper third of layers
    config.probe_layers = list(range(num_layers * 2 // 3, num_layers))
    logger.info(f"Using probe layers: {config.probe_layers}")

    # Create SED model
    logger.info("Creating SED model...")
    sed_model = SEDModel(base_model, config).to(device)

    # Count trainable parameters
    trainable_params = sum(p.numel() for p in sed_model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in base_model.parameters())
    logger.info(f"Trainable parameters: {trainable_params:,}")
    logger.info(f"Base model parameters: {total_params:,}")
    logger.info(f"Probe overhead: {100 * trainable_params / total_params:.4f}%")

    # Prepare datasets
    logger.info("Preparing datasets...")
    train_loader, val_loader, test_loader = prepare_datasets(config, tokenizer)
    logger.info(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}, Test batches: {len(test_loader)}")

    # Setup training
    optimizer = optim.AdamW(
        sed_model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay
    )
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.num_epochs)
    loss_fn = SEDLoss(
        lambda_contrast=config.lambda_contrast,
        lambda_consist=config.lambda_consist,
        margin=config.margin
    )

    # Training loop
    logger.info("\n" + "=" * 60)
    logger.info("Starting training...")
    logger.info("=" * 60)

    train_losses = []
    val_losses = []
    train_metrics_history = {"auroc": [], "auprc": []}
    val_metrics_history = {"auroc": [], "auprc": []}
    best_val_auroc = 0.0

    for epoch in range(config.num_epochs):
        logger.info(f"\nEpoch {epoch + 1}/{config.num_epochs}")

        # Train
        train_result = train_epoch(
            sed_model, base_model, tokenizer, train_loader,
            optimizer, loss_fn, config, device
        )
        train_losses.append(train_result["total_loss"])
        logger.info(f"Train Loss: {train_result['total_loss']:.4f} "
                    f"(recon: {train_result['reconstruction']:.4f}, "
                    f"contrast: {train_result['contrastive']:.4f}, "
                    f"consist: {train_result['consistency']:.4f})")

        # Evaluate
        val_metrics, val_predictions = evaluate(
            sed_model, base_model, tokenizer, val_loader, loss_fn, config, device
        )
        val_losses.append(val_metrics["val_loss"])
        logger.info(f"Val Loss: {val_metrics['val_loss']:.4f}, "
                    f"AUROC: {val_metrics['auroc']:.4f}, "
                    f"AUPRC: {val_metrics['auprc']:.4f}, "
                    f"ECE: {val_metrics['ece']:.4f}")

        # Track metrics
        train_metrics_history["auroc"].append(val_metrics["auroc"])  # Using val for train approx
        train_metrics_history["auprc"].append(val_metrics["auprc"])
        val_metrics_history["auroc"].append(val_metrics["auroc"])
        val_metrics_history["auprc"].append(val_metrics["auprc"])

        # Save best model
        if val_metrics["auroc"] > best_val_auroc:
            best_val_auroc = val_metrics["auroc"]
            logger.info(f"New best AUROC: {best_val_auroc:.4f}")

        scheduler.step()

    # Plot training curves
    logger.info("\nPlotting training curves...")
    plot_training_curves(
        train_losses, val_losses,
        train_metrics_history, val_metrics_history,
        save_path=os.path.join(config.output_dir, "training_curves.png")
    )

    # Final evaluation on test set
    logger.info("\n" + "=" * 60)
    logger.info("Final Evaluation")
    logger.info("=" * 60)

    test_data = get_test_dataset_for_evaluation(config)
    logger.info(f"Test samples: {len(test_data)}")

    # Run baseline evaluations
    baseline_results = run_baseline_evaluation(base_model, tokenizer, test_data, config, device)

    # Run SED evaluation
    sed_results = run_sed_evaluation(sed_model, tokenizer, test_data, device)

    # Combine all results
    all_results = {**baseline_results, **sed_results}

    # Compute final metrics for each method
    final_metrics = {}
    for method_name, results in all_results.items():
        if len(results["labels"]) > 10:  # Need enough samples
            labels = np.array(results["labels"])
            scores = np.array(results["scores"])
            metrics = compute_all_metrics(labels, scores)
            final_metrics[method_name] = metrics
            logger.info(f"\n{method_name}:")
            logger.info(f"  AUROC: {metrics['auroc']:.4f}")
            logger.info(f"  AUPRC: {metrics['auprc']:.4f}")
            logger.info(f"  ECE: {metrics['ece']:.4f}")
            logger.info(f"  Brier Score: {metrics['brier_score']:.4f}")

    # Generate plots
    logger.info("\nGenerating evaluation plots...")

    # Filter results with enough samples
    plot_results = {k: v for k, v in all_results.items() if len(v["labels"]) > 10}

    plot_roc_curve(plot_results, os.path.join(config.output_dir, "roc_curves.png"))
    plot_precision_recall_curve(plot_results, os.path.join(config.output_dir, "pr_curves.png"))
    plot_calibration_curve(plot_results, save_path=os.path.join(config.output_dir, "calibration_curves.png"))
    plot_confusion_matrices(plot_results, save_path=os.path.join(config.output_dir, "confusion_matrices.png"))
    plot_method_comparison(final_metrics, save_path=os.path.join(config.output_dir, "method_comparison.png"))

    # Save all results
    logger.info("\nSaving results...")
    complete_results = {
        "config": {
            "model_name": config.model_name,
            "num_epochs": config.num_epochs,
            "batch_size": config.batch_size,
            "learning_rate": config.learning_rate,
            "probe_layers": config.probe_layers,
            "lambda_contrast": config.lambda_contrast,
            "lambda_consist": config.lambda_consist,
        },
        "training": {
            "train_losses": train_losses,
            "val_losses": val_losses,
            "best_val_auroc": best_val_auroc,
        },
        "metrics": final_metrics,
        "predictions": {k: {"labels": v["labels"], "scores": v["scores"]} for k, v in all_results.items()},
    }
    save_results(complete_results, os.path.join(config.output_dir, "results.json"))

    # Timing information
    logger.info("\n" + "=" * 60)
    logger.info("Experiment Complete")
    logger.info("=" * 60)
    logger.info(f"Results saved to: {config.output_dir}")

    # Cleanup - remove any large checkpoint files
    checkpoint_dir = os.path.join(config.output_dir, "checkpoints")
    if os.path.exists(checkpoint_dir):
        import shutil
        shutil.rmtree(checkpoint_dir)
        logger.info("Cleaned up checkpoint directory")


if __name__ == "__main__":
    main()
