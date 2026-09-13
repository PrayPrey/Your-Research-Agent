import os
import sys
sys.stdout.reconfigure(line_buffering=True)
import json
from dataset import load_all_problems
from config import CONFIG
from multi_model_data import build_multi_model_dataframe
from cross_correlate import compute_per_model_correlations, cross_model_variance, determine_gate_pass
from visualize import generate_all_figures

def write_results(df, correlations_pylint, correlations_radon, mean_r, std_r, min_r, gate_passed):
    os.makedirs(CONFIG.results_dir, exist_ok=True)
    df.to_csv(f"{CONFIG.results_dir}/h_c1_data.csv", index=False)
    results = {
        "pylint_score": {m: {"r": r, "p": p} for m, (r, p) in correlations_pylint.items()},
        "radon_cc": {m: {"r": r, "p": p} for m, (r, p) in correlations_radon.items()},
    }
    with open(f"{CONFIG.results_dir}/h_c1_correlations.json", "w") as f:
        json.dump(results, f, indent=2)
    summary = {
        "n_models": len(correlations_pylint),
        "n_samples_total": len(df),
        "gate_passed": gate_passed,
        "pylint_mean_r": mean_r,
        "pylint_std_r": std_r,
        "pylint_min_r": min_r,
        "variance_threshold": CONFIG.variance_threshold,
        "mean_r_threshold": CONFIG.mean_r_threshold,
        "min_r_threshold": CONFIG.min_r_threshold,
    }
    with open(f"{CONFIG.results_dir}/h_c1_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    return summary

def main():
    print("Loading problems...")
    problems = load_all_problems()
    print(f"Loaded {len(problems)} problems")

    print("Building multi-model dataframe...")
    df = build_multi_model_dataframe(list(CONFIG.models), problems, CONFIG.completions_dir)
    print(f"Combined DataFrame: {len(df)} samples across {df['model_id'].nunique()} models")

    print("Computing per-model correlations (pylint_score)...")
    correlations_pylint = compute_per_model_correlations(df, "pylint_score")
    for m, (r, p) in correlations_pylint.items():
        print(f"  {m}: r={r:.4f}, p={p:.4e}")

    print("Computing per-model correlations (radon_cc)...")
    correlations_radon = compute_per_model_correlations(df, "radon_cc")
    for m, (r, p) in correlations_radon.items():
        print(f"  {m}: r={r:.4f}, p={p:.4e}")

    print("Computing cross-model variance...")
    mean_r, std_r, min_r = cross_model_variance(correlations_pylint)
    print(f"pylint_score: mean_r={mean_r:.4f}, std_r={std_r:.4f}, min_r={min_r:.4f}")

    gate_passed = determine_gate_pass(mean_r, std_r, min_r)
    print(f"\nGate check: std_r < {CONFIG.variance_threshold} AND mean_r > {CONFIG.mean_r_threshold} AND min_r > {CONFIG.min_r_threshold}")
    print(f"Result: {std_r:.4f} < {CONFIG.variance_threshold} = {std_r < CONFIG.variance_threshold}")
    print(f"        {mean_r:.4f} > {CONFIG.mean_r_threshold} = {mean_r > CONFIG.mean_r_threshold}")
    print(f"        {min_r:.4f} > {CONFIG.min_r_threshold} = {min_r > CONFIG.min_r_threshold}")

    print("Writing results...")
    summary = write_results(df, correlations_pylint, correlations_radon, mean_r, std_r, min_r, gate_passed)

    print("Generating figures...")
    generate_all_figures(df, correlations_pylint, correlations_radon)

    print("\n=== EXPERIMENT COMPLETE ===")
    print(f"Gate result: {'PASS' if gate_passed else 'FAIL'}")
    print(f"Models: {list(correlations_pylint.keys())}")
    print(f"pylint_score variance: std(r)={std_r:.4f} (threshold: {CONFIG.variance_threshold})")
    return gate_passed

if __name__ == "__main__":
    main()
