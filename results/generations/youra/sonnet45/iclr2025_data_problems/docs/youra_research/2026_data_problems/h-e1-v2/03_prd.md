# Product Requirements Document: h-e1-v2
# Targeted Model Card Sampling for Documentation Feature Variance

**Hypothesis:** h-e1-v2 (EXISTENCE — SCOPE_REFINEMENT from h-e1)
**Date:** 2026-03-17
**Type:** EXISTENCE PoC
**Gate:** MUST_WORK
**Tier:** LIGHT (≤15 tasks)

---

## 1. Executive Summary

h-e1-v2 implements a minimal modification to the validated h-e1 codebase: replacing alphabetical model card retrieval with targeted family-based sampling. The root cause of h-e1's PARTIAL result was that alphabetical sampling (0–A range: 177 cards) retrieved models from families that do not document advanced curation practices (perplexity filtering, decontamination). By prioritizing well-documented families (LLaMA, Mistral, Qwen, Falcon, Pythia, OLMo), h-e1-v2 targets ≥200 models with ≥3/4 binary documentation features showing non-zero variance, enabling the downstream OLS regression pipeline.

**Primary Deliverable:** A valid LLM Documentation-Benchmark Registry (n≥200 models) with sufficient feature variance (≥3/4 features) to proceed with H-M1 through H-M3 analyses.

---

## 2. Problem Statement

**H-e1 PARTIAL Result:**
- `n_analyzable` = 4,488 (PASS — registry infrastructure works)
- `n_features_with_variance` = 2/4 (FAIL — `perplexity_filter_documented` and `decontamination_documented` had zero variance)

**Root Cause:** 177/4,497 model cards retrieved from alphabetical 0–A range. Models in that range (fine-tuned derivatives) do not systematically document advanced curation practices.

**Required Fix:** Sort model_ids to prioritize well-documented model families BEFORE retrieving cards. This is a single-function addition to `main.py`.

**Impact:** All downstream hypotheses (h-m1, h-m2, h-m3) require a registry with ≥3/4 feature variance. h-e1-v2 is a GATE — pipeline stops if it fails.

---

## 3. Hypothesis Specification

**Statement:** Under the Open LLM Leaderboard v2 snapshot (`open-llm-leaderboard/contents`), if model cards from well-documented model families (LLaMA, Mistral, Qwen, Falcon, Pythia, OLMo) are retrieved in targeted fashion, then a dataset of ≥200 models with non-missing binary curation documentation features in ≥3/4 dimensions, ≥4/6 benchmark scores, and recoverable parameter count can be assembled.

**Success Gate (MUST_WORK):**
- `n_analyzable ≥ 200` AND `n_features_with_variance ≥ 3`
- Both conditions must be TRUE to proceed

---

## 4. Data Specification

### 4.1 Primary Data Sources

| Source | Access Method | Status |
|--------|--------------|--------|
| Open LLM Leaderboard v2 | `datasets.load_dataset("open-llm-leaderboard/contents", split="train")` | Auto-download — NO task needed |
| HuggingFace Model Cards | `huggingface_hub.ModelCard.load(model_id)` (with checkpoint resume) | Programmatic API |

**No manual downloads required.** All data accessed programmatically.

### 4.2 Dataset Properties

| Property | Value |
|----------|-------|
| Leaderboard rows | ~4,576 (validated from h-e1) |
| Post-benchmark-filter | ~4,488 (≥4/6 benchmarks non-missing) |
| Targeted family models (priority) | ~300–600 (LLaMA/Mistral/Qwen known to have hundreds of variants) |
| Target registry size | ≥200 models with complete feature set |
| Benchmark columns (v2) | IFEval, BBH, MATH Lvl 5, GPQA, MUSR, MMLU-PRO → `avg_score` |
| Parameter source | `params_b` column in leaderboard (validated in h-e1) |

### 4.3 Feature Engineering (Pre-registered, Unchanged from h-e1)

| Feature | Regex Pattern | Expected Variance |
|---------|--------------|-------------------|
| `dedup_documented` | `dedup\|near.?dup\|minhash\|exact.?dedup` | Present (showed variance in h-e1) |
| `perplexity_filter_documented` | `perplexity.{0,20}filter\|ppl.{0,10}filter` | **TARGET** (zero in h-e1) |
| `domain_composition_documented` | `domain.{0,30}(%\|percent\|composition)\|data.{0,30}mix` | Present (showed variance in h-e1) |
| `decontamination_documented` | `decontaminat\|n.?gram.{0,20}overlap\|benchmark.{0,20}holdout` | **TARGET** (zero in h-e1) |

### 4.4 Targeted Family Configuration (NEW in h-e1-v2)

```python
TARGETED_FAMILY_PREFIXES = [
    "meta-llama/", "NousResearch/Llama",   # LLaMA family
    "mistralai/",                            # Mistral
    "Qwen/",                                 # Qwen
    "tiiuae/falcon",                         # Falcon
    "EleutherAI/pythia",                     # Pythia
    "allenai/OLMo",                          # OLMo
]
```

**Priority logic:** Targeted families first (sorted by family), remainder alphabetical.

---

## 5. Functional Requirements

### FR-1: Targeted Family Sort (CORE CHANGE)

- **Description:** Add `sort_model_ids_by_family()` function to `main.py`
- **Input:** `model_ids: list[str]` — all models passing benchmark filter
- **Output:** Reordered `list[str]` with targeted families first, remainder alphabetical
- **Integration Point:** `run_pipeline()` — replace `model_ids = filtered_df['model_name'].tolist()` with `model_ids = sort_model_ids_by_family(filtered_df['model_name'].tolist())`
- **REUSE:** All other h-e1 functions unchanged

