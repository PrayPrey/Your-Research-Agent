import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def plot_wga_curve(wga_history, peak_epoch, save_path):
    plt.figure(figsize=(10, 6))
    epochs = range(len(wga_history))
    plt.plot(epochs, wga_history, 'b-', linewidth=2, label='WGA')
    plt.axvline(x=peak_epoch, color='r', linestyle='--', label=f'Crystallization (epoch {peak_epoch})')
    plt.xlabel('Epoch')
    plt.ylabel('Worst-Group Accuracy')
    plt.title('WGA Over Training')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

def plot_second_derivative(d2, peak_epoch, save_path):
    plt.figure(figsize=(10, 6))
    epochs = range(len(d2))
    plt.plot(epochs, d2, 'g-', linewidth=2, label='d²WGA/dt²')
    plt.axvline(x=peak_epoch, color='r', linestyle='--', label=f'Peak (epoch {peak_epoch})')
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.xlabel('Epoch')
    plt.ylabel('Second Derivative')
    plt.title('WGA Second Derivative')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

def plot_gradient_ratio_timeline(gradient_ratio_history, inflection_epoch, save_path):
    plt.figure(figsize=(10, 6))
    epochs = range(len(gradient_ratio_history))
    plt.plot(epochs, gradient_ratio_history, 'purple', linewidth=2, label='Gradient Ratio (minority/majority)')
    plt.axvline(x=inflection_epoch, color='r', linestyle='--', label=f'Inflection (epoch {inflection_epoch})')
    plt.xlabel('Epoch')
    plt.ylabel('Gradient Ratio')
    plt.title('Gradient Ratio Timeline')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

def plot_wga_gradient_overlay(wga_history, gradient_ratio_history, save_path):
    fig, ax1 = plt.subplots(figsize=(10, 6))
    epochs = range(len(wga_history))
    ax1.plot(epochs, wga_history, 'b-', linewidth=2, label='WGA')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('WGA', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax2 = ax1.twinx()
    epochs_grad = range(len(gradient_ratio_history))
    ax2.plot(epochs_grad, gradient_ratio_history, 'purple', linewidth=2, label='Gradient Ratio')
    ax2.set_ylabel('Gradient Ratio', color='purple')
    ax2.tick_params(axis='y', labelcolor='purple')
    fig.suptitle('WGA vs Gradient Ratio')
    fig.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

def plot_per_group_gradient_norms(group_norm_history, save_path):
    plt.figure(figsize=(10, 6))
    all_groups = set()
    for norms in group_norm_history:
        all_groups.update(norms.keys())
    for g in sorted(all_groups):
        values = [norms.get(g, 0) for norms in group_norm_history]
        plt.plot(range(len(values)), values, linewidth=2, label=f'Group {g}')
    plt.xlabel('Epoch')
    plt.ylabel('Gradient Norm')
    plt.title('Per-Group Gradient Norms')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

def plot_gate_metrics_comparison(correlation_result, save_path):
    fig, ax = plt.subplots(figsize=(8, 6))
    metrics = ['Inflection Epoch', 'WGA Peak Epoch']
    values = [correlation_result['inflection_epoch'], correlation_result['wga_peak_epoch']]
    bars = ax.bar(metrics, values, color=['purple', 'blue'], alpha=0.7)
    ax.set_ylabel('Epoch')
    ax.set_title(f"Gate Metrics Comparison\nr={correlation_result['r']:.3f}, p={correlation_result['p_value']:.4f}")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, str(val), ha='center')
    gate_text = "PASS" if correlation_result['gate_pass'] else "FAIL"
    ax.text(0.95, 0.95, f"Gate: {gate_text}", transform=ax.transAxes, ha='right', va='top',
            fontsize=14, fontweight='bold', color='green' if correlation_result['gate_pass'] else 'red')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
