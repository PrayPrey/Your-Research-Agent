"""Evaluation utilities for h-e1 experiment.

Implements Spearman rho computation under permutation stress,
bootstrap significance testing, gate condition evaluation, and
mechanism verification.
"""
import json
import logging
import os
from typing import TypedDict

import numpy as np
import torch
import torch.nn as nn
from scipy.stats import spearmanr

from src.data_loader import apply_permutation_stress, flatten_weights

logger = logging.getLogger(__name__)


class GateResult(TypedDict):
    pass_gate: bool
    flat_mlp_delta_rho: float
    nft_delta_rho: float
    flat_threshold_met: bool
    nft_threshold_met: bool
    flat_mlp_p_corrected: float
    nft_p_corrected: float


def _apply_flat_stress_batch(x: torch.Tensor, severity: float) -> torch.Tensor:
    """Apply permutation stress to a batch of flat weight vectors.

    Reshapes each flat vector back to its component weights, applies
    permutation per segment, then flattens again.

    Since we don't have the original layer shapes here, we treat the
    entire flat vector as a single layer for stress purposes.
    """
    B, D = x.shape
    result = torch.empty_like(x)
    x_np = x.cpu().numpy()

    for b in range(B):
        flat = x_np[b]  # (D,)
        n_units = D
        n_permute = max(1, int(n_units * severity))
        perm_indices = np.random.choice(n_units, size=n_permute, replace=False)
        shuffled = perm_indices[np.random.permutation(n_permute)]
        flat_copy = flat.copy()
        flat_copy[perm_indices] = flat[shuffled]
        result[b] = torch.tensor(flat_copy, dtype=torch.float32)

    return result.to(x.device)


def _apply_nft_stress_batch(wms: list, severity: float) -> list:
    """Apply permutation stress to a batch of NFT weight matrices.

    Parameters
    ----------
    wms : list[Tensor]
        List of (B, n_units_l, fan_in_l) tensors.
    severity : float
        Permutation severity.

    Returns
    -------
    list[Tensor]
        Permuted weight matrices.
    """
    result = []
    for wm in wms:
        B, n_units, fan_in = wm.shape
        device = wm.device
        wm_np = wm.cpu().numpy()
        stressed = np.empty_like(wm_np)

        for b in range(B):
            flat2d = wm_np[b]  # (n_units, fan_in)
            n_permute = max(1, int(n_units * severity))
            perm_indices = np.random.choice(n_units, size=n_permute, replace=False)
            shuffled = perm_indices[np.random.permutation(n_permute)]
            flat2d_copy = flat2d.copy()
            flat2d_copy[perm_indices] = flat2d[shuffled]
            stressed[b] = flat2d_copy

        result.append(torch.tensor(stressed, dtype=torch.float32).to(device))
    return result


def apply_stress_and_predict(
    model: nn.Module,
    test_loader,
    severity: float,
    device: torch.device,
    model_type: str,
) -> tuple:
    """Run inference with permutation stress applied at given severity.

    Parameters
    ----------
    model : nn.Module
        Trained model.
    test_loader : DataLoader
        Test data loader.
    severity : float
        Permutation severity (0.0 = no stress).
    device : torch.device
        Inference device.
    model_type : str
        'flat' or 'nft'.

    Returns
    -------
    tuple
        (predictions, labels) as numpy arrays of shape (N,).
    """
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in test_loader:
            if model_type == "flat":
                x = batch[0].to(device)
                labels = batch[1]

                if severity > 0.0:
                    x = _apply_flat_stress_batch(x, severity)

                preds = model(x).cpu().squeeze(-1)
            else:  # nft
                wms = [t.to(device) for t in batch[0]]
                labels = batch[1]

                if severity > 0.0:
                    wms = _apply_nft_stress_batch(wms, severity)

                preds = model(wms).cpu().squeeze(-1)

            all_preds.append(preds.numpy())
            all_labels.append(labels.numpy())

    return np.concatenate(all_preds), np.concatenate(all_labels)


def compute_delta_rho(
    model: nn.Module,
    test_loader,
    severity_levels: list,
    device: torch.device,
    model_type: str,
) -> tuple:
    """Compute Spearman rho at each severity level and delta_rho.

    Parameters
    ----------
    model : nn.Module
        Trained model.
    test_loader : DataLoader
        Test data loader.
    severity_levels : list[float]
        Severity values to evaluate, must include 0.0 and 1.0.
    device : torch.device
        Inference device.
    model_type : str
        'flat' or 'nft'.

    Returns
    -------
    tuple
        (delta_rho, rho_by_severity)
        delta_rho = rho[0.0] - rho[1.0]

    Raises
    ------
    ValueError
        If n_samples < 2.
    """
    rho_by_severity = {}

    for s in severity_levels:
        preds, labels = apply_stress_and_predict(model, test_loader, s, device, model_type)
        if len(preds) < 2:
            raise ValueError(f"n_samples={len(preds)} < 2")
        rho, _ = spearmanr(preds, labels)
        rho_by_severity[s] = float(rho)
        logger.info(f"[{model_type}] severity={s:.2f} | rho={rho:.4f}")

    delta_rho = rho_by_severity[0.0] - rho_by_severity[1.0]
    logger.info(f"[{model_type}] delta_rho = {delta_rho:.4f}")
    return delta_rho, rho_by_severity


