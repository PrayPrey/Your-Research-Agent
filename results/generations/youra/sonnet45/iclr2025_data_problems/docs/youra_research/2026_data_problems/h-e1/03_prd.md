# Product Requirements Document: H-E1 — LLM Documentation-Benchmark Registry Construction

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (MUST_WORK gate)
**Date:** 2026-03-17
**Phase:** 3 — Implementation Planning
**Source:** 02c_experiment_brief.md
**Status:** Draft

---

## Executive Summary

H-E1 is a **foundational data assembly hypothesis** that validates whether a statistically sufficient LLM Documentation-Benchmark Registry can be constructed from publicly available sources. The registry combines Open LLM Leaderboard v1 benchmark scores with binary curation documentation features extracted from HuggingFace model cards.

**Gate Condition (MUST_WORK):** If n_analyzable < 200 or doc_score variance is trivial in <3 of 4 features, the entire pipeline halts — downstream hypotheses H-M1, H-M2, H-M3 cannot proceed without this registry.

**Deliverable:** A validated `registry.csv` (≥200 rows) with benchmark scores and 4 binary curation features, plus analysis confirming non-trivial variance.

---

## Problem Statement

### Background

Research on LLM training data quality (Subramanyam et al., 2025 L(N,D,Q) framework) posits that documented curation practices proxy for higher effective data quality Q. Testing this hypothesis requires an observational dataset linking:
1. Model-level benchmark performance (MMLU, ARC-Challenge, HellaSwag, WinoGrande, TruthfulQA, GSM8K)
2. Binary indicators of curation documentation from model cards

No such pre-assembled registry exists publicly. H-E1 creates it.

### Core Question

> Can a registry of ≥200 open-weight LLMs with complete curation documentation features and benchmark scores be assembled from the Open LLM Leaderboard v1 and HuggingFace Hub?

### Success Criterion (Binary)

| Criterion | Threshold | Gate |
|-----------|-----------|------|
| n_analyzable (models with complete feature set) | ≥ 200 | MUST_WORK PASS |
| doc_score variance non-trivial | ≥ 3/4 features with variance > 0 | MUST_WORK PASS |

---

## Scope

### In Scope

- Downloading Open LLM Leaderboard v1 snapshot via HuggingFace `datasets` library
- Filtering by benchmark completeness (≥4/6 scores non-missing)
- Retrieving HuggingFace model cards via `huggingface_hub` API
- Extracting 4 binary curation features via keyword regex
- Filtering by recoverable parameter count
- Fitting baseline OLS and proposed OLS (doc_score added) for preliminary signal check
- Generating `registry.csv` and summary statistics
- Producing visualizations: doc_score histogram, feature coverage, dropout funnel

### Out of Scope

- Training or fine-tuning any neural network
- Acquiring proprietary datasets
- Testing causal claims (H-M1/M2/M3 scope)
- Full regression analysis (H-M2/M3 scope)

---

## Functional Requirements

### FR-1: Leaderboard Data Acquisition

**Priority:** Critical
**Description:** Download and process the Open LLM Leaderboard v1 snapshot.

**Acceptance Criteria:**
- `datasets.load_dataset("open-llm-leaderboard/results", split="train")` succeeds
- Benchmark columns extracted: `mmlu`, `arc_challenge`, `hellaswag`, `winogrande`, `truthfulqa`, `gsm8k`
- Deduplication by model_name (keep latest evaluation per model)
- Expected raw count: 3,000–5,000 entries

**Implementation Notes:**
```python
from datasets import load_dataset
leaderboard = load_dataset("open-llm-leaderboard/results", split="train")
```

---

### FR-2: Benchmark Completeness Filter

**Priority:** Critical
**Description:** Retain only models with ≥4/6 benchmark scores non-missing.

**Acceptance Criteria:**
- Models with < 4 non-null benchmark scores are excluded
- Expected post-filter count: ~1,000–2,000
- Filter applied before model card retrieval (efficiency)

---

### FR-3: Model Card Retrieval

**Priority:** Critical
**Description:** Retrieve HuggingFace model cards for benchmark-eligible models.

**Acceptance Criteria:**
- `ModelCard.load(model_id)` called for each eligible model
- Rate limiting handled with exponential backoff (max 5 retries, base 2s delay)
- `HfApi().model_info(model_id)` called for parameter count
- Models with inaccessible cards excluded (logged but not fatal)
- Expected accessible fraction: 40–70% of filtered models

**Implementation Notes:**
```python
from huggingface_hub import HfApi, ModelCard
api = HfApi()
try:
    card = ModelCard.load(model_id)
    model_info = api.model_info(model_id)
except Exception:
    continue  # inaccessible
```

---

### FR-4: Curation Feature Extraction

**Priority:** Critical
**Description:** Extract 4 binary curation documentation features from model card text using pre-registered keyword patterns.

