"""
Visualization utilities for experimental results
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from typing import Dict, List
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.size'] = 10

def plot_training_curves(training_history: Dict[str, List[float]],
                        save_path: str, title: str = "Training Curves"):
    """Plot training loss curves"""
    fig, ax = plt.subplots(figsize=(10, 6))

    for model_name, losses in training_history.items():
        epochs = list(range(1, len(losses) + 1))
        ax.plot(epochs, losses, marker='o', label=model_name, linewidth=2, markersize=4)

    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Loss', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()

def plot_model_comparison(results: Dict[str, Dict[str, float]],
                         metrics: List[str], save_path: str,
                         title: str = "Model Comparison"):
    """Plot bar chart comparing models across metrics"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    model_names = list(results.keys())
    x = np.arange(len(model_names))
    width = 0.6

    for idx, metric in enumerate(metrics[:4]):
        ax = axes[idx]
        values = [results[model].get(metric, 0) for model in model_names]

        bars = ax.bar(x, values, width, alpha=0.8)

        # Color bars
        colors = ['#d62728' if 'static' in name else '#2ca02c' if 'adaptive' in name
                 else '#ff7f0e' for name in model_names]
        for bar, color in zip(bars, colors):
            bar.set_color(color)

        ax.set_xlabel('Model', fontsize=11)
        ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=11)
        ax.set_title(f'{metric.replace("_", " ").title()}', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([name.replace('_', '\n') for name in model_names],
                          rotation=0, fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.3f}', ha='center', va='bottom', fontsize=9)

    plt.suptitle(title, fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()

def plot_temporal_tracking(tracking_results: Dict[str, Dict],
                          save_path: str, metric: str = 'accuracy_over_time',
                          title: str = "Preference Tracking Over Time"):
    """Plot how models track preferences over time"""
    fig, ax = plt.subplots(figsize=(12, 6))

    for model_name, results in tracking_results.items():
        timesteps = results.get('timesteps', [])
        values = results.get(metric, [])
        ax.plot(timesteps, values, marker='o', label=model_name,
               linewidth=2, markersize=3, alpha=0.8)

    ax.set_xlabel('Interaction Timestep', fontsize=12)
    ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()

def plot_model_value_evolution(tracking_results: Dict,
                               scenario: str, model_name: str,
                               save_dir: str):
    """Plot how a specific model tracks value evolution"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    timesteps = tracking_results['timesteps']
    accuracy = tracking_results['accuracy_over_time']
    alignment = tracking_results['alignment_over_time']

    # Plot accuracy
    ax1.plot(timesteps, accuracy, marker='o', linewidth=2,
            markersize=4, color='#1f77b4', alpha=0.8)
    ax1.axhline(y=np.mean(accuracy), color='r', linestyle='--',
               alpha=0.5, label=f'Mean: {np.mean(accuracy):.3f}')
    ax1.set_xlabel('Interaction Timestep', fontsize=12)
    ax1.set_ylabel('Accuracy', fontsize=12)
    ax1.set_title(f'Prediction Accuracy Over Time - {model_name}',
                 fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Plot alignment score
    ax2.plot(timesteps, alignment, marker='s', linewidth=2,
            markersize=4, color='#ff7f0e', alpha=0.8)
    ax2.axhline(y=np.mean(alignment), color='r', linestyle='--',
               alpha=0.5, label=f'Mean: {np.mean(alignment):.3f}')
    ax2.set_xlabel('Interaction Timestep', fontsize=12)
    ax2.set_ylabel('Alignment Score', fontsize=12)
    ax2.set_title(f'Alignment Score Over Time - {model_name}',
                 fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    save_path = os.path.join(save_dir, f'model_value_evolution_{model_name}_{scenario}.png')
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()

def plot_human_value_evolution(environment, scenario: str, save_path: str):
    """Visualize simulated human value evolution"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    # Sample a few users
    sample_users = [0, 1, 2, 3]

    for idx, user_id in enumerate(sample_users):
        ax = axes[idx]
        trajectory = environment.generate_interaction_trajectory(user_id)

        timesteps = trajectory['timesteps']
        actions = trajectory['human_actions']
        pref_types = trajectory['preference_type']

        # Plot action distribution over time using a rolling window
        window_size = 10
        action_diversity = []
        for i in range(len(actions) - window_size):
            window_actions = actions[i:i+window_size]
            diversity = len(set(window_actions)) / window_size
            action_diversity.append(diversity)

        if len(action_diversity) > 0:
            ax.plot(timesteps[window_size:], action_diversity,
                   linewidth=2, color='#2ca02c')
            ax.set_xlabel('Timestep', fontsize=11)
            ax.set_ylabel('Action Diversity', fontsize=11)
            ax.set_title(f'User {user_id} - Value Evolution', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)

            # Mark preference type changes
            evolved_timesteps = [t for t, pt in zip(timesteps, pref_types) if pt == 'evolved']
            if evolved_timesteps:
                ax.axvline(x=evolved_timesteps[0], color='r', linestyle='--',
                          alpha=0.5, label='Preference Evolution')
                ax.legend(fontsize=9)

    plt.suptitle(f'Human Value Evolution - {scenario}',
                fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()

def plot_scenario_comparison(all_results: Dict[str, Dict[str, Dict]],
                            metric: str, save_path: str):
    """Compare model performance across different scenarios"""
    scenarios = list(all_results.keys())
    models = list(next(iter(all_results.values())).keys())

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(scenarios))
    width = 0.2
    multiplier = 0

    for model in models:
        values = [all_results[scenario][model].get(metric, 0)
                 for scenario in scenarios]
        offset = width * multiplier
        bars = ax.bar(x + offset, values, width, label=model, alpha=0.8)
        multiplier += 1

    ax.set_xlabel('Scenario', fontsize=12)
    ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=12)
    ax.set_title(f'{metric.replace("_", " ").title()} Across Scenarios',
                fontsize=14, fontweight='bold')
    ax.set_xticks(x + width * (len(models) - 1) / 2)
    ax.set_xticklabels([s.replace('_', ' ').title() for s in scenarios])
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()

def plot_radar_chart(results: Dict[str, Dict[str, float]],
                    metrics: List[str], save_path: str):
    """Create radar chart comparing models"""
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]

    for model_name, model_results in results.items():
        values = [model_results.get(metric, 0) for metric in metrics]
        values += values[:1]

        ax.plot(angles, values, 'o-', linewidth=2, label=model_name, markersize=6)
        ax.fill(angles, values, alpha=0.15)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([m.replace('_', ' ').title() for m in metrics], fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_title('Model Performance Comparison (Radar Chart)',
                fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
    ax.grid(True)

    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()

def plot_aggregate_comparison(all_results: Dict[str, Dict[str, Dict]],
                              save_path: str):
    """Create comprehensive comparison across all scenarios"""
    # Aggregate metrics across scenarios
    models = list(next(iter(all_results.values())).keys())
    metrics = ['accuracy', 'alignment_score', 'stability', 'user_satisfaction']

    aggregated = {model: {metric: [] for metric in metrics} for model in models}

    for scenario, scenario_results in all_results.items():
        for model, model_results in scenario_results.items():
            for metric in metrics:
                if metric in model_results:
                    aggregated[model][metric].append(model_results[metric])

    # Compute means
    mean_results = {}
    for model in models:
        mean_results[model] = {
            metric: np.mean(values) if values else 0
            for metric, values in aggregated[model].items()
        }

    # Plot
    fig, axes = plt.subplots(1, len(metrics), figsize=(18, 5))

    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        values = [mean_results[model][metric] for model in models]
        x = np.arange(len(models))

        bars = ax.bar(x, values, alpha=0.8)
        colors = ['#d62728', '#ff7f0e', '#bcbd22', '#2ca02c']
        for bar, color in zip(bars, colors):
            bar.set_color(color)

        ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=11)
        ax.set_title(metric.replace('_', ' ').title(), fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([m.replace('_', '\n') for m in models],
                          rotation=0, fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.3f}', ha='center', va='bottom', fontsize=9)

    plt.suptitle('Aggregate Performance Across All Scenarios',
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()
