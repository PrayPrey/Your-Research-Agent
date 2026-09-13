#!/usr/bin/env python3
# run.py - h-m3 RCI Flip Pattern Detection (MECHANISM) orchestrator
import os
import sys
import json
import csv
from tqdm import tqdm

# Add code dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG, set_seed
from data import load_truthfulqa_mc1, build_prompts
from model import load_model, get_hidden_states, label_hallucination
from rci import RCIFlipDetector
from evaluate import compute_rates, check_gate
from visualize import (
    plot_gate_metrics,
    plot_flip_position_heatmap,
    plot_flip_distribution,
    plot_layer_flip_rates,
)


def verify_mechanism(model, tokenizer, detector, sample_prompt):
    """Verify RCI flip detection mechanism works correctly."""
    hidden_states = get_hidden_states(model, tokenizer, sample_prompt)

    # Check 1: Hidden states available for all layers
    assert len(hidden_states) >= 33, f"Expected 33+ layers, got {len(hidden_states)}"

    # Check 2: Layer logits extraction works
    layer_logits = detector.extract_layer_predictions(hidden_states)
    expected_layers = CONFIG["layer_range"][1] - CONFIG["layer_range"][0] + 1
    assert layer_logits.shape[0] == expected_layers, f"Expected {expected_layers} layers, got {layer_logits.shape[0]}"

    # Check 3: Flip detection returns valid output
    num_flips, flip_positions = detector.detect_flip_pattern(layer_logits)
    assert num_flips[0] >= 0, "Flip count must be non-negative"

    print("✓ Mechanism verification passed")
    return True


def main():
    print("=" * 60)
    print("RCI Flip Pattern Detection - h-m3 (MECHANISM)")
    print("=" * 60)

    # Setup
    set_seed()
    os.makedirs(CONFIG["figures_dir"], exist_ok=True)
    os.makedirs(CONFIG["outputs_dir"], exist_ok=True)

    # Step 1: Load data
    print("\n[1/6] Loading TruthfulQA MC1 dataset...")
    samples = load_truthfulqa_mc1()
    prompts = build_prompts(samples)
    print(f"  Loaded {len(prompts)} questions")

    # Step 2: Load model
    print("\n[2/6] Loading LLaMA-2-7B...")
    model, tokenizer = load_model()
    print(f"  Model loaded with output_hidden_states=True")

    # Initialize RCI detector
    detector = RCIFlipDetector(model.lm_head.weight)
    print(f"  RCI detector initialized (layers {CONFIG['layer_range']})")

    # Step 3: Verify mechanism
    print("\n[3/6] Verifying mechanism...")
    verify_mechanism(model, tokenizer, detector, prompts[0]["prompt"])

    # Step 4: Process all samples
    print("\n[4/6] Processing samples...")
    results = []

    for item in tqdm(prompts, desc="RCI Analysis"):
        # Label hallucination via greedy decode
        is_halluc, model_answer = label_hallucination(
            model, tokenizer, item["prompt"], item["correct_answer"]
        )

        # Get hidden states and compute RCI
        hidden_states = get_hidden_states(model, tokenizer, item["prompt"])
        rci_result = detector.compute_sample(hidden_states)

        results.append({
            "question": item["question"],
            "correct_answer": item["correct_answer"],
            "model_answer": model_answer,
            "is_hallucination": is_halluc,
            **rci_result,
        })

    # Step 5: Evaluate
    print("\n[5/6] Computing rates and checking gate...")
    rates = compute_rates(results)
    gate_result = check_gate(rates)

    print(f"\n  Results:")
    print(f"    Hallucination flip rate: {rates['hallucination_flip_rate']:.1%} ({rates['halluc_flip_count']}/{rates['n_hallucinations']})")
    print(f"    Correct flip rate:       {rates['correct_flip_rate']:.1%} ({rates['correct_flip_count']}/{rates['n_correct']})")
    print(f"    Separation:              {rates['separation']:.1%}")
    print(f"\n  Gate Status:")
    print(f"    Full pass:  {'PASS' if gate_result['pass'] else 'FAIL'}")
    print(f"    PoC pass:   {'PASS' if gate_result['poc_pass'] else 'FAIL'}")
    print(f"    Falsified:  {'YES' if gate_result['falsified'] else 'NO'}")

    # Step 6: Visualize
    print("\n[6/6] Generating figures...")
    fig_paths = []
    fig_paths.append(plot_gate_metrics(rates))
    fig_paths.append(plot_flip_position_heatmap(results))
    fig_paths.append(plot_flip_distribution(results))
    fig_paths.append(plot_layer_flip_rates(results))
    for p in fig_paths:
        print(f"  Saved: {p}")

    # Save results
    results_path = os.path.join(CONFIG["outputs_dir"], "results.json")
    output = {
        "hypothesis_id": "h-m3",
        "hypothesis_type": "MECHANISM",
        "gate_type": "SHOULD_WORK",
        "gate_result": {
            "full_pass": gate_result["pass"],
            "poc_pass": gate_result["poc_pass"],
            "falsified": gate_result["falsified"],
        },
        "metrics": {
            "hallucination_flip_rate": rates["hallucination_flip_rate"],
            "correct_flip_rate": rates["correct_flip_rate"],
            "separation": rates["separation"],
            "n_hallucinations": rates["n_hallucinations"],
            "n_correct": rates["n_correct"],
        },
        "thresholds": {
            "halluc_rate_threshold": CONFIG["halluc_rate_threshold"],
            "correct_rate_threshold": CONFIG["correct_rate_threshold"],
            "separation_threshold": CONFIG["separation_threshold"],
        },
        "dataset": {
            "name": "TruthfulQA MC1",
            "n_samples": len(prompts),
        },
        "model": CONFIG["model_id"],
        "figures": fig_paths,
    }

    with open(results_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved: {results_path}")

    # Save CSV
    csv_path = os.path.join(CONFIG["outputs_dir"], "results.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "is_hallucination", "has_flip", "num_flips"])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "question": r["question"][:100],
                "is_hallucination": r["is_hallucination"],
                "has_flip": r["has_flip"],
                "num_flips": r["num_flips"],
            })
    print(f"  CSV saved: {csv_path}")

    print("\n" + "=" * 60)
    poc_status = "PASSED" if gate_result["poc_pass"] else "FAILED"
    full_status = "PASSED" if gate_result["pass"] else "FAILED"
    print(f"EXPERIMENT COMPLETE: PoC {poc_status}, Full Gate {full_status}")
    print("=" * 60)

    # Return PoC pass for SHOULD_WORK gate
    return gate_result["poc_pass"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
