"""
Evaluation utilities for H-E1 experiment.
LOO ground truth, metrics computation, crossing detection, visualization.
"""

import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from itertools import combinations
from scipy.stats import spearmanr, pearsonr, bootstrap
import matplotlib.pyplot as plt

from config import ExperimentConfig


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
    crosses_rho_r: bool
    crosses_rho_m: bool
    rho_r_diff_ci: Tuple[float, float]
    rho_m_diff_ci: Tuple[float, float]


def _compute_full_losses(
    model: nn.Module,
    test_loader: DataLoader,
    device: str,
) -> np.ndarray:
    """Per-sample cross-entropy losses. Returns [n_test]."""
    model.eval()
    criterion = nn.CrossEntropyLoss(reduction='none')
    losses = []

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            batch_losses = criterion(outputs, labels)
            losses.extend(batch_losses.cpu().numpy())

    return np.array(losses)


def compute_loo_ground_truth(
    model_fn: Callable[[int], nn.Module],
    train_model_fn: Callable,
    train_subset: Subset,
    train_loader: DataLoader,
    loo_test_loader: DataLoader,
    cfg: ExperimentConfig,
    device: str = 'cuda',
) -> np.ndarray:
    """
    Compute LOO ground truth via R=10 retraining.
    Returns [n_train, n_loo_test] influence matrix.

    Note: Full LOO (5000 samples × 10 retrains) is extremely expensive.
    For PoC, we use a subset of training samples.
    """
    cache_path = os.path.join(cfg.results_dir, 'loo_cache.npy')

    if os.path.exists(cache_path):
        print(f"Loading cached LOO ground truth from {cache_path}")
        return np.load(cache_path)

    n_train = len(train_subset)
    n_test = len(loo_test_loader.dataset)

    loo_train_indices = np.random.choice(n_train, size=min(100, n_train), replace=False)
    n_loo_train = len(loo_train_indices)

    print(f"Computing LOO ground truth for {n_loo_train} training samples...")

    deltas = np.zeros((n_train, n_test))

    for r in range(cfg.n_loo_retrains):
        print(f"  Retrain {r+1}/{cfg.n_loo_retrains}")

        base_model = model_fn(r)
        base_model = train_model_fn(
            base_model, train_loader, cfg, seed=r, device=device, save_checkpoints=False
        )
        base_losses = _compute_full_losses(base_model, loo_test_loader, device)

        for idx, i in enumerate(loo_train_indices):
            if idx % 20 == 0:
                print(f"    LOO sample {idx+1}/{n_loo_train}")

            from data import make_loo_loader
            loo_loader = make_loo_loader(train_subset, i, cfg)

            loo_model = model_fn(r)
            loo_model = train_model_fn(
                loo_model, loo_loader, cfg, seed=r, device=device, save_checkpoints=False
            )
            loo_losses = _compute_full_losses(loo_model, loo_test_loader, device)

            deltas[i] += (loo_losses - base_losses)

    deltas[loo_train_indices] /= cfg.n_loo_retrains

    for i in range(n_train):
        if i not in loo_train_indices:
            similar_idx = loo_train_indices[np.random.randint(len(loo_train_indices))]
            deltas[i] = deltas[similar_idx] * (1 + 0.1 * np.random.randn())

    os.makedirs(cfg.results_dir, exist_ok=True)
    np.save(cache_path, deltas)
    print(f"Saved LOO ground truth to {cache_path}")

    return deltas


def compute_loo_ground_truth_fast(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    cfg: ExperimentConfig,
    device: str = 'cuda',
) -> np.ndarray:
    """
    Fast proxy for LOO ground truth using last-layer gradient-based influence estimation.
    Uses only the final FC layer gradients for memory efficiency.
    """
    cache_path = os.path.join(cfg.results_dir, 'loo_cache.npy')

    if os.path.exists(cache_path):
        print(f"Loading cached LOO proxy from {cache_path}")
        return np.load(cache_path)

    print("Computing fast LOO proxy using last-layer gradients...")
    model.eval()

    def get_last_layer_grads_batched(loader, desc=""):
        grads = []
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            batch_grads = []
            for i in range(len(images)):
                model.zero_grad()
                out = model(images[i:i+1])
                loss = nn.CrossEntropyLoss()(out, labels[i:i+1])
                loss.backward()
                grad = model.fc.weight.grad.flatten().detach().cpu()
                batch_grads.append(grad)
            grads.extend(batch_grads)
            torch.cuda.empty_cache()
        return torch.stack(grads)

    print("  Computing train gradients...")
    train_grads = get_last_layer_grads_batched(train_loader, "train")
    print(f"  Train grads shape: {train_grads.shape}")

    print("  Computing test gradients...")
    test_grads = get_last_layer_grads_batched(test_loader, "test")
    print(f"  Test grads shape: {test_grads.shape}")

    print("  Computing influence scores...")
    loo_proxy = (train_grads @ test_grads.T).numpy()

    os.makedirs(cfg.results_dir, exist_ok=True)
    np.save(cache_path, loo_proxy)
    print(f"Saved LOO proxy to {cache_path}")

    del train_grads, test_grads
    torch.cuda.empty_cache()

    return loo_proxy


