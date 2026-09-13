from __future__ import annotations
import json
import logging
import os
from dataclasses import asdict

import pandas as pd

from config import Config, load_config
from data_loader import DataLoader
from ngram_extractor import NgramExtractor
from pile_query import PileQuery
from stats_analyzer import StatsAnalyzer
from visualizer import Visualizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_primary(config: Config) -> dict:
    """Full pipeline: load -> query Pile -> stats -> visualize -> assert gate.
    Returns: {"rates_df": pd.DataFrame, "stats": dict, "labels": dict[str, list[int]]}"""
    logger.info("=== Phase 1: Loading benchmark datasets ===")
    loader = DataLoader(config)
    extractor = NgramExtractor(config)
    querier = PileQuery(config, extractor)
    analyzer = StatsAnalyzer(config)
    viz = Visualizer(config)

    subtask_texts = loader.load_all()
    logger.info(f"Loaded {len(subtask_texts)} sub-tasks, total items: {sum(len(v) for v in subtask_texts.values())}")

    logger.info(f"=== Phase 2: Querying Pile index (mode={querier.mode}) ===")
    labels = querier.query_all(subtask_texts)

    logger.info("=== Phase 3: Statistical analysis ===")
    rates_df = analyzer.compute_rates(labels)
    stats = analyzer.kruskal_wallis(labels)
    logger.info(f"Kruskal-Wallis H={stats['kruskal_stat']:.4f}, p={stats['p_value']:.6f}")
    logger.info(f"Gate: {'PASS' if stats['gate_pass'] else 'FAIL'}")

    logger.info("=== Phase 4: Generating figures ===")
    os.makedirs(config.figures_dir, exist_ok=True)
    viz.save_all(rates_df, stats)

    logger.info("=== Phase 5: Gate assertion ===")
    analyzer.assert_gate(stats["p_value"])

    return {"rates_df": rates_df, "stats": stats, "labels": labels}


def run_sensitivity(config: Config, primary_rates: pd.DataFrame) -> dict:
    """Repeat pipeline with question-only format; compute Spearman vs primary.
    Returns: {"sensitivity_rates_df": pd.DataFrame, "rho": float, "p_value": float}"""
    logger.info("=== Sensitivity Analysis (question-only format) ===")
    sens_config = Config(**{**asdict(config), "text_format": "question_only"})

    loader = DataLoader(sens_config)
    extractor = NgramExtractor(sens_config)
    querier = PileQuery(sens_config, extractor)
    analyzer = StatsAnalyzer(sens_config)
    viz = Visualizer(sens_config)

    subtask_texts = loader.load_all()
    labels = querier.query_all(subtask_texts)
    sens_rates_df = analyzer.compute_rates(labels)

    # Align on common subtasks for Spearman
    merged = primary_rates.set_index("subtask")[["rate"]].join(
        sens_rates_df.set_index("subtask")[["rate"]],
        lsuffix="_primary",
        rsuffix="_sens",
    ).dropna()

    rho, p = analyzer.spearman_correlation(merged["rate_primary"], merged["rate_sens"])
    logger.info(f"Sensitivity Spearman rho={rho:.4f}, p={p:.6f}")
    viz.plot_sensitivity_scatter(merged["rate_primary"], merged["rate_sens"], rho)

    return {"sensitivity_rates_df": sens_rates_df, "rho": rho, "p_value": p}


def save_results(rates_df: pd.DataFrame, stats: dict, config: Config) -> None:
    """Writes contamination_rates.csv and statistical_tests.json to results/."""
    os.makedirs(config.results_dir, exist_ok=True)

    csv_path = os.path.join(config.results_dir, "contamination_rates.csv")
    rates_df.to_csv(csv_path, index=False)
    logger.info(f"Saved contamination rates: {csv_path}")

    json_path = os.path.join(config.results_dir, "statistical_tests.json")
    # Convert any non-serializable values
    serializable_stats = {}
    for k, v in stats.items():
        if isinstance(v, dict):
            serializable_stats[k] = v
        else:
            try:
                json.dumps(v)
                serializable_stats[k] = v
            except (TypeError, ValueError):
                serializable_stats[k] = str(v)

    with open(json_path, "w") as f:
        json.dump(serializable_stats, f, indent=2)
    logger.info(f"Saved statistical tests: {json_path}")


def main() -> None:
    """Entry point: load_config -> run_primary -> run_sensitivity -> save_results."""
    logger.info("=== H-E1 Experiment: Cross-Sub-Task Contamination Variance ===")
    config = load_config()

    primary = run_primary(config)
    sensitivity = run_sensitivity(config, primary["rates_df"])

    all_stats = {
        **primary["stats"],
        "sensitivity": {
            "rho": sensitivity["rho"],
            "p_value": sensitivity["p_value"],
        },
    }
    save_results(primary["rates_df"], all_stats, config)

    logger.info("=== EXPERIMENT COMPLETE ===")
    logger.info(f"Gate result: {'PASS' if primary['stats']['gate_pass'] else 'FAIL'}")
    logger.info(f"Kruskal-Wallis p={primary['stats']['p_value']:.6f}")
    logger.info(f"Sensitivity Spearman rho={sensitivity['rho']:.4f}")


if __name__ == "__main__":
    main()
