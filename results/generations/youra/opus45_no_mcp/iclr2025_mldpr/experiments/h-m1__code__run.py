"""Pipeline orchestration for H-M1 bibliometric study."""
import logging
import json
import os

from config import CONFIG
from openml_client import fetch_vision_datasets, select_high_low_groups
from semantic_scholar_client import count_optimization_papers
from aggregate import build_dataset_records, save_records
from stats import compute_ratio, mannwhitney_test, spearman_correlation
from gate import evaluate_gate, write_gate_report
from visualize import (
    plot_gate_comparison,
    plot_per_dataset_bars,
    plot_boxplot,
    plot_correlation_scatter,
)


def main() -> dict:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    logging.info("Step 1: Fetching vision datasets from OpenML...")
    df_meta = fetch_vision_datasets()
    logging.info(f"Found {len(df_meta)} vision datasets")

    high, low = select_high_low_groups(df_meta)
    logging.info(f"Selected {len(high)} high-use and {len(low)} low-use datasets")

    logging.info("Step 2: Querying Semantic Scholar for paper counts...")
    for i, d in enumerate(high):
        d["paper_count"] = count_optimization_papers(d["name"])
        logging.info(f"  High [{i+1}/{len(high)}] {d['name']}: {d['paper_count']} papers")

    for i, d in enumerate(low):
        d["paper_count"] = count_optimization_papers(d["name"])
        logging.info(f"  Low [{i+1}/{len(low)}] {d['name']}: {d['paper_count']} papers")

    logging.info("Step 3: Building aggregated records...")
    df = build_dataset_records(high, low)
    save_records(df, os.path.join(CONFIG.results_dir, "dataset_records.csv"))

    logging.info("Step 4: Computing statistics...")
    ratio_result = compute_ratio(df)
    mw_result = mannwhitney_test(df)
    corr_result = spearman_correlation(df)

    logging.info(f"  Ratio: {ratio_result['ratio']:.2f} (high_avg={ratio_result['high_use_avg']:.1f}, low_avg={ratio_result['low_use_avg']:.1f})")
    logging.info(f"  Mann-Whitney p-value: {mw_result['p_value']:.4f}")
    logging.info(f"  Spearman rho: {corr_result['rho']:.3f}")

    logging.info("Step 5: Evaluating gate...")
    gate_result = evaluate_gate(ratio_result, mw_result)
    write_gate_report(gate_result, os.path.join(CONFIG.results_dir, "gate_report.json"))

    logging.info("Step 6: Generating visualizations...")
    plot_gate_comparison(ratio_result, os.path.join(CONFIG.figures_dir, "gate_comparison.png"))
    plot_per_dataset_bars(df, os.path.join(CONFIG.figures_dir, "per_dataset_bars.png"))
    plot_boxplot(df, os.path.join(CONFIG.figures_dir, "boxplot.png"))
    plot_correlation_scatter(df, corr_result, os.path.join(CONFIG.figures_dir, "correlation_scatter.png"))

    gate_status = "PASS" if gate_result["pass_gate"] else "FAIL"
    logging.info(f"Gate Result: {gate_status}")
    logging.info(f"  Ratio: {gate_result['ratio']:.2f} (threshold: {gate_result['ratio_threshold']})")
    logging.info(f"  p-value: {gate_result['p_value']:.4f} (threshold: {gate_result['p_threshold']})")

    experiment_results = {
        "gate_result": gate_result,
        "ratio_result": ratio_result,
        "mw_result": mw_result,
        "corr_result": corr_result,
        "datasets": {"high": high, "low": low},
    }

    with open(os.path.join(CONFIG.results_dir, "experiment_results.json"), "w") as f:
        json.dump(experiment_results, f, indent=2)

    return experiment_results


if __name__ == "__main__":
    main()
