import numpy as np


def compute_deltas(correctness: dict, contaminated_mask: np.ndarray,
                   clean_mask: np.ndarray) -> dict:
    """Compute per-model delta = acc_contaminated - acc_clean."""
    deltas = {}
    for model_id, correct in correctness.items():
        # Align masks to correctness array (skip fewshot offset)
        n = len(correct)
        contam = contaminated_mask[:n]
        clean = clean_mask[:n]

        if contam.sum() > 0 and clean.sum() > 0:
            acc_contam = correct[contam].mean()
            acc_clean = correct[clean].mean()
            deltas[model_id] = acc_contam - acc_clean
        else:
            deltas[model_id] = 0.0
    return deltas


def amplification_index(deltas: dict, treatment: str = "perplexity",
                        baseline: str = "random") -> float:
    """Compute AI = mean(delta_treatment) - mean(delta_baseline)."""
    treatment_deltas = [v for k, v in deltas.items() if treatment in k]
    baseline_deltas = [v for k, v in deltas.items() if baseline in k]

    if not treatment_deltas or not baseline_deltas:
        return 0.0

    return np.mean(treatment_deltas) - np.mean(baseline_deltas)


def bootstrap_ai_ci(perplexity_deltas: np.ndarray, random_deltas: np.ndarray,
                    n_bootstrap: int = 10000, confidence: float = 0.95) -> tuple:
    """Paired bootstrap CI for Amplification Index."""
    n = len(perplexity_deltas)
    ai_samples = []

    np.random.seed(42)
    for _ in range(n_bootstrap):
        idx = np.random.randint(0, n, size=n)
        ai = perplexity_deltas[idx].mean() - random_deltas[idx].mean()
        ai_samples.append(ai)

    alpha = (1 - confidence) / 2
    ci_lower = np.percentile(ai_samples, alpha * 100)
    ci_upper = np.percentile(ai_samples, (1 - alpha) * 100)

    return ci_lower, ci_upper


def gate_check(ai: float, ci_lower: float) -> bool:
    """Gate: AI > 0 AND ci_lower > 0."""
    return ai > 0 and ci_lower > 0
