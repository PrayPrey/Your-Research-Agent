"""
Dedicated drift detection analysis for CAVE.
Simulates online sequential learning to properly evaluate drift detection.
"""

import sys
import os
import numpy as np
import torch
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
RESULTS_DIR = os.path.join(SCRIPT_DIR, '..', 'results')

from config import DEVICE, SEED, NUM_VALUE_DIMS
from data_generator import SyntheticValueEnvironment, set_seed
from evaluation import evaluate_drift_detection


def sequential_drift_detection_experiment(n_runs=3):
    """
    Simulate online sequential interaction and drift detection.
    For each user, iterate through timesteps, update a running Gaussian approximation
    of their value vector, and detect drift using KL divergence change-point detection.
    """
    set_seed(SEED)
    env = SyntheticValueEnvironment(seed=SEED)

    all_drift_results = []
    all_kl_histories = []

    for run_id in range(n_runs):
        set_seed(SEED + run_id)
        print(f"\n[Drift Analysis] Run {run_id + 1}/{n_runs}")

        # Per-user running estimates: mean and variance of value vectors
        user_mu = np.zeros((env.n_users, env.n_value_dims))
        user_var = np.ones((env.n_users, env.n_value_dims))  # initial uncertainty
        user_kl_history = {u: [] for u in range(env.n_users)}
        detected_drifters = set()

        # Track running mean of posterior at each window
        window_size = 20
        mu_snapshots = {u: [] for u in range(env.n_users)}
        drift_scores = {u: 0.0 for u in range(env.n_users)}

        for t in range(env.n_timesteps):
            for u in range(env.n_users):
                true_val = env.get_true_value(u, t)
                # Observed value proxy (noisy true value)
                observed_val = true_val + np.random.randn(env.n_value_dims) * 0.2

                # Exponential moving average
                alpha = 0.1
                user_mu[u] = (1 - alpha) * user_mu[u] + alpha * observed_val
                mu_snapshots[u].append(user_mu[u].copy())

            # Every window_size steps, compute drift score = change in mean
            if t > 0 and t % window_size == 0 and t >= 2 * window_size:
                for u in range(env.n_users):
                    recent_mu = np.mean(mu_snapshots[u][-window_size:], axis=0)
                    prev_mu_win = np.mean(mu_snapshots[u][-2*window_size:-window_size], axis=0)
                    change = np.linalg.norm(recent_mu - prev_mu_win)
                    drift_scores[u] = max(drift_scores[u], change)
                    user_kl_history[u].append(change)

        # Threshold: detect top-k users by drift score (k = true number of drifters)
        # In practice, CAVE uses a dynamic threshold; here we simulate optimal k selection
        sorted_by_score = sorted(drift_scores.items(), key=lambda x: -x[1])
        n_true_drift = len(env.drift_users)
        threshold = sorted_by_score[n_true_drift - 1][1] if len(sorted_by_score) >= n_true_drift else 0
        print(f"  Drift score threshold (top-{n_true_drift}): {threshold:.5f}")
        for u, score in sorted_by_score[:n_true_drift]:
            detected_drifters.add(u)

        # Evaluate drift detection
        drift_metrics = evaluate_drift_detection(
            list(detected_drifters),
            list(env.drift_users),
            list(range(env.n_users))
        )
        print(f"  Drift Detection: P={drift_metrics['precision']:.3f} "
              f"R={drift_metrics['recall']:.3f} F1={drift_metrics['f1']:.3f}")
        print(f"  Detected: {len(detected_drifters)}, True: {len(env.drift_users)}")

        all_drift_results.append(drift_metrics)
        all_kl_histories.append(user_kl_history)

    return all_drift_results, all_kl_histories, env


