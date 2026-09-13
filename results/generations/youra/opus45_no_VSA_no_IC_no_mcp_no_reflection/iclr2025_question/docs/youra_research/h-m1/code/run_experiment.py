#!/usr/bin/env python3
# run_experiment.py - h-m1: Semantic Entropy via NLI clustering
import os
import sys
import json
import csv
import random
import numpy as np
import torch
from tqdm import tqdm

# Import h-m1 local modules first (before adding h-e1 to path)
import importlib.util
spec = importlib.util.spec_from_file_location("config_m1", os.path.join(os.path.dirname(__file__), "config.py"))
config_m1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_m1)

SEED = config_m1.SEED
RESULTS_DIR = config_m1.RESULTS_DIR
FIGURES_DIR = config_m1.FIGURES_DIR
AUROC_GATE = config_m1.AUROC_GATE
MODEL_ID = config_m1.MODEL_ID
DTYPE = config_m1.DTYPE
DEVICE_MAP = config_m1.DEVICE_MAP
NUM_SAMPLES = config_m1.NUM_SAMPLES
TEMPERATURE = config_m1.TEMPERATURE
MAX_NEW_TOKENS = config_m1.MAX_NEW_TOKENS

from nli_cluster import load_nli_model
from semantic_entropy import SemanticEntropy
from baselines import load_h_e1_scores, load_h_e1_metrics
from evaluate import compute_auroc, verify_mechanism, apply_gate
from visualize import plot_auroc_comparison, plot_cluster_histogram, plot_score_correlation, plot_roc_overlay

# Add h-e1 code to path for data loader
sys.path.insert(0, os.path.abspath("../../h-e1/code"))
from data import load_truthfulqa_mc1

# Use h-e1 model loader pattern
from transformers import AutoModelForCausalLM, AutoTokenizer

SAMPLE_SIZE = 200  # Full run: use 817. For time budget, use subset.


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_model_and_tokenizer(model_id=MODEL_ID):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    dtype = torch.bfloat16 if DTYPE == "bfloat16" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=dtype, device_map=DEVICE_MAP, trust_remote_code=True
    )
    model.eval()
    return model, tokenizer


def format_mc_prompt(q):
    """Format as MC question with lettered choices."""
    lines = [f"Question: {q['question']}", "Choices:"]
    for i, c in enumerate(q["choices"]):
        lines.append(f"  {chr(65+i)}) {c}")
    lines.append("Answer with just the letter (A, B, C, etc.):")
    return "\n".join(lines)


def parse_choice(response: str, num_choices: int) -> int:
    """Extract letter choice from response. Returns -1 if not found."""
    response = response.strip().upper()
    for c in response:
        if c in "ABCDEFGHIJ"[:num_choices]:
            return ord(c) - ord('A')
    return -1


def get_label_from_samples(samples: list[str], correct_idx: int, num_choices: int) -> int:
    """Majority vote on samples. 1 = hallucination (wrong), 0 = correct."""
    votes = []
    for s in samples:
        pred = parse_choice(s, num_choices)
        if pred != -1:
            votes.append(pred == correct_idx)
    if not votes:
        return 1  # No valid predictions = hallucination
    return 0 if sum(votes) > len(votes) / 2 else 1


