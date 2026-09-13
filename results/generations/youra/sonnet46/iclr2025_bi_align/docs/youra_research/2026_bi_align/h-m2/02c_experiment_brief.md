# Experiment Design: h-m2

**Date:** 2026-03-15
**Author:** Anonymous
**Hypothesis Statement:** C_sem^H←A (human accommodates to AI) systematically exceeds C_sem^A←H (AI accommodates to human) at >= 2/3 RLHF tiers (Mann-Whitney p < 0.05), consistent with power asymmetry framework. Tests directional asymmetry: H->AI > AI->H semantic accommodation as predicted by epistemic authority hypothesis [Danescu-Niculescu-Mizil et al. 2011].
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** — Tests directional asymmetry in bilateral semantic accommodation.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** h-m1 = VALIDATED (MUST_WORK gate PASSED)
**Gate Status:** SHOULD_WORK — if fails, refines thesis to symmetric mutual coherence interpretation; does not block H-M4

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (VALIDATED)

### Gate Condition

**Gate Type:** SHOULD_WORK

**Pass Condition:** C_sem^H←A > C_sem^A←H with p < 0.05 (Mann-Whitney, one-sided) at >= 2/3 RLHF tiers

**If Fail:** Refines thesis to symmetric mutual coherence interpretation; does not block H-M4; document as scope limitation; reinterpret as evidence against epistemic authority hypothesis

---

## Continuation Context

### From h-m1 (VALIDATED)

**Reusing established infrastructure:**
- All HH-RLHF tier embeddings cached: 18 .npy files (3 models × 3 tiers × 2 splits [H, A])
- Cache path: `.data_cache/datasets/hh-rlhf`
- `compute_tier_csem_matrix()` (accommodation.py) — proven, extends directly
- `bonferroni_mannwhitney()` (statistics.py) — reusable for bidirectional test
- `ks_test_tier_distributions()` + `compute_ipw_csem()` (statistics.py) — covariate shift already confirmed, rerunning for A←H direction
- All visualization infrastructure (visualize.py) reusable

**Net new computation:** bidirectional extension only (~2× runtime of h-m1 due to added A←H direction, but embeddings cached so KNN recomputation minimal)

### Previous Hypothesis Results (h-m1)

| Model | T1: Base | T2: RS | T3: Online | Monotonic? |
|-------|----------|--------|------------|------------|
| all-MiniLM-L6-v2 | 0.3036 | 0.3367 | 0.3678 | ✓ |
| paraphrase-MiniLM-L6-v2 | 0.2714 | 0.3068 | 0.3456 | ✓ |
| all-mpnet-base-v2 | 0.3138 | 0.3483 | 0.3820 | ✓ |

J-T p=0.001 (all 3 models), Cohen's d T1 vs T3: 0.18–0.25 (all ≥ 0.1)

**IPW correction applied** (KS triggered at all tier pairs). Monotonicity holds after IPW.

**Key insight for h-m2:** Since RLHF training optimizes AI responses for helpfulness and epistemic quality, human accommodation C_sem^H←A is high and tier-monotonic. The asymmetry test checks whether the reverse direction (AI accommodating to human phrasing) is systematically lower, which would confirm power asymmetry dynamics.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Queries Executed:** 5
- Query 1: "directional accommodation asymmetry linguistic coordination" → 5 results (similarity ~0.28–0.31)
- Query 2: "bidirectional semantic similarity accommodation human AI dialogue" → 5 results (similarity ~0.39–0.44)
- Query 3: "Mann-Whitney paired comparison cosine similarity implementation" → 3 results (similarity ~0.35–0.38)
- Code Query 1: "bidirectional cosine similarity paired comparison Mann-Whitney" → 5 results (cuBLAS docs, similarity ~0.28–0.30)
- Code Query 2: "sentence transformer semantic similarity direction accommodation" → 5 results (BibTeX/diffusion, similarity ~0.29–0.32)

**Assessment:** Archon KB contains primarily diffusion model/CUDA documentation (source_id: 8b1c7f40739544a6). No domain-relevant results for linguistic accommodation, bidirectional dialogue analysis, or RLHF behavioral studies. Consistent with h-e1 and h-m1 findings (0 relevant results). All 5 queries executed per protocol.

