"""Main Orchestrator for H-M3 Multi-Dimensional Correlation Experiment"""
import torch
import random
import numpy as np
from typing import Dict
import logging
import json
from pathlib import Path

# Import h-m3 modules
from config_h_m3 import H_M3_Config, get_default_config
from data_multi_dimensional import MultiDimensionalDataset
from evaluators import MultiDimensionalEvaluator
from correlation_analyzer import (
    CrossDimensionalCorrelationAnalyzer,
    PermutationTester,
    LayerWiseCorrelationAnalyzer
)
from visualize_h_m3 import H_M3_FigureGenerator

# Import h-m2 modules (reuse)
from model import BaselineModel, LoRAInterventionModel
from transformer_lens_wrapper import TransformerLensWrapper
from representation_analyzer import RepresentationAnalyzer
from similarity import CKASimilarity
from train import InterventionTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def setup_gpu(gpu_id: int):
    """Setup GPU environment."""
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    logger.info(f"Using GPU: {gpu_id}")

def run_single_replicate(
    config: H_M3_Config,
    seed: int,
    dataset_loader: MultiDimensionalDataset
) -> Dict:
    """Run single replicate with multi-dimensional evaluation.
    
    Returns: {seed, pre_scores, post_scores, cka_scores, deltas}"""
    set_seed(seed)
    logger.info(f"=== Replicate seed={seed} ===")
    
    # 1. Load baseline model
    baseline = BaselineModel(model_id=config.model_id)
    model = baseline.load_model()
    tokenizer = baseline.load_tokenizer()
    
    # 2. Wrap with TransformerLens (for representation analysis later)
    wrapper = TransformerLensWrapper(model_id=config.model_id, device=config.device)
    hooked_model = wrapper.load_baseline_hooked()

    # 3. Pre-intervention evaluation (all 3 dimensions) - use base model for evaluation
    logger.info("Pre-intervention evaluation...")
    evaluator = MultiDimensionalEvaluator(model, tokenizer, config.dimensions)
    pre_scores = evaluator.evaluate_all_dimensions()
    
    # 4. Extract pre-intervention activations (REAL)
    logger.info("Extracting pre-intervention activations...")
    rep_analyzer = RepresentationAnalyzer(config)

    # Prepare evaluation tokens from all dimensions
    eval_dataset = dataset_loader.get_eval_samples_per_dimension("truthfulness")
    # Select subset for activation extraction (Dataset.select returns Dataset, not dict)
    eval_subset = eval_dataset.select(range(min(100, len(eval_dataset))))
    eval_tokens_tensor = dataset_loader.prepare_tokens(eval_subset)
    eval_tokens_tensor = eval_tokens_tensor.to(config.device)

    # Extract activations using TransformerLens
    pre_acts = rep_analyzer.extract_pre_intervention(
        model=hooked_model,
        eval_tokens=eval_tokens_tensor,
        seed=seed
    )
    
    # 5. Apply LoRA intervention
    logger.info("Applying LoRA intervention...")
    train_data = dataset_loader.get_training_samples(config.training_samples)
    lora_wrapper = LoRAInterventionModel(
        base_model=model,
        lora_rank=config.lora_rank,
        lora_alpha=config.lora_alpha,
        target_modules=config.target_modules
    )
    peft_model = lora_wrapper.apply_lora()

    # Create DataLoader for training
    from torch.utils.data import DataLoader, Dataset as TorchDataset
    class SimpleDataset(TorchDataset):
        def __init__(self, data, tokenizer, max_length=512):
            self.data = data
            self.tokenizer = tokenizer
            self.max_length = max_length

        def __len__(self):
            return len(self.data)

        def __getitem__(self, idx):
            text = self.data[idx].get("question", "") if isinstance(self.data[idx], dict) else str(self.data[idx])
            encoding = self.tokenizer(
                text,
                truncation=True,
                max_length=self.max_length,
                padding="max_length",
                return_tensors="pt"
            )
            return {
                "input_ids": encoding["input_ids"].squeeze(),
                "attention_mask": encoding["attention_mask"].squeeze(),
                "labels": encoding["input_ids"].squeeze()
            }

    train_dataset = SimpleDataset(train_data, tokenizer, config.max_length)
    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)

    # Convert config to dict for trainer
    config_dict = {
        'learning_rate': config.learning_rate,
        'num_epochs': config.num_epochs,
        'batch_size': config.batch_size,
        'gradient_accumulation_steps': config.gradient_accumulation_steps,
        'warmup_ratio': config.warmup_ratio,
        'max_grad_norm': config.max_grad_norm,
        'device': config.device
    }
    trainer = InterventionTrainer(peft_model, config_dict)
    history = trainer.run_intervention(train_loader, num_epochs=config.num_epochs)
    
    # 6. Post-intervention evaluation - use trained PEFT model
    logger.info("Post-intervention evaluation...")
    post_evaluator = MultiDimensionalEvaluator(peft_model, tokenizer, config.dimensions)
    post_scores = post_evaluator.evaluate_all_dimensions()
    
    # 7. Extract post-intervention activations (REAL)
    logger.info("Extracting post-intervention activations...")

    # Convert PEFT model to HookedTransformer for activation extraction
    post_hooked_model = wrapper.convert_peft_to_hooked(peft_model)

    post_acts = rep_analyzer.extract_post_intervention(
        model=post_hooked_model,
        eval_tokens=eval_tokens_tensor,
        seed=seed
    )

    # 8. Compute CKA similarity (REAL)
    logger.info("Computing CKA similarity...")
    cka_module = CKASimilarity(device=config.device)
    cka_scores = cka_module.compute_all_layers(
        pre_acts=pre_acts,
        post_acts=post_acts,
        layers=config.layers_to_analyze
    )
    
    # 9. Compute deltas
    corr_analyzer = CrossDimensionalCorrelationAnalyzer(config.dimensions)
    deltas = corr_analyzer.compute_deltas(pre_scores, post_scores)
    
    return {
        "seed": seed,
        "pre_scores": pre_scores,
        "post_scores": post_scores,
        "cka_scores": cka_scores,
        "deltas": deltas
    }

