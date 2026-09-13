import numpy as np
from scipy.stats import pearsonr
from typing import Dict, List
from config import ExperimentConfig


class CorrelationAnalyzer:
    def __init__(self, cfg: ExperimentConfig):
        self.cfg = cfg

    def aggregate_across_seeds(
        self,
        results_per_seed: Dict[int, Dict[int, Dict[str, float]]],
    ) -> Dict[int, Dict[str, float]]:
        # Collect all epochs from first seed
        all_seeds = list(results_per_seed.keys())
        if not all_seeds:
            return {}
        all_epochs = sorted(results_per_seed[all_seeds[0]].keys())

        aggregated = {}
        for epoch in all_epochs:
            erm_wgas = []
            dfr_wgas = []
            improvements = []
            for seed in all_seeds:
                metrics = results_per_seed[seed].get(epoch, {})
                if metrics:
                    erm_wgas.append(metrics["erm_wga"])
                    dfr_wgas.append(metrics["dfr_wga"])
                    improvements.append(metrics["wga_improvement"])

            aggregated[epoch] = {
                "mean_erm_wga": float(np.mean(erm_wgas)),
                "mean_dfr_wga": float(np.mean(dfr_wgas)),
                "mean_wga_improvement": float(np.mean(improvements)),
                "std_wga_improvement": float(np.std(improvements)),
            }
        return aggregated

    def compute_pearson(
        self,
        aggregated: Dict[int, Dict[str, float]],
        t_star: float,
    ) -> Dict:
        epochs = sorted(aggregated.keys())
        x = [float(epoch) - t_star for epoch in epochs]   # epochs_past_tstar
        y = [aggregated[e]["mean_wga_improvement"] for e in epochs]  # improvements

        if len(x) < 2:
            raise ValueError(f"Need at least 2 epoch conditions for Pearson r, got {len(x)}")
        r, p_two = pearsonr(x, y)
        p_one = p_two / 2.0 if r > 0 else 1.0 - p_two / 2.0

        return {
            "pearson_r": float(r),
            "pearson_p_twotailed": float(p_two),
            "pearson_p_onetailed": float(p_one),
            "epochs_past_tstar": x,
            "improvements": y,
            "epochs": epochs,
        }

    def evaluate_gate(self, pearson_r: float) -> Dict:
        gate_passed = pearson_r > self.cfg.analysis.pearson_r_threshold
        if gate_passed:
            decision = "PASS"
            note = f"Pearson r={pearson_r:.4f} > threshold={self.cfg.analysis.pearson_r_threshold}"
        else:
            decision = "LIMITATION"
            note = (f"Pearson r={pearson_r:.4f} <= threshold={self.cfg.analysis.pearson_r_threshold}; "
                    f"logged as limitation")
        return {
            "gate_passed": gate_passed,
            "pearson_r": float(pearson_r),
            "threshold": self.cfg.analysis.pearson_r_threshold,
            "decision": decision,
            "note": note,
        }

    def verify_monotonicity(self, improvements: List[float]) -> Dict:
        diffs = [improvements[i + 1] - improvements[i] for i in range(len(improvements) - 1)]
        n_positive = sum(1 for d in diffs if d > 0)
        is_monotonic = all(d > 0 for d in diffs)
        return {
            "is_monotonic": is_monotonic,
            "n_positive_diffs": n_positive,
            "n_diffs": len(diffs),
            "positive_fraction": float(n_positive / len(diffs)) if diffs else 0.0,
        }