**Acceptance Criteria:**
- All 4 features extracted for each accessible model:

| Feature | Regex Pattern | Expected Coverage |
|---------|---------------|-------------------|
| `dedup_documented` | `dedup\|near.?dup\|minhash\|exact.?dedup` | 30–60% |
| `perplexity_filter_documented` | `perplexity.{0,20}filter\|ppl.{0,10}filter` | 20–50% |
| `domain_composition_documented` | `domain.{0,30}(%\|percent\|composition)\|data.{0,30}mix` | 40–70% |
| `decontamination_documented` | `decontaminat\|n.?gram.{0,20}overlap\|benchmark.{0,20}holdout` | 10–40% |

- `doc_score` = sum of 4 binary features (range 0–4)
- Keyword patterns are case-insensitive
- Regex applied to `card.content.lower()`

---

### FR-5: Parameter Count Recovery

**Priority:** Critical
**Description:** Recover parameter count N for each model.

**Acceptance Criteria:**
- Primary source: `model_info.safetensors.total` (parameter count)
- Fallback 1: Parse parameter count from model card text (e.g., "7B", "13B")
- Fallback 2: Map model name to known parameter counts (LLaMA-7B → 7e9)
- Models without recoverable N excluded
- `log_params = log(N)` computed for all retained models

---

### FR-6: Training Token Recovery (Optional)

**Priority:** Medium
**Description:** Recover training token count D where available.

**Acceptance Criteria:**
- Extracted from model card text where documented
- `log_tokens = log(D)` computed where available
- Missing D does not exclude model (covariate available for subset analysis)
- Target: ≥100 models with D recoverable

---

### FR-7: Registry Assembly and Export

**Priority:** Critical
**Description:** Assemble filtered records into validated registry DataFrame and export to CSV.

**Acceptance Criteria:**
- `registry.csv` saved to `h-e1/data/registry.csv`
- Columns: `model_id`, `mmlu`, `arc_challenge`, `hellaswag`, `winogrande`, `truthfulqa`, `gsm8k`, `dedup_documented`, `perplexity_filter_documented`, `domain_composition_documented`, `decontamination_documented`, `doc_score`, `n_params`, `log_params`, `log_tokens` (nullable), `arch_family`
- `n_analyzable = len(registry_df) ≥ 200` (primary gate)
- `assert len(registry_df) >= 200, f"Registry too small: {len(registry_df)}"` passes

---

### FR-8: Architecture Family Assignment

**Priority:** High
**Description:** Assign architecture family fixed effect to each model.

**Acceptance Criteria:**
- `arch_family` derived from model_id prefix (LLaMA, Falcon, Mistral, Pythia, OLMo, Other)
- Mapping rules applied via regex on model_id
- No model left without arch_family assignment

---

### FR-9: Descriptive Statistics and Variance Check

**Priority:** Critical
**Description:** Compute and report registry summary statistics including doc_score distribution and variance check.

**Acceptance Criteria:**
- `doc_score_variance = registry_df["doc_score"].var()` reported
- Per-feature variance computed: `{feature: registry_df[feature].var() for feature in FEATURE_COLS}`
- `n_features_with_variance = sum(v > 0 for v in feature_vars.values()) ≥ 3` (secondary gate)
- Distribution table: fraction of models at doc_score 0, 1, 2, 3, 4
- No single level > 90% of models (non-trivial variance)

---

### FR-10: Baseline and Proposed OLS Fit

**Priority:** High
**Description:** Fit OLS models for preliminary signal check.

**Acceptance Criteria:**
- Baseline OLS: `mmlu_score ~ log_params + log_tokens + C(arch_family)` (statsmodels)
- Proposed OLS: `mmlu_score ~ log_params + log_tokens + doc_score + C(arch_family)`
- Report: baseline R², proposed R², ΔR², β_docs, p-value for β_docs
- Direction check: `beta_docs > 0` noted (not required for gate pass)
- ARC-Challenge secondary: same models, same specification

---

### FR-11: Dropout Funnel Logging

**Priority:** Medium
**Description:** Log and report step-by-step filtering counts.

**Acceptance Criteria:**
- Counts logged at each filter step:
  1. Raw leaderboard entries
  2. After deduplication
  3. After ≥4/6 benchmark filter
  4. After model card accessibility filter
  5. After parameter count filter (= n_analyzable)
- Waterfall/funnel chart exported to `h-e1/figures/dropout_funnel.png`

---

### FR-12: Visualizations

**Priority:** Medium
**Description:** Generate required and recommended visualizations.

**Acceptance Criteria:**

| Figure | Filename | Priority |
|--------|----------|----------|
| doc_score distribution histogram | `doc_score_distribution.png` | REQUIRED |
| Dropout funnel waterfall | `dropout_funnel.png` | REQUIRED |
| Feature coverage bar chart (4-panel) | `feature_coverage.png` | Recommended |
| Model family doc_score breakdown | `family_breakdown.png` | Recommended |
| Benchmark availability heatmap | `benchmark_heatmap.png` | Recommended |

