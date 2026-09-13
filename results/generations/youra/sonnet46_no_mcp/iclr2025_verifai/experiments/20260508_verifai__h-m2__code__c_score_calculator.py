import json
import logging
from typing import Dict, List, Set

import numpy as np

from config import CScoreConfig

logger = logging.getLogger(__name__)


class CScoreCalculator:
    def __init__(self, cfg: CScoreConfig) -> None:
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.seed)

    def compute_c_score(
        self,
        set_a: Set[str],
        set_b: Set[str],
        stratum: List[str],
    ) -> Dict:
        stratum_set = set(stratum)
        n = len(stratum_set)
        if n == 0:
            return {
                "j_obs": 0.0, "e_j": 0.0, "c_score": 0.0,
                "r1": 0.0, "r2": 0.0,
                "intersection_size": 0, "union_size": 0, "stratum_size": 0,
            }
        a_in = set_a & stratum_set
        b_in = set_b & stratum_set
        r1 = len(a_in) / n
        r2 = len(b_in) / n
        inter = a_in & b_in
        union = a_in | b_in
        j_obs = len(inter) / len(union) if union else 0.0
        denom = r1 + r2 - r1 * r2
        e_j = (r1 * r2) / denom if denom > 0 else 0.0
        c_score = (e_j - j_obs) / e_j if e_j > 0 else 0.0
        return {
            "j_obs": j_obs,
            "e_j": e_j,
            "c_score": c_score,
            "r1": r1,
            "r2": r2,
            "intersection_size": len(inter),
            "union_size": len(union),
            "stratum_size": n,
        }

    def bootstrap_c_score_ci(
        self,
        set_a: Set[str],
        set_b: Set[str],
        stratum: List[str],
    ) -> Dict:
        stratum_arr = np.array(list(stratum))
        n = len(stratum_arr)
        result = {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "p_value": 1.0, "n_bootstrap": self.cfg.n_bootstrap}
        if n == 0:
            return result
        if n < self.cfg.min_stratum_size:
            logger.warning(f"Stratum size {n} < min {self.cfg.min_stratum_size} — underpowered")
            result["underpowered"] = True

        boot_scores = []
        alpha = self.cfg.alpha
        for _ in range(self.cfg.n_bootstrap):
            idx = self.rng.integers(0, n, size=n)
            boot_stratum = list(stratum_arr[idx])
            boot_scores.append(self.compute_c_score(set_a, set_b, boot_stratum)["c_score"])
        boot_arr = np.array(boot_scores)
        result.update({
            "mean": float(np.mean(boot_arr)),
            "ci_lower": float(np.percentile(boot_arr, alpha / 2 * 100)),
            "ci_upper": float(np.percentile(boot_arr, (1 - alpha / 2) * 100)),
            "p_value": float(np.mean(boot_arr <= 0)),
            "n_bootstrap": self.cfg.n_bootstrap,
        })
        return result

    def define_eligibility_conditioned_stratum(
        self,
        fmd_classifications: Dict[str, List[str]],
        mypy_eligible_problems: Set[str],
    ) -> List[str]:
        # CRITICAL: FMDClassifier returns "type" not "type_structural"
        result = []
        for task_id, labels in fmd_classifications.items():
            if any(lbl == "type" for lbl in labels) and task_id in mypy_eligible_problems:
                result.append(task_id)
        return sorted(result)

    def compute_difficulty_quintiles(
        self,
        problems: List[str],
        baseline_pass_rates: Dict[str, float],
    ) -> Dict[int, List[str]]:
        sorted_probs = sorted(problems, key=lambda t: baseline_pass_rates.get(t, 0.0))
        n = len(sorted_probs)
        quintiles = {}
        for q in range(5):
            start = q * n // 5
            end = (q + 1) * n // 5 if q < 4 else n
            quintiles[q] = sorted_probs[start:end]
        return quintiles

    def compute_c_score_by_quintile(
        self,
        set_a: Set[str],
        set_b: Set[str],
        quintiles: Dict[int, List[str]],
    ) -> Dict[int, Dict]:
        return {q: self.compute_c_score(set_a, set_b, stratum) for q, stratum in quintiles.items()}

    def save_results(
        self,
        conditioned_result: Dict,
        conditioned_ci: Dict,
        raw_result: Dict,
        quintile_results: Dict[int, Dict],
        output_path: str,
    ) -> dict:
        merged = {
            "c_score": conditioned_result.get("c_score"),
            "j_obs": conditioned_result.get("j_obs"),
            "e_j": conditioned_result.get("e_j"),
            "r1": conditioned_result.get("r1"),
            "r2": conditioned_result.get("r2"),
            "stratum_size": conditioned_result.get("stratum_size"),
            "intersection_size": conditioned_result.get("intersection_size"),
            "union_size": conditioned_result.get("union_size"),
            "ci_lower": conditioned_ci.get("ci_lower"),
            "ci_upper": conditioned_ci.get("ci_upper"),
            "bootstrap_p_value": conditioned_ci.get("p_value"),
            "ci_mean": conditioned_ci.get("mean"),
            "n_bootstrap": conditioned_ci.get("n_bootstrap"),
            "raw_c_score": raw_result.get("c_score"),
            "raw_j_obs": raw_result.get("j_obs"),
            "raw_e_j": raw_result.get("e_j"),
            "raw_stratum_size": raw_result.get("stratum_size"),
            "quintile_results": {
                str(q): v for q, v in quintile_results.items()
            },
        }
        with open(output_path, "w") as f:
            json.dump(merged, f, indent=2)
        return merged
