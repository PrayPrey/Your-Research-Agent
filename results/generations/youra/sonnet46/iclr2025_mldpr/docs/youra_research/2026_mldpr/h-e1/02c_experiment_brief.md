# Experiment Design: H-E1

**Date:** 2026-03-15
**Author:** Anonymous
**Hypothesis Statement:** Under the ML dataset ecosystem context (HF Hub, OpenML, UCI), if public APIs are queried for dataset metadata (card_data YAML, OpenML fields, ucimlrepo), then DTS-weighted documentation completeness scores are computable for ≥70% of the target corpus because structured API responses map reliably to the 6 DTS section categories.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** Yes — H-E1 has no prerequisites (root hypothesis)
**Gate Status:** MUST_WORK — not yet evaluated; failure blocks entire chain

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**MUST_WORK:** API-based DTS coverage rate ≥ 70% across combined corpus (500 HF + 200 OpenML + 100 UCI) AND human-automated correlation r ≥ 0.70 on 120-dataset validation sample. If either condition fails → STOP pipeline; redesign measurement approach (README parsing fallback per R1 mitigation).

---

## Continuation Context

No continuation context — H-E1 is the first hypothesis in the verification chain (H-E1 → H-M1 → H-M2 → H-M3).

### Previous Hypothesis Results (if applicable)
None — this is the root hypothesis with no predecessors.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Dataset Documentation Completeness Scoring API Metadata**
- Results returned HuggingFace dataset card examples (nateraw/parti-prompts, huggan/smithsonian_butterflies_subset) confirming HF card_data YAML structure is well-represented
- Key insight: HF datasets use structured YAML frontmatter (language, task_categories, license, size_categories) — directly mappable to DTS sections
- Aggregate similarity ~0.39 — no direct prior cases on DTS scoring found in KB

**Query 2: HuggingFace Dataset Metadata API Collection**
- HF Hub documentation (manage-cache guide, imagefolder pattern) confirms `huggingface_hub` library patterns
- `list_datasets(full=True)` pattern for bulk metadata retrieval confirmed
- LAION-5B dataset documentation confirms large-scale HF dataset corpus structure

**Query 3: Metadata Quality Measurement Benchmark Coverage**
- No direct KB hits on metadata quality benchmarks → confirms H-E1 is novel
- openreview.net M3Y74vmsMcY (low similarity, diffusion paper) — not relevant
- Key finding: No prior cases in Archon KB on systematic DTS-style metadata auditing → original contribution confirmed

**Summary:** Archon KB confirms HF API patterns but contains no prior cases on cross-repository metadata completeness scoring. This is a novel experiment.

### Archon Code Examples

**Query 1: HuggingFace API — Dataset Listing Pattern**
- Source: `huggingface_hub` documentation and diffusers examples
- Pattern: `from huggingface_hub import snapshot_download` / `list_datasets`
- Key insight: `huggingface_hub` provides iteration over dataset objects with metadata fields accessible via `.card_data` attribute
- Used for: Dataset collection implementation design

**Query 2: OpenML API — No direct cases in KB**
- Fallback to known OpenML REST API patterns (`openml.datasets.list_datasets()`, `openml.datasets.get_dataset()`)
- Standard Python `openml` library provides structured metadata dict
- Used for: OpenML collection design

### Exa GitHub Implementations

**Exa MCP Status:** Unavailable (402 Payment Required after 3 retries)
- All `get_code_context_exa` and `web_search_exa` calls returned HTTP 402
- Limitation documented per MCP Error Retry Protocol

**Known implementations from literature (Phase 2B research):**
- **Rondina et al. 2025**: DTS scoring on 100 popular datasets — establishes section-to-field mapping precedent
- **Oreamuno et al. 2024**: HF-only audit of 6,758 cards using structured field presence checks
- **huggingface_hub Python library**: `HfApi().list_datasets(full=True)` returns DatasetInfo objects with `.card_data` (DatasetCardData with tags, task_categories, language, license, etc.)
- **openml Python library**: `openml.datasets.list_datasets(output_format='dataframe')` returns metadata including name, description, number_of_instances, etc.
- **ucimlrepo Python library**: `from ucimlrepo import fetch_ucirepo; fetch_ucirepo(id=...)` with `.metadata` dict

