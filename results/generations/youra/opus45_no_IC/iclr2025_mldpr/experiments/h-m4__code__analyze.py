# analyze.py - H-M4 main analysis: entropy vs benchmark breadth concentration
# Using REAL PWC data - no synthetic fallback

import json
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr

from config import (
    ALPHA, MIN_VENUE_YEARS_PER_VENUE, MIN_VENUES_WITH_EFFECT,
    OUTPUT_DIR, FIGURES_DIR, SEED
)
from data_loader import load_entropy_by_venue_year, load_multi_benchmark_papers_from_pwc
from variance import aggregate_venue_year
import visualize


def run_correlation_test(entropy_by_vy: dict, breadth_df) -> dict:
    """
    Compute Spearman correlation between entropy and mean concentration.

    H-M4 hypothesis: low entropy (concentrated benchmarks) correlates with
    high concentration (narrower benchmark breadth per paper).

    Args:
        entropy_by_vy: dict[(venue, year), entropy]
        breadth_df: DataFrame with venue, year, mean_concentration columns

    Returns:
        dict with spearman_rho, p_value, n_venue_years, per_venue results
    """
    # Align on common keys
    common_keys = set()
    for _, row in breadth_df.iterrows():
        key = (row["venue"], row["year"])
        if key in entropy_by_vy:
            common_keys.add(key)

    if len(common_keys) < 5:
        return {
            "spearman_rho": float("nan"),
            "p_value": 1.0,
            "n_venue_years": len(common_keys),
            "per_venue": {},
            "error": "Insufficient common venue-years",
        }

    # Build aligned arrays
    entropies = []
    concentrations = []
    venue_year_data = []

    for key in common_keys:
        entropies.append(entropy_by_vy[key])
        row = breadth_df[(breadth_df["venue"] == key[0]) & (breadth_df["year"] == key[1])].iloc[0]
        concentrations.append(row["mean_concentration"])
        venue_year_data.append({"venue": key[0], "year": key[1], "entropy": entropy_by_vy[key], "mean_concentration": row["mean_concentration"]})

    # Overall Spearman correlation
    # Expect NEGATIVE: low entropy -> high concentration (less breadth)
    rho, p_value = spearmanr(entropies, concentrations)

    # Per-venue analysis
    per_venue = {}
    for venue in ["NeurIPS", "ICML", "ICLR"]:
        venue_data = [d for d in venue_year_data if d["venue"] == venue]
        if len(venue_data) >= MIN_VENUE_YEARS_PER_VENUE:
            v_ent = [d["entropy"] for d in venue_data]
            v_conc = [d["mean_concentration"] for d in venue_data]
            v_rho, v_p = spearmanr(v_ent, v_conc)
            per_venue[venue] = {"rho": float(v_rho), "p": float(v_p), "n": len(venue_data)}
        else:
            per_venue[venue] = {"rho": float("nan"), "p": 1.0, "n": len(venue_data), "note": "insufficient data"}

    return {
        "spearman_rho": float(rho),
        "p_value": float(p_value),
        "n_venue_years": len(common_keys),
        "per_venue": per_venue,
    }


def gate_check(results: dict) -> bool:
    """
    H-M4 Gate: SHOULD_WORK
    - ρ < 0 (negative correlation: low entropy -> high concentration)
    - p < 0.05 (significant)
    - Effect in ≥2/3 venues (negative ρ in at least 2 venues)

    Note: We test entropy vs concentration (1/breadth).
    Negative correlation means: low entropy -> high concentration -> less breadth.
    This supports the hypothesis that concentrated venues have narrower evaluation.
    """
    rho = results.get("spearman_rho", 0)
    p = results.get("p_value", 1)
    per_venue = results.get("per_venue", {})

    # Primary: overall negative correlation
    if rho >= 0 or p >= ALPHA:
        return False

    # Secondary: effect in ≥2 venues
    venues_with_effect = sum(
        1 for v in per_venue.values()
        if not np.isnan(v.get("rho", float("nan"))) and v.get("rho", 0) < 0
    )

    return venues_with_effect >= MIN_VENUES_WITH_EFFECT


def main():
    """Main analysis pipeline."""
    np.random.seed(SEED)

    print("=" * 60)
    print("H-M4: Cross-Benchmark Variance Analysis")
    print("=" * 60)

    # Step 1: Load entropy data from H-E1
    print("\n[1] Loading entropy data from H-E1...")
    entropy_by_vy = load_entropy_by_venue_year()
    print(f"    Loaded entropy for {len(entropy_by_vy)} venue-years")

    # Step 2: Load multi-benchmark papers
    print("\n[2] Loading multi-benchmark papers...")
    papers_df = load_multi_benchmark_papers_from_pwc()
    print(f"    Loaded {len(papers_df)} papers with 2+ benchmarks")

    # Step 3: Compute venue-year breadth aggregates
    print("\n[3] Computing benchmark breadth/concentration...")
    breadth_df = aggregate_venue_year(papers_df)
    print(f"    Aggregated to {len(breadth_df)} venue-years (min {breadth_df['n_papers'].min()} papers)")

    # Add entropy column for visualization
    breadth_df["entropy"] = breadth_df.apply(
        lambda row: entropy_by_vy.get((row["venue"], row["year"]), float("nan")),
        axis=1
    )

    # Step 4: Run correlation test
    print("\n[4] Running Spearman correlation test...")
    results = run_correlation_test(entropy_by_vy, breadth_df)

    print(f"\n    Overall Spearman ρ: {results['spearman_rho']:.4f}")
    print(f"    p-value: {results['p_value']:.4e}")
    print(f"    N venue-years: {results['n_venue_years']}")

    print("\n    Per-venue results:")
    for venue, stats in results.get("per_venue", {}).items():
        print(f"      {venue}: ρ={stats['rho']:.3f}, p={stats['p']:.3e}, n={stats['n']}")

    # Step 5: Gate check
    print("\n[5] Gate check (SHOULD_WORK)...")
    gate_passed = gate_check(results)
    results["gate_passed"] = gate_passed
    results["hypothesis_supported"] = gate_passed

    if gate_passed:
        print("    ✓ GATE PASSED: Low entropy correlates with high cross-benchmark variance")
    else:
        print("    ✗ GATE FAILED: Insufficient evidence for entropy-variance correlation")

    # Step 6: Generate visualizations
    print("\n[6] Generating figures...")
    Path(FIGURES_DIR).mkdir(parents=True, exist_ok=True)
    visualize.generate_all(results, breadth_df, FIGURES_DIR)

    # Step 7: Save results
    print("\n[7] Saving results...")
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Main results JSON
    results_path = Path(OUTPUT_DIR) / "results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"    Saved: {results_path}")

    # CSV for downstream use
    csv_path = Path(OUTPUT_DIR) / "breadth_by_venue_year.csv"
    breadth_df.drop(columns=["paper_ids"], errors="ignore").to_csv(csv_path, index=False)
    print(f"    Saved: {csv_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Hypothesis: H-M4 (Reduced diversity hides overfitting)")
    print(f"  Spearman ρ: {results['spearman_rho']:.4f} (expected: < 0)")
    print(f"  p-value: {results['p_value']:.4e} (threshold: < 0.05)")
    print(f"  Gate: {'PASSED' if gate_passed else 'FAILED'}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
