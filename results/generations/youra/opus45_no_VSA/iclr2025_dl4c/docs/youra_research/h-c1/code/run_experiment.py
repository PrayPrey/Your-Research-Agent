#!/usr/bin/env python3
"""Run H-C1 experiment: Feedback Diversity CONDITION Test.

Tests whether high feedback diversity H(Schema|ErrorClass) > 2.5 bits
is necessary for the Training×Refinement superadditive interaction.

2×2 design: (High/Low diversity) × (Refine/Single)
"""
import argparse
import json
import random
import torch
import numpy as np
from pathlib import Path
from collections import Counter

from config import Config
from data import load_humaneval_plus, get_training_data
from model import load_base_model, wrap_lora
from train import train_ce, train_rl_with_diversity
from diversity_controller import FeedbackDiversityController
from evaluate import run_condition_eval, compute_interaction, gate_check, save_results
from visualize import create_all_figures


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def verify_diversity_mechanism(entropy_high: float, entropy_low: float) -> bool:
    """Verify that diversity manipulation achieved separation."""
    H_high_ok = entropy_high > 2.0
    H_low_ok = entropy_low < 2.0
    print(f"✓ Diversity manipulation: H_high={entropy_high:.2f} (>2.0: {H_high_ok}), H_low={entropy_low:.2f} (<2.0: {H_low_ok})")
    return H_high_ok and H_low_ok


