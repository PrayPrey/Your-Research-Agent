"""H-E1: RLHF Dual-Signal Co-existence Verification pipeline."""
import sys
import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ExperimentConfig:
    coste_csv_path: str = "data/coste2023_kl_curves.csv"
    gao_csv_path: str = "data/gao2023_kl_curves.csv"
    figures_dir: str = "docs/youra_research/h-e1/figures"
    results_dir: str = "docs/youra_research/h-e1/results"
    results_filename: str = "h_e1_results.json"
    min_kl_levels: int = 5
    min_variation: float = 0.01
    figure_dpi: int = 150
    random_seed: int = 1

    def validate(self) -> None:
        for attr in ("coste_csv_path", "gao_csv_path"):
            p = Path(getattr(self, attr))
            if not p.exists():
                raise FileNotFoundError(f"Required input not found: {p}")


def load_config(path: str = "config.yaml") -> ExperimentConfig:
    cfg_path = Path(path)
    if not cfg_path.exists():
        return ExperimentConfig()
    with open(cfg_path) as f:
        data = yaml.safe_load(f) or {}
    return ExperimentConfig(**{k: v for k, v in data.items()
                               if k in ExperimentConfig.__dataclass_fields__})


def main() -> None:
    from src.data.loader import load_dataset
    from src.verification.coexistence import verify_signal_coexistence
    from src.visualization.plots import plot_dual_axis, plot_comparison
    from src.reporting.reporter import print_report, save_results

    cfg = load_config()
    cfg.validate()

    datasets = [
        (cfg.coste_csv_path, "Coste2023"),
        (cfg.gao_csv_path, "Gao2023"),
    ]

    dfs = []
    names = []
    for csv_path, name in datasets:
        df = load_dataset(csv_path, name)
        dfs.append(df)
        names.append(name)

    results = []
    for df, name in zip(dfs, names):
        res = verify_signal_coexistence(df, name)
        results.append(res)

    for df, name in zip(dfs, names):
        plot_dual_axis(df, name, cfg.figures_dir, dpi=cfg.figure_dpi)

    plot_comparison(results, dfs, names, cfg.figures_dir, dpi=cfg.figure_dpi)

    print_report(results)

    out_path = str(Path(cfg.results_dir) / cfg.results_filename)
    save_results(results, out_path)

    overall = all(r["passed"] for r in results)
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
