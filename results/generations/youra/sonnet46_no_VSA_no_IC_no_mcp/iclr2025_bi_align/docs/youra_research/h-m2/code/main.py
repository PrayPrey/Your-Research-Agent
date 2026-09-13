#!/usr/bin/env python3
"""H-M2: Calibration-Alignment Divergence Gap Verification."""

import sys
import argparse
from pathlib import Path

# Allow running from code/ directory
sys.path.insert(0, str(Path(__file__).parent))

from src.config import load_config
from src.data.loader import load_dataset
from src.analysis.normalizer import run_gap_analysis
from src.visualization.plots import (
    plot_gap_curve, plot_dual_line, plot_gap_scatter, plot_gate_metrics
)
from src.reporting.reporter import print_report, save_results, save_gap_curve
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="H-M2 gap analysis")
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    cfg.validate()

    print(f"Loading data from: {cfg.input_csv_path}")
    df = load_dataset(cfg.input_csv_path)
    print(f"  Loaded {len(df)} rows")

    print("Running gap analysis...")
    results = run_gap_analysis(df, high_kl_min_positive=cfg.high_kl_min_positive)

    print("Generating figures...")
    p1 = plot_gap_curve(results["kl"], results["gap"], results["high_kl_mask"],
                        results["max_gap"], cfg.figures_dir, cfg.figure_dpi)
    p2 = plot_dual_line(results["kl"], results["rm_norm"], results["gold"],
                        cfg.figures_dir, cfg.figure_dpi)
    p3 = plot_gap_scatter(results["kl"], results["gap"], results["rho_gap_kl"],
                          results["high_kl_mask"], cfg.figures_dir, cfg.figure_dpi)
    p4 = plot_gate_metrics(results, cfg.figures_dir, cfg.figure_dpi)
    print(f"  Figures: {p1}, {p2}, {p3}, {p4}")

    print_report(results)
    save_results(results, cfg.results_json_path)
    save_gap_curve(df, results["rm_norm"], results["gap"], cfg.gap_csv_path)

    sys.exit(0 if results["gate_pass"] else 1)


if __name__ == "__main__":
    main()
