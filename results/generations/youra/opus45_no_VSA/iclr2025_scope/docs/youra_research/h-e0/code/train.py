"""Main training script for h-e0 linear separability experiment."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data import load_and_prepare_data
from model import BaselineClassifier, InstructionPrefixClassifier
from evaluate import compute_metrics, verify_mechanism, gate_check
from visualize import plot_gate_metrics, plot_confusion_matrix, plot_tsne_embeddings, plot_per_family_f1
from config import FIGURES_DIR, OUTPUTS_DIR, SEED

import numpy as np
np.random.seed(SEED)


def main():
    print("=" * 60)
    print("H-E0: Linear Separability of Instruction Prefixes")
    print("=" * 60)

    X_train, X_test, y_train, y_test, families = load_and_prepare_data()

    print("\n--- Training Baseline (Stratified Random) ---")
    baseline = BaselineClassifier()
    baseline.fit(X_train, y_train)
    baseline_pred = baseline.predict(X_test)
    baseline_metrics = compute_metrics(y_test, baseline_pred)
    print(f"Baseline Macro-F1: {baseline_metrics['macro_f1']:.4f}")

    print("\n--- Training Proposed (MiniLM + LogReg) ---")
    proposed = InstructionPrefixClassifier()
    proposed.fit(X_train, y_train)

    print("\n--- Verifying Mechanism ---")
    verify_mechanism(proposed, X_test, y_test)

    print("\n--- Evaluating Proposed Model ---")
    proposed_pred = proposed.predict(X_test)
    proposed_metrics = compute_metrics(y_test, proposed_pred)
    print(f"Proposed Macro-F1: {proposed_metrics['macro_f1']:.4f}")
    print(f"Proposed Accuracy: {proposed_metrics['accuracy']:.4f}")

    print("\n--- Gate Check ---")
    gate_result = gate_check(proposed_metrics['macro_f1'], baseline_metrics['macro_f1'])
    print(f"Gate PASS: {gate_result['pass']}")
    if gate_result['reasons']:
        print(f"Reasons: {gate_result['reasons']}")

    print("\n--- Generating Visualizations ---")
    os.makedirs(FIGURES_DIR, exist_ok=True)
    plot_gate_metrics(baseline_metrics['macro_f1'], proposed_metrics['macro_f1'], 0.75)
    plot_confusion_matrix(y_test, proposed_pred, families)
    train_emb = proposed.get_train_embeddings()
    if train_emb is not None:
        plot_tsne_embeddings(train_emb, y_train)
    plot_per_family_f1(proposed_metrics['report'])
    print(f"Figures saved to {FIGURES_DIR}")

    print("\n--- Saving Results ---")
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    results = {
        "hypothesis_id": "h-e0",
        "gate_type": "MUST_WORK",
        "gate_threshold": 0.75,
        "baseline": {
            "macro_f1": baseline_metrics['macro_f1'],
            "accuracy": baseline_metrics['accuracy'],
        },
        "proposed": {
            "macro_f1": proposed_metrics['macro_f1'],
            "accuracy": proposed_metrics['accuracy'],
            "per_family_f1": {k: v['f1-score'] for k, v in proposed_metrics['report'].items()
                             if k not in ['accuracy', 'macro avg', 'weighted avg']}
        },
        "gate_result": gate_result,
        "num_families": len(families),
        "families": families,
        "train_size": len(X_train),
        "test_size": len(X_test),
    }

    results_path = os.path.join(os.path.dirname(OUTPUTS_DIR), "experiment_results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {results_path}")

    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE")
    print(f"Gate Result: {'PASS' if gate_result['pass'] else 'FAIL'}")
    print(f"Proposed Macro-F1: {proposed_metrics['macro_f1']:.4f} (threshold: 0.75)")
    print("=" * 60)

    return gate_result['pass']


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
