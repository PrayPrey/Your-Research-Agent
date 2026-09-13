"""Main execution script for h-e1 experiment."""
import os
import sys
import json
import random
import torch
import numpy as np
from tqdm import tqdm
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import CONFIG, validate_config
from data import TaskStratifier
from execution import AgentMeshOrchestrator
from analysis import TraceAnalyzer
from visualization import FigureGenerator


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_model_and_tokenizer(config):
    """Load CodeLlama model and tokenizer."""
    print(f"Loading model: {config.model.model_id}")

    tokenizer = AutoTokenizer.from_pretrained(config.model.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        config.model.model_id,
        torch_dtype=torch.float16 if config.model.torch_dtype == "auto" else torch.float32,
        device_map=config.model.device_map,
        load_in_8bit=config.model.load_in_8bit
    )

    print("Model loaded successfully")
    return model, tokenizer


def stratify_tasks(config):
    """Stratify SWE-bench tasks."""
    print("Loading SWE-bench dataset...")
    dataset = load_dataset(
        config.data.swebench_dataset,
        split=config.data.swebench_split,
        cache_dir=config.data.cache_dir
    )

    print("Loading CWE distribution and keywords...")
    with open(config.data.purplelama_cwe_dist_path, 'r') as f:
        target_dist = json.load(f)

    with open('data/h-e1/cwe_keywords.json', 'r') as f:
        cwe_keywords = json.load(f)

    print(f"Stratifying to {config.data.target_sample_size} tasks...")
    stratifier = TaskStratifier(target_dist, cwe_keywords, config.data.seed)
    stratified_tasks = stratifier.stratify_tasks(
        dataset,
        n_samples=config.data.target_sample_size,
        min_per_cwe=config.data.min_samples_per_cwe
    )

    # Save stratified tasks
    output_path = 'data/h-e1/stratified_tasks.json'
    with open(output_path, 'w') as f:
        json.dump(stratified_tasks, f, indent=2)

    report = stratifier.get_stratification_report(stratified_tasks)
    print(f"Stratification complete: {report['total_tasks']} tasks")
    print(f"CWE distribution: {report['cwe_distribution']}")

    return stratified_tasks


def execute_batch(tasks, orchestrator, config):
    """Execute batch of tasks with checkpointing."""
    checkpoint_file = os.path.join(config.trace.checkpoint_dir, 'checkpoint.json')

    # Check for resume
    start_idx = 0
    if config.resume_from_checkpoint and os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
            start_idx = checkpoint.get('last_completed_index', 0) + 1
            print(f"Resuming from task {start_idx}")

    all_traces = []

    for idx in tqdm(range(start_idx, len(tasks)), desc="Executing tasks"):
        task = tasks[idx]

        try:
            result = orchestrator.execute_task(task)

            # Save trace
            if result['revision_log']:
                orchestrator.save_trace(
                    task['task_id'],
                    result['revision_log'],
                    config.trace.trace_output_dir
                )
                all_traces.extend(result['revision_log'])

            # Checkpoint every N tasks
            if (idx + 1) % config.trace.checkpoint_interval == 0:
                orchestrator.save_checkpoint(
                    {'last_completed_index': idx, 'total_tasks': len(tasks)},
                    checkpoint_file
                )

        except Exception as e:
            print(f"Task {task['task_id']} failed: {e}")
            continue

    # Final checkpoint
    orchestrator.save_checkpoint(
        {'last_completed_index': len(tasks) - 1, 'total_tasks': len(tasks)},
        checkpoint_file
    )

    return all_traces


