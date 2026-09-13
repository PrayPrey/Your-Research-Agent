"""Evaluation functions for H-M1: WikiText-103 loading and visualization.

This module handles:
1. WikiText-103 dataset loading and tokenization
2. Evaluation sequence preparation
3. Context length computation
4. Results saving
5. Figure generation (PPL curve, gate metrics)
"""

import os
from typing import TYPE_CHECKING, Dict, List, Tuple

import numpy as np
import torch
import yaml
from torch import Tensor

if TYPE_CHECKING:
    from config import ExperimentConfig


def load_wikitext103(config: "ExperimentConfig"):
    """Load WikiText-103 validation split from HuggingFace.

    Args:
        config: Experiment configuration

    Returns:
        HuggingFace Dataset (validation split)
    """
    from datasets import load_dataset

    print(f"Loading {config.dataset_name}/{config.dataset_config}...")
    dataset = load_dataset(
        config.dataset_name,
        config.dataset_config,
        split="validation",
        trust_remote_code=True,
    )
    print(f"Loaded {len(dataset)} validation samples")
    return dataset


def prepare_eval_sequences(
    dataset,
    tokenizer,
    config: "ExperimentConfig",
) -> Tensor:
    """Tokenize and chunk dataset into evaluation sequences.

    Concatenates all tokens and creates non-overlapping chunks
    of max_seq_length tokens.

    Args:
        dataset: HuggingFace dataset with 'text' column
        tokenizer: Tokenizer for encoding
        config: Experiment configuration

    Returns:
        Tensor of shape [num_eval_sequences, max_seq_length]
    """
    print("Tokenizing and chunking sequences...")

    # Concatenate all text
    all_text = " ".join([item["text"] for item in dataset if item["text"].strip()])

    # Tokenize
    encoded = tokenizer(all_text, return_tensors="pt", truncation=False)
    all_input_ids = encoded["input_ids"].squeeze(0)  # [total_tokens]

    print(f"Total tokens: {len(all_input_ids)}")

    # Create non-overlapping chunks
    max_len = config.max_seq_length
    num_chunks = len(all_input_ids) // max_len

    chunks = []
    for i in range(min(num_chunks, config.num_eval_sequences)):
        start = i * max_len
        end = start + max_len
        chunks.append(all_input_ids[start:end])

    sequences = torch.stack(chunks)
    print(f"Created {sequences.size(0)} evaluation sequences of length {sequences.size(1)}")

    return sequences


def compute_context_lengths(
    h_spec: float,
    multipliers: Tuple[float, ...],
    min_tokens: int = 16,
) -> List[int]:
    """Compute context lengths as multiples of H_spec.

    Args:
        h_spec: Spectral memory horizon
        multipliers: Tuple of multipliers (e.g., 0.1, 0.25, 0.5, 1.0, 2.0, 4.0)
        min_tokens: Minimum context length

    Returns:
        List of integer context lengths
    """
    context_lengths = []
    for m in multipliers:
        ctx = max(min_tokens, int(h_spec * m))
        context_lengths.append(ctx)

    return context_lengths


def save_results(results: dict, path: str) -> None:
    """Write results dict to YAML file.

    Args:
        results: Results dictionary
        path: Output file path
    """
    with open(path, "w") as f:
        yaml.dump(results, f, default_flow_style=False, sort_keys=False)
    print(f"Results saved to {path}")


