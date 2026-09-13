# Product Requirements Document (PRD)

**Date:** 2026-03-18
**Hypothesis:** H-E1 - Repository Heterogeneity in Documentation Completeness
**Type:** EXISTENCE (Proof of Concept)
**Gate:** MUST_WORK (ICC ≥ 0.10 AND repository variance ≥ modality variance)

---

## Executive Summary

This PRD defines the implementation requirements for validating repository-level heterogeneity in metadata documentation completeness across large-scale cross-repository datasets. The study establishes whether repository-specific practices create measurable variance in MVR-BCS scores beyond modality-level differences.

**Deliverable:** Statistical analysis producing ICC values, variance decomposition, and bootstrap confidence intervals across N≥1000 repositories from HuggingFace, OpenML, and UCI.

---

## Problem Statement

**Context:** The MVR-BCS framework hypothesis requires empirical validation that repository-level documentation practices create measurable heterogeneity in metadata completeness scores.

**Challenge:** Without establishing repository-level variance (ICC ≥ 0.10), subsequent mechanism hypotheses lack a valid foundation for repository-specific interventions.

**Solution:** Conduct large-scale cross-repository study with stratified sampling (N≥1000), MVR-BCS scoring, and multilevel ICC modeling to quantify repository vs. modality variance.

---

## Functional Requirements

### FR-1: Large-Scale Dataset Collection System

**Priority:** P0 (Critical)

**Description:** Programmatic collection of N≥1000 datasets from three repositories with stratified sampling by modality.

**Acceptance Criteria:**
- Collect ≥400 datasets from HuggingFace Hub API
- Collect ≥400 datasets from OpenML API
- Collect ≥200 datasets from UCI ML Repository (web scraping)
- Stratification: Balance across modalities (NLP, CV, Tabular)
- Modality distribution: Track modality for all datasets
- Quality range: Include full quality spectrum (no pre-filtering)
- Published date range: 2015-2024 (sufficient historical coverage)

**Data Outputs:**
```
data/h-e1/
├── datasets_metadata.csv (≥1000 rows: dataset_id, repository, modality, mvr_bcs_score)
└── documentation/
    ├── hf/ (≥400 dataset cards)
    ├── openml/ (≥400 metadata JSONs)
    └── uci/ (≥200 HTML extracts)
```

**Dependencies:**
- HuggingFace `datasets` library
- OpenML Python API
- BeautifulSoup4 (for UCI scraping)
- Requests library
- pandas for metadata tracking

---

### FR-2: MVR-BCS Scoring Pipeline

**Priority:** P0 (Critical)

**Description:** Implement MVR-BCS (Minimal Validity Rules + Basic Completeness Score) for all collected datasets.

**Acceptance Criteria:**
- **Structural Component:**
  - Field presence detection (non-empty check)
  - Basic type validation (numeric, categorical, text)
  - Completeness percentage calculation
- **LLM Semantic Component:**
  - GPT-4 semantic validation (per-modality F1 ≥ 0.75 target)
  - Binary classification: Valid/Invalid per field
  - Cross-modality F1 range validation (≤ 0.10)
- **Composite Score:**
  - MVR-BCS = 0.6 × structural + 0.4 × semantic
  - Score range: [0, 1]
  - Per-repository score distribution tracking

**Data Outputs:**
```
data/h-e1/
├── mvr_bcs_scores.csv (≥1000 rows: dataset_id, structural_score, semantic_score, mvr_bcs, repository, modality)
└── llm_validation/
    ├── prompts/ (semantic validation prompts)
    └── responses/ (LLM classification results)
```

**Dependencies:**
- OpenAI API (GPT-4)
- Custom MVR rule engine
- Field extraction utilities

---

### FR-3: Multilevel ICC Modeling

**Priority:** P0 (Critical)

**Description:** Compute Intraclass Correlation Coefficient (ICC) with multilevel modeling to quantify repository-level variance.

**Acceptance Criteria:**
- **Model:** Mixed-effects model with repository as random effect, modality as fixed effect
- **ICC Calculation:** `ICC = σ²_repository / (σ²_repository + σ²_residual)`
- **Bootstrap CI:** 1000 iterations for 95% confidence intervals
- **Variance Decomposition:**
  - Repository variance component
  - Modality variance component
  - Residual variance component
  - Variance ratio: repository / modality

