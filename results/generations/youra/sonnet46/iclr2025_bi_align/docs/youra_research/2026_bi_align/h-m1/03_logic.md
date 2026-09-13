# Logic Design: h-m1

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1)
**Status**: API signatures verified from actual h-e1 code via direct file reads.
**Analyzed Path**: `docs/youra_research/20260315_bi_align/h-e1/code/`
**Relevant Symbols**:
- `data_loader.py`: `load_all_splits(cache_dir: str) -> List[dict]`, `extract_pairs(conversations: List[dict]) -> Dict`. Return dict keys: `h_next, a_actual, h_prompt, token_counts, jaccard_overlaps`.
- `embedder.py`: `Embedder.__init__(model_name, cache_dir)`, `Embedder.encode(texts: List[str], cache_key: str) -> np.ndarray`. Cache key pattern: `f"{prefix}_{model_slug}_{n_pairs}"` (suffix, NOT prefix).
- `accommodation.py`: `compute_cosine_similarities(h_next, a_actual, a_topic, a_random) -> Dict[str, np.ndarray]`, `compute_c_sem(cos_actual, cos_random) -> float`, `apply_residualization(cos_dict, token_counts, jaccard_overlaps) -> Dict`.
- `statistics.py`: `bootstrap_c_sem(cos_actual, cos_random, n_bootstrap=1000, seed=42) -> Tuple[float, np.ndarray]`, `bootstrap_cohen_d(arr_a, arr_b, n_bootstrap=1000, seed=42) -> Tuple[float, np.ndarray]`, `mann_whitney_test(arr_a, arr_b) -> Dict`, `run_all_tests(cos_actual, cos_topic, cos_random, n_pairs) -> Dict`, `verify_mechanism_activated(results: Dict, embeddings_computed: bool) -> Tuple[bool, Dict]`.
- `run_experiment.py`: `run_experiment(config: dict) -> ExperimentResults`, `run_robustness_checks(base_config: dict) -> dict`. Config dict keys: `cache_dir, model_name, output_dir, n_samples`.
- `controls.py` (from architecture): `build_random_control(ai_embeddings, seed=42)`, `build_topic_control(prompt_embeddings, ai_embeddings, k=5)`.

---

## External Dependencies API

### Verified Signatures from h-e1 Actual Code

```python
# From: h-e1/code/data_loader.py (ACTUAL CODE)
def load_all_splits(cache_dir: str) -> List[dict]:
    """Returns flat list of dicts with 'chosen' and 'rejected' keys."""
    ...

def extract_pairs(conversations: List[dict]) -> Dict:
    """Returns: {h_next, a_actual, h_prompt, token_counts, jaccard_overlaps}
    Each value is a list. Asserts len >= 1000.
    """
    ...

# From: h-e1/code/embedder.py (ACTUAL CODE)
class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = "embeddings"):
        ...
    def encode(self, texts: List[str], cache_key: str) -> np.ndarray:
        """Returns (N, D) float32 L2-normalized. Cache key = filename without .npy."""
        ...
    def load_cache(self, cache_key: str) -> Optional[np.ndarray]: ...
    def save_cache(self, embeddings: np.ndarray, cache_key: str) -> None: ...

# From: h-e1/code/accommodation.py (ACTUAL CODE)
def compute_cosine_similarities(
    h_next: np.ndarray,    # (N, D)
    a_actual: np.ndarray,  # (N, D)
    a_topic: np.ndarray,   # (N, D)
    a_random: np.ndarray,  # (N, D)
) -> Dict[str, np.ndarray]:
    """Returns: {cos_actual, cos_topic, cos_random} each shape (N,)"""
    ...

def compute_c_sem(cos_actual: np.ndarray, cos_random: np.ndarray) -> float:
    """C_sem = mean(cos_actual) - mean(cos_random)"""
    ...

# From: h-e1/code/statistics.py (ACTUAL CODE)
def bootstrap_c_sem(
    cos_actual: np.ndarray, cos_random: np.ndarray,
    n_bootstrap: int = 1000, seed: int = 42,
) -> Tuple[float, np.ndarray]:
    """Returns: (c_sem, ci_array) where ci_array shape (2,) = [lower, upper]"""
    ...

def bootstrap_cohen_d(
    arr_a: np.ndarray, arr_b: np.ndarray,
    n_bootstrap: int = 1000, seed: int = 42,
) -> Tuple[float, np.ndarray]:
    """Returns: (cohen_d, ci_array) shape (2,). Uses pooled std."""
    ...

def verify_mechanism_activated(
    results: Dict,
    embeddings_computed: bool,   # ← 2nd positional arg, NOT keyword (verified!)
) -> Tuple[bool, Dict]:
    """5 indicators. Returns (all_activated, indicators_dict)."""
    ...

# From: h-e1/code/run_experiment.py (ACTUAL CODE)
def run_experiment(config: dict) -> ExperimentResults:
    """config keys: cache_dir, model_name, output_dir, n_samples"""
    ...
```

