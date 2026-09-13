"""H-M2: Domain-Stratified Contamination Re-Analysis.

Pipeline: load_config -> load_matrix -> classify -> stratify ->
          directional_tests -> kruskal_interaction -> top5 ->
          visualize -> save_results -> assert_gate -> log gate result.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

from config import load_config, Config
from domain_classifier import DomainClassifier
from stats_analyzer import StatsAnalyzer
from visualizer import Visualizer


def load_matrix(path: str) -> dict:
    """Load contamination matrix from CSV or JSON. Returns {subtask: {corpus: rate}}."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Matrix file not found: {path}")

    if p.suffix == ".csv":
        df = pd.read_csv(path)
        # Expect columns: subtask, pile, c4, redpajama
        if "subtask" not in df.columns:
            raise ValueError(f"CSV missing 'subtask' column. Found: {df.columns.tolist()}")
        expected_corpora = {"pile", "c4", "redpajama"}
        missing = expected_corpora - set(df.columns)
        if missing:
            raise ValueError(f"CSV missing corpus columns: {missing}")
        matrix = {}
        for _, row in df.iterrows():
            matrix[row["subtask"]] = {
                "pile": float(row["pile"]),
                "c4": float(row["c4"]),
                "redpajama": float(row["redpajama"]),
            }
    else:
        # JSON fallback — try to extract matrix from h-m1 experiment_results.json
        with open(path) as f:
            data = json.load(f)
        # Check if it's a contamination_matrix dict directly
        if isinstance(data, dict) and "contamination_matrix" in data:
            matrix = data["contamination_matrix"]
        elif isinstance(data, dict) and all(
            isinstance(v, dict) and set(v.keys()) >= {"pile", "c4", "redpajama"}
            for v in list(data.values())[:3]
        ):
            matrix = data
        else:
            raise ValueError(
                f"Cannot extract 59×3 matrix from JSON. "
                f"Expected dict with subtask keys each having pile/c4/redpajama. "
                f"Top-level keys: {list(data.keys())[:10]}"
            )

    if len(matrix) != 59:
        raise ValueError(
            f"Expected 59 subtasks in matrix, got {len(matrix)}. "
            f"Check source file: {path}"
        )

    # Validate all corpora present
    for subtask, vals in matrix.items():
        for corpus in ("pile", "c4", "redpajama"):
            if corpus not in vals:
                raise ValueError(f"Missing corpus '{corpus}' for subtask '{subtask}'")

    return matrix


def save_results(
    stratified: dict,
    tests: dict,
    kruskal: dict,
    top5: dict,
    gate_result: bool,
    config: Config,
) -> None:
    """Write results/domain_stratified_rates.json and results/statistical_tests.json."""
    os.makedirs(config.results_dir, exist_ok=True)

    # domain_stratified_rates.json — 2x3 mean table (no _rates lists for compactness)
    rates_summary = {}
    for corpus, v in stratified.items():
        rates_summary[corpus] = {
            "academic": v["academic"],
            "commonsense": v["commonsense"],
            "n_academic": len(v["academic_rates"]),
            "n_commonsense": len(v["commonsense_rates"]),
        }
    with open(os.path.join(config.results_dir, "domain_stratified_rates.json"), "w") as f:
        json.dump(rates_summary, f, indent=2)

    # statistical_tests.json — all test results + gate
    tests_out = {
        "directional_tests": tests,
        "kruskal_interaction": kruskal,
        "gate_result": "PASS" if gate_result else "FAIL",
        "gate_type": "SHOULD_WORK",
        "min_corpora_required": config.min_corpora_directional_confirmed,
        "alpha": config.alpha,
        "top5_per_corpus": top5,
    }
    with open(os.path.join(config.results_dir, "statistical_tests.json"), "w") as f:
        json.dump(tests_out, f, indent=2)


