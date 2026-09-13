"""Evaluation pipeline for IPCR routing experiment."""
import random
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import numpy as np
from scipy import stats

class EvaluationPipeline:
    """Evaluates routing strategies: Oracle, IPCR, Random, Uniform."""

    def __init__(
        self,
        model,  # MultiAdapterModel
        router,  # IPCRRouter
        task_type_fn,  # function to get task type from family
        seed: int = 42,
    ):
        self.model = model
        self.router = router
        self.task_type_fn = task_type_fn
        self.seed = seed
        random.seed(seed)

    def _select_adapter(self, sample: Dict, mode: str) -> Optional[str]:
        """Select adapter based on routing mode."""
        if mode == "oracle":
            return sample["task_family"]
        elif mode == "ipcr":
            return self.router.route(sample["instruction"])
        elif mode == "random":
            return random.choice(self.model.adapter_names)
        elif mode == "uniform":
            return None
        else:
            raise ValueError(f"Unknown mode: {mode}")

    def evaluate_routing(
        self,
        samples: List[Dict],
        mode: str,
        max_samples: Optional[int] = None,
    ) -> List[Dict]:
        """Evaluate routing strategy on samples."""
        if max_samples:
            samples = samples[:max_samples]

        results = []
        for sample in samples:
            adapter = self._select_adapter(sample, mode)

            if mode == "uniform":
                self.model.set_uniform()
            elif adapter:
                if adapter in self.model.adapter_names:
                    self.model.set_adapter(adapter)
                else:
                    adapter = self.model.adapter_names[0]
                    self.model.set_adapter(adapter)

            pred = self.model.generate(sample["instruction"])
            results.append({
                "prediction": pred,
                "reference": sample["response"],
                "task_family": sample["task_family"],
                "task_type": self.task_type_fn(sample["task_family"]),
                "selected_adapter": adapter,
                "instruction": sample["instruction"],
            })

        return results

    def compute_metrics(self, results: List[Dict]) -> Dict[str, float]:
        """Compute task-appropriate metrics."""
        family_scores = defaultdict(list)

        for r in results:
            pred = r["prediction"].lower().strip()
            ref = r["reference"].lower().strip()
            task_type = r["task_type"]

            if task_type == "classification":
                score = 1.0 if pred[:20] == ref[:20] else 0.0
            elif task_type == "qa":
                score = self._exact_match(pred, ref)
            else:
                score = self._rouge_l(pred, ref)

            family_scores[r["task_family"]].append(score)

        metrics = {}
        for family, scores in family_scores.items():
            metrics[family] = np.mean(scores) if scores else 0.0

        metrics["overall"] = np.mean(list(metrics.values())) if metrics else 0.0
        return metrics

    def _exact_match(self, pred: str, ref: str) -> float:
        """Exact match score."""
        pred_clean = "".join(pred.split())
        ref_clean = "".join(ref.split())
        return 1.0 if pred_clean == ref_clean else 0.0

    def _rouge_l(self, pred: str, ref: str) -> float:
        """Simple ROUGE-L (LCS-based) score."""
        pred_tokens = pred.split()
        ref_tokens = ref.split()

        if not ref_tokens:
            return 1.0 if not pred_tokens else 0.0

        m, n = len(pred_tokens), len(ref_tokens)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if pred_tokens[i-1] == ref_tokens[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])

        lcs = dp[m][n]
        precision = lcs / m if m > 0 else 0
        recall = lcs / n if n > 0 else 0

        if precision + recall == 0:
            return 0.0
        return 2 * precision * recall / (precision + recall)

    def compute_relative_score(
        self, ipcr_metrics: Dict[str, float], oracle_metrics: Dict[str, float]
    ) -> float:
        """Compute IPCR score relative to oracle."""
        oracle_overall = oracle_metrics.get("overall", 0)
        ipcr_overall = ipcr_metrics.get("overall", 0)

        if oracle_overall == 0:
            return 0.0
        return (ipcr_overall / oracle_overall) * 100

    def compare_significance(
        self, ipcr_scores: List[float], uniform_scores: List[float]
    ) -> Dict:
        """Paired t-test IPCR vs Uniform."""
        if len(ipcr_scores) != len(uniform_scores) or len(ipcr_scores) < 2:
            return {"t_stat": 0.0, "p_value": 1.0, "significant": False}

        t_stat, p_value = stats.ttest_rel(ipcr_scores, uniform_scores)
        return {
            "t_stat": float(t_stat),
            "p_value": float(p_value),
            "significant": p_value < 0.05,
        }

    def get_routing_accuracy(self, results: List[Dict]) -> float:
        """Compute routing accuracy (predicted adapter == oracle adapter)."""
        correct = 0
        total = 0
        for r in results:
            if r.get("selected_adapter") and r.get("task_family"):
                total += 1
                if r["selected_adapter"] == r["task_family"]:
                    correct += 1
        return correct / total if total > 0 else 0.0

    def get_per_family_breakdown(
        self, results: Dict[str, Dict[str, float]]
    ) -> Dict[str, Dict[str, float]]:
        """Get per-family scores for each routing mode."""
        breakdown = defaultdict(dict)
        for mode, metrics in results.items():
            for family, score in metrics.items():
                if family != "overall":
                    breakdown[family][mode] = score
        return dict(breakdown)


def evaluate_all_modes(
    model,
    router,
    samples: List[Dict],
    task_type_fn,
    max_samples: int = None,
) -> Dict[str, Dict]:
    """Evaluate all routing modes."""
    pipeline = EvaluationPipeline(model, router, task_type_fn)

    results = {}
    for mode in ["oracle", "ipcr", "random", "uniform"]:
        print(f"Evaluating {mode}...")
        mode_results = pipeline.evaluate_routing(samples, mode, max_samples)
        results[mode] = {
            "raw_results": mode_results,
            "metrics": pipeline.compute_metrics(mode_results),
        }

    relative_score = pipeline.compute_relative_score(
        results["ipcr"]["metrics"], results["oracle"]["metrics"]
    )

    ipcr_family_scores = list(results["ipcr"]["metrics"].values())
    uniform_family_scores = list(results["uniform"]["metrics"].values())
    significance = pipeline.compare_significance(
        ipcr_family_scores, uniform_family_scores
    )

    return {
        "modes": results,
        "relative_to_oracle": relative_score,
        "significance_vs_uniform": significance,
        "routing_accuracy": pipeline.get_routing_accuracy(
            results["ipcr"]["raw_results"]
        ),
    }