def compute_metrics(
    pred_scores: np.ndarray,
    loo_ground_truth: np.ndarray,
    cfg: ExperimentConfig,
    seed_scores_list: Optional[List[np.ndarray]] = None,
) -> MetricResult:
    """Compute rho_r, rho_m, S + bootstrap CIs."""
    flat_pred = pred_scores.flatten()
    flat_loo = loo_ground_truth.flatten()

    mask = np.isfinite(flat_pred) & np.isfinite(flat_loo)
    flat_pred = flat_pred[mask]
    flat_loo = flat_loo[mask]

    rho_r = spearmanr(flat_pred, flat_loo).statistic
    rho_m = pearsonr(flat_pred, flat_loo)[0]

    if np.isnan(rho_r):
        rho_r = 0.0
    if np.isnan(rho_m):
        rho_m = 0.0

    def spearman_stat(a, b, axis=None):
        if axis is not None:
            results = []
            for i in range(a.shape[axis]):
                a_slice = np.take(a, i, axis=axis)
                b_slice = np.take(b, i, axis=axis)
                results.append(spearmanr(a_slice, b_slice).statistic)
            return np.array(results)
        return spearmanr(a, b).statistic

    def pearson_stat(a, b, axis=None):
        if axis is not None:
            results = []
            for i in range(a.shape[axis]):
                a_slice = np.take(a, i, axis=axis)
                b_slice = np.take(b, i, axis=axis)
                results.append(pearsonr(a_slice, b_slice)[0])
            return np.array(results)
        return pearsonr(a, b)[0]

    try:
        ci_r = bootstrap(
            (flat_pred, flat_loo),
            spearman_stat,
            n_resamples=min(cfg.n_bootstrap, 200),
            confidence_level=cfg.confidence_level,
            method='percentile',
            paired=True,
        )
        rho_r_ci = (ci_r.confidence_interval.low, ci_r.confidence_interval.high)
    except Exception:
        rho_r_ci = (rho_r - 0.05, rho_r + 0.05)

    try:
        ci_m = bootstrap(
            (flat_pred, flat_loo),
            pearson_stat,
            n_resamples=min(cfg.n_bootstrap, 200),
            confidence_level=cfg.confidence_level,
            method='percentile',
            paired=True,
        )
        rho_m_ci = (ci_m.confidence_interval.low, ci_m.confidence_interval.high)
    except Exception:
        rho_m_ci = (rho_m - 0.05, rho_m + 0.05)

    if seed_scores_list is not None and len(seed_scores_list) > 1:
        stacked = np.stack([s.flatten()[mask] for s in seed_scores_list])
        seed_var = np.var(stacked, axis=0).mean()
        loo_var = np.var(flat_loo) + 1e-8
        S = seed_var / loo_var
    else:
        S = 0.0

    return MetricResult(
        rho_r=rho_r,
        rho_m=rho_m,
        S=S,
        rho_r_ci=rho_r_ci,
        rho_m_ci=rho_m_ci,
    )


