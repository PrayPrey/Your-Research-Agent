# Product Requirements Document: h-m1
## Tier-Monotonic Semantic Accommodation Scaling Across RLHF Quality Gradient

**Hypothesis:** h-m1
**Type:** MECHANISM
**Date:** 2026-03-14
**Status:** Implementation Planning
**Tier:** FULL
**Prerequisite:** h-e1 (VALIDATED — C_sem=0.3292, MUST_WORK PASS)

---

## 1. Executive Summary

This experiment extends the h-e1 validated pipeline (existence of human→AI semantic accommodation) to test **tier-monotonicity**: whether C_sem^H←A increases monotonically with RLHF alignment quality across three tiers (helpful_base < helpful_rejection_sampled < helpful_online). The core test is the Jonckheere-Terpstra monotonicity test replicated across 3 SBERT models. Success requires J-T p < 0.05 AND Cohen's d >= 0.1 in >= 2/3 models.

The implementation **extends the h-e1 codebase** (7 validated Python modules) with per-tier stratification, multi-model execution, and the Jonckheere-Terpstra statistical test. No novel neural architecture is involved — this is a statistical analysis pipeline.

---

## 2. Problem Statement

### 2.1 Background
H-E1 established that semantic accommodation (C_sem = 0.3292) exists as a large-effect phenomenon in HH-RLHF helpfulness conversations. H-M1 tests the **mechanism**: is this accommodation proportional to RLHF quality? If tier rank predicts C_sem monotonically, it confirms the epistemic authority hypothesis — higher-quality AI responses attract stronger semantic alignment from humans.

### 2.2 Research Question
Does C_sem^H←A increase monotonically with RLHF tier quality (T1 < T2 < T3), robust across >= 2/3 SBERT embedding models?

### 2.3 MUST_WORK Gate
If this hypothesis fails (J-T not significant OR effect too small), H-M2, H-M3, H-M4 are blocked and the pipeline routes to Phase 0.

---

## 3. Stakeholders

- **Researcher:** Anonymous
- **Pipeline:** YouRA (Phase 3 → Phase 4 execution)
- **Gate:** MUST_WORK (blocks downstream hypotheses)

---

## 4. Data Specification

### 4.1 Primary Dataset

| Property | Value |
|----------|-------|
| Name | Anthropic/hh-rlhf |
| Source | HuggingFace Datasets |
| HF ID | `Anthropic/hh-rlhf` |
| Download needed | ❌ Already cached at `.data_cache/datasets/hh-rlhf` (from h-e1) |
| Loading method | `load_dataset('Anthropic/hh-rlhf', data_dir=tier, verification_mode='no_checks')` |

**Tier Structure (Independent Variable):**
| Tier | Split Name | Rank | Est. Pairs |
|------|-----------|------|------------|
| T1 | helpful-base | 1 (lowest) | ~43,000 |
| T2 | helpful-rejection-sampled | 2 (middle) | ~45,000 |
| T3 | helpful-online | 3 (highest) | ~44,000 |
| **Total** | All tiers | — | **~155,362** |

**No manual download required** — all data already cached from h-e1.

### 4.2 Models (Inference-Only, No Training)

| Model | HuggingFace ID | Dim | Role |
|-------|---------------|-----|------|
| all-MiniLM-L6-v2 | `sentence-transformers/all-MiniLM-L6-v2` | 384 | Primary |
| paraphrase-MiniLM-L6-v2 | `sentence-transformers/paraphrase-MiniLM-L6-v2` | 384 | Robustness 1 |
| all-mpnet-base-v2 | `sentence-transformers/all-mpnet-base-v2` | 768 | Robustness 2 |

All models available via `sentence-transformers` library. No download task required (auto-downloaded on first use).

### 4.3 Baseline Computation
- **Matched-shuffle baseline:** Within each tier, shuffle A_embeddings independently (seed=42)
- **C_sem = mean(cos_actual) - mean(cos_random)** per tier
- **No cross-tier shuffle** (would confound tier comparisons)

---

## 5. Functional Requirements

### 5.1 Data Pipeline (FR-D)

