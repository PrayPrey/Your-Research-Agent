#!/usr/bin/env python3
# run_poc_mc.py - h-e1 PoC: Multiple-choice format (forces label variance)
# ponytail: MC format gives clean labels. Model picks A/B/C/D, we check against correct_idx.
import os
import json
import csv
import random
import numpy as np
import torch
from tqdm import tqdm

from config import SEED, RESULTS_DIR, FIGURES_DIR, AUROC_THRESHOLD
from data import load_truthfulqa_mc1
from model import load_model_and_tokenizer

SAMPLE_SIZE = 50

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def format_mc_prompt(q):
    """Format as MC question with lettered choices."""
    lines = [f"Question: {q['question']}", "Choices:"]
    for i, c in enumerate(q["choices"]):
        lines.append(f"  {chr(65+i)}) {c}")
    lines.append("Answer with just the letter (A, B, C, etc.):")
    return "\n".join(lines)

def parse_choice(response, num_choices):
    """Extract letter choice from response."""
    response = response.strip().upper()
    for c in response:
        if c in "ABCDEFGHIJ"[:num_choices]:
            return ord(c) - ord('A')
    return -1

def token_entropy_from_logits(logits):
    if logits is None:
        return 0.0
    import torch.nn.functional as F
    p = F.softmax(logits, dim=-1)
    log_p = F.log_softmax(logits, dim=-1)
    return -torch.sum(p * log_p).item()

def choice_entropy(model, tok, prompt, num_choices):
    """Entropy over the choice letters A/B/C/D at first token."""
    import torch.nn.functional as F
    inputs = tok(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model(**inputs)

    logits = out.logits[0, -1]  # last position
    choice_ids = [tok.encode(chr(65+i), add_special_tokens=False)[0] for i in range(num_choices)]
    choice_logits = logits[choice_ids]
    probs = F.softmax(choice_logits, dim=-1)
    log_probs = F.log_softmax(choice_logits, dim=-1)
    entropy = -torch.sum(probs * log_probs).item()
    return entropy, probs.float().cpu().numpy()

def main():
    print("=" * 60)
    print("h-e1 PoC (MC): Choice Entropy on 50 TruthfulQA samples")
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
    all_scores = {"choice_entropy": [], "max_prob": []}
    y_true = []
    rows = []

    for i, q in enumerate(tqdm(data, desc="Processing")):
        prompt = format_mc_prompt(q)
        num_choices = len(q["choices"])

        entropy, probs = choice_entropy(model, tok, prompt, num_choices)
        pred_idx = int(np.argmax(probs))
        correct_idx = q["correct_idx"]

        label = 0 if pred_idx == correct_idx else 1  # 1=hallucination
        max_prob = float(probs[pred_idx])

        y_true.append(label)
        all_scores["choice_entropy"].append(entropy)
        all_scores["max_prob"].append(1 - max_prob)  # higher = less confident = more hallucinatory

        rows.append({
            "idx": i, "label": label,
            "choice_entropy": entropy,
            "max_prob": max_prob,
            "pred": chr(65+pred_idx),
            "correct": chr(65+correct_idx)
        })

    print("\n[4/4] Metrics...")
    from sklearn.metrics import roc_auc_score

    metrics = {}
    for method, scores in all_scores.items():
        if len(set(y_true)) < 2:
            auroc = 0.5
        else:
            auroc = roc_auc_score(y_true, scores)
        metrics[method] = {"auroc": auroc}
        print(f"  {method}: AUROC={auroc:.4f}")

    n_correct = sum(1 for l in y_true if l == 0)
    n_wrong = sum(1 for l in y_true if l == 1)
    print(f"\n  Labels: {n_correct} correct, {n_wrong} hallucinations")

    best_method = max(metrics.keys(), key=lambda k: metrics[k]["auroc"])
    best_auroc = metrics[best_method]["auroc"]
    passed = best_auroc > AUROC_THRESHOLD

    print(f"  Gate: {'PASSED' if passed else 'FAILED'} (best={best_method}, AUROC={best_auroc:.4f}, threshold={AUROC_THRESHOLD})")

    with open(os.path.join(RESULTS_DIR, "scores_mc.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    results = {
        "metrics": metrics,
        "gate_passed": passed,
        "best_method": best_method,
        "sample_size": SAMPLE_SIZE,
        "correct_rate": n_correct / len(y_true),
        "hallucination_rate": n_wrong / len(y_true),
        "threshold": AUROC_THRESHOLD
    }
    with open(os.path.join(RESULTS_DIR, "metrics_mc.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    return passed, results

if __name__ == "__main__":
    passed, _ = main()
    exit(0 if passed else 1)
