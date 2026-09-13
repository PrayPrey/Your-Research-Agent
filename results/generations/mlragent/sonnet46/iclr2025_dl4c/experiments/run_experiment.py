"""
Main experiment script for HierAlign: Hierarchical Execution Feedback for Code Alignment.

Experimental design:
- Generate multiple code solutions per problem at different quality levels using a small LLM
- Score each solution with different reward models
- Compare discriminability and correlation with true quality across reward models
- Show that hierarchical reward provides better signal than binary pass/fail

Key metrics:
1. Reward discriminability: How well does the reward differentiate good from bad solutions?
2. Kendall-tau correlation with ground truth ranking
3. Reward signal for partial solutions (binary gives 0, hierarchical gives gradient)
4. Reward-guided selection rate
"""

import os
import json
import time
import logging
import sys
import numpy as np
from pathlib import Path
from data import get_problems
from reward_models import get_reward_model
from utils import extract_code_from_response

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Model configuration
MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct"


def load_model():
    """Load a small code LLM from HuggingFace."""
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch

    logger.info(f"Loading model: {MODEL_NAME}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None,
        trust_remote_code=True,
    )
    model.eval()

    return model, tokenizer, device


def generate_solution(model, tokenizer, device, problem, temperature=0.7, max_new_tokens=512):
    """Generate a single code solution using the model."""
    import torch

    prompt = f"""You are an expert Python programmer. Write a complete Python function for the following task.

Task: {problem['prompt']}

Write only the Python function, no explanation or markdown:
"""

    messages = [
        {"role": "system", "content": "You are a helpful Python programming assistant. Write clean, correct Python code."},
        {"role": "user", "content": prompt}
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(text, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=(temperature > 0),
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated = outputs[0][inputs["input_ids"].shape[1]:]
    response = tokenizer.decode(generated, skip_special_tokens=True)
    code = extract_code_from_response(response)

    # If no code block found, use response as-is
    if not code:
        code = response.strip()

    return code


def generate_solutions_at_quality_levels(model, tokenizer, device, problem, n_per_level=2):
    """
    Generate solutions at 3 quality levels for a problem using temperature control:
    - High quality: low temperature (0.1) for precise, correct code
    - Medium quality: medium temperature (0.7) for typical generation
    - Low quality: high temperature (1.5) for noisy, potentially incorrect code
    """
    solutions = []
    temperature_by_level = {
        "high": 0.1,   # Low temp = more precise, likely correct
        "medium": 0.7, # Medium temp = typical behavior
        "low": 1.5,    # High temp = noisy, often incorrect
    }

    for level, temp in temperature_by_level.items():
        for attempt in range(n_per_level):
            try:
                code = generate_solution(model, tokenizer, device, problem, temperature=temp)
                solutions.append({
                    "task_id": problem["task_id"],
                    "quality_level": level,
                    "attempt": attempt,
                    "code": code,
                    "temperature": temp,
                })
                logger.info(f"  Generated {level} solution {attempt+1}/{n_per_level} (temp={temp}): {code[:60].strip()!r}...")
            except Exception as e:
                logger.error(f"  Error generating {level} solution: {e}")
                solutions.append({
                    "task_id": problem["task_id"],
                    "quality_level": level,
                    "attempt": attempt,
                    "code": f"def {problem.get('entry_point', 'solution')}():\n    pass",
                    "temperature": temp,
                    "generation_error": str(e),
                })

    return solutions


def evaluate_solutions_with_reward_models(solutions, problems_by_id, reward_model_names):
    """Evaluate all solutions with all reward models."""
    reward_models = {name: get_reward_model(name) for name in reward_model_names}
    results = []

    for sol in solutions:
        task_id = sol["task_id"]
        problem = problems_by_id[task_id]
        tests = problem["tests"]
        code = sol["code"]

        sol_result = {
            "task_id": task_id,
            "quality_level": sol["quality_level"],
            "attempt": sol["attempt"],
            "code": code,
            "rewards": {}
        }

        for rm_name, rm in reward_models.items():
            eval_result = rm.compute(code, tests)
            sol_result["rewards"][rm_name] = eval_result

        # Log summary
        hr = sol_result["rewards"]["hierarchical"]
        br = sol_result["rewards"]["binary"]
        logger.info(
            f"  {task_id} {sol['quality_level']} attempt {sol['attempt']}: "
            f"binary={br['reward']:.3f}, hier={hr['reward']:.3f} "
            f"(passed {hr['passed_tests']}/{hr['total_tests']})"
        )

        results.append(sol_result)

    return results


def compute_discriminability_metrics(results, reward_model_names):
    """
    Compute how well each reward model discriminates between quality levels.
    """
    from scipy import stats

    metrics = {}

    for rm_name in reward_model_names:
        rewards_by_level = {"high": [], "medium": [], "low": []}

        for sol in results:
            level = sol["quality_level"]
            reward = sol["rewards"][rm_name]["reward"]
            rewards_by_level[level].append(reward)

        # Mean rewards by level
        mean_by_level = {level: np.mean(rewards) if rewards else 0.0
                         for level, rewards in rewards_by_level.items()}

        # Effect size between high and low quality
        high = np.array(rewards_by_level["high"])
        low = np.array(rewards_by_level["low"])

        if len(high) > 0 and len(low) > 0:
            pooled_std = np.sqrt((np.std(high)**2 + np.std(low)**2) / 2)
            cohen_d = (np.mean(high) - np.mean(low)) / (pooled_std + 1e-8)
        else:
            cohen_d = 0.0

        # Kendall-tau: assign ranks (high=2, medium=1, low=0)
        level_to_rank = {"high": 2, "medium": 1, "low": 0}
        true_ranks = []
        pred_rewards = []
        for sol in results:
            true_ranks.append(level_to_rank[sol["quality_level"]])
            pred_rewards.append(sol["rewards"][rm_name]["reward"])

        if len(set(true_ranks)) > 1 and len(set(pred_rewards)) > 1:
            tau, p_val = stats.kendalltau(true_ranks, pred_rewards)
        else:
            tau, p_val = 0.0, 1.0

        # Within-level variance
        within_var = np.mean([
            np.var(rewards_by_level[level]) if rewards_by_level[level] else 0
            for level in ["high", "medium", "low"]
        ])

        # Partial solution reward analysis
        zero_pass_rewards = [
            sol["rewards"][rm_name]["reward"]
            for sol in results
            if sol["rewards"][rm_name]["passed_tests"] == 0
        ]
        mean_partial_reward = np.mean(zero_pass_rewards) if zero_pass_rewards else 0.0

        full_pass_rewards = [
            sol["rewards"][rm_name]["reward"]
            for sol in results
            if sol["rewards"][rm_name]["passed_tests"] == sol["rewards"][rm_name]["total_tests"]
            and sol["rewards"][rm_name]["total_tests"] > 0
        ]
        mean_full_reward = np.mean(full_pass_rewards) if full_pass_rewards else 0.0

        reward_separation = mean_full_reward - mean_partial_reward
        is_monotonic = bool(mean_by_level["high"] >= mean_by_level["medium"] >= mean_by_level["low"])

        metrics[rm_name] = {
            "mean_high": mean_by_level["high"],
            "mean_medium": mean_by_level["medium"],
            "mean_low": mean_by_level["low"],
            "cohen_d": cohen_d,
            "kendall_tau": tau,
            "kendall_p": p_val,
            "within_level_variance": within_var,
            "mean_partial_reward": mean_partial_reward,
            "mean_full_reward": mean_full_reward,
            "reward_separation": reward_separation,
            "is_monotonic": is_monotonic,
            "n_partial_solutions": len(zero_pass_rewards),
            "n_full_solutions": len(full_pass_rewards),
        }

    return metrics


def compute_pass_at_k_stats(results, reward_model_names):
    """
    Compute reward-guided selection statistics.
    """
    # Group by task_id
    by_task = {}
    for sol in results:
        tid = sol["task_id"]
        if tid not in by_task:
            by_task[tid] = []
        by_task[tid].append(sol)

    stats = {}
    for rm_name in reward_model_names:
        n_tasks = len(by_task)
        reward_guided_correct = 0
        random_correct_sum = 0.0
        n_trials = 0

        for tid, sols in by_task.items():
            # Ground truth: solutions that pass all tests
            n_correct = sum(
                1 for s in sols
                if s["rewards"][rm_name]["total_tests"] > 0 and
                s["rewards"][rm_name]["passed_tests"] == s["rewards"][rm_name]["total_tests"]
            )

            # Reward-guided: pick solution with highest reward
            if sols:
                best_sol = max(sols, key=lambda s: s["rewards"][rm_name]["reward"])
                if (best_sol["rewards"][rm_name]["total_tests"] > 0 and
                    best_sol["rewards"][rm_name]["passed_tests"] == best_sol["rewards"][rm_name]["total_tests"]):
                    reward_guided_correct += 1

            n_total = len(sols)
            if n_total > 0:
                random_correct_sum += n_correct / n_total
                n_trials += 1

        reward_guided_rate = reward_guided_correct / n_tasks if n_tasks > 0 else 0
        random_rate = random_correct_sum / n_trials if n_trials > 0 else 0

        stats[rm_name] = {
            "reward_guided_correct_rate": reward_guided_rate,
            "random_selection_rate": random_rate,
            "improvement_over_random": reward_guided_rate - random_rate,
        }

    return stats


def run_ablation_study(results, problems_by_id):
    """Ablation: show contribution of each reward component."""
    component_contributions = {"syntax": [], "runtime": [], "coverage": [], "semantic": []}

    for sol in results:
        full_result = sol["rewards"]["hierarchical"]
        components = full_result.get("components", {})
        for comp in ["syntax", "runtime", "coverage", "semantic"]:
            if comp in components:
                component_contributions[comp].append(components[comp])

    ablation_stats = {}
    for comp, values in component_contributions.items():
        if values:
            ablation_stats[comp] = {
                "mean": np.mean(values),
                "std": np.std(values),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
            }

    return ablation_stats


def main():
    logger.info("=" * 60)
    logger.info("HierAlign Experiment: Hierarchical Execution Feedback")
    logger.info("=" * 60)

    problems = get_problems()
    problems_by_id = {p["task_id"]: p for p in problems}
    reward_model_names = ["binary", "syntax_only", "coverage", "hierarchical"]

    # Step 1: Load model
    logger.info("\nStep 1: Loading code generation model...")
    model, tokenizer, device = load_model()

    # Step 2: Generate solutions
    logger.info(f"\nStep 2: Generating solutions for {len(problems)} problems...")
    all_solutions = []

    for i, problem in enumerate(problems):
        logger.info(f"\nProblem {i+1}/{len(problems)}: {problem['task_id']}")
        solutions = generate_solutions_at_quality_levels(
            model, tokenizer, device, problem, n_per_level=2
        )
        all_solutions.extend(solutions)
        logger.info(f"  Generated {len(solutions)} solutions")

    logger.info(f"\nTotal solutions generated: {len(all_solutions)}")

    # Step 3: Evaluate with reward models
    logger.info("\nStep 3: Evaluating solutions with reward models...")
    eval_results = evaluate_solutions_with_reward_models(
        all_solutions, problems_by_id, reward_model_names
    )

    # Step 4: Compute discriminability metrics
    logger.info("\nStep 4: Computing discriminability metrics...")
    disc_metrics = compute_discriminability_metrics(eval_results, reward_model_names)

    for rm_name, metrics in disc_metrics.items():
        logger.info(f"\n{rm_name}:")
        logger.info(f"  Mean rewards: high={metrics['mean_high']:.3f}, "
                    f"med={metrics['mean_medium']:.3f}, low={metrics['mean_low']:.3f}")
        logger.info(f"  Cohen's d: {metrics['cohen_d']:.3f}")
        logger.info(f"  Kendall-tau: {metrics['kendall_tau']:.3f} (p={metrics['kendall_p']:.4f})")
        logger.info(f"  Partial solution reward: {metrics['mean_partial_reward']:.3f}")
        logger.info(f"  Reward separation: {metrics['reward_separation']:.3f}")
        logger.info(f"  Monotonic: {metrics['is_monotonic']}")

    # Step 5: Pass@k analysis
    logger.info("\nStep 5: Computing reward-guided selection stats...")
    pass_stats = compute_pass_at_k_stats(eval_results, reward_model_names)

    for rm_name, stats in pass_stats.items():
        logger.info(f"\n{rm_name}:")
        logger.info(f"  Reward-guided correct rate: {stats['reward_guided_correct_rate']:.3f}")
        logger.info(f"  Random selection rate: {stats['random_selection_rate']:.3f}")
        logger.info(f"  Improvement over random: {stats['improvement_over_random']:.3f}")

    # Step 6: Ablation study
    logger.info("\nStep 6: Running ablation study...")
    ablation = run_ablation_study(eval_results, problems_by_id)
    for comp, stats in ablation.items():
        logger.info(f"  {comp}: mean={stats['mean']:.3f}, std={stats['std']:.3f}")

    # Save results
    output = {
        "solutions": eval_results,
        "discriminability_metrics": disc_metrics,
        "pass_at_k_stats": pass_stats,
        "ablation_study": ablation,
        "config": {
            "model": MODEL_NAME,
            "n_problems": len(problems),
            "n_solutions": len(all_solutions),
            "reward_models": reward_model_names,
        }
    }

    output_path = RESULTS_DIR / "experiment_results.json"

    def convert_for_json(obj):
        if isinstance(obj, bool):
            return bool(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=convert_for_json)
    logger.info(f"\nResults saved to {output_path}")

    return output


if __name__ == "__main__":
    main()
