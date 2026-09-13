"""Main experiment runner for H-M1: Semantic Entropy / Error Correlation."""

import os
import sys
import json
import numpy as np
from datetime import datetime
from tqdm import tqdm

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (SEED, SAMPLE_SIZE, N_GENERATIONS, TEMPERATURE,
                    RESULTS_PATH, OUTPUTS_DIR, FIGURES_DIR)
from data_loader import load_triviaqa
from response_generator import ResponseGenerator
from entailment_clusterer import EntailmentClusterer
from semantic_entropy import compute_semantic_entropy
from correctness import has_any_correct
from stat_eval import evaluate_gate
from visualize import generate_all_figures


def main():
    print("=" * 60)
    print("H-M1: Semantic Entropy / Error Correlation Experiment")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Sample size: {SAMPLE_SIZE}")
    print(f"N generations: {N_GENERATIONS}")
    print(f"Temperature: {TEMPERATURE}")
    print()

    # Step 1: Load data
    print("[1/6] Loading TriviaQA data...")
    data = load_triviaqa(seed=SEED, n=SAMPLE_SIZE)
    print(f"Loaded {len(data)} questions")

    # Step 2: Initialize models
    print("\n[2/6] Loading models...")
    generator = ResponseGenerator()
    clusterer = EntailmentClusterer()

    # Step 3: Generate responses and compute entropy
    print(f"\n[3/6] Generating responses and computing semantic entropy...")
    results_per_question = []
    entropy_values = []
    correctness_labels = []

    for i, item in enumerate(tqdm(data, desc="Processing")):
        question = item["question"]
        aliases = item["aliases"]

        # Generate N responses
        responses = generator.generate_n(question, n=N_GENERATIONS)
        texts = [r["text"] for r in responses]
        logprobs = [r["logprob"] for r in responses]

        # Compute semantic entropy
        se = compute_semantic_entropy(texts, logprobs, clusterer, question)

        # Check if any response is correct
        is_correct_set = has_any_correct(texts, aliases)

        entropy_values.append(se)
        correctness_labels.append(is_correct_set)

        results_per_question.append({
            "question_idx": i,
            "question": question[:100],
            "semantic_entropy": se,
            "is_correct": is_correct_set,
            "n_responses": len(responses)
        })

        # Checkpoint every 100 questions
        if (i + 1) % 100 == 0:
            print(f"\nCheckpoint: {i+1}/{len(data)} processed")
            n_correct = sum(correctness_labels)
            print(f"  Accuracy so far: {n_correct}/{i+1} = {n_correct/(i+1):.2%}")

    # Step 4: Split by correctness
    print("\n[4/6] Analyzing results...")
    entropy_values = np.array(entropy_values)
    correctness_labels = np.array(correctness_labels)

    entropy_correct = entropy_values[correctness_labels]
    entropy_incorrect = entropy_values[~correctness_labels]

    print(f"Correct questions: {len(entropy_correct)}")
    print(f"Incorrect questions: {len(entropy_incorrect)}")

    # Step 5: Statistical evaluation
    print("\n[5/6] Running statistical tests...")
    gate_results = evaluate_gate(entropy_correct, entropy_incorrect)

    print(f"\n{'='*40}")
    print("GATE RESULTS (MUST_WORK)")
    print(f"{'='*40}")
    print(f"Mean entropy (correct):   {gate_results['mean_entropy_correct']:.4f}")
    print(f"Mean entropy (incorrect): {gate_results['mean_entropy_incorrect']:.4f}")
    print(f"p-value:                  {gate_results['p_value']:.6f}")
    print(f"Cohen's d:                {gate_results['cohens_d']:.4f}")
    print(f"AUROC:                    {gate_results['auroc']:.4f}")
    print(f"{'='*40}")
    print(f"GATE PASSED: {gate_results['gate_passed']}")
    print(f"{'='*40}")

    # Step 6: Generate figures
    print("\n[6/6] Generating figures...")
    figure_paths = generate_all_figures(gate_results, entropy_correct, entropy_incorrect)

    # Save results
    final_results = {
        "hypothesis_id": "h-m1",
        "hypothesis_type": "MECHANISM",
        "gate_type": "MUST_WORK",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "sample_size": SAMPLE_SIZE,
            "n_generations": N_GENERATIONS,
            "temperature": TEMPERATURE,
            "seed": SEED
        },
        "metrics": gate_results,
        "gate_passed": gate_results["gate_passed"],
        "figures": figure_paths,
        "per_question_results": results_per_question[:20]  # Save first 20 for verification
    }

    with open(RESULTS_PATH, 'w') as f:
        json.dump(final_results, f, indent=2)
    print(f"\nResults saved to: {RESULTS_PATH}")

    # Save detailed data
    np.save(os.path.join(OUTPUTS_DIR, "entropy_values.npy"), entropy_values)
    np.save(os.path.join(OUTPUTS_DIR, "correctness_labels.npy"), correctness_labels)
    print(f"Detailed data saved to: {OUTPUTS_DIR}")

    print(f"\nExperiment completed at: {datetime.now().isoformat()}")

    return gate_results["gate_passed"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
