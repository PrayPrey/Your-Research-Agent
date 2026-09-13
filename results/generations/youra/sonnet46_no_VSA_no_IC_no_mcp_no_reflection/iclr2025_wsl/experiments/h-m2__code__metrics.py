"""H-M2 metrics: partial Spearman (P3), bootstrap CI helpers."""
import numpy as np
from scipy.stats import spearmanr, rankdata
from sklearn.linear_model import LinearRegression


def rank_residuals(x: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Residuals of regressing rank(x) on rank(z)."""
    x_rank = rankdata(x).reshape(-1, 1)
    z_rank = z.reshape(-1, 1)
    lr = LinearRegression().fit(z_rank, x_rank)
    resid = x_rank.ravel() - lr.predict(z_rank).ravel()
    return resid


def partial_spearman(
    pred_gap: np.ndarray,
    true_gap: np.ndarray,
    true_testacc: np.ndarray,
) -> tuple:
    """Spearman(resid(pred_gap|rank(true_testacc)), resid(true_gap|rank(true_testacc))).
    Returns (r, p_value)."""
    z_rank = rankdata(true_testacc)
    pred_resid = rank_residuals(pred_gap, z_rank)
    true_resid = rank_residuals(true_gap, z_rank)
    r, p = spearmanr(pred_resid, true_resid)
    return float(r), float(p)


def bootstrap_spearman_ci(
    preds: np.ndarray,
    targets: np.ndarray,
    n_boot: int = 1000,
    seed: int = 42,
) -> tuple:
    """Bootstrap 95% CI on Spearman r. Returns (ci_low, ci_high)."""
    rng = np.random.RandomState(seed)
    n = len(preds)
    boot_rs = []
    for _ in range(n_boot):
        idx = rng.randint(0, n, size=n)
        r, _ = spearmanr(preds[idx], targets[idx])
        if np.isnan(r):
            r = 0.0
        boot_rs.append(r)
    return float(np.percentile(boot_rs, 2.5)), float(np.percentile(boot_rs, 97.5))


def verify_h_m2_mechanism(
    testacc_results: dict,
    gap_results: dict,
    delta: dict,
    p3: tuple,
) -> bool:
    """4 sanity checks; returns True if all pass."""
    check1 = all(np.isfinite(v) for v in testacc_results.values())
    check2 = 0.75 < testacc_results.get("FlatMLP", 0.0) < 0.95
    check3 = abs(gap_results.get("NFT", 0.0) - 0.5752) < 0.05
    check4 = all(np.isfinite(v) for v in delta.values())
    checks = {
        "all_testacc_finite": check1,
        "flatmlp_testacc_range [0.75,0.95]": check2,
        "nft_gap_consistent (±0.05 of 0.5752)": check3,
        "all_delta_finite": check4,
    }
    for k, v in checks.items():
        status = "✅" if v else "❌"
        print(f"[H-M2 verify] {status} {k}: {v}")
    n_pass_gate = sum(1 for d in delta.values() if d > 0.02)
    print(f"[H-M2 verify] gate_result: {n_pass_gate}/3 encoders Δ > 0.02")
    return all(checks.values())