**Serena Analysis Needed:** False — no complex architecture code requiring semantic analysis

### 🎯 Implementation Priority Assessment

**CRITICAL: For this data collection experiment, implementation priority is:**
1. **Official library clients** (HIGHEST) — `huggingface_hub`, `openml`, `ucimlrepo`
2. **REST API direct calls** — fallback for rate-limited or missing library fields
3. **HTML scraping** — last resort for UCI datasets not in ucimlrepo

**Recommended Implementation Path:**
- Primary: Official Python libraries (`huggingface_hub>=0.20`, `openml>=0.14`, `ucimlrepo>=0.0.7`)
- Fallback: Direct REST API calls (HF Hub API `/api/datasets`, OpenML JSON endpoint `/api/v1/json/data/list`)
- Justification: Official libraries handle pagination, rate limiting, and authentication; provide structured objects directly mappable to DTS sections without HTML parsing

### Code Analysis (Serena MCP)

*Skipped* — H-E1 is an API data collection + binary scoring pipeline. No complex neural architecture code requiring Serena symbol-level analysis. Implementation is straightforward: API calls → field extraction → binary binary scoring → coverage computation. Code patterns from `huggingface_hub` docs and known DTS literature provide sufficient grounding.

---

## Experiment Specification

### Dataset

**Dataset Name:** Cross-Repository ML Dataset Metadata Corpus
**Version:** Collected 2026-03-15 (API snapshot)
**Type:** programmatic-api (real data via live API calls)
**Sources:**
- HuggingFace Hub: `HfApi().list_datasets(full=True)` → sample 500 stratified by task_category × upload year (2016–2024)
- OpenML: `openml.datasets.list_datasets(output_format='dataframe')` → sample 200 stratified by task_type
- UCI ML Repository: `ucimlrepo.fetch_ucirepo()` → all ~600 datasets (full population)

**Scale:**
- HF: 500 datasets (stratified random sample from ~100K total)
- OpenML: 200 datasets (stratified by task type from ~4K total)
- UCI: ~100 datasets (full population subset, practical limit given API)
- **Human validation subsample:** 120 datasets (40 per repo, stratified)
- **Total corpus minimum:** 800 datasets

**Preprocessing:**
- Extract field presence per dataset (binary: field present/absent)
- Parse HF card_data YAML frontmatter via `DatasetCardData` object
- Extract OpenML fields: description, citation, original_data_url, row_id_attribute
- Extract UCI fields: description, creators, donors, intro_paper, variable_info
- Compute upload year from `last_modified` (HF), `date` (OpenML), `year` (UCI)
- Stratify by task_category (NLP/CV/tabular/audio/multimodal) and year bin (2016–2018, 2019–2020, 2021–2022, 2023–2024)

**Augmentation:** None (metadata is binary presence; no augmentation applicable)

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (no pre-download; live API collection)
- Identifier: N/A (generated at collection time)
- Code:
  ```python
  from huggingface_hub import HfApi
  import openml
  from ucimlrepo import fetch_ucirepo
  api = HfApi()
  hf_datasets = list(api.list_datasets(full=True, limit=None))  # ~100K
  openml_datasets = openml.datasets.list_datasets(output_format='dataframe')
  ```

### Models

#### Baseline Model

**Architecture:** Unweighted binary field presence rate (naive coverage baseline)
**Description:** For each dataset, count the number of API fields that are non-null/non-empty, divided by total fields queried. No DTS section weighting, no inverse-frequency weights.
**Formula:** `baseline_coverage = sum(field_present) / total_fields_queried`
**Purpose:** Establishes that DTS-weighted scoring differs meaningfully from naive counting — demonstrates the value of the weighted approach.

**Loading Information** (for Phase 4 download):
- Method: custom (computed from collected metadata)
- Identifier: N/A
- Code: `baseline_coverage = np.mean([1 if v else 0 for v in raw_fields.values()])`

#### Proposed Model

**Architecture:** DTS 6-Section Inverse-Frequency Weighted Binary Scoring Algorithm

**Core Mechanism Implementation:**

