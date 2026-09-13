"""Evaluation and visualization for H-M2: Eigenvalue Preservation.

Implements:
- Validation perplexity computation
- Results saving to YAML
- Figure generation (6 figures including mandatory gate metrics)
"""

import os
from typing import Dict, List

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import torch
import yaml
from torch import Tensor

from config import ExperimentConfig


def load_wikitext103_valid(config: ExperimentConfig, tokenizer):
    """Load and tokenize WikiText-103 validation split.

    Args:
        config: Experiment configuration
        tokenizer: Tokenizer for text encoding

    Returns:
        HuggingFace Dataset with 'input_ids' column
    """
    from datasets import load_dataset

    print("Loading WikiText-103 validation split...")
    dataset = load_dataset(
        config.dataset_name,
        config.dataset_config,
        split="validation"
    )

    # Filter empty texts
    dataset = dataset.filter(lambda x: len(x["text"].strip()) > 0)

    def tokenize_and_chunk(examples):
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

    # Limit for speed
    if len(tokenized_dataset) > config.num_eval_sequences:
        tokenized_dataset = tokenized_dataset.select(range(config.num_eval_sequences))

    print(f"Validation set: {len(tokenized_dataset)} sequences")
    return tokenized_dataset


def compute_perplexity(model, tokenizer, dataset, config: ExperimentConfig) -> float:
    """Compute validation perplexity on WikiText-103.

    Args:
        model: Model for evaluation
        tokenizer: Tokenizer
        dataset: Tokenized validation dataset
        config: Experiment configuration

    Returns:
        Perplexity value
    """
    import torch.nn.functional as F
    from torch.utils.data import DataLoader

    device = torch.device(config.device)
    model.eval()

    def collate_fn(batch):
        input_ids = torch.tensor([item["input_ids"] for item in batch], dtype=torch.long)
        return {"input_ids": input_ids}

    dataloader = DataLoader(dataset, batch_size=4, collate_fn=collate_fn)

    total_loss = 0.0
    total_tokens = 0

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            outputs = model(input_ids=input_ids, labels=input_ids)

            # Get per-token loss
            loss = outputs.loss
            num_tokens = input_ids.numel()

            total_loss += loss.item() * num_tokens
            total_tokens += num_tokens

    avg_loss = total_loss / total_tokens
    perplexity = np.exp(avg_loss)

    return perplexity


def save_results(results: Dict, path: str) -> None:
    """Save results dictionary to YAML file.

    Args:
        results: Results dictionary
        path: Output file path
    """
    # Convert numpy/torch types to Python types
    def convert(obj):
        if isinstance(obj, (np.floating, np.integer)):
            return float(obj) if isinstance(obj, np.floating) else int(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, torch.Tensor):
            return obj.cpu().tolist()
        elif isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(v) for v in obj]
        return obj

    results_converted = convert(results)

    with open(path, 'w') as f:
        yaml.dump(results_converted, f, default_flow_style=False, sort_keys=False)

    print(f"Results saved to {path}")