def main():
    print("=" * 60)
    print("h-m1: Semantic Entropy via NLI Clustering")
    print("=" * 60)

    set_seed(SEED)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    print("\n[1/6] Loading data...")
    data = load_truthfulqa_mc1()
    random.shuffle(data)
    data = data[:SAMPLE_SIZE]
    print(f"  Using {len(data)} questions")

    print("\n[2/6] Loading models...")
    print("  Loading LLM...")
    llm_model, llm_tokenizer = load_model_and_tokenizer()
    print(f"  LLM on {llm_model.device}")
    print("  Loading NLI model...")
    nli_model, nli_tokenizer = load_nli_model()
    print("  NLI loaded")

    print(f"\n[3/6] Computing semantic entropy for {len(data)} questions...")
    se = SemanticEntropy(llm_model, llm_tokenizer, nli_model, nli_tokenizer,
                         num_samples=NUM_SAMPLES, threshold=0.7)

    results = []
    y_true = []
    semantic_scores = []

    for i, q in enumerate(tqdm(data, desc="Scoring")):
        prompt = format_mc_prompt(q)
        res = se.compute(prompt)

        # Determine label from majority vote on samples
        num_choices = len(q["choices"])
        label = get_label_from_samples(res["samples"], q["correct_idx"], num_choices)

        res.update({
            "idx": i,
            "question": q["question"][:100],
            "category": q.get("category", "unknown"),
            "correct_idx": q["correct_idx"],
            "label": label,
        })
        results.append(res)
        y_true.append(label)
        semantic_scores.append(res["semantic_entropy"])

    print("\n[4/6] Computing metrics...")
    # Load h-e1 baseline metrics (authoritative AUROC values)
    h_e1_metrics = load_h_e1_metrics()
    h_e1_scores = load_h_e1_scores()

    # Compute semantic entropy AUROC
    sem_auroc = compute_auroc(y_true, semantic_scores)
    print(f"  Semantic entropy AUROC: {sem_auroc:.4f}")

    # Mechanism verification
    mech = verify_mechanism(results)
    print(f"  Mechanism check: avg_clusters={mech['avg_clusters']:.2f}, entropy_std={mech['entropy_std']:.4f}, passed={mech['passed']}")

    # Build AUROC comparison dict
    aurocs = {"semantic_entropy": sem_auroc}
    if h_e1_metrics.get("metrics"):
        for method, m in h_e1_metrics["metrics"].items():
            aurocs[f"h-e1_{method}"] = m.get("auroc", 0.5)

    # Gate verdict
    gate = apply_gate(sem_auroc, AUROC_GATE)
    print(f"\n  Gate: {gate['gate']} - {gate['result']}")

    print("\n[5/6] Generating visualizations...")
    plot_auroc_comparison(aurocs, os.path.join(FIGURES_DIR, "auroc_comparison.png"))
    plot_cluster_histogram(results, os.path.join(FIGURES_DIR, "cluster_histogram.png"))

    # Use h-e1 scores for correlation if available and aligned
    if "choice_entropy" in h_e1_scores and len(h_e1_scores["choice_entropy"]) >= len(semantic_scores):
        plot_score_correlation(semantic_scores, h_e1_scores["choice_entropy"][:len(semantic_scores)],
                               "choice_entropy", os.path.join(FIGURES_DIR, "score_correlation.png"))

    # ROC overlay with semantic entropy only (h-e1 scores may not align with our sample)
    plot_roc_overlay(y_true, {"semantic_entropy": semantic_scores}, os.path.join(FIGURES_DIR, "roc_overlay.png"))

    print("\n[6/6] Writing results...")
    # Write scores CSV
    csv_path = os.path.join(RESULTS_DIR, "scores.csv")
    with open(csv_path, "w", newline="") as f:
        fieldnames = ["idx", "label", "semantic_entropy", "num_clusters", "question", "category"]
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        w.writerows(results)

    # Write cluster stats
    cluster_stats = {
        "total_questions": len(results),
        "avg_clusters": mech["avg_clusters"],
        "entropy_std": mech["entropy_std"],
        "cluster_size_variety": mech["cluster_size_variety"],
        "all_cluster_sizes": [r["cluster_sizes"] for r in results]
    }
    with open(os.path.join(RESULTS_DIR, "cluster_stats.json"), "w") as f:
        json.dump(cluster_stats, f, indent=2)

    # Write main metrics
    metrics = {
        "semantic_entropy_auroc": sem_auroc,
        "mechanism_verification": mech,
        "gate": gate,
        "baseline_comparison": aurocs,
        "sample_size": len(data),
        "hallucination_rate": sum(y_true) / len(y_true),
        "config": {
            "num_samples": NUM_SAMPLES,
            "temperature": TEMPERATURE,
            "threshold": 0.7
        }
    }
    with open(os.path.join(RESULTS_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"\nResults:")
    print(f"  Semantic entropy AUROC: {sem_auroc:.4f}")
    print(f"  Gate (>= {AUROC_GATE}): {gate['gate']}")
    print(f"  Mechanism verified: {mech['passed']}")
    print(f"  h-e1 max_prob baseline: {aurocs.get('h-e1_max_prob', 'N/A')}")
    print(f"  h-e1 choice_entropy baseline: {aurocs.get('h-e1_choice_entropy', 'N/A')}")

    return gate["gate"] == "PASSED", metrics


if __name__ == "__main__":
    passed, _ = main()
    sys.exit(0 if passed else 1)
