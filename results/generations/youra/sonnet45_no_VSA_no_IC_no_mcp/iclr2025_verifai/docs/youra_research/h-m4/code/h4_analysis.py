"""Analysis module for h-m4 results."""

import json
import matplotlib.pyplot as plt
import numpy as np


def plot_validity_distribution(results: dict, save_path: str):
    """Plot valid vs invalid final outputs."""
    valid = sum(results['validity_labels'])
    invalid = len(results['validity_labels']) - valid

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(['Valid', 'Invalid'], [valid, invalid], color=['green', 'red'])
    ax.set_ylabel('Count')
    ax.set_title('Final Output Syntax Validity Distribution')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_baseline_comparison(greedy_results: dict, beam_results: dict, save_path: str):
    """Plot greedy vs beam search error rates."""
    greedy_error = greedy_results['syntax_error_rate']
    beam_error = beam_results['syntax_error_rate']

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(['Greedy', 'Beam Search'], [greedy_error * 100, beam_error * 100], color=['orange', 'blue'])
    ax.set_ylabel('Syntax Error Rate (%)')
    ax.set_title('Greedy vs Beam Search Syntax Error Rate')
    ax.axhline(y=40, color='r', linestyle='--', label='Target (≤40%)')
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_selection_accuracy(selection_results: dict, save_path: str):
    """Plot selection accuracy by beam availability."""
    fig, ax = plt.subplots(figsize=(6, 4))
    accuracy_1plus = selection_results['accuracy_1plus'] * 100
    accuracy_3plus = selection_results['accuracy_3plus'] * 100

    ax.bar(['≥1 Valid Beam', '≥3 Valid Beams'], [accuracy_1plus, accuracy_3plus], color=['purple', 'cyan'])
    ax.set_ylabel('Selection Accuracy (%)')
    ax.set_title('Selection Accuracy by Beam Availability')
    ax.axhline(y=90, color='r', linestyle='--', label='Target (≥90%)')
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_strategy_comparison(strategy_results: dict, save_path: str):
    """Plot validity per strategy."""
    strategies = ['argmax_validity', 'validity_first_validity', 'random_valid_validity']
    labels = ['Argmax', 'Validity-First', 'Random Valid']
    values = [strategy_results[s] * 100 for s in strategies]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values, color=['blue', 'green', 'orange'])
    ax.set_ylabel('Syntax Validity Rate (%)')
    ax.set_title('Selection Strategy Comparison')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_gate_metrics(beam_results: dict, greedy_results: dict, save_path: str):
    """MANDATORY: Plot target vs actual gate metrics."""
    validity_rate = beam_results['syntax_validity_rate'] * 100
    greedy_error = greedy_results['syntax_error_rate'] * 100
    beam_error = beam_results['syntax_error_rate'] * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Primary metric 1: Syntax validity rate
    ax1.bar(['Target', 'Actual'], [60, validity_rate], color=['gray', 'green'])
    ax1.set_ylabel('Syntax Validity Rate (%)')
    ax1.set_title('Primary Gate 1: Final Output Validity')
    ax1.axhline(y=60, color='r', linestyle='--', label='Min Threshold')
    ax1.legend()

    # Primary metric 2: Error rate comparison
    ax2.bar(['Greedy Baseline', 'Beam Search'], [greedy_error, beam_error], color=['orange', 'blue'])
    ax2.set_ylabel('Syntax Error Rate (%)')
    ax2.set_title('Primary Gate 2: Baseline Comparison')
    ax2.legend()

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def save_results(results: dict, path: str):
    """Save results to JSON."""
    # Convert numpy arrays to lists for JSON serialization
    serializable = {}
    for key, value in results.items():
        if isinstance(value, (list, tuple)):
            serializable[key] = [
                v.tolist() if hasattr(v, 'tolist') else v for v in value
            ]
        elif hasattr(value, 'tolist'):
            serializable[key] = value.tolist()
        else:
            serializable[key] = value

    with open(path, 'w') as f:
        json.dump(serializable, f, indent=2)
