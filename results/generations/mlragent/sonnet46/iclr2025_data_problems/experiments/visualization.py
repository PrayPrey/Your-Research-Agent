"""Visualization utilities for DynaMix experiment results."""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.gridspec import GridSpec

from config import DOMAINS


def moving_average(data, window=10):
    """Compute moving average for smoothing."""
    if len(data) < window:
        return data
    return np.convolve(data, np.ones(window) / window, mode='valid')


def plot_training_curves(results_dict, output_dir, window=20):
    """Plot training loss curves for all methods."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Training and Evaluation Loss Curves", fontsize=14, fontweight='bold')

    colors = {'DynaMix': '#e74c3c', 'Static Uniform': '#3498db',
              'Static Tuned': '#2ecc71', 'DoReMi-style': '#9b59b6',
              'PiKE-style': '#f39c12'}
    linestyles = {'DynaMix': '-', 'Static Uniform': '--',
                  'Static Tuned': '-.', 'DoReMi-style': ':', 'PiKE-style': (0, (3, 1, 1, 1))}

    ax1, ax2 = axes

    for method, metrics in results_dict.items():
        color = colors.get(method, 'gray')
        ls = linestyles.get(method, '-')
        train_losses = metrics.get('train_losses', [])

        if train_losses:
            # Smooth training loss
            smoothed = moving_average(train_losses, window=window)
            x = np.linspace(0, len(train_losses), len(smoothed))
            ax1.plot(x, smoothed, label=method, color=color, linestyle=ls, linewidth=2)

    ax1.set_xlabel("Training Steps", fontsize=12)
    ax1.set_ylabel("Training Loss (Cross-Entropy)", fontsize=12)
    ax1.set_title("Training Loss", fontsize=12)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Eval loss
    for method, metrics in results_dict.items():
        color = colors.get(method, 'gray')
        ls = linestyles.get(method, '-')
        eval_steps = metrics.get('eval_steps', [])
        domain_eval = metrics.get('domain_eval_losses', [])

        if eval_steps and domain_eval:
            ax2.plot(eval_steps, domain_eval, label=method, color=color,
                    linestyle=ls, linewidth=2, marker='o', markersize=4)

    ax2.set_xlabel("Training Steps", fontsize=12)
    ax2.set_ylabel("Evaluation Loss (Cross-Entropy)", fontsize=12)
    ax2.set_title("Evaluation Loss (Average Across Domains)", fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, "training_curves.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def plot_domain_perplexity(results_dict, output_dir):
    """Plot per-domain perplexity comparison."""
    methods = list(results_dict.keys())
    n_domains = len(DOMAINS)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Per-Domain Perplexity Comparison", fontsize=14, fontweight='bold')

    colors = plt.cm.Set2(np.linspace(0, 1, len(methods)))
    x = np.arange(n_domains)
    width = 0.8 / len(methods)

    ax_ppl = axes[0]
    ax_loss = axes[1]

    for i, method in enumerate(methods):
        metrics = results_dict[method]
        final_ppl = metrics.get('final_perplexity', {})
        final_loss = metrics.get('final_domain_losses', {})

        ppl_vals = [final_ppl.get(d, np.nan) for d in DOMAINS]
        loss_vals = [final_loss.get(d, np.nan) for d in DOMAINS]

        offset = (i - len(methods) / 2 + 0.5) * width
        bars = ax_ppl.bar(x + offset, ppl_vals, width * 0.9, label=method,
                          color=colors[i], alpha=0.85)
        bars2 = ax_loss.bar(x + offset, loss_vals, width * 0.9, label=method,
                            color=colors[i], alpha=0.85)

    ax_ppl.set_xticks(x)
    ax_ppl.set_xticklabels([d.capitalize() for d in DOMAINS], rotation=15)
    ax_ppl.set_ylabel("Perplexity", fontsize=12)
    ax_ppl.set_title("Final Perplexity per Domain", fontsize=12)
    ax_ppl.legend(fontsize=9)
    ax_ppl.grid(True, alpha=0.3, axis='y')

    ax_loss.set_xticks(x)
    ax_loss.set_xticklabels([d.capitalize() for d in DOMAINS], rotation=15)
    ax_loss.set_ylabel("Cross-Entropy Loss", fontsize=12)
    ax_loss.set_title("Final Cross-Entropy Loss per Domain", fontsize=12)
    ax_loss.legend(fontsize=9)
    ax_loss.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    path = os.path.join(output_dir, "domain_perplexity.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def plot_mixture_evolution(results_dict, output_dir):
    """Plot how mixture weights evolve over training for each method."""
    methods_with_dynamic = {k: v for k, v in results_dict.items()
                             if v.get('mixture_log')}

    if not methods_with_dynamic:
        return None

    n_methods = len(methods_with_dynamic)
    fig, axes = plt.subplots(1, n_methods, figsize=(6 * n_methods, 5))
    if n_methods == 1:
        axes = [axes]

    fig.suptitle("Data Mixture Weight Evolution During Training", fontsize=14, fontweight='bold')
    domain_colors = plt.cm.tab10(np.linspace(0, 1, len(DOMAINS)))

    for ax, (method, metrics) in zip(axes, methods_with_dynamic.items()):
        mixture_log = metrics.get('mixture_log', [])
        if not mixture_log:
            continue

        mixture_arr = np.array(mixture_log)
        steps = np.arange(len(mixture_arr))

        # Sample if too many points
        if len(steps) > 500:
            idx = np.linspace(0, len(steps) - 1, 500, dtype=int)
            steps = steps[idx]
            mixture_arr = mixture_arr[idx]

        ax.stackplot(steps, mixture_arr.T, labels=[d.capitalize() for d in DOMAINS],
                    colors=domain_colors, alpha=0.8)
        ax.set_xlabel("Training Steps", fontsize=11)
        ax.set_ylabel("Mixture Weight", fontsize=11)
        ax.set_title(method, fontsize=12, fontweight='bold')
        ax.set_ylim(0, 1)
        ax.legend(loc='upper right', fontsize=8, ncol=2)
        ax.grid(True, alpha=0.2)

    plt.tight_layout()
    path = os.path.join(output_dir, "mixture_evolution.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def plot_overall_comparison(results_dict, output_dir):
    """Plot overall performance comparison bar chart."""
    methods = list(results_dict.keys())
    final_losses = [results_dict[m].get('final_eval_loss', np.nan) for m in methods]
    final_ppls = [np.exp(min(l, 15)) for l in final_losses]

    colors = {'DynaMix': '#e74c3c', 'Static Uniform': '#3498db',
              'Static Tuned': '#2ecc71', 'DoReMi-style': '#9b59b6',
              'PiKE-style': '#f39c12'}
    bar_colors = [colors.get(m, 'steelblue') for m in methods]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Overall Method Comparison", fontsize=14, fontweight='bold')

    ax1, ax2 = axes
    x = np.arange(len(methods))

    # Loss comparison
    bars1 = ax1.bar(x, final_losses, color=bar_colors, alpha=0.85, edgecolor='black', linewidth=0.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, rotation=20, ha='right', fontsize=10)
    ax1.set_ylabel("Final Evaluation Loss", fontsize=12)
    ax1.set_title("Final Average Cross-Entropy Loss\n(Lower is Better)", fontsize=12)
    ax1.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for bar, val in zip(bars1, final_losses):
        if not np.isnan(val):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=9)

    # Perplexity comparison
    bars2 = ax2.bar(x, final_ppls, color=bar_colors, alpha=0.85, edgecolor='black', linewidth=0.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(methods, rotation=20, ha='right', fontsize=10)
    ax2.set_ylabel("Final Average Perplexity", fontsize=12)
    ax2.set_title("Final Average Perplexity\n(Lower is Better)", fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')

    for bar, val in zip(bars2, final_ppls):
        if not np.isnan(val):
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    path = os.path.join(output_dir, "overall_comparison.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def plot_convergence_speed(results_dict, output_dir, target_loss_pct=0.1):
    """Plot convergence speed: steps to reach target loss improvement."""
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle("Convergence Speed Comparison", fontsize=14, fontweight='bold')

    colors = {'DynaMix': '#e74c3c', 'Static Uniform': '#3498db',
              'Static Tuned': '#2ecc71', 'DoReMi-style': '#9b59b6',
              'PiKE-style': '#f39c12'}
    linestyles = {'DynaMix': '-', 'Static Uniform': '--',
                  'Static Tuned': '-.', 'DoReMi-style': ':', 'PiKE-style': (0, (3, 1, 1, 1))}

    for method, metrics in results_dict.items():
        eval_steps = metrics.get('eval_steps', [])
        domain_eval = metrics.get('domain_eval_losses', [])

        if eval_steps and domain_eval:
            color = colors.get(method, 'gray')
            ls = linestyles.get(method, '-')
            ax.plot(eval_steps, domain_eval, label=method, color=color,
                   linestyle=ls, linewidth=2.5, marker='s', markersize=5)

    ax.set_xlabel("Training Steps", fontsize=12)
    ax.set_ylabel("Average Evaluation Loss", fontsize=12)
    ax.set_title("Convergence: Average Evaluation Loss over Training\n(Lower is Better)", fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, "convergence_speed.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def plot_scaling_law(scaling_estimator, output_dir):
    """Plot fitted scaling law curves."""
    if not scaling_estimator.is_fitted or len(scaling_estimator.observations) < 3:
        return None

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.suptitle("Scaling Law Estimation", fontsize=14, fontweight='bold')

    obs = scaling_estimator.observations
    xs = [o['n_params'] * o['compute'] for o in obs]
    ys = [o['loss'] for o in obs]

    # Plot observations
    ax.scatter(xs, ys, color='steelblue', s=60, zorder=5, label='Observations', alpha=0.8)

    # Plot fitted curve
    x_range = np.logspace(np.log10(min(xs) * 0.5), np.log10(max(xs) * 2), 100)
    y_pred = [scaling_estimator.predict_loss(x, 1) for x in x_range]
    ax.plot(x_range, y_pred, 'r-', linewidth=2, label='Fitted Scaling Law')

    ax.set_xscale('log')
    ax.set_xlabel("N × C (Model Parameters × Compute)", fontsize=12)
    ax.set_ylabel("Validation Loss", fontsize=12)
    ax.set_title("Power-Law Scaling Fit for DynaMix Proxy", fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, "scaling_law.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def plot_rl_training(dynamix_metrics, output_dir):
    """Plot RL controller training metrics."""
    ppo_losses = dynamix_metrics.get('ppo_losses', [])
    value_losses = dynamix_metrics.get('value_losses', [])

    if not ppo_losses:
        return None

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("DynaMix RL Controller Training", fontsize=14, fontweight='bold')

    ax1, ax2 = axes
    x = np.arange(len(ppo_losses))

    ax1.plot(x, ppo_losses, color='#e74c3c', linewidth=2, marker='o', markersize=3)
    ax1.set_xlabel("PPO Update #", fontsize=12)
    ax1.set_ylabel("PPO Policy Loss", fontsize=12)
    ax1.set_title("RL Policy Loss During Training", fontsize=12)
    ax1.grid(True, alpha=0.3)

    ax2.plot(x, value_losses, color='#3498db', linewidth=2, marker='s', markersize=3)
    ax2.set_xlabel("PPO Update #", fontsize=12)
    ax2.set_ylabel("Value Function Loss", fontsize=12)
    ax2.set_title("RL Value Loss During Training", fontsize=12)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, "rl_training.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def generate_all_figures(results_dict, output_dir, controller=None):
    """Generate all figures for the experiment."""
    os.makedirs(output_dir, exist_ok=True)
    figure_paths = {}

    figure_paths['training_curves'] = plot_training_curves(results_dict, output_dir)
    figure_paths['domain_perplexity'] = plot_domain_perplexity(results_dict, output_dir)
    figure_paths['mixture_evolution'] = plot_mixture_evolution(results_dict, output_dir)
    figure_paths['overall_comparison'] = plot_overall_comparison(results_dict, output_dir)
    figure_paths['convergence_speed'] = plot_convergence_speed(results_dict, output_dir)

    if controller is not None:
        if hasattr(controller, 'scaling_law'):
            sl_path = plot_scaling_law(controller.scaling_law, output_dir)
            if sl_path:
                figure_paths['scaling_law'] = sl_path

        rl_metrics = {
            'ppo_losses': getattr(controller, 'ppo_losses', []),
            'value_losses': getattr(controller, 'value_losses', []),
        }
        rl_path = plot_rl_training(rl_metrics, output_dir)
        if rl_path:
            figure_paths['rl_training'] = rl_path

    return figure_paths
