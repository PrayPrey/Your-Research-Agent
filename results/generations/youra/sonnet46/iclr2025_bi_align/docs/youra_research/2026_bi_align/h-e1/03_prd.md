# Product Requirements Document: h-e1

**Hypothesis:** h-e1 — Semantic Accommodation Existence (EXISTENCE PoC)
**Phase:** 3 — Implementation Planning
**Date:** 2026-03-15
**Author:** Anonymous
**Type:** EXISTENCE (LIGHT tier — 15 tasks max)
**Gate:** MUST_WORK

---

## 1. Executive Summary

This PRD specifies requirements for implementing the **h-e1 semantic accommodation existence test**. The experiment tests whether human follow-up turns in HH-RLHF helpfulness conversations show statistically significant partner-specific semantic alignment to their preceding AI turns at the SBERT embedding level.

**Success criterion (PoC direction only):**
- `C_sem^H←A > 0` with bootstrap 95% CI lower bound > 0
- Cohen's d ≥ 0.1 between cos(H_next, A_actual) and cos(H_next, A_topic_matched)
- Three-way ordering: cos_actual > cos_topic > cos_random

---

## 2. Problem Statement

**Research Question:** Does interaction-specific semantic accommodation exist in HH-RLHF conversations beyond topical coherence?

**Null Hypothesis (H₀):** No interaction-specific accommodation. C_sem = E[cos(H_{t+1}, A_actual)] − E[cos(H_{t+1}, A_random)] ≤ 0 or below statistical threshold.

**Why This Matters:** If RLHF-optimized AI responses trigger greater human semantic alignment, this constitutes a measurable quality signal embedded in conversational dynamics — foundational for H-M1 through H-M4.

---

## 3. Scope

