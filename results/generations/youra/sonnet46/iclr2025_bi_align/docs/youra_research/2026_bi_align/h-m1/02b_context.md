# Phase 2B Context: H-M1 — Tier-Monotonic Semantic Accommodation Scaling

**Generated:** 2026-03-14 (JIT by Phase 2C Step 1)
**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Gate:** MUST_WORK
**Prerequisites:** h-e1 ✅ VALIDATED

---

## 1. Hypothesis Information

### Statement
RLHF tier quality (helpful_base rank=1, helpful_rejection_sampling rank=2, helpful_online rank=3) produces monotonically increasing C_sem^H←A across tiers (Jonckheere-Terpstra p < 0.05, Cohen's d >= 0.1 for tier contrast), consistent across >= 2/3 SBERT models (all-MiniLM-L6-v2, paraphrase-MiniLM-L6-v2, all-mpnet-base-v2). Tests tier-monotonicity of semantic accommodation driven by RLHF quality gradient.

### Rationale
This is the core mechanistic claim linking RLHF quality gradient to accommodation magnitude. It tests whether the existence-level C_sem (established in H-E1 as 0.3292) is specifically driven by tier quality, not just an artifact of the dataset or SBERT geometry. Multi-model replication rules out geometry-specific artifacts. This is the primary test of Prediction P1.

### Variables
- **IV:** RLHF alignment tier (categorical, 3 levels: helpful_base/RS/online; rank 1/2/3)
- **DV:** C_sem^H←A per tier (continuous)
- **CV:** Prompt embedding distribution (KS test + IPW if distributions differ), response length, lexical overlap

---

## 2. Experimental Setup

### Dataset
| Component | Selection |
|-----------|-----------|
| Name | Anthropic/hh-rlhf (helpfulness splits) |
| Type | standard |
| Splits | helpful-base, helpful-rejection-sampled, helpful-online (3 tiers) |
| Source | HuggingFace: `datasets.load_dataset('Anthropic/hh-rlhf', data_dir='helpful-base|helpful-rejection-sampled|helpful-online')` |
| Size | ~273,617 conversation turns total (~155,362 pairs from h-e1) |
| Cache | Already downloaded at: `.data_cache/datasets/hh-rlhf` |

### Models
| Component | Selection |
|-----------|-----------|
| Primary | all-MiniLM-L6-v2 (SBERT, 384-dim) |
| Robustness 1 | paraphrase-MiniLM-L6-v2 |
| Robustness 2 | all-mpnet-base-v2 |
| Type | sentence-transformers (pre-trained, inference-only) |
| Source | HuggingFace model hub / sentence-transformers library |

---

## 3. Verification Protocol (from Phase 2B)

1. Compute C_sem^H←A **per tier** using matched-shuffle baseline for each of 3 SBERT models separately.
2. Run **Jonckheere-Terpstra monotonicity test** across three tiers (alternative: increasing).
3. Compute pairwise Mann-Whitney U + bootstrap Cohen's d (n=1000, seed=42) for all tier pairs; apply Bonferroni correction.
4. Run KS test on prompt embedding distributions across tiers; if KS p < 0.05, apply inverse-probability weighting and recompute.
5. Check consistency across >= 2/3 SBERT models; report all three models transparently.

---

## 4. Success Criteria

- **Primary:** J-T p < 0.05 AND d >= 0.1 for tier contrast in >= 2/3 SBERT models
- **Secondary:** Monotonic direction consistent across all three models (even if only >= 2/3 significant)

---

## 5. Gate Condition

- **Type:** MUST_WORK
- **If Fail:** H-M2, H-M3, H-M4 blocked; document tier monotonicity failure; ROUTE_TO_0 or scope to existence-only claim

---

## 6. Baseline & Comparison Targets

| Method | Evidence |
|--------|----------|
| Function-word coordination (Danescu et al. 2011) | Monotonic power-driven accommodation in Wikipedia/Supreme Court |
| Chang & Wang 2025 | Word-level style matching in LLM-human dialog |
| H-E1 validated result (this pipeline) | C_sem=0.3292 (pooled), d=1.998 (actual vs random), n=155,362 pairs |

---

## 7. Key Assumptions

| ID | Assumption | Risk |
|----|------------|------|
| A1 | SBERT captures accommodation-relevant semantic variation | High — validated by H-E1 (partner-specificity confirmed) |
| A2 | HH-RLHF tier user populations comparable | Medium — require KS test |
| A4 | Semantic accommodation exists at SBERT level | Resolved by H-E1 PASS |

---

## 8. Prerequisites Satisfied

| Prerequisite | Result | Key Finding |
|-------------|--------|-------------|
| H-E1 | PASS (MUST_WORK) | C_sem=0.3292, 95% CI [0.3280, 0.3304], all Mann-Whitney p=0.0, Cohen's d(actual vs random)=1.998, partner-specificity confirmed (0.3534 > 0.2688 > 0.0241) |

---

## 9. Reusable Components from H-E1

| Component | File | Reuse |
|-----------|------|-------|
| DataLoader (load_all_splits) | `h-e1/code/data_loader.py` | Yes — extend to return per-tier splits |
| Embedder (SentenceTransformer + cache) | `h-e1/code/embedder.py` | Yes — reuse for all 3 SBERT models |
| Controls (random + KNN K=5) | `h-e1/code/controls.py` | Yes — apply per-tier |
| C_sem computation | `h-e1/code/accommodation.py` | Yes — compute per-tier |
| Statistical testing suite | `h-e1/code/statistics.py` | Yes — add J-T test + Bonferroni |
| Visualization suite | `h-e1/code/visualize.py` | Yes — add tier comparison plots |

**Critical hyperparameters (carry over from H-E1):**
- batch_size=256, knn_k=5, knn_n_jobs=1 (IMPORTANT: n_jobs=-1 crashes)
- bootstrap_n=1000, bootstrap_seed=42, OPENBLAS_NUM_THREADS=4
- verification_mode='no_checks' for dataset loading
- Cache key: `{model_slug}_{n_pairs}` to avoid stale cache
- Statistical tests on raw cosines, NOT OLS residuals

---

*JIT-generated by Phase 2C Step 1 from 02b_verification_plan.md and h-e1/04_validation.md*
