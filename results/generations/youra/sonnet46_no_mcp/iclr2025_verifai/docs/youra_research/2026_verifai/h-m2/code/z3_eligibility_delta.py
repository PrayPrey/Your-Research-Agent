import ast
import json
import logging
from typing import Dict, List, Tuple

import numpy as np

from config import Z3DeltaConfig

logger = logging.getLogger(__name__)


class Z3EligibilityDelta:
    def __init__(self, cfg: Z3DeltaConfig) -> None:
        self.cfg = cfg

    def _compute_arith_density(self, code: str) -> float:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0.0
        all_nodes = list(ast.walk(tree))
        n_total = len(all_nodes)
        if n_total == 0:
            return 0.0
        arith_count = sum(1 for n in all_nodes if isinstance(n, (ast.BinOp, ast.Compare)))
        return arith_count / n_total

    def _has_return_annotation(self, code: str) -> bool:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False
        return any(
            isinstance(n, ast.FunctionDef) and n.returns is not None
            for n in ast.walk(tree)
        )

    def check_z3_eligible_heuristic(self, code: str) -> bool:
        try:
            ast.parse(code)
        except SyntaxError:
            return False
        density = self._compute_arith_density(code)
        has_annot = self._has_return_annotation(code)
        return density > self.cfg.arith_density_threshold and has_annot

    def compute_eligibility_rate(
        self,
        pool: Dict[str, List[dict]],
        use_best_of: bool = True,
    ) -> Dict[str, bool]:
        result = {}
        for task_id, records in pool.items():
            if not records:
                result[task_id] = False
                continue
            if use_best_of:
                candidates = [r for r in records if r.get("ast_valid", False)]
                sample = candidates[0] if candidates else records[0]
            else:
                sample = records[0]
            code = sample.get("completion") or sample.get("final_code", "")
            result[task_id] = self.check_z3_eligible_heuristic(code)
        return result

    def compute_delta_p(
        self,
        baseline_eligible: Dict[str, bool],
        post_mypy_eligible: Dict[str, bool],
    ) -> Tuple[float, float, float, float]:
        common_ids = sorted(set(baseline_eligible) & set(post_mypy_eligible))
        if not common_ids:
            return (0.0, 0.0, 0.0, 1.0)
        b_arr = np.array([float(baseline_eligible[t]) for t in common_ids])
        m_arr = np.array([float(post_mypy_eligible[t]) for t in common_ids])
        diffs = m_arr - b_arr
        delta_p = float(np.mean(diffs))
        rng = np.random.default_rng(42)
        n = len(diffs)
        boot = np.array([np.mean(diffs[rng.integers(0, n, size=n)]) for _ in range(10000)])
        ci_lower = float(np.percentile(boot, 2.5))
        ci_upper = float(np.percentile(boot, 97.5))
        p_value = float(np.mean(boot <= 0))
        return delta_p, ci_lower, ci_upper, p_value

    def save_results(
        self,
        delta_p: float,
        ci_lower: float,
        ci_upper: float,
        p_value: float,
        output_path: str,
        baseline_eligible: Dict[str, bool] = None,
        post_mypy_eligible: Dict[str, bool] = None,
    ) -> dict:
        n_problems = 0
        p_baseline = 0.0
        p_post_mypy = 0.0
        if baseline_eligible and post_mypy_eligible:
            common = sorted(set(baseline_eligible) & set(post_mypy_eligible))
            n_problems = len(common)
            if n_problems > 0:
                p_baseline = float(np.mean([float(baseline_eligible[t]) for t in common]))
                p_post_mypy = float(np.mean([float(post_mypy_eligible[t]) for t in common]))
        result = {
            "delta_p": delta_p,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "p_value": p_value,
            "n_problems": n_problems,
            "p_baseline": p_baseline,
            "p_post_mypy": p_post_mypy,
            "n_bootstrap": 10000,
        }
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        return result
