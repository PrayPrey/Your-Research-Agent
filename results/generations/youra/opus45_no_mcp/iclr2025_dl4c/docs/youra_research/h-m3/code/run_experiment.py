#!/usr/bin/env python3
"""End-to-end pipeline for H-M3 gradient noise analysis."""
import os
import sys
import json
import random
import numpy as np
import torch

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
H_M1_CODE = os.path.join(CODE_DIR, '../../h-m1/code')
H_M2_CODE = os.path.join(CODE_DIR, '../../h-m2/code')
sys.path.insert(0, CODE_DIR)
sys.path.insert(0, H_M1_CODE)
sys.path.insert(0, H_M2_CODE)

from h_m3_config import get_config, MODEL_NAME
from sample_builder import collect_stratified_samples
from noise_analysis import run_noise_analysis
from h_m3_stats import compare_concentration, summarize_noise_ratio
from h_m3_viz import (
    plot_concentration_boxplot,
    plot_noise_ratio_histogram,
    plot_gradient_heatmap,
    plot_concentration_vs_noise_scatter,
)


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def main():
    os.chdir(CODE_DIR)
    config = get_config()
    set_seed(config.seed)

    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    print("=" * 60)
    print("H-M3: Unreliable Localization Causes Gradient Noise")
    print("=" * 60)

    from transformers import T5ForConditionalGeneration, RobertaTokenizer
    print(f"Loading model: {MODEL_NAME}")
    tokenizer = RobertaTokenizer.from_pretrained(MODEL_NAME)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    # Load REAL APPS dataset (not synthetic)
    from datasets import load_dataset
    print(f"\nLoading APPS dataset from HuggingFace...")
    apps_dataset = load_dataset("codeparrot/apps", split="train")
    print(f"Dataset loaded: {len(apps_dataset)} samples")

    print(f"\nCollecting {config.samples.n_per_category * 2} REAL samples from APPS...")
    samples = collect_stratified_samples(
        model=model,
        tokenizer=tokenizer,
        dataset=apps_dataset,
        n_per_category=config.samples.n_per_category,
        seed=config.samples.seed
    )
    print(f"Collected {len(samples)} total samples")

    print("\nRunning noise analysis...")
    results = run_noise_analysis(
        model, tokenizer, samples,
        target_penalty=config.noise.target_penalty,
        other_penalty=config.noise.other_penalty
    )

    u_line_conc = [r['gt_concentration'] for r in results['u_line']]
    u_ignore_conc = [r['gt_concentration'] for r in results['u_ignore']]
    u_ignore_noise = [r['noise_ratio'] for r in results['u_ignore']]

    print("\nComputing statistics...")
    stats_result = compare_concentration(u_line_conc, u_ignore_conc)
    noise_summary = summarize_noise_ratio(u_ignore_noise)

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"U_line GT concentration:  mean={stats_result['u_line_mean']:.4f} (std={stats_result['u_line_std']:.4f})")
    print(f"U_ignore GT concentration: mean={stats_result['u_ignore_mean']:.4f} (std={stats_result['u_ignore_std']:.4f})")
    print(f"Difference: {stats_result['u_line_mean'] - stats_result['u_ignore_mean']:.4f}")
    print(f"t-test p-value: {stats_result['t_p']:.6f}")
    print(f"Mann-Whitney p-value: {stats_result['u_p']:.6f}")
    print(f"Cohen's d: {stats_result['cohens_d']:.4f}")
    print(f"95% CI for diff: [{stats_result['ci_95_low']:.4f}, {stats_result['ci_95_high']:.4f}]")
    print(f"\nU_ignore noise ratio: mean={noise_summary['mean']:.4f}, median={noise_summary['median']:.4f}")
    print(f"Percent with noise > 1.0: {noise_summary['pct_above_1']:.1f}%")

    poc_pass = (
        stats_result['u_line_mean'] > stats_result['u_ignore_mean'] and
        stats_result['t_p'] < config.stats.significance_threshold
    )
    full_pass = (
        poc_pass and
        noise_summary['mean'] > 1.0 and
        stats_result['cohens_d'] > config.stats.effect_size_medium
    )

    print("\n" + "=" * 60)
    print("GATE EVALUATION")
    print("=" * 60)
    print(f"PoC PASS criteria met: {poc_pass}")
    print(f"  - U_line mean > U_ignore mean: {stats_result['u_line_mean'] > stats_result['u_ignore_mean']}")
    print(f"  - p < 0.05: {stats_result['t_p'] < 0.05}")
    print(f"Full validation criteria met: {full_pass}")
    print(f"  - Noise ratio > 1.0: {noise_summary['mean'] > 1.0}")
    print(f"  - Cohen's d > 0.5: {stats_result['cohens_d'] > 0.5}")

    print("\nGenerating figures...")
    plot_concentration_boxplot(u_line_conc, u_ignore_conc, config.viz.boxplot_path)
    plot_noise_ratio_histogram(u_ignore_noise, config.viz.histogram_path)
    if results['u_line'] and results['u_ignore']:
        plot_gradient_heatmap(results['u_line'][0], results['u_ignore'][0], config.viz.heatmap_path)
    plot_concentration_vs_noise_scatter(results, config.viz.scatter_path)

    metrics = {
        "hypothesis_id": "h-m3",
        "n_samples_total": len(samples),
        "n_u_line": len(results['u_line']),
        "n_u_ignore": len(results['u_ignore']),
        "concentration_stats": stats_result,
        "noise_ratio_summary": noise_summary,
        "poc_pass": poc_pass,
        "full_validation_pass": full_pass,
        "gate_verdict": "PASS" if poc_pass else "FAIL",
    }

    metrics_path = os.path.join(config.output_dir, "metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"\nSaved metrics to: {metrics_path}")

    print("\n" + "=" * 60)
    print(f"FINAL VERDICT: {'PASS' if poc_pass else 'FAIL'}")
    print("=" * 60)

    return metrics


if __name__ == "__main__":
    main()
