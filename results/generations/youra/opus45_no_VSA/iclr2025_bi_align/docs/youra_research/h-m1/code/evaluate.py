"""Evaluation metrics for adversarial probing."""
import torch
import numpy as np
from sklearn.metrics import roc_auc_score, r2_score


def evaluate_bai_auroc(prober, h_test: torch.Tensor, bai_labels: np.ndarray, device: str = "cuda") -> float:
    """Compute AUROC for BAI classification."""
    prober.eval()
    h_test = h_test.to(device)

    with torch.no_grad():
        bai_logits, _ = prober(h_test)
        probs = torch.sigmoid(bai_logits).cpu().numpy()

    if len(np.unique(bai_labels)) < 2:
        return 0.5

    return roc_auc_score(bai_labels, probs)


def evaluate_reward_r2(probe, h_test: torch.Tensor, reward_labels: np.ndarray, device: str = "cuda") -> float:
    """Compute R² for reward prediction."""
    probe.eval()
    h_test = h_test.to(device)

    with torch.no_grad():
        if hasattr(probe, 'reward_probe'):
            logits = probe.reward_probe(h_test).squeeze(-1)
        else:
            logits = probe(h_test)
        preds = torch.sigmoid(logits).cpu().numpy()

    if np.std(reward_labels) < 1e-6:
        return 0.0

    return r2_score(reward_labels, preds)


def compute_r2_degradation(r2_baseline: float, r2_after_grl: float) -> float:
    """Compute R² degradation percentage."""
    return (r2_baseline - r2_after_grl) * 100


def run_evaluation(prober, baseline_probe, h_test, bai_labels, reward_labels, device="cuda"):
    """Full evaluation returning all metrics."""
    bai_auroc = evaluate_bai_auroc(prober, h_test, bai_labels, device)
    r2_baseline = evaluate_reward_r2(baseline_probe, h_test, reward_labels, device)
    r2_grl = evaluate_reward_r2(prober, h_test, reward_labels, device)
    degradation = compute_r2_degradation(r2_baseline, r2_grl)

    return {
        "bai_auroc": bai_auroc,
        "reward_r2_baseline": r2_baseline,
        "reward_r2_grl": r2_grl,
        "r2_degradation_pct": degradation,
        "pass_primary": bai_auroc >= 0.7,
        "pass_secondary": degradation < 2.0,
    }
