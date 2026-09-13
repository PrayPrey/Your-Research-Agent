"""Main orchestration for h-m1 cross-dataset transfer experiment."""

import os
import sys
import random
import numpy as np
import torch
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    SEED, MODEL_ID, NLI_MODEL_ID, LAYER_IDX, ABLATION_LAYERS,
    RESULTS_DIR, FIGURES_DIR, TRAIN_N_SAMPLES
)
from models import ModelWrapper
from sep import SemanticEntropyProbe
from data import load_triviaqa, load_truthfulqa
from semantic_entropy import SemanticEntropyLabels
from evaluate import compute_auroc, check_gate, save_results
from visualize import (
    plot_gate_metric, plot_roc_curve, plot_layer_analysis,
    plot_calibration, plot_distribution_comparison
)


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def extract_all_hidden_states(probe: SemanticEntropyProbe, model: ModelWrapper, questions: list) -> np.ndarray:
    """Extract hidden states for all questions."""
    states = []
    for i, q in enumerate(tqdm(questions, desc="Extracting hidden states")):
        inputs = model.tokenizer(q, return_tensors="pt").to(model.model.device)
        h = probe.extract_hidden_state(model, inputs["input_ids"], inputs["attention_mask"])
        states.append(h[0])
    return np.vstack(states)


def per_layer_auroc(
    model: ModelWrapper,
    train_questions: list,
    eval_questions: list,
    train_se_binary: list,
    eval_correctness: list,
    candidate_layers: list = None
) -> dict:
    """Sweep AUROC across layers."""
    if candidate_layers is None:
        candidate_layers = ABLATION_LAYERS

    results = {}
    for layer in candidate_layers:
        print(f"  Layer {layer}...")
        probe_l = SemanticEntropyProbe(layer_idx=layer, token_position="last")
        train_h = extract_all_hidden_states(probe_l, model, train_questions)
        eval_h = extract_all_hidden_states(probe_l, model, eval_questions)
        probe_l.fit(train_h, train_se_binary)
        proba = probe_l.predict_proba(eval_h)[:, 1]
        auroc = compute_auroc(eval_correctness, proba)
        results[layer] = auroc
        print(f"    AUROC: {auroc:.4f}")
    return results


def main():
    print("=" * 60)
    print("h-m1: Cross-Dataset Transfer Experiment")
    print("=" * 60)

    set_seed(SEED)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    print("\n[1/7] Loading model...")
    model = ModelWrapper(MODEL_ID)
    model.load()

    print("\n[2/7] Loading datasets...")
    train_data = load_triviaqa(TRAIN_N_SAMPLES)
    eval_data = load_truthfulqa()
    train_questions = train_data["question"]
    eval_questions = eval_data["question"]
    eval_references = eval_data["best_answer"]
    print(f"  TriviaQA: {len(train_questions)} questions")
    print(f"  TruthfulQA: {len(eval_questions)} questions")

    print("\n[3/7] Computing SE labels...")
    se_labels = SemanticEntropyLabels(NLI_MODEL_ID)
    print("  Computing SE scores on TriviaQA (train)...")
    train_se = se_labels.compute_se_scores(model, train_questions)
    train_se_binary = se_labels.binarize(train_se)
    print(f"  SE binary distribution: {sum(train_se_binary)}/{len(train_se_binary)} high-SE")

    print("  Computing correctness labels on TruthfulQA (eval)...")
    eval_correctness = se_labels.correctness_labels(model, eval_questions, eval_references)
    print(f"  Correctness distribution: {sum(eval_correctness)}/{len(eval_correctness)} correct")

    print("\n[4/7] Extracting hidden states...")
    probe = SemanticEntropyProbe(LAYER_IDX, "last")
    train_hidden = extract_all_hidden_states(probe, model, train_questions)
    eval_hidden = extract_all_hidden_states(probe, model, eval_questions)
    print(f"  Train hidden shape: {train_hidden.shape}")
    print(f"  Eval hidden shape: {eval_hidden.shape}")

    print("\n[5/7] Training probe and evaluating...")
    probe.fit(train_hidden, train_se_binary)
    eval_proba = probe.predict_proba(eval_hidden)[:, 1]
    train_proba = probe.predict_proba(train_hidden)[:, 1]

    assert np.std(eval_proba) > 0.01, "Probe outputs are constant!"

    auroc = compute_auroc(eval_correctness, eval_proba)
    gate = check_gate(auroc)
    print(f"  AUROC: {auroc:.4f}")
    print(f"  Gate: {gate['status'].upper()}")

    print("\n[6/7] Layer ablation...")
    layer_aurocs = per_layer_auroc(
        model, train_questions, eval_questions,
        train_se_binary, eval_correctness
    )
    best_layer = max(layer_aurocs, key=layer_aurocs.get)
    print(f"  Best layer: {best_layer} (AUROC={layer_aurocs[best_layer]:.4f})")

    print("\n[7/7] Saving results and figures...")
    results = {
        "auroc": auroc,
        "gate": gate,
        "layer_idx": LAYER_IDX,
        "layer_ablation": {str(k): v for k, v in layer_aurocs.items()},
        "best_layer": best_layer,
        "best_layer_auroc": layer_aurocs[best_layer],
        "train_samples": len(train_questions),
        "eval_samples": len(eval_questions),
        "train_se_high_count": sum(train_se_binary),
        "eval_correct_count": sum(eval_correctness),
    }
    save_results(results)

    plot_gate_metric(auroc, 0.70)
    plot_roc_curve(eval_correctness, eval_proba)
    plot_layer_analysis(layer_aurocs)
    plot_calibration(eval_correctness, eval_proba)
    plot_distribution_comparison(train_proba, eval_proba)

    print("\n" + "=" * 60)
    print(f"FINAL RESULT: AUROC = {auroc:.4f}, Gate = {gate['status'].upper()}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
