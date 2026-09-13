"""Pipeline orchestration for h-e1 experiment."""

import os
import sys
import json
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MODELS, NLI_MODEL_ID, SEED, TRAIN_SPLIT, LAYER_FRACTION, RESULTS_DIR, FIGURES_DIR
from data import load_truthfulqa, split_train_val
from models import ModelWrapper
from semantic_entropy import SemanticEntropyBaseline
from sep import SemanticEntropyProbe
from evaluate import compute_auroc, compute_gap, check_success
from visualize import plot_auroc_comparison


def run_pipeline_for_model(model_key: str, train_data, val_data, se_baseline) -> dict:
    """Full per-model run."""
    print(f"\n{'='*60}")
    print(f"Processing model: {model_key}")
    print(f"{'='*60}")

    cfg = MODELS[model_key]
    model = ModelWrapper(cfg["id"])
    print(f"Loading {cfg['id']}...")
    model.load()

    train_questions = [train_data[i]["question"] for i in range(len(train_data))]
    val_questions = [val_data[i]["question"] for i in range(len(val_data))]

    print(f"Computing SE scores for {len(train_questions)} train questions...")
    train_se = se_baseline.compute_se_scores(model, train_questions)
    print(f"Computing SE scores for {len(val_questions)} val questions...")
    val_se = se_baseline.compute_se_scores(model, val_questions)

    train_labels = se_baseline.binarize(train_se)
    val_labels = se_baseline.binarize(val_se)

    layer_idx = int(cfg["n_layers"] * LAYER_FRACTION)
    print(f"Using layer {layer_idx} (of {cfg['n_layers']}) for SEP")
    probe = SemanticEntropyProbe(layer_idx, token_position="last")

    print("Extracting train hidden states...")
    train_hidden_list = []
    for q in train_questions:
        inputs = model.tokenizer(q, return_tensors="pt").to(model.model.device)
        h = probe.extract_hidden_state(model, inputs["input_ids"], inputs["attention_mask"])
        train_hidden_list.append(h)
    train_hidden = np.vstack(train_hidden_list)

    print("Extracting val hidden states...")
    val_hidden_list = []
    for q in val_questions:
        inputs = model.tokenizer(q, return_tensors="pt").to(model.model.device)
        h = probe.extract_hidden_state(model, inputs["input_ids"], inputs["attention_mask"])
        val_hidden_list.append(h)
    val_hidden = np.vstack(val_hidden_list)

    print("Fitting SEP probe...")
    probe.fit(train_hidden, train_labels)
    sep_proba = probe.predict_proba(val_hidden)[:, 1]

    auroc_sep = compute_auroc(val_labels, sep_proba)
    auroc_se = compute_auroc(val_labels, val_se)
    gap = compute_gap(auroc_sep, auroc_se)

    print(f"Results for {model_key}:")
    print(f"  AUROC SEP: {auroc_sep:.4f}")
    print(f"  AUROC SE:  {auroc_se:.4f}")
    print(f"  Gap:       {gap:.4f}")

    del model.model
    torch.cuda.empty_cache()

    return {"auroc_sep": auroc_sep, "auroc_se": auroc_se, "gap": gap}


def main():
    print("Loading TruthfulQA dataset...")
    dataset = load_truthfulqa()
    print(f"Total samples: {len(dataset)}")

    # PoC smoke test: minimal validation run
    POC_SAMPLE_SIZE = 20
    if len(dataset) > POC_SAMPLE_SIZE:
        print(f"PoC mode: using {POC_SAMPLE_SIZE} samples (of {len(dataset)})")
        import random
        random.seed(SEED)
        indices = random.sample(range(len(dataset)), POC_SAMPLE_SIZE)
        dataset = dataset.select(indices)

    train_data, val_data = split_train_val(dataset, TRAIN_SPLIT, SEED)
    print(f"Train: {len(train_data)}, Val: {len(val_data)}")

    print(f"Loading NLI model: {NLI_MODEL_ID}")
    se_baseline = SemanticEntropyBaseline(NLI_MODEL_ID)

    results = {}
    POC_MODELS = ["llama3-8b"]  # Single model for PoC smoke test
    for model_key in POC_MODELS:
        results[model_key] = run_pipeline_for_model(model_key, train_data, val_data, se_baseline)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    results_path = os.path.join(RESULTS_DIR, "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    fig_path = os.path.join(FIGURES_DIR, "auroc_comparison.png")
    plot_auroc_comparison(results, fig_path)
    print(f"Figure saved to {fig_path}")

    gaps = {k: v["gap"] for k, v in results.items()}
    status = check_success(gaps)
    print(f"\n{'='*60}")
    print("EXPERIMENT SUMMARY")
    print(f"{'='*60}")
    print(f"Passed: {status['passed']}")
    print(f"Models within 0.05 gap: {status['n_within_05']}/{status['n_models']}")
    print(f"All within 0.10: {status['all_within_10']}")
    for model, gap in gaps.items():
        status_str = "PASS" if gap <= 0.05 else ("MARGINAL" if gap <= 0.10 else "FAIL")
        print(f"  {model}: gap={gap:.4f} [{status_str}]")

    return status


if __name__ == "__main__":
    main()
