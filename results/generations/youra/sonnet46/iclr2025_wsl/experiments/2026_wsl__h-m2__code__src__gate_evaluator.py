"""H-M2 Gate Evaluator: SHOULD_WORK three-way ranking gate.

Evaluates whether permutation augmentation and oracle canonicalization
provide partial compensation (but not full match) of NFT-base robustness.

Gate criteria (SHOULD_WORK):
- aug_partial:   flat-MLP+aug   Δρ > 0.05  (partial compensation)
- canon_partial: flat-MLP+canon Δρ > 0.03  (partial compensation)
- nft_superior:  NFT-base       Δρ < 0.02  (robust to permutation)
- ranking:       strict NFT-base < flat-MLP+canon < flat-MLP+aug < flat-MLP

Also includes:
- Paired bootstrap tests for (aug vs NFT) and (canon vs NFT)
- Holm-Bonferroni correction
- Cohen's d effect sizes
- Consistency check vs H-M1 known values
"""
import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ENCODERS_HM2: List[str] = ["flat-MLP", "flat-MLP+aug", "flat-MLP+canon", "NFT-base"]

AUG_THRESHOLD: float = 0.05
CANON_THRESHOLD: float = 0.03
NFT_THRESHOLD: float = 0.02

# H-M1 known values for consistency check
HM1_KNOWN: Dict[str, Dict[str, float]] = {
    "NFT-base":       {"delta_rho": 4.71e-7},
    "flat-MLP+aug":   {"delta_rho": 0.2239},
}

HM1_NFT_CONSISTENCY_MAX: float = 0.03   # NFT-base Δρ <= 0.03
HM1_AUG_CONSISTENCY_MIN: float = 0.21   # aug Δρ >= 0.21


# ---------------------------------------------------------------------------
# Bootstrap Statistical Tests (A-5)
# ---------------------------------------------------------------------------

