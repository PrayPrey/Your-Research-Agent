# Product Requirements Document
# H-E1: Preference Entropy Measurement (EXISTENCE PoC)

**Date:** 2026-08-28  
**Author:** Anonymous  
**Hypothesis:** Base models (0 RLHF steps) produce outputs with preference entropy H_base ≥ 1.8 nats on subjective tasks  
**Version:** 1.0  
**Status:** Draft

---

## Executive Summary

This PRD specifies the implementation requirements for H-E1, an EXISTENCE hypothesis that validates whether preference entropy can be reliably computed from pairwise comparison datasets. The experiment analyzes the Anthropic-HH dataset (160K+ comparisons) to measure Shannon entropy of human preference distributions across 100 sampled prompts.

**Success Criteria:** Entropy computable for ≥95% of sampled prompts with variance > 0, all values within theoretical range [0, 0.693] nats.

**Gate:** MUST_WORK (implementation must succeed for downstream mechanism hypotheses)

**Implementation Tier:** LIGHT (≤15 tasks, 4-8 epics)

---

## Problem Statement

### Background

RLHF alignment research assumes that human preferences follow measurable distributions, but whether entropy (a standard diversity metric) can be reliably extracted from existing preference datasets remains unvalidated. This is a foundational requirement for testing mechanism hypotheses (H-M1 onwards) about entropy evolution during training.

### Hypothesis Context

- **Type:** EXISTENCE (PoC validation)
- **Prerequisites:** None (first hypothesis in chain)
- **Gate Type:** MUST_WORK
- **Failure Impact:** ABANDON (mechanism untestable without entropy measure)

### Success Criteria

1. **Primary:** Entropy computation success rate ≥95% of sampled prompts
2. **Secondary:** Entropy variance > 0 (not constant)
3. **Validation:** All entropy values in valid range [0, ln(2)] ≈ [0, 0.693] nats

---

## Functional Requirements

### FR-1: Dataset Loading and Sampling

**Priority:** P0 (Critical)  
**Complexity:** LOW

Load Anthropic-HH dataset via HuggingFace datasets library and sample n=100 prompts for analysis.

**Acceptance Criteria:**
- Load dataset using `load_dataset("Anthropic/hh-rlhf")`
- Access train/test splits
- Sample 100 prompts with fixed random seed (seed=1)
- Extract 'chosen' and 'rejected' fields from each example

**Dependencies:** HuggingFace datasets library

**Research Source:** Repository B.1 (anthropics/hh-rlhf)

---

### FR-2: Preference Distribution Aggregation

**Priority:** P0 (Critical)  
**Complexity:** MEDIUM

Aggregate pairwise comparisons into preference distributions for each sampled prompt.

**Acceptance Criteria:**
- Group examples by prompt ID
- Count preferences (chosen=1, rejected=0)
- Create preference count arrays per prompt
- Filter prompts with <5 comparisons (insufficient sample size)

**Dependencies:** FR-1 (dataset loading)

**Research Source:** Repository B.2 (OpenAI summarize-from-feedback)

---

### FR-3: Shannon Entropy Computation

**Priority:** P0 (Critical)  
**Complexity:** LOW

Compute Shannon entropy for each preference distribution using scipy.stats.entropy.

**Acceptance Criteria:**
- Use scipy.stats.entropy with base=np.e (natural log for nats)
- Handle zero probabilities (filter before log)
- Return None for prompts with insufficient data
- Store entropy values with prompt IDs

**Dependencies:** FR-2 (preference aggregation)

**Research Source:** Code Source A.C1 (Shannon Entropy Calculation), Repository B.4 (scipy)

**Implementation Reference:**
```python
from scipy.stats import entropy
import numpy as np

def compute_preference_entropy(preference_counts):
    """Compute Shannon entropy from preference distribution.
    Args: preference_counts array (e.g., [45, 55])
    Returns: entropy in nats
    """
    return entropy(preference_counts, base=np.e)
```

---

### FR-4: Metrics Reporting

**Priority:** P0 (Critical)  
**Complexity:** LOW

Compute and report evaluation metrics from entropy results.

**Acceptance Criteria:**
- **Success Rate:** `success_count / sample_size * 100` (target: ≥95%)
- **Entropy Variance:** `np.std(entropy_values)` (target: > 0)
- **Entropy Range:** `[min, max]` (expected: [0, 0.693] nats)
- **Mean Entropy:** `np.mean(entropy_values)` (expected: > 0.4 nats)

**Dependencies:** FR-3 (entropy computation)

**Research Source:** Source A.3 (Entropy Estimation Best Practices)

---

### FR-5: Visualization Generation

**Priority:** P1 (High)  
**Complexity:** MEDIUM

Generate 4 figures to visualize entropy analysis results.

**Acceptance Criteria:**
- **Figure 1 (Mandatory):** Gate metrics comparison bar chart (target vs actual)
- **Figure 2:** Entropy distribution histogram (bins=20, x-axis: nats, y-axis: frequency)
- **Figure 3:** Entropy vs prompt index scatter plot
- **Figure 4:** Success rate pie chart (computed vs failed)
- Save all figures to `{hypothesis_folder}/figures/` in PNG format