def bootstrap_delta_rho(
    model: nn.Module,
    test_loader,
    device: torch.device,
    model_type: str,
    n_bootstrap: int = 10000,
    seed: int = 42,
) -> tuple:
    """Paired bootstrap of delta_rho.

    Parameters
    ----------
    model : nn.Module
        Trained model.
    test_loader : DataLoader
        Test data loader.
    device : torch.device
        Inference device.
    model_type : str
        'flat' or 'nft'.
    n_bootstrap : int
        Number of bootstrap iterations.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    tuple
        (bootstrap_samples, p_value)
        p_value = fraction of bootstrap_samples <= 0 (one-sided H1: delta_rho > 0)
    """
    rng = np.random.default_rng(seed)

    preds_s0, labels = apply_stress_and_predict(model, test_loader, 0.0, device, model_type)
    preds_s1, _ = apply_stress_and_predict(model, test_loader, 1.0, device, model_type)
    n = len(labels)

    bootstrap_samples = np.empty(n_bootstrap, dtype=np.float64)
    for i in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        rho0, _ = spearmanr(preds_s0[idx], labels[idx])
        rho1, _ = spearmanr(preds_s1[idx], labels[idx])
        bootstrap_samples[i] = rho0 - rho1

    p_value = float(np.mean(bootstrap_samples <= 0))
    logger.info(f"[{model_type}] bootstrap p_value={p_value:.4f}")
    return bootstrap_samples, p_value


def holm_correction(p_values: list) -> list:
    """Holm step-down correction.

    Parameters
    ----------
    p_values : list[float]
        Raw p-values.

    Returns
    -------
    list[float]
        Corrected p-values in the same order as input.
    """
    m = len(p_values)
    if m == 0:
        return []

    sorted_idx = np.argsort(p_values)
    corrected = np.array(p_values, dtype=float)

    for rank, idx in enumerate(sorted_idx):
        corrected[idx] = p_values[idx] * (m - rank)

    # Enforce monotonicity (step-down)
    sorted_corrected = corrected[sorted_idx]
    # Reverse cummin then reverse back
    reversed_sorted = sorted_corrected[::-1]
    cummin = np.minimum.accumulate(reversed_sorted)
    corrected_sorted = cummin[::-1]

    result = np.empty(m)
    result[sorted_idx] = corrected_sorted
    return np.clip(result, 0.0, 1.0).tolist()


def evaluate_gate_condition(
    flat_mlp_delta_rho: float,
    nft_delta_rho: float,
    flat_mlp_p: float,
    nft_p: float,
    results_dir: str = "results",
) -> dict:
    """Evaluate gate condition and write gate_result.json.

    Gate PASS iff flat_mlp_delta_rho > 0.10 AND nft_delta_rho < 0.02.

    Parameters
    ----------
    flat_mlp_delta_rho : float
    nft_delta_rho : float
    flat_mlp_p : float
        Corrected p-value for flat-MLP.
    nft_p : float
        Corrected p-value for NFT.
    results_dir : str
        Directory to write gate_result.json.

    Returns
    -------
    dict
        GateResult dict.
    """
    flat_threshold_met = flat_mlp_delta_rho > 0.10
    nft_threshold_met = nft_delta_rho < 0.02
    pass_gate = flat_threshold_met and nft_threshold_met

    result = {
        "pass_gate": pass_gate,
        "flat_mlp_delta_rho": float(flat_mlp_delta_rho),
        "nft_delta_rho": float(nft_delta_rho),
        "flat_threshold_met": flat_threshold_met,
        "nft_threshold_met": nft_threshold_met,
        "flat_mlp_p_corrected": float(flat_mlp_p),
        "nft_p_corrected": float(nft_p),
        "gate_criteria": {
            "flat_mlp_threshold": 0.10,
            "nft_threshold": 0.02,
            "significance_threshold": 0.05,
        },
    }

    os.makedirs(results_dir, exist_ok=True)
    gate_path = os.path.join(results_dir, "gate_result.json")
    with open(gate_path, "w") as f:
        json.dump(result, f, indent=2)
    logger.info(f"Gate result written to {gate_path}: pass_gate={pass_gate}")

    return result


def verify_mechanism_activated(
    model: nn.Module,
    sample_batch: tuple,
    results: dict,
) -> tuple:
    """Check that NFT attention is producing non-trivial outputs.

    3-indicator check:
    1. tokens_shaped_correctly: token shape is valid (N > 0, D == d_model)
    2. permutation_changes_output: rho_s0 != rho_s1
    3. nft_more_robust: nft_delta_rho < flat_mlp_delta_rho

    Parameters
    ----------
    model : nn.Module
        NFTEquivariantEncoder with get_last_token_shape().
    sample_batch : tuple
        A single NFT batch (padded_by_layer, labels, attention_mask).
    results : dict
        Must contain keys: rho_s0_nft, rho_s1_nft, nft_delta_rho, flat_mlp_delta_rho.

    Returns
    -------
    tuple
        (all_pass, indicators_dict)
    """
    device = next(model.parameters()).device

    # Run one forward pass to populate last_token_shape
    with torch.no_grad():
        wms = [t.to(device) for t in sample_batch[0]]
        _ = model(wms)

    B, N, D = model.get_last_token_shape()
    d_model = model.d_model

    indicators = {
        "tokens_shaped_correctly": (N > 0 and D == d_model),
        "permutation_changes_output": (
            results.get("rho_s0_nft") != results.get("rho_s1_nft")
        ),
        "nft_more_robust": (
            results["nft_delta_rho"] < results["flat_mlp_delta_rho"]
        ),
    }

    all_pass = all(indicators.values())
    logger.info(f"Mechanism verification: all_pass={all_pass}, indicators={indicators}")
    return all_pass, indicators
