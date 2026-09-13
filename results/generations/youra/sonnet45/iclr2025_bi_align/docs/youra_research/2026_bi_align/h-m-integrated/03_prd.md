---
name: Product Requirements Document
type: prd
hypothesis_id: h-m-integrated
hypothesis_type: MECHANISM
created_at: 2026-03-17
version: 1.0
stepsCompleted: ['requirements', 'data_spec', 'metrics', 'dependencies']
---

# Product Requirements Document: H-M-Integrated Linguistic Mechanism Validation

**Hypothesis:** Under HH-RLHF evaluation conditions, if linguistic agency markers are extracted from 161K chosen-rejected response pairs, then chosen responses will exhibit systematically lower marker frequencies (modal verbs, hedging, alternatives) with small-to-medium effect (Cohen's d ≥ 0.15, p < 0.05, chosen < rejected), internal consistency across markers (Cronbach's α > 0.7), and cross-dataset replication (2/3 splits), because the 4-step causal chain (RLHF optimization → efficiency preference → directness priority → reduced markers) operates as theorized.

**Gate Type:** MUST_WORK
**Prerequisites:** h-e1 (COMPLETED with PASS)

---

## Executive Summary

This PRD defines requirements for implementing a paired linguistic marker comparison system to validate the full causal mechanism linking RLHF optimization to reduced agency-preserving language. Building on h-e1's validated extraction pipeline (100% precision, CV=0.781), the system will perform within-pair statistical comparisons of linguistic markers between chosen and rejected responses across 161K HH-RLHF preference pairs.

**Success Criteria:** Cohen's d ≥ 0.15, p < 0.05 (chosen < rejected) AND Cronbach's α > 0.7 AND 2/3 splits pass primary criteria

**Key Innovation:** First computational operationalization of Human→AI alignment dimension via linguistic proxies with rigorous statistical validation.

---

## Problem Statement

Current RLHF evaluation lacks metrics for human-side effects (agency preservation, critical thinking capacity). While h-e1 established that linguistic markers can be reliably extracted, we must now test whether these markers systematically differ between RLHF-preferred (chosen) and rejected responses, validating the theorized causal mechanism:

**4-Step Causal Chain:**
1. RLHF optimization → reward maximization
2. Reward maximization → efficiency preference
3. Efficiency preference → directness priority
4. Directness priority → reduced agency-preserving markers

**This is a statistical mechanism validation study using paired linguistic analysis, NOT a model training experiment.**

---

## Functional Requirements

### FR1: Reuse H-E1 Validated Extraction Pipeline

**Priority:** P0 (Critical)

**Description:** Import and integrate the h-e1 validated linguistic marker extraction pipeline (proven: 100% precision, CV=0.781).

**Acceptance Criteria:**
- Load h-e1 extraction module from `h-e1/code/extractor.py`
- Verify extraction methods: modal verbs (spaCy MD), hedging (15-word lexicon), alternatives (5 regex patterns)
- Confirm per-100-words normalization
- Validate against h-e1 baseline metrics (modal CV=0.781)

**Dependencies:**
- h-e1 code artifacts (validated)
- spaCy v3+ with `en_core_web_sm` model
- NLTK with punkt tokenizer

**Reuse Rationale:** Enables controlled comparison (same measurement tools), eliminates extraction as confounding variable, faster implementation.

---

### FR2: Paired Data Preparation

**Priority:** P0 (Critical)

**Description:** Load HH-RLHF dataset and organize as matched chosen-rejected response pairs for within-pair comparison.

**Acceptance Criteria:**
- Load all 3 splits: helpful-base, helpful-online, helpful-rejection-sampled
- Create paired structure: [(chosen_1, rejected_1), (chosen_2, rejected_2), ...]
- Maintain pair correspondence for matched-pair t-test design
- Verify pair count: ~161K matched pairs total

**Data Specification:**
```python
from datasets import load_dataset

# Load splits
dataset_base = load_dataset("Anthropic/hh-rlhf", split="train")  # ~88K pairs
dataset_online = load_dataset("Anthropic/hh-rlhf", split="test")  # ~43K pairs
dataset_rs = load_dataset("Anthropic/hh-rlhf",
                          data_files="helpful-rejection-sampled/train.jsonl")  # ~30K pairs

# Paired structure
pairs = []
for sample in dataset:
    pairs.append((sample['chosen'], sample['rejected']))
```

**Statistical Design:** Matched-pair design controls for conversation context, response length, topic - isolates preference effect.

---

