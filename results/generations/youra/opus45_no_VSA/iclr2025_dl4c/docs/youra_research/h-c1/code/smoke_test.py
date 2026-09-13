#!/usr/bin/env python3
"""Smoke test for H-C1: validates full code path without heavy training."""
import json
import random
import torch
import numpy as np
from pathlib import Path

from config import Config
from data import load_humaneval_plus, get_training_data
from model import load_base_model, wrap_lora, RLCodeTrainer
from diversity_controller import FeedbackDiversityController
from error_taxonomy import classify_error, ErrorClass
from refine import single_shot, self_refine, execute_and_get_feedback
from evaluate import compute_pass_at_1, compute_interaction, gate_check, save_results
from visualize import create_all_figures


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def run_smoke_test():
    """Run minimal smoke test to verify code correctness."""
    cfg = Config()
    cfg.seed = 42
    set_seed(cfg.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Load data
    print("\n=== Loading Data ===")
    problems = load_humaneval_plus(cfg)
    data = get_training_data(problems)
    print(f"Loaded {len(data)} problems")

    # Subset for smoke test
    problems_subset = dict(list(problems.items())[:10])
    data_subset = data[:10]
    print(f"Using {len(data_subset)} problems for smoke test")

    # Load model
    print("\n=== Loading Model ===")
    base_model, tokenizer = load_base_model(cfg)
    model = wrap_lora(base_model, cfg)
    model = model.to(device)
    print("Model loaded successfully")

    # Test diversity controller
    print("\n=== Testing Diversity Controller ===")
    ctrl_high = FeedbackDiversityController(mode="high")
    ctrl_low = FeedbackDiversityController(mode="low")

    # Create synthetic samples with error types
    samples = [
        {"error_type": ErrorClass.COMPILE_ERROR, "prompt": "p1", "tests": [], "code": "c1"},
        {"error_type": ErrorClass.RUNTIME_ERROR, "prompt": "p2", "tests": [], "code": "c2"},
        {"error_type": ErrorClass.FAILED_TEST, "prompt": "p3", "tests": [], "code": "c3"},
        {"error_type": ErrorClass.PASSED_TEST, "prompt": "p4", "tests": [], "code": "c4"},
        {"error_type": ErrorClass.FAILED_TEST, "prompt": "p5", "tests": [], "code": "c5"},
        {"error_type": ErrorClass.FAILED_TEST, "prompt": "p6", "tests": [], "code": "c6"},
        {"error_type": ErrorClass.FAILED_TEST, "prompt": "p7", "tests": [], "code": "c7"},
        {"error_type": ErrorClass.RUNTIME_ERROR, "prompt": "p8", "tests": [], "code": "c8"},
    ]

    filtered_high = ctrl_high.filter_batch(samples, batch_size=8)
    H_high = ctrl_high.compute_entropy(filtered_high)
    print(f"High diversity batch: H={H_high:.3f} bits")

    filtered_low = ctrl_low.filter_batch(samples, batch_size=8)
    H_low = ctrl_low.compute_entropy(filtered_low)
    print(f"Low diversity batch: H={H_low:.3f} bits")

    # Test generation on one sample
    print("\n=== Testing Generation ===")
    test_problem = list(problems_subset.values())[0]
    prompt = test_problem["prompt"]

    code_single = single_shot(model, tokenizer, prompt, cfg)
    print(f"Single-shot generation: {len(code_single)} chars")

    entry_point = test_problem.get("entry_point", "solution")
    base_input = test_problem.get("base_input", [])
    tests = [f"assert {entry_point}(*{t[0]}) == {t[1]}" for t in base_input if len(t) >= 2][:2]

    if tests:
        code_refine = self_refine(model, tokenizer, prompt, tests, cfg)
        print(f"Refined generation: {len(code_refine)} chars")

        pass_rate, err_msg = execute_and_get_feedback(code_single, tests)
        error_type = classify_error(err_msg, pass_rate)
        print(f"Execution feedback: pass_rate={pass_rate:.2f}, error_type={error_type.value}")

    # Test evaluation (on subset)
    print("\n=== Testing Evaluation ===")
    samples_dict = {}
    for task_id in list(problems_subset.keys())[:3]:
        problem = problems_subset[task_id]
        code = single_shot(model, tokenizer, problem["prompt"], cfg)
        samples_dict[task_id] = code

    pass_at_1 = compute_pass_at_1(samples_dict, problems_subset)
    print(f"pass@1 on 3 samples: {pass_at_1:.4f}")

    # Build mock results
    results = {
        "conditions": {
            "RL-High-Single": {"pass_at_1": 0.05, "entropy": 2.3, "interaction": 0.0},
            "RL-High-Refine": {"pass_at_1": 0.10, "entropy": 2.3, "interaction": 0.05},
            "RL-Low-Single": {"pass_at_1": 0.04, "entropy": 1.2, "interaction": 0.0},
            "RL-Low-Refine": {"pass_at_1": 0.06, "entropy": 1.2, "interaction": 0.02},
        },
        "entropy_high": 2.3,
        "entropy_low": 1.2,
        "interaction_high": 0.05,
        "interaction_low": 0.02,
        "gate_check": True,
        "diversity_mechanism_verified": True,
    }

    # Test gate check
    gate_passed = gate_check(results["interaction_high"], results["interaction_low"])
    print(f"Gate check (High > Low): {gate_passed}")

    # Save results
    print("\n=== Saving Results ===")
    save_results(results, cfg)
    print(f"Saved to {cfg.outputs_dir / 'results.json'}")

    # Create figures
    print("\n=== Creating Figures ===")
    figures = create_all_figures(results, cfg)
    print(f"Created figures: {[str(f) for f in figures]}")

    print("\n" + "="*60)
    print("SMOKE TEST PASSED")
    print("="*60)
    print("All code paths validated. Ready for full experiment.")

    return results


if __name__ == "__main__":
    run_smoke_test()
