"""
analyze.py — Statistical Analysis Core
H-M1: KL divergence, Wilcoxon rank-sum, near-uniform proportion, Cohen's d
"""
import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import entropy, ranksums

logger = logging.getLogger(__name__)


@dataclass
class TaskAnalysisResult:
    task_name: str
    kl_divergence_from_uniform: float   # nats
    kl_passes: bool                      # kl > 0.05
    wilcoxon_pvalue: float
    wilcoxon_statistic: float
    wilcoxon_passes: bool                # pvalue < 0.05
    p_near_uniform: float                # proportion scalar
    class_means: List[float]             # [P(contra), P(neutral), P(entail)] means
    cohens_d: float
    not_near_uniform: bool               # p_near_uniform < 0.10


@dataclass
class GateResult:
    gate_pass: bool
    kl_all_pass: bool
    wilcoxon_pass_count: int             # 0-3
    mechanism_activated: bool


def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Cohen's d; group1=hallucinated, group2=non-hallucinated.

    Mirrors h-e1 cohen_d: pooled_std = sqrt((var1 + var2) / 2)
    NOTE: Simple average of variances, NOT weighted by n.
    """
    var1 = np.var(group1)
    var2 = np.var(group2)
    pooled_std = np.sqrt((var1 + var2) / 2.0)
    if pooled_std == 0:
        return 0.0
    return float((np.mean(group1) - np.mean(group2)) / pooled_std)


def analyze_nli_distribution(
    scores_nxt3: np.ndarray,   # shape (N, 3): [P(contra), P(neutral), P(entail)]
    labels_n: np.ndarray,      # shape (N,), binary {0,1}
    task_name: str,
    config,
) -> TaskAnalysisResult:
    """KL divergence + Wilcoxon + near-uniform + Cohen's d for one task.

    Pseudo-code from 03_logic.md:
    1. class_means = scores_nxt3.mean(axis=0)
    2. uniform = [1/3, 1/3, 1/3]
    3. kl = entropy(class_means + 1e-10, uniform + 1e-10)
    4. kl_passes = kl > config.kl_threshold
    5. contra_scores = scores_nxt3[:, 0]
    6. hal_scores = contra_scores[labels_n == 1]
    7. corr_scores = contra_scores[labels_n == 0]
    8. stat, pvalue = ranksums(hal_scores, corr_scores)
    9. wilcoxon_passes = pvalue < config.wilcoxon_alpha
    10. near_uniform_mask = np.all(np.abs(scores_nxt3 - 1/3) < 0.05, axis=1)
    11. p_near_uniform = near_uniform_mask.mean()
    12. not_near_uniform = p_near_uniform < 0.10
    13. d = compute_cohens_d(hal_scores, corr_scores)
    """
    # Step 1-4: KL divergence from uniform
    class_means = scores_nxt3.mean(axis=0)  # shape (3,)
    uniform = np.array([1/3, 1/3, 1/3])
    kl = float(entropy(class_means + 1e-10, uniform + 1e-10))
    kl_passes = kl > config.kl_threshold

    # Step 5-9: Wilcoxon rank-sum on P(contradiction)
    contra_scores = scores_nxt3[:, 0]          # P(contradiction) column
    hal_scores = contra_scores[labels_n == 1]   # hallucinated group
    corr_scores = contra_scores[labels_n == 0]  # correct group
    stat, pvalue = ranksums(hal_scores, corr_scores)
    wilcoxon_passes = float(pvalue) < config.wilcoxon_alpha

    # Step 10-12: Near-uniform proportion
    near_uniform_mask = np.all(np.abs(scores_nxt3 - 1/3) < config.near_uniform_threshold, axis=1)
    p_near_uniform = float(near_uniform_mask.mean())
    not_near_uniform = p_near_uniform < 0.10

    # Step 13: Cohen's d
    d = compute_cohens_d(hal_scores, corr_scores)

    # Warn if high near-uniform proportion
    if p_near_uniform > config.near_uniform_warn_threshold:
        logger.warning(
            f"Task '{task_name}': High near-uniform proportion={p_near_uniform:.3f} "
            f"(> {config.near_uniform_warn_threshold}). Scores may be poorly calibrated."
        )

    logger.info(
        f"Task '{task_name}': KL={kl:.4f} (pass={kl_passes}), "
        f"Wilcoxon p={pvalue:.4e} (pass={wilcoxon_passes}), "
        f"near_uniform={p_near_uniform:.3f}, Cohen's d={d:.4f}"
    )

    return TaskAnalysisResult(
        task_name=task_name,
        kl_divergence_from_uniform=kl,
        kl_passes=kl_passes,
        wilcoxon_pvalue=float(pvalue),
        wilcoxon_statistic=float(stat),
        wilcoxon_passes=wilcoxon_passes,
        p_near_uniform=p_near_uniform,
        class_means=class_means.tolist(),
        cohens_d=d,
        not_near_uniform=not_near_uniform,
    )


def evaluate_gate(
    results: List[TaskAnalysisResult],
    config,
) -> GateResult:
    """Apply MUST_WORK gate: KL > 0.05 on all 3 AND Wilcoxon p < 0.05 on >= 2/3.

    Logs gate result with format: "GATE: PASS/FAIL (KL_all={}, Wilcoxon_count={}/3)"
    """
    kl_all_pass = all(r.kl_passes for r in results)
    wilcoxon_pass_count = sum(1 for r in results if r.wilcoxon_passes)
    gate_pass = kl_all_pass and (wilcoxon_pass_count >= config.wilcoxon_tasks_required)

    # Structured logging per task
    for r in results:
        logger.info(
            f"  [{r.task_name}] KL={r.kl_divergence_from_uniform:.4f} "
            f"(pass={r.kl_passes}), "
            f"Wilcoxon p={r.wilcoxon_pvalue:.4e} (pass={r.wilcoxon_passes}), "
            f"near_uniform={r.p_near_uniform:.3f}"
        )
        if r.p_near_uniform > 0.50:
            logger.warning(f"  [{r.task_name}] WARNING: p_near_uniform={r.p_near_uniform:.3f} > 0.50")

    gate_str = "PASS" if gate_pass else "FAIL"
    logger.info(
        f"GATE: {gate_str} (KL_all={kl_all_pass}, Wilcoxon_count={wilcoxon_pass_count}/3)"
    )

    _, indicators = verify_mechanism_activated(results, config)
    mechanism_activated = all(
        v.get("kl_passes") and v.get("wilcoxon_passes")
        for v in indicators.values()
    )

    return GateResult(
        gate_pass=gate_pass,
        kl_all_pass=kl_all_pass,
        wilcoxon_pass_count=wilcoxon_pass_count,
        mechanism_activated=mechanism_activated,
    )


def verify_mechanism_activated(
    results: List[TaskAnalysisResult],
    config,
) -> Tuple[bool, Dict[str, Dict[str, bool]]]:
    """Per-task indicators: kl_passes, wilcoxon_passes, not_near_uniform.

    Returns (all_pass, {task_name: {indicator: bool}})
    """
    indicators: Dict[str, Dict[str, bool]] = {}
    for r in results:
        indicators[r.task_name] = {
            "kl_passes": r.kl_passes,
            "wilcoxon_passes": r.wilcoxon_passes,
            "not_near_uniform": r.not_near_uniform,
        }

    all_pass = all(
        v["kl_passes"] and v["wilcoxon_passes"] and v["not_near_uniform"]
        for v in indicators.values()
    )

    return all_pass, indicators
