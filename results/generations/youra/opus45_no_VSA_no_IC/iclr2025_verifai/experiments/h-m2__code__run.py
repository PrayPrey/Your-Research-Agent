import os
import json
from config import CONFIG
from data_loader import load_h_m1_data
from optimize import grid_search_weights
from ensemble import compute_ensemble_score
from visualize import generate_all_figures

def main():
    print("Loading h-m1 data...")
    df = load_h_m1_data()
    print(f"  Loaded {len(df)} samples")

    print("Running grid search...")
    best_weights, best_r, best_p, weight_r_pairs = grid_search_weights(df)
    print(f"  Best weights: {best_weights}")
    print(f"  Best r: {best_r:.4f}, p: {best_p:.6f}")

    gate = best_r > CONFIG.max_r_individual and best_p < CONFIG.alpha
    print(f"Gate evaluation: r_ensemble={best_r:.4f} > max_r_individual={CONFIG.max_r_individual} AND p={best_p:.6f} < {CONFIG.alpha}")
    print(f"  Gate PASSED: {gate}")

    os.makedirs(CONFIG.results_dir, exist_ok=True)

    results = {
        "best_weights": best_weights,
        "best_r": best_r,
        "best_p": best_p,
        "max_r_individual": CONFIG.max_r_individual,
        "gate_passed": gate,
        "weight_r_pairs": weight_r_pairs,
        "n_samples": len(df),
    }
    with open(os.path.join(CONFIG.results_dir, "h_m2_ensemble.json"), "w") as f:
        json.dump(results, f, indent=2)

    df_final = compute_ensemble_score(df, best_weights)
    df_final.to_csv(os.path.join(CONFIG.results_dir, "h_m2_data.csv"), index=False)

    summary = {
        "hypothesis": "h-m2",
        "statement": "Weighted ensemble of SA metrics achieves higher correlation with pass@1 than any single metric",
        "result": "PASS" if gate else "FAIL",
        "r_ensemble": best_r,
        "r_max_individual": CONFIG.max_r_individual,
        "improvement": best_r - CONFIG.max_r_individual if gate else None,
        "p_value": best_p,
        "optimal_weights": best_weights,
    }
    with open(os.path.join(CONFIG.results_dir, "h_m2_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print("Generating figures...")
    generate_all_figures(best_r, CONFIG.max_r_individual, weight_r_pairs)

    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"Result: {'PASS' if gate else 'FAIL'}")
    print(f"r_ensemble: {best_r:.4f}")
    print(f"max(r_individual): {CONFIG.max_r_individual:.4f}")
    if gate:
        print(f"Improvement: +{best_r - CONFIG.max_r_individual:.4f}")
    print(f"p-value: {best_p:.6f}")

    return gate, results

if __name__ == "__main__":
    main()
