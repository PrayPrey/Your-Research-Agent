"""
H-M3: Analysis entrypoint
- Mann-Whitney U test + Cohen's d
- Gate check
- Main pipeline
"""
import os
import sys
import json
import numpy as np
from pathlib import Path
from scipy.stats import mannwhitneyu

sys.path.insert(0, str(Path(__file__).parent))

from data_loader import load_papers, build_citation_pairs
from overlap import compute_citation_dataset_overlap
import visualize


def run_statistical_test(citing_overlaps: list[float], random_overlaps: list[float]) -> dict:
    """Mann-Whitney U (alternative='greater') + Cohen's d.
    Returns {mann_whitney_stat, p_value, mean_citing_overlap, mean_random_overlap,
    cohens_d, n_citing_pairs, n_random_pairs}."""

    citing_arr = np.array(citing_overlaps)
    random_arr = np.array(random_overlaps)

    if len(citing_arr) == 0 or len(random_arr) == 0:
        return {
            "mann_whitney_stat": np.nan,
            "p_value": 1.0,
            "mean_citing_overlap": 0.0,
            "mean_random_overlap": 0.0,
            "cohens_d": 0.0,
            "n_citing_pairs": len(citing_arr),
            "n_random_pairs": len(random_arr),
            "gate_passed": False,
        }

    stat, p_value = mannwhitneyu(citing_arr, random_arr, alternative="greater")

    mean_citing = float(np.mean(citing_arr))
    mean_random = float(np.mean(random_arr))

    var_citing = float(np.var(citing_arr, ddof=1)) if len(citing_arr) > 1 else 0.0
    var_random = float(np.var(random_arr, ddof=1)) if len(random_arr) > 1 else 0.0
    pooled_std = np.sqrt((var_citing + var_random) / 2)

    cohens_d = (mean_citing - mean_random) / pooled_std if pooled_std > 0 else 0.0

    return {
        "mann_whitney_stat": float(stat),
        "p_value": float(p_value),
        "mean_citing_overlap": mean_citing,
        "mean_random_overlap": mean_random,
        "std_citing": float(np.std(citing_arr)),
        "std_random": float(np.std(random_arr)),
        "cohens_d": float(cohens_d),
        "n_citing_pairs": int(len(citing_arr)),
        "n_random_pairs": int(len(random_arr)),
    }


def gate_check(metrics: dict) -> bool:
    """p_value < 0.01 AND cohens_d > 0.3 AND n_citing_pairs >= 1000."""
    return (
        metrics["p_value"] < 0.01 and
        metrics["cohens_d"] > 0.3 and
        metrics["n_citing_pairs"] >= 1000
    )


def main() -> dict:
    """Main pipeline:
    1. load_papers()
    2. build_citation_pairs()
    3. compute_citation_dataset_overlap()
    4. run_statistical_test() + gate_check()
    5. visualize.generate_all()
    6. save results to outputs/results.json
    """
    print("=" * 60)
    print("H-M3: Citation-Benchmark Overlap Analysis")
    print("=" * 60)

    code_dir = Path(__file__).parent
    outputs_dir = code_dir / "outputs"
    figures_dir = code_dir.parent / "figures"
    outputs_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)

    print("\n[1/6] Loading papers...")
    papers_df = load_papers()

    api_key = os.environ.get("S2_API_KEY")
    if not api_key:
        print("WARNING: S2_API_KEY not set. API requests may be rate-limited.")

    print("\n[2/6] Building citation pairs...")
    citations_df = build_citation_pairs(papers_df, api_key)

    if len(citations_df) == 0:
        print("ERROR: No citation pairs found. Cannot proceed with analysis.")
        results = {
            "error": "No citation pairs found",
            "n_papers": len(papers_df),
            "gate_passed": False,
        }
        with open(outputs_dir / "results.json", "w") as f:
            json.dump(results, f, indent=2)
        return results

    print("\n[3/6] Computing overlap distributions...")
    citing_overlaps, random_overlaps = compute_citation_dataset_overlap(
        papers_df, citations_df, seed=42
    )

    print("\n[4/6] Running statistical tests...")
    metrics = run_statistical_test(citing_overlaps, random_overlaps)
    gate_passed = gate_check(metrics)
    metrics["gate_passed"] = gate_passed

    print("\n[5/6] Generating visualizations...")
    generated_figures = visualize.generate_all(
        metrics, citing_overlaps, random_overlaps,
        papers_df, citations_df, str(figures_dir)
    )

    results = {
        "hypothesis_id": "h-m3",
        "hypothesis_statement": "Papers follow standards for comparability - citation drives benchmark homogeneity",
        "gate_type": "SHOULD_WORK",
        "gate_passed": gate_passed,
        "metrics": metrics,
        "sample_sizes": {
            "n_papers": len(papers_df),
            "n_citation_pairs": len(citations_df),
            "n_citing_overlaps": len(citing_overlaps),
            "n_random_overlaps": len(random_overlaps),
        },
        "figures": generated_figures,
    }

    results_path = outputs_dir / "results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[6/6] Results saved to {results_path}")

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Papers analyzed: {len(papers_df):,}")
    print(f"Citation pairs: {len(citations_df):,}")
    print(f"Citing overlaps computed: {len(citing_overlaps):,}")
    print(f"Random overlaps computed: {len(random_overlaps):,}")
    print()
    print(f"Mean citing overlap: {metrics['mean_citing_overlap']:.4f}")
    print(f"Mean random overlap: {metrics['mean_random_overlap']:.4f}")
    print(f"Mann-Whitney U: {metrics['mann_whitney_stat']:.2f}")
    print(f"p-value: {metrics['p_value']:.6f}")
    print(f"Cohen's d: {metrics['cohens_d']:.4f}")
    print()
    print(f"GATE RESULT: {'PASS' if gate_passed else 'FAIL'}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results.get("gate_passed", False) else 1)
