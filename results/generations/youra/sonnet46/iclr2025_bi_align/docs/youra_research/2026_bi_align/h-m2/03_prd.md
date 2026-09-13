# PRD: h-m2 — Bidirectional C_sem Directional Asymmetry

**stepsCompleted**: [prd-step-01, prd-step-02, prd-step-03, prd-step-04, prd-step-05]
**Hypothesis**: h-m2
**Type**: MECHANISM (INCREMENTAL — extends h-m1)
**Date**: 2026-03-15
**Gate**: SHOULD_WORK
**Prerequisites**: h-m1 (VALIDATED — J-T p=0.001, Cohen d 0.18–0.25)
**Base Hypothesis**: h-m1

---

## 1. Executive Summary

H-M2 tests whether human-to-AI semantic accommodation (C_sem^H←A) systematically exceeds AI-to-human accommodation (C_sem^A←H) at ≥ 2/3 RLHF tiers using Mann-Whitney U (one-sided, p < 0.05). This directional asymmetry test is grounded in the epistemic authority / power asymmetry hypothesis (Danescu-Niculescu-Mizil et al. 2011): lower-power interlocutors accommodate more to higher-status partners. RLHF-optimized AI responses carry high epistemic quality signals, predicting greater human accommodation than AI accommodation to human phrasing.

The implementation extends the h-m1 codebase minimally: adding the `A←H` direction to `compute_tier_csem_matrix()` and a new statistical test function. All 18 embedding .npy files from h-m1 are reused. An additional encoding pass may be needed if `A_{t+1}` embeddings (for the A←H direction) are not already cached.

---

## 2. Problem Statement

### Background
H-E1 established positive semantic accommodation (C_sem = 0.3292 > 0). H-M1 established monotonic tier-quality dependence (J-T p = 0.001, Cohen d 0.18–0.25). H-M2 now tests the directionality: is H←A accommodation systematically larger than A←H?

### Research Question
Does C_sem^H←A > C_sem^A←H with statistical significance (Mann-Whitney p < 0.05) at ≥ 2/3 RLHF tiers, consistent across ≥ 2/3 SBERT models?

### Motivation
If confirmed, this asymmetry supports the epistemic authority interpretation of semantic accommodation in RLHF conversations. If not confirmed (symmetric coherence result), this refines the thesis without blocking H-M4.

---

## 3. Scope

### In Scope
- Bidirectional C_sem computation: H←A (reuse from h-m1) + A←H (new)
- Per-tier Mann-Whitney U test (one-sided): H←A > A←H
- IPW correction for covariate shift (same procedure as h-m1)
- Asymmetry magnitude monotonicity secondary analysis (Δ_asymmetry: T3 > T2 > T1?)
- 3 SBERT model consistency check (≥ 2/3 required)
- Required visualization + 5 additional figures

### Out of Scope
- Retraining any SBERT model
- New datasets beyond Anthropic/hh-rlhf
- Cross-conversation comparison (only within-conversation turn pairs)

---

## 4. Data Specification

### Primary Dataset

| Field | Value |
|-------|-------|
| **Name** | Anthropic/hh-rlhf |
| **HuggingFace ID** | `Anthropic/hh-rlhf` |
| **Type** | standard (real, no synthetic data) |
| **Cache** | `.data_cache/datasets/hh-rlhf` (cached from h-e1/h-m1) |
| **Tiers** | helpful-base (43,835), helpful-rejection-sampled (52,421), helpful-online (22,007) |
| **Total pairs** | 155,362 conversation turn-pairs |

**Data preparation task**: NOT REQUIRED — dataset fully cached from h-m1. `load_all_splits()` and `split_by_tier()` from h-m1 `data_loader.py` reused as-is.

### Embedding Cache (h-m1 Heritage)

| Cache Files | Status | Reuse |
|-------------|--------|-------|
| `{model}_H_next_{tier}.npy` (×9) | Cached ✓ | Full reuse |
| `{model}_A_curr_{tier}.npy` (×9) | Cached ✓ | Full reuse |
| `{model}_H_curr_{tier}.npy` | May be missing | Needed for A←H direction |
| `{model}_A_next_{tier}.npy` | **May be missing** | **Critical: needed for A←H** |