**Relevant Archon Findings:** None directly applicable. Implementation grounded in:
- h-m1 validated codebase (proven modules)
- 02b_verification_plan.md protocol specifications
- Danescu-Niculescu-Mizil et al. [2011] (accommodation direction asymmetry)
- Chang & Wang [2025] (word-level bidirectional LLM-human adaptation)

### Archon Code Examples

**Assessment:** No relevant code examples found. Archon KB code examples are cuBLAS matrix operation templates (not applicable to Python/scipy/sentence-transformers statistical pipeline).

**Pattern from h-m1 codebase (ground truth):**
```python
# From h-m1/code/accommodation.py (proven pattern)
def compute_tier_csem_matrix(tier_embeddings_H, tier_embeddings_A,
                              shuffle_indices, direction='H←A'):
    actual_cos = cosine_similarity(tier_embeddings_H[t+1], tier_embeddings_A[t])
    shuffle_cos = cosine_similarity(tier_embeddings_H[t+1],
                                    tier_embeddings_A[shuffle_indices[t]])
    return actual_cos - shuffle_cos
```

### Exa GitHub Implementations

**Status:** Unavailable (402 error) — consistent with h-e1 and h-m1. Both queries attempted:
- Query 1: "Danescu-Niculescu-Mizil bidirectional accommodation coordination linguistic GitHub implementation"
- Query 2: "bidirectional semantic similarity human AI accommodation RLHF Mann-Whitney directional asymmetry GitHub"

**Limitation noted:** No external GitHub implementations found. Implementation grounded in h-m1 validated codebase.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This experiment extends the h-m1 analytical pipeline — not a reproduction of an external paper method. The primary reference is the within-codebase h-m1 infrastructure (validated, passing all 21 pytest tests).

**Recommended Implementation Path:**
- Primary: h-m1 codebase extension (h-m1/code/ as base) — highest priority, proven
- Fallback: From-scratch Python implementation following 02b_verification_plan.md protocol
- Justification: h-m1 modules fully validated; bidirectional extension is additive and non-breaking

### Code Analysis (Serena MCP)

*Skipped* — Analytical pipeline extension of h-m1 SBERT infrastructure. No complex code requiring Serena analysis (no custom neural network, no unfamiliar architecture patterns). Core pattern is adding `direction='A←H'` parameter to `compute_tier_csem_matrix()`. Exa unavailable (402), no external complex code found.

---

## Experiment Specification

### Dataset

**Primary Dataset:** Anthropic/hh-rlhf (Helpfulness Splits — 3 tiers)

| Field | Value |
|-------|-------|
| **Name** | Anthropic/hh-rlhf |
| **Type** | standard (real, established) |
| **Splits** | helpful-base (43,835 pairs), helpful-rejection-sampled (52,421 pairs), helpful-online (22,007 pairs) |
| **Total** | 155,362 conversation turn-pairs (H, A adjacent turns) |
| **Source** | HuggingFace Hub (Bai et al. 2022) |
| **Cache** | `.data_cache/datasets/hh-rlhf` (already cached from h-m1) |

**Synthetic Data Policy:** PASSES — type=standard (real HuggingFace dataset)

**Continuation Note:** Full dataset cached and verified from h-e1 and h-m1. No re-download needed.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets` library
- Identifier: `Anthropic/hh-rlhf`
- Code:
```python
from datasets import load_dataset
for split in ['helpful-base', 'helpful-rejection-sampled', 'helpful-online']:
    ds = load_dataset('Anthropic/hh-rlhf', data_dir=split, cache_dir='.data_cache/datasets/hh-rlhf')