def generate_figures(
    baseline_a_logs: List[Tensor],
    post_a_logs: List[Tensor],
    preservation_metrics: Dict,
    train_losses: List[float],
    per_layer_baseline_h_spec: List[float],
    per_layer_post_h_spec: List[float],
    output_dir: str,
) -> List[str]:
    """Generate all visualization figures.

    Generates:
    1. Gate metrics bar chart (REQUIRED)
    2. Eigenvalue distribution overlay
    3. Per-layer H_spec change bar chart
    4. A_log diff heatmap
    5. Eigenvalue scatter pre vs post
    6. Training loss curve

    Args:
        baseline_a_logs: A_log tensors before training
        post_a_logs: A_log tensors after training
        preservation_metrics: Results from EigenvaluePreservationValidator
        train_losses: Per-step training losses
        per_layer_baseline_h_spec: H_spec per layer before training
        per_layer_post_h_spec: H_spec per layer after training
        output_dir: Directory to save figures

    Returns:
        List of generated figure paths
    """
    os.makedirs(output_dir, exist_ok=True)
    plt.style.use('seaborn-v0_8-whitegrid')
    figure_paths = []

    # =========================================================================
    # Figure 1: Gate Metrics Bar Chart (REQUIRED)
    # =========================================================================
    fig, ax = plt.subplots(figsize=(10, 6))

    metrics = ['|ΔH_spec| (%)', 'Eigenvalue Corr.']
    actual_values = [
        preservation_metrics['delta_h_spec_percent'],
        preservation_metrics['eigenvalue_correlation'],
    ]
    thresholds = [10.0, 0.95]  # Threshold for delta, minimum for correlation
    colors = ['steelblue', 'steelblue']

    x = np.arange(len(metrics))
    width = 0.35

    bars1 = ax.bar(x - width/2, actual_values, width, label='Actual', color=colors)
    bars2 = ax.bar(x + width/2, thresholds, width, label='Threshold', color='coral', alpha=0.7)

    ax.set_ylabel('Value')
    ax.set_title('H-M2 Gate Metrics: Eigenvalue Preservation')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()

    # Add pass/fail annotations
    for i, (actual, thresh) in enumerate(zip(actual_values, thresholds)):
        if i == 0:  # Delta - should be BELOW threshold
            passed = actual < thresh
        else:  # Correlation - should be ABOVE threshold
            passed = actual > thresh
        color = 'green' if passed else 'red'
        ax.annotate(
            'PASS' if passed else 'FAIL',
            xy=(i - width/2, actual),
            ha='center', va='bottom',
            fontweight='bold', color=color
        )

    gate_path = os.path.join(output_dir, 'gate_metrics.png')
    plt.tight_layout()
    plt.savefig(gate_path, dpi=150)
    plt.close()
    figure_paths.append(gate_path)
    print(f"  Generated: {gate_path}")

    # =========================================================================
    # Figure 2: Eigenvalue Distribution Overlay
    # =========================================================================
    fig, ax = plt.subplots(figsize=(10, 6))

    # Compute discrete eigenvalues
    baseline_eigenvalues = torch.cat([
        torch.exp(-torch.exp(a.float())).flatten()
        for a in baseline_a_logs
    ]).cpu().numpy()
    post_eigenvalues = torch.cat([
        torch.exp(-torch.exp(a.float())).flatten()
        for a in post_a_logs
    ]).cpu().numpy()

    ax.hist(baseline_eigenvalues, bins=100, alpha=0.5, label='Baseline', density=True)
    ax.hist(post_eigenvalues, bins=100, alpha=0.5, label='Post-Training', density=True)
    ax.set_xlabel('Discrete Eigenvalue λ')
    ax.set_ylabel('Density')
    ax.set_title('Eigenvalue Distribution: Pre vs Post LoRA Training')
    ax.legend()

    eigenvalue_dist_path = os.path.join(output_dir, 'eigenvalue_distribution.png')
    plt.tight_layout()
    plt.savefig(eigenvalue_dist_path, dpi=150)
    plt.close()
    figure_paths.append(eigenvalue_dist_path)
    print(f"  Generated: {eigenvalue_dist_path}")

    # =========================================================================
    # Figure 3: Per-Layer H_spec Change Bar Chart
    # =========================================================================
    fig, ax = plt.subplots(figsize=(14, 6))

    num_layers = len(per_layer_baseline_h_spec)
    x = np.arange(num_layers)

    # Compute percentage change per layer
    delta_h_spec_per_layer = [
        abs(post - base) / base * 100 if base > 0 else 0
        for base, post in zip(per_layer_baseline_h_spec, per_layer_post_h_spec)
    ]

    colors = ['green' if d < 10.0 else 'red' for d in delta_h_spec_per_layer]
    ax.bar(x, delta_h_spec_per_layer, color=colors, alpha=0.7)
    ax.axhline(y=10.0, color='red', linestyle='--', label='10% Threshold')
    ax.set_xlabel('Layer Index')
    ax.set_ylabel('|ΔH_spec| (%)')
    ax.set_title('Per-Layer H_spec Change After LoRA Training')
    ax.legend()

    per_layer_path = os.path.join(output_dir, 'per_layer_h_spec_change.png')
    plt.tight_layout()
    plt.savefig(per_layer_path, dpi=150)
    plt.close()
    figure_paths.append(per_layer_path)
    print(f"  Generated: {per_layer_path}")

    # =========================================================================
    # Figure 4: A_log Diff Heatmap (Sample Layers)
    # =========================================================================
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # Sample 6 layers evenly
    sample_indices = [0, 9, 19, 29, 39, 47]

    for idx, (ax, layer_idx) in enumerate(zip(axes.flat, sample_indices)):
        if layer_idx < len(baseline_a_logs):
            diff = torch.abs(
                post_a_logs[layer_idx].float() - baseline_a_logs[layer_idx].float()
            ).cpu().numpy()

            im = ax.imshow(diff, aspect='auto', cmap='hot')
            ax.set_title(f'Layer {layer_idx} |A_log diff|')
            ax.set_xlabel('d_state')
            ax.set_ylabel('d_inner')
            plt.colorbar(im, ax=ax)

    plt.suptitle('A_log Parameter Difference (Should be ~0)', fontsize=14)
    heatmap_path = os.path.join(output_dir, 'a_log_diff_heatmap.png')
    plt.tight_layout()
    plt.savefig(heatmap_path, dpi=150)
    plt.close()
    figure_paths.append(heatmap_path)
    print(f"  Generated: {heatmap_path}")

    # =========================================================================
    # Figure 5: Eigenvalue Scatter Pre vs Post
    # =========================================================================
    fig, ax = plt.subplots(figsize=(8, 8))

    # Subsample for visualization
    n_samples = min(10000, len(baseline_eigenvalues))
    indices = np.random.choice(len(baseline_eigenvalues), n_samples, replace=False)

    ax.scatter(
        baseline_eigenvalues[indices],
        post_eigenvalues[indices],
        alpha=0.1, s=1
    )

    # Identity line
    min_val = min(baseline_eigenvalues.min(), post_eigenvalues.min())
    max_val = max(baseline_eigenvalues.max(), post_eigenvalues.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', label='y=x (perfect preservation)')

    ax.set_xlabel('Baseline Eigenvalues')
    ax.set_ylabel('Post-Training Eigenvalues')
    ax.set_title(f'Eigenvalue Scatter (r={preservation_metrics["eigenvalue_correlation"]:.4f})')
    ax.legend()

    scatter_path = os.path.join(output_dir, 'eigenvalue_scatter.png')
    plt.tight_layout()
    plt.savefig(scatter_path, dpi=150)
    plt.close()
    figure_paths.append(scatter_path)
    print(f"  Generated: {scatter_path}")

    # =========================================================================
    # Figure 6: Training Loss Curve
    # =========================================================================
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(train_losses, alpha=0.3, label='Step Loss')

    # Moving average
    window = min(50, len(train_losses) // 10) if len(train_losses) > 10 else 1
    if window > 1:
        smoothed = np.convolve(train_losses, np.ones(window)/window, mode='valid')
        ax.plot(range(window-1, len(train_losses)), smoothed, label=f'Smoothed (window={window})')

    ax.set_xlabel('Training Step')
    ax.set_ylabel('Loss')
    ax.set_title('LoRA Fine-tuning Loss Curve')
    ax.legend()

    loss_path = os.path.join(output_dir, 'training_loss.png')
    plt.tight_layout()
    plt.savefig(loss_path, dpi=150)
    plt.close()
    figure_paths.append(loss_path)
    print(f"  Generated: {loss_path}")

    return figure_paths
