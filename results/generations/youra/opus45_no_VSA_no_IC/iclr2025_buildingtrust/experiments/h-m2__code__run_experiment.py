"""H-M2 Experiment: HaluEval vs TruthfulQA Correlation Analysis."""

import json
from pathlib import Path

from data import load_model_scores, validate_columns
from correlations import compute_halueval_correlations, bootstrap_ci, check_gate
from visualize import plot_correlation_heatmap, plot_scatter, plot_gate_metrics
from report import write_validation_report


def main():
    base_dir = Path(__file__).parent.parent
    h_m1_csv = base_dir.parent / "h-m1" / "code" / "data_cache" / "scores.csv"

    print(f"Loading data from {h_m1_csv}")
    df = load_model_scores(str(h_m1_csv))

    required_cols = ["model", "truthfulqa_mc2", "halueval_qa", "halueval_dialogue", "halueval_summarization"]
    validate_columns(df, required_cols)

    n_models = len(df)
    print(f"Loaded {n_models} models")
    assert n_models >= 30, f"Insufficient models: {n_models} < 30"

    # Compute correlations
    halueval_cols = ["halueval_qa", "halueval_dialogue", "halueval_summarization"]
    results = compute_halueval_correlations(df, "truthfulqa_mc2", halueval_cols)

    # Bootstrap CI for primary correlation
    halueval_agg = df[halueval_cols].mean(axis=1).values
    ci = bootstrap_ci(halueval_agg, df["truthfulqa_mc2"].values, n_bootstrap=1000)
    results["halueval_vs_truthfulqa_ci"] = ci

    # Gate check
    gate = check_gate(results)

    print(f"\n=== H-M2 Results ===")
    print(f"Primary: r(HaluEval, TruthfulQA) = {gate['r_cross']:.3f}")
    print(f"Intra-HaluEval mean: {gate['r_intra_mean']:.3f}")
    print(f"95% CI: [{ci[0]:.3f}, {ci[1]:.3f}]")
    print(f"Gate: {gate['status']}")

    # Generate figures
    figures_dir = base_dir / "figures"
    figures_dir.mkdir(exist_ok=True)

    all_cols = ["truthfulqa_mc2"] + halueval_cols
    plot_correlation_heatmap(df, all_cols, str(figures_dir / "correlation_heatmap.png"))
    plot_scatter(df, "halueval_qa", "truthfulqa_mc2", gate["r_cross"], str(figures_dir / "scatter_halueval_truthfulqa.png"))
    plot_gate_metrics(gate["r_cross"], gate["r_intra_mean"], gate["threshold"], str(figures_dir / "gate_metrics.png"))

    print(f"Figures saved to {figures_dir}")

    # Generate report
    report_path = base_dir / "04_validation.md"
    write_validation_report(results, gate, ci, n_models, str(report_path))
    print(f"Report saved to {report_path}")

    # Save JSON results
    results_dir = base_dir / "code" / "results"
    results_dir.mkdir(exist_ok=True)

    json_results = {
        "r_halueval_truthfulqa": gate["r_cross"],
        "r_intra_halueval_mean": gate["r_intra_mean"],
        "ci_95": list(ci),
        "gate_status": gate["status"],
        "primary_pass": gate["primary_pass"],
        "secondary_pass": gate["secondary_pass"],
        "n_models": n_models,
        "correlations": {k: list(v) if isinstance(v, tuple) else v for k, v in results.items()},
    }

    with open(results_dir / "h_m2_results.json", "w") as f:
        json.dump(json_results, f, indent=2)

    print("\nEXPERIMENT COMPLETE")
    return gate["status"]


if __name__ == "__main__":
    main()