```

### Models

#### Baseline Model

**Architecture:** SBERT sentence-transformers (inference-only; no training)

| Model | Role | HuggingFace ID |
|-------|------|----------------|
| `all-MiniLM-L6-v2` | Primary | `sentence-transformers/all-MiniLM-L6-v2` |
| `paraphrase-MiniLM-L6-v2` | Robustness check | `sentence-transformers/paraphrase-MiniLM-L6-v2` |
| `all-mpnet-base-v2` | Robustness check | `sentence-transformers/all-mpnet-base-v2` |

**Configuration (inherited from h-m1):**
- Batch size: 256 (CPU-optimal for 14K sentences/sec)
- Embedding cache: 18 .npy files fully reusable from h-m1 (tier-namespaced)
- No fine-tuning required

**Loading Information** (for Phase 4 download):
- Method: sentence-transformers library
- Identifier: `all-MiniLM-L6-v2` (primary)
- Code:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
embeddings = model.encode(texts, batch_size=256, show_progress_bar=True)
```

#### Proposed Model

**Architecture:** Baseline + bidirectional C_sem computation (A←H direction)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Bidirectional C_sem Computation for Directional Asymmetry Test
# Based on: h-m1/code/accommodation.py (proven), 02b_verification_plan.md protocol
# Extension: adds A←H direction to existing H←A infrastructure

def compute_bidirectional_csem_per_tier(tier_data, model_name,
                                          cache_dir, knn_k=5, seed=42):
    """
    Args:
        tier_data: dict with keys 'human_turns' (H_t, H_{t+1}) and 'ai_turns' (A_t)
        model_name: SBERT model slug (e.g., 'all-MiniLM-L6-v2')
        Returns: dict with 'csem_H_given_A' and 'csem_A_given_H' per-pair arrays
    """
    # Load cached embeddings from h-m1 (tier-namespaced .npy files)
    emb_H_next = load_cached(f"{cache_dir}/{model_name}_H_next_{tier}.npy")  # H_{t+1}
    emb_A_curr = load_cached(f"{cache_dir}/{model_name}_A_curr_{tier}.npy")  # A_t
    emb_H_curr = load_cached(f"{cache_dir}/{model_name}_H_curr_{tier}.npy")  # H_t
    emb_A_next = load_cached(f"{cache_dir}/{model_name}_A_next_{tier}.npy")  # A_{t+1}

    # KNN topic-control shuffle indices (reuse from h-m1, k=5, n_jobs=1)
    shuffle_H = build_knn_shuffle(emb_H_next, emb_H_curr, k=knn_k, seed=seed)
    shuffle_A = build_knn_shuffle(emb_A_next, emb_A_curr, k=knn_k, seed=seed)

    # Direction 1: H←A (human accommodates to AI) — proven in h-m1
    csem_H_given_A = (cosine_sim(emb_H_next, emb_A_curr) -
                      cosine_sim(emb_H_next, emb_A_curr[shuffle_H]))

    # Direction 2: A←H (AI accommodates to human) — new for h-m2
    csem_A_given_H = (cosine_sim(emb_A_next, emb_H_curr) -
                      cosine_sim(emb_A_next, emb_H_curr[shuffle_A]))

    return {'csem_H_given_A': csem_H_given_A, 'csem_A_given_H': csem_A_given_H}


# Per-tier statistical test: H←A vs A←H directional comparison
def test_directional_asymmetry(results_by_tier, alpha=0.05):
    tiers_passing = 0
    for tier, results in results_by_tier.items():
        stat, p = mannwhitney_u(results['csem_H_given_A'],
                                 results['csem_A_given_H'],
                                 alternative='greater')  # one-sided: H←A > A←H
        d = cohen_d(results['csem_H_given_A'], results['csem_A_given_H'])
        log(f"[FR-M2] {tier}: C_sem^H←A={mean(results['csem_H_given_A']):.4f}, "
            f"C_sem^A←H={mean(results['csem_A_given_H']):.4f}, p={p:.4f}, d={d:.4f}")
        if p < alpha:
            tiers_passing += 1
    gate_pass = tiers_passing >= 2  # >= 2/3 tiers required
    return gate_pass, tiers_passing
