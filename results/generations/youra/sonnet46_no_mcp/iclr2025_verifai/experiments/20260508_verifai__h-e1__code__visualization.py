import os
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


class Visualizer:
    def __init__(self, figures_dir: str) -> None:
        self.figures_dir = figures_dir
        os.makedirs(figures_dir, exist_ok=True)
        sns.set_style("whitegrid")
        plt.rcParams.update({"font.size": 12})

    def _save(self, fig, name: str) -> None:
        base = os.path.join(self.figures_dir, name)
        fig.savefig(base + ".pdf", bbox_inches="tight")
        fig.savefig(base + ".png", dpi=150, bbox_inches="tight")
        plt.close(fig)

    def plot_gate_metrics(self, metrics: dict, save_path: str = None) -> None:
        """3-panel bar chart of gate metrics vs thresholds."""
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))

        items = [
            ("Δ_ast", metrics.get("delta_ast", 0), 0.0, metrics.get("gate_checks", {}).get("delta_ast_pass", False)),
            ("z3_rate", metrics.get("z3_eligibility_rate", 0), 0.15, metrics.get("gate_checks", {}).get("z3_rate_pass", False)),
            ("mypy_rate", metrics.get("mypy_structured_rate", 0), 0.90, metrics.get("gate_checks", {}).get("mypy_rate_pass", False)),
        ]

        for ax, (label, value, threshold, passed) in zip(axes, items):
            color = "green" if passed else "red"
            ax.bar([label], [value], color=color, alpha=0.7)
            ax.axhline(y=threshold, color="black", linestyle="--", label=f"threshold={threshold}")
            status = "PASS" if passed else "FAIL"
            ax.set_title(f"{label}\n{status}")
            ax.legend(fontsize=8)

        fig.suptitle(f"Gate Metrics — {'PASS' if metrics.get('gate_pass') else 'FAIL'}", fontsize=14)
        fig.tight_layout()
        self._save(fig, "gate_metrics")

    def plot_ast_failure_heatmap(
        self,
        baseline_rates: Dict[str, float],
        syncode_rates: Dict[str, float],
        save_path: str = None,
    ) -> None:
        """Per-problem ast failure rate: baseline vs syncode."""
        task_ids = list(baseline_rates.keys())[:50]  # Limit to 50 for readability
        b_vals = [baseline_rates.get(t, 0) for t in task_ids]
        s_vals = [syncode_rates.get(t, 0) for t in task_ids]

        data = np.array([b_vals, s_vals])
        fig, ax = plt.subplots(figsize=(16, 3))
        im = ax.imshow(data, aspect="auto", cmap="RdYlGn_r", vmin=0, vmax=1)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["Baseline", "SynCode"])
        ax.set_xlabel("Problem index (first 50)")
        ax.set_title("AST Parse Failure Rate per Problem")
        plt.colorbar(im, ax=ax, label="Failure rate")
        fig.tight_layout()
        self._save(fig, "ast_failure_heatmap")

    def plot_z3_eligibility(
        self, eligibility: Dict[str, bool], save_path: str = None
    ) -> None:
        """Bar chart of eligible vs non-eligible problems."""
        eligible = sum(1 for v in eligibility.values() if v)
        non_eligible = len(eligibility) - eligible

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["Z3-Eligible", "Non-Eligible"], [eligible, non_eligible],
               color=["green", "gray"], alpha=0.7)
        ax.set_ylabel("Problem count")
        ax.set_title(f"Z3 Eligibility (rate={eligible/len(eligibility):.2%})")
        fig.tight_layout()
        self._save(fig, "z3_eligibility")

    def plot_mypy_error_types(
        self, mypy_results: dict, save_path: str = None
    ) -> None:
        """Distribution of mypy error codes across checked samples."""
        from collections import Counter
        error_codes: Counter = Counter()

        for r in mypy_results.values():
            for err in r.get("parsed_errors", []):
                code = err.get("error_code") or "unknown"
                error_codes[code] += 1

        if not error_codes:
            error_codes["no_errors"] = len(mypy_results)

        labels = [k for k, _ in error_codes.most_common(10)]
        counts = [error_codes[k] for k in labels]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(labels, counts, color="steelblue", alpha=0.7)
        ax.set_xlabel("Error code")
        ax.set_ylabel("Count")
        ax.set_title("mypy Error Type Distribution")
        plt.xticks(rotation=30, ha="right")
        fig.tight_layout()
        self._save(fig, "mypy_error_types")

    def save_all(
        self,
        metrics: dict,
        pools: dict,
        eligibility: dict,
        mypy_results: dict,
    ) -> None:
        """Generate and save all four figures."""
        # Compute per-problem AST failure rates for heatmap
        import ast as ast_module

        def per_problem_ast_rate(pool: Dict[str, List[str]]) -> Dict[str, float]:
            rates = {}
            for task_id, completions in pool.items():
                if not completions:
                    rates[task_id] = 0.0
                    continue
                fails = sum(
                    1 for c in completions
                    if _parse_fails(c)
                )
                rates[task_id] = fails / len(completions)
            return rates

        def _parse_fails(code: str) -> bool:
            try:
                ast_module.parse(code)
                return False
            except SyntaxError:
                return True

        baseline_pool = pools.get("baseline", {})
        syncode_pool = pools.get("syncode", {})

        baseline_rates = per_problem_ast_rate(baseline_pool)
        syncode_rates = per_problem_ast_rate(syncode_pool)

        self.plot_gate_metrics(metrics)
        self.plot_ast_failure_heatmap(baseline_rates, syncode_rates)
        self.plot_z3_eligibility(eligibility)
        self.plot_mypy_error_types(mypy_results)

        print(f"  Figures saved to: {self.figures_dir}")
