import ast
import json
from typing import Dict, List, Tuple

import numpy as np


class ASTFailureRateComputer:

    def compute_per_problem_rates(
        self,
        pool: Dict[str, List[dict]],
    ) -> Dict[str, float]:
        rates = {}
        for task_id, records in pool.items():
            if not records:
                rates[task_id] = 0.0
                continue
            failures = sum(1 for r in records if not r.get("ast_valid", True))
            rates[task_id] = failures / len(records)
        return rates

    def compute_arrays(
        self,
        baseline_pool: Dict[str, List[dict]],
        syncode_pool: Dict[str, List[dict]],
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        all_task_ids = sorted(set(baseline_pool.keys()) | set(syncode_pool.keys()))
        baseline_rates_dict = self.compute_per_problem_rates(baseline_pool)
        syncode_rates_dict = self.compute_per_problem_rates(syncode_pool)

        baseline_arr = np.array([baseline_rates_dict.get(t, 0.0) for t in all_task_ids])
        syncode_arr = np.array([syncode_rates_dict.get(t, 0.0) for t in all_task_ids])
        return baseline_arr, syncode_arr, all_task_ids

    def compute_delta_ast(
        self,
        baseline_rates: np.ndarray,
        syncode_rates: np.ndarray,
    ) -> float:
        return float(np.mean(baseline_rates) - np.mean(syncode_rates))

    def save_results(
        self,
        baseline_rates: np.ndarray,
        syncode_rates: np.ndarray,
        task_ids: List[str],
        output_path: str,
    ) -> dict:
        delta_ast = self.compute_delta_ast(baseline_rates, syncode_rates)
        per_problem = {
            task_ids[i]: {
                "baseline_rate": float(baseline_rates[i]),
                "syncode_rate": float(syncode_rates[i]),
                "delta": float(baseline_rates[i] - syncode_rates[i]),
            }
            for i in range(len(task_ids))
        }
        result = {
            "delta_ast": delta_ast,
            "baseline_mean": float(np.mean(baseline_rates)),
            "syncode_mean": float(np.mean(syncode_rates)),
            "n_problems": len(task_ids),
            "per_problem": per_problem,
        }
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        return result
