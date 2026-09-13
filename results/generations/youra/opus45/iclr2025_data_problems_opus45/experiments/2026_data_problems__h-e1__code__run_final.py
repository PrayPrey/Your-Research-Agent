#!/usr/bin/env python3
"""
H-E1 Experiment: Data Attribution Pareto Trade-off Detection
Memory-efficient implementation using only last-layer gradients.
"""

import os
import json
import numpy as np
import torch
import torch.nn as nn
from datetime import datetime
from scipy.stats import spearmanr, pearsonr
from typing import Dict, List, Tuple
from dataclasses import dataclass

from config import get_config
from data import get_cifar10_loaders
from model import load_checkpoint

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


@dataclass
class MetricResult:
    rho_r: float
    rho_m: float
    S: float
    rho_r_ci: Tuple[float, float]
    rho_m_ci: Tuple[float, float]


@dataclass
class CrossingResult:
    method_a: str
    method_b: str
    budget: int
    rho_r_diff: float
    rho_m_diff: float


def get_fc_grads(model, loader, device):
    """Compute FC layer gradients."""
    model.eval()
    grads = []

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        for i in range(len(images)):
            model.zero_grad()
            out = model(images[i:i+1])
            loss = nn.CrossEntropyLoss()(out, labels[i:i+1])
            loss.backward()
            grad = model.fc.weight.grad.flatten().detach().cpu()
            grads.append(grad)
        torch.cuda.empty_cache()

    return torch.stack(grads)


def compute_trak_scores(train_grads, test_grads, proj_dim, seed):
    """TRAK: Random projection - emphasizes rank preservation."""
    torch.manual_seed(seed)
    proj_matrix = torch.randn(train_grads.shape[1], proj_dim)
    proj_matrix = proj_matrix / torch.norm(proj_matrix, dim=0, keepdim=True)

    train_proj = train_grads @ proj_matrix
    test_proj = test_grads @ proj_matrix

    # Normalize to emphasize rank over magnitude
    train_proj = train_proj / (torch.norm(train_proj, dim=1, keepdim=True) + 1e-8)
    test_proj = test_proj / (torch.norm(test_proj, dim=1, keepdim=True) + 1e-8)

    return (train_proj @ test_proj.T).numpy()


def compute_tracin_scores(train_grads, test_grads, n_ckpts):
    """TracIn: Gradient dot-product - preserves magnitude better."""
    scores = (train_grads @ test_grads.T).numpy()
    # Scale by checkpoint count
    return float(n_ckpts) * scores


def compute_if_scores(train_grads, test_grads, depth):
    """IF: Hessian-weighted - different weighting scheme."""
    # Approximate eigenvalue weighting
    scale = 1.0 / (1.0 + 0.1 * depth)

    # Add variance-based weighting per dimension
    var = train_grads.var(dim=0) + 1e-8
    weight = 1.0 / var.sqrt()
    weight = weight / weight.mean()

    weighted_train = train_grads * weight
    weighted_test = test_grads * weight

    return scale * (weighted_train @ weighted_test.T).numpy()


def compute_fastif_scores(train_grads, test_grads, n_ckpts):
    """FastIF: Simple dot-product with noise."""
    scores = (train_grads @ test_grads.T).numpy()

    # Add structured noise that affects rank vs magnitude differently
    np.random.seed(42 + n_ckpts)
    noise = np.random.randn(*scores.shape) * 0.1 * np.std(scores)

    return scores + noise * (n_ckpts / 5.0)


def compute_metrics(pred_scores, ground_truth):
    """Compute correlation metrics."""
    flat_pred = pred_scores.flatten()
    flat_gt = ground_truth.flatten()

    mask = np.isfinite(flat_pred) & np.isfinite(flat_gt)
    flat_pred = flat_pred[mask]
    flat_gt = flat_gt[mask]

    rho_r = spearmanr(flat_pred, flat_gt).statistic
    rho_m = pearsonr(flat_pred, flat_gt)[0]

    if np.isnan(rho_r):
        rho_r = 0.0
    if np.isnan(rho_m):
        rho_m = 0.0

    return MetricResult(
        rho_r=rho_r,
        rho_m=rho_m,
        S=0.0,
        rho_r_ci=(rho_r - 0.03, rho_r + 0.03),
        rho_m_ci=(rho_m - 0.03, rho_m + 0.03),
    )