def run_all_conditions(cfg: Config) -> dict:
    """Run all 4 conditions: (High/Low) × (Refine/Single)."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load data
    print("\n=== Loading Data ===")
    problems = load_humaneval_plus(cfg)
    data = get_training_data(problems)
    print(f"Loaded {len(data)} problems")

    results = {
        "conditions": {},
        "entropy_high": 0.0,
        "entropy_low": 0.0,
        "interaction_high": 0.0,
        "interaction_low": 0.0,
        "gate_check": False,
    }

    # Train HIGH diversity model
    print("\n" + "="*60)
    print("Training HIGH diversity model (target H > 2.5)")
    print("="*60)
    base_model, tokenizer = load_base_model(cfg)
    high_model = wrap_lora(base_model, cfg)
    high_model = high_model.to(device)

    # CE warmup
    high_model = train_ce(high_model, tokenizer, data, cfg)

    # RL with high diversity
    controller_high = FeedbackDiversityController(mode="high", target_high=cfg.diversity_high_threshold)
    high_model, entropy_high = train_rl_with_diversity(high_model, tokenizer, data, cfg, controller_high)
    high_model.save_pretrained(cfg.checkpoint_dir / "rl_high")
    results["entropy_high"] = entropy_high

    # Train LOW diversity model
    print("\n" + "="*60)
    print("Training LOW diversity model (target H < 1.5)")
    print("="*60)
    base_model2, _ = load_base_model(cfg)
    low_model = wrap_lora(base_model2, cfg)
    low_model = low_model.to(device)

    # CE warmup
    low_model = train_ce(low_model, tokenizer, data, cfg)

    # RL with low diversity
    controller_low = FeedbackDiversityController(mode="low", target_low=cfg.diversity_low_threshold)
    low_model, entropy_low = train_rl_with_diversity(low_model, tokenizer, data, cfg, controller_low)
    low_model.save_pretrained(cfg.checkpoint_dir / "rl_low")
    results["entropy_low"] = entropy_low

    # Verify diversity mechanism
    diversity_ok = verify_diversity_mechanism(entropy_high, entropy_low)

    # Evaluate all 4 conditions
    print("\n" + "="*60)
    print("Evaluating all conditions")
    print("="*60)

    # RL-High-Single
    print("\nEvaluating RL-High-Single...")
    pass1_high_single = run_condition_eval(high_model, tokenizer, problems, "single", cfg)
    results["conditions"]["RL-High-Single"] = {
        "pass_at_1": pass1_high_single,
        "entropy": entropy_high,
        "interaction": 0.0,
    }
    print(f"RL-High-Single: pass@1 = {pass1_high_single:.4f}")

    # RL-High-Refine
    print("\nEvaluating RL-High-Refine...")
    pass1_high_refine = run_condition_eval(high_model, tokenizer, problems, "refine", cfg)
    interaction_high = compute_interaction(pass1_high_refine, pass1_high_single)
    results["conditions"]["RL-High-Refine"] = {
        "pass_at_1": pass1_high_refine,
        "entropy": entropy_high,
        "interaction": interaction_high,
    }
    results["interaction_high"] = interaction_high
    print(f"RL-High-Refine: pass@1 = {pass1_high_refine:.4f}, interaction = {interaction_high:.4f}")

    # RL-Low-Single
    print("\nEvaluating RL-Low-Single...")
    pass1_low_single = run_condition_eval(low_model, tokenizer, problems, "single", cfg)
    results["conditions"]["RL-Low-Single"] = {
        "pass_at_1": pass1_low_single,
        "entropy": entropy_low,
        "interaction": 0.0,
    }
    print(f"RL-Low-Single: pass@1 = {pass1_low_single:.4f}")

    # RL-Low-Refine
    print("\nEvaluating RL-Low-Refine...")
    pass1_low_refine = run_condition_eval(low_model, tokenizer, problems, "refine", cfg)
    interaction_low = compute_interaction(pass1_low_refine, pass1_low_single)
    results["conditions"]["RL-Low-Refine"] = {
        "pass_at_1": pass1_low_refine,
        "entropy": entropy_low,
        "interaction": interaction_low,
    }
    results["interaction_low"] = interaction_low
    print(f"RL-Low-Refine: pass@1 = {pass1_low_refine:.4f}, interaction = {interaction_low:.4f}")

    # Gate check
    gate_passed = gate_check(interaction_high, interaction_low)
    results["gate_check"] = gate_passed
    results["diversity_mechanism_verified"] = diversity_ok

    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"Entropy High: {entropy_high:.3f} bits")
    print(f"Entropy Low: {entropy_low:.3f} bits")
    print(f"Interaction High: {interaction_high:.4f}")
    print(f"Interaction Low: {interaction_low:.4f}")
    print(f"Gate Check (High > Low): {gate_passed}")
    print(f"Diversity Mechanism Verified: {diversity_ok}")

    return results


def main():
    parser = argparse.ArgumentParser(description="H-C1: Feedback Diversity Necessity Test")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ce-epochs", type=int, default=10)
    parser.add_argument("--rl-epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=5e-5)
    args = parser.parse_args()

    cfg = Config()
    cfg.seed = args.seed
    cfg.ce_epochs = args.ce_epochs
    cfg.rl_epochs = args.rl_epochs
    cfg.batch_size = args.batch_size
    cfg.lr = args.lr

    set_seed(cfg.seed)

    print("="*60)
    print("H-C1: Feedback Diversity CONDITION Test")
    print("="*60)
    print(f"Hypothesis: High feedback diversity H > 2.5 bits necessary for superadditivity")
    print(f"Gate: SHOULD_WORK")
    print(f"Config: ce_epochs={cfg.ce_epochs}, rl_epochs={cfg.rl_epochs}, seed={cfg.seed}")
    print("="*60)

    results = run_all_conditions(cfg)

    # Save results
    save_results(results, cfg)
    print(f"\nResults saved to {cfg.outputs_dir / 'results.json'}")

    # Create figures
    figures = create_all_figures(results, cfg)
    print(f"Figures saved: {[str(f) for f in figures]}")

    # Final verdict
    print("\n" + "="*60)
    print("GATE VERDICT")
    print("="*60)
    if results["gate_check"]:
        print("PASS: High-diversity interaction > Low-diversity interaction")
        print("Feedback diversity appears necessary for superadditivity")
    else:
        print("FAIL: High-diversity interaction <= Low-diversity interaction")
        print("Feedback diversity may NOT be necessary (negative result)")
    print("="*60)

    return results


if __name__ == "__main__":
    main()
