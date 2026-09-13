# Logic: h-m2 — Bidirectional C_sem Directional Asymmetry

**Hypothesis**: h-m2 (MECHANISM, INCREMENTAL)
**Date**: 2026-03-15
**Base**: h-m1 (VALIDATED)
**Budget**: 13 subtasks (A-5: 4, A-7: 4, A-4: 3, A-9: 2)

Applied: copy-extend pattern (h-m1 base signatures verified from actual source files)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified via direct Read tool on actual h-m1 source files (Serena project not active for this path — used Read tool as fallback, which provides equivalent verification fidelity)
**Analyzed Path**: `docs/youra_research/20260315_bi_align/h-m1/code/`
**Relevant Symbols**:
- `compute_tier_csem_matrix(tier_pairs, embedder, controls_fn_random, controls_fn_topic, seed=42)` → `Dict[str, Dict]`
- `compute_cosine_similarities(h_next, a_actual, a_topic, a_random)` → `Dict[str, np.ndarray]`
- `compute_c_sem(cos_actual, cos_random)` → `float`
- `apply_residualization(cos_dict, token_counts, jaccard_overlaps)` → `Dict[str, np.ndarray]`
- `aggregate_model_results(all_model_results)` → `Dict`
- `verify_mechanism_activated_m1(all_model_results, experiment_log)` → `Tuple[bool, Dict]`
- `check_model_consistency(all_model_results, jt_alpha, d_threshold)` → `Dict` (keys: `consistent_count`, `consistent_models`, `gate_passed`)
- `run_tier_experiment(config: Dict)` → `Dict` (config keys: `cache_dir`, `embeddings_dir`, `dry_run`, `n_samples_dry_run`)
- `save_results_json(results, output_path)` → `None`  ← NOTE: h-m2 version returns str

---

## External Dependencies API (Base Hypothesis: h-m1)

Signatures verified from actual h-m1 code (NOT specs):

```python
# From: h-m1/code/accommodation.py (ACTUAL CODE)
def compute_tier_csem_matrix(
    tier_pairs: Dict,
    embedder,
    controls_fn_random: Callable,   # build_random_control(ai_emb, seed=42)
    controls_fn_topic: Callable,    # build_topic_control(prompt_emb, ai_emb)
    seed: int = 42,
) -> Dict[str, Dict]:
    # Returns: {tier: {c_sem, cos_actual_mean, cos_random_mean,
    #                  raw_cos_actual, raw_cos_random, n_pairs}}
    ...

def compute_cosine_similarities(
    h_next: np.ndarray,    # [N, D]
    a_actual: np.ndarray,  # [N, D]
    a_topic: np.ndarray,   # [N, D]
    a_random: np.ndarray,  # [N, D]
) -> Dict[str, np.ndarray]:
    # Returns: {cos_actual, cos_topic, cos_random} each [N,]
    ...

def apply_residualization(
    cos_dict: Dict[str, np.ndarray],
    token_counts: List[int],
    jaccard_overlaps: List[float],
) -> Dict[str, np.ndarray]: ...

# From: h-m1/code/statistics.py (ACTUAL CODE)
def verify_mechanism_activated_m1(
    all_model_results: Dict,
    experiment_log: str,
) -> Tuple[bool, Dict]: ...

def check_model_consistency(
    all_model_results: Dict,
    jt_alpha: float = 0.05,       # param name is jt_alpha (not alpha)
    d_threshold: float = 0.1,
) -> Dict:
    # Returns: {consistent_count, consistent_models, gate_passed}
    ...

def ks_test_tier_distributions(
    tier_prompt_embeddings: Dict,
    tier_order: List[str],
) -> Dict:
    # Returns: {pair_key: {ks_statistic, ks_pvalue, ipw_triggered}}
    ...

def compute_ipw_csem(
    tier_results: Dict,             # {tier: {raw_cos_actual, raw_cos_random, n_pairs}}
    tier_prompt_embeddings: Dict,   # {tier: np.ndarray [N, D]}
) -> Dict:
    # Returns: {tier_name: ipw_c_sem_float}
    ...

def bootstrap_cohen_d(
    arr_a: np.ndarray,
    arr_b: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Tuple[float, np.ndarray]: ...

# From: h-m1/code/run_experiment.py (ACTUAL CODE)
def run_tier_experiment(config: Dict) -> Dict:
    # config keys: cache_dir, embeddings_dir, dry_run, n_samples_dry_run
    # Returns: {all_model_results, consistency, pairwise_all,
    #           ks_results, ipw_csem, mechanism, experiment_log}
    ...

def save_results_json(results: Dict, output_path: str) -> None: ...
# CRITICAL: h-m1 takes output_path (file), h-m2 version takes output_dir (dir) and returns str
```

