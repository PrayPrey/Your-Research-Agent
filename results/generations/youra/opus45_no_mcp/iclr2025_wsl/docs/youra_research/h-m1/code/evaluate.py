import numpy as np
import torch
from scipy.stats import pearsonr, ttest_rel
import matplotlib.pyplot as plt
from train import prepare_flatten_batch

def predict(model, loader, device, method, input_dim=None):
    model.eval()
    all_preds = []
    all_targets = []
    with torch.no_grad():
        for weights_list, targets in loader:
            if method == "flatten":
                weights_input = prepare_flatten_batch(weights_list, input_dim, device)
            else:
                weights_input = weights_list
            preds = model(weights_input, device)
            all_preds.append(preds.cpu().numpy())
            all_targets.append(targets.numpy())
    return np.concatenate(all_preds), np.concatenate(all_targets)

def compute_pearson(preds, targets):
    r, p = pearsonr(preds, targets)
    return {'pearson_r': r, 'p_value': p}

def compare_methods(flatten_results, layerwise_results):
    t_stat, p_val = ttest_rel(layerwise_results, flatten_results)
    delta_r = np.mean(layerwise_results) - np.mean(flatten_results)
    return {'delta_r': delta_r, 't_stat': t_stat, 'p_value': p_val}

def plot_gate_metrics(flatten_r, layerwise_r, save_path):
    fig, ax = plt.subplots(figsize=(8, 6))
    means = [np.mean(flatten_r), np.mean(layerwise_r)]
    stds = [np.std(flatten_r), np.std(layerwise_r)]
    bars = ax.bar(['Flatten+MLP', 'Layer-wise'], means, yerr=stds, capsize=5, color=['#2ecc71', '#3498db'])
    ax.set_ylabel('Pearson r')
    ax.set_title('Gate Metrics: Flatten+MLP vs Layer-wise')
    ax.set_ylim(0, 1)
    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f'{mean:.3f}', ha='center')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_scatter(preds, targets, method_name, save_path):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(targets, preds, alpha=0.3, s=5)
    ax.plot([0, 1], [0, 1], 'r--', label='Perfect')
    ax.set_xlabel('Actual Accuracy')
    ax.set_ylabel('Predicted Accuracy')
    ax.set_title(f'{method_name}: Predicted vs Actual')
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_per_seed(flatten_r, layerwise_r, save_path):
    fig, ax = plt.subplots(figsize=(8, 5))
    seeds = range(len(flatten_r))
    ax.plot(seeds, flatten_r, 'o-', label='Flatten+MLP', color='#2ecc71')
    ax.plot(seeds, layerwise_r, 's-', label='Layer-wise', color='#3498db')
    ax.set_xlabel('Seed')
    ax.set_ylabel('Pearson r')
    ax.set_title('Per-Seed Results')
    ax.legend()
    ax.set_xticks(list(seeds))
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_loss_curves(history, method_name, save_path):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(history['train_loss'], label='Train')
    ax.plot(history['val_loss'], label='Val')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('MSE Loss')
    ax.set_title(f'{method_name}: Loss Curves')
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