**Verified from**: actual file reads of all 5 h-e1 source files (not spec).
**Critical**: `verify_mechanism_activated` takes `embeddings_computed` as 2nd positional arg. Cache key suffix is `f"{prefix}_{model_slug}_{n_pairs}"` — h-m1 extends to `f"{prefix}_{model_slug}_{tier_slug}_{n_pairs}"`.

---

## Subtask Designs

### Epic A-7: Multi-Model Orchestrator [4 subtasks, budget: 4]

#### L-7-1: run_tier_experiment [Complexity: 7, Budget: 4]

Applied: Standard scipy statistical test wrapping pattern; nested multi-model-tier loop from h-e1 run_robustness_checks pattern.

```python
# run_experiment.py

HYPOTHESIS_ID = "h-m1"
TIER_ORDER = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]
TIER_SLUGS = {
    "helpful-base": "base",
    "helpful-rejection-sampled": "rs",
    "helpful-online": "online",
}
MODEL_CONFIGS = [
    {"name": "all-MiniLM-L6-v2",         "slug": "minilm",     "role": "primary"},
    {"name": "paraphrase-MiniLM-L6-v2",   "slug": "paraphrase", "role": "robustness1"},
    {"name": "all-mpnet-base-v2",          "slug": "mpnet",      "role": "robustness2"},
]

def run_tier_experiment(config: dict) -> dict:
    """Main entry point: 3-model x 3-tier nested loop.

    Args:
        config: {cache_dir, output_dir, dry_run (bool), n_per_tier (int|None)}
    Returns:
        all_results: {model_slug: {tier: tier_metrics_dict}, 'gate': gate_dict,
                      'mechanism': mechanism_dict, 'ks': ks_dict}
    Raises:
        AssertionError if any tier has < 1000 pairs.
    """
    ...
```

Pseudo-code:
```
1. logger = _setup_logging(config['output_dir'])
2. tier_pairs = split_by_tier(config['cache_dir'])          # {tier: pairs_dict}
   - if dry_run: subsample first n_per_tier per tier
3. tier_prompt_embs = {}  # for KS test (computed during model loop)
4. all_model_results = {}
5. FOR model_cfg IN MODEL_CONFIGS:
     model_results = run_single_model(model_cfg, tier_pairs, output_dir, dry_run)
     all_model_results[model_cfg['slug']] = model_results
     # collect prompt embeddings from primary model for KS
     if model_cfg['role'] == 'primary':
         tier_prompt_embs = model_results['tier_prompt_embs']
6. ks_result = ks_test_tier_distributions(tier_prompt_embs, TIER_ORDER)
7. ipw_csem = {}
   if any(r['ipw_triggered'] for r in ks_result.values()):
       ipw_csem = compute_ipw_csem(all_model_results['minilm'], tier_prompt_embs)
8. gate = evaluate_gate(all_model_results)
9. mechanism = verify_mechanism_activated_m1(all_model_results, experiment_log_path)
10. figures_dir = os.path.join(output_dir, 'figures'); os.makedirs(figures_dir, exist_ok=True)
11. generate all 7 plot types
12. write_results_yaml(all_model_results, gate, output_dir)
13. generate_validation_report(all_model_results, gate, output_dir + '/04_validation.md')
14. return {**all_model_results, 'gate': gate, 'mechanism': mechanism, 'ks': ks_result}
```

**Subtasks**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | run_tier_experiment | Main entry point, 3-model x 3-tier nested loop |
| L-7-2 | evaluate_gate | MUST_WORK gate: J-T p < 0.05 AND d >= 0.1 in >= 2/3 models |
| L-7-3 | generate_validation_report | Write 04_validation.md |
| L-7-4 | run_dry_run | Fast pre-flight with n_per_tier=500 |

