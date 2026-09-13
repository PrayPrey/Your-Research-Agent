"""H-M1 Analysis - Correlation analysis and divergent model detection."""
import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple
import config

def compute_tqa_mmlu_correlation(scores_df: pd.DataFrame) -> Tuple[float, float]:
    """Spearman r(truthfulqa, mmlu). Returns (r, p)."""
    r, p = stats.spearmanr(scores_df["truthfulqa"], scores_df["mmlu"])
    return float(r), float(p)

def compute_mmlu_internal_correlation(scores_df: pd.DataFrame) -> Tuple[float, np.ndarray]:
    """Pairwise Spearman r across all mmlu_* subject cols.
    Returns (mean_r, all_rs) where all_rs = flat array of all subject-pair correlations.
    """
    subjects = [c for c in scores_df.columns if c.startswith("mmlu_")]
    assert len(subjects) >= 2, f"Need >= 2 MMLU subjects, got {len(subjects)}"

    rs = []
    for i in range(len(subjects)):
        for j in range(i + 1, len(subjects)):
            r, _ = stats.spearmanr(scores_df[subjects[i]], scores_df[subjects[j]])
            if not np.isnan(r):
                rs.append(r)

    return float(np.mean(rs)), np.array(rs)

def compute_r2_gap(r_tqa_mmlu: float, r_mmlu_internal_mean: float) -> float:
    """r_mmlu_internal_mean**2 - r_tqa_mmlu**2, variance-share difference."""
    return r_mmlu_internal_mean**2 - r_tqa_mmlu**2

def detect_divergent_models(
    scores_df: pd.DataFrame,
    mmlu_z_thresh: float = None,
    tqa_z_thresh: float = None,
) -> pd.DataFrame:
    """Flag models with mmlu_z > mmlu_z_thresh AND tqa_z < tqa_z_thresh."""
    if mmlu_z_thresh is None:
        mmlu_z_thresh = config.Z_HIGH_MMLU
    if tqa_z_thresh is None:
        tqa_z_thresh = config.Z_LOW_TRUTHFULQA

    mmlu_z = (scores_df["mmlu"] - scores_df["mmlu"].mean()) / scores_df["mmlu"].std()
    tqa_z = (scores_df["truthfulqa"] - scores_df["truthfulqa"].mean()) / scores_df["truthfulqa"].std()

    mask = (mmlu_z > mmlu_z_thresh) & (tqa_z < tqa_z_thresh)

    out = scores_df[mask].copy()
    out["mmlu_z"] = mmlu_z[mask]
    out["tqa_z"] = tqa_z[mask]

    return out.sort_values("mmlu_z", ascending=False)

def evaluate_gate(
    r_tqa_mmlu: float,
    r_mmlu_internal_mean: float,
    divergent_df: pd.DataFrame,
) -> dict:
    """Combine conditions 1 & 2 into gate_pass bool + full results dict."""
    cond1 = r_tqa_mmlu < r_mmlu_internal_mean
    cond2 = len(divergent_df) >= 1
    gate_pass = cond1 and cond2

    return {
        "r_truthfulqa_mmlu": r_tqa_mmlu,
        "r_mmlu_internal_mean": r_mmlu_internal_mean,
        "condition_1_pass": cond1,
        "condition_2_pass": cond2,
        "divergent_count": len(divergent_df),
        "divergent_models": divergent_df["model"].tolist() if len(divergent_df) > 0 else [],
        "gate_pass": gate_pass,
    }

class CorrelationAnalyzer:
    """Main analyzer class orchestrating H-M1 analysis."""

    def __init__(self, population: pd.DataFrame):
        self.population = population
        self.results = {}

    def compute_cross_correlation(self) -> float:
        """r(truthfulqa, mmlu_overall)."""
        r, p = compute_tqa_mmlu_correlation(self.population)
        self.results["r_tqa_mmlu"] = r
        self.results["p_tqa_mmlu"] = p
        return r

    def compute_internal_correlations(self) -> pd.DataFrame:
        """r matrix across mmlu_<subject> cols."""
        mean_r, all_rs = compute_mmlu_internal_correlation(self.population)
        self.results["r_mmlu_internal_mean"] = mean_r
        self.results["r_mmlu_internal_std"] = float(np.std(all_rs))
        self.results["r_mmlu_internal_n_pairs"] = len(all_rs)
        return pd.DataFrame({"pairwise_r": all_rs})

    def find_divergent_models(self) -> pd.DataFrame:
        """z(mmlu)>1 & z(truthfulqa)<0 rows."""
        divergent = detect_divergent_models(self.population)
        self.results["divergent_count"] = len(divergent)
        self.results["divergent_models"] = divergent["model"].tolist() if len(divergent) > 0 else []
        return divergent

    def evaluate_hypothesis(self) -> dict:
        """Run full analysis and return gate evaluation."""
        self.compute_cross_correlation()
        self.compute_internal_correlations()
        divergent = self.find_divergent_models()

        r2_gap = compute_r2_gap(
            self.results["r_tqa_mmlu"],
            self.results["r_mmlu_internal_mean"]
        )
        self.results["r2_gap"] = r2_gap

        gate_result = evaluate_gate(
            self.results["r_tqa_mmlu"],
            self.results["r_mmlu_internal_mean"],
            divergent
        )

        self.results.update(gate_result)
        self.results["n_models"] = len(self.population)

        return self.results