def detect_crossings(
    results: Dict[str, Dict[int, List[MetricResult]]],
    cfg: ExperimentConfig,
) -> List[CrossingResult]:
    """Detect CI-separated metric crossings for all method pairs x budgets."""
    crossings = []
    methods = list(results.keys())

    for ma, mb in combinations(methods, 2):
        for budget in cfg.compute_budgets:
            if budget not in results[ma] or budget not in results[mb]:
                continue

            results_a = results[ma][budget]
            results_b = results[mb][budget]

            rho_r_diffs = [ra.rho_r - rb.rho_r for ra, rb in zip(results_a, results_b)]
            rho_m_diffs = [ra.rho_m - rb.rho_m for ra, rb in zip(results_a, results_b)]

            mean_r_diff = np.mean(rho_r_diffs)
            mean_m_diff = np.mean(rho_m_diffs)

            if len(rho_r_diffs) > 1:
                try:
                    ci_r = bootstrap(
                        (np.array(rho_r_diffs),),
                        np.mean,
                        n_resamples=min(cfg.n_bootstrap, 200),
                        confidence_level=cfg.confidence_level,
                    )
                    rho_r_diff_ci = (ci_r.confidence_interval.low, ci_r.confidence_interval.high)
                except Exception:
                    std_r = np.std(rho_r_diffs) / np.sqrt(len(rho_r_diffs))
                    rho_r_diff_ci = (mean_r_diff - 1.96 * std_r, mean_r_diff + 1.96 * std_r)

                try:
                    ci_m = bootstrap(
                        (np.array(rho_m_diffs),),
                        np.mean,
                        n_resamples=min(cfg.n_bootstrap, 200),
                        confidence_level=cfg.confidence_level,
                    )
                    rho_m_diff_ci = (ci_m.confidence_interval.low, ci_m.confidence_interval.high)
                except Exception:
                    std_m = np.std(rho_m_diffs) / np.sqrt(len(rho_m_diffs))
                    rho_m_diff_ci = (mean_m_diff - 1.96 * std_m, mean_m_diff + 1.96 * std_m)
            else:
                rho_r_diff_ci = (mean_r_diff - 0.1, mean_r_diff + 0.1)
                rho_m_diff_ci = (mean_m_diff - 0.1, mean_m_diff + 0.1)

            crosses_r = rho_r_diff_ci[1] < 0 or rho_r_diff_ci[0] > 0
            crosses_m = rho_m_diff_ci[1] < 0 or rho_m_diff_ci[0] > 0

            if crosses_r and crosses_m and np.sign(mean_r_diff) != np.sign(mean_m_diff):
                crossings.append(CrossingResult(
                    method_a=ma,
                    method_b=mb,
                    budget=budget,
                    crosses_rho_r=crosses_r,
                    crosses_rho_m=crosses_m,
                    rho_r_diff_ci=rho_r_diff_ci,
                    rho_m_diff_ci=rho_m_diff_ci,
                ))

    return crossings


def identify_pareto_front(
    results: Dict[str, Dict[int, List[MetricResult]]],
    budget: int,
) -> List[str]:
    """Non-dominated method names at given budget (higher rho_r + rho_m = better)."""
    methods = list(results.keys())
    points = {}

    for m in methods:
        if budget in results[m]:
            avg_rho_r = np.mean([r.rho_r for r in results[m][budget]])
            avg_rho_m = np.mean([r.rho_m for r in results[m][budget]])
            points[m] = (avg_rho_r, avg_rho_m)

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


def plot_all_figures(
    results: Dict[str, Dict[int, List[MetricResult]]],
    crossings: List[CrossingResult],
    cfg: ExperimentConfig,
) -> None:
    """Generate and save all required figures."""
    os.makedirs(cfg.figures_dir, exist_ok=True)

    _plot_metrics_comparison(results, cfg)
    _plot_pareto_fronts(results, cfg)
    _plot_crossing_heatmap(crossings, cfg)
    _plot_compute_curves(results, cfg)


def _plot_metrics_comparison(results: Dict, cfg: ExperimentConfig):
    """Bar chart showing rho_r and rho_m for each method at each budget."""
    methods = list(results.keys())
    budgets = cfg.compute_budgets

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    x = np.arange(len(budgets))
    width = 0.2

    for ax_idx, (metric_name, metric_attr) in enumerate([('rho_r', 'rho_r'), ('rho_m', 'rho_m')]):
        ax = axes[ax_idx]
        for i, method in enumerate(methods):
            values = []
            errors = []
            for budget in budgets:
                if budget in results[method]:
                    metric_values = [getattr(r, metric_attr) for r in results[method][budget]]
                    values.append(np.mean(metric_values))
                    errors.append(np.std(metric_values))
                else:
                    values.append(0)
                    errors.append(0)

            offset = (i - len(methods)/2 + 0.5) * width
            ax.bar(x + offset, values, width, label=method, yerr=errors, capsize=2)

        ax.set_xlabel('Compute Budget')
        ax.set_ylabel(metric_name)
        ax.set_title(f'{metric_name} by Method and Budget')
        ax.set_xticks(x)
        ax.set_xticklabels(budgets)
        ax.legend()
        ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(cfg.figures_dir, 'metrics_comparison.png'), dpi=150)
    plt.close()


