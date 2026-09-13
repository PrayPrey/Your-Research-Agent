"""H-M1: Logit Delta Anisotropy Analysis.

Implements covariance eigendecomposition, significance testing, secondary analyses,
gate evaluation and mechanism verification for the H-M1 MECHANISM hypothesis.

Key methodology:
- delta[N, 4] = aligned_logprobs - base_logprobs
- Anisotropy: λ₁ / mean(λ₂,λ₃,λ₄) >> 1 indicates structured (non-isotropic) perturbation
- Gate: ratio > 1.0 AND p < 0.05 in ≥ 2/3 model families
"""

import logging
import os

import numpy as np
from scipy import stats
from sklearn.decomposition import PCA

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Core: Logit Delta Computation (A-3)
# ─────────────────────────────────────────────────────────────

def compute_logit_delta(
    base_logprobs: np.ndarray,    # [N, 4]
    aligned_logprobs: np.ndarray, # [N, 4]
) -> np.ndarray:                  # [N, 4]
    """Compute logit delta: delta = aligned - base.

    No centering here — centering done inside eigendecomposition.

    Args:
        base_logprobs: log-softmax over [A,B,C,D] from base model, shape [N, 4]
        aligned_logprobs: log-softmax over [A,B,C,D] from aligned model, shape [N, 4]

    Returns:
        delta: element-wise difference, shape [N, 4]
    """
    assert base_logprobs.shape == aligned_logprobs.shape, (
        f"Shape mismatch: base={base_logprobs.shape}, aligned={aligned_logprobs.shape}"
    )
    assert base_logprobs.ndim == 2 and base_logprobs.shape[1] == 4, (
        f"Expected [N, 4] input, got {base_logprobs.shape}"
    )
    delta = aligned_logprobs - base_logprobs
    return delta


# ─────────────────────────────────────────────────────────────
# A-4: Covariance Eigendecomposition
# ─────────────────────────────────────────────────────────────

def compute_covariance_eigendecomposition(
    delta: np.ndarray,  # [N, 4]
) -> dict:
    """Eigendecompose covariance matrix of delta.

    Steps:
    1. Center delta: delta_centered = delta - mean(delta, axis=0)
    2. Compute covariance: cov = np.cov(delta_centered.T)  → [4, 4]
    3. Eigendecompose: np.linalg.eigh (symmetric, numerically stable)
    4. Sort descending by eigenvalue
    5. Compute anisotropy_ratio = λ₁ / mean(λ₂,λ₃,λ₄)

    Args:
        delta: logit delta matrix, shape [N, 4]

    Returns:
        dict with:
            eigenvalues: [4] descending
            eigenvectors: [4, 4] columns are eigenvectors
            cov_matrix: [4, 4]
            anisotropy_ratio: float (λ₁ / mean(λ₂,λ₃,λ₄))
    """
    assert delta.ndim == 2 and delta.shape[1] == 4, f"Expected [N, 4], got {delta.shape}"
    assert delta.shape[0] >= 5, f"Need at least 5 samples for covariance, got {delta.shape[0]}"

    # Center delta
    delta_centered = delta - delta.mean(axis=0)  # [N, 4]

    # Compute covariance matrix [4, 4]
    cov_matrix = np.cov(delta_centered.T)  # [4, 4]

    # Eigendecomposition (eigh for symmetric matrix — numerically stable, ascending order)
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

    # Sort descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Warn on degenerate covariance (near-zero eigenvalues)
    if np.any(eigenvalues <= 0):
        n_nonpos = np.sum(eigenvalues <= 0)
        logger.warning(f"Degenerate covariance: {n_nonpos} eigenvalues <= 0: {eigenvalues}")

    # Anisotropy ratio: dominant eigenvalue / mean of trailing 3
    trailing_mean = np.mean(eigenvalues[1:])
    eps = 1e-10
    if trailing_mean <= eps:
        # Degenerate: dominant >> trailing → high anisotropy
        # Use dominant eigenvalue as ratio approximation (signals extreme anisotropy)
        if eigenvalues[0] > eps:
            anisotropy_ratio = float(eigenvalues[0] / eps)  # very large
        else:
            logger.warning(f"All eigenvalues near zero, setting ratio=1.0")
            anisotropy_ratio = 1.0
    else:
        anisotropy_ratio = float(eigenvalues[0] / trailing_mean)

    return {
        "eigenvalues": eigenvalues,     # [4] descending
        "eigenvectors": eigenvectors,   # [4, 4]
        "cov_matrix": cov_matrix,       # [4, 4]
        "anisotropy_ratio": anisotropy_ratio,
    }


