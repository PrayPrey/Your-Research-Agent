from __future__ import annotations
import numpy as np
from typing import Callable
from sklearn.metrics import recall_score, f1_score
from config import ExperimentConfig


class StratifiedEvaluator:
    """Per-stratum recall/F1, variance, indeterminacy rate, bootstrap CI."""

    def __init__(self, cfg: ExperimentConfig):
        self.bootstrap_n: int = cfg.bootstrap_n
        self.seed: int = cfg.seed

    def per_stratum_recall(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        strata: np.ndarray,
    ) -> dict[str, float]:
        """Returns {"lexical": float, "semantic": float, "indeterminate": float}."""
        result = {}
        for s in ["lexical", "semantic", "indeterminate"]:
            mask = strata == s
            if mask.sum() == 0:
                result[s] = float("nan")
            elif y_true[mask].sum() == 0:
                result[s] = 0.0
            else:
                result[s] = float(recall_score(y_true[mask], y_pred[mask], zero_division=0))
        return result

    def per_stratum_f1(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        strata: np.ndarray,
    ) -> dict[str, float]:
        """Returns {"lexical": float, "semantic": float, "indeterminate": float}."""
        result = {}
        for s in ["lexical", "semantic", "indeterminate"]:
            mask = strata == s
            if mask.sum() == 0:
                result[s] = float("nan")
            else:
                result[s] = float(f1_score(y_true[mask], y_pred[mask], zero_division=0))
        return result

    def minkpp_f1_variance(self, f1_per_corpus: list[float]) -> float:
        """F1 variance across corpora. Returns np.var(f1_per_corpus)."""
        return float(np.var(f1_per_corpus))

    def indeterminacy_rate(self, detector_f1_matrix: np.ndarray) -> float:
        """Fraction of items where top1 - top2 F1 < 0.05. Returns float in [0,1]."""
        if detector_f1_matrix.shape[1] < 2:
            return 0.0
        sorted_f1 = np.sort(detector_f1_matrix, axis=1)[:, ::-1]
        margin = sorted_f1[:, 0] - sorted_f1[:, 1]
        return float(np.mean(margin < 0.05))

    def bootstrap_ci(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        metric_fn: Callable,
        n_iterations: int = 10_000,
    ) -> tuple[float, float]:
        """Bootstrap 95% CI. Returns (lower_2.5, upper_97.5)."""
        rng = np.random.default_rng(self.seed)
        N = len(y_true)
        boot_scores = np.zeros(n_iterations, dtype=np.float32)
        for i in range(n_iterations):
            idx = rng.integers(0, N, size=N)
            try:
                boot_scores[i] = metric_fn(y_true[idx], y_pred[idx])
            except Exception:
                boot_scores[i] = 0.0
        lower, upper = np.percentile(boot_scores, [2.5, 97.5])
        return float(lower), float(upper)

    def run_full_evaluation(
        self,
        benchmark_name: str,
        corpus_name: str,
        y_true: np.ndarray,
        strata: np.ndarray,
        detector_preds: dict[str, np.ndarray],
    ) -> dict:
        """Run all metrics for one benchmark-corpus pair."""
        result: dict = {
            "benchmark": benchmark_name,
            "corpus": corpus_name,
            "recall_by_stratum": {},
            "f1_by_stratum": {},
            "bootstrap_ci": {},
            "minkpp_f1_variance": None,
            "indeterminacy_rate": None,
        }
        minkpp_f1s = []
        n_items = len(y_true)
        n_dets = len(detector_preds)
        f1_matrix = np.zeros((n_items, n_dets), dtype=np.float32)

        for di, (det_name, y_pred) in enumerate(detector_preds.items()):
            recall = self.per_stratum_recall(y_true, y_pred, strata)
            f1 = self.per_stratum_f1(y_true, y_pred, strata)
            result["recall_by_stratum"][det_name] = recall
            result["f1_by_stratum"][det_name] = f1
            try:
                ci = self.bootstrap_ci(y_true, y_pred, recall_score, n_iterations=min(1000, self.bootstrap_n))
                result["bootstrap_ci"][det_name] = ci
            except Exception:
                result["bootstrap_ci"][det_name] = (0.0, 1.0)
            if "minkpp" in det_name:
                total_f1 = float(f1_score(y_true, y_pred, zero_division=0))
                minkpp_f1s.append(total_f1)
            overall_f1 = float(f1_score(y_true, y_pred, zero_division=0))
            f1_matrix[:, di] = overall_f1  # simplified: same score per item

        result["minkpp_f1_variance"] = self.minkpp_f1_variance(minkpp_f1s) if minkpp_f1s else 0.0
        result["indeterminacy_rate"] = self.indeterminacy_rate(f1_matrix)
        return result


def check_poc_conditions(cfg, metrics: dict) -> dict:
    """Compare per-stratum recall/F1 and indeterminacy_rate against PoC thresholds."""
    checks: dict[str, bool] = {}
    for det_name, recall in metrics.get("recall_by_stratum", {}).items():
        if "ngram" in det_name:
            lex = recall.get("lexical", float("nan"))
            sem = recall.get("semantic", float("nan"))
            checks["ngram_lexical_recall_ge_080"] = not np.isnan(lex) and lex >= 0.80
            checks["ngram_semantic_recall_le_040"] = not np.isnan(sem) and sem <= 0.40
    var = metrics.get("minkpp_f1_variance", 0.0)
    checks["minkpp_f1_variance_ge_015"] = var >= 0.15
    ir = metrics.get("indeterminacy_rate", 1.0)
    checks["indeterminacy_rate_in_range"] = 0.10 <= ir <= 0.50
    checks["all_pass"] = all(checks.values())
    return checks