def main():
    """Main experiment orchestrator for h-m3."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Run quick sanity check (1 epoch, 1%% data)")
    args = parser.parse_args()

    dry_run_mode = args.dry_run
    logger.info(f"Starting H-M3 Multi-Dimensional Correlation Experiment (dry_run={dry_run_mode})")

    # 1. Load config
    config = get_default_config()

    # Override config for dry run
    if dry_run_mode:
        logger.info("DRY RUN MODE: Using minimal config (1 epoch, 1 seed, 10 samples)")
        config.num_epochs = 1
        config.random_seeds = [config.random_seeds[0]]  # Only first seed
        config.training_samples = 10  # Minimal samples
        config.eval_limit = {dim: 10 for dim in config.dimensions}  # Minimal eval
        config.permutation_iterations = 10  # Fast permutation test

    set_seed(config.random_seeds[0])
    setup_gpu(0)
    
    # 2. Load datasets
    logger.info("Loading multi-dimensional datasets...")
    baseline = BaselineModel(model_id=config.model_id)
    tokenizer = baseline.load_tokenizer()
    dataset_loader = MultiDimensionalDataset(tokenizer, config.dimensions)
    
    # Load all datasets
    dataset_loader.load_truthfulqa()
    dataset_loader.load_bbq()
    dataset_loader.load_advglue()
    
    # 3. Run replicates
    all_results = []
    for seed in config.random_seeds:
        try:
            result = run_single_replicate(config, seed, dataset_loader)
            all_results.append(result)
        except Exception as e:
            logger.error(f"Replicate {seed} failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            continue
    
    if not all_results:
        logger.error("All replicates failed!")
        return
    
    # 4. Cross-dimensional correlation analysis
    logger.info("Performing correlation analysis...")
    corr_analyzer = CrossDimensionalCorrelationAnalyzer(config.dimensions)
    
    # Aggregate deltas
    deltas_per_seed = {r["seed"]: r["deltas"] for r in all_results}
    
    # Compute correlations
    correlations = corr_analyzer.compute_all_pairs(deltas_per_seed)
    
    # 5. Permutation tests
    logger.info("Running permutation tests...")
    perm_tester = PermutationTester(n_permutations=config.permutation_iterations)
    permutation_results = {}
    
    for pair, (r, p) in correlations.items():
        dim1, dim2 = pair.split("_vs_")
        deltas1 = [deltas_per_seed[seed][dim1] for seed in config.random_seeds if dim1 in deltas_per_seed[seed]]
        deltas2 = [deltas_per_seed[seed][dim2] for seed in config.random_seeds if dim2 in deltas_per_seed[seed]]
        p_perm = perm_tester.permutation_test(deltas1, deltas2)
        permutation_results[pair] = p_perm
    
    # 6. Layer-wise correlation (REAL)
    logger.info("Computing layer-wise correlations...")

    # Compute representation changes from CKA scores across all replicates
    rep_changes = {}
    for layer in config.layers_to_analyze:
        # Aggregate representation change (1 - CKA) across replicates
        layer_changes = []
        for result in all_results:
            if layer in result["cka_scores"]:
                change = 1.0 - result["cka_scores"][layer]
                layer_changes.append(change)
        if layer_changes:
            rep_changes[layer] = np.mean(layer_changes)

    perf_deltas = {
        dim: [deltas_per_seed[seed].get(dim, 0) for seed in config.random_seeds]
        for dim in config.dimensions
    }
    layer_analyzer = LayerWiseCorrelationAnalyzer(config.layers_to_analyze, config.dimensions)
    layer_correlations = layer_analyzer.correlate_layer_with_dimensions(rep_changes, perf_deltas)
    
    # 7. Visualization
    logger.info("Generating visualizations...")
    visualizer = H_M3_FigureGenerator(config.figures_dir)
    visualizer.save_all_figures({
        "correlations": correlations,
        "permutation_tests": permutation_results,
        "layer_correlations": layer_correlations,
        "deltas_per_seed": deltas_per_seed,
        "pre_scores": all_results[0]["pre_scores"],
        "post_scores": all_results[0]["post_scores"]
    })
    
    # 8. Save results
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results_data = {
        "correlations": {k: {"r": v[0], "p": v[1]} for k, v in correlations.items()},
        "permutation_tests": permutation_results,
        "deltas_per_seed": deltas_per_seed,
        "replicates": all_results
    }
    
    results_path = output_dir / "h_m3_validation.json"
    with open(results_path, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    logger.info(f"Results saved to: {results_path}")
    logger.info("H-M3 experiment completed successfully!")

if __name__ == "__main__":
    main()