### FR-2: Leaderboard Loading (REUSE)

- Load `open-llm-leaderboard/contents` dataset from HuggingFace
- Filter: ≥4/6 benchmark scores non-missing
- Extract `fullname` as model_id, `params_b` for parameter count
- **Source:** `data_collection.py` (h-e1, unchanged)

### FR-3: Model Card Retrieval with Checkpoint (REUSE)

- `retrieve_model_cards(model_ids, ...)` processes in priority order
- Checkpoint-based resume — handles HF API rate limits (exponential backoff, max 5 retries)
- Stores retrieved cards incrementally to `cards_cache.json`
- **Source:** `data_collection.py` (h-e1, unchanged)

### FR-4: Feature Extraction (REUSE)

- Apply 4 pre-registered regex patterns to model card text
- Produce `dedup_documented`, `perplexity_filter_documented`, `domain_composition_documented`, `decontamination_documented` binary columns
- **Source:** `feature_extraction.py` (h-e1, unchanged)

### FR-5: Registry Assembly (REUSE)

- Build `registry_df` from leaderboard + model cards
- Compute: `doc_score` (0–4 sum), `log_params`, `log_tokens`, `arch_family`
- Filter: keep models with recoverable parameter count
- **Source:** `registry_builder.py` (h-e1, unchanged)

### FR-6: OLS Analysis (REUSE)

- Fit baseline OLS: `avg_score ~ log_params + log_tokens + C(arch_family)`
- Fit proposed OLS: adds `doc_score`
- Report: `n_analyzable`, `n_features_with_variance`, `delta_R2`, `beta_docs`
- **Source:** `analysis.py` (h-e1, unchanged)

### FR-7: Gate Metric Computation

- Compute and report:
  - `n_analyzable = len(registry_df)` — MUST be ≥ 200
  - `n_features_with_variance = sum(v > 0 for v in feature_vars.values())` — MUST be ≥ 3
  - `gate_passed = (n_analyzable >= 200) and (n_features_with_variance >= 3)`
- Log: `"Targeted families: {n_targeted} models; n_analyzable={n}, n_features_variance={k}/4"`

### FR-8: Visualization (REUSE with updated paths)

- Gate Metrics Comparison: bar chart (n_analyzable vs 200; n_features_with_variance vs 3)
- doc_score Distribution: histogram (compare h-e1 vs h-e1-v2)
- Feature Coverage: 4-panel bar chart
- Family Breakdown: stacked bar
- Output to: `h-e1-v2/figures/`
- **Source:** `visualization.py` (h-e1, adapted paths)

---

## 6. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| **Reproducibility** | `random_state=42` (fixed seed) |
| **Rate Limit Handling** | Exponential backoff, max 5 retries per card |
| **Checkpointing** | `cards_cache.json` — resume on interrupt |
| **API Access** | HuggingFace Hub API (validated operational in h-e1) |
| **Runtime** | Targeted ~300–600 cards: estimated 1–2 hours with checkpointing |
| **Storage** | cards_cache.json (~50–200 MB for 300–600 cards) |

---

## 7. Dependencies

### 7.1 Python Packages (All validated in h-e1)

```
datasets>=2.14.0
huggingface_hub>=0.17.0
pandas>=2.0.0
numpy>=1.24.0
statsmodels>=0.14.0
scipy>=1.11.0
matplotlib>=3.7.0
seaborn>=0.12.0
tqdm>=4.65.0
PyYAML>=6.0
```

### 7.2 Code Dependencies

| Dependency | Source | Usage |
|-----------|--------|-------|
| h-e1 codebase | `docs/youra_research/20260317_data_problems/h-e1/code/` | All modules reused (data_collection, feature_extraction, registry_builder, analysis, visualization) |
| h-e1 checkpoint | `h-e1/cards_cache.json` | Optional — can reuse or restart from scratch |

---

## 8. Success Criteria

### 8.1 Primary (MUST_WORK Gate)

| Criterion | Threshold | Expected |
|-----------|-----------|---------|
| `n_analyzable` | ≥ 200 | ~300–500 from targeted families |
| `n_features_with_variance` | ≥ 3 | 4/4 (all features show variance) |

### 8.2 Secondary (Informational)

| Criterion | Threshold |
|-----------|-----------|
| Training tokens recoverable | n ≥ 100 |
| Targeted families fraction | ≥ 60% of retrieved cards |
| OLS convergence | Baseline R² ~0.43 (as in h-e1) |
| `beta_docs` direction | > 0 |

---

## 9. Implementation Constraints

- **Single code change:** Only `main.py` modified — add `sort_model_ids_by_family()` and update call site
- **All other modules:** Copied/reused from h-e1 unchanged (data_collection.py, feature_extraction.py, registry_builder.py, analysis.py, visualization.py, config.py)
- **Output location:** `h-e1-v2/code/` (separate from h-e1 for clean isolation)
- **No neural network training** — statistical analysis only, no GPU required

---

## 10. Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Targeted families still insufficient variance | Low | LLaMA-2, Mistral, Qwen model cards known to document all 4 features |
| HF API rate limits | Medium | Checkpoint resume already implemented in h-e1 |
| LLaMA/Mistral fine-tunes don't inherit parent docs | Low | Original model families (meta-llama/, mistralai/, Qwen/) have strong docs |
| n_analyzable < 200 from targeted alone | Very Low | ~300–600 models expected; h-e1 proved n=4,488 registry exists |

---

*Generated: Phase 3 PRD Workflow (inline — BMAD bmm not installed)*
*Input: h-e1-v2/02c_experiment_brief.md*
*Hypothesis Type: EXISTENCE | Budget Tier: LIGHT (≤15 tasks)*
