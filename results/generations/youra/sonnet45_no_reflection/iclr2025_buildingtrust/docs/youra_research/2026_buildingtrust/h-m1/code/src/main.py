"""Main experiment orchestration for H-M1: Target Dimension Improvement Validation"""
import torch
import json
import random
import numpy as np
from pathlib import Path
from typing import Dict, List
from torch.utils.data import DataLoader
from scipy.stats import ttest_rel

from src.config import get_default_config
from src.data import TrustworthinessDataset, DataCollator
from src.model import BaselineModel, LoRAInterventionModel
from src.train import InterventionTrainer
from src.evaluate import TrustEvaluator


def set_seed(seed: int):
    """Set random seeds for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def evaluate_baseline(model, tokenizer, target_dimension: str) -> float:
    """Evaluate baseline model on target dimension using lm-eval harness"""
    print(f"\nEvaluating baseline on {target_dimension} using lm-eval harness...")
    evaluator = TrustEvaluator(model, tokenizer)
    score = evaluator.evaluate(target_dimension)
    print(f"  Baseline {target_dimension}: {score:.4f}")
    return score


def run_intervention(
    base_model,
    tokenizer,
    target_dimension: str,
    config,
    seed: int
) -> Dict:
    """Run single intervention replicate with LoRA fine-tuning"""
    set_seed(seed)

    print(f"\n{'='*60}")
    print(f"Replicate: Seed {seed}")
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

    print(f"\nTraining on {len(subset_dataset)} examples...")

    # Train
    trainer = InterventionTrainer(peft_model, config.__dict__)
    history = trainer.run_intervention(
        train_dataloader,
        num_epochs=config.num_epochs
    )

    # Evaluate post-intervention
    print(f"\nEvaluating post-intervention on {target_dimension} using lm-eval harness...")
    evaluator = TrustEvaluator(peft_model, tokenizer)
    post_score = evaluator.evaluate(target_dimension)
    print(f"  Post {target_dimension}: {post_score:.4f}")

    return {
        "seed": seed,
        "post_score": post_score,
        "training_history": history
    }


def main():
    """Main experiment entry point for H-M1"""
    print("="*60)
    print("H-M1: Target Dimension Improvement Validation")
    print("="*60)
    print("\nHypothesis: Targeted intervention (fine-tuning) improves")
    print("target dimension performance (TruthfulQA)")
    print("\nGate: Mean Δ(Target) > 0 with p<0.05")

    # Load configuration
    config = get_default_config()

    # H-M1 focuses only on target dimension (truthfulness)
    target_dimension = "truthfulness"

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
    print("Phase 1: Baseline Evaluation (Pre-Intervention)")
    print("="*60)

    baseline_score = evaluate_baseline(model, tokenizer, target_dimension)

    # Phase 2: Interventions (3 replicates)
    print("\n" + "="*60)
    print(f"Phase 2: LoRA Fine-Tuning on {target_dimension}")
    print(f"Replicates: {len(config.random_seeds)}")
    print("="*60)

    intervention_results = []
    post_scores = []

    for i, seed in enumerate(config.random_seeds):
        print(f"\n--- Replicate {i+1}/{len(config.random_seeds)} ---")

        result = run_intervention(
            model,
            tokenizer,
            target_dimension,
            config,
            seed
        )

        intervention_results.append(result)
        post_scores.append(result["post_score"])

        # Compute delta for this replicate
        delta = result["post_score"] - baseline_score
        print(f"  Δ(Target) = {delta:+.4f}")

    # Phase 3: Statistical Analysis
    print("\n" + "="*60)
    print("Phase 3: Statistical Analysis")
    print("="*60)

    # Compute deltas
    deltas = [post - baseline_score for post in post_scores]
    mean_delta = np.mean(deltas)
    std_delta = np.std(deltas)

    print(f"\nΔ(Target) scores: {[f'{d:+.4f}' for d in deltas]}")
    print(f"Mean Δ(Target): {mean_delta:+.4f}")
    print(f"Std Δ(Target): {std_delta:.4f}")

    # Paired t-test (H₀: μ(Δ) = 0)
    pre_scores = [baseline_score] * len(post_scores)
    t_stat, p_value = ttest_rel(post_scores, pre_scores)

    print(f"\nPaired t-test:")
    print(f"  t-statistic: {t_stat:.4f}")
    print(f"  p-value: {p_value:.4f}")
    print(f"  Significant: {p_value < 0.05}")

    # Directional consistency check
    positive_deltas = sum(1 for d in deltas if d > 0)
    consistency_rate = positive_deltas / len(deltas)

    print(f"\nDirectional Consistency:")
    print(f"  Positive Δ: {positive_deltas}/{len(deltas)} ({consistency_rate:.1%})")
    print(f"  Threshold: ≥70%")

    # Gate Evaluation
    print("\n" + "="*60)
    print("Gate Evaluation: MUST_WORK")
    print("="*60)

    gate_passed = (mean_delta > 0) and (p_value < 0.05) and (consistency_rate >= 0.7)

    print(f"\nCriteria:")
    print(f"  1. Mean Δ(Target) > 0: {mean_delta > 0} ({mean_delta:+.4f})")
    print(f"  2. p < 0.05: {p_value < 0.05} (p={p_value:.4f})")
    print(f"  3. ≥70% positive Δ: {consistency_rate >= 0.7} ({consistency_rate:.1%})")

    gate_result = "PASS" if gate_passed else "FAIL"
    print(f"\n  Gate Status: {gate_result}")

    if not gate_passed:
        print("\n⚠️  GATE FAILED: Targeted interventions do not reliably improve target dimension")
        print("    This invalidates the mechanism hypothesis H-M1")

    # Save results
    results = {
        "experiment": "H-M1: Target Dimension Improvement Validation",
        "hypothesis": "Targeted intervention improves target dimension performance",
        "config": {
            "model": config.model_id,
            "target_dimension": target_dimension,
            "num_replicates": len(config.random_seeds),
            "seeds": config.random_seeds,
            "lora_config": {
                "rank": config.lora_rank,
                "alpha": config.lora_alpha,
                "target_modules": config.target_modules,
                "dropout": config.lora_dropout
            },
            "training": {
                "learning_rate": config.learning_rate,
                "num_epochs": config.num_epochs,
                "batch_size": config.batch_size
            }
        },
        "baseline_score": float(baseline_score),
        "post_scores": [float(s) for s in post_scores],
        "deltas": [float(d) for d in deltas],
        "statistical_analysis": {
            "mean_delta": float(mean_delta),
            "std_delta": float(std_delta),
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "significant": bool(p_value < 0.05),
            "positive_deltas": int(positive_deltas),
            "consistency_rate": float(consistency_rate)
        },
        "gate_evaluation": {
            "type": "MUST_WORK",
            "criteria": {
                "mean_delta_positive": bool(mean_delta > 0),
                "p_significant": bool(p_value < 0.05),
                "directional_consistency": bool(consistency_rate >= 0.7)
            },
            "status": gate_result,
            "passed": bool(gate_passed)
        },
        "intervention_results": [
            {
                "replicate": i + 1,
                "seed": result["seed"],
                "post_score": float(result["post_score"]),
                "delta": float(result["post_score"] - baseline_score)
            }
            for i, result in enumerate(intervention_results)
        ]
    }

    output_file = output_dir / "experiment_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print("\nEXPERIMENT COMPLETE")

    return results


if __name__ == "__main__":
    main()
