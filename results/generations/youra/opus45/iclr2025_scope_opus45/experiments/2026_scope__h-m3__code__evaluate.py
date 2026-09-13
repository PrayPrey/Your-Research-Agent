"""Evaluation and visualization for H-M3: Eigenmode Energy Redistribution.

Implements:
- WikiText-103 validation set loading
- Perplexity computation
- Energy distribution visualization
- Gate metrics visualization
"""

import os
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import torch
import yaml
from torch import Tensor
from tqdm import tqdm

from config import ExperimentConfig


def load_wikitext103_eval(config: ExperimentConfig, tokenizer):
    """Load and tokenize WikiText-103 validation split.

    Args:
        config: Experiment configuration
        tokenizer: Tokenizer for text encoding

    Returns:
        HuggingFace Dataset with 'input_ids' column
    """
    from datasets import load_dataset

    print(f"Loading WikiText-103 validation split...")
    dataset = load_dataset(
        config.dataset_name,
        config.dataset_config,
        split="validation"
    )

    # Filter empty texts
    dataset = dataset.filter(lambda x: len(x["text"].strip()) > 0)

    print(f"Tokenizing {len(dataset)} validation examples...")

    def tokenize_and_chunk(examples):
        """Tokenize text and create fixed-length chunks."""
        tokenized = tokenizer(
            examples["text"],
            truncation=False,
            padding=False,
            return_attention_mask=False,
        )

        all_input_ids = []
        for ids in tokenized["input_ids"]:
            all_input_ids.extend(ids)

        chunks = []
        for i in range(0, len(all_input_ids) - config.max_seq_length, config.max_seq_length):
            chunks.append(all_input_ids[i:i + config.max_seq_length])

        return {"input_ids": chunks}

    tokenized_dataset = dataset.map(
        tokenize_and_chunk,
        batched=True,
        batch_size=1000,
        remove_columns=dataset.column_names,
        desc="Tokenizing validation",
    )

    print(f"Created {len(tokenized_dataset)} validation sequences")

    # Subsample if needed
    if config.num_eval_sequences and len(tokenized_dataset) > config.num_eval_sequences:
        tokenized_dataset = tokenized_dataset.select(range(config.num_eval_sequences))
        print(f"Subsampled to {len(tokenized_dataset)} sequences for evaluation")

    return tokenized_dataset


def compute_perplexity(model, eval_dataset, config: ExperimentConfig) -> float:
    """Compute cross-entropy perplexity on evaluation set.

    Args:
        model: Model for evaluation
        eval_dataset: Dataset with 'input_ids' column
        config: Experiment configuration

    Returns:
        Perplexity as float
    """
    device = next(model.parameters()).device
    model.eval()

    total_loss = 0.0
    total_tokens = 0

    # Use subset for speed
    num_samples = min(100, len(eval_dataset))

    print(f"Computing perplexity on {num_samples} samples...")

    with torch.no_grad():
        for i in tqdm(range(num_samples), desc="Computing perplexity"):
            input_ids = torch.tensor(
                eval_dataset[i]["input_ids"],
                dtype=torch.long,
                device=device
            ).unsqueeze(0)

            outputs = model(input_ids=input_ids, labels=input_ids)
            loss = outputs.loss

            seq_len = input_ids.shape[1]
            total_loss += loss.item() * seq_len
            total_tokens += seq_len

    avg_loss = total_loss / total_tokens
    perplexity = np.exp(avg_loss)

    print(f"Perplexity: {perplexity:.2f}")
    return perplexity


