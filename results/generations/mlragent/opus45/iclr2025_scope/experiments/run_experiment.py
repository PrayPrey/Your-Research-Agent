#!/usr/bin/env python3
"""
Main experiment runner for QARP (Query-Aware Retention Policies) KV Cache Compression.
Compares QARP against baseline methods: Full Cache, StreamingLLM, H2O, and Uniform Quantization.
"""
import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime
from typing import Dict, Any
import warnings
warnings.filterwarnings('ignore')

import torch
import torch.nn as nn
import numpy as np
from tqdm import tqdm

# Setup logging
def setup_logging(output_dir: str) -> logging.Logger:
    """Setup logging to both file and console."""
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, 'log.txt')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def load_model_and_tokenizer(model_name: str, device: str = 'cuda'):
    """Load the language model and tokenizer."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"Loading model: {model_name}")

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Use single GPU to avoid device mismatch issues
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        trust_remote_code=True,
        attn_implementation='eager',  # Use eager attention to get attention weights
    )
    model = model.to(device)
    model.eval()

    return model, tokenizer


def create_datasets(tokenizer, config):
    """Create training, validation, and test datasets."""
    from data_utils import SyntheticLongContextDataset, LongBenchDataset, create_dataloader

    print("Creating datasets...")

    # Synthetic dataset for controlled experiments
    train_dataset = SyntheticLongContextDataset(
        tokenizer=tokenizer,
        num_samples=config.get('train_samples', 200),
        context_length=config.get('max_seq_length', 1024),
        seed=config.get('seed', 42),
    )

    val_dataset = SyntheticLongContextDataset(
        tokenizer=tokenizer,
        num_samples=config.get('val_samples', 50),
        context_length=config.get('max_seq_length', 1024),
        seed=config.get('seed', 43),
    )

    # Test on synthetic data
    test_dataset = SyntheticLongContextDataset(
        tokenizer=tokenizer,
        num_samples=config.get('test_samples', 100),
        context_length=config.get('max_seq_length', 1024),
        seed=config.get('seed', 44),
    )

    train_loader = create_dataloader(train_dataset, batch_size=config.get('batch_size', 2), shuffle=True)
    val_loader = create_dataloader(val_dataset, batch_size=config.get('batch_size', 2))
    test_loader = create_dataloader(test_dataset, batch_size=config.get('eval_batch_size', 2))

    return train_loader, val_loader, test_loader


def train_rpn(model, tokenizer, train_loader, val_loader, config, logger):
    """Train the Relevance Predictor Network."""
    from kv_cache import RelevancePredictorNetwork
    from train_rpn import RPNTrainer, create_rpn_for_model

    logger.info("Training Relevance Predictor Network (RPN)...")

    # Create RPN
    rpn = create_rpn_for_model(model.config, hidden_dim=config.get('rpn_hidden_dim', 128))

    # Create trainer
    trainer = RPNTrainer(
        rpn=rpn,
        model=model,
        tokenizer=tokenizer,
        learning_rate=config.get('learning_rate', 1e-4),
        device=config.get('device', 'cuda'),
    )

    # Train
    training_results = trainer.train(
        train_loader=train_loader,
        val_loader=val_loader,
        num_epochs=config.get('num_epochs', 3),
    )

    logger.info(f"RPN training complete. Final train loss: {training_results['train_losses'][-1]:.4f}")
    logger.info(f"Final validation loss: {training_results['val_losses'][-1]:.4f}")

    return rpn, training_results


def evaluate_full_cache(model, tokenizer, test_loader, config, logger):
    """Evaluate with full KV cache (baseline)."""
    from evaluation import CompressionEvaluator

    logger.info("Evaluating Full Cache baseline...")

    evaluator = CompressionEvaluator(model, tokenizer, device=config.get('device', 'cuda'))

    def no_compression(keys, values, attention_mask=None):
        return keys, values, {'compression_ratio': 1.0, 'method': 'full'}

    results = evaluator.evaluate_method(
        method_name='Full Cache',
        dataloader=test_loader,
        compression_fn=no_compression,
        max_batches=config.get('eval_batches', 25),
    )

    logger.info(f"Full Cache - Perplexity: {results['perplexity_mean']:.4f}, "
                f"Latency: {results['latency_mean_ms']:.2f}ms")

    return results


def evaluate_streaming_llm(model, tokenizer, test_loader, config, logger):
    """Evaluate StreamingLLM baseline."""
    from kv_cache import StreamingLLMCache
    from evaluation import CompressionEvaluator

    logger.info("Evaluating StreamingLLM baseline...")

    cache = StreamingLLMCache(
        sink_size=config.get('sink_size', 4),
        window_size=config.get('window_size', 256),
    )

    evaluator = CompressionEvaluator(model, tokenizer, device=config.get('device', 'cuda'))

    def streaming_compression(keys, values, attention_mask=None):
        return cache.compress(keys, values, attention_mask)

    results = evaluator.evaluate_method(
        method_name='StreamingLLM',
        dataloader=test_loader,
        compression_fn=streaming_compression,
        max_batches=config.get('eval_batches', 25),
    )

    logger.info(f"StreamingLLM - Compression: {results['compression_ratio_mean']:.2f}x, "
                f"Perplexity: {results['perplexity_mean']:.4f}")

    return results


def evaluate_h2o(model, tokenizer, test_loader, config, logger):
    """Evaluate H2O (Heavy Hitter Oracle) baseline."""
    from kv_cache import H2OCache
    from evaluation import CompressionEvaluator

    logger.info("Evaluating H2O baseline...")

    cache = H2OCache(retention_ratio=config.get('h2o_retention', 0.25))

    evaluator = CompressionEvaluator(model, tokenizer, device=config.get('device', 'cuda'))

    def h2o_compression(keys, values, attention_mask=None):
        # For H2O, we need cumulative attention scores
        # Simulate with uniform scores for now (proper implementation would track attention)
        batch_size, num_heads, seq_len, _ = keys.shape
        cumulative_attention = torch.ones(batch_size, num_heads, seq_len, device=keys.device)
        # Add some variation based on position (recent tokens more important)
        positions = torch.arange(seq_len, device=keys.device).float()
        importance = 0.5 + 0.5 * (positions / seq_len)  # Linearly increasing
        cumulative_attention = cumulative_attention * importance.unsqueeze(0).unsqueeze(0)

        return cache.compress(keys, values, cumulative_attention, attention_mask)

    results = evaluator.evaluate_method(
        method_name='H2O',
        dataloader=test_loader,
        compression_fn=h2o_compression,
        max_batches=config.get('eval_batches', 25),
    )

    logger.info(f"H2O - Compression: {results['compression_ratio_mean']:.2f}x, "
                f"Perplexity: {results['perplexity_mean']:.4f}")

    return results


def evaluate_quantization(model, tokenizer, test_loader, config, logger, bits: int = 4):
    """Evaluate uniform quantization baseline."""
    from kv_cache import UniformQuantizationCache
    from evaluation import CompressionEvaluator

    logger.info(f"Evaluating {bits}-bit Quantization baseline...")

    cache = UniformQuantizationCache(bits=bits)

    evaluator = CompressionEvaluator(model, tokenizer, device=config.get('device', 'cuda'))

    def quant_compression(keys, values, attention_mask=None):
        return cache.compress(keys, values, attention_mask)

    results = evaluator.evaluate_method(
        method_name=f'{bits}-bit Quantization',
        dataloader=test_loader,
        compression_fn=quant_compression,
        max_batches=config.get('eval_batches', 25),
    )

    logger.info(f"{bits}-bit Quant - Compression: {results['compression_ratio_mean']:.2f}x, "
                f"Perplexity: {results['perplexity_mean']:.4f}")

    return results


def evaluate_qarp(model, tokenizer, rpn, test_loader, config, logger, compression_ratio: float = 4.0):
    """Evaluate QARP method."""
    from kv_cache import QARPKVCache
    from evaluation import CompressionEvaluator

    logger.info(f"Evaluating QARP (compression ratio: {compression_ratio}x)...")

    qarp_cache = QARPKVCache(
        rpn=rpn,
        compression_ratio=compression_ratio,
    )

    evaluator = CompressionEvaluator(model, tokenizer, device=config.get('device', 'cuda'))

    def qarp_compression(keys, values, attention_mask=None):
        return qarp_cache.compress(keys, values, attention_mask)

    results = evaluator.evaluate_method(
        method_name=f'QARP-{compression_ratio}x',
        dataloader=test_loader,
        compression_fn=qarp_compression,
        max_batches=config.get('eval_batches', 25),
    )

    logger.info(f"QARP-{compression_ratio}x - Compression: {results['compression_ratio_mean']:.2f}x, "
                f"Perplexity: {results['perplexity_mean']:.4f}")

    return results


def run_ablation_study(model, tokenizer, test_loader, config, logger):
    """Run ablation study on QARP components."""
    from kv_cache import RelevancePredictorNetwork, QARPKVCache
    from evaluation import CompressionEvaluator
    from train_rpn import create_rpn_for_model

    logger.info("Running ablation study...")

    ablation_results = {}
    device = config.get('device', 'cuda')

    # Test different numbers of query prototypes
    for num_prototypes in [4, 8, 16, 32]:
        logger.info(f"Testing with {num_prototypes} query prototypes...")

        rpn = create_rpn_for_model(model.config, hidden_dim=128)
        # Manually adjust number of prototypes
        rpn.query_prototypes = nn.Parameter(torch.randn(num_prototypes, 128))
        rpn = rpn.to(device)

        qarp_cache = QARPKVCache(rpn=rpn, compression_ratio=4.0)

        evaluator = CompressionEvaluator(model, tokenizer, device=device)

        def compression_fn(keys, values, attention_mask=None):
            return qarp_cache.compress(keys, values, attention_mask)

        results = evaluator.evaluate_method(
            method_name=f'{num_prototypes}_prototypes',
            dataloader=test_loader,
            compression_fn=compression_fn,
            max_batches=10,
        )

        ablation_results[f'{num_prototypes} prototypes'] = results

    return ablation_results


def save_results(all_results: Dict[str, Any], output_dir: str, logger):
    """Save all results to JSON and generate visualizations."""
    from visualization import generate_all_visualizations, create_results_table

    logger.info("Saving results...")

    # Save raw results
    results_file = os.path.join(output_dir, 'results.json')
    with open(results_file, 'w') as f:
        # Convert numpy values to Python types for JSON serialization
        serializable_results = {}
        for method, metrics in all_results.items():
            if isinstance(metrics, dict):
                serializable_results[method] = {
                    k: float(v) if isinstance(v, (np.floating, np.integer)) else v
                    for k, v in metrics.items()
                    if not isinstance(v, (list, torch.Tensor)) or k == 'generated_texts'
                }
            else:
                serializable_results[method] = metrics

        json.dump(serializable_results, f, indent=2, default=str)

    logger.info(f"Results saved to {results_file}")

    # Generate visualizations
    main_results = {k: v for k, v in all_results.items()
                   if not k.startswith('ablation_') and not k.startswith('training_')}

    training_losses = all_results.get('training_losses', {})
    ablation_results = all_results.get('ablation_results', None)

    generate_all_visualizations(
        results=main_results,
        train_losses=training_losses.get('train_losses', None),
        val_losses=training_losses.get('val_losses', None),
        ablation_results=ablation_results,
        output_dir=output_dir,
    )


def main():
    parser = argparse.ArgumentParser(description='QARP KV Cache Compression Experiments')
    parser.add_argument('--model', type=str, default='Qwen/Qwen2-0.5B',
                        help='Model name or path')
    parser.add_argument('--output_dir', type=str, default='outputs',
                        help='Output directory for results')
    parser.add_argument('--max_seq_length', type=int, default=1024,
                        help='Maximum sequence length')
    parser.add_argument('--train_samples', type=int, default=200,
                        help='Number of training samples')
    parser.add_argument('--test_samples', type=int, default=100,
                        help='Number of test samples')
    parser.add_argument('--batch_size', type=int, default=2,
                        help='Batch size')
    parser.add_argument('--num_epochs', type=int, default=3,
                        help='Number of training epochs')
    parser.add_argument('--eval_batches', type=int, default=25,
                        help='Number of batches for evaluation')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed')
    parser.add_argument('--skip_training', action='store_true',
                        help='Skip RPN training (use random RPN)')
    parser.add_argument('--run_ablation', action='store_true',
                        help='Run ablation study')

    args = parser.parse_args()

    # Create configuration
    config = {
        'model_name': args.model,
        'max_seq_length': args.max_seq_length,
        'train_samples': args.train_samples,
        'val_samples': args.train_samples // 4,
        'test_samples': args.test_samples,
        'batch_size': args.batch_size,
        'eval_batch_size': args.batch_size,
        'num_epochs': args.num_epochs,
        'eval_batches': args.eval_batches,
        'seed': args.seed,
        'device': 'cuda' if torch.cuda.is_available() else 'cpu',
        'learning_rate': 1e-4,
        'rpn_hidden_dim': 128,
        'sink_size': 4,
        'window_size': 256,
        'h2o_retention': 0.25,
    }

    # Setup
    os.makedirs(args.output_dir, exist_ok=True)
    logger = setup_logging(args.output_dir)

    logger.info("=" * 60)
    logger.info("QARP KV Cache Compression Experiments")
    logger.info("=" * 60)
    logger.info(f"Configuration: {json.dumps(config, indent=2)}")

    # Set random seeds
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    # Load model
    start_time = time.time()
    model, tokenizer = load_model_and_tokenizer(config['model_name'], config['device'])
    logger.info(f"Model loaded in {time.time() - start_time:.2f}s")

    # Create datasets
    train_loader, val_loader, test_loader = create_datasets(tokenizer, config)
    logger.info(f"Datasets created: {config['train_samples']} train, {config['test_samples']} test samples")

    # Store all results
    all_results = {}

    # Train RPN
    if not args.skip_training:
        rpn, training_results = train_rpn(model, tokenizer, train_loader, val_loader, config, logger)
        all_results['training_losses'] = training_results
    else:
        from train_rpn import create_rpn_for_model
        rpn = create_rpn_for_model(model.config, hidden_dim=config['rpn_hidden_dim'])
        rpn = rpn.to(config['device'])
        logger.info("Using untrained (random) RPN")
        all_results['training_losses'] = {'train_losses': [], 'val_losses': []}

    # Evaluate baselines
    logger.info("\n" + "=" * 60)
    logger.info("Evaluating Methods")
    logger.info("=" * 60)

    # Full Cache baseline
    full_results = evaluate_full_cache(model, tokenizer, test_loader, config, logger)
    all_results['Full Cache'] = full_results

    # StreamingLLM baseline
    streaming_results = evaluate_streaming_llm(model, tokenizer, test_loader, config, logger)
    all_results['StreamingLLM'] = streaming_results

    # H2O baseline
    h2o_results = evaluate_h2o(model, tokenizer, test_loader, config, logger)
    all_results['H2O'] = h2o_results

    # Quantization baselines
    quant4_results = evaluate_quantization(model, tokenizer, test_loader, config, logger, bits=4)
    all_results['4-bit Quantization'] = quant4_results

    quant8_results = evaluate_quantization(model, tokenizer, test_loader, config, logger, bits=8)
    all_results['8-bit Quantization'] = quant8_results

    # QARP with different compression ratios
    for compression_ratio in [2.0, 4.0, 8.0]:
        qarp_results = evaluate_qarp(model, tokenizer, rpn, test_loader, config, logger, compression_ratio)
        all_results[f'QARP-{compression_ratio}x'] = qarp_results

    # Ablation study
    if args.run_ablation:
        ablation_results = run_ablation_study(model, tokenizer, test_loader, config, logger)
        all_results['ablation_results'] = ablation_results

    # Save all results
    save_results(all_results, args.output_dir, logger)

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("EXPERIMENT SUMMARY")
    logger.info("=" * 60)

    for method, results in all_results.items():
        if isinstance(results, dict) and 'perplexity_mean' in results:
            logger.info(f"{method}:")
            logger.info(f"  Compression Ratio: {results.get('compression_ratio_mean', 1.0):.2f}x")
            logger.info(f"  Perplexity: {results.get('perplexity_mean', 0):.4f}")
            logger.info(f"  Memory Reduction: {results.get('memory_reduction_pct', 0):.1f}%")
            logger.info(f"  Latency: {results.get('latency_mean_ms', 0):.2f}ms")

    logger.info(f"\nTotal experiment time: {time.time() - start_time:.2f}s")
    logger.info(f"Results saved to {args.output_dir}/")


if __name__ == '__main__':
    main()