def main() -> None:
    config = load_config()

    os.makedirs(config.results_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    print("=" * 60)
    print("H-M2: Domain-Stratified Contamination Re-Analysis")
    print("=" * 60)

    # 1. Load matrix
    print(f"\n[1/7] Loading contamination matrix from: {config.h_m1_results_path}")
    matrix = load_matrix(config.h_m1_results_path)
    print(f"  ✓ Loaded {len(matrix)} subtasks × 3 corpora")

    # 2. Classify domains
    print("\n[2/7] Classifying subtask domains...")
    classifier = DomainClassifier()
    domain_map = classifier.build_domain_map(list(matrix.keys()))
    n_academic = sum(1 for v in domain_map.values() if v == "academic")
    n_commonsense = sum(1 for v in domain_map.values() if v == "commonsense")
    print(f"  ✓ academic={n_academic}, commonsense={n_commonsense}")

    # 3. Compute stratified rates
    print("\n[3/7] Computing domain-stratified rates (2×3 table)...")
    analyzer = StatsAnalyzer(config)
    stratified = analyzer.compute_domain_stratified_rates(matrix, domain_map)
    for corpus in config.corpora:
        acad = stratified[corpus]["academic"] * 100
        comm = stratified[corpus]["commonsense"] * 100
        print(f"  {corpus}: academic={acad:.2f}%, commonsense={comm:.2f}%")

    # 4. Directional tests
    print("\n[4/7] Running directional Mann-Whitney U tests...")
    directional_tests = analyzer.run_directional_tests(stratified)
    confirmed_count = 0
    for test_name, res in directional_tests.items():
        confirmed = res["direction_confirmed"]
        if confirmed:
            confirmed_count += 1
        print(f"  {test_name}: p={res['p']:.4f}, r={res['effect_size_r']:.3f}, "
              f"d={res['cohens_d']:.3f}, confirmed={confirmed}")

    # 5. Kruskal-Wallis interaction
    print("\n[5/7] Kruskal-Wallis interaction test (6 groups)...")
    kruskal = analyzer.kruskal_interaction(stratified)
    print(f"  H={kruskal['H']:.4f}, p={kruskal['p']:.4f}, significant={kruskal['significant']}")

    # 6. Top-N per corpus
    print(f"\n[6/7] Computing top-{config.top_n} subtasks per corpus...")
    top5 = analyzer.top_n_per_corpus(matrix, domain_map, n=config.top_n)

    # 7. Visualize
    print("\n[7/7] Generating figures...")
    viz = Visualizer(config)
    viz.plot_domain_corpus_heatmap(stratified)
    print("  ✓ domain_corpus_heatmap.png")
    viz.plot_domain_boxplots(stratified, directional_tests)
    print("  ✓ domain_boxplots.png")
    viz.plot_top5_per_corpus(top5, domain_map)
    print("  ✓ top5_per_corpus.png")
    viz.plot_directional_test_summary(directional_tests)
    print("  ✓ directional_test_summary.png")

    # Save results
    gate_result = analyzer.assert_gate(directional_tests)
    save_results(stratified, directional_tests, kruskal, top5, gate_result, config)
    print("\n  ✓ results/domain_stratified_rates.json")
    print("  ✓ results/statistical_tests.json")

    # Write experiment_results.json
    experiment_results = {
        "hypothesis_id": "h-m2",
        "status": "completed",
        "completed_at": datetime.utcnow().isoformat() + "+00:00",
        "gate": {
            "type": "SHOULD_WORK",
            "pass": gate_result,
            "min_corpora_required": config.min_corpora_directional_confirmed,
            "corpora_confirmed": confirmed_count,
        },
        "directional_patterns_confirmed": confirmed_count,
        "gate_result": "PASS" if gate_result else "FAIL",
        "directional_tests": directional_tests,
        "kruskal_interaction": kruskal,
        "domain_stratified_rates": {
            corpus: {
                "academic": stratified[corpus]["academic"],
                "commonsense": stratified[corpus]["commonsense"],
            }
            for corpus in config.corpora
        },
        "top5_per_corpus": top5,
    }
    with open("../experiment_results.json", "w") as f:
        json.dump(experiment_results, f, indent=2)
    print("  ✓ experiment_results.json")

    # Gate verdict
    print("\n" + "=" * 60)
    if gate_result:
        print(f"✅ GATE PASSED (SHOULD_WORK): {confirmed_count}/3 corpora confirmed directional pattern")
    else:
        print(f"⚠️  GATE FAILED (SHOULD_WORK): only {confirmed_count}/3 corpora confirmed "
              f"(required ≥{config.min_corpora_directional_confirmed})")
        print("   SHOULD_WORK failure → continuing with limitation note")
    print("=" * 60)
    print("\nEXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
