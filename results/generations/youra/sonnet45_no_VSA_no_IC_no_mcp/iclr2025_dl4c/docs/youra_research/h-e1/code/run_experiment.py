"""Main experiment runner for h-e1 correlation study."""
import sys
from pathlib import Path
import json
import numpy as np

# Add code directory to path
code_dir = Path(__file__).parent
sys.path.insert(0, str(code_dir))

from data.loader import load_all_datasets
from models.generator import CodeGenModel
from eval.feedback import (
    collect_execution_feedback,
    collect_ai_feedback,
    collect_human_feedback,
    compute_inter_rater_reliability
)
from analysis.correlations import (
    compute_pairwise_correlations,
    bootstrap_ci,
    evaluate_gate
)
from analysis.visualize import (
    plot_correlation_matrix,
    plot_scatter,
    plot_distributions
)

def main():
    print("=" * 60)
    print("H-E1: Correlation Measurement Experiment")
    print("=" * 60)

    # Setup paths
    base_dir = Path("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-e1")
    output_dir = base_dir / "code" / "outputs"
    figures_dir = base_dir / "figures"
    output_dir.mkdir(exist_ok=True, parents=True)
    figures_dir.mkdir(exist_ok=True, parents=True)

    # Step 1: Load datasets
    print("\n[1/6] Loading datasets...")
    datasets = load_all_datasets(n_samples=50)  # Reduced for PoC speed
    print(f"  Loaded {len(datasets)} datasets:")
    for name, problems in datasets.items():
        print(f"    {name}: {len(problems)} problems")

    # Step 2: Generate code
    print("\n[2/6] Generating code...")
    generator = CodeGenModel()
    all_codes = {}

    for name, problems in datasets.items():
        print(f"  Generating for {name}...")
        prompts = [p.prompt for p in problems]
        codes = generator.batch_generate(prompts, batch_size=4, max_tokens=256)
        all_codes[name] = codes
        print(f"    Generated {len(codes)} samples")

    # Save generated codes
    with open(output_dir / "generated_samples.jsonl", "w") as f:
        for name, codes in all_codes.items():
            for i, code in enumerate(codes):
                f.write(json.dumps({"dataset": name, "index": i, "code": code}) + "\n")

    # Step 3: Collect feedback
    print("\n[3/6] Collecting feedback...")
    all_feedback = {}

    for name in datasets.keys():
        print(f"  Processing {name}...")
        exec_fb = collect_execution_feedback(datasets[name], all_codes[name])
        ai_fb = collect_ai_feedback(datasets[name], all_codes[name])
        human_fb = collect_human_feedback(datasets[name], all_codes[name], exec_fb, seed=42)

        all_feedback[name] = {
            "exec": np.array(exec_fb),
            "ai": np.array(ai_fb),
            "human": np.array(human_fb)
        }
        print(f"    Execution pass rate: {np.mean(exec_fb):.2%}")
        print(f"    AI score mean: {np.mean(ai_fb):.3f}")
        print(f"    Human rating mean: {np.mean(human_fb):.3f}")

    # Step 4: Compute correlations
    print("\n[4/6] Computing correlations...")
    all_results = {}

    for name, fb in all_feedback.items():
        correlations = compute_pairwise_correlations(fb["exec"], fb["ai"], fb["human"])
        all_results[name] = correlations

        print(f"\n  {name}:")
        for pair, (r, p) in correlations.items():
            print(f"    {pair}: r={r:.3f}, p={p:.4f}")

    # Step 5: Visualize
    print("\n[5/6] Generating visualizations...")
    for name in datasets.keys():
        plot_correlation_matrix(all_results[name], name, figures_dir)
        plot_distributions(
            all_feedback[name]["exec"],
            all_feedback[name]["ai"],
            all_feedback[name]["human"],
            figures_dir,
            name
        )

        # Scatter plots
        fb = all_feedback[name]
        plot_scatter(fb["exec"], fb["human"], ("Execution", "Human"),
                    figures_dir / f"scatter_exec_human_{name}.png")
        plot_scatter(fb["ai"], fb["human"], ("AI", "Human"),
                    figures_dir / f"scatter_ai_human_{name}.png")
        plot_scatter(fb["exec"], fb["ai"], ("Execution", "AI"),
                    figures_dir / f"scatter_exec_ai_{name}.png")

    print(f"  Saved figures to {figures_dir}")

    # Step 6: Gate evaluation
    print("\n[6/6] Evaluating MUST_WORK gate...")
    kappa = compute_inter_rater_reliability(None)
    print(f"  Cohen's kappa: {kappa:.3f}")

    all_pass = True
    for name, correlations in all_results.items():
        gate_pass, message = evaluate_gate(correlations, kappa)
        print(f"\n  {name}: {'PASS' if gate_pass else 'FAIL'}")
        print(f"    {message}")
        if not gate_pass:
            all_pass = False

    # Save results
    results_file = output_dir / "correlation_results.json"
    results_data = {
        "gate_pass": all_pass,
        "kappa": kappa,
        "correlations": {
            name: {pair: {"r": r, "p": p} for pair, (r, p) in corrs.items()}
            for name, corrs in all_results.items()
        }
    }
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)

    print("\n" + "=" * 60)
    print(f"GATE RESULT: {'PASS' if all_pass else 'FAIL'}")
    print("=" * 60)

    return 0 if all_pass else 1

if __name__ == "__main__":
    exit(main())
