"""Evaluation suite for H-E1"""

import torch
import evaluate
from scipy.stats import spearmanr

from config import BENCHMARKS, GATE_THRESHOLDS


def evaluate_benchmark(model, tokenizer, dataset, metric_name, max_samples=500):
    """Evaluate model on a benchmark."""
    model.eval()
    device = next(model.parameters()).device

    predictions = []
    references = []

    samples = min(len(dataset), max_samples)

    with torch.no_grad():
        for i in range(samples):
            sample = dataset[i]

            if "question" in sample:
                text = sample["question"]
            elif "text" in sample:
                text = sample["text"]
            else:
                text = str(sample[list(sample.keys())[0]])

            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
            inputs = {k: v.to(device) for k, v in inputs.items()}

            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                pad_token_id=tokenizer.pad_token_id,
                do_sample=False,
            )

            pred = tokenizer.decode(outputs[0], skip_special_tokens=True)
            predictions.append(pred)

            if "answer" in sample:
                ref = sample["answer"]
            elif "label" in sample:
                ref = str(sample["label"])
            else:
                ref = ""
            references.append(ref)

    if metric_name == "exact_match":
        metric = evaluate.load("exact_match")
        score = metric.compute(predictions=predictions, references=references)
        return score.get("exact_match", 0.0)
    elif metric_name == "f1":
        correct = sum(1 for p, r in zip(predictions, references) if r.lower() in p.lower())
        return correct / len(predictions) if predictions else 0.0
    elif metric_name == "accuracy":
        correct = sum(1 for p, r in zip(predictions, references) if p.strip() == r.strip())
        return correct / len(predictions) if predictions else 0.0

    return 0.0


def compute_deltas(transformer_scores: dict, mamba_scores: dict) -> dict:
    """Compute accuracy deltas (Mamba - Transformer)."""
    deltas = {}
    for key in transformer_scores:
        if key in mamba_scores:
            deltas[key] = mamba_scores[key] - transformer_scores[key]
    return deltas


def get_densities() -> dict:
    """Get retrieval densities from config."""
    return {name: cfg["density"] for name, cfg in BENCHMARKS.items()}


def spearman_correlation(deltas: dict, densities: dict) -> float:
    """Compute Spearman correlation between deltas and densities."""
    common_keys = set(deltas.keys()) & set(densities.keys())
    if len(common_keys) < 3:
        return 0.0

    delta_vals = [deltas[k] for k in sorted(common_keys)]
    density_vals = [densities[k] for k in sorted(common_keys)]

    corr, _ = spearmanr(delta_vals, density_vals)
    return corr if not torch.isnan(torch.tensor(corr)) else 0.0


def check_gate_conditions(deltas: dict, correlation: float) -> dict:
    """Check MUST_WORK gate conditions."""
    gsm8k_pass = deltas.get("gsm8k", -1) >= GATE_THRESHOLDS["gsm8k_delta_min"]
    nq_pass = deltas.get("nq", 0) <= GATE_THRESHOLDS["nq_delta_max"]
    correlation_pass = correlation > GATE_THRESHOLDS["spearman_min"]

    overall_pass = gsm8k_pass and nq_pass and correlation_pass

    return {
        "gsm8k_pass": gsm8k_pass,
        "nq_pass": nq_pass,
        "correlation_pass": correlation_pass,
        "overall_pass": overall_pass,
        "gate_verdict": "PASS" if overall_pass else "FAIL",
    }
