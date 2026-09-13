"""Fast experiment: AI-critic vs random baseline (HumanEval subset for PoC)."""

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

# PoC subset: 100 problems for statistically meaningful comparison
SAMPLE_SIZE = 100


def run_experiment():
    """Run h-e2 PoC experiment on subset."""
    random.seed(config.SEED)

    print("=" * 60)
    print("h-e2: AI-Critic vs Random Baseline (PoC Subset)")
    print(f"Sample size: {SAMPLE_SIZE} problems (HumanEval + MBPP sample)")
    print("=" * 60)

    # Load model
    print("\nLoading CodeLlama-7B-Instruct...")
    llm = CodeLLM(config.MODEL_ID)

    # Initialize refinement loops
    ai_critic = AICriticRefinement(llm, k=config.K_ITERS)
    random_baseline = RandomFeedbackRefinement(llm, k=config.K_ITERS)

    # Load and sample datasets
    humaneval = load_problems("humaneval")
    mbpp = load_problems("mbpp")

    # Sample 50 from each
    random.shuffle(humaneval)
    random.shuffle(mbpp)
    problems = humaneval[:50] + mbpp[:50]
    random.shuffle(problems)

    print(f"Sampled {len(problems)} problems (50 HumanEval + 50 MBPP)")

    # Results storage
    all_results = {
        "zero_shot": [],
        "ai_critic": [],
        "random_baseline": [],
    }

    iteration_curves = {
        "ai_critic": [0] * (config.K_ITERS + 1),
        "random_baseline": [0] * (config.K_ITERS + 1),
    }

    for prob in tqdm(problems, desc="Processing"):
        pid = prob["id"]
        prompt = prob["prompt"]
        test = prob["test"]
        entry = prob["entry_point"]

        # 1. Zero-shot (same as AI-critic iteration 0)
        zero_code = ai_critic.generate_initial(prompt)
        zero_pass = run_tests(zero_code, test, entry)
        all_results["zero_shot"].append({"id": pid, "passed": zero_pass})

        # 2. AI Critic refinement
        ai_snapshots = ai_critic.run(prompt)
        for k, code in enumerate(ai_snapshots):
            if run_tests(code, test, entry):
                iteration_curves["ai_critic"][k] += 1
        ai_pass = run_tests(ai_snapshots[-1], test, entry)
        all_results["ai_critic"].append({"id": pid, "passed": ai_pass})

        # 3. Random baseline refinement
        rand_snapshots = random_baseline.run(prompt)
        for k, code in enumerate(rand_snapshots):
            if run_tests(code, test, entry):
                iteration_curves["random_baseline"][k] += 1
        rand_pass = run_tests(rand_snapshots[-1], test, entry)
        all_results["random_baseline"].append({"id": pid, "passed": rand_pass})

    # Compute pass@1 rates
    n = len(problems)
    pass_rates = {
        cond: compute_pass_at_1(results)
        for cond, results in all_results.items()
    }

    # Normalize iteration curves
    for key in iteration_curves:
        iteration_curves[key] = [c / n for c in iteration_curves[key]]

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
    print(f"  Difference: {ai_rate - rand_rate:.4f} ({(ai_rate - rand_rate) / max(rand_rate, 0.001) * 100:.1f}%)")
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
            "sample_size": SAMPLE_SIZE,
        },
        "pass_rates": pass_rates,
        "iteration_curves": iteration_curves,
        "gate_result": "PASS" if gate_pass else "FAIL",
        "total_problems": n,
        "detailed_results": all_results,
    }

    with open("../experiment_results.json", "w") as f:
        json.dump(results_data, f, indent=2)
    print("Results saved to experiment_results.json")

    return gate_pass, pass_rates


if __name__ == "__main__":
    gate_pass, pass_rates = run_experiment()
    print("\nEXPERIMENT COMPLETE")