**Verified from**: `h-m1/code/accommodation.py`, `h-m1/code/statistics.py`, `h-m1/code/run_experiment.py` (actual implementation)

**Critical notes**:
- `build_topic_control` uses `NearestNeighbors(n_jobs=1)` — must remain `n_jobs=1` at 155k scale
- `check_model_consistency` param is `jt_alpha` not `alpha`
- h-m1 `save_results_json(results, output_path)` → `None`; h-m2 redesigns as `save_results_json(results, output_dir)` → `str`

---

## A-4: Extend accommodation.py [Complexity: 14, Budget: 3 subtasks]

Applied: copy-extend pattern (bidirectional direction via separate cosine computation)

### API Signatures

```python
# accommodation.py — NEW functions for h-m2

def compute_h_given_a_csem_array(
    emb_h_next: np.ndarray,      # [N, D] L2-normalized
    emb_a_curr: np.ndarray,      # [N, D] L2-normalized
    emb_a_shuffle: np.ndarray,   # [N, D] topic-matched shuffle of A_curr
) -> np.ndarray:
    """Per-pair C_sem^H<-A = cos(H_{t+1}, A_t) - cos(H_{t+1}, A_t[shuffle]).
    Returns: [N,]
    """
    ...

def compute_a_given_h_csem_array(
    emb_a_next: np.ndarray,      # [N, D] L2-normalized
    emb_h_curr: np.ndarray,      # [N, D] L2-normalized
    emb_h_shuffle: np.ndarray,   # [N, D] topic-matched shuffle of H_curr
) -> np.ndarray:
    """Per-pair C_sem^A<-H = cos(A_{t+1}, H_t) - cos(A_{t+1}, H_t[shuffle_A]).
    Returns: [N,]
    """
    ...

def compute_bidirectional_csem_per_tier(
    tier_pairs: Dict,
    embedder,
    controls_fn_random: Callable,
    controls_fn_topic: Callable,
    ipw_weights: Optional[Dict[str, np.ndarray]] = None,
    seed: int = 42,
) -> Dict[str, Dict]:
    """Compute both H<-A and A<-H C_sem per tier. Logs [FR-M2] prefix.

    For each tier:
      H<-A: cos(H_{t+1}, A_t) - cos(H_{t+1}, A_t[shuffle_H])
      A<-H: cos(A_{t+1}, H_t) - cos(A_{t+1}, H_t[shuffle_A])
    Logs: [FR-M2] Tier {tier}: C_sem^H<-A={:.4f}, C_sem^A<-H={:.4f}

    Returns:
        {tier: {
            csem_H_given_A: float,             # mean of per-pair H<-A
            csem_A_given_H: float,             # mean of per-pair A<-H
            csem_H_given_A_array: np.ndarray,  # [N,] per-pair H<-A diffs
            csem_A_given_H_array: np.ndarray,  # [N,] per-pair A<-H diffs
            raw_cos_H_given_A: np.ndarray,     # [N,] cos(H_next, A_curr)
            raw_cos_A_given_H: np.ndarray,     # [N,] cos(A_next, H_curr)
            n_pairs: int,
        }}
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| emb_h_next | [N, D] | H_{t+1} embeddings, L2-normalized |
| emb_a_curr | [N, D] | A_t embeddings (h-m1 reuse) |
| emb_a_next | [N, D] | A_{t+1} embeddings (new for A<-H) |
| emb_h_curr | [N, D] | H_t embeddings (new for A<-H) |
| csem_*_array | [N,] | Per-pair C_sem (elementwise difference) |

### Pseudo-code (compute_bidirectional_csem_per_tier)

```
for tier in TIER_ORDER:
    pairs = tier_pairs[tier]
    N = len(pairs['h_next'])

    # H<-A direction (reuse h-m1 logic)
    emb_h_next  = embedder.encode_tier(pairs['h_next'],   prefix='h',      tier=tier, n_pairs=N)
    emb_a_curr  = embedder.encode_tier(pairs['a_actual'], prefix='a',      tier=tier, n_pairs=N)
    emb_p       = embedder.encode_tier(pairs['h_prompt'], prefix='p',      tier=tier, n_pairs=N)
    emb_a_shuffle = build_topic_control(emb_p, emb_a_curr)   # n_jobs=1
    h_given_a   = compute_h_given_a_csem_array(emb_h_next, emb_a_curr, emb_a_shuffle)  # [N,]

    # A<-H direction (new)
    emb_a_next  = embedder.encode_tier(pairs['a_next'],   prefix='a_next', tier=tier, n_pairs=N)
    emb_h_curr  = embedder.encode_tier(pairs['h_curr'],   prefix='h_curr', tier=tier, n_pairs=N)
    emb_h_shuffle = build_topic_control(emb_p, emb_h_curr)   # n_jobs=1
    a_given_h   = compute_a_given_h_csem_array(emb_a_next, emb_h_curr, emb_h_shuffle)  # [N,]

    if ipw_weights and tier in ipw_weights:
        w = ipw_weights[tier]  # [N,]
        csem_H = float(np.sum(w * h_given_a))
        csem_A = float(np.sum(w * a_given_h))
    else:
        csem_H = float(np.mean(h_given_a))
        csem_A = float(np.mean(a_given_h))

    logger.info(f"[FR-M2] Tier {tier}: C_sem^H<-A={csem_H:.4f}, C_sem^A<-H={csem_A:.4f}")
    results[tier] = {csem_H_given_A: csem_H, csem_A_given_H: csem_A,
                     csem_H_given_A_array: h_given_a, csem_A_given_H_array: a_given_h,
                     raw_cos_H_given_A: cos(H_next, A_curr), raw_cos_A_given_H: cos(A_next, H_curr),
                     n_pairs: N}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | per-pair helper functions | `compute_h_given_a_csem_array`, `compute_a_given_h_csem_array` |
