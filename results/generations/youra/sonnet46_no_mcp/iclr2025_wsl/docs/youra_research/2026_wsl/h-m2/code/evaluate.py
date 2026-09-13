"""Evaluation, gate check, and results saving for H-M2 (NFN encoder)."""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
from scipy.stats import spearmanr
from torch.utils.data import DataLoader

logger = logging.getLogger("h-m2")


def compute_spearman(model, loader: DataLoader, device: torch.device) -> float:
    """Compute Spearman rho on full loader (NFN batch format).

    Batch: (weight_list, flat_w, acc) — uses weight_list for forward.
    """
    model.eval()
    preds, labels = [], []
    with torch.no_grad():
        for weight_list, flat_w, acc in loader:
            weight_list = [w.to(device) for w in weight_list]
            _, pred = model(weight_list)
            preds.extend(pred.squeeze(-1).cpu().numpy().tolist())
            labels.extend(acc.numpy().tolist())
    rho = spearmanr(preds, labels).statistic
    return float(rho) if not np.isnan(rho) else 0.0


def run_gate_check_nfn(
    sensitivity_score: float,
    spearman_rho: float,
    param_count: int,
    n_pairs: int,
    cfg,
) -> Dict:
    """Check SHOULD_WORK gate: sensitivity_score < both absolute and relative thresholds.

    gate_absolute: sensitivity_score < cfg.sensitivity_gate_absolute (0.1)
    gate_relative: sensitivity_score < cfg.sensitivity_gate_relative (0.3245)
    gate_pass = gate_absolute AND gate_relative
    """
    gate_absolute = sensitivity_score < cfg.sensitivity_gate_absolute
    gate_relative = sensitivity_score < cfg.sensitivity_gate_relative
    gate_pass = gate_absolute and gate_relative
    param_in_range = cfg.target_params_min <= param_count <= cfg.target_params_max
    pairs_sufficient = n_pairs >= cfg.min_pairs

    logger.info(
        f"[H-M2] Gate {'PASS' if gate_pass else 'FAIL'}: "
        f"sensitivity_score={sensitivity_score:.4f} "
        f"(abs_thresh={cfg.sensitivity_gate_absolute}, rel_thresh={cfg.sensitivity_gate_relative})"
    )
    logger.info(
        f"[H-M2] gate_absolute={gate_absolute}, gate_relative={gate_relative}"
    )
    logger.info(
        f"[H-M2] spearman_rho={spearman_rho:.4f}, "
        f"param_count={param_count:,} (in_range={param_in_range}), "
        f"n_pairs={n_pairs} (sufficient={pairs_sufficient})"
    )

    return {
        "hypothesis_id": "h-m2",
        "gate_pass": gate_pass,
        "gate_absolute_pass": gate_absolute,
        "gate_relative_pass": gate_relative,
        "sensitivity_score": sensitivity_score,
        "sensitivity_gate_absolute": cfg.sensitivity_gate_absolute,
        "sensitivity_gate_relative": cfg.sensitivity_gate_relative,
        "flat_mlp_sensitivity_score": cfg.flat_mlp_sensitivity_score,
        "spearman_rho": spearman_rho,
        "spearman_target": cfg.spearman_target,
        "param_count": param_count,
        "param_in_range": param_in_range,
        "n_pairs": n_pairs,
        "pairs_sufficient": pairs_sufficient,
    }


def save_results(results: Dict, cfg) -> None:
    """Save results as JSON to cfg.results_dir/h-m2_results.json."""
    results_dir = Path(cfg.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / "h-m2_results.json"

    def _convert(obj):
        if isinstance(obj, bool):
            return bool(obj)
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
        return obj

    payload = _convert(results)
    payload["timestamp"] = datetime.utcnow().isoformat() + "Z"

    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    logger.info(f"[H-M2] Results saved to {out_path}")
