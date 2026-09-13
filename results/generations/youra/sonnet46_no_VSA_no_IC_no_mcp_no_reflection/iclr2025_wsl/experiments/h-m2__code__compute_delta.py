"""H-M2: Δ computation, gate check, bootstrap CI on Δ."""
from __future__ import annotations
import numpy as np
from scipy.stats import spearmanr

H_M1_GAP: dict[str, float] = {
    "FlatMLP": 0.5329689989580692,
    "DWSNet":  0.48809483873768406,
    "NFT":     0.5752373204944404,
    "GNN":     0.3747222199638867,
}
EQUIVARIANT = ["DWSNet", "NFT", "GNN"]
GATE_THRESHOLD: float = 0.02
GATE_MIN_PASS: int = 2
BOOTSTRAP_N: int = 1000


def compute_delta(
    gap_results: dict[str, float],
    testacc_results: dict[str, float],
) -> dict[str, float]:
    """Δ(enc) = (gap[enc]-gap[FlatMLP]) - (acc[enc]-acc[FlatMLP]). FlatMLP excluded."""
    baseline_gap = gap_results["FlatMLP"]
    baseline_acc = testacc_results["FlatMLP"]
    delta = {}
    for enc in EQUIVARIANT:
        gap_imp = gap_results[enc] - baseline_gap
        acc_imp = testacc_results[enc] - baseline_acc
        delta[enc] = gap_imp - acc_imp
        print(f"[H-M2] {enc}: gap_imp={gap_imp:.4f}, acc_imp={acc_imp:.4f}, Δ={delta[enc]:.4f}")
    return delta


def gate_check(
    delta: dict[str, float],
    threshold: float = GATE_THRESHOLD,
    min_pass: int = GATE_MIN_PASS,
) -> tuple[int, bool]:
    """Returns (n_pass, passed). Counts encoders in EQUIVARIANT with Δ > threshold."""
    n_pass = sum(1 for enc in EQUIVARIANT if delta.get(enc, -np.inf) > threshold)
    passed = n_pass >= min_pass
    return n_pass, passed


def bootstrap_delta_ci(
    gap_preds: dict[str, np.ndarray],
    testacc_preds: dict[str, np.ndarray],
    true_gap: np.ndarray,
    true_testacc: np.ndarray,
    n_boot: int = BOOTSTRAP_N,
    seed: int = 42,
) -> dict[str, tuple[float, float]]:
    """Returns {enc: (ci_low, ci_high)} 95% CI on Δ for equivariant encoders."""
    rng = np.random.RandomState(seed)
    n = len(true_gap)
    boot_deltas: dict[str, list] = {enc: [] for enc in EQUIVARIANT}
    for _ in range(n_boot):
        idx = rng.randint(0, n, size=n)
        gap_flat_r, _ = spearmanr(gap_preds["FlatMLP"][idx], true_gap[idx])
        acc_flat_r, _ = spearmanr(testacc_preds["FlatMLP"][idx], true_testacc[idx])
        if np.isnan(gap_flat_r):
            gap_flat_r = 0.0
        if np.isnan(acc_flat_r):
            acc_flat_r = 0.0
        for enc in EQUIVARIANT:
            gap_r, _ = spearmanr(gap_preds[enc][idx], true_gap[idx])
            acc_r, _ = spearmanr(testacc_preds[enc][idx], true_testacc[idx])
            if np.isnan(gap_r):
                gap_r = 0.0
            if np.isnan(acc_r):
                acc_r = 0.0
            d = (gap_r - gap_flat_r) - (acc_r - acc_flat_r)
            boot_deltas[enc].append(d)
    return {
        enc: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)))
        for enc, v in boot_deltas.items()
    }
