"""
Main experiment runner for ExecGuide vs baselines.
Tests the hypothesis that ExecGuide improves code generation correctness.
"""

import os
import sys
import json
import time
import logging
import numpy as np
import torch
import random
from pathlib import Path

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from evaluation import load_humaneval, evaluate_method, extract_function_body, run_humaneval_test
from spec_augment import HUMANEVAL_SPECS, check_smt_consistency, run_test_cases
from reward_model import VerifiabilityRewardModel, SimpleCodeTokenizer, train_reward_model
from baselines import generate_code_greedy, generate_multiple_samples, post_hoc_repair
from execguide import ExecGuide, generate_training_data_for_reward_model


# Setup logging
os.makedirs(CODE_DIR, exist_ok=True)
log_path = os.path.join(CODE_DIR, "log.txt")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_model_and_tokenizer(model_name: str, device: torch.device):
    """Load model and tokenizer."""
    from transformers import AutoTokenizer, AutoModelForCausalLM

    logger.info(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype = torch.float16 if device.type == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=dtype,
        trust_remote_code=True,
    ).to(device)
    model.eval()
    logger.info(f"Model loaded on {device}")
    return model, tokenizer


def prepare_prompt(problem: dict) -> str:
    """Prepare code generation prompt - use raw prompt to keep code parseable."""
    return problem["prompt"]


def run_baseline_greedy(model, tokenizer, device, problems):
    """Baseline: Standard greedy decoding."""
    logger.info("=" * 60)
    logger.info("Running Baseline: Standard Greedy Decoding")
    logger.info("=" * 60)

    def generate_fn(prompt, problem_id, entry_point):
        full_prompt = prepare_prompt({"prompt": prompt})
        code = generate_code_greedy(
            full_prompt, model, tokenizer,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            device=device,
        )
        return [full_prompt + code]

    results = evaluate_method("Standard Greedy", problems, generate_fn)
    logger.info(f"Standard Greedy: pass@1={results['pass_at_1']:.4f}, avg_time={results['avg_time']:.2f}s")
    return results


def run_baseline_sampling(model, tokenizer, device, problems, n_samples=4):
    """Baseline: Multiple sampling (pass@k)."""
    logger.info("=" * 60)
    logger.info("Running Baseline: Multiple Sampling")
    logger.info("=" * 60)

    def generate_fn(prompt, problem_id, entry_point):
        full_prompt = prepare_prompt({"prompt": prompt})
        samples = generate_multiple_samples(
            full_prompt, model, tokenizer,
            num_samples=n_samples,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=0.8,
            device=device,
        )
        return [full_prompt + s for s in samples]

    results = evaluate_method("Multiple Sampling", problems, generate_fn, num_samples=n_samples)
    logger.info(f"Multiple Sampling: pass@1={results['pass_at_1']:.4f}, avg_time={results['avg_time']:.2f}s")
    return results


def run_baseline_post_hoc(model, tokenizer, device, problems, max_repair=2):
    """Baseline: Post-hoc repair."""
    logger.info("=" * 60)
    logger.info("Running Baseline: Post-hoc Repair")
    logger.info("=" * 60)

    def generate_fn(prompt, problem_id, entry_point):
        full_prompt = prepare_prompt({"prompt": prompt})
        code, rounds, _ = post_hoc_repair(
            full_prompt, model, tokenizer,
            problem_id, entry_point,
            test_cases=HUMANEVAL_SPECS.get(problem_id, {}).get("test_cases", []),
            max_repair_rounds=max_repair,
            max_new_tokens=MAX_NEW_TOKENS,
            device=device,
        )
        return [code]

    results = evaluate_method("Post-hoc Repair", problems, generate_fn)
    logger.info(f"Post-hoc Repair: pass@1={results['pass_at_1']:.4f}, avg_time={results['avg_time']:.2f}s")
    return results