**Metrics:**
- **Primary:** ICC value with 95% CI
- **Secondary:**
  - Lower 95% CI bound (must be >0.05)
  - Variance ratio (repository / modality ≥ 1.0)
  - Per-repository mean scores
  - Per-modality mean scores

**Output Format:**
```python
{
  "icc": 0.15,
  "ci_95": (0.08, 0.22),
  "lower_ci_bound": 0.08,
  "variance_decomposition": {
    "repository": 0.12,
    "modality": 0.08,
    "residual": 0.68
  },
  "variance_ratio": 1.5,
  "gate_passed": true
}
```

**Dependencies:**
- `statsmodels` (mixed linear models)
- `scipy.stats` (bootstrap)
- `numpy` for variance calculations

---

### FR-4: LLM Semantic Classifier Validation

**Priority:** P0 (Critical)

**Description:** Validate LLM semantic classification performance per modality with F1 score tracking.

**Acceptance Criteria:**
- **Per-Modality F1:** Measure F1 score for NLP, CV, Tabular separately
- **Target:** F1 ≥ 0.75 for all modalities
- **Cross-Modality Range:** max(F1) - min(F1) ≤ 0.10
- **Validation Method:** Hold-out test set (10% of each modality)
- **Ground Truth:** Manual annotation of 100 samples per modality

**Metrics:**
- F1 score per modality
- Precision and Recall per modality
- Cross-modality F1 range
- Confusion matrices per modality

**Output Format:**
```python
{
  "nlp": {"f1": 0.78, "precision": 0.76, "recall": 0.80},
  "cv": {"f1": 0.76, "precision": 0.75, "recall": 0.77},
  "tabular": {"f1": 0.77, "precision": 0.78, "recall": 0.76},
  "cross_modality_range": 0.02,
  "all_pass_threshold": true
}
```

---

### FR-5: Gate Validation Logic

**Priority:** P0 (Critical)

**Description:** MUST_WORK gate check for hypothesis success/failure.

**Acceptance Criteria:**
- **Primary Gate:** ICC ≥ 0.10 AND lower 95% CI > 0.05 AND variance_ratio ≥ 1.0
- **Secondary Gate:** LLM F1 ≥ 0.75 for all modalities AND cross-modality range ≤ 0.10
- **Pass:** Display "✅ MUST_WORK gate PASSED"
- **Fail Modes:**
  - ICC < 0.05: "❌ ABANDON - No heterogeneity detected"
  - Modality variance ≥ 40%: "⚠️ PIVOT - Domain-specific framework needed"
  - LLM F1 fails: "⚠️ EXPLORE - Alternative semantic validators"

**Gate Logic:**
```python
primary_pass = (
    icc >= 0.10
    and ci_lower > 0.05
    and variance_ratio >= 1.0
)
secondary_pass = (
    all(f1 >= 0.75 for f1 in llm_f1_scores.values())
    and cross_modality_range <= 0.10
)
gate_passed = primary_pass and secondary_pass
```

---

### FR-6: Visualization Suite

**Priority:** P1 (Important)

**Description:** Generate 5 figures for validation report.

**Acceptance Criteria:**

**Figure 1: Gate Metrics Comparison (MANDATORY)**
- Bar chart: ICC (actual vs threshold 0.10), variance ratio (actual vs 1.0)
- Horizontal lines at thresholds (red dashed)
- Error bars: 95% confidence intervals for ICC
- Color coding: Green (pass), Red (fail)

**Figure 2: Variance Decomposition Pie Chart**
- 3 slices: Repository variance, Modality variance, Residual variance
- Percentages labeled
- Highlight repository slice if ≥ modality

**Figure 3: Repository-Level Distribution**
- Box plot: MVR-BCS scores per repository (HF, OpenML, UCI)
- Overlaid violin plot showing distribution shape
- Mean markers with error bars

**Figure 4: Modality-Level Distribution**
- Box plot: MVR-BCS scores per modality (NLP, CV, Tabular)
- Side-by-side comparison
- Statistical significance markers (ANOVA post-hoc)

**Figure 5: LLM Classifier Performance**
- Grouped bar chart: F1, Precision, Recall per modality
- Horizontal line at F1 = 0.75 threshold
- Error bars from cross-validation

**Output Path:** `h-e1/figures/` (5 PNG files)

---

## Non-Functional Requirements

### NFR-1: Reproducibility

**Requirement:** All random sampling and modeling must be seeded.

