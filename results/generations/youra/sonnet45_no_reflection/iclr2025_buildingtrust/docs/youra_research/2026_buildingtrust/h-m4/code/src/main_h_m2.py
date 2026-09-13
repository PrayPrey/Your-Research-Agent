"""
Main Orchestrator for H-M2 Hypothesis
Workflow: pre-extract → train → post-extract → analyze → visualize
"""

import torch
import random
import numpy as np
import logging
import json
from pathlib import Path
from typing import Dict, List
from dataclasses import asdict

from config import H_M2_Config, get_default_config
from transformer_lens_wrapper import TransformerLensWrapper
from representation_analyzer import RepresentationAnalyzer
from similarity import CKASimilarity, CorrelationAnalyzer, StatisticalAnalyzer
from visualize import FigureGenerator
from data import TrustworthinessDataset as TruthfulQADataset
from model import BaselineModel, LoRAInterventionModel
from train import InterventionTrainer
from transformers import AutoTokenizer
from torch.utils.data import DataLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    if torch.cuda.is_available():
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def setup_gpu(gpu_id: int = 0):
    """Setup GPU environment."""
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    logger.info(f"Using GPU {gpu_id}")


def train_single_replicate(
    config: H_M2_Config,
    seed: int,
    eval_tokens: torch.Tensor,
    train_loader: DataLoader
) -> Dict:
    """
    Train single replicate with activation tracking.

    Returns:
        {
            "seed": int,
            "pre_activations_path": str,
            "post_activations_path": str,
            "cka_scores": Dict[str, float],
            "training_history": Dict
        }
    """
    logger.info(f"=" * 80)
    logger.info(f"Training replicate with seed={seed}")
    logger.info(f"=" * 80)

    set_seed(seed)

    # Step 1: Load baseline model with TransformerLens
    logger.info("Step 1: Loading baseline model with TransformerLens")
    tl_wrapper = TransformerLensWrapper(config.model_id, config.device)
    hooked_baseline = tl_wrapper.load_baseline_hooked()

    # Verify hooks
    tl_wrapper.verify_hooks(config.layers_to_analyze)

    # Step 2: Extract pre-intervention activations
    logger.info("Step 2: Extracting pre-intervention activations")
    analyzer = RepresentationAnalyzer(config)
    pre_acts = analyzer.extract_pre_intervention(hooked_baseline, eval_tokens, seed)
    pre_acts_path = f"pre_activations_seed{seed}.pt"

    # Step 3: Convert to HuggingFace + LoRA for training
    logger.info("Step 3: Applying LoRA intervention")
    baseline_model = BaselineModel(model_id=config.model_id)
    hf_model = baseline_model.load_model()

    lora_wrapper = LoRAInterventionModel(
        base_model=hf_model,
        lora_rank=config.lora_rank,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=config.target_modules
    )
    peft_model = lora_wrapper.apply_lora()

    # Step 4: Train with h-m1 protocol
    logger.info("Step 4: Training LoRA model")
    trainer = InterventionTrainer(
        model=peft_model,
        config={
            'learning_rate': config.learning_rate,
            'num_epochs': config.num_epochs,
            'device': config.device,
            'max_grad_norm': config.max_grad_norm,
            'warmup_ratio': config.warmup_ratio
        }
    )
    history = trainer.run_intervention(train_loader, num_epochs=config.num_epochs)

    # Step 5: Convert trained model back to HookedTransformer
    logger.info("Step 5: Converting trained model to HookedTransformer")
    hooked_post = tl_wrapper.convert_peft_to_hooked(peft_model)

    # Step 6: Extract post-intervention activations
    logger.info("Step 6: Extracting post-intervention activations")
    post_acts = analyzer.extract_post_intervention(hooked_post, eval_tokens, seed)
    post_acts_path = f"post_activations_seed{seed}.pt"

    # Step 7: Compute CKA similarity
    logger.info("Step 7: Computing CKA similarity")
    cka_module = CKASimilarity(device=config.device)
    cka_scores = cka_module.compute_all_layers(
        pre_acts, post_acts, config.layers_to_analyze
    )

    # Save CKA scores
    cka_path = Path(config.output_dir) / f"cka_scores_seed{seed}.json"
    cka_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cka_path, 'w') as f:
        json.dump(cka_scores, f, indent=2)

    logger.info(f"Replicate {seed} complete")

    return {
        "seed": seed,
        "pre_activations_path": pre_acts_path,
        "post_activations_path": post_acts_path,
        "cka_scores": cka_scores,
        "training_history": history
    }


