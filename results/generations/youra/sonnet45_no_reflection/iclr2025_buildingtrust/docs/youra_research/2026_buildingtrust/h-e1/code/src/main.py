"""Main experiment orchestration for H-E1"""
import torch
import json
import os
import random
import numpy as np
from pathlib import Path
from typing import Dict
from torch.utils.data import DataLoader

from src.config import get_default_config
from src.data import TrustworthinessDataset, DataCollator
from src.model import BaselineModel, LoRAInterventionModel
from src.train import InterventionTrainer
from src.evaluate import TrustEvaluator, CorrelationAnalyzer


def set_seed(seed: int):
    """Set random seeds for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def evaluate_baseline(model, tokenizer, dimensions) -> Dict[str, float]:
    """Evaluate baseline model on all dimensions"""
    baseline_scores = {}

    for dim in dimensions:
        print(f"\nEvaluating baseline on {dim}...")
        dataset = TrustworthinessDataset(dim)
        evaluator = TrustEvaluator(model, tokenizer)
        score = evaluator.evaluate(dataset.data, batch_size=8)
        baseline_scores[dim] = score
        print(f"  Baseline {dim}: {score:.4f}")

    return baseline_scores


def run_intervention(
    base_model,
    tokenizer,
    target_dimension: str,
    config,
    seed: int
) -> Dict[str, any]:
    """Run single intervention replicate"""
    set_seed(seed)

    print(f"\n{'='*60}")
    print(f"Intervention: {target_dimension}, Seed: {seed}")
    print(f"{'='*60}")

    # Apply LoRA
    lora_model = LoRAInterventionModel(
        base_model,
        lora_rank=config.lora_rank,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=config.target_modules
    )
    peft_model = lora_model.apply_lora()

    # Print trainable parameters
    params = lora_model.get_trainable_params()
    print(f"Trainable params: {params['trainable']:,} / {params['total']:,} ({params['percentage']:.2f}%)")

    # Load training data
    train_dataset = TrustworthinessDataset(target_dimension)
    collator = DataCollator(tokenizer, max_length=config.max_length)

    # Create dataloader (use subset for PoC)
    subset_size = min(100, len(train_dataset))
    subset_indices = list(range(subset_size))
    subset_dataset = torch.utils.data.Subset(train_dataset.data, subset_indices)

    train_dataloader = DataLoader(
        subset_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        collate_fn=collator
    )

    # Train
    trainer = InterventionTrainer(peft_model, config.__dict__)
    history = trainer.run_intervention(
        train_dataloader,
        num_epochs=config.num_epochs
    )

    # Evaluate on all dimensions
    post_scores = {}
    for dim in config.target_dimensions:
        print(f"\nEvaluating post-intervention on {dim}...")
        dataset = TrustworthinessDataset(dim)
        evaluator = TrustEvaluator(peft_model, tokenizer)
        score = evaluator.evaluate(dataset.data, batch_size=config.eval_batch_size)
        post_scores[dim] = score
        print(f"  Post {dim}: {score:.4f}")

    return {
        "target_dimension": target_dimension,
        "seed": seed,
        "post_scores": post_scores,
        "training_history": history
    }


def main():
    """Main experiment entry point"""
    print("="*60)
    print("H-E1: Cross-Dimensional Trustworthiness Effects")
    print("="*60)

    # Load configuration
    config = get_default_config()

    # Create output directory
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    # Load base model
    print("\nLoading base model...")
    baseline = BaselineModel(config.model_id)
    model = baseline.load_model()
    tokenizer = baseline.load_tokenizer()

    print(f"Model: {config.model_id}")
    print(f"Device: {model.device}")

    # Phase 1: Baseline Evaluation
    print("\n" + "="*60)
    print("Phase 1: Baseline Evaluation")
    print("="*60)

    baseline_scores = evaluate_baseline(model, tokenizer, config.target_dimensions)

    # Phase 2: Interventions
    print("\n" + "="*60)
    print("Phase 2: Interventions (PoC: 3 replicates)")
    print("="*60)

    intervention_results = {}

    for i, seed in enumerate(config.random_seeds):
        # For PoC, intervene on first dimension only
        target_dim = config.target_dimensions[0]

        result = run_intervention(
            model,
            tokenizer,
            target_dim,
            config,
            seed
        )

        intervention_results[f"replicate_{i}"] = result["post_scores"]

    # Phase 3: Correlation Analysis
    print("\n" + "="*60)
    print("Phase 3: Correlation Analysis")
    print("="*60)

    analyzer = CorrelationAnalyzer()
    correlation_results = analyzer.analyze_cross_dimensional_effects(
        baseline_scores,
        intervention_results
    )

    print(f"\nCorrelation Results:")
    for pair, stats in correlation_results["correlations"].items():
        sig_marker = "***" if stats["significant"] else ""
        print(f"  {pair}: rho={stats['rho']:.3f}, p={stats['p_value']:.4f} {sig_marker}")

    print(f"\nSignificant pairs: {correlation_results['summary']['significant_pairs']}/{correlation_results['summary']['total_pairs']}")
    print(f"Significance rate: {correlation_results['summary']['significance_rate']:.2%}")

    # Save results
    results = {
        "config": config.__dict__,
        "baseline_scores": baseline_scores,
        "intervention_results": intervention_results,
        "correlation_results": correlation_results
    }

    output_file = output_dir / "results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print("\nEXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