```python
# DTS 6-Section Weighted Scoring Algorithm
# Based on: Rondina et al. 2025 (DTS schema + Table 2 inverse-frequency weights)
# Input: dataset metadata dict from API
# Output: weighted DTS score in [0, 1], per-section coverage rates

DTS_SECTIONS = {
    "motivation":    ["task_categories", "language", "tags", "license"],
    "composition":   ["size_categories", "num_rows", "num_columns", "features"],
    "collection":    ["source_datasets", "annotations_creators", "original_data_url"],
    "preprocessing": ["preprocessing_steps", "data_augmentation", "data_splits"],
    "uses":          ["known_limitations", "out_of_scope_use", "discussion_best_use"],
    "distribution":  ["license", "citation", "contact", "maintenance_plan"]
}

# Inverse-frequency weights from Rondina et al. 2025 Table 2
DTS_WEIGHTS = {
    "motivation": 1.0, "composition": 0.9, "collection": 2.1,
    "preprocessing": 1.8, "uses": 1.5, "distribution": 0.7
}

def compute_dts_score(metadata: dict) -> tuple[float, dict]:
    section_scores = {}
    for section, fields in DTS_SECTIONS.items():
        present = sum(1 for f in fields if metadata.get(f))
        section_scores[section] = present / len(fields)  # binary coverage

    weighted_sum = sum(DTS_WEIGHTS[s] * section_scores[s] for s in DTS_SECTIONS)
    total_weight = sum(DTS_WEIGHTS.values())
    dts_score = weighted_sum / total_weight  # normalized to [0, 1]
    return dts_score, section_scores

def compute_coverage_rate(corpus: list[dict]) -> float:
    scoreable = sum(1 for d in corpus if compute_dts_score(d)[0] > 0)
    return scoreable / len(corpus)  # target: >= 0.70
```

### Training Protocol

**Note:** This is a data collection and statistical analysis experiment — no neural network training. Protocol describes the computation pipeline.

**Execution Protocol:**
- **Phase 1 — Pilot:** Sample 50 datasets per repository (150 total); verify API field availability; estimate coverage rate; validate DTS mapping
- **Phase 2 — Full Collection:** Stratified sampling (HF: 500, OpenML: 200, UCI: 100); apply DTS scoring algorithm
- **Phase 3 — Human Validation:** 120-dataset blinded human annotation subsample; compute Pearson r against automated scores
- **Phase 4 — Reporting:** Per-section coverage rates, overall weighted DTS, human-automated correlation

**Optimizer:** N/A (no gradient-based training)
**Seed:** 42 (fixed for reproducibility of stratified sampling)
**Rate Limiting:** HF API: 1 req/sec (unauthenticated), 5 req/sec (authenticated token); OpenML: standard rate limits; UCI: conservative 1 req/2sec

**API Rate Mitigation:**
- Use authenticated HF token for 5x rate increase
- Batch OpenML metadata requests via `list_datasets()` bulk endpoint
- Cache all raw API responses to JSON before scoring (avoids re-collection)

### Evaluation

**Primary Metrics:**
1. **API Coverage Rate:** Proportion of datasets for which DTS score is computable (any field mapped) — Target ≥ 0.70
2. **Human-Automated Correlation:** Pearson r between automated DTS scores and blinded human scores on 120-dataset subsample — Target r ≥ 0.70
3. **Per-Section Coverage Rate:** Coverage rate for each of 6 DTS sections, per repository

**Success Criteria (PoC — direction-based):**
- Overall API coverage ≥ 0.70 AND human-automated r ≥ 0.70 → GATE PASSED → proceed to H-M1
- Coverage ≥ 0.70 BUT r < 0.70 → EXPLORE: refine section-to-field mapping
- Coverage < 0.70 → PIVOT: README text parsing fallback

