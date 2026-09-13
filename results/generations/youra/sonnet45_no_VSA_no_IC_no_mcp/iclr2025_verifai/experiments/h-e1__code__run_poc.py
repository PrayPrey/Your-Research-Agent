import json
import sys
from pathlib import Path

from config import ExperimentConfig
from data_loader import load_humaneval, extract_poc_subset
from model_loader import setup_device, load_codellama
from beam_search import run_beam_search
from metrics import time_generation, measure_ast_latency, compute_gate_metrics
from visualizations import plot_gate_metrics, plot_ast_latency_dist

def main():
    # Load config
    config_path = Path(__file__).parent / 'config.yaml'
    config = ExperimentConfig.from_yaml(str(config_path))

    print("="*60)
    print("h-e1 Beam Search Infrastructure PoC")
    print("="*60)

    # Setup device and model
    device = setup_device(config.model.device)
    model, tokenizer = load_codellama(config.model.name, device, config.model.dtype)

    # Load data
    print("\nLoading HumanEval dataset...")
    dataset = load_humaneval()
    problems = extract_poc_subset(dataset, config.dataset.poc_subset_size)
    prompts = [p['prompt'] for p in problems]
    print(f"Loaded {len(prompts)} problems for PoC")

    # Run beam search with timing
    print("\nRunning beam search...")
    def generate():
        return run_beam_search(
            model,
            tokenizer,
            prompts,
            k=config.beam_search.k,
            max_new_tokens=config.beam_search.max_new_tokens
        )

    candidates, elapsed_sec = time_generation(generate)
    print(f"Generation completed in {elapsed_sec:.1f} seconds ({elapsed_sec/60:.2f} minutes)")

    # Measure AST latency
    print("\nMeasuring AST parse latency...")
    latency_stats = measure_ast_latency(candidates)
    print(f"Mean latency: {latency_stats['mean']:.2f}ms")
    print(f"Min latency: {latency_stats['min']:.2f}ms")
    print(f"Max latency: {latency_stats['max']:.2f}ms")

    # Compute gate metrics
    gate_metrics = compute_gate_metrics(
        elapsed_sec,
        latency_stats['mean'],
        config.gate.time_target_seconds,
        config.gate.latency_target_ms
    )

    # Create output directories
    project_root = Path(__file__).parent.parent
    figures_dir = project_root / config.output.figures_dir
    outputs_dir = project_root / 'outputs'
    figures_dir.mkdir(exist_ok=True)
    outputs_dir.mkdir(exist_ok=True)

    # Generate visualizations
    print("\nGenerating visualizations...")
    plot_gate_metrics(gate_metrics, str(figures_dir / 'gate_metrics.png'))
    plot_ast_latency_dist(latency_stats['all'], str(figures_dir / 'ast_latency_dist.png'))

    # Save results
    results = {
        'gate_metrics': gate_metrics,
        'latency_stats': {
            'mean': latency_stats['mean'],
            'min': latency_stats['min'],
            'max': latency_stats['max']
        },
        'num_problems': len(prompts),
        'beam_width': config.beam_search.k,
        'total_candidates': sum(len(c) for c in candidates)
    }

    results_path = outputs_dir / 'results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved results to {results_path}")

    # Print summary
    print("\n" + "="*60)
    print("PoC Complete!")
    print("="*60)
    print(f"Gate Status: {'PASS' if gate_metrics['gate_pass'] else 'FAIL'}")
    print(f"  Time: {elapsed_sec:.1f}s / {gate_metrics['time_target']}s [{gate_metrics['time_pass']}]")
    print(f"  Latency: {latency_stats['mean']:.1f}ms / {gate_metrics['latency_target']}ms [{gate_metrics['latency_pass']}]")
    print("="*60)

    return 0 if gate_metrics['gate_pass'] else 1

if __name__ == '__main__':
    sys.exit(main())
