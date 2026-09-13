"""Main pipeline orchestrator for h-m4."""

import json
import os
import sys
from typing import Dict

# Import modules
from config import *
from generator import HypothesisGenerator
from verifier import VerificationPipeline
from sampler import RandomSampler
from executor import ExperimentExecutor
from validator import StatisticalValidator
from visualizer import Visualizer


def run_pipeline(config: Dict) -> Dict:
    """Execute complete meta-research validation pipeline.

    Returns: {success_rate, gate_passed, metrics, figures}
    """
    print("=" * 80)
    print("H-M4: Post-Hoc Experimental Validation")
    print("=" * 80)

    # Create output directories
    os.makedirs(config['output_dir'], exist_ok=True)
    os.makedirs(config['figures_dir'], exist_ok=True)

    # Step 1: Generate hypothesis pool
    print("\n[1/6] Generating hypothesis pool...")
    generator = HypothesisGenerator(
        domains=config['domains'],
        complexity_levels=config['complexity_levels'],
        seed=config['seed']
    )
    hypotheses = generator.generate_pool(n=config['n_hypothesis_pool'])
    print(f"  Generated: {len(hypotheses)} hypotheses")

    # Save pool
    pool_path = os.path.join(config['output_dir'], 'hypothesis_pool.json')
    with open(pool_path, 'w') as f:
        json.dump(hypotheses, f, indent=2)

    # Step 2: Run verification pipeline
    print("\n[2/6] Running verification pipeline (KB + confounds)...")
    verifier = VerificationPipeline(
        kb_path=config['kb_path'],
        confound_patterns=config['confound_patterns']
    )

    for hypothesis in hypotheses:
        classification, reason = verifier.classify_hypothesis(hypothesis)
        hypothesis['system_classification'] = classification
        hypothesis['classification_reason'] = reason

    testable_count = sum(1 for h in hypotheses if h['system_classification'] == 'testable')
    print(f"  Classified: {testable_count} testable, {len(hypotheses) - testable_count} not-testable")

    # Save testable pool
    testable_pool = [h for h in hypotheses if h['system_classification'] == 'testable']
    testable_path = os.path.join(config['output_dir'], 'testable_pool.json')
    with open(testable_path, 'w') as f:
        json.dump(testable_pool, f, indent=2)

    # Step 3: Sample from testable pool
    print("\n[3/6] Sampling from testable pool...")
    sampler = RandomSampler(seed=config['seed'])
    sampled = sampler.sample_testable(hypotheses, k=config['n_sample_size'])
    print(f"  Sampled: {len(sampled)} hypotheses")

    if len(sampled) == 0:
        print("ERROR: No testable hypotheses found!")
        return {"error": "No testable hypotheses", "success_rate": 0.0, "gate_passed": False}

    # Save sampled
    sampled_path = os.path.join(config['output_dir'], 'sampled_hypotheses.json')
    with open(sampled_path, 'w') as f:
        json.dump(sampled, f, indent=2)

    # Step 4: Run experiments
    print("\n[4/6] Running simplified PoC experiments...")
    executor = ExperimentExecutor(seed=config['seed'])
    results = []
    for i, hypothesis in enumerate(sampled, 1):
        result = executor.run_experiment(hypothesis)
        results.append(result)
        print(f"  [{i}/{len(sampled)}] {result['hypothesis_id']}: p={result['p_value']:.4f} {'✓' if result['success'] else '✗'}")

    # Save results
    results_path = os.path.join(config['output_dir'], 'experimental_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    # Step 5: Validate and check gate
    print("\n[5/6] Statistical validation...")
    validator = StatisticalValidator(
        gate_threshold=config['gate_threshold'],
        baseline=config['baseline_threshold']
    )

    p_values = [r['p_value'] for r in results]
    success_rate = validator.compute_success_rate(p_values)
    gate_metrics = validator.check_gate(success_rate, p_values)

    print(f"  Success Rate: {success_rate:.2%} ({gate_metrics['successes']}/{gate_metrics['n_samples']})")
    print(f"  Gate Status: {gate_metrics['status']} (threshold: {config['gate_threshold']:.2%})")
    print(f"  PoC Status: {'PASS' if gate_metrics['poc_passed'] else 'FAIL'} (baseline: {config['baseline_threshold']:.2%})")
    print(f"  Binomial Test: p={gate_metrics['binomial_p']:.4f}")

    # Step 6: Generate visualizations
    print("\n[6/6] Generating visualizations...")
    visualizer = Visualizer(output_dir=config['figures_dir'])

    fig1 = visualizer.plot_gate_comparison(
        baseline=config['baseline_threshold'],
        proposed=success_rate,
        threshold=config['gate_threshold'],
        gate_passed=gate_metrics['gate_passed']
    )
    print(f"  Figure 1: {fig1}")

    fig2 = visualizer.plot_success_by_domain(results, sampled)
    print(f"  Figure 2: {fig2}")

    fig3 = visualizer.plot_classification_dist(hypotheses)
    print(f"  Figure 3: {fig3}")

    fig4 = visualizer.plot_pvalue_dist(p_values)
    print(f"  Figure 4: {fig4}")

    # Return metrics
    return {
        "success_rate": success_rate,
        "gate_passed": gate_metrics['gate_passed'],
        "poc_passed": gate_metrics['poc_passed'],
        "gate_status": gate_metrics['status'],
        "binomial_p": gate_metrics['binomial_p'],
        "successes": gate_metrics['successes'],
        "n_samples": gate_metrics['n_samples'],
        "testable_count": testable_count,
        "total_hypotheses": len(hypotheses),
        "figures": [fig1, fig2, fig3, fig4],
    }


if __name__ == "__main__":
    config = {
        "seed": SEED,
        "n_hypothesis_pool": N_HYPOTHESIS_POOL,
        "n_sample_size": N_SAMPLE_SIZE,
        "gate_threshold": GATE_THRESHOLD,
        "baseline_threshold": BASELINE_THRESHOLD,
        "domains": DOMAINS,
        "complexity_levels": COMPLEXITY_LEVELS,
        "kb_path": H_M1_KB_PATH,
        "confound_patterns": CONFOUND_PATTERNS,
        "output_dir": OUTPUT_DIR,
        "figures_dir": FIGURES_DIR,
    }

    metrics = run_pipeline(config)

    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"Success Rate: {metrics['success_rate']:.2%}")
    print(f"Gate Status: {metrics['gate_status']}")
    print(f"PoC Status: {'PASS' if metrics['poc_passed'] else 'FAIL'}")
    print("=" * 80)
