"""Temperature optimization via L-BFGS-B for H-M2."""

import numpy as np
from scipy.optimize import minimize
from scipy.special import softmax
from config import T_BOUNDS, T_INIT, EPS


def nll_loss(T, logits, labels):
    """Negative log-likelihood loss for temperature scaling.

    Args:
        T: [1] temperature parameter
        logits: [N, C] raw scores (padded with -inf)
        labels: [N] correct class indices

    Returns:
        float: mean NLL
    """
    scaled = logits / T[0]
    probs = softmax(scaled, axis=1)
    nll = -np.mean(np.log(probs[np.arange(len(labels)), labels] + EPS))
    return nll


def optimize_temperature(logits, labels, bounds=T_BOUNDS, t_init=T_INIT):
    """Optimize temperature via L-BFGS-B.

    Args:
        logits: [N, C] raw scores
        labels: [N] correct class indices
        bounds: (min, max) temperature bounds
        t_init: initial temperature

    Returns:
        float: optimal temperature
    """
    result = minimize(
        nll_loss,
        x0=[t_init],
        args=(logits, labels),
        method='L-BFGS-B',
        bounds=[bounds],
    )
    return float(result.x[0])


def optimize_temperature_per_cluster(logits_by_cluster, labels_by_cluster, bounds=T_BOUNDS, t_init=T_INIT):
    """Optimize temperature for each cluster independently.

    Returns:
        dict[int, float]: {cluster_id: optimal_T}
    """
    optimal_temps = {}
    for cid in logits_by_cluster:
        if len(logits_by_cluster[cid]) > 0:
            optimal_temps[cid] = optimize_temperature(
                logits_by_cluster[cid], labels_by_cluster[cid], bounds, t_init
            )
    return optimal_temps


def cross_validate_temperatures(logits_by_cluster, labels_by_cluster, splits_by_cluster, bounds=T_BOUNDS, t_init=T_INIT):
    """Cross-validate temperature optimization per cluster.

    Returns:
        dict[int, list[float]]: {cluster_id: [T_fold1, ..., T_fold5]}
    """
    fold_temps = {}
    for cid, folds in splits_by_cluster.items():
        if len(folds) == 0:
            continue
        temps = []
        for train_idx, val_idx in folds:
            T = optimize_temperature(
                logits_by_cluster[cid][train_idx],
                labels_by_cluster[cid][train_idx],
                bounds, t_init
            )
            temps.append(T)
        fold_temps[cid] = temps
    return fold_temps