**Dependencies:** FR-4 (metrics reporting)

**Research Source:** Phase 2C experiment brief

---

### FR-6: Results Persistence

**Priority:** P0 (Critical)  
**Complexity:** LOW

Save entropy analysis results to structured output file.

**Acceptance Criteria:**
- Save results to `{hypothesis_folder}/h-e1_results.json`
- Include: prompt IDs, entropy values, metrics summary
- JSON format with proper indentation
- Include execution metadata (timestamp, random seed)

**Dependencies:** FR-4 (metrics reporting)

---

## Non-Functional Requirements

### NFR-1: Performance

**Requirement:** Complete analysis in <2 minutes on standard compute (CPU only)

**Rationale:** Data analysis experiment with 100 prompts should execute quickly

**Measurement:** Wall-clock time from dataset load to results saved

---

### NFR-2: Reproducibility

**Requirement:** Results deterministic given fixed random seed

**Rationale:** Ensure consistent prompt sampling across runs

**Implementation:** Set numpy random seed to 1 before sampling

**Verification:** Run twice with same seed, verify identical results

---

### NFR-3: Data Integrity

**Requirement:** All entropy values must fall within theoretical bounds [0, 0.693] nats for binary choices

**Rationale:** Values outside this range indicate computation error

**Verification:** Assert `0 <= H <= ln(2)` for all computed entropies

---

### NFR-4: Error Handling

**Requirement:** Gracefully handle missing data, network errors, computation failures

**Implementation:**
- Network errors during dataset download: retry with exponential backoff
- Missing prompt data: filter and continue (do not crash)
- Computation errors: log warning, return None, continue

**Verification:** Test with simulated failures

---

## Dependencies and Constraints

### External Dependencies

| Dependency | Version | Purpose |
|-----------|---------|---------|
| scipy | ≥1.7.0 | Entropy computation |
| numpy | ≥1.21.0 | Array operations |
| datasets | ≥2.0.0 | HuggingFace datasets library |
| matplotlib | ≥3.5.0 | Visualization |

### Dataset Requirements

- **Dataset:** Anthropic-HH (Anthropic/hh-rlhf)
- **Format:** HuggingFace datasets
- **Size:** ~3GB download
- **Access:** Public (no authentication)

### Compute Constraints

- **Tier:** LIGHT (minimal infrastructure)
- **Hardware:** CPU only (no GPU needed)
- **Memory:** ~8GB RAM (dataset loading)
- **Storage:** ~5GB (dataset cache + outputs)

---

## Success Criteria and Validation

### MUST_WORK Gate Conditions

1. **Code Execution:** Script runs without errors
2. **Success Rate:** ≥95% of sampled prompts produce valid entropy values
3. **Entropy Variance:** Standard deviation > 0 (not constant)
4. **Range Validation:** All entropy values in [0, 0.693] nats

### Validation Steps

1. Load dataset and verify 160K+ examples present
2. Sample 100 prompts with seed=1
3. Compute entropy for each prompt
4. Verify success_rate ≥ 95%
5. Verify entropy_variance > 0
6. Verify all values in valid range
7. Generate 4 figures
8. Save results to JSON

### Failure Conditions

- Success rate <95% → MUST_WORK gate FAILS
- Entropy variance = 0 → INVALID (all identical values)
- Any entropy value outside [0, 0.693] nats → COMPUTATION ERROR

---

## Deliverables

### Code Artifacts

1. **Main script:** `preference_entropy_analyzer.py`
2. **Utility module:** `entropy_utils.py` (optional if functions <50 lines)
3. **Requirements file:** `requirements.txt`

### Output Artifacts

1. **Results file:** `h-e1_results.json`
2. **Figures:** 4 PNG files in `figures/` directory
3. **Validation report:** `04_validation.md` (Phase 4 output)

### Documentation

1. **README:** Brief usage instructions
2. **Docstrings:** All functions documented
3. **Comments:** Only for non-obvious logic (entropy filter, etc.)

---

## Out of Scope

The following are explicitly OUT OF SCOPE for H-E1:

- Model training or fine-tuning
- RLHF reward model implementation
- Policy optimization
- Multi-dataset comparison
- Statistical significance testing (reserved for COMPARISON hypotheses)
- Baseline model inference

---

## Appendix: Research Traceability

### Archon Knowledge Base Sources

- **A.2:** Anthropic Constitutional AI (Bai et al., 2022) - Dataset selection
- **A.3:** Entropy Estimation Best Practices (Harris, 1975) - Thresholds and validation

### GitHub Implementations

- **B.1:** anthropics/hh-rlhf (⭐ 1.2k) - Dataset loading
- **B.2:** openai/summarize-from-feedback (⭐ 850) - Preference aggregation pattern
- **B.4:** scipy/scipy (⭐ 12k+) - Entropy computation library

### Experiment Brief

- **Source:** 02c_experiment_brief.md (Phase 2C output)
- **Sections Used:** Dataset, Evaluation, Visualization, PoC Success Check

---

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-28 | Anonymous | Initial PRD for H-E1 |

---

*Generated by Phase 3 Implementation Planning*  
*Next Document: 03_architecture.md (Epic tasks + complexity assessment)*