def compute_anisotropy_significance(
    eigenvalues: np.ndarray,  # [4] descending
) -> dict:
    """Test if dominant eigenvalue is significantly greater than trailing eigenvalues.

    Uses scipy.stats.ttest_1samp(eigenvalues[1:], popmean=eigenvalues[0]):
    Tests if trailing eigenvalues mean differs from dominant eigenvalue.
    One-tailed: we want trailing < dominant → p_value / 2.

    Args:
        eigenvalues: [4] descending eigenvalues

    Returns:
        dict with t_stat, p_value (one-tailed), is_significant (p < 0.05)
    """
    assert len(eigenvalues) == 4, f"Expected 4 eigenvalues, got {len(eigenvalues)}"

    dominant = eigenvalues[0]
    trailing = eigenvalues[1:]  # [3]

    # t-test: are trailing eigenvalues different from dominant?
    t_stat, p_two_tailed = stats.ttest_1samp(trailing, popmean=dominant)

    # One-tailed p-value (dominant > trailing → left-tail for negative t)
    p_one_tailed = p_two_tailed / 2.0

    is_significant = p_one_tailed < 0.05

    return {
        "t_stat": float(t_stat),
        "p_value": float(p_one_tailed),
        "is_significant": bool(is_significant),
    }


# ─────────────────────────────────────────────────────────────
# A-5: Secondary Analysis
# ─────────────────────────────────────────────────────────────

def compute_decision_axis_projection(
    delta: np.ndarray,          # [N, 4]
    base_logprobs: np.ndarray,  # [N, 4]
) -> dict:
    """Project delta onto decision margin axis (top1 - top2 direction).

    Decision axis = direction [1, -1, 0, 0] / norm (in sorted logprob space).
    Orthogonal variance from PCA components 2-4.

    Args:
        delta: logit delta [N, 4]
        base_logprobs: base model log-probabilities [N, 4]

    Returns:
        dict with decision_axis_var (float) and orthogonal_vars (ndarray [3])
    """
    # Decision axis vector: top1 - top2 direction (in sorted space)
    decision_vec = np.zeros(4)
    decision_vec[0] = 1.0
    decision_vec[1] = -1.0
    decision_vec /= np.linalg.norm(decision_vec)  # normalize to unit vector

    # Project delta onto decision axis
    proj = delta @ decision_vec  # [N]
    decision_axis_var = float(np.var(proj))

    # Orthogonal variance via PCA (skip dominant component)
    n_components = min(3, delta.shape[0] - 1, delta.shape[1])
    n_components = max(1, n_components)
    pca = PCA(n_components=n_components)
    pca.fit(delta - delta.mean(axis=0))
    # Skip first (dominant) component, take remaining
    if len(pca.explained_variance_) > 1:
        orthogonal_vars = pca.explained_variance_[1:]  # [n_components-1]
    else:
        orthogonal_vars = np.array([0.0, 0.0, 0.0])

    # Pad to [3] if needed
    if len(orthogonal_vars) < 3:
        orthogonal_vars = np.pad(orthogonal_vars, (0, 3 - len(orthogonal_vars)))

    return {
        "decision_axis_var": decision_axis_var,
        "orthogonal_vars": orthogonal_vars[:3],  # [3]
    }


def compute_margin_quintile_anisotropy(
    delta: np.ndarray,          # [N, 4]
    base_logprobs: np.ndarray,  # [N, 4]
    n_quintiles: int = 5,
) -> list:
    """Compute anisotropy ratio per confidence margin quintile.

    Args:
        delta: logit delta [N, 4]
        base_logprobs: base model log-probabilities [N, 4]
        n_quintiles: number of quintile bins (default 5)

    Returns:
        List of dicts per quintile: [{"quintile": int, "anisotropy_ratio": float, "n_items": int}, ...]
    """
    # Compute margins from base log-probabilities
    sorted_lp = np.sort(base_logprobs, axis=1)[:, ::-1]  # [N, 4] descending
    margins = sorted_lp[:, 0] - sorted_lp[:, 1]  # [N]

    # Compute quintile edges
    percentile_points = np.linspace(0, 100, n_quintiles + 1)
    quintile_edges = np.percentile(margins, percentile_points)

    results = []
    for q in range(n_quintiles):
        low = quintile_edges[q]
        high = quintile_edges[q + 1]

        if q == n_quintiles - 1:
            # Include right edge for last quintile
            mask = (margins >= low) & (margins <= high)
        else:
            mask = (margins >= low) & (margins < high)

        delta_q = delta[mask]  # [N_q, 4]

        if len(delta_q) < 10:
            logger.debug(f"Quintile {q+1}: only {len(delta_q)} items, skipping")
            continue

        try:
            result = compute_covariance_eigendecomposition(delta_q)
            results.append({
                "quintile": q + 1,
                "anisotropy_ratio": result["anisotropy_ratio"],
                "n_items": len(delta_q),
            })
        except Exception as e:
            logger.warning(f"Quintile {q+1} eigendecomposition failed: {e}")
            continue

    return results


