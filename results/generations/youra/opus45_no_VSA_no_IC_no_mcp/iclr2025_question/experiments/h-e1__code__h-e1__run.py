#!/usr/bin/env python3
import os
import json
import csv
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np

import config
from data import load_truthfulqa
from metrics import generate_greedy, compute_token_entropy, generate_n_samples, compute_consistency, label_response
from evaluate import compute_auroc, bootstrap_ci, plot_roc_curves

def main():
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.CACHE_DIR, exist_ok=True)

    print("Loading TruthfulQA...")
    data = load_truthfulqa()
    print(f"Loaded {len(data)} questions")

    print(f"Loading model {config.MODEL_ID}...")
    tokenizer = AutoTokenizer.from_pretrained(config.MODEL_ID, token=os.environ.get("HF_TOKEN"))
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        config.MODEL_ID,
        torch_dtype=torch.float16,
        device_map="auto",
        token=os.environ.get("HF_TOKEN"),
    )
    model.eval()

    print(f"Loading encoder {config.EMBED_MODEL_ID}...")
    encoder = SentenceTransformer(config.EMBED_MODEL_ID)

    results = []
    for item in tqdm(data, desc="Processing"):
        question = item["question"]
        response_text, logits = generate_greedy(model, tokenizer, question)
        entropy = compute_token_entropy(logits)
        samples = generate_n_samples(model, tokenizer, question, config.N_SAMPLES, config.TEMPERATURE)
        consistency = compute_consistency(samples, encoder)
        label = label_response(response_text, item["best_answer"], item["incorrect_answers"])
        results.append({
            "question_id": item["question_id"],
            "entropy": entropy,
            "consistency": consistency,
            "label": label,
        })

    scores_path = os.path.join(config.OUTPUT_DIR, "scores.csv")
    with open(scores_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["question_id", "entropy", "consistency", "label"])
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved scores to {scores_path}")

    labels = np.array([r["label"] for r in results])
    entropy_scores = np.array([r["entropy"] for r in results])
    consistency_scores = np.array([r["consistency"] for r in results])

    entropy_auroc = compute_auroc(labels, entropy_scores)
    consistency_auroc = compute_auroc(labels, -consistency_scores)
    entropy_ci = bootstrap_ci(labels, entropy_scores, config.N_BOOTSTRAP, config.SEED)
    consistency_ci = bootstrap_ci(labels, -consistency_scores, config.N_BOOTSTRAP, config.SEED)

    metrics = {
        "entropy_auroc": entropy_auroc,
        "entropy_ci_lower": entropy_ci[0],
        "entropy_ci_upper": entropy_ci[1],
        "consistency_auroc": consistency_auroc,
        "consistency_ci_lower": consistency_ci[0],
        "consistency_ci_upper": consistency_ci[1],
        "n_samples": len(results),
        "n_correct": int((labels == 0).sum()),
        "n_hallucinated": int((labels == 1).sum()),
    }

    metrics_path = os.path.join(config.OUTPUT_DIR, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {metrics_path}")
    print(f"Entropy AUROC: {entropy_auroc:.4f} [{entropy_ci[0]:.4f}, {entropy_ci[1]:.4f}]")
    print(f"Consistency AUROC: {consistency_auroc:.4f} [{consistency_ci[0]:.4f}, {consistency_ci[1]:.4f}]")

    roc_path = os.path.join(config.OUTPUT_DIR, "roc_curves.png")
    plot_roc_curves(labels, entropy_scores, consistency_scores, roc_path)
    print(f"Saved ROC curves to {roc_path}")

    passed = entropy_auroc > 0.55 and consistency_auroc > 0.55 and entropy_ci[0] > 0.50 and consistency_ci[0] > 0.50
    print(f"\nGate Result: {'PASS' if passed else 'FAIL'}")
    return passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
