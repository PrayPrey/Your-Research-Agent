"""Evaluation utilities for H-M1 experiment.

Extends H-E1 evaluation for 6-encoder suite:
- Per-encoder Delta_rho at each severity x seed (72 rows)
- Mediation Delta_R2: R2(NFT-base) - R2(flat-MLP+aug) >= 0.10
- Bootstrap CI (n=10,000) per encoder per severity
- Holm-corrected p-values across 6 encoders
- Gate v2: dual-condition (Delta_rho < 0.02 AND Delta_R2 >= 0.10)
- verify_mechanism_activated() with 5 boolean indicators (C-5-2)
"""
import json
import logging
import os
from datetime import datetime

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from scipy.stats import spearmanr

from src.config import ENCODER_CONFIG, ExperimentConfig, GateConfig
from src.models import build_encoder
from src.train import load_checkpoint

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# H-E1 stress helpers (ported verbatim)
# ---------------------------------------------------------------------------

def _apply_flat_stress_batch(x: torch.Tensor, severity: float) -> torch.Tensor:
    """Apply permutation stress to flat weight batch."""
    B, D = x.shape
    result = torch.empty_like(x)
    x_np = x.cpu().numpy()
    for b in range(B):
        flat = x_np[b].copy()
        n_units = D
        n_permute = max(1, int(n_units * severity))
        perm_indices = np.random.choice(n_units, size=n_permute, replace=False)
        shuffled = perm_indices[np.random.permutation(n_permute)]
        flat[perm_indices] = x_np[b][shuffled]
        result[b] = torch.tensor(flat, dtype=torch.float32)
    return result.to(x.device)


def _apply_nft_stress_batch(wms: list, severity: float) -> list:
    """Apply permutation stress to NFT weight matrix batch."""
    result = []
    for wm in wms:
        B, n_units, fan_in = wm.shape
        wm_np = wm.cpu().numpy()
        stressed = wm_np.copy()
        n_permute = max(1, int(n_units * severity))
        for b in range(B):
            perm_indices = np.random.choice(n_units, size=n_permute, replace=False)
            shuffled = perm_indices[np.random.permutation(n_permute)]
            stressed[b][perm_indices] = wm_np[b][shuffled]
        result.append(torch.tensor(stressed, dtype=torch.float32).to(wm.device))
    return result


def apply_stress_and_predict(
    model: nn.Module,
    test_loader,
    severity: float,
    device: torch.device,
    model_type: str,
) -> tuple:
    """Run inference with permutation stress. Returns (preds, labels) as numpy arrays."""
    model.eval()
    all_preds, all_labels = [], []

    with torch.no_grad():
        for batch in test_loader:
            if model_type == "flat":
                x = batch[0].to(device)
                labels = batch[1]
                if severity > 0.0:
                    x = _apply_flat_stress_batch(x, severity)
                preds = model(x).cpu().squeeze(-1)
            else:
                wms = [t.to(device) for t in batch[0]]
                labels = batch[1]
                if severity > 0.0:
                    wms = _apply_nft_stress_batch(wms, severity)
                preds = model(wms).cpu().squeeze(-1)

            all_preds.append(preds.numpy())
            all_labels.append(labels.numpy())

    return np.concatenate(all_preds), np.concatenate(all_labels)


# ---------------------------------------------------------------------------
# Holm correction (H-E1 pattern reuse — L-4-3)
# ---------------------------------------------------------------------------