```

### Training Protocol

**Note:** H-M2 is a statistical analysis experiment — no neural network training. "Protocol" refers to statistical computation configuration.

**From h-m1 validated configuration (inherited for controlled comparison):**

| Parameter | Value | Source |
|-----------|-------|--------|
| **Significance level** | α = 0.05 (one-sided Mann-Whitney) | 02b_verification_plan.md |
| **Bootstrap resamples** | 1,000 (seed=42) | h-m1 validation report |
| **Cohen's d threshold** | 0.1 (minimum meaningful effect) | h-m1 validated |
| **KNN k** | 5 (topic-matched control) | h-m1 validated |
| **KNN n_jobs** | 1 (CRITICAL: n_jobs=-1 crashes at 155k scale) | h-m1 lesson learned |
| **Bootstrap seed** | 42 | h-m1 validated |
| **Consistency threshold** | >= 2/3 models | h-m1 validated |
| **Tiers required** | >= 2/3 RLHF tiers (Gate) | 02b_verification_plan.md |
| **Seeds** | 1 (single run, fixed) | Pipeline standard |

**Statistical Test:** Mann-Whitney U (one-sided, alternative='greater') — tests C_sem^H←A > C_sem^A←H

**IPW correction:** Re-run KS test on A←H tier distributions; apply IPW if KS p < 0.05 (expected: yes, same tiers as h-m1)

**Asymmetry pattern analysis (secondary):** Check if asymmetry magnitude (C_sem^H←A - C_sem^A←H) increases monotonically with tier quality (T3 > T2 > T1)

**Rationale:** Reusing h-m1 configuration for controlled comparison — only the measured direction changes (IV), not statistical methodology.

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Threshold |
|--------|-----------|-------------------|
| `C_sem^H←A` per tier | E[cos(H_{t+1}, A_t)] - shuffle baseline | Already established (h-m1) |
| `C_sem^A←H` per tier | E[cos(A_{t+1}, H_t)] - shuffle baseline | Measured fresh for h-m2 |
| `Δ_asymmetry` per tier | C_sem^H←A - C_sem^A←H | > 0 with p < 0.05 |
| `p_MW` per tier | Mann-Whitney p (one-sided, H←A > A←H) | < 0.05 |
| `d_MW` per tier | Cohen's d (H←A vs A←H) | Reported (not threshold) |
| `tiers_passing` | Count of tiers with p < 0.05 | >= 2 (gate: 2/3) |

**Success Criteria (Gate: SHOULD_WORK):**
- **Primary:** C_sem^H←A > C_sem^A←H with p < 0.05 (Mann-Whitney, one-sided) at >= 2/3 RLHF tiers
- **Secondary:** Asymmetry magnitude increases with tier quality (Δ_asymmetry^online > Δ_asymmetry^RS > Δ_asymmetry^base) — tests epistemic authority hypothesis prediction
- **Model consistency:** Same directional pattern in >= 2/3 SBERT models

**Expected Results (from CAT theory and h-m1 validated mechanism):**
- C_sem^H←A: ~0.30–0.37 per tier (proven in h-m1)
- C_sem^A←H: Expected < C_sem^H←A (AI turn embeddings serve as "response" to human, but RLHF training focuses on helpfulness not accommodation)
- Expected Δ_asymmetry: 0.05–0.15 (moderate positive asymmetry based on power asymmetry theory)
- Expected gate result: SHOULD_WORK pass (moderate confidence; symmetric coherence alternative is plausible)

**Statistical Test:** Mann-Whitney U (one-sided, `alternative='greater'`): tests whether paired C_sem^H←A values are stochastically greater than C_sem^A←H values within each tier.

**Ablation Study:**

| Variant | What It Tests | Expected Result |
|---------|--------------|-----------------|
| H←A direction only (baseline, h-m1) | Existence of accommodation | PASS (proven) |
| A←H direction only (new) | AI accommodation to human | Expected lower C_sem |
| H←A vs A←H within tier (core) | Directional asymmetry | Gate metric |
| Asymmetry × tier interaction | Epistemic authority monotonicity | Secondary analysis |
| IPW-adjusted asymmetry | Robustness to covariate shift | Reported alongside raw |
| Per-model consistency (3 SBERT) | Geometry artifact ruling-out | >= 2/3 models must agree |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical analysis (cosine similarity comparison)
- Library: `scipy.stats.mannwhitneyu`, `numpy`, `sklearn.metrics.pairwise.cosine_similarity`
- Code:
```python
from scipy.stats import mannwhitneyu
import numpy as np
stat, p = mannwhitneyu(csem_H_given_A, csem_A_given_H, alternative='greater')
d = (np.mean(csem_H_given_A) - np.mean(csem_A_given_H)) / pooled_std(...)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Grouped bar chart — C_sem^H←A vs C_sem^A←H per tier (3 groups × 2 bars each), with CI whiskers

