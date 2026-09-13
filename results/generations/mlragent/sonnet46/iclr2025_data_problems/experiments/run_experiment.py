"""Main experiment runner for DynaMix: Adaptive Data Mixing.

Hypothesis: DynaMix (adaptive data mixing with RL controller and gradient SNR signals)
achieves lower perplexity and faster convergence compared to static baseline methods.

Experiment:
1. Load real text data from 5 domains (web, code, science, wiki, instructions)
2. Train small GPT-2 style language model with each mixing strategy
3. Evaluate on per-domain and average perplexity
4. Compare: Static Uniform, Static Tuned, DoReMi-style, PiKE-style, DynaMix
"""

import os
import sys
import json
import logging
import time
import copy
import numpy as np
import torch

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import config
from config import (PROXY_MODEL_SIZES, DOMAINS, MAX_STEPS, EVAL_INTERVAL,
                    DEVICE, SEED, RESULTS_DIR, DATA_CACHE_DIR)
from data_utils import get_tokenizer, load_all_domains, DomainDataset, get_eval_data
from model import create_model
from baselines import UniformMixer, StaticTunedMixer, DoReMiStyleMixer, PiKEStyleMixer
from dynamix import DynaMixController
from trainer import train_model
from visualization import generate_all_figures

# Setup logging
os.makedirs(os.path.join(BASE_DIR, "outputs"), exist_ok=True)
log_path = os.path.join(BASE_DIR, "outputs", "log.txt")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


