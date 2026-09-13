#!/usr/bin/env python
"""
Main experiment script for EmbedPrint data attribution.
"""
import os
import sys
import json
import logging
import argparse
import time
from pathlib import Path
from datetime import datetime

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ExperimentConfig, BaselineConfig
from data_utils import (
    load_and_prepare_data,
    create_canary_samples,
    cluster_texts,
    create_dataloaders,
)
from models import EmbedPrintModel
from trainer import EmbedPrintTrainer, BaselineTrainer
from baselines import EmbeddingSimilarityAttributor
from evaluation import (
    evaluate_embedprint_attribution,
    evaluate_baseline_attribution,
)
from visualization import generate_all_figures, create_results_table

# Setup logging
def setup_logging(log_file: str):
    """Setup logging to file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
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


def main(args):
    """Main experiment function."""
    # Setup
    start_time = time.time()

    # Create output directories
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results_dir = output_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Setup logging
    log_file = results_dir / "log.txt"
    logger = setup_logging(str(log_file))

    logger.info("=" * 60)
    logger.info("EmbedPrint Data Attribution Experiment")
    logger.info("=" * 60)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Configuration
    config = ExperimentConfig(
        model_name=args.model_name,
        num_train_samples=args.num_train_samples,
        num_eval_samples=args.num_eval_samples,
        num_canary_samples=args.num_canary_samples,
        num_epochs=args.num_epochs,
        batch_size=args.batch_size,
        output_dir=str(output_dir),
        results_dir=str(results_dir),
        seed=args.seed,
    )

    baseline_config = BaselineConfig()

    # Set device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    config.device = device
    logger.info(f"Using device: {device}")
    if device == "cuda":
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")

    set_seed(config.seed)

    # Log configuration
    logger.info("\n--- Configuration ---")
    for key, value in vars(config).items():
        logger.info(f"  {key}: {value}")

    # ========================================
    # Step 1: Load and prepare data
    # ========================================
    logger.info("\n" + "=" * 60)
    logger.info("Step 1: Loading and preparing data")
    logger.info("=" * 60)

    train_texts, eval_texts = load_and_prepare_data(config)
    logger.info(f"Loaded {len(train_texts)} training samples and {len(eval_texts)} eval samples")

    # Create canary samples
    train_texts, is_canary = create_canary_samples(
        train_texts, config.num_canary_samples, config.seed
    )
    logger.info(f"Created {is_canary.sum()} canary samples for evaluation")

    # Cluster training data
    logger.info("\nClustering training data...")
    cluster_ids, coarse_clusters, embeddings = cluster_texts(
        train_texts,
        config.num_coarse_clusters,
        config.num_fine_clusters_per_coarse,
        device=device,
    )
    logger.info(f"Created {len(np.unique(cluster_ids))} clusters")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(config.model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Create dataloaders
    train_loader, eval_loader = create_dataloaders(
        config, train_texts, eval_texts, cluster_ids, is_canary, tokenizer
    )
    logger.info(f"Created dataloaders: {len(train_loader)} train batches, {len(eval_loader)} eval batches")

    # ========================================
    # Step 2: Train EmbedPrint model
    # ========================================
    logger.info("\n" + "=" * 60)
    logger.info("Step 2: Training EmbedPrint model")
    logger.info("=" * 60)

    embedprint_model = EmbedPrintModel(
        model_name=config.model_name,
        num_clusters=config.total_clusters,
        signature_dim=config.signature_dim,
        projection_dim=config.projection_dim,
    )

    embedprint_trainer = EmbedPrintTrainer(
        model=embedprint_model,
        config=config,
        train_loader=train_loader,
        eval_loader=eval_loader,
        device=device,
    )

    embedprint_history = embedprint_trainer.train(
        train_texts, cluster_ids, is_canary, tokenizer
    )

    logger.info("EmbedPrint training complete!")
    logger.info(f"  Final train loss: {embedprint_history['train_loss'][-1]:.4f}")
    logger.info(f"  Final eval perplexity: {embedprint_history['eval_perplexity'][-1]:.2f}")
    if embedprint_history['attribution_accuracy']:
        logger.info(f"  Final attribution P@10: {embedprint_history['attribution_accuracy'][-1]:.3f}")

    # ========================================
    # Step 3: Train Baseline model (without fingerprints)
    # ========================================
    logger.info("\n" + "=" * 60)
    logger.info("Step 3: Training Baseline model")
    logger.info("=" * 60)

    baseline_lm = AutoModelForCausalLM.from_pretrained(config.model_name)

    baseline_trainer = BaselineTrainer(
        model=baseline_lm,
        config=config,
        train_loader=train_loader,
        eval_loader=eval_loader,
        device=device,
    )

    baseline_history = baseline_trainer.train()

    logger.info("Baseline training complete!")
    logger.info(f"  Final train loss: {baseline_history['train_loss'][-1]:.4f}")
    logger.info(f"  Final eval perplexity: {baseline_history['eval_perplexity'][-1]:.2f}")

    # ========================================
    # Step 4: Evaluate all methods
    # ========================================
    logger.info("\n" + "=" * 60)
    logger.info("Step 4: Evaluating attribution methods")
    logger.info("=" * 60)

    all_results = {}

    # Prepare test data (subset of training data with known clusters)
    test_indices = np.where(is_canary)[0]
    if len(test_indices) > 50:
        test_indices = test_indices[:50]  # Limit for efficiency

    test_texts = [train_texts[i] for i in test_indices]
    test_cluster_ids = cluster_ids[test_indices]

    # 4.1 EmbedPrint evaluation
    logger.info("\nEvaluating EmbedPrint...")
    embedprint_results = evaluate_embedprint_attribution(
        model=embedprint_model,
        train_texts=train_texts,
        test_texts=test_texts,
        train_cluster_ids=cluster_ids,
        test_cluster_ids=test_cluster_ids,
        tokenizer=tokenizer,
        config=config,
        device=device,
    )
    all_results["EmbedPrint"] = embedprint_results
    logger.info(f"EmbedPrint: P@10={embedprint_results['precision@10']:.3f}, "
                f"MRR={embedprint_results['mrr']:.3f}, "
                f"Latency={embedprint_results['avg_latency_ms']:.2f}ms")

    # 4.2 Embedding Similarity baseline
    logger.info("\nEvaluating Embedding Similarity baseline...")
    embed_attributor = EmbeddingSimilarityAttributor(device=device)
    embed_attributor.fit(train_texts, cluster_ids)

    embed_results = evaluate_baseline_attribution(
        attributor=embed_attributor,
        train_texts=train_texts,
        test_texts=test_texts,
        train_cluster_ids=cluster_ids,
        test_cluster_ids=test_cluster_ids,
        num_clusters=config.total_clusters,
        method_name="Embedding Similarity",
    )
    all_results["Embedding Similarity"] = embed_results

    # 4.3 Random baseline
    logger.info("\nEvaluating Random baseline...")
    random_scores = np.random.rand(len(test_texts), config.total_clusters)
    random_results = {}
    for k in config.top_k_values:
        correct = 0
        for i in range(len(test_texts)):
            top_k_pred = np.argsort(random_scores[i])[-k:][::-1]
            if test_cluster_ids[i] in top_k_pred:
                correct += 1
        random_results[f"precision@{k}"] = correct / len(test_texts)

    # MRR for random
    mrr_sum = 0
    for i in range(len(test_texts)):
        ranked = np.argsort(random_scores[i])[::-1]
        rank = np.where(ranked == test_cluster_ids[i])[0]
        if len(rank) > 0:
            mrr_sum += 1.0 / (rank[0] + 1)
    random_results["mrr"] = mrr_sum / len(test_texts)
    random_results["avg_latency_ms"] = 0.1  # Negligible
    random_results["throughput_qps"] = 10000

    all_results["Random"] = random_results
    logger.info(f"Random: P@10={random_results['precision@10']:.3f}, MRR={random_results['mrr']:.3f}")

    # ========================================
    # Step 5: Generate visualizations
    # ========================================
    logger.info("\n" + "=" * 60)
    logger.info("Step 5: Generating visualizations")
    logger.info("=" * 60)

    generate_all_figures(
        embedprint_history=embedprint_history,
        baseline_history=baseline_history,
        all_results=all_results,
        output_dir=str(results_dir),
    )

    # ========================================
    # Step 6: Save results
    # ========================================
    logger.info("\n" + "=" * 60)
    logger.info("Step 6: Saving results")
    logger.info("=" * 60)

    # Save all results to JSON
    results_json = {
        "config": {
            "model_name": config.model_name,
            "num_train_samples": config.num_train_samples,
            "num_eval_samples": config.num_eval_samples,
            "num_canary_samples": config.num_canary_samples,
            "num_epochs": config.num_epochs,
            "batch_size": config.batch_size,
            "num_clusters": config.total_clusters,
            "signature_dim": config.signature_dim,
            "lambda_fp": config.lambda_fp,
            "temperature": config.temperature,
        },
        "embedprint_history": {k: [float(v) for v in vals] for k, vals in embedprint_history.items()},
        "baseline_history": {k: [float(v) for v in vals] for k, vals in baseline_history.items()},
        "attribution_results": {
            method: {k: float(v) if isinstance(v, (int, float, np.floating)) else v
                     for k, v in metrics.items()}
            for method, metrics in all_results.items()
        },
    }

    with open(results_dir / "results.json", "w") as f:
        json.dump(results_json, f, indent=2)
    logger.info(f"Saved results to {results_dir / 'results.json'}")

    # Create summary table
    create_results_table(all_results, str(results_dir / "results_table.csv"))

    # ========================================
    # Summary
    # ========================================
    total_time = time.time() - start_time
    logger.info("\n" + "=" * 60)
    logger.info("Experiment Complete!")
    logger.info("=" * 60)
    logger.info(f"Total time: {total_time/60:.2f} minutes")
    logger.info(f"\nKey Results:")
    logger.info(f"  EmbedPrint Precision@10: {all_results['EmbedPrint']['precision@10']:.3f}")
    logger.info(f"  EmbedPrint MRR: {all_results['EmbedPrint']['mrr']:.3f}")
    logger.info(f"  EmbedPrint Latency: {all_results['EmbedPrint']['avg_latency_ms']:.2f}ms")
    logger.info(f"  Baseline Perplexity: {baseline_history['eval_perplexity'][-1]:.2f}")
    logger.info(f"  EmbedPrint Perplexity: {embedprint_history['eval_perplexity'][-1]:.2f}")

    ppl_degradation = ((embedprint_history['eval_perplexity'][-1] - baseline_history['eval_perplexity'][-1])
                       / baseline_history['eval_perplexity'][-1] * 100)
    logger.info(f"  Perplexity Degradation: {ppl_degradation:+.2f}%")

    logger.info(f"\nResults saved to: {results_dir}")

    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EmbedPrint Data Attribution Experiment")
    parser.add_argument("--model_name", type=str, default="distilgpt2",
                        help="Pretrained model name")
    parser.add_argument("--num_train_samples", type=int, default=3000,
                        help="Number of training samples")
    parser.add_argument("--num_eval_samples", type=int, default=300,
                        help="Number of evaluation samples")
    parser.add_argument("--num_canary_samples", type=int, default=100,
                        help="Number of canary samples")
    parser.add_argument("--num_epochs", type=int, default=3,
                        help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=16,
                        help="Batch size")
    parser.add_argument("--output_dir", type=str, default="outputs",
                        help="Output directory")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")

    args = parser.parse_args()
    main(args)
