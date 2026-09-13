"""UQ mechanism validator: Spearman, AUROC, AUSE + gate check."""
from typing import Dict, List, Tuple
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score


class UQMechanismValidator:
    """Validate UQ mechanism via multiple metrics."""

    def __init__(
        self,
        uq_scores: Dict[str, List[float]],
        labels: List[int]
    ):
        """
        Initialize validator.

        Args:
            uq_scores: {method_name: [uncertainty scores]}
            labels: Binary labels (0=correct, 1=incorrect)
        """
        self.uq_scores = uq_scores
        self.labels = np.array(labels)
        self.n_samples = len(labels)

    def compute_spearman(self, method_name: str) -> Tuple[float, float]:
        """
        Spearman correlation between uncertainty and incorrectness.

        Returns:
            (rho, p_value)
        """
        uncertainties = np.array(self.uq_scores[method_name])
        rho, p_value = spearmanr(uncertainties, self.labels)
        return rho, p_value

    def compute_auroc(self, method_name: str) -> float:
        """
        AUROC treating uncertainty as positive class score.

        Returns:
            AUROC score (0.5 to 1.0)
        """
        uncertainties = np.array(self.uq_scores[method_name])
        return roc_auc_score(self.labels, uncertainties)

    def compute_ause(self, method_name: str, n_bins: int = 10) -> float:
        """
        Area Under Sparsification Error.

        Algorithm:
            1. Sort by uncertainty descending
            2. For k in [0%, 10%, 20%, ..., 100%]:
                - Remove top k% uncertain samples
                - Compute error on remaining
            3. Integrate error curve (trapezoidal)

        Returns:
            AUSE score (lower is better)
        """
        uncertainties = np.array(self.uq_scores[method_name])
        sorted_indices = np.argsort(uncertainties)[::-1]  # Descending

        fractions = np.linspace(0, 1, n_bins + 1)
        errors = []

        for frac in fractions:
            # Remove top frac% of high-uncertainty samples
            n_remove = int(frac * self.n_samples)
            remaining_indices = sorted_indices[n_remove:]

            if len(remaining_indices) == 0:
                errors.append(1.0)  # All removed
            else:
                # Error on remaining samples
                remaining_error = self.labels[remaining_indices].mean()
                errors.append(remaining_error)

        # AUSE = area under the sparsification error curve
        ause = np.trapz(errors, fractions)
        return ause

    def validate_all_methods(self) -> Dict[str, Dict]:
        """
        Run all metrics on all methods.

        Returns:
            {
                "temp_scaling": {
                    "spearman_rho": float,
                    "spearman_p": float,
                    "auroc": float,
                    "ause": float,
                    "pass_gate": bool
                },
                ...
            }
        """
        results = {}
        for method_name in self.uq_scores.keys():
            rho, p_val = self.compute_spearman(method_name)
            auroc = self.compute_auroc(method_name)
            ause = self.compute_ause(method_name)

            # Gate check: Non-degenerate methods must pass Spearman > 0.2 OR AUROC > 0.55
            is_degenerate = (method_name == "mc_k1")
            pass_gate = is_degenerate or (rho > 0.2 or auroc > 0.55)

            results[method_name] = {
                "spearman_rho": float(rho),
                "spearman_p": float(p_val),
                "auroc": float(auroc),
                "ause": float(ause),
                "pass_gate": bool(pass_gate),
                "is_degenerate": bool(is_degenerate)
            }

        return results

    def check_gate(self, results: Dict) -> Tuple[bool, str]:
        """
        Gate logic: >=4 of 5 non-degenerate methods pass.

        Pass condition per method: rho > 0.2 OR auroc > 0.55

        Returns:
            (passed, reason_str)
        """
        non_degenerate = [m for m in results.keys() if not results[m]["is_degenerate"]]
        passed_methods = [m for m in non_degenerate if results[m]["pass_gate"]]

        passed = len(passed_methods) >= 4
        reason = f"{len(passed_methods)}/5 non-degenerate methods passed gate"

        return passed, reason

    def compute_sparsification_data(self, method_name: str, n_bins: int = 10) -> Dict:
        """
        Compute sparsification curve data for plotting.

        Returns:
            {
                "fractions": List[float],
                "errors": List[float],
                "oracle_errors": List[float]  # Sorted by true error
            }
        """
        uncertainties = np.array(self.uq_scores[method_name])
        sorted_by_unc = np.argsort(uncertainties)[::-1]
        sorted_by_error = np.argsort(self.labels)[::-1]  # Oracle: sort by true error

        fractions = np.linspace(0, 1, n_bins + 1)
        errors = []
        oracle_errors = []

        for frac in fractions:
            n_remove = int(frac * self.n_samples)

            # Method-based removal
            remaining_method = sorted_by_unc[n_remove:]
            err_method = self.labels[remaining_method].mean() if len(remaining_method) > 0 else 1.0
            errors.append(float(err_method))

            # Oracle removal
            remaining_oracle = sorted_by_error[n_remove:]
            err_oracle = self.labels[remaining_oracle].mean() if len(remaining_oracle) > 0 else 1.0
            oracle_errors.append(float(err_oracle))

        return {
            "fractions": fractions.tolist(),
            "errors": errors,
            "oracle_errors": oracle_errors
        }
