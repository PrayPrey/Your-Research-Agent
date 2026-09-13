import torch
import numpy as np


def eval_mmlu_accuracy(model, tokenizer, mmlu: list[dict], device=None) -> float:
    """Multiple-choice log-likelihood scoring on MMLU."""
    if device is None:
        device = next(model.parameters()).device

    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for sample in mmlu:
            question = sample["question"]
            choices = sample["choices"]
            answer_idx = sample["answer"]

            best_score = float("-inf")
            best_choice = -1

            for i, choice in enumerate(choices):
                text = f"Question: {question}\nAnswer: {choice}"
                enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
                input_ids = enc["input_ids"].to(device)

                outputs = model(input_ids=input_ids, labels=input_ids)
                log_prob = -outputs.loss.item() * input_ids.shape[1]

                if log_prob > best_score:
                    best_score = log_prob
                    best_choice = i

            if best_choice == answer_idx:
                correct += 1
            total += 1

    return correct / total if total > 0 else 0.0


def compute_degradation_ratio(baseline_acc: float, high_ccr_acc: float, random_acc: float) -> float:
    """Degradation ratio: high-CCR degradation / random degradation."""
    high_ccr_drop = baseline_acc - high_ccr_acc
    random_drop = baseline_acc - random_acc
    return high_ccr_drop / max(random_drop, 1e-6)


def bootstrap_degradation_ci(
    baseline_accs: np.ndarray,
    high_ccr_accs: np.ndarray,
    random_accs: np.ndarray,
    n_bootstrap: int = 1000
) -> tuple[float, float, float]:
    """Bootstrap 95% CI for degradation ratio."""
    rng = np.random.default_rng(42)
    n = len(baseline_accs)
    ratios = []

    for _ in range(n_bootstrap):
        idx = rng.choice(n, n, replace=True)
        baseline_mean = baseline_accs[idx].mean()
        high_ccr_mean = high_ccr_accs[idx].mean()
        random_mean = random_accs[idx].mean()
        ratio = compute_degradation_ratio(baseline_mean, high_ccr_mean, random_mean)
        ratios.append(ratio)

    ratios = np.array(ratios)
    mean_ratio = ratios.mean()
    ci_low = np.percentile(ratios, 2.5)
    ci_high = np.percentile(ratios, 97.5)
    return mean_ratio, ci_low, ci_high
