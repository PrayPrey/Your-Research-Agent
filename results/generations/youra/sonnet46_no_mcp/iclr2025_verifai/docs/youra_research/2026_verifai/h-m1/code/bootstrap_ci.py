import json
from typing import Tuple

import numpy as np


class BootstrapCI:

    def __init__(self, n_bootstrap: int = 10000, alpha: float = 0.05) -> None:
        self.n_bootstrap = n_bootstrap
        self.alpha = alpha

    def compute(
        self,
        baseline_rates: np.ndarray,
        syncode_rates: np.ndarray,
    ) -> Tuple[float, float, float, float]:
        diffs = baseline_rates - syncode_rates
        delta_mean = float(np.mean(diffs))

        rng = np.random.default_rng(seed=42)
        n = len(diffs)
        boot_deltas = np.array([
            np.mean(diffs[rng.integers(0, n, size=n)])
            for _ in range(self.n_bootstrap)
        ])

        ci_lower = float(np.percentile(boot_deltas, self.alpha / 2 * 100))
        ci_upper = float(np.percentile(boot_deltas, (1 - self.alpha / 2) * 100))
        p_value = float(np.mean(boot_deltas <= 0))

        return delta_mean, ci_lower, ci_upper, p_value

    def evaluate_gate(self, delta_mean: float, ci_lower: float) -> str:
        if delta_mean > 0 and ci_lower > 0:
            return "PASS"
        elif delta_mean > 0:
            return "PARTIAL"
        else:
            return "FAIL"

    def save_results(
        self,
        delta_mean: float,
        ci_lower: float,
        ci_upper: float,
        p_value: float,
        gate_result: str,
        output_path: str,
    ) -> dict:
        result = {
            "delta_ast": delta_mean,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "p_value": p_value,
            "gate_result": gate_result,
            "n_bootstrap": self.n_bootstrap,
            "alpha": self.alpha,
            "interpretation": "one-sided: p_value = fraction of bootstrap deltas <= 0",
        }
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        return result
