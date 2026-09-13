"""H-M2: Pipeline orchestration - entropy-eviction tolerance experiment."""

import os
import sys
import json
import torch
import numpy as np
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import (DOMAINS, DataConfig, ModelConfig, StratConfig,
                    EvictionConfig, ExperimentConfig, GateConfig)
from data import load_all_samples_full
from stratify import (load_entropy_artifacts, domain_median_split,
                      assign_sample_groups, per_sample_entropy)
from h2o_eviction import verify_h2o_mechanism
from inference import run_all_conditions, compute_retention
from stats import compare_groups, evaluate_gate
from visualize import (plot_gate_bar, plot_boxplot,
                       plot_scatter_entropy_retention, plot_heatmap_domain_ratio)


def run_pipeline(strat_config: StratConfig = None,
                 model_config: ModelConfig = None,
                 eviction_config: EvictionConfig = None,
                 experiment_config: ExperimentConfig = None,
                 gate_config: GateConfig = None) -> dict:
    """Full H-M2 pipeline."""
    if strat_config is None:
        strat_config = StratConfig()
    if model_config is None:
        model_config = ModelConfig()
    if eviction_config is None:
        eviction_config = EvictionConfig()
    if experiment_config is None:
        experiment_config = ExperimentConfig()
    if gate_config is None:
        gate_config = GateConfig()

    os.makedirs(experiment_config.figure_dir, exist_ok=True)

    print("=" * 60)
    print("H-M2: Entropy-Eviction Tolerance Experiment")
    print("=" * 60)

    print("\n[1/8] Loading entropy artifacts from H-M1...")
    entropy_matrix, domain_means = load_entropy_artifacts(strat_config)
    print(f"  Entropy matrix: {entropy_matrix.shape}")
    print(f"  Domain means: {domain_means}")

    print("\n[2/8] Stratifying by entropy...")
    high_domains, low_domains = domain_median_split(domain_means)
    print(f"  High-entropy domains: {high_domains}")
    print(f"  Low-entropy domains: {low_domains}")

    group_mask = assign_sample_groups(DOMAINS, 30, high_domains)
    print(f"  High-entropy samples: {group_mask.sum()}, Low: {(~group_mask).sum()}")

    print("\n[3/8] Loading samples...")
    samples = load_all_samples_full()
    assert len(samples) == 180, f"Expected 180 samples, got {len(samples)}"

    print("\n[4/8] Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(model_config.model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_config.model_name,
        torch_dtype=torch.float16 if model_config.torch_dtype == "float16" else torch.float32,
        device_map=model_config.device_map,
    )
    model.eval()
    print(f"  Model loaded: {model_config.model_name}")

    print("\n[5/8] Verifying H2O mechanism...")
    try:
        verify_h2o_mechanism(model, tokenizer, samples[0], ratio=0.4)
        print("  H2O mechanism verified")
    except Exception as e:
        print(f"  Warning: H2O verification failed: {e}")
        print("  Continuing with experiment...")

    print("\n[6/8] Running inference (3 conditions)...")
    acc_by_condition = run_all_conditions(
        model, tokenizer, samples, eviction_config,
        experiment_config.max_new_tokens
    )

    print("\n[7/8] Computing retention and statistics...")
    retention = compute_retention(acc_by_condition)

    primary_ratio = 0.4
    high_retention = retention[primary_ratio][group_mask]
    low_retention = retention[primary_ratio][~group_mask]

    stats_result = compare_groups(high_retention, low_retention)
    gate_pass = evaluate_gate(
        stats_result["p_value"],
        stats_result["high_mean"],
        stats_result["low_mean"],
        stats_result["cohens_d"],
        gate_config.p_threshold,
        gate_config.min_d
    )
    stats_result["gate_pass"] = gate_pass

    print(f"\n  Statistics (ratio={primary_ratio}):")
    print(f"    High-entropy mean: {stats_result['high_mean']:.4f} ± {stats_result['high_std']:.4f}")
    print(f"    Low-entropy mean:  {stats_result['low_mean']:.4f} ± {stats_result['low_std']:.4f}")
    print(f"    Test: {stats_result['test_used']}, p={stats_result['p_value']:.4e}")
    print(f"    Cohen's d: {stats_result['cohens_d']:.3f}")
    print(f"    GATE: {'PASS' if gate_pass else 'FAIL'}")

    print("\n[8/8] Generating visualizations...")
    plot_gate_bar(high_retention, low_retention, stats_result, experiment_config.figure_dir)
    plot_boxplot(high_retention, low_retention, experiment_config.figure_dir)

    sample_entropy = per_sample_entropy(entropy_matrix)
    plot_scatter_entropy_retention(sample_entropy, retention[primary_ratio],
                                   group_mask, experiment_config.figure_dir)

    retention_by_domain_ratio = {}
    for i, domain in enumerate(DOMAINS):
        start = i * 30
        end = start + 30
        retention_by_domain_ratio[domain] = {}
        for ratio in [0.8, 0.4]:
            retention_by_domain_ratio[domain][ratio] = float(retention[ratio][start:end].mean())
    plot_heatmap_domain_ratio(retention_by_domain_ratio, experiment_config.figure_dir)

    results = {
        "hypothesis": "h-m2",
        "timestamp": datetime.now().isoformat(),
        "primary_ratio": primary_ratio,
        "statistics": stats_result,
        "gate_pass": gate_pass,
        "accuracy_by_ratio": {str(k): {"mean": float(np.mean(v)), "std": float(np.std(v))}
                              for k, v in acc_by_condition.items()},
        "retention_by_ratio": {str(k): {"mean": float(v.mean()), "std": float(v.std())}
                               for k, v in retention.items()},
        "domain_means": domain_means,
        "high_domains": high_domains,
        "low_domains": low_domains,
        "n_samples": {"high": int(group_mask.sum()), "low": int((~group_mask).sum())},
    }

    results_path = os.path.join(experiment_config.output_dir, experiment_config.results_path)
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved: {results_path}")

    np.save(os.path.join(experiment_config.output_dir, 'retention_matrix.npy'),
            np.stack([retention[r] for r in eviction_config.retention_ratios]))

    print("\n" + "=" * 60)
    print(f"H-M2 COMPLETE: GATE {'PASSED' if gate_pass else 'FAILED'}")
    print("=" * 60)

    return results


def main():
    """CLI entry point."""
    results = run_pipeline()
    sys.exit(0 if results["gate_pass"] else 1)


if __name__ == "__main__":
    main()
