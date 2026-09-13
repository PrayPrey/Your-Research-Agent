"""H-E1 Analysis Module: Capability detrending and correlation analysis."""
import json
import os
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional

import numpy as np
from scipy.stats import spearmanr

from config import CONFIG, PATHS
from evaluate import CheckpointResult

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

@dataclass
class CorrelationResult:
    r: float
    p_value: float
    n: int
    per_benchmark: dict = field(default_factory=dict)

def fit_capability_regression(
    wikitext_ppl: np.ndarray,
    scores: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Fit linear regression: score ~ log(1/perplexity)."""
    valid_mask = (wikitext_ppl > 0) & np.isfinite(wikitext_ppl) & np.isfinite(scores)
    if valid_mask.sum() < 2:
        return np.array([0.0, 0.0]), scores.copy()

    x = np.log(1.0 / wikitext_ppl[valid_mask])
    y = scores[valid_mask]

    coeffs = np.polyfit(x, y, deg=1)

    expected_scores = np.zeros_like(scores)
    expected_scores[valid_mask] = np.polyval(coeffs, x)
    expected_scores[~valid_mask] = scores[~valid_mask]

    return coeffs, expected_scores

def compute_inflation_residuals(
    scores: np.ndarray,
    expected_scores: np.ndarray,
) -> np.ndarray:
    """Compute inflation residuals: actual - expected."""
    return scores - expected_scores

def compute_correlation(
    contamination_pct: np.ndarray,
    inflation_residuals: np.ndarray,
) -> tuple[float, float]:
    """Compute Spearman correlation between contamination and inflation."""
    valid_mask = np.isfinite(contamination_pct) & np.isfinite(inflation_residuals)
    if valid_mask.sum() < 3:
        return 0.0, 1.0

    r, p = spearmanr(contamination_pct[valid_mask], inflation_residuals[valid_mask])
    return float(r), float(p)

def run_full_analysis(
    checkpoints_data: list[CheckpointResult],
    contamination_by_task_pct: dict[str, float],
) -> CorrelationResult:
    """Run complete analysis: detrend per benchmark, correlate with contamination."""
    tasks = list(set(c.task for c in checkpoints_data))

    per_benchmark = {}
    all_contam = []
    all_residuals = []

    for task in tasks:
        rows = [c for c in checkpoints_data if c.task == task]
        if len(rows) < 3:
            log.warning(f"Skipping {task}: insufficient data ({len(rows)} rows)")
            continue

        ppl = np.array([r.wikitext_ppl for r in rows])
        scores = np.array([r.score for r in rows])

        _, expected = fit_capability_regression(ppl, scores)
        residuals = compute_inflation_residuals(scores, expected)

        contam_val = contamination_by_task_pct.get(task, 0.0)
        contam = np.full(len(rows), contam_val)

        r_val, p_val = compute_correlation(contam, residuals)
        per_benchmark[task] = {"r": r_val, "p": p_val, "n": len(rows)}

        all_contam.extend(contam.tolist())
        all_residuals.extend(residuals.tolist())

        log.info(f"{task}: r={r_val:.3f}, p={p_val:.4f}, n={len(rows)}")

    all_contam = np.array(all_contam)
    all_residuals = np.array(all_residuals)

    agg_r, agg_p = compute_correlation(all_contam, all_residuals)

    result = CorrelationResult(
        r=agg_r,
        p_value=agg_p,
        n=len(all_contam),
        per_benchmark=per_benchmark,
    )

    log.info(f"Aggregate: r={agg_r:.3f}, p={agg_p:.4f}, n={len(all_contam)}")

    return result

def save_analysis(result: CorrelationResult, output_path: Optional[str] = None) -> None:
    """Save analysis results to JSON."""
    output_path = output_path or PATHS.analysis_output_path
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(asdict(result), f, indent=2)
    log.info(f"Saved analysis to {output_path}")

if __name__ == "__main__":
    from evaluate import run_all_evaluations
    from contamination import contamination_by_task

    results = run_all_evaluations()
    contam = contamination_by_task()
    analysis = run_full_analysis(results, contam)
    save_analysis(analysis)

    print(f"\nGate Check:")
    print(f"  r = {analysis.r:.3f} (threshold: > {CONFIG.gate_r_threshold})")
    print(f"  p = {analysis.p_value:.4f} (threshold: < {CONFIG.gate_p_threshold})")
    gate_pass = analysis.r > CONFIG.gate_r_threshold and analysis.p_value < CONFIG.gate_p_threshold
    print(f"  Result: {'PASS' if gate_pass else 'FAIL'}")
