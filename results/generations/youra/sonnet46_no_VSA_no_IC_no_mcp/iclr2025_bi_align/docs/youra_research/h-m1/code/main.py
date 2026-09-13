"""H-M1: RLHF Proxy-Gold Divergence Mechanism Verification — main entry point."""
import sys
from pathlib import Path

from src.config import load_config
from src.data.loader import load_dataset
from src.analysis.trajectory import run_analysis
from src.visualization.plots import (
    plot_trajectory_dual_axis,
    plot_divergence_gap,
    plot_spearman_scatter,
    plot_gao_overlay,
    plot_gate_metrics,
)
from src.reporting.reporter import print_report, save_results, save_divergence_curve


def main() -> None:
    cfg = load_config("config.yaml")
    cfg.validate()

    # Load datasets
    coste_df = load_dataset(cfg.coste_csv_path, "Coste2023")
    try:
        gao_df = load_dataset(cfg.gao_csv_path, "Gao2023")
    except Exception as e:
        print(f"Warning: Gao dataset unavailable ({e}). Proceeding with Coste only.")
        gao_df = None

    # Primary analysis on Coste dataset
    results = run_analysis(coste_df, dataset_name="Coste2023")

    # Figures
    figs_dir = cfg.figures_dir
    plot_trajectory_dual_axis(coste_df, results, figs_dir, cfg.figure_dpi)
    plot_divergence_gap(
        coste_df["kl_budget"].values,
        results["divergence_curve"],
        figs_dir,
        cfg.figure_dpi,
    )
    plot_spearman_scatter(
        coste_df["kl_budget"].values,
        coste_df["rm_score"].values,
        results["rho_rm_kl"],
        results["p_rho"],
        figs_dir,
        cfg.figure_dpi,
    )
    if gao_df is not None:
        plot_gao_overlay(gao_df, figs_dir, cfg.figure_dpi)
    plot_gate_metrics(results, figs_dir, cfg.figure_dpi)

    # Report + save
    print_report(results)
    save_results(results, cfg.results_json_path, config_path="config.yaml")
    save_divergence_curve(coste_df, results["divergence_curve"], cfg.divergence_csv_path)

    sys.exit(0 if results["gate_pass"] else 1)


if __name__ == "__main__":
    main()