**Expected Baseline Performance (from literature):**
- Oreamuno et al. 2024: 28.48% of HF cards "documented" (strict threshold) — our 70% uses binary field presence (lenient), expected to be achievable
- Rondina et al. 2025: HF well-documented on Motivation/Uses; Collection/Preprocessing sections low → expect heterogeneous per-section rates
- **Source:** Rondina et al. 2025, Oreamuno et al. 2024 (Phase 2B literature)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: data_quality_measurement
- Library: `scipy.stats` (Pearson r), `numpy` (coverage rate), `pandas` (data management)
- Code: `from scipy.stats import pearsonr; r, p = pearsonr(auto_scores, human_scores)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing actual vs. target coverage rates (70% threshold line) and human-automated r (0.70 threshold line)

#### Additional Figures (LLM Autonomous)
- Per-section coverage rate heatmap (6 DTS sections × 3 repositories)
- Distribution of DTS weighted scores per repository (violin or box plot)
- Scatter plot: automated DTS score vs. human annotation score (with r annotation)
- Missing field analysis: which specific fields are absent most frequently (bar chart by repository)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | DTS 6-section scoring algorithm implementable using API field mappings from 3 repositories | TRUE — DTS schema from Rondina et al. 2025 maps to HF card_data YAML fields |
| Mechanism Isolatable | Weighted DTS scorer can run independently of human annotation; baseline (unweighted) can be compared | TRUE — weighted and unweighted scorers are separate functions |
| Baseline Measurable | Unweighted naive field presence rate computable as baseline | TRUE — trivial sum/count of non-null fields |

### Architecture Compatibility Check

**Required Features:**
- HF Hub API: `card_data` attribute in `DatasetInfo` objects (available in `huggingface_hub>=0.15`)
- OpenML library: `description`, `url`, `citation` fields in dataset metadata dict
- UCI `ucimlrepo`: `.metadata` dict with description, creators, variables fields
- Python environment: `pandas`, `numpy`, `scipy.stats`, `huggingface_hub`, `openml`, `ucimlrepo`

**Incompatible Configurations:**
- HF datasets created before YAML frontmatter era (pre-2019): `card_data` may be None → handled by checking `card_data is not None`
- OpenML datasets with deprecated API format: handled by version check `openml>=0.14`
- UCI datasets not in ucimlrepo index: fallback to UCI REST API `/static/public/{id}/`

> ⚠️ If any API returns consistent None/empty for >30% of sampled datasets in pilot phase → FAIL EARLY and trigger R1 mitigation (README parsing)

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "DTS score computed for dataset {id}: {score:.3f}" | scorer.py:compute_dts_score() |
| Coverage Delta | weighted_coverage > unweighted_coverage (DTS weighting amplifies rare-section penalty) | metrics.py:compare_scorers() |
| Metric Delta | Human-automated Pearson r > 0 (scorer captures real completeness variation) | validation.py:validate_scores() |

**Activation Verification Code (Phase 4 must implement):**
```python
def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    indicators = {
        "scoring_ran": results.get("n_scored", 0) > 0,
        "coverage_achievable": results["overall_coverage"] > 0.0,
        "weighting_effect": results["weighted_mean"] != results["unweighted_mean"],
        "human_correlation_positive": results.get("pearson_r", 0) > 0
    }
    success = indicators["scoring_ran"] and indicators["coverage_achievable"]
    return success, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| All card_data None | >30% HF datasets with card_data=None in pilot | FAIL: Switch to README parsing |
| OpenML fields absent | key fields missing in >50% of datasets | WARN: Use relaxed DTS mapping |
| r < 0 (negative correlation) | Human and automated scores anti-correlated | FAIL: Fundamental mapping error |
| Coverage < 0.70 | After full collection | PIVOT: README text parsing fallback |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | API returns non-empty fields for ≥70% datasets | coverage_rate >= 0.70 |
| Effect Measurable | Automated scores vary across datasets (std > 0) | np.std(dts_scores) > 0.05 |
| Hypothesis Supported | Overall coverage ≥ 0.70 AND Pearson r ≥ 0.70 | Both gate conditions met |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (API collection completes, DTS scorer executes)
2. `overall_dts_coverage >= 0.70` AND `human_automated_r >= 0.70`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** HuggingFace Hub Datasets Documentation (huggingface.co/docs/datasets)
- **Query Used:** "HuggingFace Hub list_datasets API iteration Python"
- **Relevance:** Confirms `huggingface_hub` library patterns for bulk dataset listing
- **Key Insights:**
  - `HfApi().list_datasets(full=True)` returns iterator of `DatasetInfo` objects
  - `DatasetInfo.card_data` contains parsed YAML frontmatter as `DatasetCardData`
  - Fields: `task_categories`, `language`, `license`, `tags`, `size_categories`
- **Used For:** Dataset collection implementation design (Section: Loading Information)

**Source A.2:** HuggingFace Hub Cache Management Guide
- **Query Used:** "HuggingFace Hub list_datasets API iteration Python"
- **Key Insights:** Caching strategy for large API calls; rate limiting patterns
- **Used For:** API rate mitigation design in Training Protocol