def run_baseline_exec_only(model, tokenizer, device, problems, n_candidates=4):
    """Baseline: Execution-only steering (no SMT)."""
    logger.info("=" * 60)
    logger.info("Running Baseline: Execution-Only Steering")
    logger.info("=" * 60)

    from baselines import execution_only_steering

    def generate_fn(prompt, problem_id, entry_point):
        full_prompt = prepare_prompt({"prompt": prompt})
        code, _ = execution_only_steering(
            full_prompt, model, tokenizer,
            problem_id, entry_point,
            num_candidates=n_candidates,
            max_new_tokens=MAX_NEW_TOKENS,
            device=device,
        )
        return [code]

    results = evaluate_method("Exec-Only Steering", problems, generate_fn)
    logger.info(f"Exec-Only Steering: pass@1={results['pass_at_1']:.4f}, avg_time={results['avg_time']:.2f}s")
    return results


def run_smt_only(model, tokenizer, device, problems, n_candidates=4):
    """Baseline: SMT-only steering (no execution)."""
    logger.info("=" * 60)
    logger.info("Running Baseline: SMT-Only Steering")
    logger.info("=" * 60)

    from baselines import smt_only_steering

    def generate_fn(prompt, problem_id, entry_point):
        full_prompt = prepare_prompt({"prompt": prompt})
        code, _ = smt_only_steering(
            full_prompt, model, tokenizer,
            problem_id,
            num_candidates=n_candidates,
            max_new_tokens=MAX_NEW_TOKENS,
            device=device,
        )
        return [code]

    results = evaluate_method("SMT-Only Steering", problems, generate_fn)
    logger.info(f"SMT-Only Steering: pass@1={results['pass_at_1']:.4f}, avg_time={results['avg_time']:.2f}s")
    return results


def train_and_get_reward_model(model, tokenizer, device, all_problems):
    """Train reward model on problem subset."""
    logger.info("=" * 60)
    logger.info("Training Reward Model")
    logger.info("=" * 60)

    code_tokenizer = SimpleCodeTokenizer(vocab_size=1000)
    reward_model = VerifiabilityRewardModel(
        vocab_size=1000,
        embed_dim=128,
        hidden_dim=256,
        num_layers=2,
    ).to(device)

    # Generate training data
    logger.info("Generating reward model training data...")
    train_probs = [p for p in all_problems if p["task_id"] in HUMANEVAL_SPECS][:8]
    training_data = generate_training_data_for_reward_model(
        model, tokenizer, train_probs, device, max_new_tokens=128
    )
    logger.info(f"Generated {len(training_data)} training samples")

    if len(training_data) < 5:
        logger.warning("Insufficient training data, using default reward model")
        return reward_model, code_tokenizer, []

    # Train
    losses = train_reward_model(
        reward_model, code_tokenizer, training_data,
        device, epochs=15, lr=1e-3,
    )
    logger.info(f"Reward model trained. Final loss: {losses[-1]:.4f}")
    return reward_model, code_tokenizer, losses


def run_execguide(
    model, tokenizer, device, problems,
    reward_model, code_tokenizer,
    lambda_val=0.5, num_beams=4, smt_check_interval=30,
):
    """Run ExecGuide framework."""
    logger.info("=" * 60)
    logger.info(f"Running ExecGuide (lambda={lambda_val}, beams={num_beams})")
    logger.info("=" * 60)

    guide = ExecGuide(
        model=model,
        tokenizer=tokenizer,
        reward_model=reward_model,
        code_tokenizer=code_tokenizer,
        device=device,
        lambda_steering=lambda_val,
        num_beams=num_beams,
        smt_weight=REWARD_SMT_WEIGHT,
        exec_weight=REWARD_EXEC_WEIGHT,
        smt_check_interval=smt_check_interval,
        max_new_tokens=MAX_NEW_TOKENS,
    )

    def generate_fn(prompt, problem_id, entry_point):
        full_prompt = prepare_prompt({"prompt": prompt})
        code, meta = guide.generate(full_prompt, problem_id, entry_point)
        return [code]

    results = evaluate_method("ExecGuide", problems, generate_fn)
    logger.info(f"ExecGuide: pass@1={results['pass_at_1']:.4f}, avg_time={results['avg_time']:.2f}s")
    return results


