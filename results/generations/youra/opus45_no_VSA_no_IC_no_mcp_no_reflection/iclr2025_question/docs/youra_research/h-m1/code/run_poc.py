#!/usr/bin/env python3
"""h-m1 PoC: Semantic Entropy via NLI - Fast validation run (50 samples)."""
import os
import sys
import json
import csv
import random
import numpy as np
import torch
from tqdm import tqdm

# Config
SEED = 42
NUM_SAMPLES = 5  # Reduced from 10 for speed
TEMPERATURE = 0.7
MAX_NEW_TOKENS = 64  # Reduced for speed
NLI_THRESHOLD = 0.7
AUROC_GATE = 0.70
SAMPLE_SIZE = 50  # PoC size

MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
NLI_MODEL_ID = "facebook/bart-large-mnli"

CODE_DIR = os.path.dirname(__file__)
RESULTS_DIR = os.path.join(CODE_DIR, "results")
FIGURES_DIR = os.path.join(CODE_DIR, "../figures")

# Add h-e1 to path
sys.path.insert(0, os.path.abspath(os.path.join(CODE_DIR, "../../h-e1/code")))

from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import roc_auc_score
import math


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_truthfulqa_mc1():
    ds = load_dataset("truthful_qa", "multiple_choice", split="validation",
                      cache_dir=os.path.join(CODE_DIR, "../../h-e1/code/.cache"))
    data = []
    for row in ds:
        mc1 = row["mc1_targets"]
        data.append({
            "question": row["question"],
            "choices": mc1["choices"],
            "correct_idx": mc1["labels"].index(1),
            "category": row.get("category", "unknown")
        })
    return data


def load_models():
    print("  Loading LLM...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, torch_dtype=torch.bfloat16, device_map="auto"
    )
    model.eval()

    print("  Loading NLI model...")
    nli_tokenizer = AutoTokenizer.from_pretrained(NLI_MODEL_ID)
    nli_model = AutoModelForSequenceClassification.from_pretrained(NLI_MODEL_ID)
    nli_model.to("cuda").eval()

    return model, tokenizer, nli_model, nli_tokenizer


def generate_samples(model, tokenizer, prompt, n=NUM_SAMPLES):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    samples = []
    with torch.no_grad():
        for _ in range(n):
            out = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=True,
                temperature=TEMPERATURE,
                pad_token_id=tokenizer.pad_token_id
            )
            text = tokenizer.decode(out[0, inputs.input_ids.shape[1]:], skip_special_tokens=True)
            samples.append(text)
    return samples


def entailment_prob(nli_model, nli_tokenizer, premise, hypothesis):
    inputs = nli_tokenizer(premise, hypothesis, return_tensors="pt", truncation=True, max_length=256).to("cuda")
    with torch.no_grad():
        logits = nli_model(**inputs).logits[0]
    probs = torch.softmax(logits, dim=-1)
    return probs[2].item()  # entailment class


def cluster_samples(nli_model, nli_tokenizer, samples, threshold=NLI_THRESHOLD):
    if not samples:
        return []
    clusters = [[samples[0]]]
    for s in samples[1:]:
        placed = False
        for c in clusters:
            p1 = entailment_prob(nli_model, nli_tokenizer, c[0], s)
            p2 = entailment_prob(nli_model, nli_tokenizer, s, c[0])
            if min(p1, p2) > threshold:
                c.append(s)
                placed = True
                break
        if not placed:
            clusters.append([s])
    return clusters


def compute_semantic_entropy(clusters):
    sizes = [len(c) for c in clusters]
    total = sum(sizes)
    if total == 0:
        return 0.0
    probs = [s / total for s in sizes]
    return -sum(p * math.log(p) for p in probs if p > 0)


def format_prompt(q):
    lines = [f"Question: {q['question']}", "Choices:"]
    for i, c in enumerate(q["choices"]):
        lines.append(f"  {chr(65+i)}) {c}")
    lines.append("Answer with just the letter:")
    return "\n".join(lines)


def parse_choice(response, num_choices):
    response = response.strip().upper()
    for c in response:
        if c in "ABCDEFGHIJ"[:num_choices]:
            return ord(c) - ord('A')
    return -1


