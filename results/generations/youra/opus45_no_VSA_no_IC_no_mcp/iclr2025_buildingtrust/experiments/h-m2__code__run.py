"""Main entry point for h-m2 Pareto-Optimal ECE analysis."""

import json
import pandas as pd

from config import H_E1_SCORES, OUTPUT_PATH, FIGURES_PATH
from analysis import run_analysis
from visualize import plot_pareto_frontier, plot_ece_comparison


def main() -> dict:
    """Load scores.csv -> run_analysis -> plots -> save results.json."""
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    FIGURES_PATH.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(H_E1_SCORES)
    results = run_analysis(df)

    df_labeled = results.pop("df_with_labels")
    plot_pareto_frontier(df_labeled, results["pareto_models"],
                         FIGURES_PATH / "pareto_frontier.png")
    plot_ece_comparison(df_labeled, FIGURES_PATH / "ece_comparison.png")

    with open(OUTPUT_PATH / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=float)

    print(f"Gate passed: {results['gate_passed']}")
    print(f"Pareto models ({results['n_pareto']}): {results['pareto_models']}")
    print(f"t-test p-value: {results['ttest']['p']:.4f}")
    print(f"Cohen's d: {results['cohens_d']:.3f}")

    return results


if __name__ == "__main__":
    main()
