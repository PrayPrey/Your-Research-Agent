"""
Visualization utilities for spurious correlation experiments.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import json


def plot_training_curves(all_results, output_dir, dataset_name):
    """Plot training and validation loss curves for all methods."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    methods = list(all_results.keys())
    colors = plt.cm.tab10(np.linspace(0, 1, len(methods)))

    for i, (method, results) in enumerate(all_results.items()):
        epochs = range(1, len(results['train_losses']) + 1)
        c = colors[i]

        axes[0].plot(epochs, results['train_losses'], label=method, color=c, linewidth=2)
        axes[1].plot(epochs, results['val_losses'], label=method, color=c, linewidth=2,
                     linestyle='--')

    axes[0].set_title(f'Training Loss - {dataset_name}', fontsize=13)
    axes[0].set_xlabel('Epoch', fontsize=11)
    axes[0].set_ylabel('Loss', fontsize=11)
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3)

    axes[1].set_title(f'Validation Loss - {dataset_name}', fontsize=13)
    axes[1].set_xlabel('Epoch', fontsize=11)
    axes[1].set_ylabel('Loss', fontsize=11)
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, f'training_curves_{dataset_name}.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")
    return path


def plot_accuracy_curves(all_results, output_dir, dataset_name):
    """Plot overall and worst-group accuracy over epochs."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    methods = list(all_results.keys())
    colors = plt.cm.tab10(np.linspace(0, 1, len(methods)))

    for i, (method, results) in enumerate(all_results.items()):
        c = colors[i]
        epochs = range(1, len(results['val_overall_accs']) + 1)

        axes[0].plot(epochs, results['val_overall_accs'], label=method,
                     color=c, linewidth=2, marker='o', markersize=4)
        axes[1].plot(epochs, results['val_wga'], label=method,
                     color=c, linewidth=2, marker='s', markersize=4)

    axes[0].set_title(f'Overall Accuracy - {dataset_name}', fontsize=13)
    axes[0].set_xlabel('Epoch', fontsize=11)
    axes[0].set_ylabel('Accuracy', fontsize=11)
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim([0, 1])

    axes[1].set_title(f'Worst-Group Accuracy - {dataset_name}', fontsize=13)
    axes[1].set_xlabel('Epoch', fontsize=11)
    axes[1].set_ylabel('Worst-Group Accuracy', fontsize=11)
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim([0, 1])

    plt.tight_layout()
    path = os.path.join(output_dir, f'accuracy_curves_{dataset_name}.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")
    return path


def plot_method_comparison(all_results, output_dir, dataset_name):
    """Bar chart comparing final performance metrics across methods."""
    methods = list(all_results.keys())
    overall_accs = [r['final_test_overall_acc'] for r in all_results.values()]
    wgas = [r['final_test_wga'] for r in all_results.values()]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    x = np.arange(len(methods))
    width = 0.6

    colors = plt.cm.tab10(np.linspace(0, 1, len(methods)))

    bars1 = axes[0].bar(x, overall_accs, width, color=colors, edgecolor='black', linewidth=0.8)
    axes[0].set_title(f'Overall Test Accuracy - {dataset_name}', fontsize=13)
    axes[0].set_xlabel('Method', fontsize=11)
    axes[0].set_ylabel('Accuracy', fontsize=11)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(methods, rotation=15, ha='right', fontsize=10)
    axes[0].set_ylim([0, 1])
    axes[0].grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars1, overall_accs):
        axes[0].text(bar.get_x() + bar.get_width()/2, val + 0.01,
                     f'{val:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    bars2 = axes[1].bar(x, wgas, width, color=colors, edgecolor='black', linewidth=0.8)
    axes[1].set_title(f'Worst-Group Test Accuracy - {dataset_name}', fontsize=13)
    axes[1].set_xlabel('Method', fontsize=11)
    axes[1].set_ylabel('Worst-Group Accuracy', fontsize=11)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(methods, rotation=15, ha='right', fontsize=10)
    axes[1].set_ylim([0, 1])
    axes[1].grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars2, wgas):
        axes[1].text(bar.get_x() + bar.get_width()/2, val + 0.01,
                     f'{val:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    path = os.path.join(output_dir, f'method_comparison_{dataset_name}.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")
    return path


def plot_spurious_dominance(cagr_results, output_dir, dataset_name):
    """Plot CAGR-specific metrics: spurious dominance ratio rho over time."""
    if 'rho_history' not in cagr_results or not cagr_results['rho_history']:
        return None

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    rho = cagr_results['rho_history']
    epochs = range(1, len(rho) + 1)

    axes[0].plot(epochs, rho, 'b-o', linewidth=2, markersize=5, label='Spurious Dominance Ratio (rho)')
    axes[0].axhline(y=0.5, color='r', linestyle='--', alpha=0.7, label='Equal balance (rho=0.5)')
    axes[0].set_title(f'Spurious Dominance Ratio (rho) - {dataset_name}', fontsize=13)
    axes[0].set_xlabel('Epoch', fontsize=11)
    axes[0].set_ylabel('rho', fontsize=11)
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim([0, 1])

    # Alpha history
    if 'alpha_history' in cagr_results and cagr_results['alpha_history']:
        alpha = cagr_results['alpha_history']
        steps = np.linspace(1, len(rho), len(alpha))
        axes[1].plot(steps, alpha, 'g-s', linewidth=2, markersize=5, label='Penalty Factor (alpha)')
        axes[1].set_title(f'Curvature-Adaptive Penalty (alpha) - {dataset_name}', fontsize=13)
        axes[1].set_xlabel('Hessian Update Step', fontsize=11)
        axes[1].set_ylabel('alpha', fontsize=11)
        axes[1].legend(fontsize=9)
        axes[1].grid(True, alpha=0.3)
        axes[1].set_ylim([0, 1])
    else:
        axes[1].text(0.5, 0.5, 'No alpha history available',
                     ha='center', va='center', transform=axes[1].transAxes)

    plt.tight_layout()
    path = os.path.join(output_dir, f'cagr_metrics_{dataset_name}.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")
    return path


def plot_per_group_accuracy(all_results, output_dir, dataset_name, n_groups=4):
    """Bar chart of per-group test accuracy for all methods."""
    methods = list(all_results.keys())
    n_methods = len(methods)

    fig, ax = plt.subplots(figsize=(14, 6))

    x = np.arange(n_groups)
    width = 0.8 / n_methods
    colors = plt.cm.tab10(np.linspace(0, 1, n_methods))

    group_labels = [f'Group {g}\n(label={g//2}, spurious={g%2})' for g in range(n_groups)]

    for i, (method, results) in enumerate(all_results.items()):
        per_group = results.get('final_test_per_group_acc', {})
        accs = [per_group.get(g, 0.0) for g in range(n_groups)]
        offset = (i - n_methods/2 + 0.5) * width
        bars = ax.bar(x + offset, accs, width, label=method, color=colors[i],
                      edgecolor='black', linewidth=0.5)

    ax.set_title(f'Per-Group Test Accuracy - {dataset_name}', fontsize=13)
    ax.set_xlabel('Group', fontsize=11)
    ax.set_ylabel('Accuracy', fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(group_labels, fontsize=9)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim([0, 1])

    plt.tight_layout()
    path = os.path.join(output_dir, f'per_group_accuracy_{dataset_name}.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")
    return path


def plot_curvature_analysis(curvature_results, output_dir, dataset_name):
    """Plot lambda_c vs lambda_s over training (Hessian analysis)."""
    if not curvature_results:
        return None

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    epochs = range(1, len(curvature_results['lambda_c']) + 1)

    axes[0].plot(epochs, curvature_results['lambda_c'], 'b-o', linewidth=2,
                 markersize=5, label='Causal curvature (lambda_c)')
    axes[0].plot(epochs, curvature_results['lambda_s'], 'r-s', linewidth=2,
                 markersize=5, label='Spurious curvature (lambda_s)')
    axes[0].set_title(f'Hessian Eigenvalue Estimates - {dataset_name}', fontsize=13)
    axes[0].set_xlabel('Epoch', fontsize=11)
    axes[0].set_ylabel('Curvature (eigenvalue)', fontsize=11)
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_yscale('log')

    # Ratio lambda_c / lambda_s
    ratios = [c/max(s, 1e-8) for c, s in zip(curvature_results['lambda_c'],
                                               curvature_results['lambda_s'])]
    axes[1].plot(epochs, ratios, 'g-^', linewidth=2, markersize=5,
                 label='lambda_c / lambda_s')
    axes[1].axhline(y=1.0, color='gray', linestyle='--', alpha=0.7, label='Equal curvature')
    axes[1].set_title(f'Curvature Ratio (lambda_c/lambda_s) - {dataset_name}', fontsize=13)
    axes[1].set_xlabel('Epoch', fontsize=11)
    axes[1].set_ylabel('Curvature Ratio', fontsize=11)
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, f'curvature_analysis_{dataset_name}.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")
    return path


def plot_overall_comparison(dataset_results, output_dir):
    """Summary plot across all datasets."""
    datasets = list(dataset_results.keys())
    if not datasets:
        return None

    # Collect all methods
    all_methods = set()
    for ds_res in dataset_results.values():
        all_methods.update(ds_res.keys())
    all_methods = sorted(all_methods)

    n_datasets = len(datasets)
    fig, axes = plt.subplots(1, n_datasets, figsize=(7 * n_datasets, 6), squeeze=False)

    colors = plt.cm.tab10(np.linspace(0, 1, len(all_methods)))
    method_colors = {m: colors[i] for i, m in enumerate(all_methods)}

    for j, ds in enumerate(datasets):
        ax = axes[0][j]
        methods_in_ds = list(dataset_results[ds].keys())
        wgas = [dataset_results[ds][m]['final_test_wga'] for m in methods_in_ds]

        x = np.arange(len(methods_in_ds))
        bars = ax.bar(x, wgas, 0.6,
                      color=[method_colors[m] for m in methods_in_ds],
                      edgecolor='black', linewidth=0.8)

        ax.set_title(f'Worst-Group Accuracy\n{ds}', fontsize=12)
        ax.set_xlabel('Method', fontsize=10)
        ax.set_ylabel('WGA', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(methods_in_ds, rotation=20, ha='right', fontsize=9)
        ax.set_ylim([0, 1])
        ax.grid(True, alpha=0.3, axis='y')

        for bar, val in zip(bars, wgas):
            ax.text(bar.get_x() + bar.get_width()/2, val + 0.01,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    plt.tight_layout()
    path = os.path.join(output_dir, 'overall_comparison.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")
    return path
