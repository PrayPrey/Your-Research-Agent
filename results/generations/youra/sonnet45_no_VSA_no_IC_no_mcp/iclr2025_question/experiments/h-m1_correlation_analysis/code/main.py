#!/usr/bin/env python3
"""Main pipeline for H-M1 correlation analysis."""

import argparse
from pathlib import Path
from typing import Dict

from data_loader import CorpusLoader
from analyzer import CorrelationAnalyzer
from per_type_analyzer import PerTypeAnalyzer
from visualizer import Visualizer
from validator import ValidationWriter


def run_analysis(corpus_path: str, output_dir: str) -> Dict:
    """
    Run full correlation analysis pipeline.
    Returns: {
        "r": float, "p": float, "k": float, "r2": float,
        "cv": float, "k_by_type": dict, "passed": bool
    }
    """
    print("=" * 60)
    print("H-M1 Correlation Analysis Pipeline")
    print("=" * 60)

    # 1. Load data
    print("\n[1/5] Loading corpus...")
    loader = CorpusLoader(corpus_path)
    corpus = loader.load()
    o10, ofull = loader.extract_overhead_arrays(corpus)
    grouped = loader.group_by_type(corpus)

    # 2. Global correlation
    print("\n[2/5] Computing global correlation...")
    analyzer = CorrelationAnalyzer()
    r, p = analyzer.compute_pearson(o10, ofull)
    k, r2, residuals = analyzer.fit_linear_regression(o10, ofull)
    print(f"  Pearson r = {r:.3f} (p = {p:.4f})")
    print(f"  Scaling factor k = {k:.3f}")
    print(f"  R² = {r2:.3f}")

    # 3. Per-type analysis
    print("\n[3/5] Per-type scaling analysis...")
    per_type = PerTypeAnalyzer(analyzer)
    type_results = per_type.analyze_types(grouped)
    k_by_type = {t: res["k"] for t, res in type_results.items()}
    cv = per_type.compute_scaling_cv(k_by_type)
    print(f"  Scaling CV = {cv:.2%}")

    # 4. Visualizations
    print("\n[4/5] Generating visualizations...")
    types = [p["hypothesis_type"] for p in corpus]
    viz = Visualizer(output_dir)
    viz.plot_correlation_scatter(o10, ofull, types, r, p, k)
    viz.plot_scaling_factors(k_by_type)
    viz.plot_residuals(o10, residuals)

    # 5. Validation
    print("\n[5/5] Writing validation report...")
    passed = r > 0.7 and p < 0.05 and cv < 0.3
    validator = ValidationWriter(f"{output_dir}/04_validation.md")
    validator.write_results(r, p, k, r2, cv, k_by_type, passed)

    print("\n" + "=" * 60)
    print(f"Analysis Complete: {'PASS' if passed else 'FAIL'}")
    print("=" * 60)

    return {
        "r": r, "p": p, "k": k, "r2": r2, "cv": cv,
        "k_by_type": k_by_type, "passed": passed
    }


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="H-M1 Correlation Analysis")
    parser.add_argument(
        "--corpus-path",
        default="experiments/h-e1_corpus_collection/code/experiments/h-e1_corpus_collection/data/retrospective_corpus/papers_metadata.json",
        help="Path to H-E1 corpus JSON"
    )
    parser.add_argument(
        "--output-dir",
        default="experiments/h-m1_correlation_analysis/figures",
        help="Output directory for figures and validation"
    )
    args = parser.parse_args()

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    results = run_analysis(args.corpus_path, args.output_dir)

    print(f"\nFinal Results:")
    print(f"  r = {results['r']:.3f}")
    print(f"  p = {results['p']:.4f}")
    print(f"  CV = {results['cv']:.2%}")
    print(f"  Status: {'PASS' if results['passed'] else 'FAIL'}")

    return 0 if results['passed'] else 1


if __name__ == "__main__":
    exit(main())