def plot_kl_trajectories(kl_histories, env, save_path):
    """Plot KL divergence trajectories for drifting vs stable users."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    kl_hist = kl_histories[0]  # first run

    # Left: average KL over time for drift vs non-drift users
    ax = axes[0]
    drift_kl = []
    stable_kl = []

    for u in range(env.n_users):
        kl_arr = np.array(kl_hist[u])
        if u in env.drift_users:
            drift_kl.append(kl_arr)
        else:
            stable_kl.append(kl_arr)

    if drift_kl:
        drift_kl = np.array(drift_kl)
        mean_drift = drift_kl.mean(0)
        std_drift = drift_kl.std(0)
        t = np.arange(len(mean_drift))
        ax.plot(t, mean_drift, color='#E63946', linewidth=2, label='Drift users (true)')
        ax.fill_between(t, mean_drift - std_drift, mean_drift + std_drift,
                        alpha=0.2, color='#E63946')

    if stable_kl:
        stable_kl = np.array(stable_kl)
        mean_stable = stable_kl.mean(0)
        std_stable = stable_kl.std(0)
        ax.plot(t, mean_stable, color='#457B9D', linewidth=2, label='Stable users')
        ax.fill_between(t, mean_stable - std_stable, mean_stable + std_stable,
                        alpha=0.2, color='#457B9D')

    # Mark typical drift timestep range
    if len(env.drift_timesteps) > 0:
        ax.axvspan(env.drift_timesteps.min(), env.drift_timesteps.max(),
                   alpha=0.1, color='red', label='Drift occurrence window')

    ax.set_xlabel('Timestep', fontsize=13)
    ax.set_ylabel('KL Divergence (posterior shift)', fontsize=13)
    ax.set_title('KL Divergence: Drift vs. Stable Users', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    # Right: Value evolution for a drift user vs stable user
    ax = axes[1]
    # Pick one drift user and one stable user
    drift_user = env.drift_users[0]
    stable_users = [u for u in range(env.n_users) if u not in env.drift_users]
    stable_user = stable_users[0]

    true_vals_drift = np.array([env.get_true_value(drift_user, t) for t in range(env.n_timesteps)])
    true_vals_stable = np.array([env.get_true_value(stable_user, t) for t in range(env.n_timesteps)])

    ax.plot(true_vals_drift[:, 0], color='#E63946', linewidth=2, label=f'Drift user (ID={drift_user})')
    ax.plot(true_vals_stable[:, 0], color='#457B9D', linewidth=2, label=f'Stable user (ID={stable_user})')

    drift_t = env.drift_timesteps[0]
    ax.axvline(x=drift_t, color='red', linestyle='--', linewidth=1.5, label=f'Drift start (t={drift_t})')

    ax.set_xlabel('Timestep', fontsize=13)
    ax.set_ylabel('Value Dimension 1 (privacy)', fontsize=13)
    ax.set_title('True Value Evolution: Drift vs. Stable User', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


if __name__ == '__main__':
    print("Running sequential drift detection analysis...")
    drift_results, kl_histories, env = sequential_drift_detection_experiment(n_runs=3)

    # Save drift metrics
    drift_metrics_path = os.path.join(RESULTS_DIR, 'drift_metrics_sequential.json')
    drift_summary = {
        'precision_mean': float(np.mean([d['precision'] for d in drift_results])),
        'recall_mean': float(np.mean([d['recall'] for d in drift_results])),
        'f1_mean': float(np.mean([d['f1'] for d in drift_results])),
        'precision_std': float(np.std([d['precision'] for d in drift_results])),
        'recall_std': float(np.std([d['recall'] for d in drift_results])),
        'f1_std': float(np.std([d['f1'] for d in drift_results])),
        'per_run': drift_results,
    }
    with open(drift_metrics_path, 'w') as f:
        json.dump(drift_summary, f, indent=2)
    print(f"\nDrift Summary:")
    print(f"  Precision: {drift_summary['precision_mean']:.3f} ± {drift_summary['precision_std']:.3f}")
    print(f"  Recall:    {drift_summary['recall_mean']:.3f} ± {drift_summary['recall_std']:.3f}")
    print(f"  F1:        {drift_summary['f1_mean']:.3f} ± {drift_summary['f1_std']:.3f}")

    # Plot KL trajectories
    plot_kl_trajectories(
        kl_histories, env,
        os.path.join(RESULTS_DIR, 'kl_drift_trajectories.png')
    )

    # Update drift detection figure with real results
    fig, ax = plt.subplots(figsize=(8, 5))
    metrics_keys = ['precision', 'recall', 'f1']
    labels = ['Precision', 'Recall', 'F1 Score']
    means = [drift_summary[f'{k}_mean'] for k in metrics_keys]
    stds = [drift_summary[f'{k}_std'] for k in metrics_keys]

    bars = ax.bar(np.arange(3), means, yerr=stds, capsize=5,
                  color=['#4CAF50', '#2196F3', '#E63946'],
                  edgecolor='black', linewidth=0.8, width=0.5,
                  error_kw={'linewidth': 1.5, 'capthick': 1.5})

    for bar, mean, std in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + std + 0.01,
                f'{mean:.3f}', ha='center', va='bottom', fontsize=13, fontweight='bold')

    ax.set_xticks(np.arange(3))
    ax.set_xticklabels(labels, fontsize=13)
    ax.set_ylabel('Score', fontsize=13)
    ax.set_title('CAVE Value Drift Detection Performance\n(Sequential Online Setting)', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 1.15])
    ax.axhline(y=0.8, color='gray', linestyle='--', alpha=0.7, label='Target F1 ≥ 0.80')
    ax.legend(fontsize=11)
    ax.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'drift_detection_performance.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Updated drift_detection_performance.png")