---

#### L-7-2: evaluate_gate

```python
from dataclasses import dataclass

@dataclass
class GateResult:
    gate_passed: bool          # consistent_count >= 2
    consistent_count: int      # models satisfying J-T p < threshold_jt_p AND d >= threshold_d
    consistent_models: list    # list of model slugs
    details: dict              # per-model {jt_pvalue, max_cohen_d, passed}

def evaluate_gate(
    results: dict,
    threshold_jt_p: float = 0.05,
    threshold_d: float = 0.1,
) -> GateResult:
    """MUST_WORK gate: check J-T p < threshold_jt_p AND Cohen's d >= threshold_d in >= 2/3 models.

    Args:
        results: {model_slug: {'jt_pvalue': float, 'pairwise': {pair: {'cohen_d': float}}}}
        threshold_jt_p: J-T p-value threshold (default 0.05)
        threshold_d: minimum Cohen's d (default 0.1)
    Returns:
        GateResult with gate_passed, consistent_count, consistent_models, details.
    """
    ...
```

Pseudo-code:
```
consistent = []
details = {}
FOR slug, model_res IN results.items():
    jt_p = model_res['jt_pvalue']
    max_d = max(v['cohen_d'] for v in model_res['pairwise'].values())
    passed = jt_p < threshold_jt_p and max_d >= threshold_d
    if passed: consistent.append(slug)
    details[slug] = {'jt_pvalue': jt_p, 'max_cohen_d': max_d, 'passed': passed}
return GateResult(gate_passed=len(consistent)>=2, consistent_count=len(consistent),
                  consistent_models=consistent, details=details)
```

---

#### L-7-3: generate_validation_report

```python
def generate_validation_report(
    results: dict,
    gate: GateResult,
    output_path: str,
) -> None:
    """Write 04_validation.md with gate evaluation and per-model metrics.

    Args:
        results: all_model_results dict from run_tier_experiment
        gate: GateResult from evaluate_gate
        output_path: absolute path to write 04_validation.md
    Returns:
        None. Writes file to output_path.
    """
    ...
```

Pseudo-code:
```
lines = ["# Validation Report: h-m1", ...]
lines += gate summary table (gate_passed, consistent_count)
FOR each model: lines += per-model J-T p, max Cohen's d, tier C_sem table
lines += mechanism activation indicators
write '\n'.join(lines) to output_path
```

---

#### L-7-4: run_dry_run

```python
def run_dry_run(config: dict, n_per_tier: int = 500) -> dict:
    """Fast pre-flight check: first n_per_tier pairs per tier, all 3 models.

    Args:
        config: same as run_tier_experiment config
        n_per_tier: pairs per tier (default 500)
    Returns:
        Same structure as run_tier_experiment output.
    Raises:
        RuntimeError if any tier yields < 100 pairs after subsample.
    """
    dry_config = {**config, "dry_run": True, "n_per_tier": n_per_tier}
    return run_tier_experiment(dry_config)
```

---

### Epic A-4: J-T + Bonferroni [3 subtasks, budget: 3]

#### L-4-1: jonckheere_terpstra_test

```python
# statistics.py

from scipy import stats
from dataclasses import dataclass

@dataclass
class JTResult:
    jt_statistic: float
    jt_pvalue: float
    alternative: str   # 'increasing'
    tier_order: list   # tier names in order

def jonckheere_terpstra_test(
    tier_arrays: list[np.ndarray],
    alternative: str = "increasing",
) -> JTResult:
    """Jonckheere-Terpstra monotonicity test on ordered raw cosine arrays.

    Args:
        tier_arrays: [arr_T1, arr_T2, arr_T3] each shape (N_i,) — raw cos_actual per tier
        alternative: 'increasing' (T1 < T2 < T3 monotonicity)
    Returns:
        JTResult with jt_statistic, jt_pvalue.
    Raises:
        ValueError if len(tier_arrays) < 2.
    Notes:
        Input is raw cosine arrays NOT OLS residuals (zero mean by construction).
    """
    ...
```

Pseudo-code:
```
result = scipy.stats.jonckheere_terpstra(*tier_arrays, alternative=alternative)
return JTResult(jt_statistic=result.statistic, jt_pvalue=result.pvalue,
                alternative=alternative, tier_order=TIER_ORDER)
```

---

#### L-4-2: bonferroni_mannwhitney