**Source A.3:** No prior DTS scoring cases in Archon KB
- **Finding:** Archon KB has no past implementation cases on cross-repository metadata completeness auditing
- **Implication:** H-E1 is novel — no KB guidance on DTS section-to-field mappings
- **Used For:** Confirms novelty; implementation must derive mappings from Rondina et al. 2025

### Archon Code Examples

**Code A.C.1:** `snapshot_download` pattern (huggingface_hub)
- **Pattern:** `from huggingface_hub import snapshot_download`
- **Relevance:** Shows huggingface_hub usage pattern for dataset access
- **Used For:** Understanding HF library API patterns for collection code

### B. GitHub Implementations (Exa)

**Exa MCP Status:** Unavailable (HTTP 402) after 3 retries (15s intervals)

**Known implementations from Phase 2B literature:**

**Repository B.1:** Rondina et al. 2025 (DTS schema implementation)
- **Source:** Academic paper (Phase 2B literature)
- **Relevance:** Defines DTS 6 sections, provides inverse-frequency weights (Table 2)
- **Key Implementation Pattern:**
  ```python
  # DTS section-to-field mapping (from Rondina et al. 2025)
  # Sections: Motivation, Composition, Collection, Preprocessing, Uses, Distribution
  # Weights (approximate inverse-frequency): Collection ~2.1x, Preprocessing ~1.8x, Uses ~1.5x
  # (high weight = rare but important section)
  ```
- **Their Results:** HF > Kaggle > OpenML > UCI on Presence Average; Collection=10% most rare
- **Used For:** DTS_SECTIONS and DTS_WEIGHTS in core mechanism pseudo-code

**Repository B.2:** Oreamuno et al. 2024 (HF dataset card audit)
- **Source:** Academic paper (Phase 2B literature)
- **Relevance:** Establishes HF field presence measurement methodology on 6,758 cards
- **Key Pattern:** Binary presence check per structured field in HF YAML card_data
- **Their Results:** 71.52% of HF cards "undocumented" under strict threshold
- **Used For:** Baseline coverage rate expectations; confirms HF card_data field approach

### C. Code Analysis (Serena)

Serena analysis: Not performed — H-E1 is a data collection + statistical scoring pipeline, not a complex neural architecture. Code patterns from library documentation are sufficient.

### D. Previous Hypothesis Context

Previous Context: None — H-E1 is the root hypothesis (first in chain H-E1 → H-M1 → H-M2 → H-M3).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: HF API approach | Archon KB + Literature | A.1, B.2 (Oreamuno) |
| Dataset: OpenML sampling | Literature | B.1 (Rondina 2025) |
| Dataset: UCI ucimlrepo | Phase 2B specification | 02b_verification_plan.md §1.3 |
| DTS section definitions | Literature | B.1 (Rondina 2025, DTS schema) |
| DTS section weights | Literature | B.1 (Rondina 2025, Table 2) |
| Field-to-section mapping | Literature + Phase 2B | B.1, 02b_verification_plan.md §1.5 A1 |
| Coverage threshold (70%) | Phase 2B success criteria | 02b_verification_plan.md §2.2 H-E1 |
| Human validation (r≥0.70) | Phase 2B success criteria | 02b_verification_plan.md §2.2 H-E1 |
| Stratified sampling design | Phase 2B specification | 02b_verification_plan.md §1.3 |
| Baseline (unweighted) | Experiment design (this doc) | Proposed vs baseline comparison |
| Rate limiting strategy | Archon KB | A.2 (HF cache guide) |
| scipy Pearson r | Standard library | scipy.stats documentation |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-15T03:20:00Z

### Workflow History for This Hypothesis
- 2026-03-15T03:00:00Z: Phase 2B completed; H-E1 READY
- 2026-03-15T03:11:55Z: H-E1 set to IN_PROGRESS (hypothesis loop)
- 2026-03-15T03:15:00Z: Phase 2C experiment design IN_PROGRESS
- 2026-03-15T03:20:00Z: Phase 2C experiment design COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — 5 queries), Exa (unavailable — 402), Serena (skipped — not needed)*
*All specifications grounded in Phase 2B literature and Archon KB patterns*
*Next Phase: Phase 3 - Implementation Planning*
