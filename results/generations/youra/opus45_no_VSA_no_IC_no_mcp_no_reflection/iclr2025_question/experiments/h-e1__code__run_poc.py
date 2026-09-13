#!/usr/bin/env python3
# run_poc.py - h-e1 Minimal PoC: 30 samples, 2 UQ methods (fastest validation)
# ponytail: smallest test proving methodology works. Skip SelfCheck (slow NLI model).
import os
import json
import csv
import random
import numpy as np
import torch
from tqdm import tqdm

from config import SEED, RESULTS_DIR, FIGURES_DIR, AUROC_THRESHOLD
from data import load_truthfulqa_mc1
from model import load_model_and_tokenizer, generate_greedy

SAMPLE_SIZE = 30

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def get_label(q, resp):
    """1=hallucination, 0=correct"""
    correct = q["choices"][q["correct_idx"]]
    return 0 if correct.lower() in resp.lower() else 1

def token_entropy(logits):
    if logits is None:
        return 0.0
    import torch.nn.functional as F
    p = F.softmax(logits, dim=-1)
    return -torch.sum(p * F.log_softmax(logits, dim=-1)).item()

def p_true(model, tok, q, resp):
    import torch.nn.functional as F
    prompt = f"{q}\nAnswer: {resp}\nIs the above answer correct? (Yes/No)"
    yes_id = tok.encode("Yes", add_special_tokens=False)[0]
    inputs = tok(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model(**inputs)
    p = F.softmax(out.logits[0, -1], dim=-1)
    return 1 - p[yes_id].item()

def compute_auroc(y_true, scores):
    from sklearn.metrics import roc_auc_score
    if len(set(y_true)) < 2:
        return 0.5
    return roc_auc_score(y_true, scores)

def main():
    print("=" * 60)
    print("h-e1 PoC: 2 UQ Methods on 30 TruthfulQA samples")
    print("=" * 60)

    set_seed(SEED)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    print("\n[1/4] Loading data...")
    data = load_truthfulqa_mc1()
    random.shuffle(data)
    data = data[:SAMPLE_SIZE]
    print(f"  Sampled {len(data)} questions")

    print("\n[2/4] Loading model...")
    model, tok = load_model_and_tokenizer()
    print(f"  Model on {model.device}")

    print(f"\n[3/4] Scoring {len(data)} questions...")
    all_scores = {"token_entropy": [], "p_true": []}
    y_true = []
    rows = []

    for i, q in enumerate(tqdm(data, desc="Processing")):
        prompt = f"Question: {q['question']}\nAnswer:"
        greedy, logits = generate_greedy(model, tok, prompt)

        te = token_entropy(logits)
        pt = p_true(model, tok, q["question"], greedy)

        label = get_label(q, greedy)
        y_true.append(label)
        all_scores["token_entropy"].append(te)
        all_scores["p_true"].append(pt)

        rows.append({"idx": i, "label": label, "token_entropy": te, "p_true": pt})

    print("\n[4/4] Metrics...")
    metrics = {}
    for method, scores in all_scores.items():
        auroc = compute_auroc(y_true, scores)
        metrics[method] = {"auroc": auroc}
        print(f"  {method}: AUROC={auroc:.4f}")

    best_method = max(metrics.keys(), key=lambda k: metrics[k]["auroc"])
    best_auroc = metrics[best_method]["auroc"]
    passed = best_auroc > AUROC_THRESHOLD

    print(f"\n  Gate: {'PASSED' if passed else 'FAILED'} (best={best_method}, AUROC={best_auroc:.4f}, threshold={AUROC_THRESHOLD})")

    with open(os.path.join(RESULTS_DIR, "scores.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    results = {
        "metrics": metrics,
        "gate_passed": passed,
        "best_method": best_method,
        "sample_size": SAMPLE_SIZE,
        "hallucination_rate": sum(y_true)/len(y_true) if y_true else 0,
        "threshold": AUROC_THRESHOLD
    }
    with open(os.path.join(RESULTS_DIR, "metrics.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    return passed, results

if __name__ == "__main__":
    passed, _ = main()
    exit(0 if passed else 1)
