"""H-M3 main experiment: OLS regression slope significance test."""
import sys
from pathlib import Path

# Ensure src/ is importable when run from repo root or code/ dir
_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))

from config import load_config
from src.data.loader import load_dataset
from src.analysis.regression import fit_ols_regression, verify_mechanism_activated, check_gate
from src.visualization.plots import (
    plot_gate_metrics,
    plot_regression_scatter,
    plot_residuals,
    plot_bootstrap_histogram,
)
from src.reporting.reporter import print_report, save_results


def main() -> None:
    cfg = load_config()
    cfg.validate()

    kl_values, gap_values = load_dataset(
        cfg.input_csv_path,
        required_columns=cfg.required_columns,
        min_n=cfg.min_n,
    )

    results = fit_ols_regression(
        kl_values,
        gap_values,
        n_boot=cfg.n_boot,
        seed=cfg.random_seed,
    )

    verify_mechanism_activated(results)

    gate_pass, gate_reason = check_gate(results)
    results["gate_pass"]   = gate_pass
    results["gate_reason"] = gate_reason

    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)

    plot_gate_metrics(results, cfg.figures_dir, cfg.figure_dpi)
    plot_regression_scatter(kl_values, gap_values, results, cfg.figures_dir, cfg.figure_dpi)
    plot_residuals(kl_values, gap_values, results, cfg.figures_dir, cfg.figure_dpi)
    plot_bootstrap_histogram(results, cfg.figures_dir, cfg.figure_dpi)

    print_report(results)
    save_results(results, cfg.results_json_path)

    sys.exit(0 if gate_pass else 1)


if __name__ == "__main__":
    main()