```python
@dataclass
class MWResult:
    pair: tuple             # e.g. ('helpful-base', 'helpful-rejection-sampled')
    pair_key: str           # e.g. 'base_vs_rs'
    mw_statistic: float
    mw_pvalue: float
    bonferroni_alpha: float # 0.05 / 3 = 0.0167
    bonferroni_significant: bool

def bonferroni_mannwhitney(
    arrays: list[np.ndarray],
    alpha: float = 0.05,
) -> list[MWResult]:
    """Pairwise Mann-Whitney U tests with Bonferroni correction for 3 tiers.

    Args:
        arrays: [arr_T1, arr_T2, arr_T3] each shape (N_i,) — raw cos_actual per tier
        alpha: family-wise alpha before correction (default 0.05)
    Returns:
        List of 3 MWResult objects for pairs (T1,T2), (T2,T3), (T1,T3).
    """
    ...
```

Pseudo-code:
```
bonferroni_alpha = alpha / 3   # = 0.0167
pairs = [(0,1,'T1_vs_T2'), (1,2,'T2_vs_T3'), (0,2,'T1_vs_T3')]
results = []
FOR (i, j, key) IN pairs:
    res = scipy.stats.mannwhitneyu(arrays[i], arrays[j], alternative='two-sided')
    results.append(MWResult(pair=(TIER_ORDER[i], TIER_ORDER[j]), pair_key=key,
                            mw_statistic=res.statistic, mw_pvalue=res.pvalue,
                            bonferroni_alpha=bonferroni_alpha,
                            bonferroni_significant=res.pvalue < bonferroni_alpha))
return results
```

---

#### L-4-3: bootstrap_cohens_d_all_pairs

```python
def bootstrap_cohens_d_all_pairs(
    tier_results: dict,
    n: int = 1000,
    seed: int = 42,
) -> dict:
    """Bootstrap Cohen's d for all tier-pair x model combinations.

    Args:
        tier_results: {tier_name: {'raw_cos_actual': np.ndarray shape (N_i,)}}
        n: bootstrap resamples (default 1000)
        seed: random seed (default 42)
    Returns:
        {pair_key: {'cohen_d': float, 'ci': [lower, upper], 'pair': (t_a, t_b)}}
        pair_key format: 'base_vs_rs', 'rs_vs_online', 'base_vs_online'
    """
    ...
```

Pseudo-code:
```
pairs = [('helpful-base','helpful-rejection-sampled','base_vs_rs'),
         ('helpful-rejection-sampled','helpful-online','rs_vs_online'),
         ('helpful-base','helpful-online','base_vs_online')]
out = {}
FOR (t_a, t_b, key) IN pairs:
    arr_a = tier_results[t_a]['raw_cos_actual']   # (N_a,)
    arr_b = tier_results[t_b]['raw_cos_actual']   # (N_b,)
    d, ci = bootstrap_cohen_d(arr_a, arr_b, n_bootstrap=n, seed=seed)
    out[key] = {'cohen_d': d, 'ci': ci.tolist(), 'pair': (t_a, t_b)}
return out
```

**Subtasks**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | jonckheere_terpstra_test | Wrap scipy.stats.jonckheere_terpstra, return JTResult |
| L-4-2 | bonferroni_mannwhitney | 3 pairwise tests, Bonferroni alpha/3 threshold |
| L-4-3 | bootstrap_cohens_d_all_pairs | Bootstrap d for all tier pairs from raw cos arrays |

---

### Epic A-3: Tier C_sem Matrix [2 subtasks, budget: 2]

#### L-3-1: compute_tier_csem_matrix

```python
# accommodation.py

def compute_tier_csem_matrix(
    tier_pairs: dict,
    model: object,
    knn_k: int = 5,
    seed: int = 42,
) -> dict:
    """Compute C_sem for all 3 tiers for a single SBERT model.

    Args:
        tier_pairs: {tier_name: {h_next, a_actual, h_prompt, token_counts, jaccard_overlaps}}
        model: Embedder instance initialized with the target model
        knn_k: KNN k for topic control (default 5, n_jobs=1 ALWAYS)
        seed: shuffle seed for random control (default 42)
    Returns:
        {tier_name: {c_sem, cos_actual_mean, cos_random_mean, cos_topic_mean,
                     n_pairs, raw_cos_actual (N,), raw_cos_random (N,),
                     raw_cos_topic (N,), c_sem_ci [2,]}}
    Raises:
        AssertionError if any tier n_pairs < 1000.
    """
    ...
```