def run_paired_bootstrap(
    y_pred_a: np.ndarray,
    y_pred_b: np.ndarray,
    y_true: np.ndarray,
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> dict:
    """Paired bootstrap test: H0: rho(A) == rho(B).

    Tests whether encoder A has significantly higher delta_rho than encoder B.
    One-sided test: P(boot_delta_rho_a > boot_delta_rho_b).

    Parameters
    ----------
    y_pred_a : np.ndarray, shape (N,)
        Predictions from encoder A (higher delta_rho = less robust)
    y_pred_b : np.ndarray, shape (N,)
        Predictions from encoder B
    y_true : np.ndarray, shape (N,)
        Ground-truth generalization gap labels
    n_bootstrap : int
        Number of bootstrap iterations
    seed : int
        Random seed for reproducibility

    Returns
    -------
    dict with keys: {p_value, ci_lower, ci_upper, delta_rho_obs, delta_rho_mean, boot_deltas}
    """
    rng = np.random.default_rng(seed)
    N = len(y_true)

    rho_a_obs, _ = spearmanr(y_pred_a, y_true)
    rho_b_obs, _ = spearmanr(y_pred_b, y_true)
    delta_rho_obs = float(rho_a_obs - rho_b_obs)  # positive = A less robust than B

    boot_deltas = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.integers(0, N, size=N)
        rho_a, _ = spearmanr(y_pred_a[idx], y_true[idx])
        rho_b, _ = spearmanr(y_pred_b[idx], y_true[idx])
        boot_deltas[i] = rho_a - rho_b

    # One-sided p-value: P(delta <= 0) tests H1: A has higher delta_rho
    p_value = float(np.mean(boot_deltas <= 0))
    ci_lower = float(np.percentile(boot_deltas, 2.5))
    ci_upper = float(np.percentile(boot_deltas, 97.5))
    delta_rho_mean = float(np.mean(boot_deltas))

    return {
        "p_value": p_value,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "delta_rho_obs": delta_rho_obs,
        "delta_rho_mean": delta_rho_mean,
        "boot_deltas": boot_deltas,
    }


def apply_holm_correction(p_values: List[float], alpha: float = 0.05) -> List[float]:
    """Holm-Bonferroni step-down correction.

    Parameters
    ----------
    p_values : list of float
        Raw p-values in any order
    alpha : float
        Significance level (default 0.05)

    Returns
    -------
    list of float
        Corrected p-values in same order as input, clipped to [0, 1]
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


def compute_cohens_d(
    delta_rho_a: np.ndarray,
    delta_rho_b: np.ndarray,
) -> float:
    """Cohen's d effect size between two bootstrap distributions.

    Parameters
    ----------
    delta_rho_a : np.ndarray, shape (n_bootstrap,)
        Bootstrap Δρ samples for encoder A
    delta_rho_b : np.ndarray, shape (n_bootstrap,)
        Bootstrap Δρ samples for encoder B

    Returns
    -------
    float
        Cohen's d = (mean_a - mean_b) / pooled_std
    """
    mean_a = np.mean(delta_rho_a)
    mean_b = np.mean(delta_rho_b)
    pooled_std = np.sqrt((np.std(delta_rho_a, ddof=1) ** 2 + np.std(delta_rho_b, ddof=1) ** 2) / 2)
    if pooled_std == 0:
        return 0.0
    return float((mean_a - mean_b) / pooled_std)


def format_p_value_report(
    bootstrap_results: dict,
    corrected_p_values: List[float],
    encoder_pairs: List[Tuple[str, str]],
) -> str:
    """Format bootstrap results as human-readable string for stdout.

    Parameters
    ----------
    bootstrap_results : dict
        Dict mapping pair_key to result dict from run_paired_bootstrap
    corrected_p_values : list of float
        Holm-corrected p-values in same order as encoder_pairs
    encoder_pairs : list of (str, str)
        List of (encoder_a, encoder_b) pairs tested

    Returns
    -------
    str
        Multi-line formatted report string
    """
    lines = [
        "",
        "=" * 60,
        "BOOTSTRAP STATISTICAL TESTS (Holm-corrected)",
        "=" * 60,
    ]
    for i, (enc_a, enc_b) in enumerate(encoder_pairs):
        pair_key = f"{enc_a}_vs_{enc_b}"
        result = bootstrap_results.get(pair_key, {})
        p_raw = result.get("p_value", float("nan"))
        p_corr = corrected_p_values[i] if i < len(corrected_p_values) else float("nan")
        delta_obs = result.get("delta_rho_obs", float("nan"))
        ci_lo = result.get("ci_lower", float("nan"))
        ci_hi = result.get("ci_upper", float("nan"))
        cohens_d = result.get("cohens_d", float("nan"))
        significant = p_corr < 0.05

        lines.append(f"  {enc_a} vs {enc_b}:")
        lines.append(f"    Δρ_obs={delta_obs:.4f}, 95% CI=[{ci_lo:.4f}, {ci_hi:.4f}]")
        lines.append(f"    p_raw={p_raw:.4f}, p_holm={p_corr:.4f}, Cohen's d={cohens_d:.3f}")
        lines.append(f"    Significant: {'YES' if significant else 'NO'} (α=0.05)")
    lines.append("=" * 60)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Gate Evaluator (A-6)
# ---------------------------------------------------------------------------

def _validate_ranking(mean_dr: Dict[str, float]) -> bool:
    """Check strict ranking: NFT-base < flat-MLP+canon < flat-MLP+aug < flat-MLP.

    Parameters
    ----------
    mean_dr : dict
        Mapping encoder_name -> mean Δρ at severity=1.0

    Returns
    -------
    bool
        True if strict ranking holds
    """
    nft = mean_dr.get("NFT-base", float("nan"))
    canon = mean_dr.get("flat-MLP+canon", float("nan"))
    aug = mean_dr.get("flat-MLP+aug", float("nan"))
    flat = mean_dr.get("flat-MLP", float("nan"))

    return (nft < canon) and (canon < aug) and (aug < flat)


def _build_gate_summary(
    mean_dr: Dict[str, float],
    aug_partial: bool,
    canon_partial: bool,
    nft_superior: bool,
    ranking: bool,
    passed: bool,
) -> str:
    """Format multi-line gate summary string for stdout.

    Parameters
    ----------
    mean_dr : dict
        Mapping encoder -> mean Δρ at s=1.0
    aug_partial : bool
    canon_partial : bool
    nft_superior : bool
    ranking : bool
    passed : bool

    Returns
    -------
    str
        Multi-line summary string
    """
    lines = [
        "",
        "=" * 60,
        f"SHOULD_WORK GATE: {'PASS' if passed else 'FAIL'}",
        "=" * 60,
        "Encoder mean Δρ at severity=1.0:",
    ]
    for enc in ENCODERS_HM2:
        dr = mean_dr.get(enc, float("nan"))
        lines.append(f"  {enc:<20s}: Δρ = {dr:.6f}")
    lines.extend([
        "",
        "Gate Conditions:",
        f"  aug_partial  (Δρ > {AUG_THRESHOLD}):  {'PASS' if aug_partial  else 'FAIL'}  [{mean_dr.get('flat-MLP+aug',  float('nan')):.6f}]",
        f"  canon_partial(Δρ > {CANON_THRESHOLD}):  {'PASS' if canon_partial else 'FAIL'}  [{mean_dr.get('flat-MLP+canon', float('nan')):.6f}]",
        f"  nft_superior (Δρ < {NFT_THRESHOLD}):  {'PASS' if nft_superior  else 'FAIL'}  [{mean_dr.get('NFT-base',      float('nan')):.6f}]",
        f"  strict_ranking:               {'PASS' if ranking      else 'FAIL'}",
        "=" * 60,
    ])
    return "\n".join(lines)


def check_checkpoint_consistency(
    eval_df: pd.DataFrame,
    expected: Optional[Dict] = None,
    tolerance: float = 0.01,
) -> dict:
    """Verify loaded checkpoint Δρ within ±tolerance of H-M1 known values.

    Parameters
    ----------
    eval_df : pd.DataFrame
        Output from evaluate_all_encoders()
    expected : dict, optional
        Expected values (defaults to HM1_KNOWN)
    tolerance : float
        Allowed deviation from expected values

    Returns
    -------
    dict with keys: {nft_consistent, aug_consistent, passed, details}
    """
    if expected is None:
        expected = HM1_KNOWN

    s1_df = eval_df[eval_df["severity"] == 1.0]

    details = {}
    results = {}

    for enc_name, exp_vals in expected.items():
        enc_df = s1_df[s1_df["encoder"] == enc_name]
        if enc_df.empty:
            logger.warning(f"Encoder '{enc_name}' not found in eval_df for consistency check")
            results[enc_name] = False
            details[enc_name] = {"status": "missing"}
            continue

        actual_dr = float(enc_df["delta_rho"].mean())
        exp_dr = exp_vals["delta_rho"]
        diff = abs(actual_dr - exp_dr)
        consistent = diff <= tolerance
        results[enc_name] = consistent
        details[enc_name] = {
            "expected": exp_dr,
            "actual": actual_dr,
            "diff": diff,
            "consistent": consistent,
        }
        logger.info(f"Consistency check {enc_name}: expected={exp_dr:.4e}, actual={actual_dr:.4e}, diff={diff:.4e}, ok={consistent}")

    nft_consistent = results.get("NFT-base", False)
    aug_consistent = results.get("flat-MLP+aug", False)
    passed = nft_consistent and aug_consistent

    return {
        "nft_consistent": nft_consistent,
        "aug_consistent": aug_consistent,
        "passed": passed,
        "details": details,
    }


def evaluate_gate_hm2(eval_df: pd.DataFrame) -> dict:
    """SHOULD_WORK gate: three-way ranking at severity=1.0.

    Evaluates whether:
    1. flat-MLP+aug shows partial compensation (Δρ > 0.05)
    2. flat-MLP+canon shows partial compensation (Δρ > 0.03)
    3. NFT-base remains robust (Δρ < 0.02)
    4. Strict ranking holds: NFT-base < flat-MLP+canon < flat-MLP+aug < flat-MLP

    Parameters
    ----------
    eval_df : pd.DataFrame
        Columns: [encoder, seed, severity, rho, delta_rho, ci_lower, ci_upper, p_value]
        Should have 48 rows for HM2 (4 encoders × 3 seeds × 4 severities)

    Returns
    -------
    dict with keys:
        aug_partial, canon_partial, nft_superior, ranking, passed,
        mean_dr_by_encoder, gate_summary, gate_type
    """
    s1_df = eval_df[eval_df["severity"] == 1.0].copy()

    if s1_df.empty:
        logger.error("No rows at severity=1.0 in eval_df")
        return {
            "aug_partial": False,
            "canon_partial": False,
            "nft_superior": False,
            "ranking": False,
            "passed": False,
            "mean_dr_by_encoder": {},
            "gate_summary": "ERROR: No severity=1.0 rows",
            "gate_type": "SHOULD_WORK",
        }

    # Compute mean Δρ per encoder at s=1.0 (averaged across seeds)
    mean_dr = {}
    for enc in ENCODERS_HM2:
        enc_df = s1_df[s1_df["encoder"] == enc]
        if enc_df.empty:
            logger.warning(f"Encoder '{enc}' not found in s1 data")
            mean_dr[enc] = float("nan")
        else:
            mean_dr[enc] = float(enc_df["delta_rho"].mean())

    aug_partial = mean_dr.get("flat-MLP+aug", float("nan")) > AUG_THRESHOLD
    canon_partial = mean_dr.get("flat-MLP+canon", float("nan")) > CANON_THRESHOLD
    nft_superior = mean_dr.get("NFT-base", float("nan")) < NFT_THRESHOLD
    ranking = _validate_ranking(mean_dr)

    passed = aug_partial and canon_partial and nft_superior and ranking

    gate_summary = _build_gate_summary(
        mean_dr, aug_partial, canon_partial, nft_superior, ranking, passed
    )

    logger.info(
        f"Gate HM2: passed={passed}, aug_partial={aug_partial}, "
        f"canon_partial={canon_partial}, nft_superior={nft_superior}, ranking={ranking}"
    )
    logger.info(f"Mean Δρ by encoder: {mean_dr}")

    return {
        "aug_partial": aug_partial,
        "canon_partial": canon_partial,
        "nft_superior": nft_superior,
        "ranking": ranking,
        "passed": passed,
        "mean_dr_by_encoder": mean_dr,
        "gate_summary": gate_summary,
        "gate_type": "SHOULD_WORK",
    }
