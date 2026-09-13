"""main.py — H-M1 pipeline orchestrator."""
from __future__ import annotations
import json
import sys
from pathlib import Path

# Ensure code/ is on sys.path regardless of CWD
_CODE_DIR = Path(__file__).parent
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

from data_loader import load_residual_cov, load_paper_count_star_idx
from analyzer import analyze
from verifier import verify_mechanism_activated
from visualizer import save_all_figures

# Paths relative to h-m1/ directory
_H_M1_DIR = _CODE_DIR.parent
_H_E1_DIR = _H_M1_DIR.parent / "h-e1"

CSV_PATH = _CODE_DIR / "data" / "pwc_cov_computed.csv"
H_E1_JSON = _H_E1_DIR / "experiment_results.json"
RESULTS_PATH = _H_M1_DIR / "experiment_results.json"
FIGURES_DIR = _H_M1_DIR / "figures"


def main() -> int:
    """Orchestrate: load → analyze → verify → visualize → save JSON.

    Returns 0 on PASS, 1 on FAIL gate, 2 on early-fail.
    """
    print("=" * 60)
    print("H-M1: Pre-Breakpoint Residual CoV Variance Characterization")
    print("=" * 60)

    # 1. Load data
    try:
        paper_counts, residual_cov = load_residual_cov(CSV_PATH)
    except (FileNotFoundError, ValueError) as e:
        print(f"EARLY FAIL: {e}")
        return 2

    print(f"Loaded residual_cov series N={len(residual_cov)}")

    try:
        paper_count_star_idx = load_paper_count_star_idx(H_E1_JSON, paper_counts, residual_cov)
    except ValueError as e:
        print(f"EARLY FAIL: {e}")
        return 2

    print(f"paper_count_star_idx = {paper_count_star_idx}")

    # 2. Analyze
    results = analyze(residual_cov, paper_count_star_idx)

    # 3. Verify gate
    gate_passed, indicators = verify_mechanism_activated(results)

    # 4. Visualize
    print("\n--- Saving Figures ---")
    fig_paths = save_all_figures(paper_counts, residual_cov, paper_count_star_idx, results, FIGURES_DIR)
    for p in fig_paths:
        print(f"  {p}")

    # 5. Save results JSON
    output = dict(results)
    output["paper_count_star_idx"] = paper_count_star_idx
    output["indicators"] = indicators
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved → {RESULTS_PATH}")

    # 6. Summary
    print("\n" + "=" * 60)
    if gate_passed:
        print("GATE: PASS")
        print(f"  p_one_tailed = {results['p_one_tailed']:.4f} < 0.10")
        print(f"  variance_ratio_pre_global = {results['variance_ratio_pre_global']:.4f} > 1.0")
        print("  Goodhart early-phase exploration mechanism SUPPORTED")
    else:
        print("GATE: FAIL")
        print(f"  p_one_tailed = {results['p_one_tailed']:.4f}")
        print(f"  variance_ratio_pre_global = {results['variance_ratio_pre_global']:.4f}")
        print("  Goodhart early-phase exploration mechanism NOT SUPPORTED for this dataset")
    print("=" * 60)

    return 0 if gate_passed else 1


if __name__ == "__main__":
    sys.exit(main())