def run_execguide_ablation(
    model, tokenizer, device, problems,
    reward_model, code_tokenizer,
):
    """Run ablation studies with different lambda values."""
    logger.info("=" * 60)
    logger.info("Running ExecGuide Ablation Studies")
    logger.info("=" * 60)

    ablation_results = {}
    for lam in [0.0, 0.25, 0.5, 1.0, 2.0]:
        logger.info(f"  Ablation: lambda={lam}")
        guide = ExecGuide(
            model=model,
            tokenizer=tokenizer,
            reward_model=reward_model,
            code_tokenizer=code_tokenizer,
            device=device,
            lambda_steering=lam,
            num_beams=4,
            smt_check_interval=30,
            max_new_tokens=MAX_NEW_TOKENS,
        )

        def make_generate_fn(g):
            def generate_fn(prompt, problem_id, entry_point):
                full_prompt = prepare_prompt({"prompt": prompt})
                code, _ = g.generate(full_prompt, problem_id, entry_point)
                return [code]
            return generate_fn

        res = evaluate_method(
            f"ExecGuide_lam={lam}",
            problems[:10],  # Use subset for ablation
            make_generate_fn(guide),
            verbose=False,
        )
        ablation_results[lam] = res
        logger.info(f"    lambda={lam}: pass@1={res['pass_at_1']:.4f}")

    return ablation_results


def compute_inference_overhead_ratio(
    baseline_time: float,
    execguide_time: float,
) -> float:
    """Compute IOR = ExecGuide time / baseline time."""
    if baseline_time == 0:
        return float('inf')
    return execguide_time / baseline_time