**Implementation:**
- Set random seed for stratified sampling: `random.seed(42)`
- Set random seed for bootstrap CI: `np.random.default_rng(seed=42)`
- Set random seed for train/test split: `sklearn.model_selection.train_test_split(random_state=42)`

### NFR-2: Data Quality

**Requirement:** Dataset collection quality controls.

**Implementation:**
- Validate API responses before storage
- Check for duplicate datasets across repositories
- Track collection errors and retry logic
- Minimum metadata field coverage per dataset

### NFR-3: Computational Efficiency

**Requirement:** Optimize for large-scale processing (N≥1000).

**Implementation:**
- Batch API calls (100 datasets per batch)
- Parallel LLM validation (10 concurrent requests)
- Cache intermediate results (MVR-BCS scores)
- Progress tracking with resume capability

### NFR-4: LLM Cost Management

**Requirement:** Control OpenAI API costs for N≥1000 datasets.

**Implementation:**
- Use GPT-4-turbo (cheaper than GPT-4)
- Batch prompts where possible
- Cache LLM responses to disk
- Estimate total cost before execution (≤ $50 budget)

### NFR-5: Documentation

**Requirement:** All code must include docstrings and execution guide.

**Standards:**
- Function docstrings with parameter descriptions
- Inline comments for statistical calculations
- README.md with setup, execution, and cost estimates
- Data dictionary for all output files

---

## Data & Environment Specifications

### Data Preparation Tasks

| Task | Description | Output |
|------|-------------|--------|
| **D-1** | Install dependencies (HF datasets, OpenML, BeautifulSoup, statsmodels) | `requirements.txt` |
| **D-2** | Collect HuggingFace datasets (≥400) with stratification | `data/h-e1/documentation/hf/` |
| **D-3** | Collect OpenML datasets (≥400) with stratification | `data/h-e1/documentation/openml/` |
| **D-4** | Collect UCI datasets (≥200) via web scraping | `data/h-e1/documentation/uci/` |
| **D-5** | Generate metadata CSV with repository and modality labels | `data/h-e1/datasets_metadata.csv` |
| **D-6** | Prepare LLM validation ground truth (manual annotation) | `data/h-e1/llm_validation/ground_truth.csv` |

### Environment Setup Tasks

| Task | Description | Output |
|------|-------------|--------|
| **E-1** | Create virtual environment | `venv/` |
| **E-2** | Install Python dependencies | Installed packages |
| **E-3** | Verify statsmodels/scipy versions | Version check script |
| **E-4** | Create folder structure | `data/h-e1/`, `h-e1/figures/` |
| **E-5** | Configure OpenAI API key | `.env` file with API key |

### Required Dependencies

```txt
# requirements.txt
datasets>=2.10.0
openml>=0.14.0
beautifulsoup4>=4.11.0
requests>=2.28.0
scikit-learn>=1.2.0
scipy>=1.10.0
statsmodels>=0.14.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
pandas>=1.5.0
openai>=1.0.0
python-dotenv>=1.0.0
tqdm>=4.65.0
```

---

## Success Criteria

### Primary Success Metrics

| Metric | Target | Gate Type |
|--------|--------|-----------|
| ICC | ≥ 0.10 | MUST_WORK (primary) |
| ICC lower 95% CI | > 0.05 | MUST_WORK (primary) |
| Repository/Modality variance ratio | ≥ 1.0 | MUST_WORK (primary) |
| LLM per-modality F1 | ≥ 0.75 for all | MUST_WORK (secondary) |
| LLM cross-modality F1 range | ≤ 0.10 | MUST_WORK (secondary) |

### Secondary Performance Expectations

| Metric | Target | Type |
|--------|--------|------|
| Sample size | ≥ 1000 datasets | Validity check |
| Repository balance | 40%/40%/20% (HF/OpenML/UCI) | Quality check |
| Modality balance | Within 20% of uniform | Quality check |
| Bootstrap CI width | < 0.15 | Precision check |

### Failure Modes & Actions

| Failure Condition | Action |
|-------------------|--------|
| ICC < 0.05 (no heterogeneity) | ABANDON hypothesis - no repository effect exists |
| Modality variance > 40% total | PIVOT to domain-specific framework |
| LLM F1 < 0.75 for any modality | EXPLORE alternative semantic validators (RoBERTa fine-tuned) |
| Variance ratio < 1.0 | PIVOT to modality-focused framework |