def apply_holm_correction(p_values: list) -> list:
    """Apply Holm-Bonferroni step-down correction to a list of p-values.

    Parameters
    ----------
    p_values : list[float]
        Raw p-values (one per encoder).

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

    sorted_corrected = corrected[sorted_idx]
    reversed_sorted = sorted_corrected[::-1]
    cummin = np.minimum.accumulate(reversed_sorted)
    corrected_sorted = cummin[::-1]

    result = np.empty(m)
    result[sorted_idx] = corrected_sorted
    return np.clip(result, 0.0, 1.0).tolist()


# ---------------------------------------------------------------------------
# Per-encoder Delta_rho evaluation (L-4-1)
# ---------------------------------------------------------------------------

def evaluate_all_encoders(
    training_results: list,
    cfg: ExperimentConfig,
    flat_test_loader,
    nft_test_loader,
    flat_input_dim: int,
    layer_fan_ins: list,
) -> pd.DataFrame:
    """Evaluate all encoders: per-encoder Delta_rho across severity x seed.

    Parameters
    ----------
    training_results : list[dict]
        Output from run_all_training().
    cfg : ExperimentConfig
    flat_test_loader : DataLoader
    nft_test_loader : DataLoader
    flat_input_dim : int
    layer_fan_ins : list[int]

    Returns
    -------
    pd.DataFrame
        Columns: [encoder, seed, severity, rho, delta_rho, ci_lower, ci_upper, p_value]
        72 rows: 6 encoders × 3 seeds × 4 severities
    """
    device = torch.device(cfg.device if torch.cuda.is_available() else "cpu")
    rows = []

    # Build checkpoint path lookup
    ckpt_lookup = {}
    for r in training_results:
        key = (r["encoder"], r["seed"])
        ckpt_lookup[key] = r.get("checkpoint_path")

    for enc_name in cfg.encoder_names:
        enc_cfg = ENCODER_CONFIG[enc_name]
        model_type = enc_cfg["model_type"]
        test_loader = nft_test_loader if model_type == "nft" else flat_test_loader

        for seed in cfg.seeds:
            ckpt_path = ckpt_lookup.get((enc_name, seed))
            if not ckpt_path or not os.path.exists(ckpt_path):
                logger.warning(f"No checkpoint for {enc_name} seed={seed}, skipping.")
                continue

            model = build_encoder(enc_name, flat_input_dim, layer_fan_ins).to(device)
            model = load_checkpoint(model, ckpt_path, device)
            model.eval()

            # Compute rho at all severity levels
            rho_by_sev = {}
            for sev in cfg.severity_levels:
                preds, labels = apply_stress_and_predict(model, test_loader, sev, device, model_type)
                rho, _ = spearmanr(preds, labels)
                rho_by_sev[sev] = float(rho)

            # delta_rho = rho[0.0] - rho[1.0]
            rho_base = rho_by_sev.get(0.0, float("nan"))

            # Bootstrap delta_rho for s=1.0 (main comparison)
            rng = np.random.default_rng(seed)
            preds_s0, labels_arr = apply_stress_and_predict(model, test_loader, 0.0, device, model_type)
            preds_s1, _ = apply_stress_and_predict(model, test_loader, 1.0, device, model_type)
            n = len(labels_arr)

            bootstrap_samples = np.empty(cfg.n_bootstrap)
            for i in range(cfg.n_bootstrap):
                idx = rng.integers(0, n, size=n)
                r0, _ = spearmanr(preds_s0[idx], labels_arr[idx])
                r1, _ = spearmanr(preds_s1[idx], labels_arr[idx])
                bootstrap_samples[i] = r0 - r1

            ci_lower = float(np.percentile(bootstrap_samples, 2.5))
            ci_upper = float(np.percentile(bootstrap_samples, 97.5))
            p_value = float(np.mean(bootstrap_samples <= 0))

            for sev in cfg.severity_levels:
                delta_rho = rho_base - rho_by_sev.get(sev, float("nan"))
                rows.append({
                    "encoder": enc_name,
                    "seed": seed,
                    "severity": sev,
                    "rho": rho_by_sev.get(sev, float("nan")),
                    "delta_rho": delta_rho if sev == 1.0 else rho_base - rho_by_sev.get(sev, float("nan")),
                    "ci_lower": ci_lower if sev == 1.0 else float("nan"),
                    "ci_upper": ci_upper if sev == 1.0 else float("nan"),
                    "p_value": p_value if sev == 1.0 else float("nan"),
                })

    df = pd.DataFrame(rows)
    logger.info(f"evaluate_all_encoders: {len(df)} rows generated")
    return df


# ---------------------------------------------------------------------------
# Mediation Delta_R2 (L-4-2)
# ---------------------------------------------------------------------------

def compute_mediation_delta_r2(eval_df: pd.DataFrame) -> float:
    """Compute mediation Delta_R2 = R2(NFT-base) - R2(flat-MLP+aug).

    Uses Spearman rho^2 as R2 proxy at severity=0.0.

    Parameters
    ----------
    eval_df : pd.DataFrame
        Output from evaluate_all_encoders().

    Returns
    -------
    float
        Delta_R2 value. Positive means NFT explains more variance than aug.
        Gate threshold: >= 0.10.
    """
    # Get mean rho at severity=0.0 for each encoder (averaged across seeds)
    s0_df = eval_df[eval_df["severity"] == 0.0].copy()

    nft_rho = s0_df[s0_df["encoder"] == "NFT-base"]["rho"].mean()
    aug_rho = s0_df[s0_df["encoder"] == "flat-MLP+aug"]["rho"].mean()

    r2_nft = float(nft_rho ** 2)
    r2_aug = float(aug_rho ** 2)
    delta_r2 = r2_nft - r2_aug

    logger.info(
        f"Mediation ΔR²: R²(NFT-base)={r2_nft:.4f}, R²(flat-MLP+aug)={r2_aug:.4f}, "
        f"ΔR²={delta_r2:.4f}"
    )
    return delta_r2


# ---------------------------------------------------------------------------
# Encoder summary statistics (L-4-3)
# ---------------------------------------------------------------------------

def summarize_encoder_stats(eval_df: pd.DataFrame) -> dict:
    """Compute per-encoder summary with Holm-corrected p-values.

    Parameters
    ----------
    eval_df : pd.DataFrame
        Output from evaluate_all_encoders().

    Returns
    -------
    dict
        encoder -> {mean_delta_rho, std_delta_rho, p_value, p_value_corrected, significant}
    """
    s1_df = eval_df[eval_df["severity"] == 1.0].copy()
    encoder_names = s1_df["encoder"].unique().tolist()

    raw_p_values = []
    summaries = {}

    for enc in encoder_names:
        enc_df = s1_df[s1_df["encoder"] == enc]
        mean_dr = float(enc_df["delta_rho"].mean())
        std_dr = float(enc_df["delta_rho"].std())
        p_val = float(enc_df["p_value"].mean())
        raw_p_values.append(p_val)
        summaries[enc] = {
            "mean_delta_rho": mean_dr,
            "std_delta_rho": std_dr,
            "p_value": p_val,
            "p_value_corrected": None,
            "significant": None,
        }

    # Apply Holm correction
    corrected = apply_holm_correction(raw_p_values)
    for i, enc in enumerate(encoder_names):
        summaries[enc]["p_value_corrected"] = corrected[i]
        summaries[enc]["significant"] = corrected[i] < 0.05

    return summaries


# ---------------------------------------------------------------------------
# Gate v2 evaluation (L-4-4)
# ---------------------------------------------------------------------------

def evaluate_gate_condition_v2(
    eval_df: pd.DataFrame,
    delta_r2: float,
    cfg: ExperimentConfig,
    gate_cfg: GateConfig = None,
    results_dir: str = "results",
) -> dict:
    """Evaluate dual-condition H-M1 MUST_WORK gate.

    Conditions:
    1. nft_base_mean_delta_rho < 0.02
    2. delta_r2 >= 0.10

    Parameters
    ----------
    eval_df : pd.DataFrame
    delta_r2 : float
    cfg : ExperimentConfig
    gate_cfg : GateConfig (optional, uses defaults)
    results_dir : str

    Returns
    -------
    dict
        gate_result with passed, conditions, indicators, metrics.
    """
    if gate_cfg is None:
        gate_cfg = GateConfig()

    s1_df = eval_df[eval_df["severity"] == 1.0]

    # Core metrics
    nft_base_mean_dr = float(s1_df[s1_df["encoder"] == "NFT-base"]["delta_rho"].mean())
    flat_mlp_mean_dr = float(s1_df[s1_df["encoder"] == "flat-MLP"]["delta_rho"].mean())
    flat_aug_mean_dr = float(s1_df[s1_df["encoder"] == "flat-MLP+aug"]["delta_rho"].mean())
    oracle_mean_dr = float(s1_df[s1_df["encoder"] == "Oracle-canon"]["delta_rho"].mean())
    nft_aug_mean_dr = float(s1_df[s1_df["encoder"] == "NFT+aug"]["delta_rho"].mean())

    # 5 boolean indicators (C-5-2)
    nft_base_robust = nft_base_mean_dr < gate_cfg.nft_delta_rho_threshold
    mediation_confirmed = delta_r2 >= gate_cfg.mediation_delta_r2_threshold
    aug_partial = gate_cfg.aug_partial_delta_rho_min <= flat_aug_mean_dr <= gate_cfg.aug_partial_delta_rho_max
    architecture_sufficient = (flat_mlp_mean_dr - nft_base_mean_dr) > 0.05
    ranking_correct = (
        oracle_mean_dr <= nft_base_mean_dr
        and nft_base_mean_dr <= flat_aug_mean_dr
        and flat_aug_mean_dr <= flat_mlp_mean_dr
    )

    passed = nft_base_robust and mediation_confirmed

    gate_result = {
        "passed": passed,
        "gate_type": "MUST_WORK",
        "nft_delta_rho": nft_base_mean_dr,
        "delta_r2": delta_r2,
        "conditions": {
            "nft_base_delta_rho_lt_0_02": nft_base_robust,
            "delta_r2_ge_0_10": mediation_confirmed,
        },
        "indicators": {
            "nft_base_robust": nft_base_robust,
            "mediation_confirmed": mediation_confirmed,
            "aug_partial": aug_partial,
            "architecture_sufficient": architecture_sufficient,
            "ranking_correct": ranking_correct,
        },
        "encoder_delta_rho": {
            "flat-MLP": flat_mlp_mean_dr,
            "flat-MLP+aug": flat_aug_mean_dr,
            "NFT-base": nft_base_mean_dr,
            "Oracle-canon": oracle_mean_dr,
            "NFT+aug": nft_aug_mean_dr,
        },
        "thresholds": {
            "nft_delta_rho_threshold": gate_cfg.nft_delta_rho_threshold,
            "mediation_delta_r2_threshold": gate_cfg.mediation_delta_r2_threshold,
        },
        "timestamp": datetime.now().isoformat(),
    }

    os.makedirs(results_dir, exist_ok=True)
    gate_path = os.path.join(results_dir, "gate_result.json")
    with open(gate_path, "w") as f:
        json.dump(gate_result, f, indent=2)
    logger.info(f"Gate result written: {gate_path} | passed={passed}")

    return gate_result


# ---------------------------------------------------------------------------
# Mechanism verification (C-5-2, A-5)
# ---------------------------------------------------------------------------

def verify_mechanism_activated(
    eval_df: pd.DataFrame,
    delta_r2: float,
    gate_cfg: GateConfig = None,
) -> tuple:
    """Check all 5 mechanism indicators.

    Parameters
    ----------
    eval_df : pd.DataFrame
        Output from evaluate_all_encoders().
    delta_r2 : float
        Mediation Delta_R2.
    gate_cfg : GateConfig (optional)

    Returns
    -------
    tuple
        (all_pass: bool, indicators: dict)
    """
    if gate_cfg is None:
        gate_cfg = GateConfig()

    s1_df = eval_df[eval_df["severity"] == 1.0]

    nft_base_mean_dr = float(s1_df[s1_df["encoder"] == "NFT-base"]["delta_rho"].mean())
    flat_mlp_mean_dr = float(s1_df[s1_df["encoder"] == "flat-MLP"]["delta_rho"].mean())
    flat_aug_mean_dr = float(s1_df[s1_df["encoder"] == "flat-MLP+aug"]["delta_rho"].mean())
    oracle_mean_dr = float(s1_df[s1_df["encoder"] == "Oracle-canon"]["delta_rho"].mean())

    indicators = {
        "nft_base_robust": nft_base_mean_dr < gate_cfg.nft_delta_rho_threshold,
        "mediation_confirmed": delta_r2 >= gate_cfg.mediation_delta_r2_threshold,
        "aug_partial": gate_cfg.aug_partial_delta_rho_min <= flat_aug_mean_dr <= gate_cfg.aug_partial_delta_rho_max,
        "architecture_sufficient": (flat_mlp_mean_dr - nft_base_mean_dr) > 0.05,
        "ranking_correct": oracle_mean_dr <= nft_base_mean_dr <= flat_aug_mean_dr <= flat_mlp_mean_dr,
    }

    all_pass = indicators["nft_base_robust"] and indicators["mediation_confirmed"]
    logger.info(f"Mechanism verification: all_pass={all_pass}, indicators={indicators}")
    return all_pass, indicators