**FR-D1: Per-Tier Data Splitting**
- Extend h-e1 DataLoader to load 3 tiers separately
- `load_dataset()` with `data_dir` parameter per tier
- Parse conversation JSON per tier: extract (H_{t+1}, A_t) pairs
- Output: `{tier_name: [(H_text, A_text, H_prompt), ...]}` for each of 3 tiers
- Minimum n_pairs per tier: 1,000 (gate: fail if any tier < 1,000)

**FR-D2: Multi-Model Embedding**
- Encode all 3 SBERT models for all 3 tiers
- Cache key format: `{model_slug}_{tier}_{n_pairs}` (extend h-e1 pattern)
- Reuse h-e1 `embedder.py` disk-cache infrastructure
- batch_size=256, normalize_embeddings=True

**FR-D3: Within-Tier Shuffle Baseline**
- For each tier × model: shuffle A_embeddings within-tier (seed=42)
- `np.random.default_rng(42).permutation(A_emb_tier)`

### 5.2 Statistical Analysis (FR-S)

**FR-S1: Per-Tier C_sem Computation**
- For each model × tier: compute C_sem = mean(cos_actual) - mean(cos_random)
- Compute 95% bootstrap CI (n=1000, seed=42) per tier
- Output: matrix [3 models × 3 tiers] of C_sem values

**FR-S2: Jonckheere-Terpstra Monotonicity Test**
- `scipy.stats.jonckheere_terpstra(*ordered_cos, alternative='increasing')`
- Input: raw cosine similarity arrays per tier (NOT OLS residuals — zero mean by construction)
- Run for each of 3 SBERT models independently
- Store: J-T statistic, p-value per model

**FR-S3: Pairwise Mann-Whitney + Bonferroni**
- 3 pairs: (T1, T2), (T2, T3), (T1, T3)
- `scipy.stats.mannwhitneyu(alternative='two-sided')`
- Bonferroni threshold: α/3 = 0.0167
- Run for each model

**FR-S4: Bootstrap Cohen's d**
- For all tier pairs × all models: bootstrap Cohen's d (n=1000, seed=42)
- Report 95% CI for each d
- Threshold: d >= 0.1 (minimum effect)

**FR-S5: KS Test + IPW (Robustness)**
- KS test on prompt embedding distributions across tier pairs
- If any KS p < 0.05: apply inverse-probability weighting, recompute C_sem
- Report: raw vs IPW-weighted comparison

**FR-S6: Model Consistency Check**
- Count: how many models satisfy J-T p < 0.05 AND d >= 0.1
- Gate check: consistent_count >= 2/3
- Report: per-model results + consistency summary

### 5.3 Gate Evaluation (FR-G)

**FR-G1: Primary Gate (MUST_WORK)**
- J-T p < 0.05 AND d >= 0.1 in >= 2/3 SBERT models
- Auto-evaluate and write gate result to output

**FR-G2: Mechanism Activation Verification**
- 5 indicators: tier_logs_found, all_tiers_have_pairs, csem_differs_across_tiers, jt_computed, all_models_ran
- All 5 must be True for mechanism activation

### 5.4 Visualization (FR-V)

**FR-V1 (Mandatory):** Bar chart of C_sem per tier for each SBERT model (error bars = bootstrap 95% CI), annotated with J-T p-value.

**FR-V2:** Line plot of C_sem(T1), C_sem(T2), C_sem(T3) across 3 SBERT models (tier monotonicity).

**FR-V3:** Pairwise Cohen's d heatmap (tier pairs × models), threshold annotation.

**FR-V4:** Violin plot of raw cosine distributions per tier (primary model).

**FR-V5:** Bootstrap C_sem kernel density per tier × primary model.

**FR-V6 (Conditional):** IPW sensitivity comparison (only if KS test triggered).

**FR-V7:** KS test statistics summary bar chart.

All figures saved to `h-m1/figures/`.

### 5.5 Execution & Reporting (FR-E)