def analyze_traces(config):
    """Analyze traces and compute metrics."""
    print("Analyzing traces...")

    with open(config.data.purplelama_cwe_dist_path, 'r') as f:
        target_dist = json.load(f)

    analyzer = TraceAnalyzer(target_dist)
    traces = analyzer.load_traces(config.trace.trace_output_dir)

    if not traces:
        print("WARNING: No traces found!")
        return None, None

    metrics = analyzer.compute_metrics(traces)
    gate_decision = analyzer.check_gate_condition(metrics)

    # Save metrics
    os.makedirs(os.path.dirname(config.metrics.metrics_output_path), exist_ok=True)
    with open(config.metrics.metrics_output_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    with open(config.metrics.gate_decision_path, 'w') as f:
        json.dump(gate_decision, f, indent=2)

    print(f"\nMetrics:")
    print(f"  Security %: {metrics['security_percentage']:.2f}%")
    print(f"  KL-divergence: {metrics['kl_divergence']:.4f}")
    print(f"  Jaccard: {metrics['jaccard_agreement']:.4f}")
    print(f"\nGate Decision: {'PASS' if gate_decision['pass'] else 'FAIL'}")
    print(f"  Reason: {gate_decision['reason']}")

    return metrics, gate_decision


def generate_figures(metrics, config):
    """Generate visualizations."""
    print("Generating figures...")

    with open(config.data.purplelama_cwe_dist_path, 'r') as f:
        target_dist = json.load(f)

    targets = {
        'security_percentage': config.metrics.target_security_percentage,
        'kl_divergence': config.metrics.target_kl_divergence,
        'jaccard_agreement': config.metrics.target_jaccard_agreement,
        'cwe_distribution': target_dist
    }

    analyzer = TraceAnalyzer(target_dist)
    traces = analyzer.load_traces(config.trace.trace_output_dir)

    visualizer = FigureGenerator(config.visualization.output_dir)
    visualizer.save_all_figures(metrics, targets, traces)


def generate_validation_report(metrics, gate_decision, config):
    """Generate validation report."""
    report_path = 'docs/youra_research/h-e1/04_validation.md'

    with open(report_path, 'w') as f:
        f.write(f"# Validation Report: h-e1\n\n")
        f.write(f"**Date:** {CONFIG.hypothesis_id}\n")
        f.write(f"**Gate Status:** {'✓ PASS' if gate_decision['pass'] else '✗ FAIL'}\n\n")
        f.write(f"## Metrics\n\n")
        f.write(f"| Metric | Target | Actual | Status |\n")
        f.write(f"|--------|--------|--------|--------|\n")
        f.write(f"| Security % | ≥{config.metrics.target_security_percentage}% | {metrics['security_percentage']:.2f}% | {'✓' if gate_decision['conditions']['security_pct_pass'] else '✗'} |\n")
        f.write(f"| KL-Divergence | <{config.metrics.target_kl_divergence} | {metrics['kl_divergence']:.4f} | {'✓' if gate_decision['conditions']['kl_div_pass'] else '✗'} |\n")
        f.write(f"| Jaccard | ≥{config.metrics.target_jaccard_agreement} | {metrics['jaccard_agreement']:.4f} | {'✓' if gate_decision['conditions']['jaccard_pass'] else '✗'} |\n\n")
        f.write(f"## Statistics\n\n")
        f.write(f"- Total revisions: {metrics['total_revisions']}\n")
        f.write(f"- Security revisions: {metrics['security_revisions']}\n")
        f.write(f"- CWE distribution: {metrics['cwe_distribution']}\n\n")
        f.write(f"## Gate Decision\n\n")
        f.write(f"{gate_decision['reason']}\n\n")
        f.write(f"## Figures\n\n")
        f.write(f"- [Gate Metrics](figures/gate_metrics.png)\n")
        f.write(f"- [CWE Comparison](figures/cwe_comparison.png)\n")
        f.write(f"- [Revision Timeline](figures/revision_timeline.png)\n")

    print(f"Validation report saved to {report_path}")


def main():
    """Main execution pipeline."""
    print("=" * 60)
    print("h-e1: Security-Instrumented Multi-Agent Trace Generation")
    print("=" * 60)

    # Validate config
    validate_config(CONFIG)
    set_seed(CONFIG.seed)

    # Step 1: Load model (comment out for testing without GPU)
    # model, tokenizer = load_model_and_tokenizer(CONFIG)

    # Step 2: Stratify tasks
    tasks = stratify_tasks(CONFIG)

    # Step 3: Execute batch (requires model)
    # orchestrator = AgentMeshOrchestrator(
    #     model, tokenizer,
    #     {
    #         'max_debugger_iterations': CONFIG.agentmesh.max_debugger_iterations,
    #         'timeout_per_task': CONFIG.agentmesh.timeout_per_task
    #     }
    # )
    # traces = execute_batch(tasks, orchestrator, CONFIG)

    # Step 4: Analyze traces (requires traces from step 3)
    # metrics, gate_decision = analyze_traces(CONFIG)

    # Step 5: Generate figures
    # if metrics:
    #     generate_figures(metrics, CONFIG)
    #     generate_validation_report(metrics, gate_decision, CONFIG)

    print("\nExperiment setup complete. Uncomment model loading and execution steps to run full experiment.")


if __name__ == '__main__':
    main()
