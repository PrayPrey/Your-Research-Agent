import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

from config import ExperimentConfig

logger = logging.getLogger(__name__)


class StatisticalValidator:
    def __init__(self, cfg: ExperimentConfig):
        self.n_bootstrap: int = cfg.analysis.n_bootstrap
        self.bootstrap_seed: int = cfg.analysis.bootstrap_seed
        self.std_gate_threshold: float = cfg.analysis.std_gate_threshold
        self.min_seeds: int = cfg.analysis.min_seeds

    def bootstrap_std_ci(
        self,
        t_star_values: List[float],
        n_resamples: int = None,
    ) -> Tuple[float, float]:
        n_resamples = n_resamples or self.n_bootstrap
        rng = np.random.default_rng(self.bootstrap_seed)
        vals = np.array(t_star_values, dtype=float)
        if len(vals) < 2:
            return (0.0, 0.0)
        boot_stds = []
        for _ in range(n_resamples):
            sample = rng.choice(vals, size=len(vals), replace=True)
            boot_stds.append(float(np.std(sample, ddof=1)))
        ci_low = float(np.percentile(boot_stds, 2.5))
        ci_high = float(np.percentile(boot_stds, 97.5))
        return (ci_low, ci_high)

    def bootstrap_mean_ci(
        self,
        values: List[float],
        n_resamples: int = None,
    ) -> Tuple[float, float]:
        n_resamples = n_resamples or self.n_bootstrap
        rng = np.random.default_rng(self.bootstrap_seed)
        vals = np.array(values, dtype=float)
        if len(vals) < 2:
            return (float(vals[0]) if len(vals) == 1 else 0.0, float(vals[0]) if len(vals) == 1 else 0.0)
        boot_means = []
        for _ in range(n_resamples):
            sample = rng.choice(vals, size=len(vals), replace=True)
            boot_means.append(float(np.mean(sample)))
        ci_low = float(np.percentile(boot_means, 2.5))
        ci_high = float(np.percentile(boot_means, 97.5))
        return (ci_low, ci_high)

    def evaluate_gate(self, analysis_results: dict) -> dict:
        t_star_per_seed = analysis_results["t_star_per_seed"]
        valid = [v for v in t_star_per_seed.values() if v is not None]

        if len(valid) < self.min_seeds:
            return {
                "gate_passed": False,
                "decision": "FAIL",
                "std_t_star": None,
                "ci_95_std": None,
                "partial_pass": False,
                "insufficient_data": True,
                "criteria": {
                    "std_gate_threshold": self.std_gate_threshold,
                    "min_seeds": self.min_seeds,
                    "valid_seeds_found": len(valid),
                },
            }

        std_val = float(np.std(valid, ddof=1)) if len(valid) > 1 else 0.0
        ci = self.bootstrap_std_ci(valid)
        gate_passed = std_val < self.std_gate_threshold
        partial = (not gate_passed) and std_val < 2.0 * self.std_gate_threshold

        if gate_passed:
            decision = "PASS"
        elif partial:
            decision = "PARTIAL-PASS"
        else:
            decision = "FAIL"

        logger.info(
            f"Gate evaluation: std(t*)={std_val:.2f}, threshold={self.std_gate_threshold}, "
            f"decision={decision}, CI=[{ci[0]:.2f}, {ci[1]:.2f}]"
        )

        return {
            "gate_passed": gate_passed,
            "decision": decision,
            "std_t_star": std_val,
            "ci_95_std": list(ci),
            "partial_pass": partial,
            "insufficient_data": False,
            "criteria": {
                "std_gate_threshold": self.std_gate_threshold,
                "min_seeds": self.min_seeds,
                "valid_seeds_found": len(valid),
            },
        }

    def verify_mechanism_activated(self, results: dict) -> Tuple[bool, dict]:
        t_star_per_seed = results.get("t_star_per_seed", {})
        indicators = {
            "all_seeds_found_t_star": all(
                t is not None for t in t_star_per_seed.values()
            ),
            "std_below_threshold": (
                results.get("std_t_star") is not None
                and results["std_t_star"] < self.std_gate_threshold
            ),
            "gap_area_positive": results.get("mean_gap_area", 0.0) > 0,
            "curves_loaded": len(results.get("delta_curves_loaded", [])) >= self.min_seeds,
        }
        all_pass = all(indicators.values())
        logger.info(f"Mechanism verification: {indicators}")
        return all_pass, indicators

    def run_full_validation(self, analysis_results: dict) -> dict:
        gate = self.evaluate_gate(analysis_results)
        mech_pass, indicators = self.verify_mechanism_activated(analysis_results)

        gap_areas = list(analysis_results.get("gap_areas", {}).values())
        gap_ci = self.bootstrap_mean_ci(gap_areas) if len(gap_areas) >= 2 else None

        return {
            "gate_passed": gate["gate_passed"],
            "gate_decision": gate["decision"],
            "std_t_star": gate["std_t_star"],
            "ci_95_std": gate["ci_95_std"],
            "partial_pass": gate["partial_pass"],
            "insufficient_data": gate["insufficient_data"],
            "gate_criteria": gate["criteria"],
            "mechanism_activated": mech_pass,
            "mechanism_indicators": indicators,
            "gap_area_ci_95": list(gap_ci) if gap_ci else None,
        }