**In Scope (EXISTENCE PoC):**
- Data loading, parsing, and preprocessing for Anthropic/hh-rlhf (all 3 helpfulness splits pooled)
- SBERT embedding generation (all-MiniLM-L6-v2)
- Three-level control construction (actual / topic-matched KNN / random shuffle)
- C_sem computation with length and lexical overlap residualization
- Statistical testing (Mann-Whitney U, bootstrap CI, Cohen's d)
- Required visualization: gate metrics bar chart + 4 additional figures
- Mechanism activation verification code

**Out of Scope:**
- RLHF tier stratification (that's H-M1)
- Directional asymmetry (that's H-M2)
- Fine-tuning or model modification
- Synthetic data augmentation

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| **Name** | Anthropic/hh-rlhf |
| **Source** | HuggingFace Hub — `Anthropic/hh-rlhf` |
| **Splits** | helpful-base, helpful-rejection-sampled, helpful-online |
| **Total turns** | ~273,617 turns (est.) across all helpfulness splits |
| **Valid pairs (est.)** | ~100,000–140,000 after filtering |
| **Download method** | `load_dataset("Anthropic/hh-rlhf", data_dir="<split>")` |
| **Requires internet** | Yes (or pre-cached) |
| **Format** | `{"chosen": "\n\nHuman: ...\n\nAssistant: ...", "rejected": "..."}` |

**Preprocessing Pipeline:**
1. Parse `chosen` field: split on `\n\nHuman:` / `\n\nAssistant:` markers
2. Extract consecutive (H_{t+1}, A_t) pairs from chosen conversations
3. Filter: minimum 2 turns, non-empty turns
4. Strip whitespace
5. Length residualization: OLS `cos_sim ~ token_count(A_t)`, use residuals
6. Lexical overlap residualization: OLS `cos_sim ~ jaccard(H_{t+1}, A_t)`, use residuals

### 4.2 No Additional Datasets

h-e1 pools all three splits for maximum N — no separate dataset loading required for existence test.

---

## 5. Functional Requirements

### FR-1: Data Loading and Preprocessing Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Load all 3 helpfulness splits via `load_dataset("Anthropic/hh-rlhf", data_dir=<split>)` | MUST |
| FR-1.2 | Parse `chosen` conversation strings into (Human, AI) turn pair lists | MUST |
| FR-1.3 | Extract (H_{t+1}, A_t) consecutive pairs; minimum 2-turn filter | MUST |
| FR-1.4 | Pool all tiers (helpful-base + helpful-rejection-sampled + helpful-online) for h-e1 | MUST |
| FR-1.5 | Also extract prompt turn H_t for KNN topic-matching | MUST |
| FR-1.6 | Compute token counts per turn for length residualization | MUST |
| FR-1.7 | Compute Jaccard overlap (H_{t+1}, A_t) for lexical overlap residualization | MUST |

### FR-2: Embedding Generation Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Load `all-MiniLM-L6-v2` via `SentenceTransformer("all-MiniLM-L6-v2")` | MUST |
| FR-2.2 | Encode ALL turns (H_next, A_actual, H_prompt) with `normalize_embeddings=True` | MUST |
| FR-2.3 | Use batch_size=256, show_progress_bar=True | MUST |
| FR-2.4 | Save embeddings to disk: `{hypothesis_folder}/embeddings/*.npy` | MUST |
| FR-2.5 | Load from cache if embeddings already exist (skip re-encoding) | SHOULD |
| FR-2.6 | Output shape: (N_pairs, 384) for all-MiniLM-L6-v2 | MUST |

### FR-3: Control Construction Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Random shuffle baseline: `np.random.seed(42); np.random.shuffle(ai_indices)` — create A_random | MUST |
| FR-3.2 | Topic-matched KNN baseline: K=5 NearestNeighbors on prompt embeddings (cosine), exclude same conversation | MUST |
| FR-3.3 | Return mean embedding of K=5 topic-matched AI turns as A_topic_matched | MUST |
| FR-3.4 | All three levels: A_actual, A_topic_matched, A_random | MUST |

### FR-4: C_sem Computation and Residualization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Compute cos_actual = (H_next · A_actual) elementwise (dot product, normalized embeddings) | MUST |
| FR-4.2 | Compute cos_topic = (H_next · A_topic_matched) elementwise | MUST |
| FR-4.3 | Compute cos_random = (H_next · A_random) elementwise | MUST |
| FR-4.4 | C_sem = cos_actual.mean() − cos_random.mean() | MUST |
| FR-4.5 | Length residualization: OLS regression of each cos array on A_t token count; use residuals | MUST |
| FR-4.6 | Lexical overlap residualization: OLS regression on Jaccard(H_{t+1}, A_t); use residuals | MUST |

### FR-5: Statistical Testing Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Bootstrap CI for C_sem: n_bootstrap=1000, seed=42; report [2.5%, 97.5%] percentile CI | MUST |
| FR-5.2 | Mann-Whitney U: pairwise (actual vs topic, alternative='greater'); p < 0.05 | MUST |
| FR-5.3 | Mann-Whitney U: (topic vs random, alternative='greater'); p < 0.05 | MUST |
| FR-5.4 | Cohen's d bootstrap: n_bootstrap=1000, seed=42 for each pairwise contrast | MUST |
| FR-5.5 | Significance threshold: p < 0.05 (two-tailed where applicable) | MUST |
| FR-5.6 | Minimum N_pairs ≥ 1000 check before statistical tests | MUST |

### FR-6: Mechanism Activation Verification

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Implement `verify_mechanism_activated(results)` as specified in 02c_experiment_brief.md | MUST |
| FR-6.2 | Check: embeddings_computed, c_sem_positive, ci_lower_positive, ordering_holds, sufficient_pairs | MUST |
| FR-6.3 | Return (bool, dict) — passed flag + indicator dict | MUST |

### FR-7: Visualization Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-7.1 | Gate Metrics Bar Chart: C_sem with 95% CI; cos_actual/cos_topic/cos_random with error bars | MUST |
| FR-7.2 | Partner-Specificity Gradient Plot: line plot with error bars, Cohen's d annotations | SHOULD |
| FR-7.3 | C_sem Bootstrap Distribution Histogram with 95% CI shading and zero-line | SHOULD |
| FR-7.4 | Cosine Similarity Distributions: violin/box plots for three control levels | SHOULD |
| FR-7.5 | Residualization Check: scatter plots raw vs residualized | SHOULD |
| FR-7.6 | KNN Quality: distribution of cosine distances to K=5 neighbors | SHOULD |
| FR-7.7 | Save all figures to `{hypothesis_folder}/figures/` | MUST |

### FR-8: Main Experiment Orchestration

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.1 | Main script: `run_experiment.py` that orchestrates all steps sequentially | MUST |
| FR-8.2 | Early failure detection: log and fail fast on dataset load failure or zero pairs | MUST |
| FR-8.3 | Log N_pairs, embedding time, model name, key statistics | MUST |
| FR-8.4 | Write results to `{hypothesis_folder}/results.json` | MUST |

### FR-9: Robustness Models (Additional)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-9.1 | Run same pipeline with `paraphrase-MiniLM-L6-v2` as robustness check | SHOULD |
| FR-9.2 | Run same pipeline with `all-mpnet-base-v2` as robustness check | SHOULD |
| FR-9.3 | Report whether results hold across ≥ 2/3 models | SHOULD |

---

## 6. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | CPU execution sufficient; ~20 min for 273K turns with all-MiniLM-L6-v2 batch_size=256 |
| NFR-2 | Memory: ~8GB RAM for embeddings (273K × 384 × float32 ≈ 400MB) |
| NFR-3 | Reproducibility: all random operations seeded (seed=42) |
| NFR-4 | Results must be deterministic across runs on same hardware |
| NFR-5 | Code must run on standard Python 3.10+ environment |
| NFR-6 | GPU optional (accelerates encoding if available) |

---

## 7. Dependencies

### 7.1 Python Packages

```
sentence-transformers>=2.2.0
datasets>=2.0.0
scipy>=1.7.0
scikit-learn>=1.0.0
numpy>=1.21.0
matplotlib>=3.4.0
statsmodels>=0.13.0
tqdm>=4.62.0
```

### 7.2 External Data Access

- Internet access OR pre-downloaded HH-RLHF cache
- HuggingFace model hub (or local cache) for all-MiniLM-L6-v2 (~90MB)

---

## 8. File Structure

```
h-e1/
├── code/
│   ├── data_loader.py       # FR-1: Dataset loading and parsing
│   ├── embedder.py          # FR-2: Embedding generation with caching
│   ├── controls.py          # FR-3: Random shuffle + KNN topic-matched controls
│   ├── accommodation.py     # FR-4: C_sem computation + residualization
│   ├── statistics.py        # FR-5+6: Bootstrap, Mann-Whitney, Cohen's d, verification
│   ├── visualize.py         # FR-7: All required and optional figures
│   └── run_experiment.py    # FR-8: Main orchestration script
├── embeddings/              # Cached embeddings (auto-generated)
├── figures/                 # All visualization outputs
├── results.json             # Final experiment results
├── 02c_experiment_brief.md
├── 03_prd.md
├── 03_architecture.md       # (generated in Step 3)
├── 03_logic.md              # (generated in Step 5)
├── 03_config.md             # (generated in Step 5)
└── 03_tasks.yaml            # (generated in Step 9)
```

---

## 9. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Code runs without error | All steps complete | No uncaught exceptions |
| C_sem > 0 | Bootstrap CI lower bound > 0 | `c_sem > 0` AND `ci[0] > 0` |
| Partner-specificity | Cohen's d ≥ 0.1 (actual vs topic) | `bootstrap_cohen_d()` |
| Three-way ordering | cos_actual > cos_topic > cos_random | All three inequalities hold |
| N_pairs sufficient | ≥ 1,000 valid pairs | `n_pairs >= 1000` |
| Embedding dim | 384 (all-MiniLM-L6-v2) | `embed_dim == 384` |

**Gate Result:**
- **PASS** (gate.satisfied = true): All success criteria met → Unlocks H-M1, H-M3
- **FAIL** (gate.satisfied = false): C_sem ≤ 0 or ordering fails → STOP pipeline, ROUTE_TO_0

---

## 10. Constraints and Risk

| Risk | Mitigation |
|------|-----------|
| HH-RLHF dataset unavailable (no internet) | Fail early with clear error message; check HF cache |
| Zero valid pairs after filtering | Validate N ≥ 1000 before statistical tests; log parsing errors |
| KNN too slow on 273K embeddings | Use sklearn NearestNeighbors with cosine metric; test with batch |
| Null result (C_sem ≤ 0) | Expected outcome possible — report accurately per gate protocol |
| GPU memory if GPU used | Use CPU by default; GPU optional for acceleration only |

---

*PRD generated by Phase 3 Implementation Planning — Anonymous Pipeline*
*Hypothesis: h-e1 | Type: EXISTENCE | Gate: MUST_WORK | Tier: LIGHT (15 tasks max)*
