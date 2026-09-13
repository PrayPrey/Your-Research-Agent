"""
Main Experiment Runner for h-e1: Tri-Modal RL Framework
Executes PoC experiment with gate validation
"""
import os
import sys
import json
import torch
import random
import numpy as np
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config.experiment_config import ExperimentConfig
from data.dataset import create_dataloaders
from models.tri_modal_aggregator import TriModalAggregator
from models.feedback_collectors import FeedbackCollector
from train.ppo_trainer import SimplifiedPPOTrainer, BaselinePPOTrainer
from evaluation.evaluator import CodeEvaluator
from transformers import AutoTokenizer


def set_seed(seed: int):
    """Set random seeds for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def run_baseline(
    config: ExperimentConfig,
    baseline_type: str,
    train_loader,
    val_loader,
    test_loader,
    device: str
):
    """Run a single baseline experiment"""
    print(f"\n{'='*60}")
    print(f"Running Baseline: {baseline_type}")
    print(f"{'='*60}")

    # Initialize feedback collector
    collector = FeedbackCollector(
        execution_timeout=config.feedback.execution_timeout,
        reward_model_name=config.feedback.reward_model_name,
        annotation_cache_path=config.feedback.annotation_cache_path,
        device=device
    )

    # Create baseline trainer
    trainer = BaselinePPOTrainer(
        model_name=config.model.model_name,
        feedback_type=baseline_type.replace("_only", ""),  # execution, human, ai
        feedback_collector=collector,
        learning_rate=config.ppo.learning_rate,
        device=device
    )

    trainer.total_steps = config.ppo.total_steps

    # Training loop (simplified for PoC)
    metrics_history = []

    for step in tqdm(range(config.ppo.total_steps), desc=f"{baseline_type}"):
        # Get batch from train loader
        try:
            batch = next(train_iter)
        except:
            train_iter = iter(train_loader)
            batch = next(train_iter)

        # Extract data
        prompts = batch['prompt'][:config.ppo.batch_size]
        test_cases = batch['test_cases'][:config.ppo.batch_size]
        task_ids = batch['sample_id'][:config.ppo.batch_size]

        # Training step
        metrics = trainer.train_step(prompts, test_cases, task_ids)

        # Log metrics
        if step % config.ppo.logging_steps == 0:
            metrics_history.append({
                'step': step,
                **metrics
            })

        # Save checkpoint
        if step % config.ppo.save_steps == 0 and step > 0:
            checkpoint_dir = Path(config.checkpoint_dir) / f"{baseline_type}_step_{step}"
            trainer.save_checkpoint(str(checkpoint_dir))

    # Evaluation with real dataset
    evaluator = CodeEvaluator(device=device)
    eval_results = evaluator.evaluate_model(
        model=trainer.model,
        tokenizer=trainer.tokenizer,
        test_loader=test_loader
    )

    return {
        'baseline_type': baseline_type,
        'training_metrics': metrics_history,
        'eval_results': eval_results
    }


def run_trimodal(
    config: ExperimentConfig,
    train_loader,
    val_loader,
    test_loader,
    device: str
):
    """Run tri-modal experiment"""
    print(f"\n{'='*60}")
    print(f"Running Tri-Modal Experiment")
    print(f"{'='*60}")

    # Initialize components
    aggregator = TriModalAggregator(
        num_phases=config.aggregator.num_phases,
        initial_weights=config.aggregator.initial_weights,
        peak_timesteps=config.aggregator.peak_timesteps,
        decay_rates=config.aggregator.decay_rates
    )

    collector = FeedbackCollector(
        execution_timeout=config.feedback.execution_timeout,
        reward_model_name=config.feedback.reward_model_name,
        annotation_cache_path=config.feedback.annotation_cache_path,
        device=device
    )

    # Create trainer
    trainer = SimplifiedPPOTrainer(
        model_name=config.model.model_name,
        aggregator=aggregator,
        feedback_collector=collector,
        learning_rate=config.ppo.learning_rate,
        device=device
    )

    trainer.total_steps = config.ppo.total_steps

    # Training loop
    metrics_history = []
    weight_trajectory = []

    train_iter = iter(train_loader)

    for step in tqdm(range(config.ppo.total_steps), desc="Tri-Modal"):
        # Get batch
        try:
            batch = next(train_iter)
        except:
            train_iter = iter(train_loader)
            batch = next(train_iter)

        prompts = batch['prompt'][:config.ppo.batch_size]
        test_cases = batch['test_cases'][:config.ppo.batch_size]
        task_ids = batch['sample_id'][:config.ppo.batch_size]

        # Training step
        metrics = trainer.train_step(prompts, test_cases, task_ids)

        # Log metrics
        if step % config.ppo.logging_steps == 0:
            metrics_history.append({
                'step': step,
                **metrics
            })

            # Track weight evolution
            weight_trajectory.append({
                'step': step,
                'execution_weight': metrics['execution_weight'],
                'ai_weight': metrics['ai_weight'],
                'human_weight': metrics['human_weight'],
                'training_progress': metrics['training_progress']
            })

        # Save checkpoint
        if step % config.ppo.save_steps == 0 and step > 0:
            checkpoint_dir = Path(config.checkpoint_dir) / f"trimodal_step_{step}"
            trainer.save_checkpoint(str(checkpoint_dir))

    # Final evaluation with real dataset
    evaluator = CodeEvaluator(device=device)
    eval_results = evaluator.evaluate_model(
        model=trainer.model,
        tokenizer=trainer.tokenizer,
        test_loader=test_loader
    )

    return {
        'baseline_type': 'trimodal',
        'training_metrics': metrics_history,
        'weight_trajectory': weight_trajectory,
        'eval_results': eval_results
    }


def main():
    """Main experiment execution"""
    print("="*60)
    print("h-e1: Tri-Modal RL Framework - PoC Experiment")
    print("="*60)

    # Load config
    config = ExperimentConfig()

    # Set seed
    set_seed(config.seed)

    # Device
    device = config.device if torch.cuda.is_available() else "cpu"
    print(f"\nDevice: {device}")

    # Create output directories
    Path(config.output_dir).mkdir(parents=True, exist_ok=True)
    Path(config.checkpoint_dir).mkdir(parents=True, exist_ok=True)

    # Load datasets
    print("\nLoading datasets...")
    tokenizer = AutoTokenizer.from_pretrained(config.model.model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_loader, val_loader, test_loader = create_dataloaders(
        tokenizer=tokenizer,
        cache_dir=config.data.cache_dir,
        batch_size=config.data.batch_size,
        max_length=config.data.max_length,
        num_workers=config.data.num_workers,
        seed=config.seed
    )

    print(f"✓ Data loaded: {len(train_loader.dataset)} train, {len(test_loader.dataset)} test")

    # Run experiments
    all_results = {}

    # Baselines
    for baseline_type in config.baseline_types:
        if baseline_type == "trimodal":
            continue

        results = run_baseline(
            config=config,
            baseline_type=baseline_type,
            train_loader=train_loader,
            val_loader=val_loader,
            test_loader=test_loader,
            device=device
        )

        all_results[baseline_type] = results

    # Tri-modal
    trimodal_results = run_trimodal(
        config=config,
        train_loader=train_loader,
        val_loader=val_loader,
        test_loader=test_loader,
        device=device
    )

    all_results['trimodal'] = trimodal_results

    # Save results
    results_file = Path(config.output_dir) / "experiment_results.json"
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✓ Results saved to: {results_file}")

    # Gate validation
    print("\n" + "="*60)
    print("GATE VALIDATION (MUST_WORK)")
    print("="*60)

    trimodal_hm = trimodal_results['eval_results']['harmonic_mean']
    best_baseline_hm = max(
        all_results[bt]['eval_results']['harmonic_mean']
        for bt in config.baseline_types if bt != "trimodal"
    )

    improvement = trimodal_hm - best_baseline_hm

    print(f"\nTri-modal harmonic mean: {trimodal_hm:.4f}")
    print(f"Best baseline harmonic mean: {best_baseline_hm:.4f}")
    print(f"Improvement: {improvement:+.4f} ({improvement/best_baseline_hm*100:+.2f}%)")

    gate_pass = improvement > 0  # PoC: any positive direction

    print(f"\nGate Result: {'PASS' if gate_pass else 'FAIL'}")

    return gate_pass


if __name__ == "__main__":
    try:
        gate_pass = main()
        sys.exit(0 if gate_pass else 1)
    except Exception as e:
        print(f"\n❌ Experiment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