**CRITICAL CHECK for Phase 4**: Verify h-m1 cache includes `H_curr` and `A_next` embeddings. If missing, additional encoding pass required (~1.5–2h per model, 3 models).

---

## 5. Functional Requirements

### FR-1: Bidirectional Embedding Cache Verification
- **What**: Check h-m1 embedding cache for `A_next_{tier}.npy` and `H_curr_{tier}.npy` files per model
- **Who**: data_loader.py / embedder.py
- **Gate**: If missing, encode and cache; if present, load directly
- **Test**: `assert os.path.exists(cache_path)` for all 6×3 = 18 additional .npy files

### FR-2: H←A C_sem Computation (Reuse from h-m1)
- **What**: Compute C_sem^H←A per tier per model using proven h-m1 implementation
- **Formula**: `C_sem^H←A = mean(cos(H_{t+1}, A_t)) - mean(cos(H_{t+1}, A_t[shuffle_H]))`
- **KNN shuffle**: k=5, n_jobs=1 (CRITICAL: not -1)
- **IPW**: Apply if KS p < 0.05 (expected: yes, same as h-m1)
- **Output**: dict `{tier: csem_H_given_A_array}` per model

### FR-3: A←H C_sem Computation (New for h-m2)
- **What**: Compute C_sem^A←H per tier per model (new direction)
- **Formula**: `C_sem^A←H = mean(cos(A_{t+1}, H_t)) - mean(cos(A_{t+1}, H_t[shuffle_A]))`
- **KNN shuffle**: build fresh from A_{t+1} and H_t embeddings, k=5, n_jobs=1
- **IPW**: Apply KS test on A←H tier distributions; apply IPW if triggered
- **Output**: dict `{tier: csem_A_given_H_array}` per model
- **Log**: `[FR-M2] Tier {tier}: C_sem^H←A={:.4f}, C_sem^A←H={:.4f}, p={:.4f}, d={:.4f}`

### FR-4: Directional Asymmetry Statistical Test
- **What**: Per-tier Mann-Whitney U (one-sided: H←A > A←H) for each model
- **Test**: `mannwhitneyu(csem_H_given_A, csem_A_given_H, alternative='greater')`
- **Secondary**: Cohen's d (H←A vs A←H)
- **Gate metric**: `tiers_passing = count(p_tier < 0.05)` ≥ 2 required
- **All baseline models**: all-MiniLM-L6-v2, paraphrase-MiniLM-L6-v2, all-mpnet-base-v2

### FR-5: Mechanism Activation Verification
- **What**: `verify_mechanism_activated(results_by_tier, logs)` check
- **Indicators**: both_directions_computed, shapes_match, asymmetry_nonzero, fr_m2_logs_found
- **Output**: `(all_pass: bool, indicators: dict)`

### FR-6: Asymmetry Monotonicity Secondary Analysis
- **What**: Check if `Δ_asymmetry = H←A - A←H` increases with tier quality (T3 > T2 > T1)
- **Test**: Jonckheere-Terpstra or simple rank comparison
- **Status**: Secondary metric, not a gate condition

### FR-7: Multi-Model Consistency Check
- **What**: Gate requires ≥ 2/3 SBERT models to show same directional pattern
- **Models**: all-MiniLM-L6-v2, paraphrase-MiniLM-L6-v2, all-mpnet-base-v2
- **Output**: `models_passing` count

### FR-8: Ablation Variants

| Variant | Description | Implementation |
|---------|-------------|----------------|
| H←A only (baseline) | Reuse h-m1 results | Load from h-m1 validation |
| A←H only (new) | Measure AI accommodation | FR-3 |
| H←A vs A←H per-tier | Core gate test | FR-4 |
| Asymmetry × tier interaction | Secondary analysis | FR-6 |
| IPW-adjusted asymmetry | Robustness | FR-2, FR-3 with IPW |
| Per-model consistency | 3 SBERT models | FR-7 |

### FR-9: Visualization
- **Required (mandatory)**: Grouped bar chart — C_sem^H←A vs C_sem^A←H per tier (3 groups × 2 bars), with CI whiskers
- **Additional figures** (LLM autonomous):
  1. Directional asymmetry bars: grouped bar + CI × 3 tiers × 3 models
  2. Asymmetry delta line: Δ_asymmetry = H←A - A←H across tiers
  3. Pairwise distribution violin: distribution of per-pair csem both directions
  4. Statistical significance heatmap: p-values for H←A > A←H (tier × model grid)
  5. Bootstrap CI comparison: Bootstrap CI for both directions per tier
  6. IPW-adjusted asymmetry: bar + error, raw vs IPW-corrected

