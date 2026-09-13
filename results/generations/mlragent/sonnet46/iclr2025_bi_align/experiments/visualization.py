"""
Visualization routines for CAVE experiment results.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import sem
import os


COLORS = {
    'CAVE': '#E63946',
    'LoCo-RLHF': '#457B9D',
    'Population-RLHF': '#2A9D8F',
    'ContextualBandit': '#F4A261',
    'StaticPersonalization': '#A8DADC',
}
MARKERS = {
    'CAVE': 'o',
    'LoCo-RLHF': 's',
    'Population-RLHF': '^',
    'ContextualBandit': 'D',
    'StaticPersonalization': 'v',
}

MODEL_LABELS = {
    'CAVE': 'CAVE (Proposed)',
    'LoCo-RLHF': 'LoCo-RLHF',
    'Population-RLHF': 'Population RLHF',
    'ContextualBandit': 'Contextual Bandit+Entropy',
    'StaticPersonalization': 'Static Personalization',
}


def plot_training_loss_curves(all_results, save_path):
    """Plot training loss curves for all models across runs."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Loss curves
    ax = axes[0]
    for name, results in all_results.items():
        losses = np.array(results['train_losses'])  # (n_runs, n_epochs)
        mean_loss = losses.mean(0)
        std_loss = losses.std(0)
        epochs = np.arange(1, len(mean_loss) + 1)
        ax.plot(epochs, mean_loss, label=MODEL_LABELS[name],
                color=COLORS[name], marker=MARKERS[name], markevery=10, linewidth=2)
        ax.fill_between(epochs, mean_loss - std_loss, mean_loss + std_loss,
                        alpha=0.15, color=COLORS[name])

    ax.set_xlabel('Epoch', fontsize=13)
    ax.set_ylabel('Training Loss', fontsize=13)
    ax.set_title('Training Loss Curves', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # Validation AUC curves
    ax = axes[1]
    for name, results in all_results.items():
        aucs = np.array(results['val_aucs'])  # (n_runs, n_epochs)
        mean_auc = aucs.mean(0)
        std_auc = aucs.std(0)
        epochs = np.arange(1, len(mean_auc) + 1)
        ax.plot(epochs, mean_auc, label=MODEL_LABELS[name],
                color=COLORS[name], marker=MARKERS[name], markevery=10, linewidth=2)
        ax.fill_between(epochs, mean_auc - std_auc, mean_auc + std_auc,
                        alpha=0.15, color=COLORS[name])

    ax.set_xlabel('Epoch', fontsize=13)
    ax.set_ylabel('Validation AUC-ROC', fontsize=13)
    ax.set_title('Preference Prediction Performance over Training', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0.45, 1.0])

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_final_auc_comparison(all_results, save_path):
    """Bar chart comparing final AUC-ROC across models."""
    names = list(all_results.keys())
    means = []
    stds = []

    for name in names:
        aucs = np.array(all_results[name]['val_aucs'])  # (n_runs, n_epochs)
        final_aucs = aucs[:, -1]
        means.append(final_aucs.mean())
        stds.append(final_aucs.std())

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(names))
    bars = ax.bar(x, means, yerr=stds, capsize=5,
                  color=[COLORS[n] for n in names],
                  edgecolor='black', linewidth=0.8, width=0.6,
                  error_kw={'linewidth': 1.5, 'capthick': 1.5})

    # Add value labels on bars
    for bar, mean, std in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + std + 0.005,
                f'{mean:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_LABELS[n] for n in names], rotation=15, ha='right', fontsize=11)
    ax.set_ylabel('Final Validation AUC-ROC', fontsize=13)
    ax.set_title('Representational Fidelity: Preference Prediction AUC-ROC', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 1.05])
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.7, label='Random baseline (0.5)')
    ax.legend(fontsize=11)
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_value_diversity_over_time(all_results, save_path):
    """Plot value diversity (JS divergence) over training epochs."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for name, results in all_results.items():
        if 'value_diversity' not in results or len(results['value_diversity']) == 0:
            continue
        divs = np.array(results['value_diversity'])  # (n_runs, n_checkpoints)
        if divs.ndim == 1:
            divs = divs.reshape(1, -1)
        mean_div = divs.mean(0)
        std_div = divs.std(0)
        x = np.linspace(0, 50, len(mean_div))
        ax.plot(x, mean_div, label=MODEL_LABELS[name],
                color=COLORS[name], marker=MARKERS[name], markevery=5, linewidth=2)
        ax.fill_between(x, mean_div - std_div, mean_div + std_div,
                        alpha=0.15, color=COLORS[name])

    ax.set_xlabel('Training Epoch', fontsize=13)
    ax.set_ylabel('Jensen-Shannon Divergence (between groups)', fontsize=13)
    ax.set_title('Value Diversity Preservation over Training\n(Higher = Better Diversity)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_drift_detection_performance(drift_results, save_path):
    """Bar chart of drift detection precision/recall/F1 for CAVE."""
    metrics_keys = ['precision', 'recall', 'f1']
    labels = ['Precision', 'Recall', 'F1 Score']

    # Average across runs
    means = [np.mean([r[k] for r in drift_results]) for k in metrics_keys]
    stds = [np.std([r[k] for r in drift_results]) for k in metrics_keys]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(labels))
    bars = ax.bar(x, means, yerr=stds, capsize=5,
                  color=['#4CAF50', '#2196F3', '#E63946'],
                  edgecolor='black', linewidth=0.8, width=0.5,
                  error_kw={'linewidth': 1.5, 'capthick': 1.5})

    for bar, mean, std in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + std + 0.01,
                f'{mean:.3f}', ha='center', va='bottom', fontsize=13, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=13)
    ax.set_ylabel('Score', fontsize=13)
    ax.set_title('CAVE Value Drift Detection Performance', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 1.15])
    ax.axhline(y=0.8, color='gray', linestyle='--', alpha=0.7, label='Target F1 ≥ 0.80')
    ax.legend(fontsize=11)
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_feedback_efficiency(all_results, save_path):
    """Plot queries vs. AUC-ROC for CAVE (active) vs. random baseline."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: cumulative queries for CAVE vs other models
    ax = axes[0]
    cave_queries = np.array(all_results['CAVE']['elicitation_counts'])  # (n_runs, n_epochs)
    if cave_queries.ndim == 1:
        cave_queries = cave_queries.reshape(1, -1)

    cumulative = np.cumsum(cave_queries, axis=1)
    mean_cum = cumulative.mean(0)
    std_cum = cumulative.std(0)
    epochs = np.arange(1, len(mean_cum) + 1)
    ax.plot(epochs, mean_cum, color=COLORS['CAVE'], linewidth=2, label='CAVE (Active)')
    ax.fill_between(epochs, mean_cum - std_cum, mean_cum + std_cum, alpha=0.2, color=COLORS['CAVE'])

    # Hypothetical uniform sampling (all samples queried)
    n_samples_per_epoch = all_results['CAVE'].get('n_train_per_epoch', 160)
    uniform_cum = np.cumsum(np.ones(len(mean_cum)) * n_samples_per_epoch)
    ax.plot(epochs, uniform_cum, '--', color='gray', linewidth=2, label='Uniform Sampling')

    ax.set_xlabel('Epoch', fontsize=13)
    ax.set_ylabel('Cumulative Feedback Queries', fontsize=13)
    ax.set_title('Feedback Efficiency: Cumulative Queries over Training', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    # Right: AUC vs. queries (efficiency curve)
    ax = axes[1]
    cave_aucs = np.array(all_results['CAVE']['val_aucs'])
    mean_auc = cave_aucs.mean(0)
    mean_cum = np.cumsum(cave_queries.mean(0))

    ax.plot(mean_cum, mean_auc, '-o', color=COLORS['CAVE'], linewidth=2,
            label='CAVE (Active)', markevery=10)

    # Other models with uniform query (n_samples * epoch)
    for name in ['Population-RLHF', 'LoCo-RLHF', 'StaticPersonalization']:
        if name in all_results:
            aucs = np.array(all_results[name]['val_aucs']).mean(0)
            uniform_q = np.cumsum(np.ones(len(aucs)) * n_samples_per_epoch)
            ax.plot(uniform_q, aucs, '--', color=COLORS[name], linewidth=2,
                    label=MODEL_LABELS[name], marker=MARKERS[name], markevery=10)

    ax.set_xlabel('Cumulative Feedback Queries', fontsize=13)
    ax.set_ylabel('Validation AUC-ROC', fontsize=13)
    ax.set_title('Feedback Efficiency: AUC vs. Queries', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0.45, 1.0])

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_value_trajectory(user_trajectories, drift_events_per_user, save_path, n_users_to_show=5):
    """
    Visualize value evolution trajectories for select users.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Value dimension evolution for selected users
    ax = axes[0]
    colors_traj = plt.cm.tab10(np.linspace(0, 1, n_users_to_show))

    for i, (uid, traj) in enumerate(list(user_trajectories.items())[:n_users_to_show]):
        traj = np.array(traj)  # (T, value_dim)
        # Show first value dimension
        ax.plot(np.arange(len(traj)), traj[:, 0], color=colors_traj[i],
                linewidth=2, label=f'User {uid}')

        # Mark drift events
        if uid in drift_events_per_user:
            for t_drift in drift_events_per_user[uid]:
                ax.axvline(x=t_drift, color=colors_traj[i], linestyle='--', alpha=0.5)

    ax.set_xlabel('Training Epoch', fontsize=13)
    ax.set_ylabel('Value Dimension 1 (mean)', fontsize=13)
    ax.set_title('User Value Trajectories\n(dashed = detected drift)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)

    # Right: Heatmap of value evolution for all users, dim 0
    ax = axes[1]
    all_trajs = np.array([v for v in user_trajectories.values()])  # (n_users, T, value_dim)
    if all_trajs.ndim == 3:
        heatmap_data = all_trajs[:, :, 0]  # first value dim
        im = ax.imshow(heatmap_data, aspect='auto', cmap='RdYlGn',
                       origin='lower', interpolation='nearest')
        plt.colorbar(im, ax=ax, label='Value (Privacy dim.)')
        ax.set_xlabel('Training Epoch', fontsize=13)
        ax.set_ylabel('User ID', fontsize=13)
        ax.set_title('Value Distribution Across Users over Time', fontsize=13, fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_group_diversity_comparison(all_results, save_path):
    """Compare final value diversity (JS divergence) across models."""
    names = list(all_results.keys())
    means = []
    stds = []

    for name in names:
        divs = all_results[name].get('value_diversity', [[0]])
        divs = np.array(divs)
        if divs.ndim == 2:
            final_divs = divs[:, -1]
        elif divs.ndim == 1:
            final_divs = divs
        else:
            final_divs = np.array([0])
        means.append(final_divs.mean())
        stds.append(final_divs.std())

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(names))
    bars = ax.bar(x, means, yerr=stds, capsize=5,
                  color=[COLORS[n] for n in names],
                  edgecolor='black', linewidth=0.8, width=0.6,
                  error_kw={'linewidth': 1.5, 'capthick': 1.5})

    for bar, mean, std in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + std + 0.002,
                f'{mean:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_LABELS[n] for n in names], rotation=15, ha='right', fontsize=11)
    ax.set_ylabel('Jensen-Shannon Divergence', fontsize=13)
    ax.set_title('Value Diversity Preservation Across Demographic Groups\n(Higher = Better Diversity)', fontsize=14, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")