Array shapes:
| Variable | Shape | Note |
|----------|-------|------|
| h_next_emb | (N_tier, D) | D=384 or 768 |
| a_actual_emb | (N_tier, D) | |
| raw_cos_actual | (N_tier,) | raw, NOT residualized |

Pseudo-code:
```
results = {}
FOR tier_name IN TIER_ORDER:
    pairs = tier_pairs[tier_name]
    N = len(pairs['h_next'])
    assert N >= 1000
    tier_slug = TIER_SLUGS[tier_name]
    n_pairs = N

    h_next_emb   = model.encode(pairs['h_next'],   f"h_next_{model.model_slug}_{tier_slug}_{n_pairs}")
    a_actual_emb = model.encode(pairs['a_actual'],  f"a_actual_{model.model_slug}_{tier_slug}_{n_pairs}")
    h_prompt_emb = model.encode(pairs['h_prompt'],  f"h_prompt_{model.model_slug}_{tier_slug}_{n_pairs}")

    a_random_emb = build_random_control(a_actual_emb, seed=seed)
    a_topic_emb  = build_topic_control(h_prompt_emb, a_actual_emb, k=knn_k)  # n_jobs=1

    cos_dict = compute_cosine_similarities(h_next_emb, a_actual_emb, a_topic_emb, a_random_emb)
    c_sem = compute_c_sem(cos_dict['cos_actual'], cos_dict['cos_random'])
    _, c_sem_ci = bootstrap_c_sem(cos_dict['cos_actual'], cos_dict['cos_random'])

    logger.info(f"Tier {tier_name} C_sem computed: {c_sem:.4f}")  # FR-E3 activation log

    results[tier_name] = {
        'c_sem': c_sem,
        'c_sem_ci': c_sem_ci,
        'cos_actual_mean': float(cos_dict['cos_actual'].mean()),
        'cos_random_mean': float(cos_dict['cos_random'].mean()),
        'cos_topic_mean':  float(cos_dict['cos_topic'].mean()),
        'n_pairs': n_pairs,
        'raw_cos_actual': cos_dict['cos_actual'],
        'raw_cos_random': cos_dict['cos_random'],
        'raw_cos_topic':  cos_dict['cos_topic'],
        'h_prompt_emb': h_prompt_emb,   # retained for KS test
    }
return results
```

---

#### L-3-2: aggregate_model_results

```python
def aggregate_model_results(all_model_results: dict) -> dict:
    """Combine 3-model results into C_sem summary matrix.

    Args:
        all_model_results: {model_slug: {tier_name: tier_metrics_dict}}
    Returns:
        {'csem_matrix': {model_slug: {tier_name: c_sem}},
         'consistency': check_model_consistency(all_model_results) output}
    """
    ...
```

Pseudo-code:
```
csem_matrix = {}
FOR model_slug, tier_results IN all_model_results.items():
    csem_matrix[model_slug] = {t: tier_results[t]['c_sem'] for t in TIER_ORDER}
consistency = check_model_consistency(all_model_results)
return {'csem_matrix': csem_matrix, 'consistency': consistency}
```

**Subtasks**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_tier_csem_matrix | Per-tier encode + controls + C_sem for one model |
| L-3-2 | aggregate_model_results | Combine 3-model results into summary matrix |

---

### Epic A-5: KS Test + IPW [2 subtasks, budget: 2]

#### L-5-1: ks_test_tier_distributions

```python
# statistics.py

@dataclass
class KSResult:
    pair_results: dict   # {pair_key: {ks_statistic, ks_pvalue, ipw_triggered}}
    any_triggered: bool  # True if any KS p < 0.05

def ks_test_tier_distributions(
    tier_prompt_embs: dict,
    tier_order: list,
) -> KSResult:
    """KS test on prompt embedding PCA-1 distributions across all 3 tier pairs.

    Args:
        tier_prompt_embs: {tier_name: np.ndarray shape (N_i, D)}
        tier_order: ['helpful-base', 'helpful-rejection-sampled', 'helpful-online']
    Returns:
        KSResult with pair_results and any_triggered flag.
    Notes:
        Uses first PCA component (n_components=1) for 1D KS test.
        scipy.stats.ks_2samp(arr_a, arr_b, alternative='two-sided').
    """
    ...
```

