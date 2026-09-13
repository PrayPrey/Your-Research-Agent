# Product Requirements Document (PRD): H-M4 Post-Hoc Experimental Validation

---
**Date:** 2026-08-25
**Hypothesis ID:** h-m4
**Hypothesis Type:** MECHANISM (PoC)
**Author:** Anonymous
**Status:** Draft

---

## Executive Summary

### Vision
Validate the complete verification system pipeline (KB construction + confound detection) by testing whether hypotheses classified as "testable" actually produce significant experimental results (ground truth confirmation).

### Purpose
This PRD defines requirements for implementing h-m4, which tests whether the system's (D,B,M) existence checks and confound flagging correctly predict experimental feasibility. Success validates the entire verification pipeline built across h-e1, h-m1, h-m2, and h-m3.

### Success Criteria (Gate Condition)
- **MUST_WORK Gate:** ≥65% of sampled "testable" hypotheses yield p < 0.05 results (13/20 successes)
- **PoC Baseline:** >50% success rate (better than random classification)
- **Failure Action:** ABANDON post-hoc validation claim, revert to expert agreement baseline

---

## Problem Statement

### Background
Prior hypotheses validated individual verification system components:
- h-e1: Knowledge base existence
- h-m1: KB lookup precision (≥80%)
- h-m2: Constraint-satisfiability routing precision (>60%)
- h-m3: Confound flagging precision (93.33%)

However, component validation does not prove the complete pipeline correctly predicts experimental feasibility. H-M4 provides ground truth validation by actually running experiments on system-classified hypotheses.

### Current State
- Verification system classifies hypotheses as "testable" or "not-testable" based on (D,B,M) existence + confound patterns
- No validation that "testable" classification correlates with actual experimental success
- Unknown false positive rate (testable → p ≥ 0.05) and false negative rate

### Target State
- Meta-research validation demonstrating ≥65% of "testable" hypotheses yield p < 0.05 results
- Statistical confirmation that system predictions outperform random baseline (50%)
- Evidence that constraint-satisfiability framework correctly predicts experimental feasibility

---

## Requirements

### Functional Requirements

#### FR-1: Hypothesis Pool Generation
**Description:** Generate 100 diverse deep learning hypotheses via LLM with controlled properties
**Priority:** P0 (Critical)
**Details:**
- Domains: NLP, Vision, Training, Multimodal
- Complexity: Simple, Moderate, Complex (balanced distribution)
- Ground truth (D,B,M) existence encoded in generation
- Each hypothesis includes: statement, domain, intervention, outcome, (D,B,M) triple

**Acceptance Criteria:**
- 100 unique hypotheses generated
- Domain balance: ~25 per domain
- Complexity balance: ~33 per level
- JSON structure matches schema in Phase 2C

#### FR-2: Verification System Pipeline Execution
**Description:** Run all 100 hypotheses through KB lookup (h-m1) + confound detection (h-m3)
**Priority:** P0 (Critical)
**Dependencies:** FR-1
**Details:**
- KB lookup: Check if required (D,B,M) triple exists in knowledge base
- Confound detection: Flag known confound patterns (from h-m3)
- Classification: "testable" if (DB M exists AND no confounds), else "not-testable"

**Acceptance Criteria:**
- All 100 hypotheses processed
- Classification recorded with reason
- (D,B,M) triple match logged for testable hypotheses

#### FR-3: Random Sampling from Testable Pool
**Description:** Sample 20 hypotheses from "testable" group without replacement
**Priority:** P0 (Critical)
**Dependencies:** FR-2
**Details:**
- Filter: system_classification == "testable"
- Sampling: Random without replacement (k=20)
- Fallback: If <20 testable hypotheses, use all available and adjust threshold

**Acceptance Criteria:**
- 20 hypotheses sampled (or all if <20 testable)
- No duplicates in sample
- Sampling seed recorded for reproducibility

#### FR-4: Simplified PoC Experiment Execution
**Description:** Run simplified experiment for each sampled hypothesis
**Priority:** P0 (Critical)
**Dependencies:** FR-3
**Details:**
- Load dataset/model from (D,B,M) triple
- Control condition: Standard model configuration
- Treatment condition: Apply hypothesis intervention
- Statistical test: Two-sample t-test (scipy.stats.ttest_ind)
- Output: p-value per hypothesis

**Acceptance Criteria:**
- All 20 experiments execute without error
- P-values computed and logged
- Execution time: <10 minutes total (simplified experiments, not full training)