def get_label(samples, correct_idx, num_choices):
    votes = []
    for s in samples:
        pred = parse_choice(s, num_choices)
        if pred != -1:
            votes.append(pred == correct_idx)
    if not votes:
        return 1  # No valid = hallucination
    return 0 if sum(votes) > len(votes) / 2 else 1


def main():
    print("=" * 60)
    print("h-m1 PoC: Semantic Entropy via NLI Clustering")
    print("=" * 60)

    set_seed(SEED)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    print("\n[1/5] Loading data...")
    data = load_truthfulqa_mc1()
    random.shuffle(data)
    data = data[:SAMPLE_SIZE]
    print(f"  Using {len(data)} questions")

    print("\n[2/5] Loading models...")
    llm, tok, nli_model, nli_tok = load_models()
    print(f"  LLM on {llm.device}")

    print(f"\n[3/5] Computing semantic entropy for {len(data)} questions...")
    results = []
    y_true = []
    scores = []

    for q in tqdm(data, desc="Scoring"):
        prompt = format_prompt(q)
        samples = generate_samples(llm, tok, prompt)
        clusters = cluster_samples(nli_model, nli_tok, samples)
        entropy = compute_semantic_entropy(clusters)

        label = get_label(samples, q["correct_idx"], len(q["choices"]))

        results.append({
            "question": q["question"][:80],
            "category": q["category"],
            "semantic_entropy": entropy,
            "num_clusters": len(clusters),
            "cluster_sizes": [len(c) for c in clusters],
            "label": label
        })
        y_true.append(label)
        scores.append(entropy)

    print("\n[4/5] Computing metrics...")
    auroc = roc_auc_score(y_true, scores)
    avg_clusters = np.mean([r["num_clusters"] for r in results])
    entropy_std = np.std(scores)

    # Mechanism verification
    mech_passed = (avg_clusters < NUM_SAMPLES) and (entropy_std > 0)

    # Gate
    gate_passed = auroc >= AUROC_GATE

    print(f"  Semantic entropy AUROC: {auroc:.4f}")
    print(f"  Avg clusters: {avg_clusters:.2f} (mechanism: clustering active)")
    print(f"  Entropy std: {entropy_std:.4f} (mechanism: entropy varies)")
    print(f"  Mechanism verified: {mech_passed}")
    print(f"  Gate (>= {AUROC_GATE}): {'PASSED' if gate_passed else 'FAILED'}")

    # Load h-e1 baselines
    h_e1_metrics_path = os.path.join(CODE_DIR, "../../h-e1/code/outputs/metrics_mc.json")
    if os.path.exists(h_e1_metrics_path):
        with open(h_e1_metrics_path) as f:
            h_e1 = json.load(f)
        print(f"  h-e1 max_prob: {h_e1['metrics']['max_prob']['auroc']:.4f}")
        print(f"  h-e1 choice_entropy: {h_e1['metrics']['choice_entropy']['auroc']:.4f}")

    print("\n[5/5] Writing results...")

    # Write scores CSV
    with open(os.path.join(RESULTS_DIR, "scores.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["question", "category", "semantic_entropy", "num_clusters", "label"])
        w.writeheader()
        for r in results:
            w.writerow({k: r[k] for k in ["question", "category", "semantic_entropy", "num_clusters", "label"]})

    # Write metrics JSON
    metrics = {
        "semantic_entropy_auroc": float(auroc),
        "mechanism_verification": {
            "avg_clusters": float(avg_clusters),
            "entropy_std": float(entropy_std),
            "passed": bool(mech_passed)
        },
        "gate": {
            "gate": "PASSED" if gate_passed else "FAILED",
            "threshold": AUROC_GATE,
            "result": f"Semantic entropy AUROC={auroc:.4f} {'>' if gate_passed else '<'} {AUROC_GATE}"
        },
        "sample_size": len(data),
        "hallucination_rate": float(sum(y_true) / len(y_true)),
        "config": {
            "num_samples": NUM_SAMPLES,
            "temperature": TEMPERATURE,
            "nli_threshold": NLI_THRESHOLD
        }
    }
    with open(os.path.join(RESULTS_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "=" * 60)
    print("POC COMPLETE")
    print("=" * 60)
    print(f"\nSemantic entropy AUROC: {auroc:.4f}")
    print(f"Gate: {'PASSED' if gate_passed else 'FAILED'}")

    return gate_passed, metrics


if __name__ == "__main__":
    passed, _ = main()
    sys.exit(0 if passed else 1)
