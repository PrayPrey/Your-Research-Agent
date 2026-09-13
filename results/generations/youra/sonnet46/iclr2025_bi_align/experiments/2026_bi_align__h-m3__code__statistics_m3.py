"""
statistics.py - Statistical tests for h-e1/h-m1 experiment.

Includes bootstrap CI, Mann-Whitney, Cohen's d, mechanism verification,
and h-m1 extensions: Jonckheere-Terpstra, Bonferroni Mann-Whitney,
KS test, IPW robustness, model consistency check.
"""
import numpy as np
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from typing import Dict, List, Tuple

TIER_ORDER = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]
BONFERRONI_ALPHA = 0.05 / 3  # = 0.0167
JT_P_THRESHOLD = 0.05
COHEN_D_THRESHOLD = 0.1
MODEL_CONSISTENCY_THRESHOLD = 2

MIN_N_PAIRS = 1000


def bootstrap_c_sem(
    cos_actual: np.ndarray,
    cos_random: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Tuple[float, np.ndarray]:
    """Bootstrap confidence interval for C_sem.

    Args:
        cos_actual: shape (N,) - actual cosine similarities
        cos_random: shape (N,) - random control cosine similarities
        n_bootstrap: number of bootstrap samples
        seed: random seed

    Returns:
        Tuple of (c_sem, ci_array) where ci_array shape (2,) = [lower, upper] at 95% CI.
    """
    rng = np.random.default_rng(seed)
    n = len(cos_actual)
    c_sem = float(np.mean(cos_actual) - np.mean(cos_random))

    boot_samples = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        boot_samples[i] = np.mean(cos_actual[idx]) - np.mean(cos_random[idx])

    ci_array = np.array([
        np.percentile(boot_samples, 2.5),
        np.percentile(boot_samples, 97.5),
    ])
    return c_sem, ci_array


def bootstrap_cohen_d(
    arr_a: np.ndarray,
    arr_b: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Tuple[float, np.ndarray]:
    """Bootstrap confidence interval for Cohen's d using pooled std.

    Pooled std formula: sqrt(((N-1)*var_a + (M-1)*var_b) / (N+M-2))
    Zero-division guard: if pooled_std == 0, d = 0.

    Args:
        arr_a: shape (N,) - first array
        arr_b: shape (M,) - second array
        n_bootstrap: number of bootstrap samples
        seed: random seed

    Returns:
        Tuple of (cohen_d, ci_array) where ci_array shape (2,).
    """
    rng = np.random.default_rng(seed)

    def _cohen_d(a, b):
        na, nb = len(a), len(b)
        pooled_var = ((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2)
        pooled_std = np.sqrt(pooled_var)
        if pooled_std == 0:
            return 0.0
        return float((np.mean(a) - np.mean(b)) / pooled_std)

    d = _cohen_d(arr_a, arr_b)

    na, nb = len(arr_a), len(arr_b)
    boot_samples = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        idx_a = rng.integers(0, na, size=na)
        idx_b = rng.integers(0, nb, size=nb)
        boot_samples[i] = _cohen_d(arr_a[idx_a], arr_b[idx_b])

    ci_array = np.array([
        np.percentile(boot_samples, 2.5),
        np.percentile(boot_samples, 97.5),
    ])
    return d, ci_array


def mann_whitney_test(arr_a: np.ndarray, arr_b: np.ndarray) -> Dict:
    """Mann-Whitney U test.

    Returns:
        dict with 'statistic' and 'p_value'.
    """
    result = stats.mannwhitneyu(arr_a, arr_b, alternative="two-sided")
    return {
        "statistic": float(result.statistic),
        "p_value": float(result.pvalue),
    }


def run_all_tests(
    cos_actual: np.ndarray,
    cos_topic: np.ndarray,
    cos_random: np.ndarray,
    n_pairs: int,
) -> Dict:
    """Run all statistical tests for h-e1.

    Args:
        cos_actual: shape (N,) - actual cosine similarities
        cos_topic: shape (N,) - topic-matched control cosine similarities
        cos_random: shape (N,) - random control cosine similarities
        n_pairs: number of pairs (must be >= MIN_N_PAIRS)

    Returns:
        Flat dict with all results.
    """
    assert n_pairs >= MIN_N_PAIRS, f"n_pairs={n_pairs} < MIN_N_PAIRS={MIN_N_PAIRS}"

    c_sem, c_sem_ci = bootstrap_c_sem(cos_actual, cos_random)
    mw_actual_vs_topic = mann_whitney_test(cos_actual, cos_topic)
    mw_topic_vs_random = mann_whitney_test(cos_topic, cos_random)
    cohen_d_actual_vs_topic, _ = bootstrap_cohen_d(cos_actual, cos_topic)
    cohen_d_actual_vs_random, _ = bootstrap_cohen_d(cos_actual, cos_random)
    cohen_d_topic_vs_random, _ = bootstrap_cohen_d(cos_topic, cos_random)

    return {
        "n_pairs": n_pairs,
        "c_sem": c_sem,
        "c_sem_ci": c_sem_ci,
        "cos_actual_mean": float(np.mean(cos_actual)),
        "cos_topic_mean": float(np.mean(cos_topic)),
        "cos_random_mean": float(np.mean(cos_random)),
        "mann_whitney_actual_vs_topic": mw_actual_vs_topic,
        "mann_whitney_topic_vs_random": mw_topic_vs_random,
        "cohen_d_actual_vs_topic": cohen_d_actual_vs_topic,
        "cohen_d_actual_vs_random": cohen_d_actual_vs_random,
        "cohen_d_topic_vs_random": cohen_d_topic_vs_random,
    }


def verify_mechanism_activated(
    results: Dict,
    embeddings_computed: bool,
) -> Tuple[bool, Dict]:
    """Verify mechanism activation via 5 indicators.

    Indicators:
      1. embeddings_computed: embeddings were successfully computed
      2. c_sem_positive: c_sem > 0
      3. ci_lower_positive: c_sem_ci[0] > 0
      4. ordering_holds: cos_actual_mean > cos_topic_mean > cos_random_mean
      5. sufficient_pairs: n_pairs >= 1000

    Returns:
        Tuple of (all_activated: bool, indicators: dict).
    """
    indicators = {
        "embeddings_computed": embeddings_computed,
        "c_sem_positive": results["c_sem"] > 0,
        "ci_lower_positive": results["c_sem_ci"][0] > 0,
        "ordering_holds": (
            results["cos_actual_mean"] > results["cos_topic_mean"] > results["cos_random_mean"]
        ),
        "sufficient_pairs": results["n_pairs"] >= 1000,
    }
    all_activated = all(indicators.values())
    return all_activated, indicators


# ============================================================================
# H-M1 EXTENSIONS: Monotonicity Tests, IPW Robustness, Model Consistency
# ============================================================================

def _jonckheere_terpstra_stat(groups: List[np.ndarray]) -> float:
    """Compute Jonckheere-Terpstra statistic (sum of Mann-Whitney U over ordered pairs).

    JT = sum_{i<j} U(groups[i], groups[j]) where U is the Mann-Whitney statistic
    testing whether groups[i] < groups[j] (one-sided).
    """
    jt_stat = 0.0
    k = len(groups)
    for i in range(k - 1):
        for j in range(i + 1, k):
            # Count pairs where groups[i][a] < groups[j][b]
            u = 0.0
            for xi in groups[i]:
                u += np.sum(xi < groups[j])
                u += 0.5 * np.sum(xi == groups[j])
            jt_stat += u
    return float(jt_stat)


def jonckheere_terpstra_test(tier_results: Dict, tier_order: List[str]) -> Dict:
    """Jonckheere-Terpstra test for ordered monotonicity.

    Tests whether raw cosine similarities increase monotonically across tiers.

    CRITICAL: Use raw_cos_actual arrays, NOT OLS residuals (zero mean by construction).

    Uses scipy.stats.jonckheere_terpstra if available (scipy >= 1.10),
    otherwise falls back to manual implementation via Mann-Whitney U.

    Args:
        tier_results: {tier_name: {raw_cos_actual: ndarray, ...}}
        tier_order: List of tier names in ascending quality order.

    Returns:
        {'jt_statistic': float, 'jt_pvalue': float}
    """
    ordered_cos = [tier_results[t]["raw_cos_actual"] for t in tier_order]

    # Try scipy native implementation first
    try:
        jt = stats.jonckheere_terpstra(*ordered_cos, alternative="increasing")
        return {
            "jt_statistic": float(jt.statistic),
            "jt_pvalue": float(jt.pvalue),
        }
    except AttributeError:
        pass

    # Fallback: manual JT test using permutation-based p-value approximation
    # JT statistic = sum of U statistics for all ordered pairs
    jt_stat = _jonckheere_terpstra_stat(ordered_cos)

    # Approximate p-value using normal approximation
    # Under H0: E[JT] = N^2/4 * k*(k-1)/2 approximately
    # Use bootstrap permutation for better accuracy
    n_total = sum(len(g) for g in ordered_cos)
    all_data = np.concatenate(ordered_cos)
    group_sizes = [len(g) for g in ordered_cos]

    rng = np.random.default_rng(42)
    n_perm = 1000
    perm_stats = []
    for _ in range(n_perm):
        perm = rng.permutation(all_data)
        perm_groups = []
        start = 0
        for size in group_sizes:
            perm_groups.append(perm[start:start + size])
            start += size
        perm_stats.append(_jonckheere_terpstra_stat(perm_groups))

    perm_stats = np.array(perm_stats)
    jt_pvalue = float(np.mean(perm_stats >= jt_stat))
    # Ensure p-value is not exactly 0 (add 1 count pseudocount)
    jt_pvalue = max(jt_pvalue, 1.0 / (n_perm + 1))

    return {
        "jt_statistic": jt_stat,
        "jt_pvalue": jt_pvalue,
    }


def bonferroni_mannwhitney(
    tier_results: Dict,
    tier_order: List[str],
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Dict:
    """Bonferroni-corrected pairwise Mann-Whitney U tests.

    Tests all 3 adjacent + non-adjacent tier pairs with Bonferroni correction.
    Bonferroni threshold: alpha/3 = 0.0167.

    Args:
        tier_results: {tier_name: {raw_cos_actual: ndarray, ...}}
        tier_order: List of tier names in order.
        n_bootstrap: Number of bootstrap samples for Cohen's d CI.
        seed: Random seed.

    Returns:
        {pair_key: {mw_statistic, mw_pvalue, bonferroni_significant, cohen_d, cohen_d_ci}}
    """
    t1, t2, t3 = tier_order
    pairs = [(t1, t2), (t2, t3), (t1, t3)]
    results = {}

    for ta, tb in pairs:
        arr_a = tier_results[ta]["raw_cos_actual"]
        arr_b = tier_results[tb]["raw_cos_actual"]
        mw = stats.mannwhitneyu(arr_a, arr_b, alternative="two-sided")
        d, d_ci = bootstrap_cohen_d(arr_a, arr_b, n_bootstrap, seed)
        pair_key = f"{ta}_vs_{tb}"
        results[pair_key] = {
            "mw_statistic": float(mw.statistic),
            "mw_pvalue": float(mw.pvalue),
            "bonferroni_significant": bool(mw.pvalue < BONFERRONI_ALPHA),
            "cohen_d": float(d),
            "cohen_d_ci": d_ci.tolist(),
        }

    return results


def bootstrap_cohens_d_all_pairs(
    tier_results: Dict,
    models_results: Dict,
    n: int = 1000,
    seed: int = 42,
) -> Dict:
    """Compute bootstrap Cohen's d for all tier pairs × all models.

    Args:
        tier_results: Unused (models_results has per-model tier results)
        models_results: {model_slug: {tier_results: {tier: {raw_cos_actual, ...}}}}
        n: Number of bootstrap samples.
        seed: Random seed.

    Returns:
        {model_slug: {pair_key: {cohen_d, cohen_d_ci}}}
    """
    tier_order = TIER_ORDER
    t1, t2, t3 = tier_order
    pairs = [(t1, t2), (t2, t3), (t1, t3)]

    all_results = {}
    for model_slug, model_data in models_results.items():
        m_tier_results = model_data.get("tier_results", {})
        pair_results = {}
        for ta, tb in pairs:
            if ta not in m_tier_results or tb not in m_tier_results:
                continue
            arr_a = m_tier_results[ta]["raw_cos_actual"]
            arr_b = m_tier_results[tb]["raw_cos_actual"]
            d, d_ci = bootstrap_cohen_d(arr_a, arr_b, n, seed)
            pair_key = f"{ta}_vs_{tb}"
            pair_results[pair_key] = {
                "cohen_d": float(d),
                "cohen_d_ci": d_ci.tolist(),
            }
        all_results[model_slug] = pair_results

    return all_results


def ks_test_tier_distributions(
    tier_prompt_embeddings: Dict,
    tier_order: List[str],
) -> Dict:
    """KS test on tier prompt embedding distributions using PCA-1 projection.

    Tests whether prompt embeddings differ across tiers (indicating covariate shift).
    Uses PCA to project to 1D before testing.

    Args:
        tier_prompt_embeddings: {tier_name: np.ndarray of shape (N, D)}
        tier_order: List of tier names in order.

    Returns:
        {pair_key: {ks_statistic, ks_pvalue, ipw_triggered}}
    """
    # PCA fit on all tiers combined
    all_embs = np.vstack([tier_prompt_embeddings[t] for t in tier_order])
    pca = PCA(n_components=1)
    pca.fit(all_embs)

    # Project each tier to 1D
    proj = {t: pca.transform(tier_prompt_embeddings[t]).ravel() for t in tier_order}

    t1, t2, t3 = tier_order
    pairs = [(t1, t2), (t2, t3), (t1, t3)]
    results = {}

    any_significant = False
    for ta, tb in pairs:
        ks = stats.ks_2samp(proj[ta], proj[tb])
        ipw_triggered = bool(ks.pvalue < 0.05)
        if ipw_triggered:
            any_significant = True
        pair_key = f"{ta}_vs_{tb}"
        results[pair_key] = {
            "ks_statistic": float(ks.statistic),
            "ks_pvalue": float(ks.pvalue),
            "ipw_triggered": ipw_triggered,
        }

    return results


def compute_ipw_csem(
    tier_results: Dict,
    tier_prompt_embeddings: Dict,
) -> Dict:
    """IPW-adjusted C_sem using logistic regression propensity scores.

    Only called when KS test shows significant distributional difference.

    Args:
        tier_results: {tier_name: {raw_cos_actual, raw_cos_random, n_pairs}}
        tier_prompt_embeddings: {tier_name: np.ndarray of shape (N, D)}

    Returns:
        {tier_name: ipw_c_sem_float}
    """
    tier_order = TIER_ORDER
    results = {}

    for target_tier in tier_order:
        # Collect all embeddings and labels
        all_embs = []
        all_labels = []
        for tier in tier_order:
            embs = tier_prompt_embeddings[tier]
            all_embs.append(embs)
            all_labels.extend([1 if tier == target_tier else 0] * len(embs))

        X = np.vstack(all_embs)
        y = np.array(all_labels)

        # Fit logistic regression for propensity score
        lr = LogisticRegression(max_iter=500, C=1.0)
        lr.fit(X, y)
        proba = lr.predict_proba(X)[:, 1]  # P(tier == target)

        # Extract proba for target tier samples only
        target_embs = tier_prompt_embeddings[target_tier]
        n_target = len(target_embs)

        # Get propensity scores for target tier
        target_start = sum(
            len(tier_prompt_embeddings[t]) for t in tier_order if t < target_tier
        )
        # Use logical indexing instead of offset
        target_mask = np.array(all_labels) == 1
        target_proba = proba[target_mask]

        # IPW weights: 1 / P(tier=t | x), truncate at 99th percentile
        weights = 1.0 / np.clip(target_proba, 1e-6, None)
        p99 = np.percentile(weights, 99)
        weights = np.clip(weights, None, p99)
        weights /= weights.sum()  # Normalize

        # IPW-weighted C_sem
        cos_actual = tier_results[target_tier]["raw_cos_actual"]
        cos_random = tier_results[target_tier]["raw_cos_random"]

        # Ensure weight array matches tier data length
        w = weights[:len(cos_actual)]
        if len(w) < len(cos_actual):
            w = np.ones(len(cos_actual)) / len(cos_actual)
        else:
            w = w[:len(cos_actual)]
            w /= w.sum()

        ipw_c_sem = float(
            np.sum(w * cos_actual) - np.sum(w * cos_random)
        )
        results[target_tier] = ipw_c_sem

    return results


def check_model_consistency(
    all_model_results: Dict,
    jt_alpha: float = JT_P_THRESHOLD,
    d_threshold: float = COHEN_D_THRESHOLD,
) -> Dict:
    """Check how many models pass the monotonicity gate.

    A model passes if: J-T p < jt_alpha AND max-tier Cohen's d >= d_threshold.
    Gate passes if: consistent_count >= MODEL_CONSISTENCY_THRESHOLD (2).

    Args:
        all_model_results: {model_slug: {jt: {...}, pairwise: {...}, tier_results: {...}}}
        jt_alpha: J-T significance threshold (default 0.05).
        d_threshold: Minimum Cohen's d (default 0.1).

    Returns:
        {consistent_count, consistent_models, gate_passed}
    """
    consistent_models = []

    for model_slug, model_data in all_model_results.items():
        jt = model_data.get("jt", {})
        pairwise = model_data.get("pairwise", {})

        jt_passes = jt.get("jt_pvalue", 1.0) < jt_alpha

        # Max Cohen's d across all tier pairs
        max_d = max(
            (abs(v.get("cohen_d", 0.0)) for v in pairwise.values()),
            default=0.0,
        )
        d_passes = max_d >= d_threshold

        if jt_passes and d_passes:
            consistent_models.append(model_slug)

    consistent_count = len(consistent_models)
    gate_passed = consistent_count >= MODEL_CONSISTENCY_THRESHOLD

    return {
        "consistent_count": consistent_count,
        "consistent_models": consistent_models,
        "gate_passed": gate_passed,
    }


def verify_mechanism_activated_m1(
    all_model_results: Dict,
    experiment_log: str,
) -> Tuple[bool, Dict]:
    """Verify h-m1 mechanism activation via 5 indicators.

    Indicators:
      1. tier_logs_found: FR-E3 logs present (C_sem computed per tier)
      2. all_tiers_have_pairs: Each tier has n_pairs >= 1000
      3. csem_differs_across_tiers: C_sem varies across tiers (std > 0)
      4. jt_computed: J-T test result present for at least one model
      5. all_models_ran: All 3 models have results

    Args:
        all_model_results: {model_slug: {tier_results, jt, pairwise}}
        experiment_log: String log output from experiment.

    Returns:
        Tuple of (all_activated: bool, indicators: dict)
    """
    # 1. tier_logs_found: Check experiment log for FR-E3 messages
    tier_logs_found = "C_sem computed" in experiment_log

    # 2. all_tiers_have_pairs
    all_tiers_have_pairs = True
    for model_slug, model_data in all_model_results.items():
        tier_results = model_data.get("tier_results", {})
        for tier in TIER_ORDER:
            if tier not in tier_results:
                all_tiers_have_pairs = False
                break
            if tier_results[tier].get("n_pairs", 0) < 1000:
                all_tiers_have_pairs = False
                break

    # 3. csem_differs_across_tiers
    csem_differs_across_tiers = False
    for model_slug, model_data in all_model_results.items():
        tier_results = model_data.get("tier_results", {})
        if len(tier_results) >= 2:
            csem_vals = [tier_results[t]["c_sem"] for t in TIER_ORDER if t in tier_results]
            if len(csem_vals) >= 2 and np.std(csem_vals) > 0:
                csem_differs_across_tiers = True
                break

    # 4. jt_computed
    jt_computed = any(
        "jt" in model_data and model_data["jt"]
        for model_data in all_model_results.values()
    )

    # 5. all_models_ran
    all_models_ran = len(all_model_results) >= 3

    indicators = {
        "tier_logs_found": tier_logs_found,
        "all_tiers_have_pairs": all_tiers_have_pairs,
        "csem_differs_across_tiers": csem_differs_across_tiers,
        "jt_computed": jt_computed,
        "all_models_ran": all_models_ran,
    }
    all_activated = all(indicators.values())
    return all_activated, indicators


# ============================================================================
# H-M2 EXTENSIONS: Directional Asymmetry Tests
# ============================================================================

import logging as _logging_m2
_logger_m2 = _logging_m2.getLogger(__name__)


def test_directional_asymmetry(  # noqa: F811
    bidir_results_by_tier: Dict,
    alpha: float = 0.05,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Dict:
    """Per-tier Mann-Whitney U one-sided test: H<-A > A<-H.

    Args:
        bidir_results_by_tier: {tier: {csem_H_given_A_array: np.ndarray[N,],
                                        csem_A_given_H_array: np.ndarray[N,], ...}}
        alpha: Significance threshold (default 0.05)
        n_bootstrap: Bootstrap samples for Cohen's d CI
        seed: Random seed

    Returns:
        {
            tier: {mw_statistic, p_value, cohen_d, cohen_d_ci, delta_asymmetry},
            'tiers_passing': int,
            'gate_passed': bool  # tiers_passing >= 2
        }
    """
    tiers_passing = 0
    result = {}

    for tier, data in bidir_results_by_tier.items():
        arr_H = data["csem_H_given_A_array"]
        arr_A = data["csem_A_given_H_array"]

        mw = stats.mannwhitneyu(arr_H, arr_A, alternative="greater")
        d, d_ci = bootstrap_cohen_d(arr_H, arr_A, n_bootstrap=n_bootstrap, seed=seed)
        delta = float(np.mean(arr_H) - np.mean(arr_A))

        _logger_m2.info(
            f"[FR-M2] Tier {tier}: C_sem^H<-A={np.mean(arr_H):.4f}, "
            f"C_sem^A<-H={np.mean(arr_A):.4f}, p={mw.pvalue:.4f}, d={d:.4f}"
        )

        if mw.pvalue < alpha:
            tiers_passing += 1

        result[tier] = {
            "mw_statistic": float(mw.statistic),
            "p_value": float(mw.pvalue),
            "cohen_d": float(d),
            "cohen_d_ci": d_ci.tolist() if hasattr(d_ci, "tolist") else list(d_ci),
            "delta_asymmetry": delta,
        }

    result["tiers_passing"] = tiers_passing
    result["gate_passed"] = tiers_passing >= 2

    return result


def compute_asymmetry_monotonicity(
    bidir_results_by_tier: Dict,
    tier_order: List[str],
) -> Dict:
    """Check if delta_asymmetry = H<-A - A<-H increases T1 < T2 < T3.

    Args:
        bidir_results_by_tier: {tier: {csem_H_given_A_array, csem_A_given_H_array, ...}}
        tier_order: List of tier names in ascending quality order.

    Returns:
        {
            'deltas': {tier: float},
            'is_monotonic': bool,
            'jt_result': Dict  # from jonckheere_terpstra_test on delta arrays
        }
    """
    deltas = {}
    for tier in tier_order:
        if tier not in bidir_results_by_tier:
            deltas[tier] = 0.0
            continue
        data = bidir_results_by_tier[tier]
        arr_H = data["csem_H_given_A_array"]
        arr_A = data["csem_A_given_H_array"]
        deltas[tier] = float(np.mean(arr_H) - np.mean(arr_A))

    # Check monotonicity: delta[T1] < delta[T2] < delta[T3]
    delta_vals = [deltas.get(t, 0.0) for t in tier_order]
    if len(delta_vals) >= 3:
        is_monotonic = bool(delta_vals[0] < delta_vals[1] < delta_vals[2])
    elif len(delta_vals) == 2:
        is_monotonic = bool(delta_vals[0] < delta_vals[1])
    else:
        is_monotonic = False

    # Run JT test on delta arrays (treat each tier's delta as a single-point group)
    # For JT, we use the per-pair difference arrays
    try:
        delta_arrays = []
        for tier in tier_order:
            if tier in bidir_results_by_tier:
                arr_H = bidir_results_by_tier[tier]["csem_H_given_A_array"]
                arr_A = bidir_results_by_tier[tier]["csem_A_given_H_array"]
                delta_arrays.append(arr_H - arr_A)
            else:
                delta_arrays.append(np.array([0.0]))

        if len(delta_arrays) >= 2:
            jt = stats.jonckheere_terpstra(*delta_arrays, alternative="increasing")
            jt_result = {
                "jt_statistic": float(jt.statistic),
                "jt_pvalue": float(jt.pvalue),
            }
        else:
            jt_result = {"jt_statistic": 0.0, "jt_pvalue": 1.0}
    except Exception as e:
        _logger_m2.warning(f"JT test failed in compute_asymmetry_monotonicity: {e}")
        jt_result = {"jt_statistic": 0.0, "jt_pvalue": 1.0}

    return {
        "deltas": deltas,
        "is_monotonic": is_monotonic,
        "jt_result": jt_result,
    }


def check_model_consistency_m2(
    all_model_bidir_results: Dict,
    alpha: float = 0.05,
) -> Dict:
    """Gate: >= 2/3 models show gate_passed=True in asymmetry_test.

    Args:
        all_model_bidir_results: {model_slug: {'asymmetry_test': {'tiers_passing': int,
                                                                    'gate_passed': bool, ...}}}
        alpha: Not used directly (gate uses asymmetry_test.gate_passed)

    Returns:
        {
            'models_passing': int,
            'passing_models': List[str],
            'gate_passed': bool  # models_passing >= 2
        }
    """
    passing_models = []

    for model_slug, model_data in all_model_bidir_results.items():
        asymmetry_test = model_data.get("asymmetry_test", {})
        if asymmetry_test.get("gate_passed", False):
            passing_models.append(model_slug)

    models_passing = len(passing_models)
    gate_passed = models_passing >= 2

    return {
        "models_passing": models_passing,
        "passing_models": passing_models,
        "gate_passed": gate_passed,
    }


def verify_mechanism_activated_m2(
    all_model_bidir_results: Dict,
    experiment_log: str,
) -> Tuple[bool, Dict]:
    """Verify h-m2 mechanism activation via 4 indicators.

    Indicators:
      1. both_directions_computed: all tiers have csem_H_given_A and csem_A_given_H
      2. shapes_match: H_given_A_array.shape == A_given_H_array.shape for all tiers
      3. asymmetry_nonzero: any |mean(H_given_A) - mean(A_given_H)| > 1e-6
      4. fr_m2_logs_found: '[FR-M2]' in experiment_log

    Args:
        all_model_bidir_results: {model_slug: {'tier_results': {tier: {...}}}}
        experiment_log: String log output from experiment.

    Returns:
        Tuple of (all_pass: bool, indicators: dict)
    """
    # 1. both_directions_computed
    both_directions_computed = True
    for model_slug, model_data in all_model_bidir_results.items():
        tier_results = model_data.get("tier_results", {})
        for tier in TIER_ORDER:
            if tier not in tier_results:
                both_directions_computed = False
                break
            tr = tier_results[tier]
            if "csem_H_given_A" not in tr or "csem_A_given_H" not in tr:
                both_directions_computed = False
                break
        if not both_directions_computed:
            break

    # 2. shapes_match
    shapes_match = True
    for model_slug, model_data in all_model_bidir_results.items():
        tier_results = model_data.get("tier_results", {})
        for tier in TIER_ORDER:
            if tier not in tier_results:
                shapes_match = False
                break
            tr = tier_results[tier]
            arr_H = tr.get("csem_H_given_A_array")
            arr_A = tr.get("csem_A_given_H_array")
            if arr_H is None or arr_A is None:
                shapes_match = False
                break
            if np.asarray(arr_H).shape != np.asarray(arr_A).shape:
                shapes_match = False
                break
        if not shapes_match:
            break

    # 3. asymmetry_nonzero
    asymmetry_nonzero = False
    for model_slug, model_data in all_model_bidir_results.items():
        tier_results = model_data.get("tier_results", {})
        for tier, tr in tier_results.items():
            h_val = tr.get("csem_H_given_A", 0.0)
            a_val = tr.get("csem_A_given_H", 0.0)
            if abs(h_val - a_val) > 1e-6:
                asymmetry_nonzero = True
                break
        if asymmetry_nonzero:
            break

    # 4. fr_m2_logs_found
    fr_m2_logs_found = "[FR-M2]" in experiment_log

    indicators = {
        "both_directions_computed": both_directions_computed,
        "shapes_match": shapes_match,
        "asymmetry_nonzero": asymmetry_nonzero,
        "fr_m2_logs_found": fr_m2_logs_found,
    }
    all_pass = all(indicators.values())
    return all_pass, indicators


def compute_ipw_csem_bidir(
    bidir_results_by_tier: Dict,
    tier_prompt_embeddings: Dict,
) -> Dict:
    """IPW-adjusted C_sem for both H<-A and A<-H using h-m1 compute_ipw_csem pattern.

    Calls compute_ipw_csem twice: once for H<-A direction using raw_cos_H_given_A,
    once for A<-H direction using raw_cos_A_given_H.

    Args:
        bidir_results_by_tier: {tier: {raw_cos_H_given_A, raw_cos_A_given_H, ...}}
        tier_prompt_embeddings: {tier: np.ndarray [N, D]}

    Returns:
        {tier: {ipw_csem_H_given_A: float, ipw_csem_A_given_H: float}}
    """
    from sklearn.linear_model import LogisticRegression

    tier_order = TIER_ORDER

    # Build H<-A tier_results format for compute_ipw_csem compatibility
    tier_results_H = {}
    tier_results_A = {}
    for tier in tier_order:
        if tier in bidir_results_by_tier:
            tr = bidir_results_by_tier[tier]
            tier_results_H[tier] = {
                "raw_cos_actual": tr.get("raw_cos_H_given_A", np.array([])),
                "raw_cos_random": tr.get("csem_H_given_A_array", np.array([])),
                "n_pairs": tr.get("n_pairs", 0),
            }
            tier_results_A[tier] = {
                "raw_cos_actual": tr.get("raw_cos_A_given_H", np.array([])),
                "raw_cos_random": tr.get("csem_A_given_H_array", np.array([])),
                "n_pairs": tr.get("n_pairs", 0),
            }

    ipw_H = compute_ipw_csem(tier_results_H, tier_prompt_embeddings)
    ipw_A = compute_ipw_csem(tier_results_A, tier_prompt_embeddings)

    result = {}
    for tier in tier_order:
        result[tier] = {
            "ipw_csem_H_given_A": ipw_H.get(tier, 0.0),
            "ipw_csem_A_given_H": ipw_A.get(tier, 0.0),
        }

    return result


# ============================================================================
# H-M3 EXTENSIONS: Delta CI, T-Test, Gate Evaluation, Mechanism Verification
# ============================================================================

def bootstrap_delta_ci(
    delta_values: np.ndarray,   # [N,] per-pair delta
    n_resamples: int = 1000,
    seed: int = 42,
) -> Tuple[float, float, float]:  # (mean_delta, ci_lower, ci_upper)
    """Bootstrap mean Δ with 95% CI using rng.choice (NOT rng.integers).

    CRITICAL: Uses rng.choice, NOT rng.integers (unlike bootstrap_c_sem).
    This is the h-m3 one-sample bootstrap for E[Δ].

    Args:
        delta_values: [N,] per-pair Δ = cos(H_next, A_chosen) - cos(H_next, A_rejected)
        n_resamples: Number of bootstrap resamples (default 1000).
        seed: Random seed (default 42).

    Returns:
        Tuple of (mean_delta, ci_lower, ci_upper) at 95% CI.
    """
    rng = np.random.default_rng(seed)
    n = len(delta_values)
    mean_delta = float(np.mean(delta_values))

    boot_means = np.empty(n_resamples)
    for i in range(n_resamples):
        sample = rng.choice(delta_values, size=n, replace=True)
        boot_means[i] = np.mean(sample)

    ci_lower = float(np.percentile(boot_means, 2.5))
    ci_upper = float(np.percentile(boot_means, 97.5))

    return mean_delta, ci_lower, ci_upper


def ttest_delta(
    delta_values: np.ndarray,  # [N,]
) -> Dict:  # {t_stat, p_value, df, significant}
    """One-sample t-test H0: E[Δ] = 0.

    Tests whether the mean delta is significantly different from zero.

    Args:
        delta_values: [N,] per-pair Δ array.

    Returns:
        Dict with t_stat, p_value, df (degrees of freedom), significant (bool).
    """
    result = stats.ttest_1samp(delta_values, popmean=0.0)
    return {
        "t_stat": float(result.statistic),
        "p_value": float(result.pvalue),
        "df": int(len(delta_values) - 1),
        "significant": bool(result.pvalue < 0.05),
    }


def cohens_d_onesample(
    delta_values: np.ndarray,  # [N,]
) -> float:
    """Cohen's d = mean(Δ) / std(Δ, ddof=1).

    One-sample Cohen's d for the delta distribution.
    Returns 0.0 if std is zero (degenerate case).

    Args:
        delta_values: [N,] per-pair Δ array.

    Returns:
        Cohen's d as float.
    """
    std = float(np.std(delta_values, ddof=1))
    if std == 0.0:
        return 0.0
    return float(np.mean(delta_values)) / std


def gate_evaluation_m3(
    ops_results: Dict,
    # {op_name: {mean_delta, ci_lower, ci_upper, n_pairs}}
    min_n_pairs: int = 1000,
) -> Dict:
    """Evaluate SHOULD_WORK gate for h-m3.

    Gate passes if:
    - ops_passing >= 2 (mean_delta > 0 AND ci_lower > 0)
    - NOT auto_demote (n_pairs_min >= min_n_pairs)

    Args:
        ops_results: {op_name: {mean_delta, ci_lower, ci_upper, n_pairs}}
        min_n_pairs: Minimum N_pairs threshold for auto-demote (default 1000).

    Returns:
        {gate_passed, ops_passing (int), ops_passing_list, auto_demote,
         n_pairs_min, gate_result}
    """
    ops_passing_list = []
    for op_name, res in ops_results.items():
        mean_d = res.get("mean_delta", 0.0)
        ci_lo = res.get("ci_lower", 0.0)
        if mean_d > 0 and ci_lo > 0:
            ops_passing_list.append(op_name)

    n_pairs_values = [res.get("n_pairs", 0) for res in ops_results.values()]
    n_pairs_min = int(min(n_pairs_values)) if n_pairs_values else 0

    auto_demote = n_pairs_min < min_n_pairs
    ops_passing = len(ops_passing_list)
    gate_passed = ops_passing >= 2 and not auto_demote
    gate_result = "PASS" if gate_passed else "FAIL"

    return {
        "gate_passed": gate_passed,
        "ops_passing": ops_passing,
        "ops_passing_list": ops_passing_list,
        "auto_demote": auto_demote,
        "n_pairs_min": n_pairs_min,
        "gate_result": gate_result,
    }


def check_model_consistency_m3(
    all_model_results: Dict,
    # {model_slug: {op_results: {op: {mean_delta, ...}}}}
    ops: List[str] = None,  # defaults to ["raw", "length_matched", "prompt_projected"]
) -> Dict:
    """Check consistency across models: >= 2/3 models show mean_delta > 0 in >= 2/3 ops.

    Args:
        all_model_results: {model_slug: {op_results: {op: {mean_delta, ...}}, ...}}
        ops: List of operationalization names to check (default: all 3).

    Returns:
        {models_consistent, consistent_models, gate_passed}
    """
    if ops is None:
        ops = ["raw", "length_matched", "prompt_projected"]

    consistent_models = []

    for model_slug, model_data in all_model_results.items():
        op_results = model_data.get("op_results", {})
        ops_positive = sum(
            1 for op in ops
            if op_results.get(op, {}).get("mean_delta", 0.0) > 0
        )
        if ops_positive >= 2:
            consistent_models.append(model_slug)

    models_consistent = len(consistent_models)
    gate_passed = models_consistent >= 2

    return {
        "models_consistent": models_consistent,
        "consistent_models": consistent_models,
        "gate_passed": gate_passed,
    }


def verify_mechanism_activated_m3(
    all_model_results: Dict,
    experiment_log: str,
) -> Tuple[bool, Dict]:
    """Verify h-m3 mechanism activation via 5 indicators.

    Indicators:
      1. n_pairs_sufficient: min n_pairs >= 1000 for at least one model
      2. delta_positive: mean_delta > 0 in at least one op for at least one model
      3. ci_lower_positive: ci_lower > 0 in at least one op for at least one model
      4. operationalizations_pass: ops_passing >= 2 for at least one model
      5. fr_m3_logs_found: '[FR-M3]' present in experiment_log

    Args:
        all_model_results: {model_slug: {op_results: {op: {...}}, gate: {...}}}
        experiment_log: String log output from experiment.

    Returns:
        Tuple of (all_activated: bool, indicators: dict)
    """
    # 1. n_pairs_sufficient
    n_pairs_sufficient = False
    for model_data in all_model_results.values():
        for op_res in model_data.get("op_results", {}).values():
            if op_res.get("n_pairs", 0) >= 1000:
                n_pairs_sufficient = True
                break
        if n_pairs_sufficient:
            break

    # 2. delta_positive
    delta_positive = False
    for model_data in all_model_results.values():
        for op_res in model_data.get("op_results", {}).values():
            if op_res.get("mean_delta", 0.0) > 0:
                delta_positive = True
                break
        if delta_positive:
            break

    # 3. ci_lower_positive
    ci_lower_positive = False
    for model_data in all_model_results.values():
        for op_res in model_data.get("op_results", {}).values():
            if op_res.get("ci_lower", 0.0) > 0:
                ci_lower_positive = True
                break
        if ci_lower_positive:
            break

    # 4. operationalizations_pass
    operationalizations_pass = False
    for model_data in all_model_results.values():
        gate = model_data.get("gate", {})
        if gate.get("ops_passing", 0) >= 2:
            operationalizations_pass = True
            break

    # 5. fr_m3_logs_found
    fr_m3_logs_found = "[FR-M3]" in experiment_log

    indicators = {
        "n_pairs_sufficient": n_pairs_sufficient,
        "delta_positive": delta_positive,
        "ci_lower_positive": ci_lower_positive,
        "operationalizations_pass": operationalizations_pass,
        "fr_m3_logs_found": fr_m3_logs_found,
    }
    all_activated = all(indicators.values())
    return all_activated, indicators
