"""analyze.py — A-6: Main pipeline orchestrator for H-M3 correlation analysis."""
import json
import sys
from pathlib import Path
from datetime import datetime
import numpy as np

# Allow running as a script from the code/ directory or the h-m3/ directory
CODE_DIR = Path(__file__).parent
HM3_DIR = CODE_DIR.parent
RESEARCH_DIR = HM3_DIR.parent

sys.path.insert(0, str(CODE_DIR))

from data_loader import (
    load_accuracy_differentials,
    load_contamination_estimates,
    load_mink_differentials,
    build_analysis_vectors,
    validate_inputs,
    BENCHMARKS,
    MODEL_SIZES,
)
from correlation import pearson_spearman, bootstrap_ci, directional_check
from ablations import (
    ablation_estimator_comparison,
    ablation_aggregation_strategy,
    ablation_token_vs_step,
    ablation_per_model_size,
)
from visualize import (
    plot_scatter,
    plot_correlation_heatmap,
    plot_per_benchmark_bars,
    plot_bootstrap_ci,
    plot_spearman_ranks,
)
from report_generator import (
    determine_gate_result,
    save_experiment_results,
    generate_markdown_report,
)

FIGURES_DIR = str(HM3_DIR / "figures")
RESULTS_DIR = str(HM3_DIR / "results")


