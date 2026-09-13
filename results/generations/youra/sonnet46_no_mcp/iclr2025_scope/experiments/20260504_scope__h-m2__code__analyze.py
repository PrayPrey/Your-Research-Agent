import json
import logging
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

import numpy as np
from scipy import stats

from config import LONGBENCH_CATEGORIES

logger = logging.getLogger(__name__)

BUDGET_RATIOS = [0.25, 0.50, 0.75]


@dataclass
class GapMatrix:
    """Per-model accuracy gap: eviction-aware minus sequential per (budget_ratio, category)."""
    model_name: str
    gaps: Dict[float, Dict[str, float]]   # gaps[r][category] = float
    mean_gaps: Dict[float, float]          # mean over 6 categories per r

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "gaps": {str(r): v for r, v in self.gaps.items()},
            "mean_gaps": {str(r): v for r, v in self.mean_gaps.items()},
        }


@dataclass
class SpearmanResult:
    model_name: str
    rho: float
    pval: float
    gate_passed: bool   # rho < -0.8

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MonotonicityResult:
    model_name: str
    per_category: Dict[str, bool]   # True if gap(0.25) > gap(0.50) > gap(0.75)
    fraction_monotone: float         # count(True) / 6

    def to_dict(self) -> dict:
        return asdict(self)


class SpearmanAnalyzer:
    def compute_gap_matrix(self, results) -> Dict[str, GapMatrix]:
        """Build GapMatrix per model_name from list of RunResults."""
        by_model = defaultdict(lambda: {"sequential": {}, "eviction-aware": {}})
        for r in results:
            by_model[r.model_name][r.adapter_type][r.budget_ratio] = r.category_scores

        gap_matrices = {}
        for model_name, adapter_data in by_model.items():
            seq = adapter_data.get("sequential", {})
            evict = adapter_data.get("eviction-aware", {})

            gaps = {}
            for ratio in BUDGET_RATIOS:
                gaps[ratio] = {}
                for cat in LONGBENCH_CATEGORIES:
                    seq_score = seq.get(ratio, {}).get(cat, float("nan"))
                    evict_score = evict.get(ratio, {}).get(cat, float("nan"))
                    gaps[ratio][cat] = evict_score - seq_score

            mean_gaps = {}
            for ratio in BUDGET_RATIOS:
                vals = [v for v in gaps[ratio].values() if not np.isnan(v)]
                mean_gaps[ratio] = float(np.mean(vals)) if vals else float("nan")

            gap_matrices[model_name] = GapMatrix(model_name, gaps, mean_gaps)

        return gap_matrices

    def compute_spearman(self, gap_matrix: GapMatrix) -> SpearmanResult:
        """scipy.stats.spearmanr([0.25, 0.50, 0.75], [mean_gap_25, mean_gap_50, mean_gap_75])."""
        ratios = BUDGET_RATIOS
        mean_gap_vals = [gap_matrix.mean_gaps.get(r, float("nan")) for r in ratios]

        # Filter out NaN
        valid = [(r, g) for r, g in zip(ratios, mean_gap_vals) if not np.isnan(g)]
        if len(valid) < 2:
            logger.warning(f"Insufficient data for Spearman: {gap_matrix.model_name}")
            return SpearmanResult(gap_matrix.model_name, rho=float("nan"), pval=1.0, gate_passed=False)

        rs, gs = zip(*valid)
        rho, pval = stats.spearmanr(list(rs), list(gs))
        gate_passed = float(rho) < -0.8

        logger.info(f"Spearman [{gap_matrix.model_name}]: rho={rho:.4f}, pval={pval:.4f}, gate={'PASS' if gate_passed else 'FAIL'}")
        return SpearmanResult(gap_matrix.model_name, rho=float(rho), pval=float(pval), gate_passed=gate_passed)

    def check_monotonicity(self, gap_matrix: GapMatrix) -> MonotonicityResult:
        """Per category: True if gaps strictly decrease as budget_ratio increases."""
        per_category = {}
        for cat in LONGBENCH_CATEGORIES:
            g25 = gap_matrix.gaps.get(0.25, {}).get(cat, float("nan"))
            g50 = gap_matrix.gaps.get(0.50, {}).get(cat, float("nan"))
            g75 = gap_matrix.gaps.get(0.75, {}).get(cat, float("nan"))
            if any(np.isnan(v) for v in [g25, g50, g75]):
                per_category[cat] = False
            else:
                per_category[cat] = (g25 > g50 > g75)

        fraction = sum(per_category.values()) / max(len(per_category), 1)
        return MonotonicityResult(
            model_name=gap_matrix.model_name,
            per_category=per_category,
            fraction_monotone=fraction,
        )

    def run_full_analysis(self, results) -> dict:
        """Returns: {gap_matrices, spearman_results, monotonicity, gate_passed}"""
        gap_matrices = self.compute_gap_matrix(results)
        spearman_results = {m: self.compute_spearman(gm) for m, gm in gap_matrices.items()}
        monotonicity = {m: self.check_monotonicity(gm) for m, gm in gap_matrices.items()}
        gate_passed = any(sr.gate_passed for sr in spearman_results.values())

        logger.info(f"Overall gate_passed: {gate_passed}")
        return {
            "gap_matrices": gap_matrices,
            "spearman_results": spearman_results,
            "monotonicity": monotonicity,
            "gate_passed": gate_passed,
        }

    def save_summary(self, analysis: dict, output_path: str) -> None:
        """Serialize analysis to JSON. Write to output_path."""
        summary = {
            "gate_passed": analysis["gate_passed"],
            "spearman_results": {
                m: sr.to_dict()
                for m, sr in analysis["spearman_results"].items()
            },
            "monotonicity": {
                m: mr.to_dict()
                for m, mr in analysis["monotonicity"].items()
            },
            "gap_matrices": {
                m: gm.to_dict()
                for m, gm in analysis["gap_matrices"].items()
            },
        }
        os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Summary saved to {output_path}")


import os  # noqa: E402 (needed for save_summary)
