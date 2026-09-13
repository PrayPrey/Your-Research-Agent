"""Main experiment runner for h-m4 final valid output selection."""

import sys
import os

# Add current directory first, then h-m3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../h-m3/code'))

import json
from h4_config import ExperimentConfig
from h4_data_loader import load_humaneval
from h4_model_loader import load_model_and_tokenizer
from experiments import (
    experiment_a_final_validity,
    experiment_b_greedy_baseline,
    experiment_c_selection_quality,
    experiment_d_strategy_comparison
)
from error_comparator import compute_error_reduction
from h4_analysis import (
    plot_validity_distribution,
    plot_baseline_comparison,
    plot_selection_accuracy,
    plot_strategy_comparison,
    plot_gate_metrics,
    save_results
)


def main():
    # Load config
    config = ExperimentConfig()
    os.makedirs(config.output.results_dir, exist_ok=True)
    os.makedirs(config.output.figures_dir, exist_ok=True)

    print("Loading dataset and model...")
    dataset = load_humaneval()
    model, tokenizer = load_model_and_tokenizer(
        config.model.name,
        config.model.device,
        config.model.dtype
    )

    print(f"\nExperiment A: Final Output Validity (k={config.beam_search.k}, α={config.scoring.alpha}, β={config.scoring.beta})")
    beam_results = experiment_a_final_validity(
        model,
        tokenizer,
        dataset,
        config.beam_search.k,
        config.scoring.alpha,
        config.scoring.beta
    )
    print(f"Syntax validity rate: {beam_results['syntax_validity_rate']:.2%}")
    print(f"Syntax error rate: {beam_results['syntax_error_rate']:.2%}")
    save_results(beam_results, config.output.final_outputs)

    print("\nExperiment B: Greedy Baseline")
    greedy_results = experiment_b_greedy_baseline(model, tokenizer, dataset)
    print(f"Greedy syntax error rate: {greedy_results['syntax_error_rate']:.2%}")
    save_results(greedy_results, config.output.greedy_baseline)

    print("\nComputing error reduction...")
    error_comparison = compute_error_reduction(
        greedy_results['greedy_outputs'],
        beam_results['selected_outputs']
    )
    print(f"Absolute reduction: {error_comparison['absolute_reduction']:.2%}")
    print(f"Relative reduction: {error_comparison['relative_reduction']:.1f}%")
    save_results(error_comparison, config.output.error_comparison)

    print("\nExperiment C: Selection Quality Analysis")
    selection_results = experiment_c_selection_quality(beam_results)
    print(f"Accuracy (≥1 valid beam): {selection_results['accuracy_1plus']:.2%}")
    print(f"Accuracy (≥3 valid beams): {selection_results['accuracy_3plus']:.2%}")
    print(f"Miss rate: {selection_results['miss_rate']:.2%}")
    save_results(selection_results, config.output.selection_quality)

    print("\nExperiment D: Strategy Comparison")
    strategy_results = experiment_d_strategy_comparison(beam_results)
    print(f"Argmax validity: {strategy_results['argmax_validity']:.2%}")
    print(f"Validity-first validity: {strategy_results['validity_first_validity']:.2%}")
    print(f"Random-valid validity: {strategy_results['random_valid_validity']:.2%}")
    print(f"Best strategy: {strategy_results['best_strategy']}")
    save_results(strategy_results, config.output.strategy_comparison)

    print("\nGenerating visualizations...")
    plot_validity_distribution(beam_results, f"{config.output.figures_dir}/validity_distribution.png")
    plot_baseline_comparison(greedy_results, beam_results, f"{config.output.figures_dir}/baseline_comparison.png")
    plot_selection_accuracy(selection_results, f"{config.output.figures_dir}/selection_accuracy.png")
    plot_strategy_comparison(strategy_results, f"{config.output.figures_dir}/strategy_comparison.png")
    plot_gate_metrics(beam_results, greedy_results, f"{config.output.figures_dir}/gate_metrics.png")

    print("\nEvaluating gates...")
    gate_passed = True
    gate_notes = []

    # Primary Gate 1: Syntax validity rate ≥60%
    if beam_results['syntax_validity_rate'] < config.gate.syntax_validity_rate_min:
        gate_passed = False
        gate_notes.append(f"FAILED: Syntax validity {beam_results['syntax_validity_rate']:.2%} < {config.gate.syntax_validity_rate_min:.2%}")
    else:
        gate_notes.append(f"PASSED: Syntax validity {beam_results['syntax_validity_rate']:.2%} ≥ {config.gate.syntax_validity_rate_min:.2%}")

    # Primary Gate 2: Beam error < Greedy error
    if beam_results['syntax_error_rate'] >= greedy_results['syntax_error_rate']:
        gate_passed = False
        gate_notes.append(f"FAILED: Beam error {beam_results['syntax_error_rate']:.2%} ≥ greedy error {greedy_results['syntax_error_rate']:.2%}")
    else:
        gate_notes.append(f"PASSED: Beam error {beam_results['syntax_error_rate']:.2%} < greedy error {greedy_results['syntax_error_rate']:.2%}")

    # Secondary Gate: Selection accuracy ≥90% (≥3 valid beams)
    if selection_results['accuracy_3plus'] < config.gate.selection_accuracy_min:
        gate_notes.append(f"WARNING: Selection accuracy {selection_results['accuracy_3plus']:.2%} < {config.gate.selection_accuracy_min:.2%} (investigate scoring)")
    else:
        gate_notes.append(f"PASSED: Selection accuracy {selection_results['accuracy_3plus']:.2%} ≥ {config.gate.selection_accuracy_min:.2%}")

    print("\nGate Results:")
    for note in gate_notes:
        print(f"  {note}")

    final_verdict = "PASS" if gate_passed else "FAIL"
    print(f"\nFinal Gate Verdict: {final_verdict}")

    # Save gate verdict
    gate_result = {
        'verdict': final_verdict,
        'notes': gate_notes,
        'metrics': {
            'syntax_validity_rate': beam_results['syntax_validity_rate'],
            'beam_error_rate': beam_results['syntax_error_rate'],
            'greedy_error_rate': greedy_results['syntax_error_rate'],
            'error_reduction_absolute': error_comparison['absolute_reduction'],
            'error_reduction_relative': error_comparison['relative_reduction'],
            'selection_accuracy_1plus': selection_results['accuracy_1plus'],
            'selection_accuracy_3plus': selection_results['accuracy_3plus']
        }
    }
    with open('results/gate_verdict.json', 'w') as f:
        json.dump(gate_result, f, indent=2)

    print("\nExperiment complete. Results saved to results/")
    print("EXPERIMENT COMPLETE")


if __name__ == '__main__':
    main()
