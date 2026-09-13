"""
Visualization utilities for experiment results
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os


def plot_training_curves(history, save_path):
    """Plot training and validation curves"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Loss curves
    ax = axes[0, 0]
    for method in history:
        if 'train_loss' in history[method]:
            epochs = range(1, len(history[method]['train_loss']) + 1)
            ax.plot(epochs, history[method]['train_loss'],
                   label=f'{method}', marker='o', markersize=3)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Training Loss')
    ax.set_title('Training Loss')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Worst group accuracy
    ax = axes[0, 1]
    for method in history:
        if 'val_worst_acc' in history[method]:
            epochs = range(1, len(history[method]['val_worst_acc']) + 1)
            ax.plot(epochs, history[method]['val_worst_acc'],
                   label=f'{method}', marker='o', markersize=3)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Worst Group Accuracy')
    ax.set_title('Worst Group Accuracy')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Average accuracy
    ax = axes[1, 0]
    for method in history:
        if 'val_avg_acc' in history[method]:
            epochs = range(1, len(history[method]['val_avg_acc']) + 1)
            ax.plot(epochs, history[method]['val_avg_acc'],
                   label=f'{method}', marker='o', markersize=3)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Average Accuracy')
    ax.set_title('Average Accuracy')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Average margin
    ax = axes[1, 1]
    for method in history:
        if 'val_margin' in history[method]:
            epochs = range(1, len(history[method]['val_margin']) + 1)
            ax.plot(epochs, history[method]['val_margin'],
                   label=f'{method}', marker='o', markersize=3)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Average Margin')
    ax.set_title('Average Margin')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved training curves to {save_path}")


def plot_group_performance(results, save_path):
    """Plot group-wise performance comparison"""
    methods = list(results.keys())
    n_groups = 4

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Group accuracies
    ax = axes[0]
    width = 0.2
    x = np.arange(n_groups)

    for i, method in enumerate(methods):
        group_accs = []
        for g in range(n_groups):
            key = f'group_{g}_accuracy'
            if key in results[method]:
                group_accs.append(results[method][key])
            else:
                group_accs.append(0)

        ax.bar(x + i * width, group_accs, width, label=method)

    ax.set_xlabel('Group')
    ax.set_ylabel('Accuracy')
    ax.set_title('Group-wise Accuracy')
    ax.set_xticks(x + width * (len(methods) - 1) / 2)
    ax.set_xticklabels([f'Group {g}' for g in range(n_groups)])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # Summary metrics
    ax = axes[1]
    metrics = ['overall_accuracy', 'worst_group_accuracy']
    x = np.arange(len(metrics))
    width = 0.2

    for i, method in enumerate(methods):
        values = [results[method].get(m, 0) for m in metrics]
        ax.bar(x + i * width, values, width, label=method)

    ax.set_ylabel('Accuracy')
    ax.set_title('Overall Performance Comparison')
    ax.set_xticks(x + width * (len(methods) - 1) / 2)
    ax.set_xticklabels(['Average Acc', 'Worst Group Acc'])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved group performance to {save_path}")


def plot_method_comparison(results, save_path):
    """Plot comparison of different methods"""
    methods = list(results.keys())

    # Extract metrics
    avg_accs = [results[m]['overall_accuracy'] for m in methods]
    worst_accs = [results[m]['worst_group_accuracy'] for m in methods]
    margins = [results[m].get('avg_margin', 0) for m in methods]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Average accuracy
    ax = axes[0]
    ax.bar(methods, avg_accs, color='steelblue')
    ax.set_ylabel('Accuracy')
    ax.set_title('Average Accuracy')
    ax.set_ylim([0, 1])
    ax.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(avg_accs):
        ax.text(i, v + 0.02, f'{v:.3f}', ha='center', va='bottom')

    # Worst group accuracy
    ax = axes[1]
    ax.bar(methods, worst_accs, color='coral')
    ax.set_ylabel('Accuracy')
    ax.set_title('Worst Group Accuracy')
    ax.set_ylim([0, 1])
    ax.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(worst_accs):
        ax.text(i, v + 0.02, f'{v:.3f}', ha='center', va='bottom')

    # Average margin
    ax = axes[2]
    ax.bar(methods, margins, color='seagreen')
    ax.set_ylabel('Margin')
    ax.set_title('Average Margin')
    ax.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(margins):
        ax.text(i, v + 0.02, f'{v:.2f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved method comparison to {save_path}")


def plot_robustness_tradeoff(results, save_path):
    """Plot robustness vs accuracy tradeoff"""
    methods = list(results.keys())

    avg_accs = [results[m]['overall_accuracy'] for m in methods]
    worst_accs = [results[m]['worst_group_accuracy'] for m in methods]

    fig, ax = plt.subplots(figsize=(8, 6))

    colors = ['blue', 'orange', 'green', 'red', 'purple']
    for i, method in enumerate(methods):
        ax.scatter(avg_accs[i], worst_accs[i],
                  s=150, c=colors[i % len(colors)],
                  alpha=0.7, label=method, edgecolors='black')
        ax.annotate(method, (avg_accs[i], worst_accs[i]),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=9)

    # Add diagonal line (ideal case)
    min_val = min(min(avg_accs), min(worst_accs))
    max_val = max(max(avg_accs), max(worst_accs))
    ax.plot([min_val, max_val], [min_val, max_val],
           'k--', alpha=0.3, label='Ideal (Avg=Worst)')

    ax.set_xlabel('Average Accuracy')
    ax.set_ylabel('Worst Group Accuracy')
    ax.set_title('Robustness-Accuracy Tradeoff')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved robustness tradeoff to {save_path}")


def save_results_table(results, save_path):
    """Save results as a table"""
    data = []

    for method in results:
        row = {
            'Method': method,
            'Average Acc': f"{results[method]['overall_accuracy']:.4f}",
            'Worst Group Acc': f"{results[method]['worst_group_accuracy']:.4f}",
            'Avg Margin': f"{results[method].get('avg_margin', 0):.4f}"
        }

        # Add group-wise accuracies
        for g in range(4):
            key = f'group_{g}_accuracy'
            if key in results[method]:
                row[f'Group {g} Acc'] = f"{results[method][key]:.4f}"

        data.append(row)

    df = pd.DataFrame(data)
    df.to_csv(save_path, index=False)
    print(f"Saved results table to {save_path}")

    return df
