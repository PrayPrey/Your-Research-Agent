#!/usr/bin/env python3
# H-M1: Token Entropy Captures Epistemic Uncertainty
# Main experiment runner
import json
import os
from tqdm import tqdm

import config
from data import load_truthfulqa, is_correct
from entropy import load_model, compute_response_entropy
from analysis import compare_groups
import visualize

def main():
    print("H-M1: Token Entropy Captures Epistemic Uncertainty")
    print("=" * 50)

    # Load data
    print("Loading TruthfulQA...")
    questions = load_truthfulqa()
    print(f"Loaded {len(questions)} questions")

    # Load model
    print("Loading model...")
    model, tokenizer = load_model()
    print("Model loaded")

    # Process all questions
    records = []
    for q in tqdm(questions, desc="Processing"):
        entropy, response, num_tokens = compute_response_entropy(
            model, tokenizer, q["question"], config.MAX_NEW_TOKENS
        )
        correct = is_correct(response, q["correct_answers"])
        records.append({
            "question": q["question"],
            "response": response,
            "entropy": entropy,
            "num_tokens": num_tokens,
            "correct": correct
        })

    # Partition by correctness
    correct_entropies = [r["entropy"] for r in records if r["correct"]]
    incorrect_entropies = [r["entropy"] for r in records if not r["correct"]]

    print(f"\nCorrect: {len(correct_entropies)}, Incorrect: {len(incorrect_entropies)}")

    # Statistical analysis
    stats = compare_groups(correct_entropies, incorrect_entropies)
    print(f"\nResults:")
    print(f"  Mean entropy (correct): {stats['mean_correct']:.4f}")
    print(f"  Mean entropy (incorrect): {stats['mean_incorrect']:.4f}")
    print(f"  Cohen's d: {stats['effect_size_d']:.4f}")
    print(f"  p-value: {stats['pvalue']:.4e}")
    print(f"  Direction pass: {stats['direction_pass']}")
    print(f"  Effect pass (d>0.2): {stats['effect_pass']}")
    print(f"  GATE PASS: {stats['gate_pass']}")

    # Generate figures
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    visualize.plot_box(correct_entropies, incorrect_entropies,
                       os.path.join(config.FIGURES_DIR, "box_plot.png"))
    visualize.plot_histogram_kde(correct_entropies, incorrect_entropies,
                                 os.path.join(config.FIGURES_DIR, "histogram_kde.png"))

    all_entropies = [r["entropy"] for r in records]
    labels = [0 if r["correct"] else 1 for r in records]
    roc_auc = visualize.plot_roc(all_entropies, labels,
                                 os.path.join(config.FIGURES_DIR, "roc_curve.png"))

    lengths = [r["num_tokens"] for r in records]
    visualize.plot_entropy_vs_length(all_entropies, lengths,
                                     os.path.join(config.FIGURES_DIR, "entropy_vs_length.png"))

    # Save results
    results = {
        "hypothesis": "H-M1",
        "summary": stats,
        "roc_auc": roc_auc,
        "n_correct": len(correct_entropies),
        "n_incorrect": len(incorrect_entropies),
        "records": records
    }

    with open(config.RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {config.RESULTS_PATH}")
    print(f"Figures saved to {config.FIGURES_DIR}")

    return stats["gate_pass"]

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
