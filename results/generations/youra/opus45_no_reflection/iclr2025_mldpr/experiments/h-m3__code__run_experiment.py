#!/usr/bin/env python3
"""Main experiment runner for H-M3: Researcher Attention Shift."""

import json
import logging
import os
import sys
from datetime import datetime
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, (np.bool_,)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

from config import ExperimentConfig, SPLIT_DATE
from data_collection import collect_paper_counts
from classifier import label_dataframe
from analysis import analyze_attention_shift, run_ablation_time_windows
from visualization import (
    plot_gate_metrics,
    plot_share_timeline,
    plot_absolute_counts,
    plot_benchmark_heatmap,
    plot_chi_square_residuals,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("experiment.log"),
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Run H-M3 experiment: Researcher Attention Shift analysis."""
    logger.info("=" * 60)
    logger.info("H-M3: Researcher Attention Shift Experiment")
    logger.info("=" * 60)

    config = ExperimentConfig()

    os.makedirs("outputs", exist_ok=True)
    os.makedirs(config.viz.output_dir, exist_ok=True)

    logger.info("Step 1: Collecting paper counts from PWC/HuggingFace...")
    df = collect_paper_counts(retries=config.data.retries)
    logger.info(f"Collected {len(df)} raw records")

    logger.info("Step 2: Labeling benchmarks...")
    df = label_dataframe(df)

    emergent_count = len(df[df["category"] == "emergent"])
    traditional_count = len(df[df["category"] == "traditional"])
    unknown_count = len(df[df["category"] == "unknown"])
    logger.info(f"Categories: {emergent_count} emergent, {traditional_count} traditional, {unknown_count} unknown")

    logger.info("Step 3: Analyzing attention shift...")
    result = analyze_attention_shift(df, SPLIT_DATE)

    logger.info("Step 4: Running ablation analysis...")
    ablation_results = run_ablation_time_windows(df)

    logger.info("Step 5: Generating visualizations...")

    figures_dir = config.viz.output_dir

    plot_gate_metrics(result, f"{figures_dir}/gate_metrics.png", config)
    logger.info(f"Generated: {figures_dir}/gate_metrics.png")

    plot_share_timeline(df, f"{figures_dir}/share_timeline.png", config)
    logger.info(f"Generated: {figures_dir}/share_timeline.png")

    plot_absolute_counts(df, f"{figures_dir}/absolute_counts.png", config)
    logger.info(f"Generated: {figures_dir}/absolute_counts.png")

    plot_benchmark_heatmap(df, f"{figures_dir}/benchmark_heatmap.png", config)
    logger.info(f"Generated: {figures_dir}/benchmark_heatmap.png")

    plot_chi_square_residuals(result, f"{figures_dir}/chi_square_residuals.png", config)
    logger.info(f"Generated: {figures_dir}/chi_square_residuals.png")

    logger.info("Step 6: Determining gate decision...")

    share_increase = result["share_increase"] > 0
    chi_significant = result["p_value"] < config.analysis.chi_square_alpha

    gate_pass = share_increase and chi_significant

    logger.info(f"Primary Metrics:")
    logger.info(f" - Pre-2021 emergent share: {result['pre_2021_emergent_share']:.2%}")
    logger.info(f" - Post-2021 emergent share: {result['post_2021_emergent_share']:.2%}")
    logger.info(f" - Share increase: {result['share_increase']:+.2%} (threshold: > 0)")
    logger.info(f" - Chi-square statistic: {result['chi2_statistic']:.2f}")
    logger.info(f" - P-value: {result['p_value']:.2e} (threshold: < 0.05)")
    logger.info(f"")
    logger.info(f"Secondary Metrics:")
    logger.info(f" - Emergent 2024 count: {result['emergent_2024_count']}")
    logger.info(f" - Traditional 2024 count: {result['traditional_2024_count']}")
    logger.info(f" - Emergent exceeds traditional (2024): {result['emergent_exceeds_traditional_2024']}")

    final_result = {
        "hypothesis_id": "h-m3",
        "hypothesis_type": "MECHANISM",
        "gate_type": "SHOULD_WORK",
        "timestamp": datetime.now().isoformat(),
        "gate_result": "PASS" if gate_pass else "FAIL",
        "gate_criteria": {
            "share_increase": {
                "value": float(result["share_increase"]),
                "threshold": "> 0",
                "passed": bool(share_increase),
            },
            "chi_square_significance": {
                "value": float(result["p_value"]),
                "threshold": "< 0.05",
                "passed": bool(chi_significant),
            },
        },
        "primary_metrics": {
            "pre_2021_emergent_share": float(result["pre_2021_emergent_share"]),
            "post_2021_emergent_share": float(result["post_2021_emergent_share"]),
            "share_increase": float(result["share_increase"]),
            "chi2_statistic": float(result["chi2_statistic"]),
            "p_value": float(result["p_value"]),
        },
        "secondary_metrics": {
            "emergent_2024_count": int(result["emergent_2024_count"]),
            "traditional_2024_count": int(result["traditional_2024_count"]),
            "emergent_exceeds_traditional_2024": bool(result["emergent_exceeds_traditional_2024"]),
        },
        "ablation_results": {k: {kk: (float(vv) if isinstance(vv, (int, float)) else bool(vv) if isinstance(vv, bool) else vv) for kk, vv in v.items()} for k, v in ablation_results.items()},
        "data_summary": {
            "total_records": len(df),
            "emergent_records": int(emergent_count),
            "traditional_records": int(traditional_count),
            "unknown_records": int(unknown_count),
        },
    }

    with open("outputs/results.json", "w") as f:
        json.dump(final_result, f, indent=2, cls=NumpyEncoder)
    logger.info("Saved: outputs/results.json")

    df.to_csv("outputs/results.csv", index=False)
    logger.info("Saved: outputs/results.csv")

    logger.info("")
    logger.info("=" * 60)
    logger.info(f"GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")
    logger.info("=" * 60)

    if gate_pass:
        logger.info("Hypothesis H-M3 PASSED: Researcher attention shifted to emergent benchmarks post-2021")
    else:
        logger.info("Hypothesis H-M3 FAILED: Attention shift not statistically significant")

    return final_result


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result["gate_result"] == "PASS" else 1)
