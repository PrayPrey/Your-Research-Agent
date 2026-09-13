"""H-M2 pipeline: post-breakpoint variance compression validation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_CODE_DIR = Path(__file__).parent
_H_M2_DIR = _CODE_DIR.parent
_H_E1_DIR = _H_M2_DIR.parent / "h-e1"

CSV_PATH = _CODE_DIR / "data" / "pwc_cov_computed.csv"
H_E1_JSON = _H_E1_DIR / "experiment_results.json"
RESULTS_PATH = _H_M2_DIR / "experiment_results.json"
FIGURES_DIR = _H_M2_DIR / "figures"

sys.path.insert(0, str(_CODE_DIR))

from data_loader import load_residual_cov, load_paper_count_star_idx
from analyzer import analyze
from verifier import verify_mechanism_activated
from visualizer import save_all_figures


def main() -> int:
    print("=== H-M2: Post-Breakpoint Variance Compression Validation ===")

    if not CSV_PATH.exists():
        print(f"ERROR: Data not found: {CSV_PATH}", file=sys.stderr)
        return 2

    if not H_E1_JSON.exists():
        print("ERROR: H-E1 paper_count* required — run H-E1 first", file=sys.stderr)
        return 2

    print(f"Loading data from {CSV_PATH}")
    paper_counts, residual_cov = load_residual_cov(CSV_PATH)
    print(f"Loaded N={len(paper_counts)} benchmarks")

    if len(residual_cov) < 10:
        print(f"ERROR: Too few observations: N={len(residual_cov)}", file=sys.stderr)
        return 2

    print(f"Loading breakpoint from {H_E1_JSON}")
    paper_count_star_idx = load_paper_count_star_idx(H_E1_JSON, paper_counts, residual_cov)
    print(f"Breakpoint index: {paper_count_star_idx} (paper_count={paper_counts[paper_count_star_idx]})")

    results = analyze(paper_counts, residual_cov, paper_count_star_idx)

    all_pass, indicators = verify_mechanism_activated(results)

    print(f"\nSaving figures to {FIGURES_DIR}")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    figure_paths = save_all_figures(paper_counts, residual_cov, paper_count_star_idx, results, FIGURES_DIR)

    output = dict(results)
    output["figure_paths"] = [str(p) for p in figure_paths]
    output["mechanism_activated"] = all_pass
    output["indicators"] = indicators

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {RESULTS_PATH}")

    print("\n=== FINAL RESULT ===")
    gate_verdict = "PASS" if results["gate_passed"] else "FAIL"
    print(f"Gate: {gate_verdict}")
    print(f"  BF p-value (two-tailed): {results['bf_p_two_tailed']:.4f} (threshold < 0.05)")
    print(f"  Variance ratio (post/pre): {results['variance_ratio']:.4f} (threshold < 1.0)")
    print(f"  n_pre={results['n_pre']}, n_post={results['n_post']}")
    print(f"  var_pre={results['var_pre']:.6f}, var_post={results['var_post']:.6f}")

    return 0 if results["gate_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