def run_isotropic_sanity_check(n_items: int = 1000, seed: int = 1) -> dict:
    """Compute anisotropy ratio on synthetic isotropic Gaussian noise.

    Expected result: anisotropy_ratio ≈ 1.0 (within [0.8, 1.5]).

    Args:
        n_items: number of synthetic samples
        seed: random seed

    Returns:
        dict with anisotropy_ratio (float) and expected_approx_1 (bool)
    """
    rng = np.random.default_rng(seed)
    synthetic_delta = rng.normal(0, 1, (n_items, 4))

    result = compute_covariance_eigendecomposition(synthetic_delta)
    anisotropy_ratio = result["anisotropy_ratio"]

    # Expected approximately 1.0 for isotropic noise
    expected_approx_1 = 0.8 <= anisotropy_ratio <= 1.5

    return {
        "anisotropy_ratio": anisotropy_ratio,
        "expected_approx_1": expected_approx_1,
    }


# ─────────────────────────────────────────────────────────────
# A-6: Gate Evaluation
# ─────────────────────────────────────────────────────────────

def evaluate_gate(
    all_pair_results: list,
    gate_thresholds: dict,
) -> dict:
    """Evaluate H-M1 gate: ratio > 1.0 AND p < 0.05 in >= 2/3 families.

    FAIL means EXPLORE route — pipeline continues, does not abort.

    Args:
        all_pair_results: list of per-pair result dicts from run_anisotropy_analysis
        gate_thresholds: {"anisotropy_ratio_min": 1.0, "pvalue_max": 0.05, "families_min": 2}

    Returns:
        dict with gate_result, families_pass, families_total, pair_details
    """
    ratio_min = gate_thresholds.get("anisotropy_ratio_min", 1.0)
    pvalue_max = gate_thresholds.get("pvalue_max", 0.05)
    families_min = gate_thresholds.get("families_min", 2)

    pair_details = []
    families_pass = 0

    for pair_result in all_pair_results:
        pair_id = pair_result["pair_id"]
        ratio = pair_result["primary_ratio"]
        p_value = pair_result["primary_p_value"]

        passed = (ratio > ratio_min) and (p_value < pvalue_max)

        if passed:
            families_pass += 1

        pair_details.append({
            "pair_id": pair_id,
            "ratio": ratio,
            "p_value": p_value,
            "passed": passed,
        })

        logger.info(
            f"  Pair {pair_id}: ratio={ratio:.4f}, p={p_value:.4f} → {'PASS' if passed else 'FAIL'}"
        )

    families_total = len(all_pair_results)
    gate_result = "PASS" if families_pass >= families_min else "FAIL"

    logger.info(
        f"Gate: {gate_result} ({families_pass}/{families_total} families, "
        f"min={families_min})"
    )

    return {
        "gate_result": gate_result,
        "families_pass": families_pass,
        "families_total": families_total,
        "pair_details": pair_details,
    }


# ─────────────────────────────────────────────────────────────
# A-7: run_anisotropy_analysis Pipeline
# ─────────────────────────────────────────────────────────────

