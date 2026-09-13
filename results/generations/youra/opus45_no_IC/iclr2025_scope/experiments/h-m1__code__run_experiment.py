"""H-M1: Pipeline orchestration - Full experiment using LongBench-v2."""

import os
import json
import time
import numpy as np
import torch

from config import (
    DOMAINS, DOMAIN_CATEGORIES,
    DataConfig, ModelConfig, EntropyConfig, GateConfig, ExperimentConfig
)
from data import load_longbench_v2, sample_domain, tokenize_probe
from entropy import load_model, extract_task_entropy, verify_mechanism
from stats import (
    aggregate_domain_means, compute_variance_ratio_from_samples,
    compute_eta_squared, evaluate_gate
)
import visualize


def run_pipeline(
    data_config: DataConfig = None,
    model_config: ModelConfig = None,
    entropy_config: EntropyConfig = None,
    gate_config: GateConfig = None,
    exp_config: ExperimentConfig = None,
) -> dict:
    """
    Full H-M1 pipeline using LongBench-v2 domains.

    Returns: {f_stat, p_value, eta_squared, gate_pass, domain_means, runtime_sec}
    """
    if data_config is None:
        data_config = DataConfig()
    if model_config is None:
        model_config = ModelConfig()
    if entropy_config is None:
        entropy_config = EntropyConfig()
    if gate_config is None:
        gate_config = GateConfig()
    if exp_config is None:
        exp_config = ExperimentConfig()

    start_time = time.time()

    print("=" * 60)
    print("H-M1: Attention Entropy Domain Discrimination")
    print("(Using LongBench-v2 domains)")
    print("=" * 60)

    # Create output directories
    os.makedirs(exp_config.output_dir, exist_ok=True)
    figure_dir = os.path.join(exp_config.output_dir, exp_config.figure_dir)
    os.makedirs(figure_dir, exist_ok=True)

    # Stage 1: Load model
    print("\n[1/6] Loading model...")
    model, tokenizer = load_model(model_config)

    # Stage 2: Load dataset
    print("\n[2/6] Loading LongBench-v2...")
    dataset = load_longbench_v2()
    print(f"  Loaded {len(dataset)} samples")

    # Verify mechanism with first sample
    print("\n[3/6] Verifying mechanism...")
    first_domain = DOMAINS[0]
    first_samples = sample_domain(dataset, first_domain, 1, data_config.seed)
    if first_samples:
        sample_input = tokenize_probe(first_samples[0], tokenizer, data_config.n_probe_tokens)
        verify_mechanism(model, sample_input)
    else:
        print(f"  Warning: No samples found for {first_domain}")

    # Stage 4: Extract entropy for all domains
    print(f"\n[4/6] Extracting entropy ({len(DOMAINS)} domains x {data_config.samples_per_domain} samples)...")
    entropy_by_domain = {}
    total_samples = 0

    for domain in DOMAINS:
        print(f"  Processing {domain[:30]}...", end=" ", flush=True)
        samples = sample_domain(dataset, domain, data_config.samples_per_domain, data_config.seed)
        if len(samples) == 0:
            print("NO SAMPLES - skipping")
            continue

        domain_entropy = extract_task_entropy(
            model, tokenizer, samples,
            data_config.n_probe_tokens, entropy_config
        )
        entropy_by_domain[domain] = domain_entropy
        total_samples += len(samples)
        print(f"shape={domain_entropy.shape}")

    # Stage 5: Assemble and save entropy matrix
    print("\n[5/6] Assembling entropy matrix...")
    entropy_tensors = [entropy_by_domain[d] for d in DOMAINS if d in entropy_by_domain]
    if not entropy_tensors:
        raise ValueError("No entropy data collected!")

    entropy_matrix = torch.cat(entropy_tensors, dim=0)
    entropy_matrix_np = entropy_matrix.numpy()
    np.save(os.path.join(exp_config.output_dir, "entropy_matrix.npy"), entropy_matrix_np)
    print(f"  Saved entropy_matrix.npy: shape={entropy_matrix_np.shape}")

    # Stage 6: Statistical analysis
    print("\n[6/6] Running statistical analysis...")
    domain_means = aggregate_domain_means(entropy_by_domain)
    f_stat, p_value = compute_variance_ratio_from_samples(entropy_by_domain)
    eta_squared = compute_eta_squared(entropy_by_domain)
    gate_pass = evaluate_gate(p_value, gate_config)

    print(f"  F-statistic: {f_stat:.4f}")
    print(f"  p-value: {p_value:.2e}")
    print(f"  eta-squared: {eta_squared:.4f}")
    print(f"  Gate (p < {gate_config.significance_threshold}): {'PASS' if gate_pass else 'FAIL'}")

    # Save results
    stats_results = {
        "f_stat": f_stat,
        "p_value": p_value,
        "eta_squared": eta_squared,
        "gate_pass": gate_pass,
        "threshold": gate_config.significance_threshold,
        "n_domains": len(entropy_by_domain),
        "total_samples": total_samples,
    }
    with open(os.path.join(exp_config.output_dir, "stats_results.json"), "w") as f:
        json.dump(stats_results, f, indent=2)

    with open(os.path.join(exp_config.output_dir, "domain_means.json"), "w") as f:
        json.dump(domain_means, f, indent=2)

    print("  Saved stats_results.json, domain_means.json")

    # Generate visualizations
    print("\nGenerating visualizations...")
    visualize.plot_gate_metrics(f_stat, p_value, gate_config.significance_threshold, figure_dir)
    print("  Gate metrics saved")

    # Domain heatmap
    samples_per_domain = data_config.samples_per_domain
    visualize.plot_entropy_heatmap(entropy_matrix_np, list(entropy_by_domain.keys()),
                                    samples_per_domain, figure_dir)
    print("  Entropy heatmap saved")

    # Domain boxplot
    visualize.plot_domain_boxplot(entropy_by_domain, figure_dir)
    print("  Domain boxplot saved")

    # Layer discrimination
    visualize.plot_layer_discrimination(entropy_by_domain, figure_dir)
    print("  Layer discrimination saved")

    runtime_sec = time.time() - start_time

    # Final summary
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Runtime: {runtime_sec:.1f}s")
    print(f"Domains analyzed: {len(entropy_by_domain)}")
    print(f"Total samples: {total_samples}")
    print(f"F-statistic: {f_stat:.4f}")
    print(f"p-value: {p_value:.2e}")
    print(f"eta-squared: {eta_squared:.4f}")
    print(f"GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")
    print("=" * 60)

    return {
        "f_stat": f_stat,
        "p_value": p_value,
        "eta_squared": eta_squared,
        "gate_pass": gate_pass,
        "domain_means": domain_means,
        "runtime_sec": runtime_sec,
    }


def main():
    """CLI entrypoint."""
    results = run_pipeline()

    if not results["gate_pass"]:
        print("\nWARNING: MUST_WORK gate FAILED")


if __name__ == "__main__":
    main()
