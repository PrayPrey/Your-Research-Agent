#!/usr/bin/env python3
"""H-M1 Pipeline: Foundation Model Emergence Timeline validation."""
import json
import os
import sys
from pathlib import Path

from config import CONFIG
from data_collector import DataCollector
from stats_engine import StatsEngine
from visualizer import Visualizer


def main() -> dict:
    print("=" * 60)
    print("H-M1: Foundation Model Emergence Timeline")
    print("=" * 60)

    dc = DataCollector(cache_dir=CONFIG.cache_dir)
    se = StatsEngine()
    viz = Visualizer(output_dir=CONFIG.output_dir)

    print("\n[1/5] Fetching foundation model papers...")
    foundation = dc.fetch_foundation_papers(CONFIG.foundation_papers)
    print(f"  Retrieved {len(foundation)} foundation papers")
    for p in foundation:
        print(f"    - {p['title'][:50]}... ({p['citationCount']} citations)")

    print("\n[2/5] Fetching comparison set (ML papers 2019-2021)...")
    comparison = dc.fetch_comparison_set(
        CONFIG.years, CONFIG.venues, CONFIG.min_papers_per_year
    )
    print(f"  Retrieved {len(comparison)} comparison papers")

    print("\n[3/5] Computing field statistics...")
    field_stats = se.compute_field_stats(comparison)
    print(f"  Field mean: {field_stats['mean']:.1f}")
    print(f"  Field std: {field_stats['std']:.1f}")
    print(f"  Sample size: {field_stats['n']}")

    field_citations = [p["citationCount"] for p in comparison]

    print("\n[4/5] Computing z-scores for foundation papers...")
    foundation_results = {}
    for p in foundation:
        z = se.compute_zscore(p["citationCount"], field_stats["mean"], field_stats["std"])
        pct = se.compute_percentile(p["citationCount"], field_citations)
        foundation_results[p["paperId"]] = {
            "title": p["title"],
            "citations": p["citationCount"],
            "z_score": z,
            "exceeds_2sigma": z > CONFIG.zscore_threshold,
            "percentile": pct,
        }
        status = "✓ PASS" if z > CONFIG.zscore_threshold else "✗ FAIL"
        print(f"  {p['title'][:40]}... z={z:.2f} {status}")

    gate_pass = se.evaluate_gate(
        foundation_results, CONFIG.zscore_threshold, CONFIG.gate_min_passing
    )
    passing_count = sum(1 for r in foundation_results.values() if r["exceeds_2sigma"])

    print("\n[5/5] Generating visualizations...")
    figures = []
    try:
        figures.append(viz.plot_zscore_bar(foundation_results))
        figures.append(viz.plot_citation_histogram(field_citations, foundation_results))
        figures.append(viz.plot_percentile_table(foundation_results))
        print(f"  Generated {len(figures)} figures")
    except Exception as e:
        print(f"  Warning: Visualization failed: {e}")

    print("\n" + "=" * 60)
    print(f"GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")
    print(f"  {passing_count}/{len(foundation_results)} papers exceed 2σ threshold")
    print(f"  Required: {CONFIG.gate_min_passing}/{len(CONFIG.foundation_papers)}")
    print("=" * 60)

    result = {
        "gate_pass": gate_pass,
        "passing_count": passing_count,
        "total_papers": len(foundation_results),
        "required_passing": CONFIG.gate_min_passing,
        "foundation_results": foundation_results,
        "field_stats": field_stats,
        "figures": figures,
    }

    output_path = Path(CONFIG.report_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nReport saved to {output_path}")

    return result


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result["gate_pass"] else 1)
