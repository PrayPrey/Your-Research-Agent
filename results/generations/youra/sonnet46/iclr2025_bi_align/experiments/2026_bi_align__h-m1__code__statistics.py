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
