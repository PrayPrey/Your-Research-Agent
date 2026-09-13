"""H-M4 Evaluation: AUROC, deltas, gate check."""
import re
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve


def normalize_text(text: str) -> str:
    """Normalize text for exact match."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def exact_match(pred_text: str, gold_answers: list) -> int:
    """Check if normalized pred matches any gold answer."""
    pred_norm = normalize_text(pred_text)
    for gold in gold_answers:
        if normalize_text(str(gold)) == pred_norm:
            return 1
        if normalize_text(str(gold)) in pred_norm or pred_norm in normalize_text(str(gold)):
            return 1
    return 0


def compute_labels(gen_outputs: list) -> np.ndarray:
    """Compute exact-match labels from live generation."""
    labels = []
    for out in gen_outputs:
        label = exact_match(out["text"], out["gold_answers"])
        labels.append(label)
    return np.array(labels)


def compute_auroc_all(probe_scores: np.ndarray, entropy_scores: np.ndarray,
                      nll_scores: np.ndarray, labels: np.ndarray) -> dict:
    """Compute AUROC for all methods."""
    return {
        "probe_auroc": roc_auc_score(labels, probe_scores),
        "entropy_auroc": roc_auc_score(labels, entropy_scores),
        "nll_auroc": roc_auc_score(labels, nll_scores)
    }


def compute_deltas(aurocs: dict) -> dict:
    """Compute deltas from probe to baselines."""
    return {
        "delta_entropy": aurocs["probe_auroc"] - aurocs["entropy_auroc"],
        "delta_nll": aurocs["probe_auroc"] - aurocs["nll_auroc"]
    }


def check_gate(deltas: dict, threshold: float = 0.05) -> dict:
    """Check if deltas meet gate threshold."""
    gate_entropy_pass = deltas["delta_entropy"] >= threshold
    gate_nll_pass = deltas["delta_nll"] >= threshold
    return {
        "gate_entropy_pass": gate_entropy_pass,
        "gate_nll_pass": gate_nll_pass,
        "gate_pass": gate_entropy_pass and gate_nll_pass
    }


def get_roc_curves(labels: np.ndarray, probe_scores: np.ndarray,
                   entropy_scores: np.ndarray, nll_scores: np.ndarray) -> dict:
    """Get ROC curve data for plotting."""
    curves = {}
    for name, scores in [("probe", probe_scores), ("entropy", entropy_scores), ("nll", nll_scores)]:
        fpr, tpr, _ = roc_curve(labels, scores)
        curves[name] = {"fpr": fpr, "tpr": tpr}
    return curves
