"""Main experiment: AI-critic vs random baseline refinement."""

import json
import os
import random
from datetime import datetime
from tqdm import tqdm

import config
from data import load_problems
from model import CodeLLM
from refine import AICriticRefinement, RandomFeedbackRefinement
from evaluate import run_tests, compute_pass_at_1, plot_comparison, plot_iteration_curve


def run_experiment():
    """Run full h-e2 experiment."""
    random.seed(config.SEED)

    print("=" * 60)
    print("h-e2: AI-Critic vs Random Baseline Experiment")
    print("=" * 60)

    # Load model
    print("\nLoading CodeLlama-7B-Instruct...")
    llm = CodeLLM(config.MODEL_ID)

    # Initialize refinement loops
    ai_critic = AICriticRefinement(llm, k=config.K_ITERS)
    random_baseline = RandomFeedbackRefinement(llm, k=config.K_ITERS)

    # Load datasets
    all_results = {
        "zero_shot": [],
        "ai_critic": [],
        "random_baseline": [],
    }

    iteration_curves = {
        "ai_critic": [0.0] * (config.K_ITERS + 1),
        "random_baseline": [0.0] * (config.K_ITERS + 1),
    }
    iteration_counts = [0] * (config.K_ITERS + 1)

    for ds_name in ["humaneval", "mbpp"]:
        print(f"\nProcessing {ds_name}...")
        problems = load_problems(ds_name)
        print(f"  Loaded {len(problems)} problems")

        for prob in tqdm(problems, desc=f"  {ds_name}"):
            pid = prob["id"]
            prompt = prob["prompt"]
            test = prob["test"]
            entry = prob["entry_point"]

            # 1. Zero-shot
            zero_code = ai_critic.generate_initial(prompt)
            zero_pass = run_tests(zero_code, test, entry)
            all_results["zero_shot"].append({
                "id": pid, "dataset": ds_name, "passed": zero_pass
            })

            # 2. AI Critic refinement
            ai_snapshots = ai_critic.run(prompt)
            for k, code in enumerate(ai_snapshots):
                passed = run_tests(code, test, entry)
                if passed:
                    iteration_curves["ai_critic"][k] += 1
                iteration_counts[k] += 1
            ai_pass = run_tests(ai_snapshots[-1], test, entry)
            all_results["ai_critic"].append({
                "id": pid, "dataset": ds_name, "passed": ai_pass,
                "iterations": len(ai_snapshots) - 1
            })

            # 3. Random baseline refinement
            rand_snapshots = random_baseline.run(prompt)
            for k, code in enumerate(rand_snapshots):
                passed = run_tests(code, test, entry)
                if passed:
                    iteration_curves["random_baseline"][k] += 1
            rand_pass = run_tests(rand_snapshots[-1], test, entry)
            all_results["random_baseline"].append({
                "id": pid, "dataset": ds_name, "passed": rand_pass,
                "iterations": len(rand_snapshots) - 1
            })

    # Compute pass@1 rates
    pass_rates = {
        cond: compute_pass_at_1(results)
        for cond, results in all_results.items()
    }

    # Normalize iteration curves
    for key in iteration_curves:
        iteration_curves[key] = [
            iteration_curves[key][k] / iteration_counts[k] if iteration_counts[k] > 0 else 0.0
            for k in range(config.K_ITERS + 1)
        ]

    # Results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for cond, rate in pass_rates.items():
        print(f"  {cond}: {rate:.4f}")

    # Gate check
    ai_rate = pass_rates["ai_critic"]
    rand_rate = pass_rates["random_baseline"]
    gate_pass = ai_rate > rand_rate

    print(f"\nGATE CHECK (MUST_WORK):")
    print(f"  AI Critic pass@1: {ai_rate:.4f}")
    print(f"  Random Baseline pass@1: {rand_rate:.4f}")
    print(f"  AI > Random: {gate_pass}")
    print(f"  GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")

    # Save figures
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    plot_comparison(pass_rates, os.path.join(config.FIGURES_DIR, "pass_at_1_comparison.png"))
    plot_iteration_curve(iteration_curves, os.path.join(config.FIGURES_DIR, "iteration_curve.png"))
    print(f"\nFigures saved to {config.FIGURES_DIR}")

    # Save results
    results_data = {
        "hypothesis": "h-e2",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "model_id": config.MODEL_ID,
            "k_iters": config.K_ITERS,
            "temperature": config.TEMPERATURE,
            "seed": config.SEED,
        },
        "pass_rates": pass_rates,
        "iteration_curves": iteration_curves,
        "gate_result": "PASS" if gate_pass else "FAIL",
        "total_problems": len(all_results["zero_shot"]),
        "detailed_results": all_results,
    }

    with open("../experiment_results.json", "w") as f:
        json.dump(results_data, f, indent=2)
    print("Results saved to experiment_results.json")

    return gate_pass, pass_rates


if __name__ == "__main__":
    gate_pass, pass_rates = run_experiment()
    print("\nEXPERIMENT COMPLETE")
