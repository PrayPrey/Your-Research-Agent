from __future__ import annotations
import math
import random

import numpy as np
from scipy import stats


def pearson_one_tailed(x: list[float], y: list[float]) -> tuple[float, float]:
    """Returns (r, one_tailed_p). one_tailed_p = two_tailed_p / 2."""
    r, p_two = stats.pearsonr(x, y)
    p_one = p_two / 2.0
    return float(r), float(p_one)


def bootstrap_ci(
    x: list[float], y: list[float], n_resamples: int = 1000, seed: int = 42
) -> tuple[float, float]:
    """Returns (ci_low, ci_high) for Pearson r at 95% confidence via bootstrap."""
    rng = np.random.default_rng(seed)
    x_arr = np.array(x)
    y_arr = np.array(y)
    n = len(x_arr)
    rs = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        r, _ = stats.pearsonr(x_arr[idx], y_arr[idx])
        rs.append(r)
    rs = np.array(rs)
    ci_low = float(np.percentile(rs, 2.5))
    ci_high = float(np.percentile(rs, 97.5))
    return ci_low, ci_high


def participation_ratio(W) -> float:
    """PR(W) = (sum(s))^2 / sum(s^2) — secondary metric, no gate."""
    import torch
    W = torch.as_tensor(W, dtype=torch.float32)
    S = torch.linalg.svdvals(W)
    return (S.sum() ** 2 / (S ** 2).sum()).item()


def compute_pr_map(model_name: str) -> dict[str, float]:
    """Compute participation ratio for all 2D weight matrices."""
    import torch
    from transformers import AutoModel
    model = AutoModel.from_pretrained(model_name, torch_dtype=torch.float32)
    model.eval()
    pr_map: dict[str, float] = {}
    with torch.no_grad():
        for name, param in model.named_parameters():
            if param.dim() != 2:
                continue
            lower = name.lower()
            if any(skip in lower for skip in ["embed", "norm", "layernorm", "ln_"]):
                continue
            pr_map[name] = participation_ratio(param.data)
    return pr_map


def run_correlation_analysis(
    erank_map: dict[str, float],
    oracle_rank_map: dict[str, int],
    pr_map: dict[str, float] = None,
    cfg=None,
) -> dict:
    """
    Compute Pearson correlation between erank and oracle rank.
    Returns dict with r, p values, CI, and pass status.
    """
    pearson_threshold = cfg.pearson_threshold if cfg else 0.65
    p_threshold = cfg.p_threshold if cfg else 0.05
    n_bootstrap = cfg.n_bootstrap if cfg else 1000
    bootstrap_seed = cfg.bootstrap_seed if cfg else 42

    # Align keys
    common_layers = sorted(set(erank_map.keys()) & set(oracle_rank_map.keys()))
    x = [erank_map[k] for k in common_layers]
    y = [float(oracle_rank_map[k]) for k in common_layers]

    r, p_one = pearson_one_tailed(x, y)
    _, p_two = stats.pearsonr(x, y)
    ci_low, ci_high = bootstrap_ci(x, y, n_resamples=n_bootstrap, seed=bootstrap_seed)

    pr_r = None
    if pr_map is not None:
        common_pr = sorted(set(pr_map.keys()) & set(oracle_rank_map.keys()))
        if len(common_pr) >= 5:
            xpr = [pr_map[k] for k in common_pr]
            ypr = [float(oracle_rank_map[k]) for k in common_pr]
            pr_r, _ = pearson_one_tailed(xpr, ypr)

    pass_gate = (r >= pearson_threshold) and (p_one < p_threshold)

    return {
        "r": r,
        "p_one_tailed": p_one,
        "p_two_tailed": float(p_two),
        "ci_low": ci_low,
        "ci_high": ci_high,
        "pr_r": pr_r,
        "n_layers": len(common_layers),
        "pass": pass_gate,
        "layers_used": common_layers,
    }


def verify_mechanism(
    erank_map: dict[str, float],
    oracle_rank_map: dict[str, int],
    model_name: str,
) -> tuple[bool, dict]:
    """Sanity checks: enough layers, oracle varies, positive r."""
    indicators = {
        "erank_layer_count": len(erank_map),
        "oracle_unique_ranks": len(set(oracle_rank_map.values())),
    }

    common = set(erank_map.keys()) & set(oracle_rank_map.keys())
    if len(common) >= 5:
        x = [erank_map[k] for k in sorted(common)]
        y = [float(oracle_rank_map[k]) for k in sorted(common)]
        r, _ = stats.pearsonr(x, y)
        indicators["r"] = float(r)
    else:
        indicators["r"] = None
        r = 0.0

    checks = {
        "enough_erank_layers": len(erank_map) >= 60,
        "oracle_varies": len(set(oracle_rank_map.values())) > 1,
        "positive_r": (indicators["r"] is not None and indicators["r"] > 0),
    }
    indicators["checks"] = checks
    all_pass = all(checks.values())
    return all_pass, indicators


def check_global_success(results_per_model: dict[str, dict]) -> bool:
    """True if >= 2/3 model families have pass=True."""
    passed = sum(1 for r in results_per_model.values() if r.get("pass", False))
    return passed >= 2