def set_seed(seed):
    """Set random seeds for reproducibility."""
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def run_single_experiment(mixer, model_config, domain_data, eval_data,
                           max_steps, device, run_name):
    """Run a single experiment with a given mixer."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Starting experiment: {run_name}")
    logger.info(f"Model: {model_config['name']}, Steps: {max_steps}")
    logger.info(f"Mixer: {mixer.name if hasattr(mixer, 'name') else type(mixer).__name__}")
    logger.info(f"{'='*60}")

    set_seed(SEED)

    # Create fresh model
    tokenizer = get_tokenizer()
    vocab_size = tokenizer.vocab_size
    model = create_model(model_config, vocab_size, config.SEQ_LEN, device)

    logger.info(f"Model parameters: {model.num_parameters():,}")

    # Create dataset
    dataset = DomainDataset(domain_data, config.SEQ_LEN)

    # Train
    start_time = time.time()
    metrics = train_model(
        model=model,
        dataset=dataset,
        mixer=mixer,
        eval_data=eval_data,
        max_steps=max_steps,
        eval_interval=EVAL_INTERVAL,
        device=device,
        run_name=run_name
    )
    elapsed = time.time() - start_time

    metrics['run_name'] = run_name
    metrics['elapsed_seconds'] = elapsed
    metrics['n_params'] = model.num_parameters()

    logger.info(f"Experiment {run_name} complete. Final eval loss: {metrics['final_eval_loss']:.4f}")
    logger.info(f"Total time: {elapsed:.1f}s")

    return metrics, model


def main():
    """Main experiment runner."""
    logger.info("=" * 70)
    logger.info("DynaMix: Adaptive Data Mixing Experiment")
    logger.info("=" * 70)
    logger.info(f"Device: {DEVICE}")
    logger.info(f"Seed: {SEED}")

    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    # Setup directories
    output_dir = os.path.join(BASE_DIR, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    # Load tokenizer
    logger.info("\nLoading tokenizer...")
    tokenizer = get_tokenizer()
    vocab_size = tokenizer.vocab_size
    logger.info(f"Vocabulary size: {vocab_size}")

    # Load domain data
    logger.info("\nLoading domain data...")
    domain_data = load_all_domains(tokenizer, max_tokens=config.TOKENS_PER_DOMAIN)

    logger.info("\nDomain data summary:")
    for domain, data in domain_data.items():
        logger.info(f"  {domain}: {len(data):,} tokens")

    # Create evaluation data
    logger.info("\nCreating evaluation splits...")
    eval_data = get_eval_data(domain_data, config.SEQ_LEN, n_batches=20, device=DEVICE)
    logger.info(f"Eval domains: {list(eval_data.keys())}")

    # Use small proxy model for efficiency
    model_config = PROXY_MODEL_SIZES[0]  # Small model
    logger.info(f"\nUsing model config: {model_config['name']}")

    # Define experiments
    experiments = [
        ("Static Uniform", UniformMixer()),
        ("Static Tuned", StaticTunedMixer()),
        ("DoReMi-style", DoReMiStyleMixer()),
        ("PiKE-style", PiKEStyleMixer()),
        ("DynaMix", DynaMixController()),
    ]

    all_results = {}
    dynamix_controller = None

    for method_name, mixer in experiments:
        try:
            metrics, model = run_single_experiment(
                mixer=mixer,
                model_config=model_config,
                domain_data=domain_data,
                eval_data=eval_data,
                max_steps=MAX_STEPS,
                device=DEVICE,
                run_name=method_name
            )
            all_results[method_name] = metrics

            if method_name == "DynaMix":
                dynamix_controller = mixer
                # Add RL training stats to metrics
                metrics['ppo_losses'] = mixer.ppo_losses
                metrics['value_losses'] = mixer.value_losses

        except Exception as e:
            logger.error(f"Experiment {method_name} failed: {e}", exc_info=True)
            continue

    # Add scaling law observations from proxy models
    if dynamix_controller is not None:
        # Fit scaling law from proxy observations collected during DynaMix training
        n_params = model.num_parameters()
        for i, (step, eval_loss) in enumerate(zip(
                all_results.get('DynaMix', {}).get('eval_steps', []),
                all_results.get('DynaMix', {}).get('domain_eval_losses', []))):
            compute = step * config.BATCH_SIZE * config.SEQ_LEN
            if compute > 0:
                dynamix_controller.scaling_law.add_observation(
                    n_params=n_params,
                    compute=max(compute, 1),
                    mixture=dynamix_controller.current_weights,
                    loss=eval_loss
                )
        dynamix_controller.scaling_law.fit()

    # Save raw results
    results_path = os.path.join(output_dir, "results.json")
    # Convert numpy arrays to lists for JSON serialization
    def convert_for_json(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert_for_json(i) for i in obj]
        return obj

    serializable_results = convert_for_json(all_results)
    with open(results_path, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    logger.info(f"\nResults saved to {results_path}")

    # Generate figures
    logger.info("\nGenerating figures...")
    figure_paths = generate_all_figures(all_results, output_dir, controller=dynamix_controller)
    logger.info(f"Figures generated: {list(figure_paths.keys())}")

    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("EXPERIMENT SUMMARY")
    logger.info("=" * 70)
    logger.info(f"{'Method':<20} {'Final Eval Loss':>15} {'Avg Perplexity':>15} {'Time (s)':>10}")
    logger.info("-" * 70)

    for method, metrics in all_results.items():
        final_loss = metrics.get('final_eval_loss', float('nan'))
        avg_ppl = np.exp(min(final_loss, 15))
        elapsed = metrics.get('elapsed_seconds', 0)
        logger.info(f"{method:<20} {final_loss:>15.4f} {avg_ppl:>15.2f} {elapsed:>10.1f}")

    # Compute relative improvements over uniform baseline
    if 'Static Uniform' in all_results and 'DynaMix' in all_results:
        base_loss = all_results['Static Uniform']['final_eval_loss']
        dyn_loss = all_results['DynaMix']['final_eval_loss']
        improvement = (base_loss - dyn_loss) / base_loss * 100
        logger.info(f"\nDynaMix vs Static Uniform: {improvement:.2f}% relative loss reduction")

    logger.info("\nAll experiments complete!")
    return all_results, figure_paths, dynamix_controller


if __name__ == "__main__":
    main()
