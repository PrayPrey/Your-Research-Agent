import json
import os
from config import CONFIG
from dataset import load_all_problems
from completions import generate_canonical_completions
from eval_pass1 import evaluate_all
from metrics import build_dataframe
from correlate import compute_all_correlations, determine_pass
from visualize import generate_all_figures

def write_results(df, results, gate_passed, best_metric, best_r, best_p):
    os.makedirs(CONFIG.results_dir, exist_ok=True)
    df.to_csv(f"{CONFIG.results_dir}/h_m1_data.csv", index=False)
    with open(f"{CONFIG.results_dir}/h_m1_correlations.json", "w") as f:
        json.dump(results, f, indent=2)
    summary = {
        "n_samples": len(df),
        "gate_passed": gate_passed,
        "best_metric": best_metric,
        "best_r_partial": best_r,
        "best_p_partial": best_p,
        "threshold": CONFIG.corr_threshold,
        "alpha": CONFIG.alpha,
    }
    with open(f"{CONFIG.results_dir}/h_m1_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Results written. N={len(df)}, gate_passed={gate_passed}, best_metric={best_metric}, r={best_r:.4f}, p={best_p:.4f}")

def main():
    print("Loading problems...")
    problems = load_all_problems()
    print(f"Loaded {len(problems)} problems")

    print("Using canonical solutions as completions...")
    completions = generate_canonical_completions(problems)

    print("Evaluating pass@1...")
    passed = evaluate_all(problems, completions)
    pass_rate = sum(passed.values()) / len(passed)
    print(f"Pass rate: {pass_rate:.2%} ({sum(passed.values())}/{len(passed)})")

    print("Building metrics dataframe (SA extraction)...")
    df = build_dataframe(problems, completions, passed)
    print(f"DataFrame shape: {df.shape}")

    assert len(df) >= CONFIG.min_samples, f"Need {CONFIG.min_samples} samples, got {len(df)}"

    print("Computing correlations...")
    results = compute_all_correlations(df)
    gate_passed, best_metric, best_r, best_p = determine_pass(results)

    print("Writing results...")
    write_results(df, results, gate_passed, best_metric, best_r, best_p)

    print("Generating figures...")
    generate_all_figures(df, results)

    print("\n=== EXPERIMENT COMPLETE ===")
    print(f"Gate result: {'PASS' if gate_passed else 'FAIL'}")
    for m, v in results.items():
        print(f"  {m}: r_partial={v['r_partial']:.4f}, p={v['p_partial']:.4f}")

if __name__ == "__main__":
    main()
