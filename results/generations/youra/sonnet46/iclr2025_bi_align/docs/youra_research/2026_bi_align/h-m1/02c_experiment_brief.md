# Experiment Design: h-m1

**Date:** 2026-03-14
**Author:** Anonymous
**Hypothesis Statement:** RLHF tier quality (helpful_base rank=1, helpful_rejection_sampling rank=2, helpful_online rank=3) produces monotonically increasing C_sem^H←A across tiers (Jonckheere-Terpstra p < 0.05, Cohen's d >= 0.1 for tier contrast), consistent across >= 2/3 SBERT models (all-MiniLM-L6-v2, paraphrase-MiniLM-L6-v2, all-mpnet-base-v2). Tests tier-monotonicity of semantic accommodation driven by RLHF quality gradient.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Hypothesis Template** - Tests tier-monotonic scaling of C_sem^H←A across RLHF quality gradient.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** h-e1 (MUST_WORK PASS: C_sem=0.3292, d=1.998, n=155,362 pairs)
**Gate Status:** MUST_WORK — If fail: Block H-M2/H-M3/H-M4; ROUTE_TO_0

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 ✅ VALIDATED

### Gate Condition
**MUST_WORK gate:** J-T p < 0.05 AND Cohen's d >= 0.1 for tier contrast in >= 2/3 SBERT models (all-MiniLM-L6-v2, paraphrase-MiniLM-L6-v2, all-mpnet-base-v2).

**Fail action:** Block H-M2, H-M3, H-M4; document tier monotonicity failure; write Serena failure memory; ROUTE_TO_0 or scope to existence-only claim.

---

## Continuation Context

### From h-e1 (Prerequisite)

**Proven fact:** Semantic accommodation exists at SBERT level (C_sem = 0.3292, n=155,362 pairs). Now testing whether this effect is **tier-monotonic** — does higher RLHF tier quality produce proportionally greater accommodation?

**Reusable components from h-e1:**
- DataLoader (`h-e1/code/data_loader.py`) — extend to return per-tier splits separately
- Embedder with disk cache (`h-e1/code/embedder.py`) — reuse for all 3 SBERT models
- Controls (random + KNN K=5) (`h-e1/code/controls.py`) — apply per-tier
- C_sem computation + OLS residualization (`h-e1/code/accommodation.py`) — compute per-tier
- Statistical testing suite (`h-e1/code/statistics.py`) — add J-T test + Bonferroni
- Visualization suite (`h-e1/code/visualize.py`) — add tier comparison plots

**Critical hyperparameters inherited from h-e1:**
- `batch_size=256`, `knn_k=5`, `knn_n_jobs=1` (CRITICAL: n_jobs=-1 crashes on 155k scale)
- `bootstrap_n=1000`, `bootstrap_seed=42`
- `OPENBLAS_NUM_THREADS=4` (env var must be set before run)
- `verification_mode='no_checks'` for HH-RLHF dataset loading
- Cache key format: `{model_slug}_{n_pairs}` to prevent stale cache

### Previous Hypothesis Results (if applicable)

| Metric | Value | Gate | Result |
|--------|-------|------|--------|
| C_sem (pooled) | 0.3292 | > 0 | PASS |
| C_sem 95% CI | [0.3280, 0.3304] | lower > 0 | PASS |
| cos_actual | 0.3534 | > cos_topic | PASS |
| cos_topic | 0.2688 | > cos_random | PASS |
| cos_random | 0.0241 | baseline | — |
| Cohen's d (actual vs topic) | 0.417 | >= 0.1 | PASS |
| Cohen's d (actual vs random) | 1.998 | >= 0.1 | PASS |
| n_pairs | 155,362 | >= 1,000 | PASS |
| All 5 mechanism indicators | True | All True | PASS |

**Key Insight from h-e1:** Interaction-specific semantic accommodation is a large-effect phenomenon (d=1.998 vs random). The signal exists at SBERT level, not surface features. This is the foundation for h-m1's tier-monotonicity test.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1:** "Jonckheere-Terpstra monotonicity test ordinal groups" — 4 results returned, all low similarity (0.29–0.31). Archon KB contains diffusers/diffusion model content, not statistical test implementations.

**Query 2:** "SBERT semantic similarity per-group stratified analysis" — 5 results, all low similarity (0.31–0.33). No relevant SBERT/NLP content in Archon KB.

**Query 3:** "RLHF tier quality gradient conversation analysis" — 5 results, max similarity 0.41 (HuggingFace Diffusers discussion forums, not RLHF-specific).

**Query 4 (code):** "Jonckheere Terpstra trend test Python" — No relevant code; Archon KB does not index scipy.stats or statistical test implementations.

**Query 5 (code):** "SentenceTransformer per-group cosine similarity stratified" — No relevant results; generic PyTorch/diffusion model content.

**Summary:** Archon KB contains no relevant prior cases for this hypothesis topic. Primary knowledge sources are: (1) h-e1 validated implementation (in-project), (2) Phase 2B protocol, (3) scipy.stats documentation (well-known library). No additional Archon insights available.

### Archon Code Examples

No relevant code examples found in Archon KB (see above). Implementation will be based on:
- h-e1 proven pipeline (directly reusable, 7 source files)
- `scipy.stats.jonckheere_terpstra` (standard library function)
- `scipy.stats.mannwhitneyu` + custom `cohen_d` bootstrap (already in h-e1/code/statistics.py)

### Exa GitHub Implementations

**Status:** Unavailable (402 Payment Required — same as h-e1 execution).

**Alternative sources used:**
- h-e1 proven implementation (validated, in-project, all tests pass)
- Phase 2B verification protocol (provides exact algorithmic steps)
- scipy documentation for `jonckheere_terpstra` (standard function, minimal code needed)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Since h-m1 is NOT a paper reproduction but an original analysis experiment on HH-RLHF, the implementation hierarchy is:
1. **Primary:** Extend h-e1 proven codebase (highest trust — already validated on this dataset)
2. **Secondary:** scipy.stats.jonckheere_terpstra for monotonicity test
3. **Fallback:** Custom J-T statistic implementation if scipy version is incompatible

**Recommended Implementation Path:**
- Primary: Extend `h-e1/code/` pipeline with per-tier stratification + J-T test
- Fallback: `scipy.stats.jonckheere_terpstra` (available in scipy >= 1.7.0)
- Justification: h-e1 pipeline already handles HH-RLHF data correctly with all known bugs fixed (KNN n_jobs, stale cache, verification_mode, OLS residuals)

### Code Analysis (Serena MCP)

*Skipped* — No complex external code to analyze. h-m1 extends the proven h-e1 pipeline (data_loader.py, embedder.py, accommodation.py, statistics.py) with per-tier stratification and Jonckheere-Terpstra monotonicity testing. All components from h-e1 are directly reusable. This is an analytical/statistical pipeline, not a novel neural architecture requiring semantic code analysis.

---

## Experiment Specification

### Dataset

**Name:** Anthropic/hh-rlhf
**Type:** standard (NOT synthetic)
**Version:** Latest (as downloaded for h-e1)
**Source:** HuggingFace Datasets

**Tier Structure (IV for h-m1):**
| Tier | Split Name | Rank | RLHF Quality |
|------|-----------|------|--------------|
| T1 | helpful-base | 1 (lowest) | Base RLHF |
| T2 | helpful-rejection-sampled | 2 (middle) | Rejection sampling |
| T3 | helpful-online | 3 (highest) | Online RLHF |

**Size:** ~273,617 conversation turns total; ~155,362 (H_next, A_actual) pairs from h-e1

**Per-tier split sizes (approximate):**
- helpful-base: ~91,165 exchanges (~43,000 pairs)
- helpful-rejection-sampled: ~92,405 exchanges (~45,000 pairs)
- helpful-online: ~89,893 exchanges (~44,000 pairs)
- All tiers: n >> 1,000 (statistical power satisfied)

**Preprocessing:**
- Parse conversation JSON: extract alternating Human/Assistant turns
- Build (H_{t+1}, A_t, H_prompt_t) triples per tier separately
- Length residualization: OLS(cos_sim ~ response_word_count) per tier for robustness reporting (NOT for primary metric)
- Lexical overlap residualization: OLS(cos_sim ~ BLEU_unigram) as secondary control
- KS test on prompt embedding distributions across tier pairs before analysis (R2 mitigation)
- If KS p < 0.05: apply inverse-probability weighting (IPW) and recompute per-tier C_sem

**Augmentation:** None (inference-only pipeline, no training)

**Cache:** Already downloaded at `.data_cache/datasets/hh-rlhf` (from h-e1). Reuse directly.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `Anthropic/hh-rlhf`
- Code:
```python
from datasets import load_dataset

# Load per tier with bug fix for split size mismatch
tier_names = ['helpful-base', 'helpful-rejection-sampled', 'helpful-online']
tier_datasets = {}
for tier in tier_names:
    tier_datasets[tier] = load_dataset(
        'Anthropic/hh-rlhf',
        data_dir=tier,
        verification_mode='no_checks',  # REQUIRED: avoids NonMatchingSplitsSizesError
        cache_dir='.data_cache/datasets/hh-rlhf'
    )
```

### Models

#### Baseline Model

**Architecture:** Matched-shuffle baseline (no semantic accommodation)
**Definition:** C_sem_baseline = E[cos(SBERT(H_{t+1}), SBERT(A_t^random-shuffle))]
**Purpose:** Per-tier null distribution for C_sem normalization

**Loading Information** (for Phase 4 download):
- Method: No download needed — computed from shuffled embeddings
- Identifier: N/A (shuffle is an algorithmic operation)
- Code: `A_shuffled = np.random.default_rng(42).permutation(A_embeddings_within_tier)`

#### Three SBERT Models (Primary + Robustness)

| Model | Role | HuggingFace ID | Embedding Dim |
|-------|------|---------------|---------------|
| all-MiniLM-L6-v2 | Primary | `sentence-transformers/all-MiniLM-L6-v2` | 384 |
| paraphrase-MiniLM-L6-v2 | Robustness 1 | `sentence-transformers/paraphrase-MiniLM-L6-v2` | 384 |
| all-mpnet-base-v2 | Robustness 2 | `sentence-transformers/all-mpnet-base-v2` | 768 |

**Loading Information** (for Phase 4 download):
- Method: sentence-transformers library
- Identifier: see table above
- Code:
```python
from sentence_transformers import SentenceTransformer

models = {
    'minilm': SentenceTransformer('all-MiniLM-L6-v2'),
    'paraphrase': SentenceTransformer('paraphrase-MiniLM-L6-v2'),
    'mpnet': SentenceTransformer('all-mpnet-base-v2')
}
```

**Success definition (MECHANISM):** Jonckheere-Terpstra test confirms monotonic increase C_sem(T1) < C_sem(T2) < C_sem(T3) with J-T p < 0.05 AND Cohen's d >= 0.1 for tier contrast in >= 2/3 models.

#### Proposed Model

**Architecture:** Tier-Stratified C_sem Analysis (extends h-e1 pipeline)
**Core mechanism:** Compute C_sem^H←A separately per tier → test monotonic increase with Jonckheere-Terpstra + pairwise Mann-Whitney + bootstrap Cohen's d

**Core Mechanism Implementation:**

```python
# Core Mechanism: Tier-Stratified C_sem with Jonckheere-Terpstra Monotonicity Test
# Based on: h-e1 validated pipeline + scipy.stats.jonckheere_terpstra
# Source: Phase 2B verification protocol (H-M1 section)

import numpy as np
from scipy import stats
from sentence_transformers import SentenceTransformer

def compute_per_tier_csem(tier_pairs: dict, model: SentenceTransformer,
                           knn_k: int = 5, seed: int = 42) -> dict:
    """
    Args:
        tier_pairs: {tier_name: [(H_next, A_actual, H_prompt), ...]}
        model: SentenceTransformer instance (normalized embeddings)
    Returns:
        {tier_name: {'c_sem': float, 'cos_actual': float, 'cos_random': float,
                     'n_pairs': int, 'embeddings': dict}}
    """
    results = {}
    for tier, pairs in tier_pairs.items():
        H_emb = model.encode([p[0] for p in pairs], batch_size=256, normalize_embeddings=True)
        A_emb = model.encode([p[1] for p in pairs], batch_size=256, normalize_embeddings=True)
        # Random shuffle baseline within-tier (not cross-tier)
        rng = np.random.default_rng(seed)
        A_shuffled = rng.permutation(A_emb)
        # C_sem: partner-specific minus random baseline
        cos_actual = np.sum(H_emb * A_emb, axis=1)       # elementwise dot = cosine (normalized)
        cos_random = np.sum(H_emb * A_shuffled, axis=1)
        c_sem = cos_actual.mean() - cos_random.mean()
        results[tier] = {'c_sem': c_sem, 'cos_actual': cos_actual.mean(),
                         'cos_random': cos_random.mean(), 'n_pairs': len(pairs),
                         'raw_cos_actual': cos_actual, 'raw_cos_random': cos_random}
    return results

def test_monotonicity(tier_results: dict, tier_order: list) -> dict:
    """
    Args:
        tier_results: output of compute_per_tier_csem
        tier_order: ['helpful-base', 'helpful-rejection-sampled', 'helpful-online']
    Returns: {'jt_stat': float, 'jt_p': float, 'pairwise_d': dict}
    """
    # Jonckheere-Terpstra monotonicity test (alternative='increasing')
    ordered_cos = [tier_results[t]['raw_cos_actual'] for t in tier_order]
    jt_result = stats.jonckheere_terpstra(*ordered_cos, alternative='increasing')
    # Pairwise Cohen's d with Bonferroni correction (3 pairs)
    pairwise = {}
    pairs = [('helpful-base', 'helpful-rejection-sampled'),
             ('helpful-rejection-sampled', 'helpful-online'),
             ('helpful-base', 'helpful-online')]
    for t1, t2 in pairs:
        d = bootstrap_cohens_d(tier_results[t1]['raw_cos_actual'],
                               tier_results[t2]['raw_cos_actual'], n=1000, seed=42)
        pairwise[f'{t1}_vs_{t2}'] = d
    return {'jt_stat': jt_result.statistic, 'jt_p': jt_result.pvalue, 'pairwise_d': pairwise}
```

### Training Protocol

**This is an inference-only analysis — no gradient-based training.**

**From h-e1 (Optimal Hyperparameters, reused for controlled comparison):**

| Parameter | Value | Source |
|-----------|-------|--------|
| embedding batch_size | 256 | h-e1 optimal |
| knn_k (topic control) | 5 | h-e1 optimal |
| knn_n_jobs | 1 | h-e1 CRITICAL (n_jobs=-1 crashes) |
| knn_algorithm | auto | h-e1 default |
| bootstrap_n | 1000 | h-e1 + Phase 2B protocol |
| bootstrap_seed | 42 | h-e1 protocol |
| ci_percentiles | [2.5, 97.5] | h-e1 standard |
| significance_level | 0.05 | Phase 2B protocol |
| OPENBLAS_NUM_THREADS | 4 | h-e1 env fix |

**Rationale:** Identical hyperparameters to h-e1 ensure fair comparison — only IV (tier stratification) changes between experiments.

**Execution sequence:**
1. Load all three HH-RLHF tier splits (reuse h-e1 cache)
2. Run KS test on prompt embedding distributions across tiers → apply IPW if needed
3. For each of 3 SBERT models:
   a. Encode per-tier pairs (embedder cache: `{model_slug}_{tier}_{n_pairs}`)
   b. Compute C_sem per tier (matched-shuffle within-tier)
   c. Run Jonckheere-Terpstra monotonicity test
   d. Run pairwise Mann-Whitney U + Bonferroni correction
   e. Bootstrap Cohen's d (n=1000, seed=42) for all tier pairs
4. Aggregate: check consistency across >= 2/3 models
5. Generate visualizations

**Seeds:** Fixed seed=42 for all bootstrap and shuffle operations.

### Evaluation

**Primary Metrics (Gate criteria):**
| Metric | Target | Evaluation Method |
|--------|--------|-------------------|
| J-T statistic p-value | < 0.05 | `scipy.stats.jonckheere_terpstra(..., alternative='increasing')` |
| Cohen's d (tier contrast) | >= 0.1 | Bootstrap (n=1000, seed=42) on per-tier C_sem values |
| Model consistency | >= 2/3 SBERT models pass | Count models satisfying J-T p < 0.05 AND d >= 0.1 |

**Secondary Metrics:**
| Metric | Target | Evaluation Method |
|--------|--------|-------------------|
| C_sem direction | T1 < T2 < T3 | Sign check on per-tier means |
| Pairwise Mann-Whitney | p < 0.05 (Bonferroni: p < 0.0167) | `scipy.stats.mannwhitneyu` |
| All-model direction | Monotonic in all 3 models | Even if only >= 2/3 significant |

**Statistical Test Battery:**
1. Jonckheere-Terpstra (primary monotonicity test, ordered alternative)
2. Bonferroni-corrected pairwise Mann-Whitney U (3 pairs: T1v2, T2v3, T1v3)
3. Bootstrap Cohen's d (n=1000, seed=42) for all tier pairs
4. KS test on prompt embedding distributions (R2 mitigation)
5. IPW-weighted reanalysis if KS p < 0.05

**Expected Values (based on h-e1 as foundation):**
- C_sem (pooled, from h-e1): 0.3292 — per-tier values expected to range above/below this
- Effect size: d >= 0.1 is the minimum; moderate (d~0.3-0.5) is plausible if tier effect exists
- Null expectation: C_sem relatively uniform across tiers (~0.32-0.33 for all)

**Success Criteria:**
- **Primary (GATE):** J-T p < 0.05 AND d >= 0.1 for tier contrast in >= 2/3 SBERT models
- **Secondary:** C_sem(T3) > C_sem(T2) > C_sem(T1) across all models (direction consistency)

**Gate PASS:** Proceed to H-M2, H-M3 (parallel)
**Gate FAIL:** Block H-M2/H-M3/H-M4; write Serena failure memory; ROUTE_TO_0

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical analysis (ordinal group comparison)
- Library: `scipy.stats` (jonckheere_terpstra, mannwhitneyu, ks_2samp), `numpy` (bootstrap Cohen's d)
- Code:
```python
from scipy import stats

# Jonckheere-Terpstra monotonicity test
jt = stats.jonckheere_terpstra(csem_t1, csem_t2, csem_t3, alternative='increasing')
# Pairwise Mann-Whitney with Bonferroni
mw_12 = stats.mannwhitneyu(csem_t1, csem_t2, alternative='two-sided')
# KS test for distribution comparability
ks_12 = stats.ks_2samp(prompt_emb_t1, prompt_emb_t2)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart of C_sem per tier (T1, T2, T3) for each SBERT model, with error bars (bootstrap 95% CI). Annotate J-T p-value and gate pass/fail status.

#### Additional Figures (LLM Autonomous)
Appropriate visualizations for h-m1 mechanism test:
1. **Tier-Monotonicity Plot:** Line plot of C_sem(T1), C_sem(T2), C_sem(T3) across 3 SBERT models (3 lines, shared x-axis of tier rank). Shows consistency across models.
2. **Pairwise Cohen's d Matrix:** Heatmap of d values for all tier pairs × all models. Color-coded by d >= 0.1 threshold.
3. **Cosine Distribution Per Tier:** Violin plot of raw cos_actual distributions per tier for primary model (all-MiniLM-L6-v2). Shows within-tier spread vs across-tier shift.
4. **Bootstrap C_sem Distribution:** For each tier and primary model, kernel density of bootstrap C_sem replicates. Shows CI overlap vs separation.
5. **IPW Sensitivity Check (conditional):** If KS test triggers IPW, compare raw vs IPW-weighted C_sem per tier. Only generated if R2 triggered.
6. **KS Test Results Summary:** Table/bar chart of KS statistics and p-values for all 3 tier-pair comparisons.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | SBERT tier-stratified C_sem computation is supported — H-E1 proved the pooled version works, and per-tier version is a straightforward extension | TRUE — verified by h-e1 architecture |
| Mechanism Isolatable | Each tier's C_sem computed independently; tier effects can be compared | TRUE — tier-split is a data partitioning operation |
| Baseline Measurable | Per-tier matched-shuffle baseline is well-defined (shuffle within tier, not cross-tier) | TRUE — within-tier shuffle preserves tier distribution |

### Architecture Compatibility Check

**Experiment type:** Statistical analysis pipeline on pre-trained SBERT embeddings
**No neural architecture changes required** — this is a data analysis experiment

| Requirement | Status |
|-------------|--------|
| SentenceTransformer inference | ✅ Available (h-e1 confirmed) |
| HH-RLHF tier splits | ✅ 3 splits downloaded and cached |
| scipy.stats.jonckheere_terpstra | ✅ Available in scipy >= 1.7.0 (standard) |
| Bootstrap infrastructure | ✅ Already in h-e1/code/statistics.py |

**Incompatible configurations:** None — pure Python/numpy statistical analysis.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Tier [T1/T2/T3] C_sem computed: {value}" for each tier | `run_experiment.py:logging` |
| Data Shape | Per-tier pair counts sum to ~155,362 (h-e1 total) | `data_loader.py:split_by_tier()` |
| Metric Delta | C_sem values differ across tiers (any delta > 0 is signal) | `accommodation.py:compute_tier_csem()` |
| J-T p-value | < 0.05 indicates monotonic trend detected | `statistics.py:jonckheere_terpstra_test()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results: dict, experiment_log: str) -> tuple:
    """
    Verify tier-monotonicity mechanism actually ran and produced measurable output.
    Returns: (all_activated: bool, indicators: dict)
    """
    indicators = {
        # Log checks
        "tier_logs_found": all(
            f"Tier {t} C_sem computed" in experiment_log
            for t in ['helpful-base', 'helpful-rejection-sampled', 'helpful-online']
        ),
        # Data checks
        "all_tiers_have_pairs": all(
            results.get(f'n_pairs_{t}', 0) >= 1000
            for t in ['base', 'rs', 'online']
        ),
        # Metric checks
        "csem_differs_across_tiers": (
            len(set(round(results.get(f'c_sem_{t}', -99), 4)
                    for t in ['base', 'rs', 'online'])) > 1
        ),
        # Gate metric
        "jt_computed": 'jt_pvalue' in results and results['jt_pvalue'] is not None,
        # Multi-model check
        "all_models_ran": all(
            f'c_sem_{m}_base' in results
            for m in ['minilm', 'paraphrase', 'mpnet']
        )
    }
    return all(indicators.values()), indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Tier split failed | n_pairs for any tier < 1000 | FAIL: Data loading error |
| C_sem identical across tiers | All tier C_sem within 0.001 | FAIL: Per-tier stratification not working |
| J-T not computed | jt_pvalue is None | FAIL: Statistical test implementation error |
| Only 1 model ran | Not all 3 model results present | FAIL: Multi-model execution incomplete |
| Bootstrap failed | bootstrap CI is [nan, nan] | FAIL: Insufficient data for bootstrap |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | All 5 indicators True | `verify_mechanism_activated()` |
| Monotonic trend measured | J-T p-value computed (regardless of value) | `results['jt_pvalue'] is not None` |
| Hypothesis Supported (GATE) | J-T p < 0.05 AND d >= 0.1 in >= 2/3 SBERT models | Gate evaluation in `run_experiment.py` |

---

## 🔬 PoC Success Check

**MECHANISM Gate Pass Condition:**
1. Code runs without error
2. J-T p < 0.05 (monotonic trend in ordered alternative)
3. Cohen's d >= 0.1 for tier contrast (minimum effect size)
4. Both criteria satisfied in >= 2/3 SBERT models

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Status:** No relevant content found.

Archon KB (source IDs: 8b1c7f40739544a6, 370d45dd0c64d97e) is indexed with diffusion model content (Stable Diffusion, diffusers library) and LaTeX documentation. 5 queries executed:
1. "Jonckheere-Terpstra monotonicity test ordinal groups" → 4 results, max similarity 0.31
2. "SBERT semantic similarity per-group stratified analysis" → 5 results, max similarity 0.33
3. "RLHF tier quality gradient conversation analysis" → 5 results, max similarity 0.41
4. "Jonckheere Terpstra trend test Python" (code) → 5 results, all diffusers/PyTorch
5. "SentenceTransformer per-group cosine similarity stratified" (code) → 5 results, all unrelated

**Used for:** Negative result (no relevant past cases). Design grounded in h-e1 instead.

### B. GitHub Implementations (Exa)

**Status:** Unavailable (402 Payment Required — consistent with h-e1 execution on 2026-03-14).

Queries attempted:
1. "Jonckheere-Terpstra test Python scipy stats monotonic trend ordinal groups implementation"
2. "SBERT SentenceTransformer per-tier stratified cosine similarity accommodation analysis Python"
3. "Anthropic hh-rlhf dataset tier analysis semantic similarity Python HuggingFace"

All returned 402. No GitHub sources available.

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was not available (Exa 402 error). h-m1 extends the proven h-e1 pipeline; no novel architecture requires semantic code analysis. Design is grounded in:
- h-e1 validated codebase (7 source files, all tests pass)
- `scipy.stats.jonckheere_terpstra` (standard library, minimal integration)
- Phase 2B verification protocol (provides exact algorithmic steps)

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — h-e1 (`h-e1/04_validation.md`)
**Gate Result:** PASS (MUST_WORK)

**Reused Components:**
- Dataset: Anthropic/hh-rlhf — already cached at `.data_cache/datasets/hh-rlhf`
- Model: all-MiniLM-L6-v2 embeddings — disk cache available (`h-e1/code/embedder.py`)
- Code architecture: All 7 source files reused with tier stratification extension
- Hyperparameters: batch_size=256, knn_k=5, knn_n_jobs=1, bootstrap_n=1000, seed=42

**Why Reused:** Enables controlled comparison — only IV (tier stratification) changes between h-e1 and h-m1. Same dataset, same models, same statistical framework.

**Critical Lessons Applied from h-e1:**
- `n_jobs=1` in KNN (CRITICAL: n_jobs=-1 crashes on 155k scale due to OpenBLAS double-free)
- Cache key `{model_slug}_{tier}_{n_pairs}` (extended from h-e1 pattern to include tier)
- `verification_mode='no_checks'` for HH-RLHF loading
- Statistical tests on **raw cosine similarities**, NOT OLS residuals (residuals have zero mean by construction)
- Dry run with n=1500 pairs recommended before full experiment

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (hh-rlhf) | Phase 2A → Phase 2B | 02b_verification_plan.md Section 1.3 |
| Three-tier IV structure | Phase 2B | H-M1 specification |
| SBERT model selection (3 models) | Phase 2A → Phase 2B | 02b_verification_plan.md Section 1.3 |
| Jonckheere-Terpstra test | Phase 2B protocol | H-M1 verification protocol step 2 |
| Bonferroni correction | Phase 2B protocol | H-M1 verification protocol step 3 |
| bootstrap_n=1000, seed=42 | h-e1 validation | 04_validation.md optimal hyperparameters |
| knn_k=5, knn_n_jobs=1 | h-e1 validation | 04_validation.md lessons learned |
| verification_mode='no_checks' | h-e1 validation | 04_validation.md bug fixes |
| batch_size=256 | h-e1 validation | 04_validation.md optimal hyperparameters |
| Within-tier shuffle baseline | Phase 2B + h-e1 | Extends h-e1 matched-shuffle to per-tier |
| KS test + IPW | Phase 2B risk mitigation | R2 mitigation strategy (A2 assumption) |
| Success criteria (J-T p<0.05, d>=0.1) | Phase 2B | H-M1 gate condition |
| Model consistency (>=2/3) | Phase 2B | H-M1 success criteria |
| Pseudo-code structure | h-e1 codebase + Phase 2B | Extends h-e1 accommodation.py pattern |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-14T23:33:00

### Workflow History for This Hypothesis

| Event | Phase | Timestamp |
|-------|-------|-----------|
| h-e1 VALIDATED (prerequisite) | Phase 4 | 2026-03-14T23:06:00 |
| h-m1 set to IN_PROGRESS | Hypothesis Loop | 2026-03-14T23:32:46 |
| Phase 2C started for h-m1 | Phase 2C | 2026-03-14T23:33:00 |
| Experiment design completed | Phase 2C | 2026-03-14T23:50:00 |

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (5 queries, 0 relevant), Exa (3 queries, 402 unavailable), Serena (skipped — analytical pipeline)*
*All specifications grounded in: h-e1 validated pipeline + Phase 2B protocol + scipy.stats documentation*
*Next Phase: Phase 3 - Implementation Planning*
