from __future__ import annotations
import copy
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from config import Config, load_config
from corpus_indexer import CorpusIndexer
from data_loader import DataLoader
from matrix_builder import MatrixBuilder
from ngram_extractor import NgramExtractor
from stats_analyzer import StatsAnalyzer, WIMBD_REFERENCE
from visualizer import Visualizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def build_indices(config: Config, extractor: NgramExtractor) -> dict:
    """Build or load MinHash LSH indices for all 3 corpora."""
    indexer = CorpusIndexer(config, extractor)
    indices = {}
    for corpus_name in ["pile", "c4", "redpajama"]:
        logger.info(f"=== Loading/building index: {corpus_name} ===")
        indices[corpus_name] = indexer.load_or_build(corpus_name)
    return indices, indexer


def run_primary(config: Config) -> tuple[pd.DataFrame, pd.DataFrame, dict, dict]:
    """Full pipeline: load benchmarks → build indices → build matrix → stats → visualize."""
    logger.info("=== Phase 1: Loading benchmark datasets ===")
    loader = DataLoader(config)
    extractor = NgramExtractor(config)
    benchmarks = loader.load_all()
    logger.info(f"Loaded {len(benchmarks)} sub-tasks, {sum(len(v) for v in benchmarks.values())} total items")

    logger.info("=== Phase 2: Building corpus indices ===")
    indices, indexer = build_indices(config, extractor)

    logger.info("=== Phase 3: Building 59×3 contamination matrix ===")
    builder = MatrixBuilder(config, extractor)
    matrix_df = builder.build_matrix(benchmarks, indices)
    matrix_wide = builder.to_wide(matrix_df)

    logger.info("=== Phase 4: Statistical analysis ===")
    analyzer = StatsAnalyzer(config)
    stats = analyzer.kruskal_wallis(matrix_wide)

    # WIMBD consistency check
    wimbd_rho, wimbd_p = float("nan"), float("nan")
    try:
        wimbd_rho, wimbd_p = analyzer.spearman_wimbd(matrix_wide["pile"], WIMBD_REFERENCE)
    except AssertionError as e:
        logger.warning(f"WIMBD consistency check failed: {e}")

    # Dunn post-hoc
    dunn_df = analyzer.dunn_posthoc(matrix_wide)

    logger.info("=== Phase 5: Generating figures ===")
    viz = Visualizer(config)
    viz.plot_corpus_comparison_bar(matrix_wide, stats["kruskal_H"], stats["kruskal_p"])
    viz.plot_contamination_heatmap(matrix_wide)
    viz.plot_corpus_pair_differences(matrix_wide)
    viz.plot_wimbd_consistency_scatter(matrix_wide["pile"], WIMBD_REFERENCE, wimbd_rho)
    viz.plot_per_corpus_rankings(matrix_wide)
    viz.plot_dunn_posthoc_heatmap(dunn_df)

    extra = {
        "wimbd_consistency": {"spearman_rho": wimbd_rho, "p_value": wimbd_p},
        "dunn_posthoc": dunn_df.values.tolist(),
        "c4_sampled": indexer.is_sampled("c4"),
        "rp_sampled": indexer.is_sampled("redpajama"),
    }
    return matrix_df, matrix_wide, stats, extra, indices, extractor


def run_sensitivity(
    config: Config, indices: dict, extractor: NgramExtractor, primary_matrix_wide: pd.DataFrame
) -> dict:
    """Repeat matrix build with question-only text format; run stats comparison."""
    logger.info("=== Sensitivity Analysis (question-only format) ===")
    sens_config = copy.copy(config)
    sens_config.text_format = "question_only"
    sens_loader = DataLoader(sens_config)
    benchmarks_sens = sens_loader.load_all()
    builder = MatrixBuilder(sens_config, extractor)
    matrix_sens = builder.build_matrix(benchmarks_sens, indices)
    matrix_wide_sens = builder.to_wide(matrix_sens)
    analyzer = StatsAnalyzer(sens_config)
    return analyzer.sensitivity_analysis(primary_matrix_wide, matrix_wide_sens)


def save_results(matrix_df: pd.DataFrame, stats: dict, extra: dict, sensitivity: dict, config: Config) -> None:
    """Write results/contamination_matrix.csv and results/statistical_tests.json."""
    Path(config.results_dir).mkdir(parents=True, exist_ok=True)
    csv_path = Path(config.results_dir) / "contamination_matrix.csv"
    matrix_df.to_csv(csv_path, index=False)
    logger.info(f"Saved matrix CSV: {csv_path}")

    output = {
        "hypothesis_id": "h-m1",
        "gate": {
            "type": "MUST_WORK",
            "threshold": config.gate_p_threshold,
            "pass": stats["gate_pass"],
            "p_value": stats["kruskal_p"],
        },
        "kruskal_wallis": {"H": stats["kruskal_H"], "p": stats["kruskal_p"]},
        "corpus_means": stats["corpus_means"],
        "max_pair_diff_pp": stats["max_pair_diff_pp"],
        "wimbd_consistency": extra.get("wimbd_consistency", {}),
        "sensitivity": sensitivity.get("format_spearman_rho", {}),
        "sensitivity_kruskal_p": sensitivity.get("sensitivity_kruskal_p"),
        "c4_sampled": extra.get("c4_sampled", False),
        "rp_sampled": extra.get("rp_sampled", False),
        "dunn_posthoc": extra.get("dunn_posthoc", []),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    json_path = Path(config.results_dir) / "statistical_tests.json"
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2)
    logger.info(f"Saved stats JSON: {json_path}")


def main() -> None:
    """Entry: load_config → run_primary → run_sensitivity → save_results → assert_gate."""
    config = load_config()
    Path(config.results_dir).mkdir(parents=True, exist_ok=True)
    Path(config.figures_dir).mkdir(parents=True, exist_ok=True)
    Path(config.indices_dir).mkdir(parents=True, exist_ok=True)

    matrix_df, matrix_wide, stats, extra, indices, extractor = run_primary(config)
    sensitivity = run_sensitivity(config, indices, extractor, matrix_wide)
    save_results(matrix_df, stats, extra, sensitivity, config)

    logger.info(f"=== EXPERIMENT COMPLETE ===")
    logger.info(f"Gate: {'PASS' if stats['gate_pass'] else 'FAIL'}")
    logger.info(f"Kruskal-Wallis H={stats['kruskal_H']:.4f}, p={stats['kruskal_p']:.6e}")
    logger.info(f"Max pair diff: {stats['max_pair_diff_pp']:.2f} pp")

    analyzer = StatsAnalyzer(config)
    analyzer.assert_gate(stats["kruskal_p"])


if __name__ == "__main__":
    main()
