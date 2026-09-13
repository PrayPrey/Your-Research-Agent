#!/usr/bin/env python3
# run_experiment_fast.py - h-e1 PoC: Fast version (3 UQ methods, 200 samples)
# ponytail: skip semantic_entropy for tractable PoC; token_entropy + p_true + selfcheck sufficient for AUROC>0.55 gate
import os
import json
import csv
import random
import numpy as np
import torch
from tqdm import tqdm

from config import SEED, RESULTS_DIR, FIGURES_DIR, AUROC_THRESHOLD
from data import load_truthfulqa_mc1
from model import load_model_and_tokenizer, generate_greedy, generate_samples
from evaluate import compute_metrics, apply_gate
from visualize import plot_gate_comparison, plot_roc_curves, plot_score_distributions

SAMPLE_SIZE = 200
NUM_SAMPLES = 3
SELFCHECK_K = 3


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


def selfcheck(resp, samples, sc_model):
    sents = [s.strip() for s in resp.split('.') if s.strip()]
    if not sents or not samples:
        return 0.0
    scores = sc_model.predict(sentences=sents, sampled_passages=samples)
    return float(np.mean(scores)) if isinstance(scores, np.ndarray) else 0.0


def main():
    print("=" * 60)
    print("h-e1 PoC (Fast): 3 UQ Methods on 200 TruthfulQA samples")
    print("=" * 60)

    set_seed(SEED)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    print("\n[1/5] Loading data...")
    data = load_truthfulqa_mc1()
    random.shuffle(data)
    data = data[:SAMPLE_SIZE]
    print(f"  Sampled {len(data)} questions")

    print("\n[2/5] Loading model...")
    model, tok = load_model_and_tokenizer()
    print(f"  Model on {model.device}")

    print("\n[3/5] Loading SelfCheck...")
    from selfcheckgpt.modeling_selfcheck import SelfCheckNLI
    sc = SelfCheckNLI(device="cuda")

    print(f"\n[4/5] Scoring {len(data)} questions...")
    all_scores = {"token_entropy": [], "p_true": [], "selfcheck": []}
    y_true = []
    rows = []

    for i, q in enumerate(tqdm(data, desc="Processing")):
        prompt = f"Question: {q['question']}\nAnswer:"
        greedy, logits = generate_greedy(model, tok, prompt)
        samples = generate_samples(model, tok, prompt, n=NUM_SAMPLES, temperature=0.7)

        te = token_entropy(logits)
        pt = p_true(model, tok, q["question"], greedy)
        sc_score = selfcheck(greedy, samples[:SELFCHECK_K], sc)

        label = get_label(q, greedy)
        y_true.append(label)
        all_scores["token_entropy"].append(te)
        all_scores["p_true"].append(pt)
        all_scores["selfcheck"].append(sc_score)

        rows.append({"idx": i, "label": label, "token_entropy": te, "p_true": pt, "selfcheck": sc_score})

    print("\n[5/5] Metrics...")
    metrics = compute_metrics(y_true, all_scores)
    for m, v in metrics.items():
        print(f"  {m}: AUROC={v['auroc']:.4f}")

    passed, best = apply_gate(metrics)
    print(f"\n  Gate: {'PASSED' if passed else 'FAILED'} (best={best}, AUROC={metrics[best]['auroc']:.4f})")

    plot_gate_comparison(metrics, out_path=os.path.join(FIGURES_DIR, "gate_comparison.png"))
    plot_roc_curves(y_true, all_scores, out_path=os.path.join(FIGURES_DIR, "roc_curves.png"))
    plot_score_distributions(y_true, all_scores, out_dir=FIGURES_DIR)

    with open(os.path.join(RESULTS_DIR, "scores.csv"), "w", newline="") as f:
        csv.DictWriter(f, fieldnames=rows[0].keys()).writeheader()
        csv.DictWriter(f, fieldnames=rows[0].keys()).writerows(rows)

    with open(os.path.join(RESULTS_DIR, "metrics.json"), "w") as f:
        json.dump({"metrics": metrics, "gate_passed": passed, "best_method": best,
                   "sample_size": SAMPLE_SIZE, "hallucination_rate": sum(y_true)/len(y_true)}, f, indent=2)

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    return passed


if __name__ == "__main__":
    main()