#### FR-5: Success Rate Calculation and Gate Check
**Description:** Calculate experimental success rate and validate against gate threshold
**Priority:** P0 (Critical)
**Dependencies:** FR-4
**Details:**
- Success definition: p < 0.05
- Success rate: (# successes) / 20
- Gate threshold: ≥0.65 (13/20 successes)
- Baseline comparison: >0.50 (random classifier)
- Statistical test: Binomial test vs random baseline

**Acceptance Criteria:**
- Success rate calculated correctly
- Gate status: PASS or FAIL
- PoC status: PASS or FAIL vs baseline
- Binomial test p-value reported

#### FR-6: Random Baseline Implementation
**Description:** Implement random binary classifier for comparison
**Priority:** P1 (High)
**Details:**
- Classification: Random choice between "testable" and "not-testable"
- Expected performance: 50% success rate (random chance)

**Acceptance Criteria:**
- Baseline implemented
- 50% success rate confirmed over large sample

#### FR-7: Result Visualization
**Description:** Generate required visualizations per Phase 2C
**Priority:** P1 (High)
**Dependencies:** FR-5
**Figures:**
1. **Gate Metrics Comparison** (mandatory): Success rate bar chart
   - X-axis: ['Random Baseline', 'Proposed System', 'Gate Threshold']
   - Y-axis: Success Rate (%)
   - Values: [50%, actual_success_rate, 65%]
   - Colors: Red (baseline), Green/Red (proposed based on gate), Blue (threshold line)
2. **Success Rate Distribution by Domain** (autonomous): Bar chart breakdown
3. **Classification Distribution** (autonomous): Pie chart (testable vs not-testable)
4. **P-value Distribution** (autonomous): Histogram of p-values

**Acceptance Criteria:**
- All 4 figures generated and saved to h-m4/figures/
- Gate metrics figure clearly shows gate status

### Data Requirements

#### DR-1: Hypothesis Test Pool Dataset
**Name:** System-Classified Hypothesis Test Pool
**Type:** custom-evaluation
**Format:** JSON array
**Size:** 100 generated hypotheses → 20 sampled
**Source:** Programmatic generation via LLM API
**Schema:**
```json
{
  "id": "string",
  "statement": "string",
  "domain": "nlp|vision|training|multimodal",
  "complexity": "simple|moderate|complex",
  "system_classification": "testable|not-testable",
  "dbm_triple": {"dataset": "string", "benchmark": "string", "metric": "string"},
  "confound_flagged": "boolean",
  "classification_reason": "string"
}
```

#### DR-2: Knowledge Base (from h-m1)
**Name:** (D,B,M) Triple Knowledge Base
**Source:** h-m1/data/kb.json (or equivalent)
**Usage:** FR-2 KB lookup

#### DR-3: Confound Pattern Database (from h-m3)
**Name:** Cross-Domain Confound Patterns
**Source:** h-m3/data/confound_db.json (or equivalent)
**Usage:** FR-2 confound detection

### Non-Functional Requirements

#### NFR-1: Reproducibility
- All random operations must use fixed seeds
- Hypothesis generation prompts logged
- Sampling seed recorded
- Experimental configurations saved

#### NFR-2: Performance
- Total execution time: <15 minutes
- Hypothesis generation: <3 minutes
- Verification pipeline: <2 minutes (100 hypotheses)
- Experiments: <10 minutes (20 simplified PoCs)

#### NFR-3: Logging and Traceability
- All classifications logged with reasons
- P-values and experimental results saved
- Intermediate outputs (testable pool, sampled hypotheses) cached

#### NFR-4: Error Handling
- Graceful degradation if <20 testable hypotheses (use all available, adjust threshold)
- Experiment failures logged but do not block pipeline
- Missing (D,B,M) triples handled explicitly

### Dependencies and Constraints

#### External Dependencies
- h-m1: Knowledge base for (D,B,M) lookup
- h-m3: Confound pattern database
- scipy.stats: Statistical testing library
- LLM API: Hypothesis generation (e.g., Claude API, OpenAI)

#### Constraints
- **Budget:** FULL tier (30 tasks max)
- **Scope:** Meta-research validation (not paper reproduction)
- **Gate Type:** MUST_WORK (≥65% success rate required)
- **Simplified Experiments:** Not full training runs, PoC-level validation only

---

## Out of Scope

- Full-scale experiments with complete training runs
- Re-implementation of h-m1/h-m2/h-m3 components
- Hypothesis pool expansion beyond 100
- Multi-round sampling or adaptive threshold adjustment
- Confound pattern discovery (h-m3 patterns are fixed)

---

## Technical Specifications

### System Architecture
```
┌──────────────────────────────────────────┐
│ Hypothesis Generator (LLM)              │
│ → 100 diverse hypotheses                │
└─────────────┬────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Verification Pipeline                   │
│ • KB Lookup (h-m1)                      │
│ • Confound Detection (h-m3)             │
│ → Classification: testable/not-testable │
└─────────────┬────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Random Sampler                          │
│ → Sample 20 from "testable" pool        │
└─────────────┬────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Experiment Executor                     │
│ • Load (D,B,M) from sampled hypotheses  │
│ • Run control vs treatment              │
│ • Compute p-value (t-test)              │
│ → 20 p-values                           │
└─────────────┬────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Statistical Validator                   │
│ • Calculate success rate                │
│ • Binomial test vs baseline             │
│ • Gate check (≥65%)                     │
│ → PASS/FAIL                             │
└──────────────────────────────────────────┘
```

### Key Algorithms
1. **Hypothesis Generation:** LLM-based diverse generation with domain/complexity constraints
2. **KB Lookup:** Exact match on (D,B,M) triple
3. **Confound Detection:** Pattern matching from h-m3 database
4. **Statistical Test:** scipy.stats.ttest_ind for intervention vs control
5. **Success Rate:** Binomial proportion with binomial test vs H0: p=0.50

### File Structure
```
h-m4/
├── 02c_experiment_brief.md (input)
├── 03_prd.md (this file)
├── 03_architecture.md (next)
├── 03_logic.md
├── 03_config.md
├── data/
│   ├── hypothesis_pool.json (100 hypotheses)
│   ├── testable_pool.json (filtered)
│   ├── sampled_hypotheses.json (20)
│   └── experimental_results.json (p-values)
├── figures/
│   ├── gate_metrics_comparison.png
│   ├── success_rate_by_domain.png
│   ├── classification_distribution.png
│   └── pvalue_distribution.png
└── 04_validation.md (Phase 4 output)
```

---

## Evaluation and Metrics

### Primary Metric
**Experimental Success Rate**
- Definition: Proportion of sampled "testable" hypotheses yielding p < 0.05
- Computation: `success_rate = sum([p < 0.05 for p in p_values]) / 20`
- Gate Threshold: ≥0.65 (13/20 successes)
- Baseline: 0.50 (random classification)

### Secondary Metrics
1. **Precision:** True positives / (True positives + False positives)
   - True positive: "testable" AND p < 0.05
   - False positive: "testable" AND p ≥ 0.05
2. **Classification Distribution:** # testable vs # not-testable from 100 hypotheses
3. **Binomial Test P-value:** Significance of success rate vs random baseline

### Gate Logic
```python
# Gate Check
gate_pass = (success_rate >= 0.65)
poc_pass = (success_rate > 0.50)

# Statistical significance
from scipy.stats import binom_test
successes = sum([p < 0.05 for p in p_values])
p_value_vs_baseline = binom_test(successes, n=20, p=0.5, alternative='greater')

# Final Status
if gate_pass:
    status = "PASS (MUST_WORK gate satisfied)"
elif poc_pass:
    status = "PARTIAL (PoC confirmed, gate failed)"
else:
    status = "FAIL (No improvement over baseline)"
```

---

## Implementation Notes

### Phase 3 Outputs
1. **03_architecture.md:** Module breakdown, Epic tasks, file structure
2. **03_logic.md:** API signatures for generator/verifier/executor/validator
3. **03_config.md:** Hypothesis generation config, experimental config, random seeds

### Phase 4 Strategy
- **Data Preparation:** Generate hypothesis pool (FR-1)
- **Environment Setup:** Load h-m1 KB + h-m3 confound DB
- **Implementation:** 5 Epic tasks (generator, verifier, sampler, executor, validator)
- **Validation:** Run full pipeline, check gate

### Risk Mitigation
- **Risk:** <20 testable hypotheses → **Mitigation:** Adjust threshold or increase pool size
- **Risk:** Experiment failures → **Mitigation:** Log and continue, report failure rate
- **Risk:** Gate failure → **Mitigation:** ABANDON claim per gate condition

---

## Appendix

### Related Hypotheses
- **h-e1:** KB existence validation
- **h-m1:** KB lookup precision (≥80%)
- **h-m2:** Constraint-satisfiability routing (>60% baseline)
- **h-m3:** Confound flagging precision (93.33%)

### References
- Phase 2C Experiment Brief: h-m4/02c_experiment_brief.md
- Ioannidis et al. "Why Most Published Research Findings Are False" (2005)
- King et al. "The Automation of Science" (2009)
- scipy.stats documentation: https://docs.scipy.org/doc/scipy/reference/stats.html

---

**Document Status:** Draft - Ready for Phase 3 Architecture/Logic/Config
