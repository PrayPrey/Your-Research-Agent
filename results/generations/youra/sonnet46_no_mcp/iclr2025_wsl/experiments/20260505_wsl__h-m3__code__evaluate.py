import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
from scipy.stats import spearmanr
from torch.utils.data import DataLoader

logger = logging.getLogger(__name__)


def bootstrap_spearman_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """Bootstrap 95% CI for Spearman rho.
    Returns: (median_rho, ci_lower_2.5pct, ci_upper_97.5pct)
    """
    rng = np.random.default_rng(seed)
    n = len(y_true)
    boot_rhos = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        rho_val = spearmanr(y_true[idx], y_pred[idx]).statistic
        if not np.isnan(rho_val):
            boot_rhos.append(rho_val)
    if not boot_rhos:
        return float("nan"), float("nan"), float("nan")
    return (float(np.median(boot_rhos)),
            float(np.percentile(boot_rhos, 2.5)),
            float(np.percentile(boot_rhos, 97.5)))


def evaluate_flat_encoder(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    n_resamples: int = 1000,
) -> Dict:
    """Evaluate FlatMLP or DeepSets (flat) encoder.
    Batch format: (flat_w: Tensor(B,D), acc: Tensor(B,)) from h-m1 WeightDataset.
    """
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for flat_w, acc in loader:
            flat_w = flat_w.to(device)
            _, pred = model(flat_w)
            all_preds.extend(pred.squeeze().cpu().numpy().tolist())
            all_labels.extend(acc.numpy().tolist())

    y_true = np.array(all_labels)
    y_pred = np.array(all_preds)
    point_rho = spearmanr(y_true, y_pred).statistic
    median_rho, ci_lower, ci_upper = bootstrap_spearman_ci(y_true, y_pred, n_resamples)
    logger.info(f"FlatEncoder: rho={point_rho:.4f} (95% CI [{ci_lower:.4f}, {ci_upper:.4f}])")
    return {
        "rho": float(point_rho),
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
        "preds": y_pred,
        "labels": y_true,
    }


def evaluate_deep_sets_encoder(
    model: "DeepSetsWithHead",
    loader: DataLoader,
    device: torch.device,
    weight_shapes: List[tuple],
    n_resamples: int = 1000,
) -> Dict:
    """Evaluate DeepSets encoder.
    Batch format: (flat_w: Tensor(B,D), acc: Tensor(B,)) — reshape via prepare_flat_elements.
    """
    from train import prepare_flat_elements_batch

    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for flat_w, acc in loader:
            flat_w = flat_w.to(device)
            x_elements = prepare_flat_elements_batch(flat_w, weight_shapes).to(device)
            _, pred = model(x_elements)
            all_preds.extend(pred.squeeze().cpu().numpy().tolist())
            all_labels.extend(acc.numpy().tolist())

    y_true = np.array(all_labels)
    y_pred = np.array(all_preds)
    point_rho = spearmanr(y_true, y_pred).statistic
    median_rho, ci_lower, ci_upper = bootstrap_spearman_ci(y_true, y_pred, n_resamples)
    logger.info(f"DeepSetsEncoder: rho={point_rho:.4f} (95% CI [{ci_lower:.4f}, {ci_upper:.4f}])")
    return {
        "rho": float(point_rho),
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
        "preds": y_pred,
        "labels": y_true,
    }


def evaluate_nfn_encoder(
    model: "NFNWithHead",
    loader: DataLoader,
    device: torch.device,
    n_resamples: int = 1000,
) -> Dict:
    """Evaluate NFN encoder.
    Batch format: (weight_list: List[Tensor(B,...)], flat_w: Tensor(B,D), acc: Tensor(B,))
    """
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for batch in loader:
            weight_list, flat_w, acc = batch
            weight_list = [w.to(device) for w in weight_list]
            _, pred = model(weight_list)
            all_preds.extend(pred.squeeze().cpu().numpy().tolist())
            all_labels.extend(acc.numpy().tolist())

    y_true = np.array(all_labels)
    y_pred = np.array(all_preds)
    point_rho = spearmanr(y_true, y_pred).statistic
    median_rho, ci_lower, ci_upper = bootstrap_spearman_ci(y_true, y_pred, n_resamples)
    logger.info(f"NFNEncoder: rho={point_rho:.4f} (95% CI [{ci_lower:.4f}, {ci_upper:.4f}])")
    return {
        "rho": float(point_rho),
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
        "preds": y_pred,
        "labels": y_true,
    }


