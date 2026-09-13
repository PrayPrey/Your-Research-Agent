"""
H-E1 Proxy Metric Validation PoC

CRITICAL NOTE: This is a PoC implementation demonstrating the measurement methodology.
Full implementation requires:
- GPU access for CodeLlama-7B-Instruct (16GB+ VRAM)
- HumanEval dataset download
- Linux perf tool for instruction counting

This PoC validates:
1. Measurement repeatability (CV calculation)
2. Complexity class separation (Cohen's d)
3. Cross-platform stability (Spearman ρ)

Using synthetic data to demonstrate gate validation logic.
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

from config import ExperimentConfig, validate_config


class ProxyMetricPoC:
    """
    Proof-of-concept for proxy metric validation.

    Demonstrates measurement reliability analysis without requiring
    full infrastructure (GPU, HumanEval, perf tools).
    """

    def __init__(self, config: ExperimentConfig):
        self.config = config
        np.random.seed(config.seed)

        # Output directories
        self.output_dir = Path("outputs")
        self.figures_dir = Path("figures")
        self.output_dir.mkdir(exist_ok=True)
        self.figures_dir.mkdir(exist_ok=True)

    def generate_synthetic_measurements(self) -> Dict[str, Dict[str, List[List[float]]]]:
        """
        Generate synthetic proxy metric measurements.

        Simulates:
        - 50 problems × 10 solutions = 500 solutions
        - 5 repeated measurements per solution
        - 3 proxy metrics (CodeBLEU, Runtime, PR-style)

        Returns:
            measurements: {metric_name: {solution_id: [rep1, rep2, ...]}}
        """
        print("\n[SYNTHETIC DATA] Generating measurements for PoC...")
        print(f"Problems: {self.config.dataset.problem_count}")
        print(f"Solutions per problem: {self.config.generation.num_solutions_per_problem}")
        print(f"Repetitions: {self.config.runtime.repetitions}")

        num_solutions = self.config.dataset.problem_count * self.config.generation.num_solutions_per_problem
        repetitions = self.config.runtime.repetitions

        measurements = {
            "CodeBLEU": {},
            "Runtime": {},
            "PR-style": {}
        }

        for sol_id in range(num_solutions):
            # CodeBLEU: Low CV (stable), good separation
            base_codebleu = np.random.beta(5, 2)  # Skewed toward higher values
            measurements["CodeBLEU"][f"sol_{sol_id}"] = [
                base_codebleu + np.random.normal(0, 0.01)  # CV ~1-2%
                for _ in range(repetitions)
            ]

            # Runtime: Very low CV (instruction count is stable)
            base_runtime = np.random.exponential(1.0)
            measurements["Runtime"][f"sol_{sol_id}"] = [
                base_runtime + np.random.normal(0, 0.01)  # CV ~1-2% (COFFE finding)
                for _ in range(repetitions)
            ]

            # PR-style: Higher CV (less stable - placeholder)
            base_pr = np.random.uniform(0, 1)
            measurements["PR-style"][f"sol_{sol_id}"] = [
                base_pr + np.random.normal(0, 0.05)  # CV ~5-10% (less reliable)
                for _ in range(repetitions)
            ]

        print(f"✓ Generated {num_solutions} solutions × {repetitions} reps × 3 metrics = "
              f"{num_solutions * repetitions * 3} measurements")

        return measurements

    def generate_controlled_complexity_data(self) -> Dict[str, Dict[str, List[float]]]:
        """
        Generate synthetic data for controlled complexity tasks.

        Used for Cohen's d calculation (O(n) vs O(n²) separation).

        Returns:
            complexity_data: {metric_name: {complexity_class: [values]}}
        """
        print("\n[SYNTHETIC DATA] Generating controlled complexity tasks...")

        num_per_class = self.config.controlled_tasks.problems_per_class

        complexity_data = {
            "CodeBLEU": {
                "O(n)": np.random.beta(6, 2, num_per_class).tolist(),  # Higher quality
                "O(n log n)": np.random.beta(4, 3, num_per_class).tolist(),
                "O(n²)": np.random.beta(2, 5, num_per_class).tolist(),  # Lower quality
            },
            "Runtime": {
                "O(n)": np.random.exponential(0.5, num_per_class).tolist(),  # Fast
                "O(n log n)": np.random.exponential(1.0, num_per_class).tolist(),
                "O(n²)": np.random.exponential(3.0, num_per_class).tolist(),  # Slow
            },
            "PR-style": {
                "O(n)": np.random.uniform(0.6, 1.0, num_per_class).tolist(),
                "O(n log n)": np.random.uniform(0.4, 0.7, num_per_class).tolist(),
                "O(n²)": np.random.uniform(0.1, 0.5, num_per_class).tolist(),
            }
        }

        print(f"✓ Generated {num_per_class} solutions per complexity class × 3 classes = "
              f"{num_per_class * 3} controlled tasks")

        return complexity_data

    def generate_cross_platform_data(
        self,
        measurements: Dict[str, Dict[str, List[List[float]]]]
    ) -> Dict[str, Tuple[List[float], List[float]]]:
        """
        Simulate cross-platform measurements.

        In real experiment: AWS GPU vs Local GPU
        In PoC: Add small noise to simulate platform differences

        Returns:
            platform_data: {metric_name: (platform1_ranks, platform2_ranks)}
        """
        print("\n[SYNTHETIC DATA] Generating cross-platform measurements...")

        platform_data = {}

        for metric_name, metric_measurements in measurements.items():
            # Platform 1: Original measurements (mean)
            platform1_means = [
                np.mean(reps) for reps in metric_measurements.values()
            ]

            # Platform 2: Add small platform noise (simulates different hardware)
            platform_noise_std = 0.02 if metric_name == "Runtime" else 0.05
            platform2_means = [
                val + np.random.normal(0, platform_noise_std)
                for val in platform1_means
            ]

            # Convert to ranks
            platform1_ranks = stats.rankdata(platform1_means)
            platform2_ranks = stats.rankdata(platform2_means)

            platform_data[metric_name] = (platform1_ranks.tolist(), platform2_ranks.tolist())

        print(f"✓ Generated cross-platform data for {len(platform_data)} metrics")

        return platform_data

    def compute_cv(self, measurements: Dict[str, Dict[str, List[List[float]]]]) -> Dict[str, float]:
        """
        Compute coefficient of variation for each metric.

        CV = (std / mean) × 100
        Threshold: ≤5%

        Returns:
            cv_results: {metric_name: mean_cv_percentage}
        """
        print("\n[ANALYSIS] Computing Coefficient of Variation (CV)...")

        cv_results = {}

        for metric_name, metric_measurements in measurements.items():
            cvs = []
            for sol_id, repetitions in metric_measurements.items():
                mean = np.mean(repetitions)
                std = np.std(repetitions, ddof=1)
                cv = (std / mean) * 100 if mean > 0 else 0
                cvs.append(cv)

            mean_cv = np.mean(cvs)
            cv_results[metric_name] = mean_cv

            threshold = self.config.thresholds.cv_max
            status = "✓ PASS" if mean_cv <= threshold else "✗ FAIL"
            print(f"  {metric_name}: {mean_cv:.2f}% (threshold: {threshold}%) {status}")

        return cv_results

    def compute_cohens_d(
        self,
        complexity_data: Dict[str, Dict[str, List[float]]]
    ) -> Dict[str, float]:
        """
        Compute Cohen's d effect size between O(n) and O(n²) complexity classes.

        d = (mean1 - mean2) / pooled_std
        Threshold: ≥0.8 (large effect)

        Returns:
            cohens_d_results: {metric_name: effect_size}
        """
        print("\n[ANALYSIS] Computing Cohen's d (complexity separation)...")

        cohens_d_results = {}

        for metric_name, complexity_values in complexity_data.items():
            group1 = np.array(complexity_values["O(n)"])
            group2 = np.array(complexity_values["O(n²)"])

            n1, n2 = len(group1), len(group2)
            var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
            pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

            d = abs(np.mean(group1) - np.mean(group2)) / pooled_std
            cohens_d_results[metric_name] = d

            threshold = self.config.thresholds.cohens_d_min
            status = "✓ PASS" if d >= threshold else "✗ FAIL"
            print(f"  {metric_name}: {d:.2f} (threshold: {threshold}) {status}")

        return cohens_d_results

    def compute_spearman_rho(
        self,
        platform_data: Dict[str, Tuple[List[float], List[float]]]
    ) -> Dict[str, Tuple[float, float]]:
        """
        Compute Spearman rank correlation between platforms.

        ρ = rank correlation coefficient
        Threshold: ≥0.8

        Returns:
            spearman_results: {metric_name: (rho, p_value)}
        """
        print("\n[ANALYSIS] Computing Spearman ρ (cross-platform stability)...")

        spearman_results = {}

        for metric_name, (ranks1, ranks2) in platform_data.items():
            rho, p_value = stats.spearmanr(ranks1, ranks2)
            spearman_results[metric_name] = (rho, p_value)

            threshold = self.config.thresholds.spearman_rho_min
            status = "✓ PASS" if rho >= threshold else "✗ FAIL"
            print(f"  {metric_name}: ρ={rho:.3f}, p={p_value:.4f} (threshold: {threshold}) {status}")

        return spearman_results

    def validate_gate(
        self,
        cv_results: Dict[str, float],
        cohens_d_results: Dict[str, float],
        spearman_results: Dict[str, Tuple[float, float]]
    ) -> Dict[str, bool]:
        """
        Validate MUST_WORK gate for each proxy.

        Gate pass condition: CV ≤5% AND Cohen's d ≥0.8 AND Spearman ρ ≥0.8

        Returns:
            gate_results: {metric_name: passed}
        """
        print("\n[GATE VALIDATION] Checking MUST_WORK criteria...")

        gate_results = {}

        for metric_name in cv_results.keys():
            cv_pass = cv_results[metric_name] <= self.config.thresholds.cv_max
            cohens_pass = cohens_d_results[metric_name] >= self.config.thresholds.cohens_d_min
            spearman_pass = spearman_results[metric_name][0] >= self.config.thresholds.spearman_rho_min

            all_pass = cv_pass and cohens_pass and spearman_pass
            gate_results[metric_name] = all_pass

            status = "✓ VALIDATED" if all_pass else "✗ FAILED"
            print(f"  {metric_name}: {status}")
            if not all_pass:
                failures = []
                if not cv_pass:
                    failures.append(f"CV={cv_results[metric_name]:.2f}%")
                if not cohens_pass:
                    failures.append(f"Cohen's d={cohens_d_results[metric_name]:.2f}")
                if not spearman_pass:
                    failures.append(f"Spearman ρ={spearman_results[metric_name][0]:.3f}")
                print(f"    Failed checks: {', '.join(failures)}")

        return gate_results

    def plot_gate_metrics(
        self,
        cv_results: Dict[str, float],
        cohens_d_results: Dict[str, float],
        spearman_results: Dict[str, Tuple[float, float]]
    ):
        """Generate mandatory gate metrics bar chart."""
        print("\n[VISUALIZATION] Generating gate metrics plot...")

        metrics = list(cv_results.keys())
        x = np.arange(len(metrics))
        width = 0.25

        fig, ax = plt.subplots(figsize=self.config.visualization.figsize)

        cv_values = [cv_results[m] / self.config.thresholds.cv_max for m in metrics]
        cohens_values = [cohens_d_results[m] / self.config.thresholds.cohens_d_min for m in metrics]
        spearman_values = [spearman_results[m][0] / self.config.thresholds.spearman_rho_min for m in metrics]

        ax.bar(x - width, cv_values, width, label='CV (normalized)',
               color=['green' if v <= 1.0 else 'red' for v in cv_values])
        ax.bar(x, cohens_values, width, label="Cohen's d (normalized)",
               color=['green' if v >= 1.0 else 'red' for v in cohens_values])
        ax.bar(x + width, spearman_values, width, label='Spearman ρ (normalized)',
               color=['green' if v >= 1.0 else 'red' for v in spearman_values])

        ax.axhline(y=1.0, color='black', linestyle='--', linewidth=0.5, label='Threshold (normalized)')
        ax.set_ylabel('Normalized Score (1.0 = threshold)')
        ax.set_xlabel('Proxy Metric')
        ax.set_title('H-E1 Gate Validation: Proxy Metric Reliability')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        output_path = self.figures_dir / "gate_metrics.png"
        plt.savefig(output_path, dpi=self.config.visualization.dpi, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved: {output_path}")

    def save_results(
        self,
        cv_results: Dict[str, float],
        cohens_d_results: Dict[str, float],
        spearman_results: Dict[str, Tuple[float, float]],
        gate_results: Dict[str, bool]
    ):
        """Save experiment results to JSON."""
        print("\n[OUTPUT] Saving results...")

        results = {
            "hypothesis_id": self.config.hypothesis_id,
            "experiment_name": self.config.experiment_name,
            "gate_type": "MUST_WORK",
            "measurements": {
                "cv": {k: float(v) for k, v in cv_results.items()},
                "cohens_d": {k: float(v) for k, v in cohens_d_results.items()},
                "spearman_rho": {k: float(v[0]) for k, v in spearman_results.items()},
                "spearman_p": {k: float(v[1]) for k, v in spearman_results.items()}
            },
            "thresholds": {
                "cv_max": float(self.config.thresholds.cv_max),
                "cohens_d_min": float(self.config.thresholds.cohens_d_min),
                "spearman_rho_min": float(self.config.thresholds.spearman_rho_min)
            },
            "gate_validation": {k: bool(v) for k, v in gate_results.items()},
            "validated_proxies": [k for k, v in gate_results.items() if v],
            "failed_proxies": [k for k, v in gate_results.items() if not v],
            "gate_verdict": "PASS" if any(gate_results.values()) else "FAIL"
        }

        output_path = self.output_dir / "results.json"
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"✓ Saved: {output_path}")

        return results

    def run(self):
        """Execute full PoC experiment."""
        print("=" * 80)
        print("H-E1 Proxy Metric Validation PoC")
        print("=" * 80)

        # Step 1: Generate synthetic measurements
        measurements = self.generate_synthetic_measurements()

        # Step 2: Generate controlled complexity data
        complexity_data = self.generate_controlled_complexity_data()

        # Step 3: Generate cross-platform data
        platform_data = self.generate_cross_platform_data(measurements)

        # Step 4: Compute reliability metrics
        cv_results = self.compute_cv(measurements)
        cohens_d_results = self.compute_cohens_d(complexity_data)
        spearman_results = self.compute_spearman_rho(platform_data)

        # Step 5: Validate gate
        gate_results = self.validate_gate(cv_results, cohens_d_results, spearman_results)

        # Step 6: Generate visualizations
        self.plot_gate_metrics(cv_results, cohens_d_results, spearman_results)

        # Step 7: Save results
        results = self.save_results(cv_results, cohens_d_results, spearman_results, gate_results)

        # Step 8: Print summary
        print("\n" + "=" * 80)
        print("EXPERIMENT COMPLETE")
        print("=" * 80)
        print(f"\nGate Verdict: {results['gate_verdict']}")
        print(f"Validated Proxies: {', '.join(results['validated_proxies']) if results['validated_proxies'] else 'None'}")
        print(f"Failed Proxies: {', '.join(results['failed_proxies']) if results['failed_proxies'] else 'None'}")

        return results


def main():
    """Main entry point."""
    config = ExperimentConfig()
    validate_config(config)

    poc = ProxyMetricPoC(config)
    results = poc.run()

    return results


if __name__ == "__main__":
    main()
