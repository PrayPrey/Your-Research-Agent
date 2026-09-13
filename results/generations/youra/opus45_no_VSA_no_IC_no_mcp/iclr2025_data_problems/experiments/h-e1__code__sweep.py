"""Sweep orchestrator: runs all 15 configs sequentially with resume support."""

import os
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SWEEP_CONFIGS, CurationConfig
from data import build_dataset
from train import build_model, train
from eval import evaluate, save_results, load_results
from transformers import GPT2Tokenizer


def run_config(config: CurationConfig, base_dir: str, tokenizer) -> dict:
    """Run data->train->eval pipeline for one config."""
    config_id = config.config_id
    ckpt_dir = os.path.join(base_dir, "checkpoints", config_id)
    results_file = os.path.join(base_dir, "results", config_id, "benchmark_results.json")

    if os.path.exists(results_file):
        print(f"[{config_id}] Results exist, loading...")
        with open(results_file, "r") as f:
            return json.load(f)

    model_path = os.path.join(ckpt_dir, "model")
    if os.path.exists(model_path):
        print(f"[{config_id}] Checkpoint exists, skipping training")
    else:
        print(f"[{config_id}] Building dataset...")
        data = build_dataset(config, tokenizer)

        print(f"[{config_id}] Training...")
        model = build_model()
        train(model, data, ckpt_dir, config_id)

    print(f"[{config_id}] Evaluating...")
    scores = evaluate(model_path)

    result = {
        "config_id": config_id,
        "perplexity_pct": config.perplexity_pct,
        "dedup": config.dedup,
        "scores": scores,
        "checkpoint_path": model_path,
    }

    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    with open(results_file, "w") as f:
        json.dump(result, f, indent=2)

    return result


def run_sweep(configs: list = None, base_dir: str = ".") -> dict:
    """Run full 15-config sweep with resume support."""
    if configs is None:
        configs = SWEEP_CONFIGS

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    all_results_file = os.path.join(base_dir, "results", "all_configs.json")
    all_results = load_results(all_results_file)

    for config in configs:
        if config.config_id in all_results:
            print(f"[{config.config_id}] Already completed, skipping")
            continue

        result = run_config(config, base_dir, tokenizer)
        all_results[config.config_id] = result
        save_results(all_results, all_results_file)
        print(f"[{config.config_id}] Done, saved to {all_results_file}")

    return all_results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", default=".", help="Base directory for outputs")
    parser.add_argument("--config", type=str, help="Run single config by ID")
    args = parser.parse_args()

    if args.config:
        config = next((c for c in SWEEP_CONFIGS if c.config_id == args.config), None)
        if config:
            tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
            run_config(config, args.base_dir, tokenizer)
        else:
            print(f"Config {args.config} not found")
    else:
        run_sweep(base_dir=args.base_dir)
