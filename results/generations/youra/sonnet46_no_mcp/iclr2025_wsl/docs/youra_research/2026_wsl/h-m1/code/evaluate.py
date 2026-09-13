"""Evaluation, gate check, and results saving for H-M1."""
import json
import logging
from pathlib import Path
from typing import Dict

import numpy as np
import torch
from scipy.stats import spearmanr
from torch.utils.data import DataLoader

logger = logging.getLogger("h-m1")


def compute_spearman(model, loader: DataLoader, device: torch.device) -> float:
    """Compute Spearman rho on full loader using scipy.stats.spearmanr."""
    model.eval()
    preds, labels = [], []
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            _, pred = model(x)
            preds.extend(pred.squeeze(-1).cpu().numpy().tolist())
            labels.extend(y.numpy().tolist())
    rho = spearmanr(preds, labels).statistic
    return float(rho) if not np.isnan(rho) else 0.0


def run_gate_check(
    sensitivity_score: float,
    spearman_rho: float,
    param_count: int,
    n_pairs: int,
    cfg,
) -> Dict:
    """Check MUST_WORK gate: sensitivity_score > cfg.sensitivity_gate.

    Returns dict with gate_pass and all metrics.
    """
    gate_pass = sensitivity_score > cfg.sensitivity_gate
    param_in_range = cfg.target_params_min <= param_count <= cfg.target_params_max
    pairs_sufficient = n_pairs >= cfg.min_pairs

    logger.info(
        f"[H-M1] Gate {'PASS' if gate_pass else 'FAIL'}: "
        f"sensitivity_score={sensitivity_score:.4f} (threshold={cfg.sensitivity_gate})"
    )
    logger.info(
        f"[H-M1] spearman_rho={spearman_rho:.4f}, "
        f"param_count={param_count:,} (in_range={param_in_range}), "
        f"n_pairs={n_pairs} (sufficient={pairs_sufficient})"
    )

    return {
        "gate_pass": gate_pass,
        "sensitivity_score": sensitivity_score,
        "spearman_rho": spearman_rho,
        "param_count": param_count,
        "n_pairs": n_pairs,
        "param_in_range": param_in_range,
        "pairs_sufficient": pairs_sufficient,
        "gate_threshold": cfg.sensitivity_gate,
        "spearman_target": cfg.spearman_target,
    }


def save_results(results: Dict, cfg) -> None:
    """Save results as JSON to cfg.results_dir/h-m1_results.json."""
    results_dir = Path(cfg.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / "h-m1_results.json"

    # Make JSON-serializable
    def _convert(obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_convert(i) for i in obj]
        if isinstance(obj, bool):
            return bool(obj)
        return obj

    with open(out_path, "w") as f:
        json.dump(_convert(results), f, indent=2)
    logger.info(f"[H-M1] Results saved to {out_path}")