#### Additional Figures (LLM Autonomous)

Based on the bidirectional asymmetry mechanism, the following visualizations are recommended:

| Figure | Type | Description |
|--------|------|-------------|
| Directional asymmetry bars | Grouped bar + CI | C_sem^H←A vs C_sem^A←H × 3 tiers × 3 models |
| Asymmetry delta line | Line plot | Δ_asymmetry = H←A - A←H across tiers (tests monotonicity) |
| Pairwise distribution violin | Violin/KDE | Distribution of per-pair csem H←A vs A←H |
| Statistical significance heatmap | Heatmap | p-values for H←A > A←H across tier × model grid |
| Bootstrap CI comparison | CI plot | Bootstrap CI for both directions per tier |
| IPW-adjusted asymmetry | Bar + error | Raw vs IPW-corrected Δ_asymmetry |

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Bidirectional C_sem computation: compute_tier_csem_matrix() already proven for H←A direction; A←H direction is symmetric extension | TRUE — h-m1 accommodation.py validated |
| Mechanism Isolatable | H←A and A←H directions computable independently; comparison is delta between them | TRUE — direction parameter toggleable |
| Baseline Measurable | C_sem^H←A (h-m1 results) serve as baseline direction; C_sem^A←H is the "proposed" second direction | TRUE — h-m1 cached results reusable |

### Architecture Compatibility Check

**Architecture:** SBERT sentence-transformers (inference-only, no training).

**Compatibility:** ✅ FULLY COMPATIBLE — bidirectional C_sem computation is symmetric by design. The same `cosine_similarity()` and KNN shuffle procedure applies identically to both directions. No architectural constraints.

**Required Features:**
- `embeddings_A_next`: AI turn embeddings at position t+1 (required for A←H direction; may need additional caching if not in h-m1 cache)
- `embeddings_H_curr`: Human turn embeddings at position t (available from h-m1 cache)
- Shuffle indices for H→A direction (build fresh using same KNN k=5 procedure)

**Important Check for Phase 4:** Verify h-m1 embedding cache includes A_{t+1} embeddings (not just A_t). If A_{t+1} not cached, requires additional encoding pass (~1.5–2h per model at full scale).

**Incompatible Architectures:** None (pure Python/scipy/numpy/sklearn pipeline).

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `[FR-M2] Tier {tier}: C_sem^H←A={val:.4f}, C_sem^A←H={val:.4f}, p={val:.4f}` | run_experiment.py:main() |
| Tensor Shape | `csem_A_given_H.shape == csem_H_given_A.shape == (n_pairs_tier,)` | accommodation.py:compute_bidirectional_csem() |
| Metric Delta | `mean(csem_H_given_A) - mean(csem_A_given_H) != 0` (non-zero asymmetry) | statistics.py:test_directional_asymmetry() |