def generate_figures(
    ppl_curve: Dict[int, float],
    h_spec: float,
    degradation_ratio: float,
    per_layer_h_specs: List[float],
    output_dir: str,
) -> None:
    """Generate visualization figures.

    Figures generated:
    1. PPL vs context length curve (with vertical line at H_spec)
    2. Gate metrics bar chart (degradation ratio vs threshold 1.1)
    3. Per-layer H_spec distribution (optional)
    4. Decay rate profile (optional)

    Args:
        ppl_curve: Dict mapping context_length -> perplexity
        h_spec: Spectral memory horizon
        degradation_ratio: Computed degradation ratio
        per_layer_h_specs: H_spec for each layer
        output_dir: Directory to save figures
    """
    import matplotlib.pyplot as plt

    os.makedirs(output_dir, exist_ok=True)

    # Sort context lengths for plotting
    ctx_sorted = sorted(ppl_curve.keys())
    ppl_values = [ppl_curve[c] for c in ctx_sorted]

    # =========================================================================
    # Figure 1: PPL vs Context Length Curve
    # =========================================================================
    plt.figure(figsize=(10, 6))
    plt.plot(ctx_sorted, ppl_values, 'o-', color='steelblue', linewidth=2, markersize=8)
    plt.axvline(x=h_spec, color='red', linestyle='--', linewidth=2, label=f'H_spec = {h_spec:.1f}')

    plt.xlabel('Context Length (tokens)', fontsize=12)
    plt.ylabel('Perplexity', fontsize=12)
    plt.title('Perplexity vs Context Length (H-M1 Validation)', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)

    # Add annotation for degradation
    if degradation_ratio > 1.0:
        plt.text(
            0.02, 0.98,
            f'Degradation Ratio: {degradation_ratio:.3f}\n(Target: > 1.1)',
            transform=plt.gca().transAxes,
            verticalalignment='top',
            fontsize=10,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        )

    plt.tight_layout()
    plt.savefig(f'{output_dir}/ppl_vs_context_length.png', dpi=150)
    plt.close()
    print(f"  Saved: {output_dir}/ppl_vs_context_length.png")

    # =========================================================================
    # Figure 2: Gate Metrics Bar Chart
    # =========================================================================
    plt.figure(figsize=(8, 6))

    threshold = 1.1
    labels = ['Threshold', 'Measured Ratio']
    values = [threshold, degradation_ratio]
    colors = ['orange', 'green' if degradation_ratio > threshold else 'red']

    bars = plt.bar(labels, values, color=colors, edgecolor='black', linewidth=1.5)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f'{val:.3f}',
            ha='center', va='bottom', fontsize=12, fontweight='bold'
        )

    # Add gate result
    gate_pass = degradation_ratio > threshold
    result_text = "PASS" if gate_pass else "FAIL"
    result_color = "green" if gate_pass else "red"
    plt.text(
        0.5, 0.85,
        f'Gate Result: {result_text}',
        transform=plt.gca().transAxes,
        ha='center', fontsize=16, fontweight='bold', color=result_color
    )

    plt.ylabel('Degradation Ratio', fontsize=12)
    plt.title('MUST_WORK Gate: Perplexity Degradation Ratio', fontsize=14)
    plt.axhline(y=threshold, color='orange', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/gate_metrics_bar.png', dpi=150)
    plt.close()
    print(f"  Saved: {output_dir}/gate_metrics_bar.png")

    # =========================================================================
    # Figure 3: Per-Layer H_spec Distribution (Optional)
    # =========================================================================
    if per_layer_h_specs:
        plt.figure(figsize=(14, 6))

        layers = range(len(per_layer_h_specs))
        plt.bar(layers, per_layer_h_specs, color='steelblue', edgecolor='black', alpha=0.8)
        plt.axhline(y=h_spec, color='red', linestyle='--', linewidth=2, label=f'Global H_spec: {h_spec:.1f}')

        plt.xlabel('Layer Index', fontsize=12)
        plt.ylabel('H_spec (tokens)', fontsize=12)
        plt.title('H_spec per Mamba Layer (Slowest Decay Mode)', fontsize=14)
        plt.legend(fontsize=11)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/per_layer_eigenvalues.png', dpi=150)
        plt.close()
        print(f"  Saved: {output_dir}/per_layer_eigenvalues.png")

    # =========================================================================
    # Figure 4: Decay Rate Profile (Optional)
    # =========================================================================
    if per_layer_h_specs:
        plt.figure(figsize=(10, 6))

        # Decay rate = 1 / H_spec
        decay_rates = [1.0 / h if h > 0 else 0 for h in per_layer_h_specs]

        plt.plot(range(len(decay_rates)), decay_rates, 'o-', color='darkgreen', linewidth=2)
        plt.xlabel('Layer Index', fontsize=12)
        plt.ylabel('Decay Rate (1/H_spec)', fontsize=12)
        plt.title('Information Decay Rate Profile Across Layers', fontsize=14)
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/decay_rate_profile.png', dpi=150)
        plt.close()
        print(f"  Saved: {output_dir}/decay_rate_profile.png")