def run_all_replicates(config: H_M2_Config) -> List[Dict]:
    """Run N=3 replicates with different seeds."""
    logger.info("Preparing data...")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(config.model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Prepare evaluation tokens
    dataset = TruthfulQADataset(tokenizer, max_length=config.max_length)
    eval_samples = dataset.prepare_training_subset(n_samples=config.training_samples)

    # Tokenize evaluation samples
    eval_texts = [sample['question'] for sample in eval_samples]
    eval_tokens = tokenizer(
        eval_texts,
        padding=True,
        truncation=True,
        max_length=config.max_length,
        return_tensors='pt'
    )['input_ids'].to(config.device)

    # Prepare training data
    train_data = dataset.prepare_training_subset(n_samples=config.training_samples)

    # Create DataLoader
    def collate_fn(batch):
        questions = [item['question'] for item in batch]
        encoded = tokenizer(
            questions,
            padding=True,
            truncation=True,
            max_length=config.max_length,
            return_tensors='pt'
        )
        return {
            'input_ids': encoded['input_ids'],
            'attention_mask': encoded['attention_mask'],
            'labels': encoded['input_ids'].clone()
        }

    train_loader = DataLoader(
        train_data,
        batch_size=config.batch_size,
        shuffle=True,
        collate_fn=collate_fn
    )

    # Run replicates
    all_results = []
    for seed in config.random_seeds:
        result = train_single_replicate(config, seed, eval_tokens, train_loader)
        all_results.append(result)

    return all_results


def main():
    """
    Main experiment orchestrator.

    Workflow:
        1. Load configuration
        2. Setup environment (GPU, seeds)
        3. For each replicate:
           a. Extract pre-intervention activations
           b. Apply LoRA intervention (h-m1 protocol)
           c. Extract post-intervention activations
           d. Compute CKA similarity
        4. Aggregate results across replicates
        5. Statistical analysis (correlation)
        6. Generate visualizations
        7. Evaluate gate (p < 0.05)
        8. Save validation report
    """
    logger.info("=" * 80)
    logger.info("H-M2 Representation Change Validation Experiment")
    logger.info("=" * 80)

    # Step 1: Load configuration
    config = get_default_config()
    logger.info(f"Configuration loaded: {config.project_name}")

    # Step 2: Setup environment
    setup_gpu(0)
    set_seed(config.random_seeds[0])

    # Step 3: Run all replicates
    all_results = run_all_replicates(config)

    # Step 4: Aggregate results
    logger.info("Aggregating results across replicates")
    corr_analyzer = CorrelationAnalyzer(performance_delta=config.h_m1_performance_delta)
    aggregated_cka = corr_analyzer.aggregate_across_replicates(
        [r["cka_scores"] for r in all_results]
    )

    # Step 5: Compute representation change
    change_magnitudes = corr_analyzer.compute_representation_change(aggregated_cka)

    # Step 6: Correlate with h-m1 performance improvement
    corr_result = corr_analyzer.correlate_representation_performance(
        list(change_magnitudes.values()),
        performance_delta=config.h_m1_performance_delta
    )

    # Step 7: Evaluate gate
    stat_analyzer = StatisticalAnalyzer()
    gate_result = stat_analyzer.evaluate_gate(
        aggregated_cka,
        performance_delta=config.h_m1_performance_delta
    )

    logger.info(f"Gate Result: {'PASS' if gate_result['pass'] else 'FAIL'}")
    logger.info(f"  Correlation: {gate_result['correlation']:.4f}")
    logger.info(f"  P-value: {gate_result['p_value']:.4e}")
    logger.info(f"  Mean Change: {gate_result['mean_change']:.4f}")
    logger.info(f"  Layers Changed: {gate_result['layers_changed']}/{gate_result['total_layers']}")

    # Step 8: Generate visualizations
    logger.info("Generating visualizations")
    visualizer = FigureGenerator(config.figures_dir)
    visualizer.save_all_figures(aggregated_cka, corr_result)

    # Step 9: Save final results
    final_results = {
        "hypothesis_id": "h-m2",
        "experiment_name": config.project_name,
        "replicates": all_results,
        "aggregated_cka": aggregated_cka,
        "change_magnitudes": change_magnitudes,
        "correlation": corr_result,
        "gate": gate_result,
        "config": asdict(config)
    }

    results_path = Path(config.output_dir) / "h_m2_validation.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, 'w') as f:
        json.dump(final_results, f, indent=2)

    logger.info(f"Results saved to {results_path}")
    logger.info("=" * 80)
    logger.info("H-M2 Experiment Complete")
    logger.info("=" * 80)

    return final_results


if __name__ == "__main__":
    main()