def main():
    set_seed(SEED)

    logger.info("=" * 60)
    logger.info("ExecGuide Experiment: Verification-Guided Code Generation")
    logger.info("=" * 60)
    logger.info(f"Model: {MODEL_NAME}")
    logger.info(f"Problems: {NUM_PROBLEMS}")
    logger.info(f"Device: {DEVICE}")

    # Setup device
    if DEVICE == "cuda" and torch.cuda.is_available():
        device = torch.device("cuda:0")
        logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        logger.info("Using CPU")

    # Load model
    model, tokenizer = load_model_and_tokenizer(MODEL_NAME, device)

    # Load HumanEval problems - filter to those with our specs
    logger.info("Loading HumanEval dataset...")
    all_problems = load_humaneval()
    # Filter to problems with our specs + a few without for diversity
    spec_problems = [p for p in all_problems if p["task_id"] in HUMANEVAL_SPECS]
    other_problems = [p for p in all_problems if p["task_id"] not in HUMANEVAL_SPECS]

    # Use spec_problems first, then fill up with others
    problems = spec_problems[:min(len(spec_problems), 20)]
    remaining = NUM_PROBLEMS - len(problems)
    if remaining > 0:
        problems = problems + other_problems[:remaining]
    problems = problems[:NUM_PROBLEMS]

    logger.info(f"Evaluating on {len(problems)} problems")
    logger.info(f"Problems with SMT specs: {len([p for p in problems if p['task_id'] in HUMANEVAL_SPECS])}")

    # Store all results
    all_results = {}
    timing_results = {}

    # 1. Baseline: Standard Greedy
    t0 = time.time()
    greedy_results = run_baseline_greedy(model, tokenizer, device, problems)
    greedy_time = time.time() - t0
    all_results["standard_greedy"] = greedy_results
    timing_results["standard_greedy"] = greedy_time

    # 2. Baseline: Multiple Sampling
    t0 = time.time()
    sampling_results = run_baseline_sampling(model, tokenizer, device, problems, n_samples=2)
    sampling_time = time.time() - t0
    all_results["multiple_sampling"] = sampling_results
    timing_results["multiple_sampling"] = sampling_time

    # 3. Baseline: Post-hoc Repair
    t0 = time.time()
    posthoc_results = run_baseline_post_hoc(model, tokenizer, device, problems, max_repair=2)
    posthoc_time = time.time() - t0
    all_results["post_hoc_repair"] = posthoc_results
    timing_results["post_hoc_repair"] = posthoc_time

    # 4. Baseline: Execution-Only Steering
    t0 = time.time()
    exec_only_results = run_baseline_exec_only(model, tokenizer, device, problems, n_candidates=2)
    exec_only_time = time.time() - t0
    all_results["exec_only_steering"] = exec_only_results
    timing_results["exec_only_steering"] = exec_only_time

    # 5. Baseline: SMT-Only Steering
    t0 = time.time()
    smt_only_results = run_smt_only(model, tokenizer, device, problems, n_candidates=2)
    smt_only_time = time.time() - t0
    all_results["smt_only_steering"] = smt_only_results
    timing_results["smt_only_steering"] = smt_only_time

    # 6. Train reward model
    reward_model, code_tokenizer, rm_losses = train_and_get_reward_model(
        model, tokenizer, device, all_problems
    )

    # 7. ExecGuide (main method)
    t0 = time.time()
    execguide_results = run_execguide(
        model, tokenizer, device, problems,
        reward_model, code_tokenizer,
        lambda_val=LAMBDA_STEERING,
        num_beams=NUM_BEAMS,
        smt_check_interval=30,
    )
    execguide_time = time.time() - t0
    all_results["execguide"] = execguide_results
    timing_results["execguide"] = execguide_time

    # 8. Ablation studies
    ablation_results = run_execguide_ablation(
        model, tokenizer, device, problems,
        reward_model, code_tokenizer,
    )
    all_results["ablation"] = {str(k): v for k, v in ablation_results.items()}

    # Compute IOR
    baseline_avg_time = greedy_results["avg_time"]
    execguide_avg_time = execguide_results["avg_time"]
    ior = compute_inference_overhead_ratio(baseline_avg_time, execguide_avg_time)
    logger.info(f"\nInference Overhead Ratio (IOR): {ior:.2f}x")

    # Compute SCR (Specification Compliance Rate)
    spec_problems_in_eval = [p for p in problems if p["task_id"] in HUMANEVAL_SPECS]
    if spec_problems_in_eval:
        from spec_augment import check_smt_consistency
        scr_values = {}
        for method_name, method_results in all_results.items():
            if method_name in ["ablation"]:
                continue
            # Approximate SCR using per-problem results
            passed_problems = [
                r for r in method_results.get("per_problem_results", [])
                if r.get("passed", False)
            ]
            scr_values[method_name] = len(passed_problems) / len(spec_problems_in_eval) if spec_problems_in_eval else 0.0
        logger.info("Specification Compliance Rates (SCR):")
        for m, scr in scr_values.items():
            logger.info(f"  {m}: {scr:.4f}")
    else:
        scr_values = {}

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("EXPERIMENT SUMMARY")
    logger.info("=" * 60)
    for method, res in all_results.items():
        if method == "ablation":
            continue
        logger.info(f"{res.get('method', method):30s}: pass@1={res['pass_at_1']:.4f}")

    # Save results
    final_results = {
        "model": MODEL_NAME,
        "num_problems": len(problems),
        "seed": SEED,
        "lambda_steering": LAMBDA_STEERING,
        "num_beams": NUM_BEAMS,
        "reward_model_losses": rm_losses,
        "timing": timing_results,
        "ior": ior,
        "scr": scr_values,
        "results": {
            k: {
                "method": v.get("method", k),
                "pass_at_1": v["pass_at_1"],
                "fpc": v.get("fpc", v["pass_at_1"]),
                "avg_time": v["avg_time"],
                "total_pass": v["total_pass"],
                "total_problems": v["total_problems"],
            }
            for k, v in all_results.items()
            if k != "ablation"
        },
        "ablation": {
            k: {
                "lambda": float(k),
                "pass_at_1": v["pass_at_1"],
                "avg_time": v["avg_time"],
            }
            for k, v in ablation_results.items()
        },
        "ablation_labels": {str(k): str(k) for k in ablation_results.keys()},
    }

    results_path = os.path.join(CODE_DIR, "results.json")
    with open(results_path, "w") as f:
        json.dump(final_results, f, indent=2)
    logger.info(f"\nResults saved to {results_path}")

    return final_results


if __name__ == "__main__":
    results = main()
    print("\nExperiment completed successfully!")
