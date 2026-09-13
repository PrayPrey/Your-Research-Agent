import numpy as np
import json
import os
from typing import Dict, List, Any, Optional

from config import GDRConfig


def compute_mean_early_gdr(
    gdr_series: List[float],
    early_epochs: List[int],
    checkpoint_interval: int,
) -> float:
    """Mean GDR over early window. early_epochs=[2,4,6] -> indices [0,1,2]."""
    indices = [(e // checkpoint_interval) - 1 for e in early_epochs]
    return float(np.mean([gdr_series[i] for i in indices]))


def run_wilcoxon_test(
    spurious_norms_early: np.ndarray,
    core_norms_early: np.ndarray,
) -> Dict[str, float]:
    """One-sided Wilcoxon: spurious > core. Returns {stat, p_value}."""
    from scipy.stats import wilcoxon
    try:
        stat, p = wilcoxon(spurious_norms_early, core_norms_early, alternative="greater")
    except ValueError:
        # All differences zero
        return {"stat": 0.0, "p_value": 1.0}
    return {"stat": float(stat), "p_value": float(p)}


def load_he1_delta(delta_path: str) -> np.ndarray:
    """Loads H-E1 delta(t) from JSON. Returns array shape (15,)."""
    with open(delta_path, "r") as f:
        data = json.load(f)
    # Try common keys
    for key in ("delta_series", "delta_t", "delta"):
        if key in data:
            return np.array(data[key])
    # Fallback: first list value
    for v in data.values():
        if isinstance(v, list):
            return np.array(v)
    raise ValueError(f"Cannot find delta series in {delta_path}")


def run_pearson_correlation(
    gdr_series: np.ndarray,
    delta_series: np.ndarray,
) -> Dict[str, float]:
    """Pearson r between gdr_series and delta_series."""
    from scipy.stats import pearsonr
    r, p = pearsonr(gdr_series, delta_series)
    return {"r": float(r), "p_value": float(p)}


def run_analysis(
    seed_results: Dict[int, Dict[str, Any]],
    cfg: GDRConfig,
    delta_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Aggregate across seeds: mean_early_GDR, Wilcoxon, Pearson."""
    checkpoint_interval = 2
    early_epochs = cfg.early_window_epochs

    mean_early_gdr_per_seed = {}
    wilcoxon_results = {}
    pearson_results = {}

    for seed, res in seed_results.items():
        gdr_series = res["gdr_series"]
        spurious_norms = res["spurious_grad_norms"]
        core_norms = res["core_grad_norms"]

        mean_gdr = compute_mean_early_gdr(gdr_series, early_epochs, checkpoint_interval)
        mean_early_gdr_per_seed[seed] = mean_gdr

        # Early indices for Wilcoxon
        indices = [(e // checkpoint_interval) - 1 for e in early_epochs]
        spurious_early = np.array([spurious_norms[i] for i in indices])
        core_early = np.array([core_norms[i] for i in indices])
        wilcoxon_results[seed] = run_wilcoxon_test(spurious_early, core_early)

        # Pearson correlation with H-E1 delta
        if delta_path and os.path.exists(delta_path):
            delta = load_he1_delta(delta_path)
            n = min(len(gdr_series), len(delta))
            pearson_results[seed] = run_pearson_correlation(
                np.array(gdr_series[:n]), delta[:n]
            )

    mean_gdr_vals = list(mean_early_gdr_per_seed.values())
    analysis = {
        "mean_early_gdr": float(np.mean(mean_gdr_vals)),
        "std_early_gdr": float(np.std(mean_gdr_vals)),
        "mean_early_gdr_per_seed": mean_early_gdr_per_seed,
        "wilcoxon_results": wilcoxon_results,
        "pearson_correlation": pearson_results,
        "per_seed": seed_results,
    }
    return analysis


def check_gate(analysis: Dict[str, Any], cfg: GDRConfig) -> bool:
    """Gate: mean_early_GDR > 1.0 in >= min_seeds_pass seeds AND Wilcoxon p < p_threshold."""
    seeds = list(analysis["mean_early_gdr_per_seed"].keys())
    seeds_pass = sum(1 for g in analysis["mean_early_gdr_per_seed"].values() if g > 1.0)
    wilcoxon_pass = sum(
        1 for r in analysis["wilcoxon_results"].values() if r["p_value"] < cfg.p_threshold
    )
    gate_pass = (seeds_pass >= cfg.min_seeds_pass) and (wilcoxon_pass >= cfg.min_seeds_pass)

    print(f"[H-M1 Gate] seeds_pass={seeds_pass}/{len(seeds)}, wilcoxon_pass={wilcoxon_pass}/{len(seeds)}")
    print(f"[H-M1 Gate] Result: {'PASS' if gate_pass else 'FAIL'}")
    return gate_pass