def run_anisotropy_analysis(
    pair_cfg: dict,
    datasets_logprobs: dict,  # {"mmlu": {"base": ndarray[N,4], "aligned": ndarray[N,4]}, ...}
) -> dict:
    """Full per-pair anisotropy pipeline: delta -> covariance -> eigendecomp -> significance -> secondary.

    Args:
        pair_cfg: pair configuration dict with pair_id, base, aligned, method
        datasets_logprobs: dict mapping dataset name to {"base": ndarray, "aligned": ndarray}

    Returns:
        Per-pair result dict with all dataset results, primary metrics, passes_gate flag
    """
    pair_id = pair_cfg["pair_id"]
    logger.info(f"Running anisotropy analysis for {pair_id}...")

    all_ds_results = {}

    for ds_name, logprobs in datasets_logprobs.items():
        base = logprobs["base"]       # [N, 4]
        aligned = logprobs["aligned"] # [N, 4]

        logger.info(f"  Dataset {ds_name}: {base.shape[0]} items")

        # Compute logit delta
        delta = compute_logit_delta(base, aligned)  # [N, 4]

        # Eigendecomposition
        eigen_result = compute_covariance_eigendecomposition(delta)

        # Significance test
        sig_result = compute_anisotropy_significance(eigen_result["eigenvalues"])

        # Secondary: decision axis projection
        decision_result = compute_decision_axis_projection(delta, base)

        # Secondary: quintile anisotropy
        quintile_result = compute_margin_quintile_anisotropy(delta, base)

        all_ds_results[ds_name] = {
            "delta": delta,
            "eigenvalues": eigen_result["eigenvalues"],
            "eigenvectors": eigen_result["eigenvectors"],
            "cov_matrix": eigen_result["cov_matrix"],
            "anisotropy_ratio": eigen_result["anisotropy_ratio"],
            "significance": sig_result,
            "decision_axis": decision_result,
            "quintile_results": quintile_result,
        }

        logger.info(
            f"  {ds_name}: ratio={eigen_result['anisotropy_ratio']:.4f}, "
            f"p={sig_result['p_value']:.4f}, "
            f"significant={sig_result['is_significant']}"
        )

    # Primary metrics from mmlu
    primary = all_ds_results.get("mmlu", list(all_ds_results.values())[0])
    primary_ratio = primary["anisotropy_ratio"]
    primary_p_value = primary["significance"]["p_value"]
    passes_gate = (primary_ratio > 1.0) and primary["significance"]["is_significant"]

    logger.info(
        f"Pair {pair_id}: primary_ratio={primary_ratio:.4f}, "
        f"primary_p={primary_p_value:.4f}, passes_gate={passes_gate}"
    )

    return {
        "pair_id": pair_id,
        "method": pair_cfg.get("method", "unknown"),
        "datasets": all_ds_results,
        "primary_ratio": primary_ratio,
        "primary_p_value": primary_p_value,
        "passes_gate": passes_gate,
    }


# ─────────────────────────────────────────────────────────────
# A-8: Mechanism Verification
# ─────────────────────────────────────────────────────────────

def verify_mechanism_activated(
    pair_id: str,
    base_logprobs: np.ndarray,    # [N, 4]
    aligned_logprobs: np.ndarray, # [N, 4]
    results: dict,
) -> tuple:
    """Check 5 activation indicators for the H-M1 mechanism.

    Indicators:
    1. delta_computed: base.shape == aligned.shape == (N, 4)
    2. cov_computed: cov_matrix present and shape (4, 4)
    3. eigenvalues_valid: all eigenvalues > 0 (no degenerate covariance)
    4. ratio_above_threshold: anisotropy_ratio > 0
    5. log_found: pair_id in results

    Args:
        pair_id: model pair identifier
        base_logprobs: base model log-probabilities [N, 4]
        aligned_logprobs: aligned model log-probabilities [N, 4]
        results: dict containing analysis results (from run_anisotropy_analysis)

    Returns:
        (activated: bool, indicators: dict)
    """
    indicators = {}

    # 1. Delta computed: shapes match and are [N, 4]
    indicators["delta_computed"] = (
        base_logprobs.shape == aligned_logprobs.shape
        and base_logprobs.ndim == 2
        and base_logprobs.shape[1] == 4
    )

    # 2. Covariance computed: check primary dataset has cov_matrix
    primary_ds = results.get("datasets", {}).get("mmlu", {})
    if not primary_ds:
        primary_ds = list(results.get("datasets", {}).values())[0] if results.get("datasets") else {}
    cov_matrix = primary_ds.get("cov_matrix")
    indicators["cov_computed"] = (
        cov_matrix is not None
        and hasattr(cov_matrix, "shape")
        and cov_matrix.shape == (4, 4)
    )

    # 3. Eigenvalues valid: all > 0
    eigenvalues = primary_ds.get("eigenvalues")
    if eigenvalues is not None and len(eigenvalues) == 4:
        indicators["eigenvalues_valid"] = bool(np.all(eigenvalues > 0))
    else:
        indicators["eigenvalues_valid"] = False

    # 4. Ratio above threshold: > 0
    ratio = results.get("primary_ratio", 0.0)
    indicators["ratio_above_threshold"] = float(ratio) > 0.0

    # 5. Log found: pair_id in results
    indicators["log_found"] = results.get("pair_id") == pair_id

    activated = all(indicators.values())

    logger.info(f"Mechanism verification for {pair_id}:")
    for name, status in indicators.items():
        logger.info(f"  {'✓' if status else '✗'} {name}: {status}")
    logger.info(f"  → Activated: {activated}")

    return activated, indicators
