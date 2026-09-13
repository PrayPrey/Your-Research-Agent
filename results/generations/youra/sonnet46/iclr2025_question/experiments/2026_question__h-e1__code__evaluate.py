"""
Evaluation suite for H-E1 EXISTENCE PoC.
AUROC, DeLong test, Cohen's d, label audit, gate condition, visualization.
"""
import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import seaborn as sns
from sklearn.metrics import roc_auc_score, roc_curve

from config import ExperimentConfig

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Data container
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TaskResult:
    task_name: str
    auroc: float
    delong_pvalue: float
    cohen_d: float
    auroc_max: float          # structural ceiling from label_audit
    p_contradictory: float    # fraction of hallucinated examples with P(contra)>0.4
    score_inverted: bool      # whether P(contradiction) was inverted
    n_examples: int
    label_distribution: Dict[str, int]   # {"0": int, "1": int}
    mechanism_passed: bool    # whether verify_mechanism_activated passed
    mechanism_indicators: Dict[str, bool]


# ─────────────────────────────────────────────────────────────────────────────
# Statistical functions
# ─────────────────────────────────────────────────────────────────────────────

def compute_auroc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """Compute AUROC via sklearn."""
    return float(roc_auc_score(y_true, y_score))


def delong_test(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """
    fastDeLong test: AUROC vs 0.5 baseline. Returns two-tailed p-value.

    Reference: Sun & Xu (2014). "Fast Implementation of DeLong's Algorithm
    for Comparing the Areas Under Correlated Receiver Operating Characteristic
    Curves." IEEE Signal Process. Lett.

    Args:
        y_true: shape (N,) binary labels {0, 1}
        y_score: shape (N,) predicted scores

    Returns:
        p_value: float (two-tailed p-value vs H0: AUROC=0.5)
    """
    pos = y_score[y_true == 1]   # shape: (m,)
    neg = y_score[y_true == 0]   # shape: (n,)
    m, n = len(pos), len(neg)

    if m == 0 or n == 0:
        logger.warning("delong_test: empty positive or negative class")
        return 1.0

    # Placement matrix (m, n)
    matrix = (pos[:, None] > neg[None, :]).astype(float)
    matrix += 0.5 * (pos[:, None] == neg[None, :]).astype(float)

    V10 = matrix.mean(axis=1)   # shape: (m,) — structural component for positives
    V01 = matrix.mean(axis=0)   # shape: (n,) — structural component for negatives

    auroc = matrix.mean()

    S10 = np.var(V10, ddof=1) / m if m > 1 else 0.0
    S01 = np.var(V01, ddof=1) / n if n > 1 else 0.0
    var_auroc = S10 + S01

    if var_auroc <= 0:
        logger.warning("delong_test: zero variance; returning p=1.0")
        return 1.0

    z = (auroc - 0.5) / np.sqrt(var_auroc)
    p_value = 2.0 * scipy.stats.norm.sf(abs(z))  # two-tailed
    return float(p_value)


def cohen_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """
    Compute Cohen's d between two groups.

    Args:
        group1: scores for hallucinated examples (label=1)
        group2: scores for non-hallucinated examples (label=0)

    Returns:
        Cohen's d = (mean1 - mean2) / pooled_std
    """
    var1 = np.var(group1, ddof=1) if len(group1) > 1 else 0.0
    var2 = np.var(group2, ddof=1) if len(group2) > 1 else 0.0
    pooled_std = np.sqrt((var1 + var2) / 2)
    if pooled_std == 0:
        return 0.0
    return float((np.mean(group1) - np.mean(group2)) / pooled_std)


def check_inversion(
    y_score: np.ndarray, y_true: np.ndarray
) -> Tuple[np.ndarray, bool]:
    """
    If AUROC < 0.5, invert scores (1 - score).

    Returns:
        (adjusted_scores, was_inverted)
    """
    auroc_raw = roc_auc_score(y_true, y_score)
    if auroc_raw < 0.5:
        logger.warning(f"Score inverted: auroc_raw={auroc_raw:.3f}")
        return 1.0 - y_score, True
    return y_score, False


def verify_mechanism_activated(
    scores: np.ndarray,
    labels: np.ndarray,
    task_name: str,
) -> Tuple[bool, Dict[str, bool]]:
    """
    Check 4 NLI mechanism indicators.

    Indicators:
        shape_correct: scores.shape[1] == 3
        non_uniform: mean std across class axis > 0.05
        above_random: AUROC(P(contra), labels) > 0.50 (using col 0 as preliminary)
        label_verified: 0.0 < labels.mean() < 1.0

    Returns:
        (all_pass, indicators_dict)
    """
    p_contra = scores[:, 0]  # preliminary check with index 0

    indicators = {
        "shape_correct": scores.shape[1] == 3,
        "non_uniform": float(scores.std(axis=0).mean()) > 0.05,
        "above_random": float(roc_auc_score(labels, p_contra)) > 0.50,
        "label_verified": 0.0 < float(labels.mean()) < 1.0,
    }
    all_pass = all(indicators.values())
    failed = [k for k, v in indicators.items() if not v]
    if failed:
        logger.warning(f"[{task_name}] Mechanism check FAILED: {failed}")
    else:
        logger.info(f"[{task_name}] All mechanism checks passed.")
    return all_pass, indicators


def label_audit(
    premises: List[str],
    hypotheses: List[str],
    labels: np.ndarray,
    scores: np.ndarray,
    contradiction_idx: int,
    seed: int = 42,
    n: int = 200,
) -> Dict:
    """
    Stratified sample n hallucinated examples; compute structural ceiling AUROC_max.

    Args:
        premises, hypotheses: text inputs (not used directly but kept for API compatibility)
        labels: shape (N,) binary labels
        scores: shape (N, 3) softmax probabilities
        contradiction_idx: verified index of contradiction class
        seed: random seed for reproducibility
        n: sample size for audit

    Returns:
        dict with p_contradictory, auroc_max, category_counts, n_sampled
    """
    rng = np.random.default_rng(seed)
    hall_idx = np.where(labels == 1)[0]           # hallucinated example indices
    sample_n = min(n, len(hall_idx))

    if sample_n == 0:
        logger.warning("label_audit: no hallucinated examples found")
        return {"p_contradictory": 0.0, "auroc_max": 0.5, "category_counts": {"A": 0, "B": 0, "C": 0}, "n_sampled": 0}

    sampled_idx = rng.choice(hall_idx, size=sample_n, replace=False)
    p_contra_sampled = scores[sampled_idx, contradiction_idx]   # shape: (sample_n,)

    # Score-threshold categorization
    cat_A = int((p_contra_sampled > 0.4).sum())   # NLI-detectable contradiction
    cat_B = int((p_contra_sampled < 0.2).sum())   # Clearly non-contradicting
    cat_C = sample_n - cat_A - cat_B               # Middle ground

    p_contradictory = cat_A / sample_n
    auroc_max = p_contradictory + 0.5 * (1 - p_contradictory)

    logger.info(
        f"Label audit: n_sampled={sample_n}, "
        f"cat_A={cat_A}, cat_B={cat_B}, cat_C={cat_C}, "
        f"p_contradictory={p_contradictory:.3f}, auroc_max={auroc_max:.3f}"
    )
    return {
        "p_contradictory": float(p_contradictory),
        "auroc_max": float(auroc_max),
        "category_counts": {"A": cat_A, "B": cat_B, "C": cat_C},
        "n_sampled": sample_n,
    }


def evaluate_task(
    task_name: str,
    scores: np.ndarray,
    labels: np.ndarray,
    premises: List[str],
    hypotheses: List[str],
    contradiction_idx: int,
    config: ExperimentConfig,
) -> TaskResult:
    """
    Full per-task evaluation: AUROC, DeLong, Cohen's d, inversion, label audit.

    Args:
        task_name: 'dialogue', 'qa', or 'summarization'
        scores: shape (N, 3) NLI class probabilities
        labels: shape (N,) binary labels
        premises, hypotheses: text inputs
        contradiction_idx: verified contradiction class index
        config: ExperimentConfig

    Returns:
        TaskResult dataclass
    """
    logger.info(f"[{task_name}] Evaluating {len(labels)} examples...")

    p_contradiction = scores[:, contradiction_idx]   # shape: (N,)

    # Mechanism check
    mech_pass, mech_indicators = verify_mechanism_activated(scores, labels, task_name)

    # Inversion check (use raw p_contradiction first)
    p_final, score_inverted = check_inversion(p_contradiction, labels)

    # AUROC
    auroc = compute_auroc(labels, p_final)

    # DeLong test
    delong_pvalue = delong_test(labels, p_final)

    # Cohen's d
    hall_scores = p_final[labels == 1]
    non_hall_scores = p_final[labels == 0]
    d = cohen_d(hall_scores, non_hall_scores)

    # Label audit
    audit = label_audit(
        premises, hypotheses, labels, scores,
        contradiction_idx=contradiction_idx,
        seed=config.seed,
        n=config.label_audit_n,
    )

    label_dist = {
        "0": int((labels == 0).sum()),
        "1": int((labels == 1).sum()),
    }

    logger.info(
        f"[{task_name}] AUROC={auroc:.4f}, DeLong_p={delong_pvalue:.4e}, "
        f"Cohen_d={d:.3f}, inverted={score_inverted}, "
        f"auroc_max={audit['auroc_max']:.3f}"
    )

    return TaskResult(
        task_name=task_name,
        auroc=float(auroc),
        delong_pvalue=float(delong_pvalue),
        cohen_d=d,
        auroc_max=audit["auroc_max"],
        p_contradictory=audit["p_contradictory"],
        score_inverted=score_inverted,
        n_examples=int(len(labels)),
        label_distribution=label_dist,
        mechanism_passed=mech_pass,
        mechanism_indicators=mech_indicators,
    )


def check_gate_condition(
    results: List[TaskResult],
    config: ExperimentConfig,
) -> Tuple[bool, str]:
    """
    H-E1 MUST_WORK gate: AUROC > 0.55 AND DeLong p < 0.05 on >= 2/3 tasks.

    Returns:
        (gate_pass, message_string)
    """
    passing_tasks = [
        r for r in results
        if r.auroc > config.auroc_threshold and r.delong_pvalue < config.delong_alpha
    ]
    n_pass = len(passing_tasks)
    gate_pass = n_pass >= config.tasks_required_to_pass

    details = []
    for r in results:
        status = "✓ PASS" if (r.auroc > config.auroc_threshold and r.delong_pvalue < config.delong_alpha) else "✗ FAIL"
        details.append(
            f"{r.task_name}: AUROC={r.auroc:.4f} (thr={config.auroc_threshold}), "
            f"p={r.delong_pvalue:.4e} (alpha={config.delong_alpha}) [{status}]"
        )

    result_str = "\n  ".join(details)
    msg = (
        f"Gate {'PASS' if gate_pass else 'FAIL'}: "
        f"{n_pass}/{len(results)} tasks pass (required: {config.tasks_required_to_pass})\n  "
        + result_str
    )
    logger.info(msg)
    return gate_pass, msg


# ─────────────────────────────────────────────────────────────────────────────
# Visualization (Task A-5)
# ─────────────────────────────────────────────────────────────────────────────

def plot_gate_metrics(results: List[TaskResult], output_path: str) -> None:
    """Bar chart of AUROC per task with threshold line."""
    fig, ax = plt.subplots(figsize=(8, 5))
    task_names = [r.task_name for r in results]
    aurocs = [r.auroc for r in results]
    colors = ["green" if r.auroc > 0.55 else "red" for r in results]

    bars = ax.bar(task_names, aurocs, color=colors, alpha=0.75, edgecolor="black")
    ax.axhline(y=0.55, color="orange", linestyle="--", linewidth=2, label="Threshold (0.55)")
    ax.axhline(y=0.5, color="gray", linestyle=":", linewidth=1, label="Random baseline (0.5)")

    for bar, auroc in zip(bars, aurocs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{auroc:.3f}", ha="center", va="bottom", fontsize=10)

    ax.set_ylim(0, 1.0)
    ax.set_xlabel("Task", fontsize=12)
    ax.set_ylabel("AUROC", fontsize=12)
    ax.set_title("H-E1: AUROC per Task (MUST_WORK Gate)", fontsize=13)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"Saved gate_metrics figure: {output_path}")


def plot_roc_curves(
    task_arrays: List[Tuple[TaskResult, np.ndarray, np.ndarray]],
    output_path: str,
    contradiction_idx: int = 0,
) -> None:
    """3-subplot ROC curves with AUC annotation."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, (result, scores, labels) in zip(axes, task_arrays):
        fpr, tpr, _ = roc_curve(labels, scores[:, contradiction_idx])
        ax.plot(fpr, tpr, color="steelblue", lw=2, label=f"AUC={result.auroc:.3f}")
        ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="Random")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("FPR", fontsize=11)
        ax.set_ylabel("TPR", fontsize=11)
        ax.set_title(f"{result.task_name.capitalize()}", fontsize=12)
        ax.legend(fontsize=10)
    fig.suptitle("H-E1: ROC Curves per Task", fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"Saved roc_curves figure: {output_path}")


def plot_score_distributions(
    task_arrays: List[Tuple[TaskResult, np.ndarray, np.ndarray]],
    output_path: str,
    contradiction_idx: int = 0,
) -> None:
    """Violin/box P(contradiction) by label per task."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, (result, scores, labels) in zip(axes, task_arrays):
        p_contra = scores[:, contradiction_idx]
        data_by_label = {
            "Non-Hallu (0)": p_contra[labels == 0],
            "Hallu (1)": p_contra[labels == 1],
        }
        ax.violinplot(
            [data_by_label["Non-Hallu (0)"], data_by_label["Hallu (1)"]],
            positions=[0, 1], showmedians=True,
        )
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Non-Hallu", "Hallucinated"])
        ax.set_ylabel("P(contradiction)", fontsize=11)
        ax.set_title(f"{result.task_name.capitalize()}", fontsize=12)
    fig.suptitle("H-E1: P(contradiction) Distribution by Label", fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"Saved score_distributions figure: {output_path}")


def plot_structural_ceiling(results: List[TaskResult], output_path: str) -> None:
    """Actual AUROC vs AUROC_max (structural ceiling) per task."""
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(results))
    width = 0.35

    aurocs = [r.auroc for r in results]
    auroc_maxes = [r.auroc_max for r in results]
    task_names = [r.task_name for r in results]

    ax.bar(x - width / 2, aurocs, width, label="Actual AUROC", color="steelblue", alpha=0.8)
    ax.bar(x + width / 2, auroc_maxes, width, label="AUROC_max (ceiling)", color="orange", alpha=0.8)
    ax.axhline(0.55, color="red", linestyle="--", linewidth=1.5, label="Threshold (0.55)")
    ax.set_xticks(x)
    ax.set_xticklabels(task_names)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("AUROC", fontsize=12)
    ax.set_title("H-E1: Actual AUROC vs Structural Ceiling", fontsize=13)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"Saved structural_ceiling figure: {output_path}")
