#!/usr/bin/env python3
"""H-M1 Validation: High HHI indicates community convergence on few datasets."""

import json
from pathlib import Path
from scipy.stats import mannwhitneyu, spearmanr
import pandas as pd

from data_loader import load_papers, build_venue_year_table
import visualize

CONFIG = {
    "alpha": 0.05,
    "spearman_rho_threshold": 0.7,
    "top_n": 5,
    "results_out_path": Path(__file__).parent / "results" / "results.json",
    "figures_out_dir": Path(__file__).parent.parent / "figures",
}


def compute_top5_share(task_counts: pd.Series) -> float:
    """Sum of top-5 category counts / total count. Returns ratio in [0, 1]."""
    if task_counts.empty:
        return 0.0
    sorted_counts = task_counts.sort_values(ascending=False)
    total = sorted_counts.sum()
    if total == 0:
        return 0.0
    return float(sorted_counts.head(CONFIG["top_n"]).sum() / total)


def validate_hhi_interpretation(venue_year_df: pd.DataFrame) -> dict:
    """Run statistical validation of HHI interpretation."""
    # Add top5_share column
    venue_year_df = venue_year_df.copy()
    venue_year_df['top5_share'] = venue_year_df['task_counts'].apply(compute_top5_share)

    # Split by median HHI
    median_hhi = venue_year_df['hhi'].median()
    high_hhi_df = venue_year_df[venue_year_df['hhi'] > median_hhi]
    low_hhi_df = venue_year_df[venue_year_df['hhi'] <= median_hhi]

    high = high_hhi_df['top5_share']
    low = low_hhi_df['top5_share']

    # Mann-Whitney U test (one-sided: high > low)
    stat, mw_p = mannwhitneyu(high, low, alternative='greater')

    # Spearman correlation
    rho, sp_p = spearmanr(venue_year_df['hhi'], venue_year_df['top5_share'])

    # Gate evaluation
    gate_passed = mw_p < CONFIG["alpha"]

    results = {
        'high_mean': float(high.mean()),
        'low_mean': float(low.mean()),
        'high_n': int(len(high)),
        'low_n': int(len(low)),
        'median_hhi': float(median_hhi),
        'mann_whitney_stat': float(stat),
        'mann_whitney_p': float(mw_p),
        'spearman_rho': float(rho),
        'spearman_p': float(sp_p),
        'gate_passed': bool(gate_passed),
        'spearman_threshold_met': bool(abs(rho) > CONFIG["spearman_rho_threshold"]),
    }

    return results, venue_year_df


def verify_mechanism_activation(results: dict) -> bool:
    """PoC sanity gate: groups_differ AND correlation_positive."""
    groups_differ = results['high_mean'] > results['low_mean']
    correlation_positive = results['spearman_rho'] > 0

    checks = {
        'groups_differ': groups_differ,
        'correlation_positive': correlation_positive,
    }
    print(f"Mechanism checks: {checks}")
    return all(checks.values())


def main():
    print("=" * 60)
    print("H-M1 Validation: HHI Interpretation Test")
    print("=" * 60)

    # Step 1: Load papers
    print("\n[1/6] Loading papers...")
    papers_df = load_papers()
    print(f"  Loaded {len(papers_df)} papers")

    # Step 2: Build venue-year table
    print("\n[2/6] Building venue-year table...")
    venue_year_df = build_venue_year_table(papers_df)
    print(f"  Built {len(venue_year_df)} venue-year rows")

    # Step 3: Run validation
    print("\n[3/6] Running statistical validation...")
    results, venue_year_df = validate_hhi_interpretation(venue_year_df)

    print(f"\n  Results:")
    print(f"    High-HHI group mean top5_share: {results['high_mean']:.4f}")
    print(f"    Low-HHI group mean top5_share:  {results['low_mean']:.4f}")
    print(f"    Mann-Whitney U stat: {results['mann_whitney_stat']:.2f}")
    print(f"    Mann-Whitney p-value: {results['mann_whitney_p']:.6f}")
    print(f"    Spearman rho: {results['spearman_rho']:.4f}")
    print(f"    Spearman p-value: {results['spearman_p']:.6f}")

    # Step 4: Verify mechanism activation
    print("\n[4/6] Verifying mechanism activation...")
    mechanism_ok = verify_mechanism_activation(results)
    results['mechanism_activated'] = mechanism_ok

    # Step 5: Generate visualizations
    print("\n[5/6] Generating visualizations...")
    CONFIG["figures_out_dir"].mkdir(parents=True, exist_ok=True)
    visualize.generate_all(results, venue_year_df, str(CONFIG["figures_out_dir"]))

    # Step 6: Save results
    print("\n[6/6] Saving results...")
    CONFIG["results_out_path"].parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG["results_out_path"], 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  Saved to {CONFIG['results_out_path']}")

    # Final gate status
    print("\n" + "=" * 60)
    if results['gate_passed']:
        print("GATE STATUS: PASSED")
        print(f"  Mann-Whitney p = {results['mann_whitney_p']:.6f} < 0.05")
    else:
        print("GATE STATUS: FAILED")
        print(f"  Mann-Whitney p = {results['mann_whitney_p']:.6f} >= 0.05")

    if results['spearman_threshold_met']:
        print(f"  Spearman rho = {results['spearman_rho']:.4f} > 0.7 (SHOULD criterion met)")
    else:
        print(f"  Spearman rho = {results['spearman_rho']:.4f} <= 0.7 (SHOULD criterion not met)")

    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