**Activation Verification Code (Phase 4 must implement):**
```python
def verify_mechanism_activated(results_by_tier, logs):
    indicators = {
        "both_directions_computed": all(
            'csem_H_given_A' in r and 'csem_A_given_H' in r
            for r in results_by_tier.values()
        ),
        "shapes_match": all(
            r['csem_H_given_A'].shape == r['csem_A_given_H'].shape
            for r in results_by_tier.values()
        ),
        "asymmetry_nonzero": any(
            abs(np.mean(r['csem_H_given_A']) - np.mean(r['csem_A_given_H'])) > 1e-6
            for r in results_by_tier.values()
        ),
        "fr_m2_logs_found": all(f"[FR-M2]" in logs for _ in results_by_tier)
    }
    return all(indicators.values()), indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| A←H direction not computed | `csem_A_given_H` missing from results | FAIL: Direction not implemented |
| Shapes mismatch | `csem_H_given_A.shape != csem_A_given_H.shape` | FAIL: Alignment error in pair construction |
| Zero asymmetry | All Δ_asymmetry ≈ 0 across tiers | INVESTIGATE: May indicate direction-agnostic metric |
| A_{t+1} embeddings missing | FileNotFoundError on A_next .npy cache | FIX: Add additional encoding pass for A_{t+1} |
| [FR-M2] logs missing | Log search fails | FAIL: Mechanism logging not triggered |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE (all 4 indicators) | verify_mechanism_activated() |
| Both directions computed | TRUE | Shape check, FR-M2 log |
| Asymmetry measurable | Δ ≠ 0 for any tier | mean(H←A) - mean(A←H) |
| Hypothesis Supported (Gate) | p < 0.05 at >= 2/3 tiers | mannwhitneyu(H←A, A←H, alternative='greater') |
| Hypothesis Supported (Metric) | tiers_passing >= 2 | count(p_tier < 0.05) |

---

## PoC Success Check

**PoC Pass Condition (SHOULD_WORK Gate):**
1. Code runs without error
2. Both directions computed for all 3 tiers × 3 models
3. `C_sem^H←A > C_sem^A←H` with p < 0.05 at >= 2/3 RLHF tiers (Mann-Whitney, one-sided)

**Gate Failure Recovery:** If SHOULD_WORK gate fails (symmetric coherence result), document as scope limitation and reinterpret as "mutual contextual coherence" rather than power asymmetry. H-M4 proceeds regardless.

---

## Appendix: Reference Implementations

| Source | Relevance | Type |
|--------|-----------|------|
| h-m1/code/accommodation.py | Core C_sem computation (H←A direction proven) — extend to bidirectional | Internal (validated) |
| h-m1/code/statistics.py | Mann-Whitney, bootstrap, IPW, KS test functions | Internal (validated) |
| h-m1/code/visualize.py | 7 figure functions reusable | Internal (validated) |
| h-m1/code/run_experiment.py | Orchestration pattern (3-model × 3-tier loop) | Internal (validated) |
| Danescu-Niculescu-Mizil et al. [2011] | Directional accommodation asymmetry: lower-power interlocutors accommodate more | Theoretical foundation |
| Chang & Wang [2025] (arXiv:2405.07719) | Bidirectional word-level adaptation in LLM-human dialogue | Related work |
| 02b_verification_plan.md §2.2 (H-M2) | Full verification protocol specification | Primary specification |
| scipy.stats.mannwhitneyu | One-sided Mann-Whitney U implementation | Library |
| sentence-transformers documentation | SBERT encoding API | Library |

**Exa GitHub:** Unavailable (402) — consistent with h-e1, h-m1. No external implementations found.
**Archon KB:** 5 queries executed, 0 domain-relevant results (diffusion/CUDA content only) — consistent with h-e1, h-m1.
**Serena:** Skipped — analytical pipeline extension, no complex external code to analyze.

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-15T12:00:00

### Workflow History for This Hypothesis

| Event | Timestamp | Details |
|-------|-----------|---------|
| h-m2 set to IN_PROGRESS | 2026-03-15T11:41:42 | External loop starting Phase 2C → 3 → 4 |
| experiment_design.status = IN_PROGRESS | 2026-03-15T12:00:00 | Phase 2C Step 1 |
| Archon KB search completed | 2026-03-15T12:10:00 | 5 queries, 0 relevant results |
| Exa search attempted | 2026-03-15T12:15:00 | 2 queries, 402 error (unavailable) |
| Dataset/model confirmed | 2026-03-15T12:20:00 | Reusing h-m1 cache, type=standard |
| Experiment spec synthesized | 2026-03-15T12:30:00 | Level 1.5 specification complete |

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — 5 queries each), Exa (unavailable/402), Serena (skipped — analytical pipeline)*
*All specifications grounded in h-m1 validated infrastructure and 02b_verification_plan.md protocol*
*Next Phase: Phase 3 - Implementation Planning*
