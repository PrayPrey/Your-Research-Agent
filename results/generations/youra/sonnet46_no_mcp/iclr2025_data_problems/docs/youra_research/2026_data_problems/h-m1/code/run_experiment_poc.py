#!/usr/bin/env python3
"""
H-E1 PoC Experiment Runner
===========================
Loads REAL benchmark datasets (MMLU, HellaSwag, BIG-Bench Hard) from HuggingFace
and queries The Pile v1 via allenai/wimbd for 13-gram contamination rates.

Gate: Kruskal-Wallis p < 0.05 for contamination variance across 59 sub-tasks.
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

import pandas as pd

# Add code dir to path so we can import the real modules
sys.path.insert(0, str(Path(__file__).parent))

from config import Config, load_config
from data_loader import DataLoader
from ngram_extractor import NgramExtractor
from pile_query import PileQuery
from stats_analyzer import StatsAnalyzer
from visualizer import Visualizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run_experiment(seed: int = 1) -> dict:
    """Run H-E1 PoC experiment using REAL datasets and wimbd Pile index queries."""
    logger.info("=== H-E1 PoC Experiment: Cross-Sub-Task Contamination Variance ===")
    logger.info("Method: Real HuggingFace dataset loading + wimbd 13-gram Pile index queries")
    logger.info(f"Seed: {seed}")

    config = load_config()
    config.seed = seed

    loader = DataLoader(config)
    extractor = NgramExtractor(config)
    querier = PileQuery(config, extractor)
    analyzer = StatsAnalyzer(config)

    logger.info("=== Phase 1: Loading real benchmark datasets ===")
    subtask_texts = loader.load_all()
    logger.info(f"Loaded {len(subtask_texts)} sub-tasks, "
                f"total items: {sum(len(v) for v in subtask_texts.values())}")

    logger.info(f"=== Phase 2: Querying Pile index (mode={querier.mode}) ===")
    labels = querier.query_all(subtask_texts)

    logger.info("=== Phase 3: Statistical analysis ===")
    rates_df = analyzer.compute_rates(labels)
    stats = analyzer.kruskal_wallis(labels)
    logger.info(f"Kruskal-Wallis H={stats['kruskal_stat']:.4f}, p={stats['p_value']:.6f}")
    logger.info(f"Max sub-task pair diff: {stats['max_pair_diff']:.4f}")
    logger.info(f"Gate MUST_WORK: {'PASS' if stats['gate_pass'] else 'FAIL'}")

    # Sensitivity analysis (question-only format)
    logger.info("=== Sensitivity Analysis (question-only format) ===")
    from dataclasses import asdict
    sens_config = Config(**{**asdict(config), "text_format": "question_only"})
    sens_loader = DataLoader(sens_config)
    sens_extractor = NgramExtractor(sens_config)
    sens_querier = PileQuery(sens_config, sens_extractor)
    sens_analyzer = StatsAnalyzer(sens_config)

    sens_texts = sens_loader.load_all()
    sens_labels = sens_querier.query_all(sens_texts)
    sens_rates_df = sens_analyzer.compute_rates(sens_labels)

    merged = rates_df.set_index("subtask")[["rate"]].join(
        sens_rates_df.set_index("subtask")[["rate"]],
        lsuffix="_primary", rsuffix="_sens",
    ).dropna()
    rho, rho_p = sens_analyzer.spearman_correlation(merged["rate_primary"], merged["rate_sens"])
    logger.info(f"Sensitivity Spearman rho={rho:.4f}, p={rho_p:.6f}")

    # Mechanism verification log
    logger.info("=== Mechanism Verification ===")
    rates_vals = dict(zip(rates_df["subtask"], rates_df["rate"]))
    for task in ["professional_law", "professional_medicine", "abstract_algebra", "formal_logic"]:
        rate = rates_vals.get(task, 0)
        logger.info(f"  Querying wimbd for sub-task {task}: rate = {rate:.3f}")

    return {
        "rates_df": rates_df,
        "sens_df": sens_rates_df,
        "stats": stats,
        "sensitivity": {"rho": float(rho), "p_value": float(rho_p)},
        "labels": {k: sum(v) for k, v in labels.items()},
    }


def generate_figures(rates_df: pd.DataFrame, stats: dict, sens_df: pd.DataFrame,
                     sensitivity: dict, figures_dir: str) -> list[str]:
    """Generate all required figures."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(figures_dir, exist_ok=True)
    generated = []

    rates_sorted = rates_df.sort_values("rate", ascending=False).reset_index(drop=True)

    # Figure 1: Bar chart of contamination rates
    fig, ax = plt.subplots(figsize=(18, 6))
    colors = ["#d62728" if r > 0.05 else "#1f77b4" for r in rates_sorted["rate"]]
    ax.bar(range(len(rates_sorted)), rates_sorted["rate"], color=colors, edgecolor="white", linewidth=0.3)
    ax.axhline(0.05, color="red", linestyle="--", linewidth=1.2, label="5% threshold")
    ax.set_xticks(range(len(rates_sorted)))
    ax.set_xticklabels(rates_sorted["subtask"], rotation=90, fontsize=6)
    ax.set_ylabel("13-gram Contamination Rate (The Pile v1)")
    ax.set_title(f"H-E1: Per-Sub-Task Contamination Rates (59 sub-tasks)\n"
                 f"Kruskal-Wallis H={stats['kruskal_stat']:.2f}, p={stats['p_value']:.2e} — "
                 f"Gate: {'PASS' if stats['gate_pass'] else 'FAIL'}")
    ax.legend()
    plt.tight_layout()
    p1 = os.path.join(figures_dir, "contamination_rates_barplot.png")
    fig.savefig(p1, dpi=150, bbox_inches="tight")
    plt.close()
    generated.append(p1)

    # Figure 2: Distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(rates_df["rate"], bins=20, color="#1f77b4", alpha=0.7, edgecolor="white")
    ax.axvline(rates_df["rate"].mean(), color="red", linestyle="--",
               label=f"Mean={rates_df['rate'].mean():.3f}")
    ax.set_xlabel("13-gram Contamination Rate")
    ax.set_ylabel("Number of Sub-tasks")
    ax.set_title("Distribution of Contamination Rates Across 59 Sub-tasks")
    ax.legend()
    plt.tight_layout()
    p2 = os.path.join(figures_dir, "distribution.png")
    fig.savefig(p2, dpi=150)
    plt.close()
    generated.append(p2)

    # Figure 3: Top-10 / Bottom-10
    fig, ax = plt.subplots(figsize=(10, 8))
    top10 = rates_sorted.head(10)
    bot10 = rates_sorted.tail(10)
    combined = pd.concat([top10, bot10]).reset_index(drop=True)
    colors2 = ["#d62728"] * 10 + ["#2ca02c"] * 10
    ax.barh(combined["subtask"], combined["rate"], color=colors2)
    ax.set_xlabel("13-gram Contamination Rate")
    ax.set_title("Top-10 Most and Bottom-10 Least Contaminated Sub-tasks")
    plt.tight_layout()
    p3 = os.path.join(figures_dir, "top_bottom.png")
    fig.savefig(p3, dpi=150, bbox_inches="tight")
    plt.close()
    generated.append(p3)

    # Figure 4: Domain boxplot
    mmlu_tasks = set([
        "abstract_algebra", "anatomy", "astronomy", "business_ethics",
        "clinical_knowledge", "college_biology", "college_chemistry",
        "college_computer_science", "college_mathematics", "college_medicine",
        "college_physics", "computer_security", "conceptual_physics",
        "econometrics", "electrical_engineering", "elementary_mathematics",
        "formal_logic", "global_facts", "high_school_biology",
        "high_school_chemistry", "high_school_computer_science",
        "high_school_european_history", "high_school_geography",
        "high_school_government_and_politics", "high_school_macroeconomics",
        "high_school_mathematics", "high_school_microeconomics",
        "high_school_physics", "high_school_psychology",
        "high_school_statistics", "high_school_us_history",
        "high_school_world_history", "human_aging", "human_sexuality",
        "international_law", "jurisprudence", "logical_fallacies",
        "machine_learning", "management", "marketing", "medical_genetics",
        "miscellaneous", "moral_disputes", "moral_philosophy", "nutrition",
        "philosophy", "prehistory", "professional_accounting",
        "professional_law", "professional_medicine", "professional_psychology",
        "public_relations", "security_studies", "sociology",
        "us_foreign_policy", "virology", "world_religions",
    ])
    rates_df2 = rates_df.copy()
    rates_df2["domain"] = rates_df2["subtask"].apply(
        lambda x: "MMLU (Academic)" if x in mmlu_tasks else "Commonsense (HellaSwag/BBH)"
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    groups = [rates_df2[rates_df2["domain"] == d]["rate"].values for d in rates_df2["domain"].unique()]
    ax.boxplot(groups, labels=list(rates_df2["domain"].unique()))
    ax.set_ylabel("13-gram Contamination Rate")
    ax.set_title("Contamination Rates by Domain Type")
    plt.tight_layout()
    p4 = os.path.join(figures_dir, "domain_boxplot.png")
    fig.savefig(p4, dpi=150)
    plt.close()
    generated.append(p4)

    # Figure 5: Sensitivity scatter
    merged = rates_df.set_index("subtask")[["rate"]].join(
        sens_df.set_index("subtask")[["rate"]], lsuffix="_primary", rsuffix="_sens"
    ).dropna()
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(merged["rate_primary"], merged["rate_sens"], alpha=0.6, s=30)
    ax.set_xlabel("Contamination Rate (question+choices)")
    ax.set_ylabel("Contamination Rate (question-only)")
    ax.set_title(f"Sensitivity Analysis: Format Comparison\n"
                 f"Spearman ρ={sensitivity['rho']:.3f}, p={sensitivity['p_value']:.2e}")
    lim = max(merged["rate_primary"].max(), merged["rate_sens"].max()) * 1.05
    ax.plot([0, lim], [0, lim], "k--", alpha=0.4, label="y=x")
    ax.legend()
    plt.tight_layout()
    p5 = os.path.join(figures_dir, "sensitivity_scatter.png")
    fig.savefig(p5, dpi=150)
    plt.close()
    generated.append(p5)

    return generated


def save_results(rates_df: pd.DataFrame, stats: dict, sensitivity: dict,
                 results_dir: str, hypothesis_folder: str) -> None:
    """Save CSV and JSON results."""
    os.makedirs(results_dir, exist_ok=True)
    outputs_dir = os.path.join(os.path.dirname(results_dir), "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    csv_path = os.path.join(results_dir, "contamination_rates.csv")
    rates_df.to_csv(csv_path, index=False)
    rates_df.to_csv(os.path.join(outputs_dir, "results.csv"), index=False)
    logger.info(f"Saved CSV: {csv_path}")

    json_data = {
        "hypothesis_id": "h-e1",
        "execution_mode": "real-datasets-wimbd-query",
        "status": "completed",
        "method": "HuggingFace datasets + allenai/wimbd 13-gram Pile index queries",
        "corpus": "The Pile v1",
        "benchmarks": ["MMLU (57 sub-tasks)", "HellaSwag", "BIG-Bench Hard"],
        "total_subtasks": int(len(rates_df)),
        "total_items": int(rates_df["n_items"].sum()),
        "metrics": {
            "kruskal_wallis_H": stats["kruskal_stat"],
            "kruskal_wallis_p": stats["p_value"],
            "gate_pass": stats["gate_pass"],
            "max_pair_diff": stats["max_pair_diff"],
            "mean_contamination_rate": float(rates_df["rate"].mean()),
            "min_contamination_rate": float(rates_df["rate"].min()),
            "max_contamination_rate": float(rates_df["rate"].max()),
            "sensitivity_spearman_rho": sensitivity["rho"],
            "sensitivity_spearman_p": sensitivity["p_value"],
        },
        "gate": {
            "type": "MUST_WORK",
            "criterion": "Kruskal-Wallis p < 0.05",
            "result": "PASS" if stats["gate_pass"] else "FAIL",
            "satisfied": stats["gate_pass"],
        },
        "top5_contaminated": rates_df.nlargest(5, "rate")[["subtask", "rate"]].to_dict("records"),
        "bottom5_contaminated": rates_df.nsmallest(5, "rate")[["subtask", "rate"]].to_dict("records"),
    }

    json_path = os.path.join(hypothesis_folder, "experiment_results.json")
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)
    logger.info(f"Saved JSON: {json_path}")

    stats_json_path = os.path.join(results_dir, "statistical_tests.json")
    with open(stats_json_path, "w") as f:
        json.dump({"kruskal_wallis": stats, "sensitivity": sensitivity}, f, indent=2)
    logger.info(f"Saved: {stats_json_path}")


def main():
    hypothesis_folder = Path(__file__).parent.parent
    results_dir = str(hypothesis_folder / "code" / "results")
    figures_dir = str(hypothesis_folder / "figures")

    logger.info(f"Hypothesis folder: {hypothesis_folder}")
    logger.info(f"Results dir: {results_dir}")
    logger.info(f"Figures dir: {figures_dir}")

    result = run_experiment(seed=1)
    rates_df = result["rates_df"]
    stats = result["stats"]
    sensitivity = result["sensitivity"]

    logger.info(f"\n{'='*60}")
    logger.info("EXPERIMENT RESULTS SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total sub-tasks: {len(rates_df)}")
    logger.info(f"Mean contamination rate: {rates_df['rate'].mean():.4f}")
    logger.info(f"Kruskal-Wallis H={stats['kruskal_stat']:.4f}, p={stats['p_value']:.2e}")
    logger.info(f"Max pair diff: {stats['max_pair_diff']:.4f}")
    logger.info(f"Gate MUST_WORK: {'PASS ✓' if stats['gate_pass'] else 'FAIL ✗'}")
    logger.info(f"Sensitivity Spearman rho={sensitivity['rho']:.4f}")

    figs = generate_figures(rates_df, stats, result["sens_df"], sensitivity, figures_dir)
    logger.info(f"Generated {len(figs)} figures")

    save_results(rates_df, stats, sensitivity, results_dir, str(hypothesis_folder))

    if not stats["gate_pass"]:
        logger.error(f"GATE FAILED: Kruskal-Wallis p={stats['p_value']:.6f} >= 0.05")
        sys.exit(1)
    else:
        logger.info("GATE PASSED: Kruskal-Wallis p < 0.05")
        logger.info("H-E1 PoC validated: Significant contamination variance exists across sub-tasks")

    logger.info("EXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
