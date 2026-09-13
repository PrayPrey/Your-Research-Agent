"""Statistical analysis for H-M2: Stratified success rates and validation."""
import csv
import json
import numpy as np
from scipy import stats
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
from config import (
    RANDOM_SEED,
    DATASET_CONFIG,
    DEPTH_CONFIG,
    STATISTICAL_CONFIG,
    LOGGING_CONFIG,
    GATE_CRITERIA,
)


@dataclass
class StratifiedResults:
    """Results from depth stratification."""
    success_full: float
    success_shallow: float
    delta: float
    n_total: int
    n_solved_full: int
    n_solved_shallow: int
    depth_distribution: Dict[str, int]


@dataclass
class StatisticalTests:
    """Statistical validation results."""
    mcnemar_chi2: float
    mcnemar_pvalue: float
    bootstrap_ci_lower: float
    bootstrap_ci_upper: float
    is_significant: bool
    sufficient_power: bool


class StratificationAnalyzer:
    """Analyze proof depth stratification."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.rng = np.random.default_rng(RANDOM_SEED)
        self.shallow_threshold = DEPTH_CONFIG["shallow_max"]
        self.n_total = DATASET_CONFIG["total_theorems"]

    def _load_tactic_counts(self) -> List[Dict]:
        """Load tactic count data."""
        csv_file = f"{self.output_dir}/{LOGGING_CONFIG['tactic_counts']}"
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def _classify_depth(self, tactic_count: int) -> str:
        """Classify proof by depth category."""
        if tactic_count <= DEPTH_CONFIG["shallow_max"]:
            return "shallow"
        elif tactic_count <= DEPTH_CONFIG["medium_max"]:
            return "medium"
        else:
            return "deep"

    def compute_success_rates(self) -> StratifiedResults:
        """Compute stratified success rates."""
        data = self._load_tactic_counts()

        n_solved_full = len(data)
        n_solved_shallow = sum(1 for row in data if int(row["min_tactic_count"]) <= self.shallow_threshold)

        success_full = n_solved_full / self.n_total
        success_shallow = n_solved_shallow / self.n_total
        delta = success_full - success_shallow

        # Depth distribution
        distribution = {"shallow": 0, "medium": 0, "deep": 0}
        for row in data:
            min_depth = int(row["min_tactic_count"])
            category = self._classify_depth(min_depth)
            distribution[category] += 1

        print(f"[Analyzer] Success (full): {success_full:.1%} ({n_solved_full}/{self.n_total})")
        print(f"[Analyzer] Success (shallow): {success_shallow:.1%} ({n_solved_shallow}/{self.n_total})")
        print(f"[Analyzer] Delta: {delta:.1%} ({delta*100:.1f} pp)")
        print(f"[Analyzer] Distribution: {distribution}")

        return StratifiedResults(
            success_full=success_full,
            success_shallow=success_shallow,
            delta=delta,
            n_total=self.n_total,
            n_solved_full=n_solved_full,
            n_solved_shallow=n_solved_shallow,
            depth_distribution=distribution,
        )

    def mcnemar_test(self, results: StratifiedResults) -> Tuple[float, float]:
        """McNemar-like test for paired comparison (using manual calculation)."""
        # Build 2x2 contingency table
        n_both_success = results.n_solved_shallow  # Shallow-solvable = success in both
        n_full_only = results.n_solved_full - results.n_solved_shallow  # Deep-only solutions
        n_shallow_only = 0  # Cannot solve shallow if not solvable full
        n_both_fail = self.n_total - results.n_solved_full

        # McNemar statistic: (b - c)^2 / (b + c) where b, c are discordant pairs
        b = n_full_only
        c = n_shallow_only

        if b + c > 0:
            chi2 = (b - c) ** 2 / (b + c)
            # p-value from chi-square distribution (df=1)
            pvalue = 1 - stats.chi2.cdf(chi2, df=1)
        else:
            chi2 = 0.0
            pvalue = 1.0

        print(f"[Analyzer] McNemar χ²: {chi2:.3f}, p-value: {pvalue:.4f}")

        return chi2, pvalue

    def bootstrap_ci(self, results: StratifiedResults) -> Tuple[float, float]:
        """Bootstrap confidence interval for delta."""
        data = self._load_tactic_counts()

        # Create (theorem, min_depth) pairs
        problems = [(row["theorem"], int(row["min_tactic_count"])) for row in data]

        deltas = []
        n_iterations = STATISTICAL_CONFIG["bootstrap_samples"]

        for _ in range(n_iterations):
            # Resample with replacement
            sample_indices = self.rng.choice(len(problems), size=len(problems), replace=True)
            sample = [problems[i] for i in sample_indices]

            n_solved_full_sample = len(sample)
            n_solved_shallow_sample = sum(1 for _, depth in sample if depth <= self.shallow_threshold)

            success_full_sample = n_solved_full_sample / self.n_total
            success_shallow_sample = n_solved_shallow_sample / self.n_total
            delta_sample = success_full_sample - success_shallow_sample

            deltas.append(delta_sample)

        confidence = STATISTICAL_CONFIG["confidence_level"]
        alpha = (1 - confidence) / 2
        ci_lower = np.percentile(deltas, alpha * 100)
        ci_upper = np.percentile(deltas, (1 - alpha) * 100)

        print(f"[Analyzer] Bootstrap {confidence*100:.0f}% CI: [{ci_lower:.1%}, {ci_upper:.1%}]")

        return ci_lower, ci_upper

    def validate_power(self, n_solved: int) -> bool:
        """Check statistical power."""
        sufficient = n_solved >= DEPTH_CONFIG["min_solved_required"]
        print(f"[Analyzer] Power check: {n_solved} solved (min {DEPTH_CONFIG['min_solved_required']}) -> {'PASS' if sufficient else 'FAIL'}")
        return sufficient

    def plot_depth_histogram(self, results: StratifiedResults):
        """Generate histogram data (matplotlib unavailable)."""
        data = self._load_tactic_counts()
        min_depths = [int(row["min_tactic_count"]) for row in data]

        # Save histogram data as CSV
        output_file = f"{self.output_dir}/depth_distribution.csv"
        with open(output_file, "w") as f:
            f.write("tactic_count,frequency\n")
            from collections import Counter
            counts = Counter(min_depths)
            for depth in sorted(counts.keys()):
                f.write(f"{depth},{counts[depth]}\n")

        print(f"[Analyzer] Saved depth distribution to {output_file} (CSV format)")

    def run_full_analysis(self) -> Dict:
        """Run complete statistical analysis pipeline."""
        results = self.compute_success_rates()

        # Power check
        sufficient_power = self.validate_power(results.n_solved_full)
        if not sufficient_power:
            print("[Analyzer] WARNING: Insufficient power, results may be unreliable")

        # Statistical tests
        mcnemar_chi2, mcnemar_pvalue = self.mcnemar_test(results)
        ci_lower, ci_upper = self.bootstrap_ci(results)

        is_significant = mcnemar_pvalue < STATISTICAL_CONFIG["mcnemar_alpha"]

        stats_results = StatisticalTests(
            mcnemar_chi2=mcnemar_chi2,
            mcnemar_pvalue=mcnemar_pvalue,
            bootstrap_ci_lower=ci_lower,
            bootstrap_ci_upper=ci_upper,
            is_significant=is_significant,
            sufficient_power=sufficient_power,
        )

        # Histogram
        self.plot_depth_histogram(results)

        # Gate evaluation
        delta = results.delta
        gate_pass = GATE_CRITERIA["delta_min"] <= delta <= GATE_CRITERIA["delta_max"]

        print(f"\n[Analyzer] Gate Evaluation:")
        print(f"  Delta: {delta:.1%} ({delta*100:.1f} pp)")
        print(f"  Target range: [{GATE_CRITERIA['delta_min']:.0%}, {GATE_CRITERIA['delta_max']:.0%}]")
        print(f"  Result: {'PASS' if gate_pass else 'FAIL'}")

        # Save results (convert numpy types to native Python)
        def to_native(obj):
            """Convert numpy/pandas types to native Python."""
            if isinstance(obj, dict):
                return {k: to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [to_native(v) for v in obj]
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            return obj

        output_data = {
            "stratified_results": to_native(asdict(results)),
            "statistical_tests": to_native(asdict(stats_results)),
            "gate_evaluation": {
                "delta": float(delta),
                "target_range": [GATE_CRITERIA["delta_min"], GATE_CRITERIA["delta_max"]],
                "pass": bool(gate_pass),
            },
        }

        output_file = f"{self.output_dir}/{LOGGING_CONFIG['results_file']}"
        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"[Analyzer] Saved results to {output_file}")

        return output_data
