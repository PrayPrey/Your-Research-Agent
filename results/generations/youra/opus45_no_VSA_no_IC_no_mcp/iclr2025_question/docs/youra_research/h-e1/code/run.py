"""Main pipeline: H-E1 EXISTENCE experiment."""

import json
import os
import sys
import csv
from pathlib import Path

import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from config import CONFIG
from data import load_truthfulqa
from metrics import (
    generate_greedy, compute_token_entropy,
    generate_n_samples, compute_consistency,
    label_response
)
from evaluate import compute_auroc, bootstrap_ci, plot_roc_curves


def main():
    # Setup output directory
    os.makedirs(CONFIG["OUTPUT_DIR"], exist_ok=True)

    print("Loading TruthfulQA...")
    data = load_truthfulqa()
    print(f"Loaded {len(data)} questions")

    print("Loading LLaMA-2-7B...")
    model = AutoModelForCausalLM.from_pretrained(
        CONFIG["MODEL_ID"],
        torch_dtype=torch.float16 if CONFIG["MODEL_DTYPE"] == "float16" else torch.float32,
        device_map=CONFIG["DEVICE_MAP"],
    )
    tokenizer = AutoTokenizer.from_pretrained(CONFIG["MODEL_ID"])
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    print("Model loaded")

    print("Loading embedding model...")
    encoder = SentenceTransformer(CONFIG["EMBED_MODEL_ID"])
    print("Encoder loaded")

    # Run pipeline
    results = []
    for item in tqdm(data, desc="Processing"):
        qid = item["question_id"]
        question = item["question"]

        # Greedy generation for entropy
        response, logits = generate_greedy(model, tokenizer, question)
        entropy = compute_token_entropy(logits)

        # N-sample generation for consistency
        samples = generate_n_samples(
            model, tokenizer, question,
            n=CONFIG["N_SAMPLES"],
            temperature=CONFIG["TEMPERATURE"]
        )
        consistency = compute_consistency(samples, encoder)

        # Label
        label = label_response(
            response,
            item["best_answer"],
            item["incorrect_answers"]
        )

        results.append({
            "question_id": qid,
            "entropy": entropy,
            "consistency": consistency,
            "label": label,
        })

    # Save scores
    with open(CONFIG["SCORES_CSV"], "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["question_id", "entropy", "consistency", "label"])
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved scores to {CONFIG['SCORES_CSV']}")

    # Compute metrics
    labels = np.array([r["label"] for r in results])
    entropy_scores = np.array([r["entropy"] for r in results])
    consistency_scores = np.array([r["consistency"] for r in results])

    entropy_auroc = compute_auroc(labels, entropy_scores)
    entropy_ci = bootstrap_ci(labels, entropy_scores)

    consistency_auroc = compute_auroc(labels, -consistency_scores)
    consistency_ci = bootstrap_ci(labels, -consistency_scores)

    metrics = {
        "n_samples": len(results),
        "n_hallucinated": int(labels.sum()),
        "n_correct": int((1 - labels).sum()),
        "entropy": {
            "auroc": entropy_auroc,
            "ci_lower": entropy_ci[0],
            "ci_upper": entropy_ci[1],
        },
        "consistency": {
            "auroc": consistency_auroc,
            "ci_lower": consistency_ci[0],
            "ci_upper": consistency_ci[1],
        },
        "success_criteria": {
            "entropy_auroc_gt_055": entropy_auroc > 0.55,
            "consistency_auroc_gt_055": consistency_auroc > 0.55,
            "entropy_ci_lower_gt_050": entropy_ci[0] > 0.50,
            "consistency_ci_lower_gt_050": consistency_ci[0] > 0.50,
        }
    }

    with open(CONFIG["METRICS_JSON"], "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {CONFIG['METRICS_JSON']}")

    # Plot ROC curves
    plot_roc_curves(labels, entropy_scores, consistency_scores, CONFIG["ROC_PLOT_PNG"])
    print(f"Saved ROC plot to {CONFIG['ROC_PLOT_PNG']}")

    # Print summary
    print("\n" + "="*50)
    print("H-E1 EXISTENCE Results")
    print("="*50)
    print(f"Samples: {len(results)} ({int(labels.sum())} hallucinated, {int((1-labels).sum())} correct)")
    print(f"Entropy AUROC: {entropy_auroc:.4f} (95% CI: [{entropy_ci[0]:.4f}, {entropy_ci[1]:.4f}])")
    print(f"Consistency AUROC: {consistency_auroc:.4f} (95% CI: [{consistency_ci[0]:.4f}, {consistency_ci[1]:.4f}])")
    print()

    # Gate evaluation
    gate_pass = (
        metrics["success_criteria"]["entropy_auroc_gt_055"] and
        metrics["success_criteria"]["consistency_auroc_gt_055"] and
        metrics["success_criteria"]["entropy_ci_lower_gt_050"] and
        metrics["success_criteria"]["consistency_ci_lower_gt_050"]
    )

    if gate_pass:
        print("GATE: PASS - Both methods predict hallucination above chance")
    else:
        print("GATE: FAIL - One or both methods did not meet threshold")
        if not metrics["success_criteria"]["entropy_auroc_gt_055"]:
            print(f"  - Entropy AUROC {entropy_auroc:.4f} <= 0.55")
        if not metrics["success_criteria"]["consistency_auroc_gt_055"]:
            print(f"  - Consistency AUROC {consistency_auroc:.4f} <= 0.55")

    return 0 if gate_pass else 1


if __name__ == "__main__":
    sys.exit(main())