---

## Dependencies & Constraints

### External Dependencies

| Dependency | Purpose | Criticality |
|------------|---------|-------------|
| HuggingFace Hub API | Dataset collection | Critical - no alternative |
| OpenML API | Dataset collection | Critical - no alternative |
| UCI Repository | Dataset collection | Important - manual fallback possible |
| OpenAI API (GPT-4) | Semantic validation | Critical - alternative: fine-tuned RoBERTa |

### Resource Constraints

| Resource | Limit | Mitigation |
|----------|-------|------------|
| OpenAI API cost | ≤ $50 | Batch requests, cache responses, use GPT-4-turbo |
| Computation time | ≤ 8 hours | Parallel processing, progress checkpoints |
| Storage | ≤ 5 GB | Compress documentation files, store only metadata |
| GPU | Not required | CPU-only implementation (statistical analysis) |

### Technical Constraints

- Python 3.9+ required (for statsmodels compatibility)
- Minimum 8 GB RAM (for multilevel modeling with N≥1000)
- Internet connection required (API calls)
- OpenAI API key required

---

## Implementation Scope

### In Scope

- Large-scale dataset collection (N≥1000)
- MVR-BCS scoring pipeline (structural + LLM semantic)
- Multilevel ICC modeling with variance decomposition
- LLM semantic classifier validation
- Gate validation logic
- Visualization suite (5 figures)
- Validation report generation

### Out of Scope

- Manual dataset curation (automated collection only)
- Custom LLM fine-tuning (use GPT-4 API)
- Longitudinal analysis (single time-point study)
- Cross-repository dataset deduplication (track but don't merge)
- Causal intervention (observational study only)

### Future Extensions (Post-H-E1)

- H-M hypotheses: Mechanism validation through predictions P2-P5
- Causal mediation analysis (P3)
- Intervention simulation (P5)
- Baseline method comparison (Phase 5)

---

## Validation & Testing

### Unit Testing

- MVR-BCS scoring logic (structural + semantic components)
- ICC calculation with synthetic data
- Variance decomposition math
- Gate validation logic

### Integration Testing

- End-to-end pipeline: Collection → Scoring → Modeling → Validation
- API error handling and retry logic
- Progress checkpoint save/resume functionality

### Statistical Validation

- Bootstrap convergence check (1000 iterations sufficient)
- Mixed model diagnostics (residual normality, homoscedasticity)
- LLM classifier cross-validation (5-fold)

---

## Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| API rate limits (HF, OpenML, OpenAI) | High | Medium | Implement exponential backoff, cache responses |
| LLM semantic validation cost overrun | Medium | Medium | Pre-estimate cost, use cheaper model (GPT-4-turbo), batch requests |
| Insufficient repository variance (ICC < 0.10) | High | Low | If fails, ABANDON per gate logic |
| Modality dominates variance (ratio < 1.0) | High | Low | If fails, PIVOT to modality-focused framework |
| Sample size < 1000 due to collection failures | Medium | Low | Over-collect by 20% margin |

---

## Timeline & Milestones

**Note:** No specific time estimates per workflow guidelines. Milestones for tracking progress only.

| Milestone | Deliverable |
|-----------|-------------|
| M1 | Data collection complete (≥1000 datasets) |
| M2 | MVR-BCS scoring complete (all datasets scored) |
| M3 | LLM validation complete (F1 scores computed) |
| M4 | ICC modeling complete (variance decomposition) |
| M5 | Gate validation complete (pass/fail decision) |
| M6 | Visualization suite complete (5 figures) |
| M7 | Validation report complete (04_validation.md) |

---

## References

### Phase 2C Source
- File: `02c_experiment_brief.md`
- Sections: Dataset, Models, Evaluation, Workflow Status

### Prior Work
- Gim et al. (2025): Qualitative FAIR assessment (small sample baseline)
- Marandi et al. (2025): DAIMS checklist (medical domain baseline)
- Roman et al. (2023): 2-tier lifecycle taxonomy (taxonomy reference)

### Statistical Methods
- Shrout & Fleiss (1979): ICC for reliability studies
- Snijders & Bosker (2011): Multilevel modeling
- Efron & Tibshirani (1993): Bootstrap confidence intervals

---

*Generated for Phase 3 Implementation Planning*
*Hypothesis: H-E1 | Type: EXISTENCE | Gate: MUST_WORK*
