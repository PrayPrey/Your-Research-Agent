"""Main entry point for H-M2 DiD experiment."""
import json
import csv
import sys
from pathlib import Path

from config import Config
from models import load_rl_ce_models
from evaluator import run_all_conditions
from did_analysis import bootstrap_did_ci, per_error_type_did, per_problem_effect_sizes, cell_means
from visualize import plot_2x2_bar, plot_did_ci, plot_error_type_did, plot_effect_hist

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-e1" / "code"))
from data import load_humaneval_plus


def main():
    print("H-M2 DiD Semantic Sensitivity Experiment")
    print("=" * 50)

    cfg = Config()

    print(f"RL checkpoint: {cfg.rl_checkpoint}")
    print(f"CE checkpoint: {cfg.ce_checkpoint}")

    if not cfg.rl_checkpoint.exists() or not cfg.ce_checkpoint.exists():
        print("ERROR: H-E1 checkpoints not found. Run H-E1 first.")
        sys.exit(1)

    print("\nLoading models...")
    models = load_rl_ce_models(cfg)

    print("\nLoading HumanEval+ dataset...")
    problems = load_humaneval_plus(cfg)
    print(f"Loaded {len(problems)} problems")

    print("\nRunning evaluation across all conditions...")
    all_results = run_all_conditions(models, problems, cfg)
    print(f"Collected {len(all_results)} result rows")

    print("\nComputing statistics...")
    means = cell_means(all_results)
    for k, v in means.items():
        print(f"  {k}: {v:.4f}")

    print("\nBootstrap DiD analysis...")
    did_result = bootstrap_did_ci(all_results, cfg.n_bootstrap, cfg.alpha, seed=42)
    print(f"  DiD contrast: {did_result['did_contrast']:.4f}")
    print(f"  95% CI: [{did_result['ci_lower']:.4f}, {did_result['ci_upper']:.4f}]")
    print(f"  Significant (CI > 0): {did_result['significant']}")
    print(f"  p-value (one-sided): {did_result['p_value_one_sided']:.4f}")

    error_type_did = per_error_type_did(all_results)
    print(f"\nPer-error-type DiD: {error_type_did}")

    effects = per_problem_effect_sizes(all_results)
    print(f"Per-problem effects: mean={sum(effects)/len(effects) if effects else 0:.4f}, n={len(effects)}")

    print("\nSaving results...")
    results_data = {
        "cell_means": means,
        "did_result": {k: v for k, v in did_result.items() if k != "boot_samples"},
        "error_type_did": error_type_did,
        "n_problems": len(problems),
        "n_results": len(all_results),
    }
    with open(cfg.outputs_dir / "results.json", "w") as f:
        json.dump(results_data, f, indent=2)

    with open(cfg.outputs_dir / "results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["problem_id", "model", "condition", "single_shot_pass", "refined_pass", "error_type"])
        writer.writeheader()
        writer.writerows(all_results)

    print("\nGenerating visualizations...")
    plot_2x2_bar(means, cfg.figures_dir / "did_bar_chart.png")
    plot_did_ci(did_result, cfg.figures_dir / "did_contrast_ci.png")
    plot_error_type_did(error_type_did, cfg.figures_dir / "error_type_did.png")
    plot_effect_hist(effects, cfg.figures_dir / "effect_size_hist.png")

    print(f"\nResults saved to: {cfg.outputs_dir}")
    print(f"Figures saved to: {cfg.figures_dir}")

    gate_pass = did_result["did_contrast"] > 0
    print(f"\n{'='*50}")
    print(f"GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")
    print(f"DiD > 0: {did_result['did_contrast']:.4f} > 0 = {gate_pass}")
    print(f"Statistically significant: {did_result['significant']}")

    return gate_pass, results_data


if __name__ == "__main__":
    main()