| L-4-2 | bidirectional main loop | `compute_bidirectional_csem_per_tier` — both directions + [FR-M2] logging |
| L-4-3 | verify_bidirectional_mechanism | Check `[FR-M2]` logs present; shapes match; asymmetry nonzero |

---

## A-5: Extend statistics.py [Complexity: 16, Budget: 4 subtasks]

Applied: copy-extend pattern (one-sided Mann-Whitney extension of h-m1 `mann_whitney_test` pattern)

### API Signatures

```python
# statistics.py — NEW functions for h-m2

def test_directional_asymmetry(
    bidir_results_by_tier: Dict,
    alpha: float = 0.05,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Dict:
    """Per-tier Mann-Whitney U one-sided: H<-A > A<-H.

    Input: {tier: {csem_H_given_A_array: np.ndarray[N,], csem_A_given_H_array: np.ndarray[N,], ...}}
    Returns: {
        tier: {mw_statistic, p_value, cohen_d, cohen_d_ci, delta_asymmetry},
        'tiers_passing': int,
        'gate_passed': bool   # tiers_passing >= 2
    }
    Logs: [FR-M2] Tier {tier}: C_sem^H<-A={:.4f}, C_sem^A<-H={:.4f}, p={:.4f}, d={:.4f}
    """
    ...

def compute_asymmetry_monotonicity(
    bidir_results_by_tier: Dict,
    tier_order: List[str],
) -> Dict:
    """Check if delta_asymmetry = H<-A - A<-H increases T1 < T2 < T3.

    Returns: {
        'deltas': {tier: float},
        'is_monotonic': bool,
        'jt_result': Dict    # from jonckheere_terpstra_test
    }
    """
    ...

def check_model_consistency_m2(
    all_model_bidir_results: Dict,
    alpha: float = 0.05,
) -> Dict:
    """Gate: >= 2/3 models show gate_passed=True in asymmetry_test.

    Input: {model_slug: {'asymmetry_test': {'tiers_passing': int, 'gate_passed': bool, ...}}}
    Returns: {
        'models_passing': int,
        'passing_models': List[str],
        'gate_passed': bool   # models_passing >= 2
    }
    """
    ...

def verify_mechanism_activated_m2(
    all_model_bidir_results: Dict,
    experiment_log: str,
) -> Tuple[bool, Dict]:
    """4 indicators: both_directions_computed, shapes_match,
       asymmetry_nonzero, fr_m2_logs_found.
    Returns: (all_pass: bool, indicators: dict)
    """
    ...

def compute_ipw_csem_bidir(
    bidir_results_by_tier: Dict,
    tier_prompt_embeddings: Dict,
) -> Dict:
    """IPW-adjusted C_sem for both H<-A and A<-H using h-m1 compute_ipw_csem pattern.

    Calls compute_ipw_csem twice: once for raw_cos_H_given_A, once for raw_cos_A_given_H.
    Returns: {tier: {ipw_csem_H_given_A: float, ipw_csem_A_given_H: float}}
    """
    ...
```

