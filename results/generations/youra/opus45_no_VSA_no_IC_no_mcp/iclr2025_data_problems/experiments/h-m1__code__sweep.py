"""Sweep orchestrator for H-M1: train 7 configs, collect loss history + benchmark scores."""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import M1_CONFIGS, TRAIN_CONFIG
from train.train_logged import build_model, train_with_history

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'h-e1', 'code'))
from data.data_pipeline import build_dataset
from eval.evaluator import evaluate, compute_ensemble_score, save_results, load_results
from transformers import GPT2Tokenizer


def run_config(config, base_dir: str, tokenizer) -> dict:
    """Run single config: data -> train -> eval. Returns results dict."""
    config_id = config.config_id
    results_dir = os.path.join(base_dir, "results", config_id)
    ckpt_dir = os.path.join(base_dir, "checkpoints", config_id)
    os.makedirs(results_dir, exist_ok=True)

    benchmark_path = os.path.join(results_dir, "benchmark_results.json")
    loss_history_path = os.path.join(results_dir, "loss_history.json")

    if os.path.exists(benchmark_path) and os.path.exists(loss_history_path):
        print(f"[{config_id}] Already complete, loading from cache")
        scores = load_results(benchmark_path)
        with open(loss_history_path) as f:
            loss_history = json.load(f)
        return {
            "config_id": config_id,
            "scores": scores,
            "loss_history": loss_history,
            "checkpoint_path": os.path.join(ckpt_dir, "model"),
        }

    print(f"[{config_id}] Building dataset...")
    data = build_dataset(config, tokenizer, max_tokens=TRAIN_CONFIG["total_tokens"])

    print(f"[{config_id}] Training model...")
    model = build_model()
    checkpoint_path, loss_history = train_with_history(
        model, data, ckpt_dir, config_id,
        batch_size=TRAIN_CONFIG["batch_size"],
        total_steps=TRAIN_CONFIG["max_steps"],
    )

    with open(loss_history_path, "w") as f:
        json.dump(loss_history, f, indent=2)

    print(f"[{config_id}] Evaluating...")
    scores = evaluate(checkpoint_path)
    save_results(scores, benchmark_path)

    return {
        "config_id": config_id,
        "scores": scores,
        "loss_history": loss_history,
        "checkpoint_path": checkpoint_path,
    }


def run_sweep(configs=None, base_dir: str = "."):
    """Run full sweep over all configs."""
    if configs is None:
        configs = M1_CONFIGS

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    all_results = {}
    all_configs_path = os.path.join(base_dir, "results", "all_configs.json")

    if os.path.exists(all_configs_path):
        with open(all_configs_path) as f:
            all_results = json.load(f)

    for config in configs:
        result = run_config(config, base_dir, tokenizer)
        all_results[result["config_id"]] = {
            "scores": result["scores"],
            "loss_history": result["loss_history"],
        }

        os.makedirs(os.path.dirname(all_configs_path), exist_ok=True)
        with open(all_configs_path, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"[{result['config_id']}] Saved to {all_configs_path}")

    all_scores = {cid: r["scores"] for cid, r in all_results.items()}
    ensemble_scores = compute_ensemble_score(all_scores)
    for cid in all_results:
        all_results[cid]["ensemble_score"] = ensemble_scores.get(cid, 0.5)

    with open(all_configs_path, "w") as f:
        json.dump(all_results, f, indent=2)

    return all_results


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    run_sweep(base_dir=base_dir)