def compute_delta_rho_ci(
    nfn_preds: np.ndarray,
    flat_preds: np.ndarray,
    labels: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """Paired bootstrap CI for delta_rho = rho(NFN) - rho(flat).
    Returns: (delta_rho, ci_lower_2.5pct, ci_upper_97.5pct)
    """
    rng = np.random.default_rng(seed)
    n = len(labels)
    boot_deltas = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        rho_nfn = spearmanr(labels[idx], nfn_preds[idx]).statistic
        rho_flat = spearmanr(labels[idx], flat_preds[idx]).statistic
        delta = rho_nfn - rho_flat
        if not np.isnan(delta):
            boot_deltas.append(delta)

    # Point estimate on full arrays
    delta_rho = (spearmanr(labels, nfn_preds).statistic
                 - spearmanr(labels, flat_preds).statistic)
    if not boot_deltas:
        return float(delta_rho), float("nan"), float("nan")
    ci_lower = float(np.percentile(boot_deltas, 2.5))
    ci_upper = float(np.percentile(boot_deltas, 97.5))
    logger.info(f"delta_rho={delta_rho:.4f} (95% CI [{ci_lower:.4f}, {ci_upper:.4f}])")
    return float(delta_rho), ci_lower, ci_upper


def compute_tier_analysis(
    flat_preds: np.ndarray,
    nfn_preds: np.ndarray,
    deep_sets_preds: np.ndarray,
    labels: np.ndarray,
) -> Dict:
    """Partition test set into accuracy terciles; compute delta_rho(NFN vs flat) per tier."""
    thresholds = np.percentile(labels, [33.3, 66.7])
    low_mask  = labels <= thresholds[0]
    mid_mask  = (labels > thresholds[0]) & (labels <= thresholds[1])
    high_mask = labels > thresholds[1]

    result = {}
    for tier, mask in [("low", low_mask), ("mid", mid_mask), ("high", high_mask)]:
        if mask.sum() < 2:
            result[tier] = float("nan")
            result[f"{tier}_n"] = int(mask.sum())
            continue
        rho_nfn = spearmanr(labels[mask], nfn_preds[mask]).statistic
        rho_flat = spearmanr(labels[mask], flat_preds[mask]).statistic
        result[tier] = float(rho_nfn - rho_flat)
        result[f"{tier}_n"] = int(mask.sum())

    logger.info(f"Tier analysis: low={result.get('low',0):.4f}, mid={result.get('mid',0):.4f}, high={result.get('high',0):.4f}")
    return result


def check_hm3_gate(results: Dict) -> Tuple[bool, bool]:
    """Evaluate P1 (primary gate) and P2 (symmetry spectrum).
    P1: delta_rho(MNIST) >= 0.05 AND ci_lower_mnist > 0
        AND (delta_rho(CIFAR) > 0 AND ci_lower_cifar > 0 if CIFAR available)
    P2: rho(flat) < rho(deep_sets) < rho(NFN) on MNIST-CNN
    Returns: (p1_pass, p2_pass)
    """
    dm = results.get("delta_metrics", {})
    enc = results.get("encoders", {})

    delta_mnist = dm.get("delta_rho_mnist", float("nan"))
    ci_lower_mnist = dm.get("ci_lower_mnist", float("nan"))
    delta_cifar = dm.get("delta_rho_cifar", None)
    ci_lower_cifar = dm.get("ci_lower_cifar", None)

    p1_mnist = (not np.isnan(delta_mnist) and delta_mnist >= 0.05
                and not np.isnan(ci_lower_mnist) and ci_lower_mnist > 0)
    if delta_cifar is not None and not np.isnan(delta_cifar):
        p1_cifar = delta_cifar > 0 and ci_lower_cifar is not None and ci_lower_cifar > 0
    else:
        p1_cifar = True  # CIFAR unavailable — not required for gate

    p1_pass = p1_mnist and p1_cifar

    # P2: rho ordering on MNIST
    flat_rho = enc.get("flat_mlp", {}).get("mnist_cnn", {}).get("rho", float("nan"))
    ds_rho   = enc.get("deep_sets", {}).get("mnist_cnn", {}).get("rho", float("nan"))
    nfn_rho  = enc.get("nfn", {}).get("mnist_cnn", {}).get("rho", float("nan"))
    p2_pass = (not any(np.isnan(v) for v in [flat_rho, ds_rho, nfn_rho])
               and flat_rho < ds_rho < nfn_rho)

    logger.info(f"Gate P1: {p1_pass} (delta_mnist={delta_mnist:.4f}, ci_lower={ci_lower_mnist:.4f})")
    logger.info(f"Gate P2: {p2_pass} (flat={flat_rho:.4f} < ds={ds_rho:.4f} < nfn={nfn_rho:.4f})")
    return p1_pass, p2_pass


def save_results(results: Dict, cfg) -> None:
    """Save full results dict as h-m3_results.json."""
    # Convert numpy arrays to lists for JSON serialization
    def _convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert(i) for i in obj]
        return obj

    clean = _convert(results)
    out_path = Path(cfg.results_dir) / "h-m3_results.json"
    with open(out_path, "w") as f:
        json.dump(clean, f, indent=2)
    logger.info(f"Results saved to {out_path}")
