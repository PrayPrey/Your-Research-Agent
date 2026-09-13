"""Analysis: bootstrap CI, gap analysis, gate check for H-M3."""
import numpy as np
import config


def bootstrap_ci(r2_values: list, n_boot: int = None) -> tuple:
    """Percentile bootstrap CI. Returns (mean, ci_lo, ci_hi)."""
    if n_boot is None:
        n_boot = config.N_BOOT
    arr = np.array(r2_values, dtype=float)
    mean = float(arr.mean())
    if len(arr) < 2:
        return mean, mean, mean
    boot = np.array([np.random.choice(arr, size=len(arr), replace=True).mean()
                     for _ in range(n_boot)])
    lo = float(np.percentile(boot, 2.5))
    hi = float(np.percentile(boot, 97.5))
    return mean, lo, hi


def compute_gap_analysis(results: dict, zoo: str = "cifar10") -> dict:
    """Compute gap metrics per training size.

    gap_total = R²(gnn_nfn) - R²(flat_mlp)
    gap_perm_aug = R²(flat_mlp_perm_aug) - R²(flat_mlp)
    perm_aug_fraction = gap_perm_aug / gap_total
    """
    gap = {}
    flat = results["flat_mlp"][zoo]
    perm = results["flat_mlp_perm_aug"][zoo]
    gnn = results["gnn_nfn"][zoo]

    for sz_str in flat:
        if sz_str not in perm or sz_str not in gnn:
            continue
        r2_flat = flat[sz_str]["mean_r2"]
        r2_perm = perm[sz_str]["mean_r2"]
        r2_gnn = gnn[sz_str]["mean_r2"]

        gap_total = r2_gnn - r2_flat
        gap_perm_aug = r2_perm - r2_flat
        fraction = gap_perm_aug / gap_total if abs(gap_total) > 1e-8 else 0.0

        gap[sz_str] = {
            "gap_total": gap_total,
            "gap_perm_aug": gap_perm_aug,
            "perm_aug_fraction": fraction,
        }
    return gap


def check_ordering_gate(results: dict, zoo: str = "cifar10",
                         gate_sizes: list = None) -> tuple:
    """Strict ordering with non-overlapping bootstrap 95% CIs at gate_sizes.

    Condition: flat_mlp CI_hi < perm_aug CI_lo  AND  perm_aug CI_hi < gnn_nfn CI_lo
    Returns (gate_passed, details).
    """
    if gate_sizes is None:
        gate_sizes = [100, 250]

    flat = results["flat_mlp"][zoo]
    perm = results["flat_mlp_perm_aug"][zoo]
    gnn = results["gnn_nfn"][zoo]

    details = {}
    all_passed = True

    for sz in gate_sizes:
        sz_str = str(sz)
        if sz_str not in flat or sz_str not in perm or sz_str not in gnn:
            details[sz_str] = {"passed": False, "reason": "missing data"}
            all_passed = False
            continue

        flat_hi = flat[sz_str]["ci_hi"]
        perm_lo = perm[sz_str]["ci_lo"]
        perm_hi = perm[sz_str]["ci_hi"]
        gnn_lo = gnn[sz_str]["ci_lo"]

        cond1 = flat_hi < perm_lo  # flat_mlp CI below perm_aug CI
        cond2 = perm_hi < gnn_lo   # perm_aug CI below gnn_nfn CI

        passed = cond1 and cond2
        if not passed:
            all_passed = False

        details[sz_str] = {
            "passed": passed,
            "flat_mlp_ci_hi": flat_hi,
            "perm_aug_ci_lo": perm_lo,
            "perm_aug_ci_hi": perm_hi,
            "gnn_nfn_ci_lo": gnn_lo,
            "cond1_flat_below_perm": cond1,
            "cond2_perm_below_gnn": cond2,
        }

    return all_passed, details