- All figures saved to `h-e1/figures/`
- matplotlib used (no external dependencies)

---

## Non-Functional Requirements

### NFR-1: Runtime Performance

- Total pipeline runtime ≤ 4 hours (network-bound by HF API calls)
- Checkpoint intermediate results after every 100 model card retrievals
- Resume capability: skip already-processed models on restart

### NFR-2: Rate Limit Compliance

- HuggingFace Hub API: exponential backoff (base 2s, max 5 retries)
- `requests.exceptions.HTTPError` with 429/503 handled
- No more than 1 concurrent API request

### NFR-3: Reproducibility

- All random seeds fixed: `random_state=42`
- Keyword regex patterns pre-registered in `config.py` (not modified post-run)
- `registry.csv` deterministic given identical leaderboard snapshot

### NFR-4: Infrastructure Level

- **Tier: LIGHT (minimal)** — EXISTENCE hypothesis
- Configuration: hardcoded constants in `config.py` (no YAML config needed)
- Logging: `print()` statements + CSV row-level log
- Testing: smoke test only (imports, API connectivity check)

### NFR-5: Dependencies

```
python>=3.9
datasets>=2.14.0
huggingface_hub>=0.21.0
pandas>=2.0.0
statsmodels>=0.14.0
scipy>=1.11.0
matplotlib>=3.7.0
tqdm>=4.65.0
```

---

## Success Criteria

### Primary Gate (MUST_WORK)

| Metric | Threshold | Status |
|--------|-----------|--------|
| `n_analyzable` | ≥ 200 | Not yet evaluated |
| `n_features_with_variance` | ≥ 3 of 4 features | Not yet evaluated |

### Secondary Criteria

| Metric | Threshold | Notes |
|--------|-----------|-------|
| `n_with_log_tokens` | ≥ 100 | For H-M2/M3 analysis |
| `doc_score` no single level > 90% | True | Non-trivial variance |
| Baseline OLS R² | ~0.60–0.75 | Expected per Phase 2B |
| `beta_docs > 0` | Direction check | Preliminary signal |

### Failure Conditions

| Condition | Action |
|-----------|--------|
| `n_analyzable < 200` | Trigger fallback: combine v1+v2 leaderboard snapshots |
| All 4 features uniformly 0 | Review keyword patterns; log distribution |
| HF API completely unavailable | Cache partial results; retry after 24h |

---

## Data Specifications

### Input Data

| Source | Identifier | Access Method |
|--------|------------|---------------|
| Open LLM Leaderboard v1 | `open-llm-leaderboard/results` | `datasets.load_dataset()` |
| HuggingFace Model Cards | model_id (from leaderboard) | `ModelCard.load(model_id)` |
| Model metadata | model_id | `HfApi().model_info(model_id)` |

### Output Data

| File | Location | Description |
|------|----------|-------------|
| `registry.csv` | `h-e1/data/registry.csv` | Primary output: n_analyzable rows × features |
| `summary_stats.json` | `h-e1/data/summary_stats.json` | n_analyzable, variance checks, OLS results |
| `dropout_log.csv` | `h-e1/data/dropout_log.csv` | Per-model filtering decisions |
| Figures (5) | `h-e1/figures/` | Visualizations |

---

## Architecture Overview

```
main.py
├── data_collection.py      # FR-1, FR-2, FR-3: Leaderboard download + model card retrieval
├── feature_extraction.py   # FR-4, FR-5, FR-6, FR-8: Feature extraction + parameter recovery
├── registry_builder.py     # FR-7: Assembly + export
├── analysis.py             # FR-9, FR-10: Statistics + OLS
├── visualization.py        # FR-12: Figures
├── config.py               # Constants, regex patterns, thresholds
└── utils.py                # Rate limiting, checkpointing, logging
```

---

## Dependencies on Other Hypotheses

| Dependency | Direction | Type |
|------------|-----------|------|
| H-E1 ← None | Input | FOUNDATION (no prerequisites) |
| H-E1 → H-M1 | Output | `registry.csv` as primary input |
| H-E1 → H-M2 | Output | `registry.csv` as primary input |
| H-E1 → H-M3 | Output | `registry.csv` as primary input |

---

## stepsCompleted

```yaml
stepsCompleted:
  - "Executive Summary"
  - "Problem Statement"
  - "Scope"
  - "Functional Requirements (FR-1 through FR-12)"
  - "Non-Functional Requirements"
  - "Success Criteria"
  - "Data Specifications"
  - "Architecture Overview"
```

---

*Generated by Phase 3 Implementation Planning*
*Source: 02c_experiment_brief.md*
*Date: 2026-03-17*
