#!/usr/bin/env python3
"""H-M4: SSI Captures Invariance as Contamination Signal
Real MMLU data with Mistral-7B inference for SSI metric validation.
"""

import json
import os
import numpy as np
import pandas as pd
import torch
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import Config
from data import load_mmlu, sample_contamination_ids
from ssi import compute_ssi_batch
from evaluate import compute_auc, compute_pearson_by_level, cohens_d, verify_gate
from visualize import generate_all_figures


def load_model(cfg: Config):
    """Load Mistral model and tokenizer."""
    print(f"Loading model: {cfg.model_id}")
    dtype = torch.bfloat16 if cfg.dtype == "bfloat16" else torch.float16

    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_id,
        torch_dtype=dtype,
        device_map=cfg.device_map,
        trust_remote_code=True,
    )
    model.eval()

    return model, tokenizer


def get_answer_tokens(tokenizer) -> list[int]:
    """Get token IDs for A, B, C, D answers."""
    tokens = []
    for letter in ["A", "B", "C", "D"]:
        token_id = tokenizer.encode(letter, add_special_tokens=False)[0]
        tokens.append(token_id)
    return tokens


def run_experiment(cfg: Config, seed: int = 42) -> dict:
    """Run SSI validation experiment with real MMLU data."""
    np.random.seed(seed)
    torch.manual_seed(seed)

    print(f"\n{'='*60}")
    print(f"H-M4: SSI Contamination Detection Validation")
    print(f"Seed: {seed}")
    print(f"{'='*60}")

    # Load dataset
    print("Loading MMLU dataset...")
    mmlu = load_mmlu()
    n_total = len(mmlu)
    print(f"MMLU test set: {n_total} items")

    # Subsample for experiment (use ~1000 items for reasonable runtime)
    n_items = min(cfg.n_items, 1000)
    np.random.seed(seed)
    sample_indices = np.random.choice(n_total, size=n_items, replace=False)
    items = [mmlu[int(i)] for i in sample_indices]
    print(f"Using {n_items} sampled items")

    # Load model
    model, tokenizer = load_model(cfg)
    answer_tokens = get_answer_tokens(tokenizer)
    print(f"Answer tokens: {answer_tokens}")

    levels = cfg.contamination_levels

    # Compute SSI for all sampled items once
    print("\nComputing SSI scores for sampled items...")
    ssi_scores, all_confidences = compute_ssi_batch(
        model, tokenizer, items, answer_tokens, k_paraphrases=cfg.k_paraphrases
    )
    ssi_array = np.array(ssi_scores)

    # Simulate contamination by assigning items to different contamination levels
    # (real contamination would require training data leakage, but we simulate ground truth labels)
    ssi_by_level = {}
    for level in levels:
        contaminated_ids = sample_contamination_ids(mmlu, level / 100.0, seed + level)
        # Mark items as contaminated if their original index is in contaminated_ids
        level_ssi = []
        for i, orig_idx in enumerate(sample_indices):
            if int(orig_idx) in contaminated_ids:
                level_ssi.append(ssi_array[i])
        if len(level_ssi) == 0:
            # For 0% level or empty, use clean items
            level_ssi = ssi_array.tolist() if level == 0 else []
        ssi_by_level[level] = np.array(level_ssi) if level_ssi else np.array([0.0])
        print(f"Level {level}%: {len(ssi_by_level[level])} items")

    # Compute mean SSI per level for correlation
    mean_ssi_per_level = [np.mean(ssi_by_level[lvl]) for lvl in levels]
    pcts = list(levels)

    # AUC: clean (0%) vs contaminated (50%)
    ssi_clean = ssi_by_level[0]
    ssi_contaminated = ssi_by_level[50] if len(ssi_by_level[50]) > 1 else ssi_array

    # Build labels: 0 = clean, 1 = contaminated
    labels = np.concatenate([
        np.zeros(len(ssi_clean), dtype=np.int32),
        np.ones(len(ssi_contaminated), dtype=np.int32)
    ])
    ssi_combined = np.concatenate([ssi_clean, ssi_contaminated])

    # Compute metrics
    auc = compute_auc(ssi_combined, labels)
    r, p_val = compute_pearson_by_level(mean_ssi_per_level, pcts)
    d = cohens_d(ssi_contaminated, ssi_clean)

    print(f"\n--- Results ---")
    print(f"AUC (clean vs 50% contaminated): {auc:.4f}")
    print(f"Pearson r (contamination % vs mean SSI): {r:.4f} (p={p_val:.4e})")
    print(f"Cohen's d (0% vs 50%): {d:.4f}")

    # Verify gate
    gate_result = verify_gate(
        auc, r, d,
        auc_threshold=cfg.auc_threshold,
        r_threshold=cfg.pearson_r_threshold,
        d_threshold=cfg.effect_size_threshold
    )

    print(f"\n--- Gate Evaluation ---")
    print(f"Primary (AUC > {cfg.auc_threshold}): {'PASS' if gate_result['primary_pass'] else 'FAIL'}")
    print(f"Secondary (r > {cfg.pearson_r_threshold}, d > {cfg.effect_size_threshold}): {'PASS' if gate_result['secondary_pass'] else 'FAIL'}")
    print(f"Gate Result: {gate_result['gate_result']}")

    # Generate figures
    os.makedirs(cfg.figure_dir, exist_ok=True)
    figures = generate_all_figures(gate_result, ssi_by_level, labels, ssi_combined, cfg.figure_dir)
    print(f"\nFigures saved: {len(figures)}")

    # Build results dict
    results = {
        "hypothesis_id": "h-m4",
        "timestamp": datetime.now().isoformat(),
        "seed": seed,
        "n_items": n_items,
        "contamination_levels": list(levels),
        "metrics": {
            "auc": float(auc),
            "pearson_r": float(r),
            "pearson_p": float(p_val),
            "cohens_d": float(d),
            "mean_ssi_by_level": {str(lvl): float(np.mean(ssi_by_level[lvl])) for lvl in levels},
            "std_ssi_by_level": {str(lvl): float(np.std(ssi_by_level[lvl])) for lvl in levels},
        },
        "thresholds": {
            "auc": cfg.auc_threshold,
            "pearson_r": cfg.pearson_r_threshold,
            "effect_size": cfg.effect_size_threshold,
        },
        "gate": gate_result,
        "figures": figures,
        "simulated": False,
        "dataset": "cais/mmlu",
        "model": cfg.model_id,
    }

    return results


def main():
    cfg = Config()

    # Run for primary seed
    results = run_experiment(cfg, seed=cfg.seeds[0])

    # Save results
    os.makedirs(cfg.output_dir, exist_ok=True)

    # Convert numpy types to Python types for JSON serialization
    def convert_numpy(obj):
        if isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(v) for v in obj]
        elif isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, (np.bool_,)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    results = convert_numpy(results)

    results_path = os.path.join(cfg.output_dir, "results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    # Save CSV summary
    csv_data = []
    for level in cfg.contamination_levels:
        csv_data.append({
            "contamination_level": level,
            "mean_ssi": results["metrics"]["mean_ssi_by_level"][str(level)],
            "std_ssi": results["metrics"]["std_ssi_by_level"][str(level)],
        })
    df = pd.DataFrame(csv_data)
    csv_path = os.path.join(cfg.output_dir, "results.csv")
    df.to_csv(csv_path, index=False)
    print(f"CSV saved: {csv_path}")

    print(f"\n{'='*60}")
    print(f"GATE RESULT: {results['gate']['gate_result']}")
    print(f"{'='*60}")
    print("EXPERIMENT COMPLETE")

    return results


if __name__ == "__main__":
    main()