### FR3: Feature Extraction for Paired Responses

**Priority:** P0 (Critical)

**Description:** Extract linguistic markers from both chosen and rejected responses in each pair using h-e1 validated methods.

**Acceptance Criteria:**
- Extract markers for ALL responses (both chosen and rejected) in all pairs
- Store as parallel arrays: `chosen_features[N, 3]`, `rejected_features[N, 3]`
- Features: [modal_verbs_per_100, hedging_per_100, alternatives_per_100]
- Handle batch processing (1000 pairs per batch) to avoid memory issues
- Estimated runtime: ~2-3 hours for 161K pairs (based on h-e1: 10K in ~30 min)

**Implementation Specification:**
```python
from h_e1.code.extractor import LinguisticMarkerExtractor

extractor = LinguisticMarkerExtractor(nlp_model=spacy.load("en_core_web_sm"))

chosen_features = []
rejected_features = []

for chosen_text, rejected_text in pairs:
    # Extract markers (per 100 words) - validated h-e1 pipeline
    chosen_feat = extractor.extract(chosen_text)  # [modal, hedge, alt]
    rejected_feat = extractor.extract(rejected_text)

    chosen_features.append(chosen_feat)
    rejected_features.append(rejected_feat)

chosen_features = np.array(chosen_features)  # Shape: (N, 3)
rejected_features = np.array(rejected_features)  # Shape: (N, 3)
```

**Dependencies:**
- h-e1 extractor module
- NumPy for array operations
- Multiprocessing for parallelization (4-8 cores)

---

### FR4: Paired T-Test and Effect Size Calculation

**Priority:** P0 (Critical) - Primary Gate Criterion

**Description:** Conduct paired t-test on modal verb frequency (primary DV) and calculate Cohen's d effect size for paired samples.

**Acceptance Criteria:**
- Paired t-test: H0: mean(chosen - rejected) = 0
- P-value < 0.05 (statistically significant)
- Cohen's d ≥ 0.15 (small-to-medium effect)
- Direction: d < 0 (chosen < rejected, indicating reduced markers)

**Implementation Specification:**
```python
from scipy.stats import ttest_rel
import numpy as np

# Paired t-test on modal verbs (primary DV)
t_stat, p_value = ttest_rel(chosen_features[:, 0], rejected_features[:, 0])

# Cohen's d for paired samples
differences = chosen_features[:, 0] - rejected_features[:, 0]
cohens_d = np.mean(differences) / np.std(differences, ddof=1)

# Gate check
primary_pass = (abs(cohens_d) >= 0.15) and (p_value < 0.05) and (cohens_d < 0)
```

**Statistical Interpretation:**
- Cohen's d = -0.15: Chosen responses have 0.15 SD fewer modal verbs than rejected
- Negative d confirms directional hypothesis (chosen < rejected)
- Paired design controls for conversation context

**Dependencies:**
- scipy v1.7+ for statistical tests
- NumPy v1.21+ for numerical operations

---

### FR5: Cronbach's Alpha Internal Consistency

**Priority:** P1 (Secondary Gate Criterion)

**Description:** Calculate Cronbach's alpha to assess internal consistency across three marker types as construct validation.

**Acceptance Criteria:**
- Cronbach's α > 0.7 (adequate internal consistency)
- Validates that three markers measure unified construct (agency preservation)
- Compute on difference scores (chosen - rejected) for each marker

**Implementation Specification:**
```python
def cronbachs_alpha(item_scores):
    """
    Args:
        item_scores: (N, k) array - N samples, k items (3 markers)
    Returns:
        alpha: Cronbach's alpha coefficient
    """
    k = item_scores.shape[1]  # Number of items (3 markers)
    item_variances = np.var(item_scores, axis=0, ddof=1)
    total_variance = np.var(np.sum(item_scores, axis=1), ddof=1)

    alpha = (k / (k - 1)) * (1 - np.sum(item_variances) / total_variance)
    return alpha

# Compute on difference scores
difference_matrix = chosen_features - rejected_features  # (N, 3)
alpha = cronbachs_alpha(difference_matrix)

# Gate check
secondary_pass = (alpha > 0.7)
```

**Alternative:** Use `pingouin.cronbach_alpha()` if available

**Dependencies:**
- NumPy for calculations
- Optional: pingouin library for validation

---

### FR6: Cross-Split Replication Analysis

**Priority:** P1 (Tertiary Gate Criterion)