def run_analysis(
    h_e1_folder: str,
    h_m1_folder: str,
    h_m2_folder: str,
) -> dict:
    print("=" * 60)
    print("H-M3 Contamination-Accuracy Correlation Analysis")
    print("=" * 60)

    # Step 1: Load inputs
    print("\n[1/6] Loading inputs...")
    acc_diff = load_accuracy_differentials(h_e1_folder)
    cont_est = load_contamination_estimates(h_m1_folder)
    validate_inputs(acc_diff, cont_est)

    # Determine source of contamination estimates
    cont_source = "H-M1 experiment" if Path(h_m1_folder, "contamination_estimates.json").exists() \
        else "literature (Lee et al. 2022, GPT-4 TR)"

    mink_diff = None
    try:
        mink_diff = load_mink_differentials(h_m2_folder)
    except Exception as e:
        print(f"  Warning: H-M2 min-k% load failed ({e}) — proceeding without secondary estimator")

    # Step 2: Build analysis vectors
    print("\n[2/6] Building analysis vectors...")
    cont_vec = np.array([cont_est[b] for b in BENCHMARKS])
    cont_repeated, diff_flat, diff_matrix = build_analysis_vectors(acc_diff, cont_est)
    print(f"  cont_repeated shape: {cont_repeated.shape}")
    print(f"  diff_flat shape: {diff_flat.shape}")
    print(f"  diff_matrix shape: {diff_matrix.shape}")

    # Step 3: Primary correlation
    print("\n[3/6] Primary correlation analysis...")
    primary_result = pearson_spearman(cont_repeated, diff_flat)
    ci_tuple, boot_r_dist = bootstrap_ci(cont_repeated, diff_flat, n_resamples=1000, seed=42)
    primary_result.bootstrap_ci_95 = ci_tuple

    dir_result = directional_check(cont_vec, diff_matrix)

    print(f"  Contamination-accuracy correlation computed: "
          f"Pearson r={primary_result.pearson_r:.3f}, p={primary_result.pearson_p:.4f}")
    print(f"  Spearman ρ={primary_result.spearman_rho:.3f}, p={primary_result.spearman_p:.4f}")
    print(f"  Bootstrap 95% CI: [{ci_tuple[0]:.3f}, {ci_tuple[1]:.3f}]")
    print(f"  Directional concordance: {dir_result['n_correct_direction']:.3f}")

    # Step 4: Ablation studies
    print("\n[4/6] Running ablation studies...")
    ablation_est = ablation_estimator_comparison(acc_diff, cont_est, mink_diff)
    ablation_agg = ablation_aggregation_strategy(cont_vec, diff_matrix)
    ablation_tvs = ablation_token_vs_step(acc_diff, None, cont_vec)  # No step-matched from H-E1
    ablation_pms = ablation_per_model_size(acc_diff, cont_vec)
    print("  All 4 ablations completed")

    # Step 5: Visualizations
    print("\n[5/6] Generating figures...")
    diff_mean_per_bench = diff_matrix.mean(axis=0)  # (4,)

    plot_scatter(
        cont_vec, diff_mean_per_bench,
        primary_result.pearson_r, primary_result.pearson_p,
        BENCHMARKS,
        f"{FIGURES_DIR}/fig_scatter_contamination_vs_differential.png",
    )

    # Correlation heatmap: build r_matrix (2 estimators × 4 model sizes)
    r_per_size_13gram = [ablation_pms[m]["pearson_r"] for m in MODEL_SIZES]
    if ablation_est.get("mink"):
        from ablations import ablation_per_model_size as _pms
        mink_cont = {b: mink_diff[b] for b in BENCHMARKS} if mink_diff else None
        if mink_cont:
            mink_cont_vec = np.array([mink_cont[b] for b in BENCHMARKS])
            r_per_size_mink = []
            for m in MODEL_SIZES:
                diff_vec = np.array([acc_diff[m][b] for b in BENCHMARKS])
                res = pearson_spearman(mink_cont_vec, diff_vec)
                r_per_size_mink.append(res.pearson_r)
        else:
            r_per_size_mink = [0.0] * 4
    else:
        r_per_size_mink = [0.0] * 4

    r_matrix = np.array([r_per_size_13gram, r_per_size_mink])  # (2, 4)
    plot_correlation_heatmap(
        r_matrix,
        estimator_labels=["13-gram overlap", "min-k% diff"],
        model_size_labels=MODEL_SIZES,
        save_path=f"{FIGURES_DIR}/fig_correlation_heatmap.png",
    )

    plot_per_benchmark_bars(
        diff_matrix, cont_vec, BENCHMARKS, MODEL_SIZES,
        f"{FIGURES_DIR}/fig_per_benchmark_bars.png",
    )

    plot_bootstrap_ci(
        boot_r_dist, ci_tuple[0], ci_tuple[1], primary_result.pearson_r,
        f"{FIGURES_DIR}/fig_bootstrap_ci.png",
    )

    plot_spearman_ranks(
        cont_vec, diff_mean_per_bench, BENCHMARKS,
        f"{FIGURES_DIR}/fig_spearman_ranks.png",
    )

    # Step 6: Gate verdict and report
    print("\n[6/6] Gate verdict and report...")
    gate = determine_gate_result(primary_result.pearson_r, primary_result.pearson_p)
    print(f"  Gate result: {gate['result']} — {gate['reasoning']}")

    # Assemble full results
    results = {
        "hypothesis_id": "h-m3",
        "timestamp": datetime.now().isoformat(),
        "gate": gate,
        "primary_correlation": primary_result.to_dict(),
        "directional_check": dir_result,
        "ablations": {
            "estimator_comparison": ablation_est,
            "aggregation_strategy": ablation_agg,
            "token_vs_step": ablation_tvs,
            "per_model_size": ablation_pms,
        },
        "contamination_estimates": cont_est,
        "contamination_source": cont_source,
        "accuracy_differentials": acc_diff,
        "vectors": {
            "cont_vec": cont_vec.tolist(),
            "cont_repeated": cont_repeated.tolist(),
            "diff_flat": diff_flat.tolist(),
            "diff_matrix": diff_matrix.tolist(),
            "diff_mean_per_benchmark": diff_mean_per_bench.tolist(),
        },
    }

    save_experiment_results(results, f"{RESULTS_DIR}/experiment_results.json")
    generate_markdown_report(results, str(HM3_DIR / "04_validation.md"))

    print("\n" + "=" * 60)
    print(f"ANALYSIS COMPLETE")
    print(f"Gate: {gate['result']}")
    print(f"Pearson r = {primary_result.pearson_r:.4f} (p = {primary_result.pearson_p:.4f})")
    print("=" * 60)
    return results


if __name__ == "__main__":
    h_e1 = str(RESEARCH_DIR / "h-e1")
    h_m1 = str(RESEARCH_DIR / "h-m1")
    h_m2 = str(RESEARCH_DIR / "h-m2")
    results = run_analysis(h_e1, h_m1, h_m2)
    sys.exit(0)
