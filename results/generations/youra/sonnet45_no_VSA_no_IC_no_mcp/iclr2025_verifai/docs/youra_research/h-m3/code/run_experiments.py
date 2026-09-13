"""Main experiment orchestrator for h-m3 invalid beam pruning tracking."""

import torch
import json
import os
from human_eval.data import read_problems
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import ExperimentConfig
from experiments import experiment_a_tracking, experiment_b_final_validity, baseline_comparison
from analysis import (
    analyze_reduction_rates,
    analyze_final_validity,
    compare_baseline,
    save_beam_validity_logs,
    save_reduction_rates,
    save_final_validity,
    save_temporal_dynamics,
    save_baseline_comparison
)


def main():
    # Load config
    config = ExperimentConfig()
    print(f"Config: α={config.scoring.alpha}, β={config.scoring.beta}, k={config.beam_search.k}")

    # Setup device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # Load model
    print(f"Loading model: {config.model.name}")
    tokenizer = AutoTokenizer.from_pretrained(config.model.name)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        config.model.name,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None
    )
    if device == "cpu":
        model = model.to(device)
    model.eval()

    # Load HumanEval
    print("Loading HumanEval dataset")
    problems = read_problems()
    dataset = [
        {'task_id': task_id, 'prompt': problem['prompt']}
        for task_id, problem in problems.items()
    ]
    print(f"Dataset size: {len(dataset)} problems")

    # Experiment A: Combined scoring with tracking
    print("\n=== Experiment A: Combined Scoring (α=0.7, β=0.3) ===")
    combined_results = experiment_a_tracking(
        model, tokenizer, dataset,
        k=config.beam_search.k,
        alpha=config.scoring.alpha,
        beta=config.scoring.beta
    )
    print(f"Completed {len(combined_results['experiments'])} problems")

    # Experiment B: Final validity analysis
    print("\n=== Experiment B: Final Validity Analysis ===")
    validity_results = experiment_b_final_validity(combined_results)
    print(f"Mean valid proportion: {validity_results['mean_valid_proportion']:.2%}")

    # Experiment C: Baseline comparison
    print("\n=== Experiment C: Baseline Comparison (α=1.0, β=0.0) ===")
    baseline_results = baseline_comparison(
        model, tokenizer, dataset, k=config.beam_search.k
    )
    print(f"Baseline completed {len(baseline_results['experiments'])} problems")

    # Analysis
    print("\n=== Analysis ===")
    reduction_analysis = analyze_reduction_rates(combined_results)
    validity_analysis = analyze_final_validity(combined_results)
    comparison = compare_baseline(combined_results, baseline_results)

    print(f"Mean reduction rate: {reduction_analysis['mean']:.2%}")
    print(f"Gate pass (≥50%): {reduction_analysis['gate_pass']}")
    print(f"Mean final valid proportion: {validity_analysis['mean_valid_proportion']:.2%}")
    print(f"Gate pass (≥60%): {validity_analysis['gate_pass']}")
    print(f"Improvement over baseline: {comparison['improvement']:.2%}")

    # Save results
    print("\n=== Saving Results ===")
    save_beam_validity_logs(combined_results, config.output.beam_validity_logs)
    save_reduction_rates(combined_results, config.output.reduction_rates)
    save_final_validity(combined_results, config.output.final_validity)
    save_temporal_dynamics(combined_results, config.output.temporal_dynamics)
    save_baseline_comparison(combined_results, baseline_results, config.output.baseline_comparison)

    # Save experiment results JSON
    experiment_results = {
        'reduction_analysis': reduction_analysis,
        'validity_analysis': validity_analysis,
        'baseline_comparison': comparison,
        'gate_results': {
            'reduction_gate': reduction_analysis['gate_pass'],
            'validity_gate': validity_analysis['gate_pass'],
            'overall_pass': reduction_analysis['gate_pass'] and validity_analysis['gate_pass']
        }
    }

    os.makedirs('outputs', exist_ok=True)
    with open('outputs/experiment_results.json', 'w') as f:
        json.dump(experiment_results, f, indent=2)

    print("\n✅ All experiments complete")
    print(f"Overall gate status: {'PASS' if experiment_results['gate_results']['overall_pass'] else 'FAIL'}")


if __name__ == '__main__':
    main()
