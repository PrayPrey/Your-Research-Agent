"""Micro PoC: AI-critic vs random baseline (5 problems, verify mechanism)."""

import json
import os
import random
from datetime import datetime

import config
from data import load_problems
from model import CodeLLM
from refine import AICriticRefinement, RandomFeedbackRefinement
from evaluate import run_tests, compute_pass_at_1, plot_comparison, plot_iteration_curve

SAMPLE_SIZE = 5


def run_experiment():
    """Run h-e2 micro PoC - verify mechanism works."""
    random.seed(config.SEED)

    print("=" * 60)
    print("h-e2: AI-Critic vs Random Baseline (MICRO PoC)")
    print(f"Sample size: {SAMPLE_SIZE} problems")
    print("=" * 60)

    print("\nLoading CodeLlama-7B-Instruct...")
    llm = CodeLLM(config.MODEL_ID)

    ai_critic = AICriticRefinement(llm, k=config.K_ITERS)
    random_baseline = RandomFeedbackRefinement(llm, k=config.K_ITERS)

    humaneval = load_problems("humaneval")
    random.shuffle(humaneval)
    problems = humaneval[:SAMPLE_SIZE]

    print(f"Sampled {len(problems)} HumanEval problems")

    results = {"zero_shot": [], "ai_critic": [], "random_baseline": []}
    curves = {
        "ai_critic": [0] * (config.K_ITERS + 1),
        "random_baseline": [0] * (config.K_ITERS + 1),
    }

    for i, prob in enumerate(problems):
        print(f"[{i+1}/{SAMPLE_SIZE}] {prob['id']}", flush=True)
        prompt, test, entry = prob["prompt"], prob["test"], prob["entry_point"]

        # Zero-shot
        zero_code = ai_critic.generate_initial(prompt)
        zero_pass = run_tests(zero_code, test, entry)
        results["zero_shot"].append({"id": prob["id"], "passed": zero_pass})

        # AI Critic
        ai_snaps = ai_critic.run(prompt)
        for k, code in enumerate(ai_snaps):
            if run_tests(code, test, entry):
                curves["ai_critic"][k] += 1
        ai_pass = run_tests(ai_snaps[-1], test, entry)
        results["ai_critic"].append({"id": prob["id"], "passed": ai_pass})

        # Random baseline
        rand_snaps = random_baseline.run(prompt)
        for k, code in enumerate(rand_snaps):
            if run_tests(code, test, entry):
                curves["random_baseline"][k] += 1
        rand_pass = run_tests(rand_snaps[-1], test, entry)
        results["random_baseline"].append({"id": prob["id"], "passed": rand_pass})

    # Compute metrics
    n = len(problems)
    pass_rates = {k: compute_pass_at_1(v) for k, v in results.items()}
    for key in curves:
        curves[key] = [c / n for c in curves[key]]

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for cond, rate in pass_rates.items():
        print(f"  {cond}: {rate:.4f}")

    ai_rate = pass_rates["ai_critic"]
    rand_rate = pass_rates["random_baseline"]
    gate_pass = ai_rate > rand_rate

    print(f"\nGATE CHECK (MUST_WORK):")
    print(f"  AI Critic: {ai_rate:.4f}")
    print(f"  Random Baseline: {rand_rate:.4f}")
    print(f"  AI > Random: {gate_pass}")
    print(f"  GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")

    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    plot_comparison(pass_rates, os.path.join(config.FIGURES_DIR, "pass_at_1_comparison.png"))
    plot_iteration_curve(curves, os.path.join(config.FIGURES_DIR, "iteration_curve.png"))

    results_data = {
        "hypothesis": "h-e2",
        "timestamp": datetime.now().isoformat(),
        "config": {"model_id": config.MODEL_ID, "k_iters": config.K_ITERS,
                   "temperature": config.TEMPERATURE, "seed": config.SEED,
                   "sample_size": SAMPLE_SIZE},
        "pass_rates": pass_rates,
        "iteration_curves": curves,
        "gate_result": "PASS" if gate_pass else "FAIL",
        "total_problems": n,
        "detailed_results": results,
    }

    with open("../experiment_results.json", "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\nResults saved to experiment_results.json")

    return gate_pass, pass_rates


if __name__ == "__main__":
    gate_pass, _ = run_experiment()
    print("\nMICRO POC COMPLETE")
    exit(0 if gate_pass else 1)