### Pseudo-code (test_directional_asymmetry)

```
tiers_passing = 0
stats = {}
for tier, data in bidir_results_by_tier.items():
    H = data['csem_H_given_A_array']   # [N,]
    A = data['csem_A_given_H_array']   # [N,]
    mw = scipy.stats.mannwhitneyu(H, A, alternative='greater')
    d, d_ci = bootstrap_cohen_d(H, A, n_bootstrap=n_bootstrap, seed=seed)
    delta = float(np.mean(H) - np.mean(A))
    logger.info(f"[FR-M2] Tier {tier}: C_sem^H<-A={np.mean(H):.4f}, C_sem^A<-H={np.mean(A):.4f}, p={mw.pvalue:.4f}, d={d:.4f}")
    if mw.pvalue < alpha:
        tiers_passing += 1
    stats[tier] = {mw_statistic: mw.statistic, p_value: mw.pvalue,
                   cohen_d: d, cohen_d_ci: d_ci, delta_asymmetry: delta}

return {**stats, 'tiers_passing': tiers_passing, 'gate_passed': tiers_passing >= 2}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | test_directional_asymmetry | Mann-Whitney one-sided per tier + Cohen's d + gate count |
| L-5-2 | compute_asymmetry_monotonicity | delta_asymmetry per tier + J-T monotonicity check |
| L-5-3 | check_model_consistency_m2 | Cross-model gate (>= 2/3) using asymmetry_test results |
| L-5-4 | verify_mechanism_activated_m2 + compute_ipw_csem_bidir | 4-indicator check + IPW both directions |

---

## A-7: run_experiment.py orchestrator [Complexity: 16, Budget: 4 subtasks]

Applied: copy-extend pattern (h-m1 `run_tier_experiment` structure extended for bidirectional)

### API Signatures

```python
# run_experiment.py — h-m2 rewrite

HYPOTHESIS_ID = "h-m2"
TIER_ORDER = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]
MODEL_CONFIGS = [
    {"name": "all-MiniLM-L6-v2",        "slug": "minilm",     "role": "primary"},
    {"name": "paraphrase-MiniLM-L6-v2", "slug": "paraphrase", "role": "robustness1"},
    {"name": "all-mpnet-base-v2",        "slug": "mpnet",      "role": "robustness2"},
]

def run_single_model(
    model_cfg: Dict,                   # {name, slug, role}
    tier_pairs: Dict,                  # {tier: {h_next, a_actual, h_curr, a_next, h_prompt, ...}}
    tier_prompt_embeddings: Dict,      # {tier: np.ndarray [N, D]} for KS test
    config,                            # ExperimentConfig
) -> Dict:
    """Full pipeline for one SBERT model.

    Steps:
      1. Build Embedder(model_cfg['name'], config.embedding_cache_dir)
      2. compute_bidirectional_csem_per_tier()
      3. KS test on tier distributions; compute_ipw_csem_bidir if triggered
      4. test_directional_asymmetry()
      5. compute_asymmetry_monotonicity()

    Returns: {
        'tier_results': Dict,       # from compute_bidirectional_csem_per_tier
        'asymmetry_test': Dict,     # from test_directional_asymmetry
        'monotonicity': Dict,       # from compute_asymmetry_monotonicity
        'ipw_bidir': Dict,          # from compute_ipw_csem_bidir ({} if not triggered)
    }
    """
    ...

def run_bidirectional_experiment(config) -> Dict:
    """Main orchestrator: 3-model x 3-tier loop.

    Steps:
      1. split_by_tier(config.cache_dir) -> tier_pairs
      2. Encode prompt embeddings with primary model for KS test
      3. ks_test_tier_distributions()
      4. for model_cfg in MODEL_CONFIGS: run_single_model()
      5. check_model_consistency_m2()
      6. verify_mechanism_activated_m2()
      7. evaluate_gate_m2()
      8. generate_all_bidir_figures()
      9. save_results()
      10. Log: gate PASS/FAIL + models_passing count

    Returns: {
        'all_model_results': {slug: single_model_result},
        'consistency_m2': {models_passing, passing_models, gate_passed},
        'mechanism_m2': (bool, dict),
        'ks_results': dict,
        'gate': dict,
    }
    """
    ...