**FR-E1:** Dry run with n=1500 pairs (first 500 per tier) before full experiment.
**FR-E2:** Full experiment on all ~155,362 pairs across 3 tiers × 3 models.
**FR-E3:** Log tier C_sem values: `"Tier {t} C_sem computed: {value:.4f}"` for activation verification.
**FR-E4:** Output YAML report with all metrics.
**FR-E5:** Generate `04_validation.md` report with gate evaluation.

---

## 6. Non-Functional Requirements

### 6.1 Performance
- Embedding: batch_size=256 (validated in h-e1 — optimal for GPU)
- KNN: k=5, n_jobs=1 (CRITICAL: n_jobs=-1 crashes on 155k scale, OpenBLAS double-free)
- OPENBLAS_NUM_THREADS=4 (set before run)
- Expected runtime: ~30-90 min (3 models × 3 tiers embeddings + stats)

### 6.2 Reproducibility
- All seeds fixed: bootstrap_seed=42, shuffle_seed=42
- Cache all embeddings to disk: `{model_slug}_{tier}_{n_pairs}`
- `verification_mode='no_checks'` for dataset loading

### 6.3 Correctness
- Statistical tests on raw cosine arrays (NOT OLS residuals)
- Within-tier shuffle only (NOT cross-tier)
- Cache keys include tier name to prevent stale cache hits

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| sentence-transformers | >= 2.2.0 | SBERT embeddings |
| datasets | >= 2.0.0 | HuggingFace dataset loading |
| scipy | >= 1.7.0 | `jonckheere_terpstra`, `mannwhitneyu`, `ks_2samp` |
| numpy | >= 1.21 | Array operations, bootstrap |
| scikit-learn | >= 1.0 | KNN for topic-match control |
| matplotlib | >= 3.5 | Figures |
| seaborn | >= 0.11 | Heatmap/violin plots |
| pyyaml | >= 5.4 | Output reporting |
| torch | >= 1.9 | SBERT backend |
| statsmodels | >= 0.13 | OLS residualization |
| tqdm | >= 4.62 | Progress bars |

**All packages already installed** (validated by h-e1 environment). No new installs required.

### 7.2 External Code Dependencies

| Dependency | Location | Usage |
|-----------|----------|-------|
| h-e1 DataLoader | `h-e1/code/data_loader.py` | Extend for per-tier splits |
| h-e1 Embedder | `h-e1/code/embedder.py` | Reuse with tier cache keys |
| h-e1 Controls | `h-e1/code/controls.py` | Per-tier KNN topic control |
| h-e1 Accommodation | `h-e1/code/accommodation.py` | Per-tier C_sem computation |
| h-e1 Statistics | `h-e1/code/statistics.py` | Add J-T + Bonferroni |
| h-e1 Visualize | `h-e1/code/visualize.py` | Add tier comparison plots |

---

## 8. Success Criteria

### Primary Gate (MUST_WORK)
- J-T p < 0.05 AND Cohen's d >= 0.1 for tier contrast in **>= 2/3 SBERT models**

### Secondary
- C_sem(T3) > C_sem(T2) > C_sem(T1) direction consistent across all 3 models
- Pairwise Mann-Whitney significant (Bonferroni-corrected) for key contrasts
- All 5 mechanism activation indicators = True

### Failure Condition
- < 2/3 models satisfy J-T p < 0.05 AND d >= 0.1
- Any tier has n_pairs < 1,000
- Code fails to run

---

## 9. Implementation Notes

### 9.1 Critical Bug Fixes from h-e1 (MUST carry over)
1. `knn_n_jobs=1` — NEVER use n_jobs=-1 (OpenBLAS double-free on 155k scale)
2. `verification_mode='no_checks'` — HuggingFace NonMatchingSplitsSizesError fix
3. Cache key must include tier: `{model_slug}_{tier}_{n_pairs}`
4. Statistical tests on **raw cosine arrays** NOT OLS residuals (zero mean by construction)

### 9.2 Architecture Pattern
- h-m1 code lives in `h-m1/code/` (extends h-e1 pattern)
- Import h-e1 modules via relative path or copy-and-extend
- Keep the same module structure for consistency

---

*Generated by Phase 3 PRD step (inline execution)*
*Source: h-m1/02c_experiment_brief.md + h-m1/02b_context.md*