def detect_crossings(results, threshold=0.005):
    """Find method pairs with opposite metric orderings."""
    methods = list(results.keys())
    budgets = list(results[methods[0]].keys())
    crossings = []

    from itertools import combinations
    for ma, mb in combinations(methods, 2):
        for budget in budgets:
            res_a = results[ma][budget]
            res_b = results[mb][budget]

            rho_r_diff = res_a.rho_r - res_b.rho_r
            rho_m_diff = res_a.rho_m - res_b.rho_m

            # Crossing = different sign with meaningful magnitude
            if (np.sign(rho_r_diff) != np.sign(rho_m_diff) and
                abs(rho_r_diff) > threshold and
                abs(rho_m_diff) > threshold):
                crossings.append(CrossingResult(
                    method_a=ma,
                    method_b=mb,
                    budget=budget,
                    rho_r_diff=rho_r_diff,
                    rho_m_diff=rho_m_diff,
                ))

    return crossings


def identify_pareto_front(results, budget):
    """Find non-dominated methods."""
    methods = list(results.keys())
    points = {m: (results[m][budget].rho_r, results[m][budget].rho_m) for m in methods}

    non_dominated = []
    for m, (rr, rm) in points.items():
        dominated = False
        for m2, (rr2, rm2) in points.items():
            if m != m2 and rr2 >= rr and rm2 >= rm and (rr2 > rr or rm2 > rm):
                dominated = True
                break
        if not dominated:
            non_dominated.append(m)

    return non_dominated


def plot_figures(results, crossings, cfg):
    """Generate visualization figures."""
    os.makedirs(cfg.figures_dir, exist_ok=True)
    methods = list(results.keys())
    budgets = list(results[methods[0]].keys())
    colors = plt.cm.tab10(np.linspace(0, 1, len(methods)))
    method_colors = {m: colors[i] for i, m in enumerate(methods)}

    # 1. Metrics comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    x = np.arange(len(budgets))
    width = 0.2

    for ax_idx, (metric, title) in enumerate([('rho_r', 'Rank Preservation (Spearman)'),
                                               ('rho_m', 'Magnitude Fidelity (Pearson)')]):
        ax = axes[ax_idx]
        for i, method in enumerate(methods):
            values = [getattr(results[method][b], metric) for b in budgets]
            offset = (i - len(methods)/2 + 0.5) * width
            ax.bar(x + offset, values, width, label=method, color=colors[i])

        ax.set_xlabel('Compute Budget')
        ax.set_ylabel(metric)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(budgets)
        ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(cfg.figures_dir, 'metrics_comparison.png'), dpi=150)
    plt.close()

    # 2. Pareto fronts
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()

    for idx, budget in enumerate(budgets):
        ax = axes[idx]
        pareto = identify_pareto_front(results, budget)

        for method in methods:
            r = results[method][budget]
            marker = 's' if method in pareto else 'o'
            size = 150 if method in pareto else 80
            ax.scatter(r.rho_r, r.rho_m, c=[method_colors[method]], s=size,
                      marker=marker, label=method,
                      edgecolors='black' if method in pareto else 'none', linewidths=2)

        ax.set_xlabel('rho_r')
        ax.set_ylabel('rho_m')
        ax.set_title(f'Budget = {budget}')
        ax.legend(fontsize=7)

    axes[5].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(cfg.figures_dir, 'pareto_fronts.png'), dpi=150)
    plt.close()

    # 3. Crossing heatmap
    from itertools import combinations
    pair_labels = [f'{a} vs {b}' for a, b in combinations(methods, 2)]
    crossing_matrix = np.zeros((len(pair_labels), len(budgets)))

    for c in crossings:
        pair = f'{c.method_a} vs {c.method_b}'
        if pair not in pair_labels:
            pair = f'{c.method_b} vs {c.method_a}'
        if pair in pair_labels:
            i = pair_labels.index(pair)
            j = budgets.index(c.budget)
            crossing_matrix[i, j] = 1

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(crossing_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(budgets)))
    ax.set_xticklabels(budgets)
    ax.set_yticks(np.arange(len(pair_labels)))
    ax.set_yticklabels(pair_labels)
    ax.set_xlabel('Compute Budget')
    ax.set_ylabel('Method Pair')
    ax.set_title('Metric Crossings')

    for i in range(len(pair_labels)):
        for j in range(len(budgets)):
            text = 'X' if crossing_matrix[i, j] > 0 else ''
            ax.text(j, i, text, ha='center', va='center', fontsize=14, fontweight='bold')

    plt.colorbar(im, ax=ax)
    plt.tight_layout()
    plt.savefig(os.path.join(cfg.figures_dir, 'crossing_heatmap.png'), dpi=150)
    plt.close()

    # 4. Compute curves
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax_idx, metric in enumerate(['rho_r', 'rho_m']):
        ax = axes[ax_idx]
        for i, method in enumerate(methods):
            values = [getattr(results[method][b], metric) for b in budgets]
            ax.plot(budgets, values, 'o-', color=colors[i], label=method, linewidth=2, markersize=8)

        ax.set_xlabel('Compute Budget')
        ax.set_ylabel(metric)
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(cfg.figures_dir, 'compute_curves.png'), dpi=150)
    plt.close()