def evaluate_gate_m2(all_model_results: Dict) -> Dict:
    """Evaluate SHOULD_WORK gate for h-m2.

    Gate: >= 2/3 models show tiers_passing >= 2 (from asymmetry_test).
    Returns: {
        'gate_passed': bool,
        'models_passing': int,
        'passing_models': List[str],
        'details': {model_slug: {'tiers_passing': int, 'gate_passed': bool}},
    }
    """
    ...

def save_results(results: Dict, output_dir: str) -> str:
    """Save JSON + CSV summary. Returns path to JSON file.

    JSON: {output_dir}/experiment_results.json  (raw arrays excluded)
    CSV:  {output_dir}/asymmetry_summary.csv    (tier x model x {csem_H, csem_A, p, delta})
    """
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | run_single_model | One-model pipeline: bidir csem + KS/IPW + asymmetry test + monotonicity |
| L-7-2 | run_bidirectional_experiment | Top-level orchestrator: data load → 3-model loop → gate |
| L-7-3 | evaluate_gate_m2 | Aggregate tiers_passing/models_passing → PASS/FAIL verdict |
| L-7-4 | save_results + generate_all_bidir_figures | JSON + CSV + 7 figures (1 mandatory + 6 additional) |

---

## A-9: Unit Tests [Complexity: 12, Budget: 2 subtasks]

Applied: Standard pytest patterns

### API Signatures

```python
# tests/test_accommodation.py

def test_bidirectional_csem_shapes():
    """Synthetic N=100, D=32. Verify output keys and shapes [N,]."""
    ...

def test_bidirectional_csem_fr_m2_log(caplog):
    """Verify [FR-M2] prefix appears in captured log output."""
    ...

def test_bidirectional_csem_values_differ():
    """H<-A and A<-H values are not identical (non-trivial computation)."""
    ...

# tests/test_statistics.py

def test_directional_asymmetry_pass():
    """H_given_A ~ N(0.5, 0.1), A_given_H ~ N(0.1, 0.1), n=500 per tier → gate_passed=True."""
    rng = np.random.default_rng(42)
    h_arr = rng.normal(0.5, 0.1, 500)
    a_arr = rng.normal(0.1, 0.1, 500)
    result = test_directional_asymmetry(
        {'helpful-base': {'csem_H_given_A_array': h_arr, 'csem_A_given_H_array': a_arr}},
        alpha=0.05,
    )
    assert result['gate_passed'] == True
    assert result['helpful-base']['p_value'] < 0.05
    ...

def test_directional_asymmetry_fail():
    """Equal arrays → gate_passed=False, tiers_passing=0."""
    rng = np.random.default_rng(42)
    arr = rng.normal(0.3, 0.1, 500)
    result = test_directional_asymmetry(
        {'helpful-base': {'csem_H_given_A_array': arr, 'csem_A_given_H_array': arr.copy()}},
        alpha=0.05,
    )
    assert result['tiers_passing'] == 0
    ...

def test_verify_mechanism_activated_m2_all_true():
    """Construct valid results → all 4 indicators True."""
    ...

def test_check_model_consistency_m2_gate():
    """2/3 models pass → gate_passed=True; 1/3 → gate_passed=False."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | test_accommodation.py | test_bidirectional_csem_shapes, _fr_m2_log, _values_differ |
| L-9-2 | test_statistics.py | test_directional_asymmetry (pass/fail), verify_mechanism_m2, check_model_consistency_m2 |

---

## Constraints Summary

| Constraint | Value | Source |
|------------|-------|--------|
| KNN n_jobs | 1 (NOT -1) | h-m1 lesson, 155k scale |
| Mann-Whitney alternative | `'greater'` (one-sided) | PRD FR-4 |
| shuffle for A<-H | `build_topic_control(emb_prompt, emb_h_curr)` | New direction |
| Log prefix | `[FR-M2]` | PRD FR-3 |
| Gate tiers | >= 2/3 | PRD FR-4 |
| Gate models | >= 2/3 | PRD FR-7 |
| Full pairs | 155,362 (no subsampling) | PRD NFR |
| Import style | `from accommodation import ...` (no package prefix) | h-m1 code pattern |
| seed | 42 | PRD NFR |
| n_bootstrap | 1000 | PRD NFR |