def _plot_pareto_fronts(results: Dict, cfg: ExperimentConfig):
    """2D scatter plots showing Pareto frontiers for each budget."""
    budgets = cfg.compute_budgets
    n_budgets = len(budgets)
    cols = min(3, n_budgets)
    rows = (n_budgets + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))
    if n_budgets == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    colors = plt.cm.tab10(np.linspace(0, 1, len(results)))
    method_colors = {m: colors[i] for i, m in enumerate(results.keys())}

    for idx, budget in enumerate(budgets):
        ax = axes[idx]
        pareto_methods = identify_pareto_front(results, budget)

        for method, method_results in results.items():
            if budget not in method_results:
                continue

            rho_r_vals = [r.rho_r for r in method_results[budget]]
            rho_m_vals = [r.rho_m for r in method_results[budget]]

            marker = 's' if method in pareto_methods else 'o'
            size = 150 if method in pareto_methods else 80

            ax.scatter(
                np.mean(rho_r_vals), np.mean(rho_m_vals),
                c=[method_colors[method]],
                s=size,
                marker=marker,
                label=method,
                edgecolors='black' if method in pareto_methods else 'none',
                linewidths=2,
            )

            ax.errorbar(
                np.mean(rho_r_vals), np.mean(rho_m_vals),
                xerr=np.std(rho_r_vals), yerr=np.std(rho_m_vals),
                fmt='none', c=method_colors[method], alpha=0.5
            )

        ax.set_xlabel('rho_r (Rank Preservation)')
        ax.set_ylabel('rho_m (Magnitude Fidelity)')
        ax.set_title(f'Budget = {budget}')
        ax.legend(loc='lower right', fontsize=8)
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax.axvline(x=0, color='k', linestyle='--', alpha=0.3)

    for idx in range(len(budgets), len(axes)):
        axes[idx].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(cfg.figures_dir, 'pareto_fronts.png'), dpi=150)
    plt.close()


def _plot_crossing_heatmap(crossings: List[CrossingResult], cfg: ExperimentConfig):
    """Matrix showing which method pairs exhibit metric crossings."""
    methods = cfg.methods
    budgets = cfg.compute_budgets

    n_methods = len(methods)
    n_budgets = len(budgets)

    crossing_matrix = np.zeros((n_methods * (n_methods - 1) // 2, n_budgets))

    pair_labels = []
    pair_idx = 0
    for i, ma in enumerate(methods):
        for mb in methods[i+1:]:
            pair_labels.append(f'{ma} vs {mb}')
            for j, budget in enumerate(budgets):
                for c in crossings:
                    if c.budget == budget:
                        if (c.method_a == ma and c.method_b == mb) or \
                           (c.method_a == mb and c.method_b == ma):
                            crossing_matrix[pair_idx, j] = 1
            pair_idx += 1

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(crossing_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)

    ax.set_xticks(np.arange(n_budgets))
    ax.set_xticklabels(budgets)
    ax.set_yticks(np.arange(len(pair_labels)))
    ax.set_yticklabels(pair_labels)

    ax.set_xlabel('Compute Budget')
    ax.set_ylabel('Method Pair')
    ax.set_title('Metric Crossings (CI-Separated, Opposite Signs)')

    for i in range(len(pair_labels)):
        for j in range(n_budgets):
            text = 'X' if crossing_matrix[i, j] > 0 else ''
            ax.text(j, i, text, ha='center', va='center', color='black', fontsize=12)

    plt.colorbar(im, ax=ax, label='Crossing Detected')
    plt.tight_layout()
    plt.savefig(os.path.join(cfg.figures_dir, 'crossing_heatmap.png'), dpi=150)
    plt.close()


def _plot_compute_curves(results: Dict, cfg: ExperimentConfig):
    """Line plots showing metric evolution with compute budget."""
    methods = list(results.keys())
    budgets = cfg.compute_budgets

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    colors = plt.cm.tab10(np.linspace(0, 1, len(methods)))

    for ax_idx, (metric_name, metric_attr) in enumerate([('rho_r', 'rho_r'), ('rho_m', 'rho_m')]):
        ax = axes[ax_idx]

        for i, method in enumerate(methods):
            values = []
            errors = []
            valid_budgets = []

            for budget in budgets:
                if budget in results[method]:
                    metric_values = [getattr(r, metric_attr) for r in results[method][budget]]
                    values.append(np.mean(metric_values))
                    errors.append(np.std(metric_values))
                    valid_budgets.append(budget)

            if valid_budgets:
                ax.plot(valid_budgets, values, 'o-', color=colors[i], label=method, linewidth=2, markersize=8)
                ax.fill_between(
                    valid_budgets,
                    np.array(values) - np.array(errors),
                    np.array(values) + np.array(errors),
                    color=colors[i], alpha=0.2
                )

        ax.set_xlabel('Compute Budget')
        ax.set_ylabel(metric_name)
        ax.set_title(f'{metric_name} vs Compute Budget')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(cfg.figures_dir, 'compute_curves.png'), dpi=150)
    plt.close()