def plot_gate_metrics(delta_e_nats: float, threshold: float, figures_dir: str) -> None:
    """Bar chart: ΔE actual vs 0.1 nats threshold with PASS/FAIL annotation.

    Args:
        delta_e_nats: Measured energy shift in nats
        threshold: Gate threshold (0.1 nats)
        figures_dir: Directory to save figure
    """
    os.makedirs(figures_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))

    # Bar data
    categories = ['Measured ΔE', 'Threshold']
    values = [delta_e_nats, threshold]
    colors = ['#2ecc71' if delta_e_nats > threshold else '#e74c3c', '#3498db']

    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1.5)

    # Add value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(f'{val:.4f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Gate result annotation
    gate_result = "PASS" if delta_e_nats > threshold else "FAIL"
    gate_color = '#2ecc71' if delta_e_nats > threshold else '#e74c3c'

    ax.axhline(y=threshold, color='#e74c3c', linestyle='--', linewidth=2, label='Gate Threshold')

    ax.set_ylabel('Energy Shift (nats)', fontsize=12)
    ax.set_title(f'H-M3 Gate Evaluation: {gate_result}', fontsize=14, fontweight='bold',
                 color=gate_color)

    # Add gate box
    props = dict(boxstyle='round', facecolor=gate_color, alpha=0.3)
    ax.text(0.95, 0.95, f'Gate: {gate_result}',
            transform=ax.transAxes, fontsize=14, fontweight='bold',
            verticalalignment='top', horizontalalignment='right', bbox=props)

    ax.set_ylim(0, max(delta_e_nats, threshold) * 1.3)
    ax.legend(loc='upper left')

    plt.tight_layout()
    filepath = os.path.join(figures_dir, 'gate_metrics.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filepath}")


def plot_energy_distribution(pre_energy: dict, post_energy: dict, figures_dir: str) -> None:
    """Histogram: per-layer slow mode fraction pre vs post.

    Args:
        pre_energy: Pre-training energy dict
        post_energy: Post-training energy dict
        figures_dir: Directory to save figure
    """
    os.makedirs(figures_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    pre_fracs = pre_energy['per_layer']
    post_fracs = post_energy['per_layer']

    bins = np.linspace(0, 1, 21)

    ax.hist(pre_fracs, bins=bins, alpha=0.6, label='Pre-training', color='#3498db', edgecolor='black')
    ax.hist(post_fracs, bins=bins, alpha=0.6, label='Post-training', color='#e74c3c', edgecolor='black')

    ax.axvline(x=np.mean(pre_fracs), color='#3498db', linestyle='--', linewidth=2,
               label=f'Pre mean: {np.mean(pre_fracs):.4f}')
    ax.axvline(x=np.mean(post_fracs), color='#e74c3c', linestyle='--', linewidth=2,
               label=f'Post mean: {np.mean(post_fracs):.4f}')

    ax.set_xlabel('Slow Mode Fraction', fontsize=12)
    ax.set_ylabel('Number of Layers', fontsize=12)
    ax.set_title('Energy Distribution: Pre vs Post Training', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')

    plt.tight_layout()
    filepath = os.path.join(figures_dir, 'energy_distribution.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filepath}")


def plot_per_layer_slow_fraction(pre_energy: dict, post_energy: dict, figures_dir: str) -> None:
    """Bar chart: slow_fraction for each of 48 layers, pre vs post.

    Args:
        pre_energy: Pre-training energy dict
        post_energy: Post-training energy dict
        figures_dir: Directory to save figure
    """
    os.makedirs(figures_dir, exist_ok=True)

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    pre_fracs = pre_energy['per_layer']
    post_fracs = post_energy['per_layer']
    num_layers = len(pre_fracs)
    x = np.arange(num_layers)

    # Top: Pre vs Post comparison
    width = 0.35
    axes[0].bar(x - width/2, pre_fracs, width, label='Pre-training', color='#3498db', alpha=0.8)
    axes[0].bar(x + width/2, post_fracs, width, label='Post-training', color='#e74c3c', alpha=0.8)

    axes[0].set_xlabel('Layer Index', fontsize=12)
    axes[0].set_ylabel('Slow Mode Fraction', fontsize=12)
    axes[0].set_title('Per-Layer Slow Mode Fraction', fontsize=14, fontweight='bold')
    axes[0].legend(loc='upper right')
    axes[0].set_xticks(x[::4])

    # Bottom: Delta per layer
    delta = [post_fracs[i] - pre_fracs[i] for i in range(num_layers)]
    colors = ['#2ecc71' if d > 0 else '#e74c3c' for d in delta]

    axes[1].bar(x, delta, color=colors, alpha=0.8)
    axes[1].axhline(y=0, color='black', linestyle='-', linewidth=1)

    axes[1].set_xlabel('Layer Index', fontsize=12)
    axes[1].set_ylabel('Δ Slow Mode Fraction', fontsize=12)
    axes[1].set_title('Per-Layer Energy Shift (Post - Pre)', fontsize=14, fontweight='bold')
    axes[1].set_xticks(x[::4])

    plt.tight_layout()
    filepath = os.path.join(figures_dir, 'per_layer_slow_fraction.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filepath}")


def plot_eigenvalue_energy_scatter(
    eigenvalues: List[Tensor],
    pre_energy: dict,
    post_energy: dict,
    figures_dir: str,
) -> None:
    """Scatter: eigenvalue magnitude vs energy contribution, colored slow/fast.

    Args:
        eigenvalues: List of eigenvalue tensors per layer
        pre_energy: Pre-training energy dict
        post_energy: Post-training energy dict
        figures_dir: Directory to save figure
    """
    os.makedirs(figures_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Aggregate eigenvalues
    all_eigenvalues = []
    layer_indices = []

    for layer_idx, eig in enumerate(eigenvalues):
        # Get mean eigenvalue per layer
        mean_eig = eig.abs().mean().item()
        all_eigenvalues.append(mean_eig)
        layer_indices.append(layer_idx)

    # Plot pre vs post energy vs eigenvalue
    pre_fracs = pre_energy['per_layer']
    post_fracs = post_energy['per_layer']

    # Scatter plot
    scatter_pre = ax.scatter(all_eigenvalues, pre_fracs, c='#3498db', alpha=0.6,
                              s=50, label='Pre-training', marker='o')
    scatter_post = ax.scatter(all_eigenvalues, post_fracs, c='#e74c3c', alpha=0.6,
                               s=50, label='Post-training', marker='^')

    # Add slow mode threshold line
    ax.axvline(x=0.99, color='green', linestyle='--', linewidth=2, label='Slow mode threshold (0.99)')

    ax.set_xlabel('Mean |λ| (Eigenvalue Magnitude)', fontsize=12)
    ax.set_ylabel('Slow Mode Fraction', fontsize=12)
    ax.set_title('Eigenvalue vs Energy Distribution per Layer', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')

    plt.tight_layout()
    filepath = os.path.join(figures_dir, 'eigenvalue_energy_scatter.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filepath}")


def plot_training_loss(losses: List[float], figures_dir: str) -> None:
    """Line chart of training loss over steps.

    Args:
        losses: List of loss values per step
        figures_dir: Directory to save figure
    """
    os.makedirs(figures_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    steps = range(1, len(losses) + 1)
    ax.plot(steps, losses, color='#3498db', linewidth=1.5, alpha=0.8)

    # Smoothed line (moving average)
    window_size = min(20, len(losses) // 5) if len(losses) > 20 else 1
    if window_size > 1:
        smoothed = np.convolve(losses, np.ones(window_size)/window_size, mode='valid')
        ax.plot(range(window_size, len(losses) + 1), smoothed, color='#e74c3c',
                linewidth=2, label=f'Smoothed (window={window_size})')

    ax.set_xlabel('Training Step', fontsize=12)
    ax.set_ylabel('Loss', fontsize=12)
    ax.set_title('Training Loss Curve', fontsize=14, fontweight='bold')
    if window_size > 1:
        ax.legend(loc='upper right')

    plt.tight_layout()
    filepath = os.path.join(figures_dir, 'training_loss.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filepath}")


def save_results(results: dict, path: str) -> None:
    """Save results dictionary to YAML file.

    Args:
        results: Results dictionary
        path: Output file path
    """
    # Convert numpy types to Python types
    def convert_types(obj):
        if isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_types(v) for v in obj]
        return obj

    results = convert_types(results)

    with open(path, 'w') as f:
        yaml.dump(results, f, default_flow_style=False, sort_keys=False)

    print(f"Results saved to: {path}")
