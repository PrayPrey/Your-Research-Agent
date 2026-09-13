"""Spearman correlation matrix for domain-exposure vs benchmark scores."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy import stats
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import config


@dataclass
class CorrelationResult:
    rho: float
    p_val: float
    ci_lower: float
    ci_upper: float
    n: int


CorrelationMatrix = dict[str, dict[str, CorrelationResult]]


def compute_ci(rho: float, n: int) -> tuple[float, float]:
    """Fisher z-transform 95% CI for Spearman rho."""
    rho_clipped = np.clip(rho, -0.9999, 0.9999)
    z = np.arctanh(rho_clipped)
    se = 1.0 / np.sqrt(n - 3)
    return (float(np.tanh(z - 1.96 * se)), float(np.tanh(z + 1.96 * se)))


def compute_spearman_matrix(
    exposure: np.ndarray,
    scores: dict[str, np.ndarray],
    domain_names: list[str] = None,
) -> CorrelationMatrix:
    """Compute Spearman rho for all (domain, benchmark) pairs.
    exposure: (T_valid, 22), scores: {task: (T_valid,)}"""
    if domain_names is None:
        domain_names = config.PILE_DOMAINS

    T_valid = exposure.shape[0]
    matrix: CorrelationMatrix = {}

    for d_idx, domain in enumerate(domain_names):
        matrix[domain] = {}
        for benchmark, task_scores in scores.items():
            rho, p_val = stats.spearmanr(exposure[:, d_idx], task_scores)
            ci_lower, ci_upper = compute_ci(float(rho), T_valid)
            matrix[domain][benchmark] = CorrelationResult(
                rho=float(rho),
                p_val=float(p_val),
                ci_lower=ci_lower,
                ci_upper=ci_upper,
                n=T_valid,
            )

    return matrix


def extract_focal_correlations(
    matrices: dict[str, CorrelationMatrix],
) -> dict:
    """Extract focal (domain, benchmark) pairs across model sizes."""
    focal: dict = {
        "rho_wiki_mmlu": {},
        "rho_wiki_hellaswag": {},
        "rho_books_hellaswag": {},
        "rho_books_mmlu": {},
        "ci_wiki_mmlu": {},
        "ci_wiki_hellaswag": {},
        "ci_books_hellaswag": {},
        "ci_books_mmlu": {},
        "n_valid": {},
    }
    wiki = config.FOCAL_DOMAINS["wikipedia"]
    books = config.FOCAL_DOMAINS["books"]

    for model_size, matrix in matrices.items():
        focal["rho_wiki_mmlu"][model_size] = matrix[wiki]["mmlu"].rho
        focal["rho_wiki_hellaswag"][model_size] = matrix[wiki]["hellaswag"].rho
        focal["rho_books_hellaswag"][model_size] = matrix[books]["hellaswag"].rho
        focal["rho_books_mmlu"][model_size] = matrix[books]["mmlu"].rho
        focal["ci_wiki_mmlu"][model_size] = (matrix[wiki]["mmlu"].ci_lower, matrix[wiki]["mmlu"].ci_upper)
        focal["ci_wiki_hellaswag"][model_size] = (matrix[wiki]["hellaswag"].ci_lower, matrix[wiki]["hellaswag"].ci_upper)
        focal["ci_books_hellaswag"][model_size] = (matrix[books]["hellaswag"].ci_lower, matrix[books]["hellaswag"].ci_upper)
        focal["ci_books_mmlu"][model_size] = (matrix[books]["mmlu"].ci_lower, matrix[books]["mmlu"].ci_upper)
        focal["n_valid"][model_size] = matrix[wiki]["mmlu"].n

    return focal