**Description:** Repeat primary analysis (paired t-test + Cohen's d) separately for each of the three HH-RLHF splits to validate generalizability.

**Acceptance Criteria:**
- Analyze separately: helpful-base, helpful-online, helpful-rejection-sampled
- Calculate Cohen's d and p-value for each split
- At least 2 of 3 splits must pass primary criteria (d ≥ 0.15, p < 0.05, d < 0)
- Document which splits pass/fail

**Implementation Specification:**
```python
splits = ['helpful-base', 'helpful-online', 'helpful-RS']
results = {}

for split_name, split_pairs in zip(splits, [pairs_base, pairs_online, pairs_rs]):
    # Extract features for this split
    chosen_split, rejected_split = extract_features(split_pairs)

    # Paired t-test
    t_stat, p_value = ttest_rel(chosen_split[:, 0], rejected_split[:, 0])

    # Cohen's d
    differences = chosen_split[:, 0] - rejected_split[:, 0]
    cohens_d = np.mean(differences) / np.std(differences, ddof=1)

    # Check pass/fail
    passed = (abs(cohens_d) >= 0.15) and (p_value < 0.05) and (cohens_d < 0)
    results[split_name] = {'d': cohens_d, 'p': p_value, 'pass': passed}

# Gate check
tertiary_pass = sum([r['pass'] for r in results.values()]) >= 2
```

**Purpose:** Validates that mechanism operates consistently across different RLHF training conditions (base, online, rejection-sampled).

---

### FR7: Visualization Generation

**Priority:** P2 (Required for validation report)

**Description:** Generate publication-quality visualizations to communicate statistical findings.

**Required Figures:**

1. **Gate Metrics Comparison** (Mandatory)
   - Bar chart: Target vs actual for Cohen's d (0.15), Cronbach's α (0.7), p-value significance
   - Saved as: `figures/gate_metrics.png`

2. **Forest Plot** - Effect sizes by split
   - X-axis: Cohen's d with 95% CI
   - Y-axis: Three splits
   - Purpose: Cross-validation replication (P3)
   - Saved as: `figures/forest_plot.png`

3. **Density Plots** - Marker distributions
   - Overlaid distributions: chosen (blue) vs rejected (red)
   - Separate panels for each marker type
   - Saved as: `figures/density_plots.png`

4. **Paired Difference Histogram**
   - Histogram of (chosen - rejected) differences
   - Vertical line at 0, shaded negative region
   - Saved as: `figures/paired_differences.png`

5. **Correlation Heatmap** - Internal consistency
   - 3x3 correlations between markers
   - Purpose: Visual validation of Cronbach's α
   - Saved as: `figures/marker_correlations.png`

**Dependencies:**
- matplotlib v3.5+ for plotting
- seaborn v0.11+ for statistical visualizations

---

## Non-Functional Requirements

### NFR1: Computational Efficiency

**Requirement:** Process 161K preference pairs (322K responses) within reasonable time frame.

**Specifications:**
- Batch processing: 1000 pairs per batch
- Parallelization: Use multiprocessing (4-8 cores) for extraction
- Memory management: Stream processing to avoid OOM errors
- Expected runtime: 2-3 hours on standard workstation

### NFR2: Reproducibility

**Requirement:** All statistical results must be exactly reproducible.

**Specifications:**
- Fixed random seed: 42 (for any random sampling)
- Version pinning: spaCy v3+, scipy v1.7+, numpy v1.21+
- Data provenance: Record HuggingFace dataset version/commit hash
- Code versioning: Git commit hash in validation report

### NFR3: Statistical Rigor

**Requirement:** Follow best practices for paired statistical testing.

**Specifications:**
- Use paired t-test (not independent samples)
- Report exact p-values (not just p < 0.05)
- Calculate 95% confidence intervals for effect sizes
- Check assumptions: normality of differences (Shapiro-Wilk if needed)

---

## Success Criteria

### Primary (P1) - MUST_WORK Gate

**Criterion:** Modal verb frequency chosen < rejected, p < 0.05, Cohen's d ≥ 0.15

**Measurement:**
- Statistical test: Paired t-test
- Effect size: Cohen's d for paired samples
- Direction: Negative d (chosen < rejected)

**Pass Condition:** ALL three conditions met

### Secondary (P2)

**Criterion:** Internal consistency Cronbach's α > 0.7

**Measurement:** Cronbach's alpha on difference scores across 3 markers

**Pass Condition:** α > 0.7 (adequate internal consistency)

**Interpretation:** Three markers converge on unified construct (agency preservation)

### Tertiary (P3)

**Criterion:** Replication in at least 2 of 3 splits (p < 0.05, d ≥ 0.15)

**Measurement:** Separate paired t-test + Cohen's d for each split

**Pass Condition:** ≥2 splits show d ≥ 0.15, p < 0.05, d < 0

**Purpose:** Validates generalizability across RLHF training conditions

---

## Dependencies and Risks

### Technical Dependencies

| Dependency | Purpose | Risk Level | Mitigation |
|------------|---------|------------|------------|
| h-e1 extraction code | Marker extraction | LOW | Already validated (100% precision) |
| HH-RLHF dataset | Preference pairs | LOW | Standard dataset, widely available |
| scipy.stats | Statistical tests | LOW | Standard library, well-documented |
| Computational resources | 161K pairs processing | MEDIUM | Batch processing, parallelization |

### Prerequisite Dependencies

**h-e1 Validation Results** (COMPLETED with PASS):
- Modal verb CV: 0.781 > 0.3 ✓
- Extraction precision: 100% > 90% ✓
- Cross-split consistency validated ✓

**Implications:**
- Extraction pipeline ready to use
- Modal verbs confirmed as primary marker (highest variance)
- Alternative-framing has low median (0.0) - may have limited utility

### Risk Analysis

**Risk 1: Effect size too small (d < 0.15)**
- Probability: MEDIUM
- Impact: MUST_WORK gate failure
- Mitigation: None (this is the empirical test)
- Consequence: PIVOT to alternative proxies OR ABANDON computational approach

**Risk 2: Low internal consistency (α < 0.7)**
- Probability: LOW
- Impact: Secondary criterion failure, proceed with limitations
- Mitigation: Focus on modal verbs (primary DV) for downstream analyses
- Consequence: Document limitation, reduce reliance on multi-marker construct

**Risk 3: Failed replication across splits**
- Probability: MEDIUM
- Impact: Tertiary criterion failure, limited generalizability
- Mitigation: Investigate split-specific characteristics
- Consequence: Scope findings to specific RLHF training condition(s)

---

## Expected Baseline Performance

From h-e1 validation (provides context for expected differences):

| Marker Type | Mean per 100 words | CV | Interpretation |
|-------------|-------------------|-----|----------------|
| Modal verbs | 2.9 | 0.781 | High frequency, sufficient variance |
| Hedging markers | 0.6 | 1.426 | Lower frequency, high variance |
| Alternatives | 0.2 | 2.576 | Very low frequency, extreme variance |

**Expected Effect:** If mechanism operates as theorized, chosen responses should show ~0.4-0.5 fewer modal verbs per 100 words compared to rejected responses (0.15 SD difference).

---

## Validation Deliverables

1. **Code Artifacts:**
   - `code/data_loader.py` - HH-RLHF paired data loading
   - `code/comparator.py` - Paired statistical comparison
   - `code/analyzer.py` - Cronbach's alpha, cross-split analysis
   - `code/visualizer.py` - Figure generation
   - `code/main.py` - Orchestration script

2. **Output Files:**
   - `results/statistics.json` - All statistical results
   - `figures/*.png` - 5 required visualizations
   - `04_validation.md` - Validation report with gate assessment

3. **Validation Report Sections:**
   - Statistical Results (primary, secondary, tertiary criteria)
   - Gate Assessment (PASS/FAIL with evidence)
   - Visualizations (embedded figures)
   - Reproducibility (environment, versions, seed)
   - Limitations and Future Work

---

## Traceability to Phase 2C

| PRD Section | Phase 2C Source | Verification |
|-------------|-----------------|--------------|
| FR1-3 | Dataset & Models section | h-e1 pipeline, HH-RLHF dataset specified ✓ |
| FR4 | Evaluation → Primary Metrics | Cohen's d ≥ 0.15, p < 0.05 specified ✓ |
| FR5 | Evaluation → Secondary Metrics | Cronbach's α > 0.7 specified ✓ |
| FR6 | Evaluation → Tertiary Metrics | 2/3 splits replication specified ✓ |
| FR7 | Visualization Requirements | 5 figures listed (gate metrics, forest plot, density, paired diff, heatmap) ✓ |
| Success Criteria | Phase 2B Section 2.2 | All three gate criteria (P1, P2, P3) specified ✓ |

**100% Traceability Achieved:** Every PRD requirement traces to Phase 2C experiment brief.

---

**Generated:** 2026-03-17
**Version:** 1.0
**Status:** Ready for Architecture Design (Phase 3 Step 3)