Pseudo-code:
```
from sklearn.decomposition import PCA
pca = PCA(n_components=1, random_state=42)
# fit on concatenated embeddings for consistent projection
all_embs = np.concatenate(list(tier_prompt_embs.values()), axis=0)
pca.fit(all_embs)
tier_proj = {t: pca.transform(tier_prompt_embs[t]).ravel() for t in tier_order}

pairs = [('helpful-base','helpful-rejection-sampled','base_vs_rs'),
         ('helpful-rejection-sampled','helpful-online','rs_vs_online'),
         ('helpful-base','helpful-online','base_vs_online')]
pair_results = {}
FOR (t_a, t_b, key) IN pairs:
    res = scipy.stats.ks_2samp(tier_proj[t_a], tier_proj[t_b], alternative='two-sided')
    pair_results[key] = {'ks_statistic': res.statistic, 'ks_pvalue': res.pvalue,
                          'ipw_triggered': res.pvalue < 0.05}
any_triggered = any(v['ipw_triggered'] for v in pair_results.values())
return KSResult(pair_results=pair_results, any_triggered=any_triggered)
```

---

#### L-5-2: compute_ipw_csem

```python
def compute_ipw_csem(
    tier_pairs: dict,
    ks_result: KSResult,
    model: object,
) -> dict:
    """IPW-weighted C_sem recomputation if KS test triggered.

    Args:
        tier_pairs: {tier_name: {raw_cos_actual (N,), raw_cos_random (N,), h_prompt_emb (N, D)}}
        ks_result: KSResult from ks_test_tier_distributions
        model: Embedder instance (used to access model_slug for logging)
    Returns:
        {tier_name: {'ipw_c_sem': float, 'raw_c_sem': float, 'n_eff': float}}
    Notes:
        IPW weights: logistic regression P(tier_label | prompt_emb).
        w_i = 1 / P(tier | prompt_emb_i). Truncate weights at 99th percentile.
        Only called if ks_result.any_triggered is True.
    """
    ...
```

Pseudo-code:
```
from sklearn.linear_model import LogisticRegression
results = {}
FOR tier_name IN TIER_ORDER:
    h_prompt_embs_tier = tier_pairs[tier_name]['h_prompt_emb']   # (N, D)
    raw_cos_actual = tier_pairs[tier_name]['raw_cos_actual']      # (N,)
    raw_cos_random = tier_pairs[tier_name]['raw_cos_random']      # (N,)

    # Build multi-class propensity model once (shared across tiers)
    # Reuse cached propensity_scores if already computed
    p_tier = propensity_scores[tier_name]   # (N,) probability of this tier
    w = 1.0 / np.clip(p_tier, 1e-6, None)
    clip_thresh = np.percentile(w, 99)
    w = np.minimum(w, clip_thresh)
    w = w / w.sum()   # normalize to sum=1

    ipw_c_sem = float(np.sum(w * raw_cos_actual) - np.sum(w * raw_cos_random))
    raw_c_sem = float(np.mean(raw_cos_actual) - np.mean(raw_cos_random))
    n_eff = float(1.0 / np.sum(w**2))

    results[tier_name] = {'ipw_c_sem': ipw_c_sem, 'raw_c_sem': raw_c_sem, 'n_eff': n_eff}
return results
```

**Subtasks**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | ks_test_tier_distributions | PCA-1 KS test across 3 tier-pairs of prompt embeddings |
| L-5-2 | compute_ipw_csem | IPW-weighted C_sem using logistic propensity model |

---

## Applied Patterns

Applied: nested_multi_model_loop — outer MODEL_CONFIGS loop, inner TIER_ORDER loop; collect all before gate.
Applied: tier_aware_cache_key — cache key extended to `f"{prefix}_{model_slug}_{tier_slug}_{n_pairs}"`.
Applied: raw_cosine_stats_not_residuals — J-T and Mann-Whitney on raw cos_actual arrays only.
Applied: knn_n_jobs_1_constraint — build_topic_control called with n_jobs=1 enforced (OpenBLAS crash prevention).
Applied: bonferroni_3pair_correction — alpha/3 = 0.0167 threshold for 3 pairwise tier comparisons.
Applied: pca1_ks_test — PCA first component for 1D KS test on high-dimensional prompt embeddings.
