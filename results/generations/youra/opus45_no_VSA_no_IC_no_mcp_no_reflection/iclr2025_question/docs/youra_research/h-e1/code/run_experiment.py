#!/usr/bin/env python3
# run_experiment.py - h-e1 EXISTENCE PoC: UQ methods hallucination detection
# Optimized: batch generation, reduced samples for tractable runtime
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

# Reduced sampling for tractable runtime (full 817 questions)
NUM_SAMPLES_FAST = 5  # was 10
SELFCHECK_K_FAST = 3  # was 5


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_ground_truth_label(question: dict, greedy_response: str) -> int:
    """Label: 1 if hallucination (wrong), 0 if correct."""
    correct_answer = question["choices"][question["correct_idx"]]
    if correct_answer.lower() in greedy_response.lower():
        return 0
    return 1


def token_entropy_fast(logits):
    """Compute entropy from final token logits."""
    if logits is None:
        return 0.0
    import torch.nn.functional as F
    probs = F.softmax(logits, dim=-1)
    log_probs = F.log_softmax(logits, dim=-1)
    return -torch.sum(probs * log_probs).item()


def p_true_fast(model, tokenizer, question: str, response: str) -> float:
    """P(True): 1 - P(Yes) for 'Is the answer correct?'."""
    import torch.nn.functional as F
    prompt = f"{question}\nAnswer: {response}\nIs the above answer correct? (Yes/No)"
    yes_id = tokenizer.encode("Yes", add_special_tokens=False)[0]
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits[0, -1]
    probs = F.softmax(logits, dim=-1)
    return 1 - probs[yes_id].item()


def semantic_entropy_fast(samples: list[str], nli_model, nli_tokenizer, device) -> float:
    """Cluster samples by NLI entailment, compute entropy."""
    import math
    if not samples or len(samples) < 2:
        return 0.0

    def entails(p, h):
        inputs = nli_tokenizer(p, h, return_tensors="pt", truncation=True, max_length=512).to(device)
        with torch.no_grad():
            logits = nli_model(**inputs).logits
        return logits.argmax(dim=-1).item() == 2  # entailment

    clusters = [[samples[0]]]
    for s in samples[1:]:
        placed = False
        for c in clusters:
            if entails(c[0], s) and entails(s, c[0]):
                c.append(s)
                placed = True
                break
        if not placed:
            clusters.append([s])

    probs = [len(c) / len(samples) for c in clusters]
    return -sum(p * math.log(p) for p in probs if p > 0)


def selfcheck_fast(response: str, samples: list[str], selfcheck_model) -> float:
    """SelfCheckGPT NLI score."""
    sentences = [s.strip() for s in response.split('.') if s.strip()]
    if not sentences or not samples:
        return 0.0
    scores = selfcheck_model.predict(sentences=sentences, sampled_passages=samples)
    return float(np.mean(scores)) if isinstance(scores, np.ndarray) else (sum(scores)/len(scores) if scores else 0.0)


def main():
    print("=" * 60)
    print("h-e1 EXISTENCE PoC: UQ Methods for Hallucination Detection")
    print("=" * 60)

    set_seed(SEED)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    # Load data (use subset for tractable PoC runtime)
    print("\n[1/6] Loading TruthfulQA mc1...")
    data = load_truthfulqa_mc1()
    # ponytail: sample 500 for PoC, full 817 when runtime budget allows
    SAMPLE_SIZE = min(500, len(data))
    random.shuffle(data)
    data = data[:SAMPLE_SIZE]
    print(f"  Loaded {len(data)} questions (sampled from 817)")

    # Load model
    print("\n[2/6] Loading Llama-3-8B-Instruct...")
    model, tokenizer = load_model_and_tokenizer()
    print(f"  Model loaded on {model.device}")

    # Load NLI model for semantic entropy
    print("\n[3/6] Loading NLI + SelfCheck models...")
    from transformers import AutoModelForSequenceClassification, AutoTokenizer as AT
    from selfcheckgpt.modeling_selfcheck import SelfCheckNLI

    nli_tokenizer = AT.from_pretrained("microsoft/deberta-v3-large")
    nli_model = AutoModelForSequenceClassification.from_pretrained("microsoft/deberta-v3-large")
    nli_model.to("cuda").eval()
    selfcheck = SelfCheckNLI(device="cuda")
    print("  Models ready")

    # Run experiment
    print(f"\n[4/6] Scoring {len(data)} questions (fast mode: {NUM_SAMPLES_FAST} samples)...")
    all_scores = {"token_entropy": [], "semantic_entropy": [], "p_true": [], "selfcheck": []}
    y_true = []
    results_rows = []

    for i, q in enumerate(tqdm(data, desc="Processing")):
        prompt = f"Question: {q['question']}\nAnswer:"

        # Greedy generation
        greedy_response, greedy_logits = generate_greedy(model, tokenizer, prompt)

        # Sample responses (reduced)
        sampled = generate_samples(model, tokenizer, prompt, n=NUM_SAMPLES_FAST, temperature=0.7)

        # Scores
        te = token_entropy_fast(greedy_logits)
        se = semantic_entropy_fast(sampled, nli_model, nli_tokenizer, "cuda")
        pt = p_true_fast(model, tokenizer, q["question"], greedy_response)
        sc = selfcheck_fast(greedy_response, sampled[:SELFCHECK_K_FAST], selfcheck)

        label = get_ground_truth_label(q, greedy_response)
        y_true.append(label)

        all_scores["token_entropy"].append(te)
        all_scores["semantic_entropy"].append(se)
        all_scores["p_true"].append(pt)
        all_scores["selfcheck"].append(sc)

        results_rows.append({
            "idx": i, "question": q["question"][:100], "category": q["category"],
            "label": label, "token_entropy": te, "semantic_entropy": se,
            "p_true": pt, "selfcheck": sc
        })

        if (i + 1) % 50 == 0:
            print(f"  Checkpoint: {i+1}/{len(data)}")

    # Metrics
    print("\n[5/6] Computing metrics...")
    metrics = compute_metrics(y_true, all_scores)
    for method, m in metrics.items():
        print(f"  {method}: AUROC={m['auroc']:.4f}, AUPRC={m['auprc']:.4f}")

    gate_passed, best_method = apply_gate(metrics)
    print(f"\n  Gate: {'PASSED' if gate_passed else 'FAILED'} (threshold={AUROC_THRESHOLD})")
    print(f"  Best: {best_method} (AUROC={metrics[best_method]['auroc']:.4f})")

    # Visualize
    print("\n[6/6] Generating visualizations...")
    plot_gate_comparison(metrics, out_path=os.path.join(FIGURES_DIR, "gate_comparison.png"))
    plot_roc_curves(y_true, all_scores, out_path=os.path.join(FIGURES_DIR, "roc_curves.png"))
    plot_score_distributions(y_true, all_scores, out_dir=FIGURES_DIR)

    # Save
    with open(os.path.join(RESULTS_DIR, "scores.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results_rows[0].keys())
        writer.writeheader()
        writer.writerows(results_rows)

    with open(os.path.join(RESULTS_DIR, "metrics.json"), "w") as f:
        json.dump({
            "metrics": metrics, "gate_passed": gate_passed, "best_method": best_method,
            "total_questions": len(data), "hallucination_rate": sum(y_true)/len(y_true),
            "num_samples": NUM_SAMPLES_FAST, "selfcheck_k": SELFCHECK_K_FAST
        }, f, indent=2)

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    return gate_passed


if __name__ == "__main__":
    main()
