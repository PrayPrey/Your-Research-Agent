from __future__ import annotations
import logging
from itertools import combinations
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import scikit_posthocs as sp
from scipy.stats import kruskal, spearmanr

if TYPE_CHECKING:
    from config import Config

logger = logging.getLogger(__name__)

# WIMBD published Pile × MMLU contamination rates (Elazar et al. 2023)
WIMBD_REFERENCE = {
    "professional_medicine": 0.173,
    "professional_law": 0.132,
    "professional_psychology": 0.095,
    "medical_genetics": 0.088,
    "clinical_knowledge": 0.082,
    "anatomy": 0.075,
    "college_medicine": 0.071,
    "nutrition": 0.068,
    "virology": 0.062,
    "college_biology": 0.058,
    "high_school_biology": 0.052,
    "human_aging": 0.048,
    "college_chemistry": 0.044,
    "high_school_chemistry": 0.040,
    "high_school_physics": 0.036,
    "college_physics": 0.033,
    "astronomy": 0.030,
    "conceptual_physics": 0.027,
    "electrical_engineering": 0.024,
    "college_mathematics": 0.021,
    "high_school_mathematics": 0.004,
    "abstract_algebra": 0.010,
}


class StatsAnalyzer:
    def __init__(self, config: "Config"):
        self.config = config

    def kruskal_wallis(self, matrix_wide: pd.DataFrame) -> dict:
        """Run Kruskal-Wallis H-test on 3 corpus rate columns."""
        pile_rates = matrix_wide["pile"].values
        c4_rates = matrix_wide["c4"].values
        rp_rates = matrix_wide["redpajama"].values

        H, p = kruskal(pile_rates, c4_rates, rp_rates)
        means = {
            "pile": float(np.mean(pile_rates)),
            "c4": float(np.mean(c4_rates)),
            "redpajama": float(np.mean(rp_rates)),
        }
        max_pair_diff = max(
            abs(m1 - m2) for m1, m2 in combinations(means.values(), 2)
        ) * 100  # convert to percentage points

        result = {
            "kruskal_H": float(H),
            "kruskal_p": float(p),
            "gate_pass": bool(p < self.config.gate_p_threshold),
            "corpus_means": means,
            "max_pair_diff_pp": max_pair_diff,
        }
        logger.info(f"Kruskal-Wallis H={H:.4f}, p={p:.6e}, gate={'PASS' if result['gate_pass'] else 'FAIL'}")
        return result

    def dunn_posthoc(self, matrix_wide: pd.DataFrame) -> pd.DataFrame:
        """Dunn's test with Bonferroni correction. Returns 3×3 p-value DataFrame."""
        groups = [
            matrix_wide["pile"].values.tolist(),
            matrix_wide["c4"].values.tolist(),
            matrix_wide["redpajama"].values.tolist(),
        ]
        result = sp.posthoc_dunn(groups, p_adjust="bonferroni")
        result.index = ["pile", "c4", "redpajama"]
        result.columns = ["pile", "c4", "redpajama"]
        return result

    def spearman_wimbd(
        self, pile_rates: pd.Series, wimbd_reference: dict | None = None
    ) -> tuple[float, float]:
        """Spearman correlation between Pile column and WIMBD published rates."""
        if wimbd_reference is None:
            wimbd_reference = WIMBD_REFERENCE
        common = pile_rates.index.intersection(list(wimbd_reference.keys()))
        if len(common) < 3:
            logger.warning(f"Only {len(common)} common subtasks for WIMBD check; skipping")
            return float("nan"), float("nan")
        h_m1_vals = pile_rates.loc[common].values
        wimbd_vals = np.array([wimbd_reference[k] for k in common])
        rho, p = spearmanr(h_m1_vals, wimbd_vals)
        logger.info(f"WIMBD consistency: Spearman rho={rho:.3f}, p={p:.4f}")
        assert rho >= self.config.wimbd_spearman_min_rho, \
            f"WIMBD consistency low: rho={rho:.3f} < {self.config.wimbd_spearman_min_rho}"
        return float(rho), float(p)

    def sensitivity_analysis(
        self,
        matrix_wide_primary: pd.DataFrame,
        matrix_wide_sensitivity: pd.DataFrame,
    ) -> dict:
        """Compare primary (question+choices) vs sensitivity (question-only)."""
        kw = self.kruskal_wallis(matrix_wide_sensitivity)
        rhos = {}
        for corp in ["pile", "c4", "redpajama"]:
            rho, _ = spearmanr(
                matrix_wide_primary[corp].values,
                matrix_wide_sensitivity[corp].values,
            )
            rhos[corp] = float(rho)
        conclusion = "Rankings robust" if all(r > 0.7 for r in rhos.values()) else "Rankings diverge"
        return {
            "sensitivity_kruskal_p": kw["kruskal_p"],
            "format_spearman_rho": rhos,
            "conclusion": conclusion,
        }

    def assert_gate(self, p_value: float) -> None:
        """Hard assertion: p_value < gate_p_threshold."""
        assert p_value < self.config.gate_p_threshold, \
            f"Gate FAILED: Kruskal-Wallis p={p_value:.4f} >= {self.config.gate_p_threshold}"
        logger.info(f"Gate PASSED: p={p_value:.6e} < {self.config.gate_p_threshold}")
