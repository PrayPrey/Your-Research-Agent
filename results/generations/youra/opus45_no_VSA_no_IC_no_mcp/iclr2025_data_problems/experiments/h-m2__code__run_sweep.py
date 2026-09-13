"""Sweep orchestration: run all dedup levels x seeds."""
import os
import json
from typing import Dict
from config import DEDUP_LEVELS, ScaledExperimentConfig, DeduplicationConfig
from data_pipeline import download_redpajama, build_dataset, tokenize_and_pack, save_packed_tokens, load_packed_tokens
from train import train_one_config
from evaluate import run_benchmarks, save_results

def run_full_sweep(cfg: ScaledExperimentConfig, base_dir: str = ".") -> Dict:
    """Orchestrate full sweep: 5 dedup levels x 3 seeds."""
    results_path = os.path.join(base_dir, "results", "sweep_results.json")

    # Load existing results if resuming
    if os.path.exists(results_path):
        with open(results_path) as f:
            results = json.load(f)
        print(f"Resuming from {len(results)} completed levels")
    else:
        results = {}

    # Download data once
    raw_docs = download_redpajama(num_samples=cfg.num_samples, cache_dir=os.path.join(base_dir, "data/raw"))

    dedup_stats = {}

    for level_cfg in DEDUP_LEVELS:
        level = level_cfg.level
        print(f"\n{'='*60}")
        print(f"Processing dedup level: {level}")
        print(f"{'='*60}")

        # Prepare deduplicated + packed data
        packed_path = os.path.join(base_dir, "data/packed", f"{level}.pt")
        if os.path.exists(packed_path):
            tokens = load_packed_tokens(level, os.path.join(base_dir, "data/packed"))
        else:
            deduped_docs = build_dataset(raw_docs.copy(), level_cfg)
            dedup_stats[level] = {
                "original": len(raw_docs),
                "deduplicated": len(deduped_docs),
                "removal_pct": (1 - len(deduped_docs)/len(raw_docs)) * 100
            }
            tokens = tokenize_and_pack(deduped_docs, cfg.total_tokens, cfg.seq_len)
            save_packed_tokens(tokens, level, os.path.join(base_dir, "data/packed"))

        if level not in results:
            results[level] = {}

        for seed in cfg.seeds:
            if str(seed) in results.get(level, {}):
                print(f"  Skipping {level}/seed{seed} (already completed)")
                continue

            print(f"\n--- Training {level}/seed{seed} ---")
            ckpt_dir = os.path.join(base_dir, "checkpoints", level, f"seed{seed}")
            ckpt_path, loss_history = train_one_config(level, seed, tokens, cfg, ckpt_dir)

            print(f"--- Evaluating {level}/seed{seed} ---")
            scores = run_benchmarks(ckpt_path, cfg)

            results[level][str(seed)] = {
                "checkpoint": ckpt_path,
                "scores": scores,
                "final_loss": loss_history[-1] if loss_history else None
            }

            save_results(scores, level, seed, os.path.join(base_dir, "results"))

            # Save incremental results
            os.makedirs(os.path.dirname(results_path), exist_ok=True)
            with open(results_path, "w") as f:
                json.dump(results, f, indent=2)
            print(f"Saved incremental results to {results_path}")

    # Save dedup stats
    stats_path = os.path.join(base_dir, "results", "dedup_stats.json")
    with open(stats_path, "w") as f:
        json.dump(dedup_stats, f, indent=2)

    return results

def run_single_arm(level_cfg: DeduplicationConfig, seed: int, cfg: ScaledExperimentConfig, base_dir: str = ".") -> Dict:
    """Run single (level, seed) arm."""
    level = level_cfg.level

    # Load or prepare data
    packed_path = os.path.join(base_dir, "data/packed", f"{level}.pt")
    if os.path.exists(packed_path):
        tokens = load_packed_tokens(level, os.path.join(base_dir, "data/packed"))
    else:
        raw_docs = download_redpajama(num_samples=cfg.num_samples, cache_dir=os.path.join(base_dir, "data/raw"))
        deduped_docs = build_dataset(raw_docs, level_cfg)
        tokens = tokenize_and_pack(deduped_docs, cfg.total_tokens, cfg.seq_len)
        save_packed_tokens(tokens, level, os.path.join(base_dir, "data/packed"))

    ckpt_dir = os.path.join(base_dir, "checkpoints", level, f"seed{seed}")
    ckpt_path, loss_history = train_one_config(level, seed, tokens, cfg, ckpt_dir)

    scores = run_benchmarks(ckpt_path, cfg)

    return {
        "checkpoint": ckpt_path,
        "scores": scores,
        "final_loss": loss_history[-1] if loss_history else None
    }