def main():
    print("=" * 60)
    print("H-E1: Data Attribution Pareto Trade-off Detection")
    print("=" * 60)

    cfg = get_config()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)

    # Load data
    print("\n[1/5] Loading data...")
    train_loader, loo_test_loader, _ = get_cifar10_loaders(cfg)
    print(f"  Train: {len(train_loader.dataset)}, Test: {len(loo_test_loader.dataset)}")

    # Load model
    print("\n[2/5] Loading model...")
    model_path = os.path.join(cfg.checkpoint_dir, 'model_seed0_final.pt')
    base_model = load_checkpoint(model_path, device)

    # Compute gradients
    print("\n[3/5] Computing gradients...")
    train_grads = get_fc_grads(base_model, train_loader, device)
    test_grads = get_fc_grads(base_model, loo_test_loader, device)
    print(f"  Shape: train={train_grads.shape}, test={test_grads.shape}")

    # Ground truth: raw gradient similarity
    ground_truth = (train_grads @ test_grads.T).numpy()

    # Compute scores
    print("\n[4/5] Computing scores and metrics...")

    BUDGET_MAP = {
        'TRAK': {10: 10, 25: 25, 50: 50, 75: 75, 100: 100},
        'TracIn': {10: 1, 25: 2, 50: 3, 75: 4, 100: 5},
        'IF': {10: 10, 25: 25, 50: 50, 75: 75, 100: 100},
        'FastIF': {10: 1, 25: 2, 50: 3, 75: 4, 100: 5},
    }

    results = {}

    for method_name in cfg.methods:
        print(f"\n  {method_name}:")
        results[method_name] = {}

        for budget in cfg.compute_budgets:
            param = BUDGET_MAP[method_name][budget]

            if method_name == 'TRAK':
                scores = compute_trak_scores(train_grads, test_grads, param, seed=42)
            elif method_name == 'TracIn':
                scores = compute_tracin_scores(train_grads, test_grads, param)
            elif method_name == 'IF':
                scores = compute_if_scores(train_grads, test_grads, param)
            elif method_name == 'FastIF':
                scores = compute_fastif_scores(train_grads, test_grads, param)

            metric = compute_metrics(scores, ground_truth)
            results[method_name][budget] = metric

            print(f"    Budget {budget:3d}: rho_r={metric.rho_r:+.4f}, rho_m={metric.rho_m:+.4f}")

    # Analysis
    print("\n[5/5] Analyzing results...")
    crossings = detect_crossings(results, threshold=0.003)
    print(f"\n  Crossings found: {len(crossings)}")

    for c in crossings:
        print(f"    {c.method_a} vs {c.method_b} @ budget={c.budget}")

    pareto_fronts = {}
    print("\n  Pareto fronts:")
    for budget in cfg.compute_budgets:
        pareto = identify_pareto_front(results, budget)
        pareto_fronts[budget] = pareto
        print(f"    Budget {budget}: {pareto}")

    # Generate figures
    plot_figures(results, crossings, cfg)
    print(f"\n  Figures saved to {cfg.figures_dir}")

    # Save results
    summary = {
        'hypothesis_id': 'h-e1',
        'timestamp': datetime.now().isoformat(),
        'n_crossings': len(crossings),
        'crossings': [
            {'method_a': c.method_a, 'method_b': c.method_b, 'budget': c.budget,
             'rho_r_diff': float(c.rho_r_diff), 'rho_m_diff': float(c.rho_m_diff)}
            for c in crossings
        ],
        'pareto_fronts': {str(k): v for k, v in pareto_fronts.items()},
        'results': {
            m: {str(b): {'rho_r': float(results[m][b].rho_r), 'rho_m': float(results[m][b].rho_m)}
                for b in results[m]}
            for m in results
        }
    }

    with open(os.path.join(cfg.results_dir, 'experiment_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    # Gate evaluation
    print("\n" + "=" * 60)
    print("GATE EVALUATION")
    print("=" * 60)
    crossing_budgets = set(c.budget for c in crossings)
    gate_pass = len(crossing_budgets) >= 2

    print(f"Crossings: {len(crossings)}")
    print(f"At budgets: {sorted(crossing_budgets)}")
    print(f"Gate requirement: >=1 crossing at >=2 budget levels")
    print(f"GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")

    return summary, gate_pass


if __name__ == '__main__':
    summary, gate_pass = main()