All figures saved to `h-m2/figures/`.

---

## 6. Non-Functional Requirements

| Category | Requirement |
|----------|------------|
| **Correctness** | Mann-Whitney one-sided (`alternative='greater'`), not two-sided |
| **Reproducibility** | seed=42, bootstrap_resamples=1000 |
| **Scale** | Full dataset: 155,362 pairs (no subsampling) |
| **KNN safety** | n_jobs=1 (NOT -1 — crashes at 155k scale, h-m1 lesson) |
| **Caching** | All embeddings cached; re-encode only if `A_next` or `H_curr` missing |
| **Logging** | `[FR-M2]` prefix for all mechanism log lines |
| **Testing** | Unit tests for all new functions (pytest) |
| **Infrastructure** | FULL tier: YAML + dataclass config, structured logging, unit tests |

---

## 7. Dependencies

### 7.1 Python Packages

```
sentence-transformers>=2.2.2
torch>=2.0.0
datasets>=2.14.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
pandas>=2.0.0
pytest>=7.4.0
pyyaml>=6.0
```

**No new packages required** — identical to h-m1 environment (fully validated).

**Environment setup task**: NOT REQUIRED — environment verified from h-m1 (all packages installed).

### 7.2 Internal Dependencies

| Module | Source | Reuse Pattern |
|--------|--------|---------------|
| `data_loader.py` | h-m1/code/ | copy-extend (add `H_curr`/`A_next` caching) |
| `embedder.py` | h-m1/code/ | copy as-is |
| `controls.py` | h-m1/code/ | copy as-is (rebuild A←H shuffle indices) |
| `accommodation.py` | h-m1/code/ | copy-extend (add `direction='A←H'` support) |
| `statistics.py` | h-m1/code/ | copy-extend (add `test_directional_asymmetry()`) |
| `visualize.py` | h-m1/code/ | copy-extend (add bidirectional figures) |
| `run_experiment.py` | h-m1/code/ | rewrite as h-m2 orchestrator |

### 7.3 External Reference Implementations

| Reference | Relevance |
|-----------|-----------|
| Danescu-Niculescu-Mizil et al. [2011] | Directional accommodation asymmetry theory |
| Chang & Wang [2025] (arXiv:2405.07719) | Bidirectional word-level LLM-human adaptation |
| scipy.stats.mannwhitneyu | One-sided Mann-Whitney U |

---

## 8. Success Criteria

### Gate Condition (SHOULD_WORK)
- **Primary**: `tiers_passing >= 2` — C_sem^H←A > C_sem^A←H, p < 0.05 (one-sided Mann-Whitney) at ≥ 2/3 tiers
- **Consistency**: ≥ 2/3 SBERT models show same directional result
- **Mechanism**: all 4 `verify_mechanism_activated()` indicators = True

### Fail Recovery (SHOULD_WORK gate)
If gate fails (symmetric coherence result):
- Document as scope limitation ("mutual contextual coherence" reinterpretation)
- H-M4 proceeds regardless
- No Phase 0 routing

### Reporting Metrics
| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| `C_sem^H←A` per tier | Already established (h-m1) | Recomputed/loaded |
| `C_sem^A←H` per tier | Expected < C_sem^H←A | Computed fresh |
| `Δ_asymmetry` | > 0 with p < 0.05 | H←A − A←H |
| `p_MW` per tier | < 0.05 | mannwhitneyu(..., alternative='greater') |
| `tiers_passing` | >= 2 (gate) | count(p < 0.05) |
| `d_MW` | Reported (not threshold) | Cohen's d |

---

## 9. Out-of-Scope Items

- Training or fine-tuning any model
- Cross-dataset generalization
- Any novel model architecture
- Changes to RLHF tier definitions
- Comparison to external baselines (beyond internal h-m1 H←A direction)

---

*Generated by Phase 3 Step 2 (Inline PRD generation — BMAD PRD workflow path not found in environment)*
*Based on: h-m2/02c_experiment_brief.md, h-m1 validated codebase*
*Date: 2026-03-15*
