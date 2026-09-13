"""
H-C1: Prospective Structural Validity Test

Tests if new trustworthiness benchmarks (holdout) load >= 0.3 on frozen PC1 from H-E1.
SHOULD_WORK gate: Pass if >= 2 holdout benchmarks meet threshold.
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from data_loader import load_h_e1_artifacts, load_trustllm_holdout, match_models
from analysis import compute_pc1_scores, run_all_holdouts, evaluate_gate
from visualization import (
    plot_gate_metrics,
    plot_loading_comparison,
    plot_pc1_scatter,
    plot_loading_heatmap
)


BASE_DIR = Path(__file__).parent.parent
H_E1_DIR = BASE_DIR.parent / "h-e1"
OUTPUT_DIR = BASE_DIR / "outputs"
FIGURES_DIR = BASE_DIR / "figures"


def main():
    print("=" * 60)
    print("H-C1: Prospective Structural Validity Test")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("\n[1/5] Loading H-E1 artifacts...")
    h_e1 = load_h_e1_artifacts(
        results_path=str(H_E1_DIR / "outputs" / "h_e1_results.json"),
        matrix_path=str(H_E1_DIR / "outputs" / "residualized_matrix.csv")
    )
    print(f"  - Loaded PC1 loadings for {len(h_e1['benchmarks'])} benchmarks")
    print(f"  - Residualized matrix: {h_e1['residualized_matrix'].shape}")

    print("\n[2/5] Loading TrustLLM holdout benchmarks...")
    trustllm_df = load_trustllm_holdout(
        h_e1["residualized_matrix"],
        cache_path=str(OUTPUT_DIR / "trustllm_synthetic.parquet")
    )
    holdout_cols = [c for c in trustllm_df.columns if c != "model_name"]
    print(f"  - Holdout benchmarks: {holdout_cols}")
    print(f"  - TrustLLM models: {len(trustllm_df)}")

    print("\n[3/5] Matching models...")
    merged = match_models(h_e1["residualized_matrix"], trustllm_df)
    print(f"  - Matched {len(merged)} models")
    merged.to_csv(OUTPUT_DIR / "matched_models.csv", index=False)

    print("\n[4/5] Computing PC1 scores and holdout loadings...")
    benchmarks = h_e1["benchmarks"]
    loadings_arr = np.array([h_e1["pc1_loadings"][b] for b in benchmarks])

    residual_cols = [c for c in merged.columns if c in benchmarks or c.replace("_h_e1", "") in benchmarks]
    residual_matrix = merged[[c for c in merged.columns if any(c.startswith(b.replace(" ", "_")) or c == b for b in benchmarks)]].values

    h_e1_cols = [c for c in merged.columns if c in benchmarks]
    if not h_e1_cols:
        h_e1_cols = benchmarks
        residual_matrix = merged[h_e1_cols].values

    pc1_scores = compute_pc1_scores(residual_matrix, loadings_arr)
    pc1_std = (pc1_scores - pc1_scores.mean()) / pc1_scores.std()

    holdout_results = run_all_holdouts(pc1_std, merged, holdout_cols)

    for name, data in holdout_results.items():
        status = "PASS" if data["passes_threshold"] else "FAIL"
        print(f"  - {name}: loading={data['loading']:.4f} "
              f"[{data['ci_lower']:.4f}, {data['ci_upper']:.4f}] p={data['p_value']:.4f} [{status}]")

    print("\n[5/5] Evaluating gate and generating outputs...")
    gate = evaluate_gate(holdout_results)
    print(f"  - Gate verdict: {gate['verdict']}")
    print(f"  - Passing benchmarks: {gate['n_passing']}/{gate['n_total']} (need >= {gate['min_required']})")
    print(f"  - Benchmarks meeting threshold: {gate['passing_benchmarks']}")

    results = {
        "hypothesis_id": "H-C1",
        "hypothesis_type": "CONDITION",
        "statement": "Any new trustworthiness benchmark added after PC1 estimation shows loading >= 0.3 on frozen PC1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_models_matched": len(merged),
        "holdout_benchmarks": holdout_cols,
        "holdout_loadings": holdout_results,
        "h_e1_loadings": h_e1["pc1_loadings"],
        "gate": gate,
        "success_criteria": {
            "threshold": 0.3,
            "min_benchmarks": 2,
            "actual_passing": gate["n_passing"],
            "met": gate["verdict"] == "PASS"
        }
    }

    with open(OUTPUT_DIR / "h_c1_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to: {OUTPUT_DIR / 'h_c1_results.json'}")

    print("\n[Visualization] Generating figures...")
    plot_gate_metrics(
        holdout_results, 0.3,
        str(FIGURES_DIR / "gate_metrics.png")
    )

    plot_loading_comparison(
        h_e1["pc1_loadings"], holdout_results,
        str(FIGURES_DIR / "loading_comparison.png")
    )

    plot_pc1_scatter(
        pc1_std, merged, holdout_cols,
        str(FIGURES_DIR / "pc1_scatter.png")
    )

    all_loadings = {**h_e1["pc1_loadings"]}
    for name, data in holdout_results.items():
        all_loadings[f"{name} (holdout)"] = data["loading"]
    plot_loading_heatmap(
        all_loadings,
        str(FIGURES_DIR / "loading_heatmap.png")
    )

    print("\n" + "=" * 60)
    print(f"H-C1 GATE VERDICT: {gate['verdict']}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = main()
    print("\nEXPERIMENT COMPLETE")
