"""Pipeline orchestration for h-m2 cross-model probe transfer experiment."""

import os
import sys
import json
import gc
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    MODELS, NLI_MODEL_ID, SEED, TRAIN_SPLIT, LAYER_FRACTION,
    RESULTS_DIR, FIGURES_DIR, CACHE_DIR,
    MEAN_GAP_SUCCESS_THRESHOLD, MAX_GAP_SUCCESS_THRESHOLD
)
from data import load_truthfulqa, split_train_val
from cache import HiddenStateCache
from extract import extract_for_model
from semantic_entropy import SemanticEntropyBaseline
from sep import SemanticEntropyProbe
from transfer import AffineAligner
from evaluate import build_transfer_matrix, compute_gap_stats, check_transfer_success
from visualize import plot_transfer_heatmap, plot_gap_bar


def main():
    print("=" * 60)
    print("H-M2: Cross-Model Probe Transfer Experiment")
    print("=" * 60)

    print("\n[1] Loading TruthfulQA dataset...")
    dataset = load_truthfulqa()
    train_data, val_data = split_train_val(dataset, TRAIN_SPLIT, SEED)
    print(f"Total: {len(dataset)} | Train: {len(train_data)} | Val: {len(val_data)}")

    train_questions = [train_data[i]["question"] for i in range(len(train_data))]
    val_questions = [val_data[i]["question"] for i in range(len(val_data))]

    model_keys = list(MODELS.keys())
    cache = HiddenStateCache(CACHE_DIR)

    hidden_train = {}
    hidden_val = {}

    print("\n[2] Computing SE labels from first model (shared for transfer test)...")
    se_baseline = SemanticEntropyBaseline(NLI_MODEL_ID)
    from models import ModelWrapper

    first_model = model_keys[0]
    cfg = MODELS[first_model]
    wrapper = ModelWrapper(cfg["id"])
    wrapper.load()

    print(f"  Computing SE scores using {first_model} ({len(train_questions)} train, {len(val_questions)} val)...")
    train_se = se_baseline.compute_se_scores(wrapper, train_questions)
    val_se = se_baseline.compute_se_scores(wrapper, val_questions)

    se_labels_train = np.array(se_baseline.binarize(train_se))
    se_labels_val = np.array(se_baseline.binarize(val_se))
    print(f"  Labels: train high-SE={se_labels_train.sum()}/{len(se_labels_train)}, val high-SE={se_labels_val.sum()}/{len(se_labels_val)}")

    wrapper.unload()
    del wrapper
    gc.collect()
    torch.cuda.empty_cache()

    print("\n[3] Extracting hidden states for all models...")
    for model_key in model_keys:
        hidden_train[model_key] = extract_for_model(model_key, train_questions, "train", cache)
        hidden_val[model_key] = extract_for_model(model_key, val_questions, "val", cache)

    print("\n[4] Training per-model SEP probes...")
    probes = {}
    for model_key in model_keys:
        cfg = MODELS[model_key]
        layer_idx = int(cfg["n_layers"] * LAYER_FRACTION)
        probe = SemanticEntropyProbe(layer_idx)
        probe.fit(hidden_train[model_key], se_labels_train)
        probes[model_key] = probe
        print(f"  {model_key}: probe trained (layer {layer_idx}, dim {hidden_train[model_key].shape[1]})")

    print("\n[5] Fitting affine aligners for all pairs...")
    aligners = {}
    for src in model_keys:
        for tgt in model_keys:
            if src != tgt:
                aligners[(src, tgt)] = AffineAligner()
                aligners[(src, tgt)].fit(hidden_train[src], hidden_train[tgt])
                print(f"  {tgt} -> {src}: aligner fitted")

    print("\n[6] Building 3x3 transfer matrix...")
    matrix, method_used = build_transfer_matrix(probes, hidden_val, se_labels_val, aligners)

    print("\nTransfer Matrix (AUROC):")
    print("             " + "  ".join(f"{k:>10}" for k in model_keys))
    for i, src in enumerate(model_keys):
        row = "  ".join(f"{matrix[i, j]:>10.3f}" for j in range(len(model_keys)))
        print(f"{src:>12} {row}")

    print("\n[7] Computing gap statistics...")
    gap_stats = compute_gap_stats(matrix, model_keys)
    print(f"Mean gap: {gap_stats['mean_gap']:.4f}")
    print(f"Max gap: {gap_stats['max_gap']:.4f}")
    print("Per-pair gaps:")
    for pair, gap in gap_stats["per_pair_gaps"].items():
        print(f"  {pair}: {gap:.4f}")

    print("\n[8] Checking success criteria...")
    result = check_transfer_success(gap_stats, MEAN_GAP_SUCCESS_THRESHOLD, MAX_GAP_SUCCESS_THRESHOLD)
    print(f"PASSED: {result['passed']}")
    print(f"  Mean gap <= {result['mean_threshold']}: {result['mean_ok']}")
    print(f"  Max gap <= {result['max_threshold']}: {result['max_ok']}")

    print("\n[9] Saving results...")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    results = {
        "hypothesis": "h-m2",
        "statement": "Probes transfer across model families with AUROC gap <0.10",
        "gate_type": "SHOULD_WORK",
        "passed": result["passed"],
        "transfer_matrix": matrix.tolist(),
        "model_keys": model_keys,
        "gap_stats": gap_stats,
        "method_used": {f"{k[0]}->{k[1]}": v for k, v in method_used.items()},
        "thresholds": {
            "mean": MEAN_GAP_SUCCESS_THRESHOLD,
            "max": MAX_GAP_SUCCESS_THRESHOLD
        }
    }

    results_path = os.path.join(RESULTS_DIR, "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {results_path}")

    print("\n[10] Generating visualizations...")
    plot_transfer_heatmap(matrix, model_keys, os.path.join(FIGURES_DIR, "transfer_heatmap.png"))
    plot_gap_bar(gap_stats, os.path.join(FIGURES_DIR, "transfer_gap_bar.png"))

    print("\n" + "=" * 60)
    print("H-M2 EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Result: {'PASS' if result['passed'] else 'FAIL'}")
    print(f"Mean gap: {gap_stats['mean_gap']:.4f} (threshold: {MEAN_GAP_SUCCESS_THRESHOLD})")
    print(f"Max gap: {gap_stats['max_gap']:.4f} (threshold: {MAX_GAP_SUCCESS_THRESHOLD})")

    return result


if __name__ == "__main__":
    main()
