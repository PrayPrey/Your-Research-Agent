# Product Requirements Document (PRD)
**Hypothesis:** h-e1
**Version:** 1.0
**Date:** 2026-08-25
**Author:** Anonymous

---

## Executive Summary

### Purpose
Validate existence of reformulation rate decrease AND diversity correlation in HH-RLHF conversations with ≥5 turns through measurement experiment.

### Hypothesis Statement
Reformulation rate decrease AND diversity correlation exist in HH-RLHF conversations with ≥5 turns.

### Hypothesis Type
EXISTENCE (Proof-of-Concept)

### Gate Condition
MUST_WORK - Hypothesis must demonstrate negative reformulation slope (< 0) to proceed. Failure blocks dependent hypotheses.

### Success Criteria
- h-e1: Reformulation slope coefficient < 0 (negative slope indicates learning)
- Statistical significance: p < 0.05 OR effect size OR > 1.2

---

## Problem Statement

### Research Question
Do users show decreasing query reformulation rates across conversation turns in RLHF dialogues, and does this correlate with AI response diversity?

### Motivation
Understanding user learning patterns and AI responsiveness in multi-turn conversations is critical for:
- Alignment quality assessment
- Conversation success prediction
- Adaptive response generation strategies

### Current State
- HH-RLHF dataset contains multi-turn conversations but lacks analysis of temporal user behavior patterns
- No existing measurement of reformulation dynamics or diversity coupling

### Desired State
- Quantified reformulation slope across conversation turns
- Measured correlation between query diversity and response diversity
- Statistical validation of both phenomena

---

## Functional Requirements

### FR1: Dataset Loading and Filtering
**Priority:** P0 (Critical)
**Component:** Data Preparation

Load HH-RLHF dataset and filter for analysis-ready conversations.

**Acceptance Criteria:**
- Load from `Anthropic/hh-rlhf` via Hugging Face datasets
- Filter conversations with ≥5 turns (minimum for slope estimation)
- Parse conversation structure: user queries, AI responses, metadata
- Extract helpfulness ratings and conversation length
- Expected output: ~50k conversations meeting criteria

**Data Structure:**
```python
{
  "conversation_id": str,
  "turns": [
    {"user_query": str, "ai_response": str, "turn_index": int}
  ],
  "helpfulness_rating": float,
  "turn_count": int
}
```

### FR2: Reformulation Detection Module
**Priority:** P0 (Critical)
**Component:** Analysis Engine

Detect query reformulation between consecutive turns using semantic + syntactic signals.

**Acceptance Criteria:**
- Implement semantic similarity via SBERT (all-MiniLM-L6-v2)
- Implement syntactic distance via Levenshtein edit distance
- Reformulation threshold: semantic_sim > 0.7 AND normalized_edit > 0.3
- Return binary reformulation indicator per turn pair

**API Signature:**
```python
def detect_reformulation(query_t: str, query_t1: str) -> bool
```

### FR3: Reformulation Slope Computation
**Priority:** P0 (Critical)
**Component:** Analysis Engine

Compute reformulation rate decline slope across turns for each conversation.

**Acceptance Criteria:**
- Apply reformulation detection to all consecutive query pairs
- Compute binary reformulation rate per turn
- Fit linear regression: rate ~ turn_index
- Return slope coefficient (negative = learning)

**API Signature:**
```python
def compute_reformulation_slope(conversation: List[str]) -> float
```

### FR4: Diversity Measurement
**Priority:** P0 (Critical)
**Component:** Analysis Engine

Compute lexical diversity using distinct-1 metric.

**Acceptance Criteria:**
- Compute distinct-1 for query sequences
- Compute distinct-1 for response sequences
- Distinct-1 = unique_tokens / total_tokens

**API Signature:**
```python
def compute_diversity(texts: List[str]) -> float
```

### FR5: Statistical Analysis
**Priority:** P0 (Critical)
**Component:** Analysis Engine

Run statistical tests for hypothesis validation.

**Acceptance Criteria:**
- Compute slope distribution across all conversations
- Test slope < 0 via one-sample t-test or sign test
- Report: slope coefficient, p-value, effect size (Cohen's d)

**Metrics:**
- Primary: Reformulation slope coefficient
- Secondary: p-value, effect size

### FR6: Visualization Generation
**Priority:** P1 (High)
**Component:** Reporting

Generate required and recommended visualizations.

**Required Figure:**
- Gate metrics comparison: target vs actual (bar chart)

**Recommended Figures:**
1. Reformulation rate over turns (line plot)
2. Slope distribution (histogram)
3. Diversity scatter plot (query vs response diversity)
4. Success stratification (slope comparison by outcome)

**Output:** All figures saved to `{hypothesis_folder}/figures/`

---

## Non-Functional Requirements

### NFR1: Statistical Validity
- Use established libraries: scipy.stats, statsmodels
- Report all assumptions and test conditions
- Use fixed random seed (42) for reproducibility

### NFR2: Performance
- Process 50k conversations within reasonable time (<30 min on standard hardware)
- Efficient SBERT batch encoding

### NFR3: Code Quality
- Type hints for all functions
- Docstrings for public APIs
- Unit tests for reformulation detection logic

### NFR4: Reproducibility
- Fixed random seed
- Versioned dependencies
- Exact library versions logged

---

## Technical Specifications

### Tools and Libraries
- **HuggingFace Datasets:** Data loading
- **sentence-transformers:** SBERT embeddings (all-MiniLM-L6-v2)
- **python-Levenshtein:** Edit distance computation
- **scipy:** Statistical analysis (linregress, pearsonr)
- **statsmodels:** Advanced statistical modeling
- **matplotlib/seaborn:** Visualization

### Installation Requirements
```bash
pip install datasets sentence-transformers python-Levenshtein scipy statsmodels matplotlib seaborn
```

### Pseudo-code Reference
See Phase 2C experiment brief Section "Proposed Model" for core algorithm implementation.

---

## Success Metrics

### Primary Gate Metric
**Reformulation Slope < 0**
- Target: slope coefficient < 0
- Measurement: Linear regression coefficient
- Success threshold: Negative value (direction check only for PoC)

### Statistical Validation
- p-value < 0.05 (statistical significance)
- OR effect size (Cohen's d) > 1.2 (large effect)

### Baseline Comparison
- Random baseline (permuted data): slope ≈ 0
- Expected effect size: medium (Cohen's d ≈ 0.5)

---

## Dependencies and Prerequisites

### Phase Dependencies
- **Upstream:** Phase 2C experiment design (COMPLETED)
- **Downstream:** Phase 4 implementation

### Data Dependencies
- HH-RLHF dataset (public, freely available)
- No proprietary data required

### Hypothesis Dependencies
- **Type:** FOUNDATION (no prerequisites)
- **Gate:** MUST_WORK (blocks dependents if failed)

---

## Out of Scope

### Explicitly Not Included
- Model training or fine-tuning
- Real-time conversation analysis
- Causality analysis (correlation only)
- Multi-dataset validation
- Human annotation or validation
- Alternative reformulation detection methods (beyond SBERT + edit distance)

---

## Risks and Mitigations

### Risk 1: Low Signal-to-Noise
**Impact:** Slope not significantly different from zero
**Mitigation:** Use large sample size (50k conversations), robust statistical tests
**Fallback:** Report effect size even if p-value marginal

### Risk 2: Reformulation Detection Accuracy
**Impact:** High false positive/negative rates
**Mitigation:** Tune thresholds (semantic_sim, edit_dist) on sample data
**Fallback:** Manual annotation of sample for validation

### Risk 3: Insufficient Long Conversations
**Impact:** <1000 conversations with ≥5 turns
**Mitigation:** Verify dataset statistics before implementation
**Fallback:** Lower turn threshold to ≥4 turns

---

## Appendix

### A. Data Schema
```python
ConversationData = {
  "conversation_id": str,
  "turns": List[Turn],
  "metadata": {
    "helpfulness": float,
    "turn_count": int
  }
}

Turn = {
  "user_query": str,
  "ai_response": str,
  "turn_index": int
}
```

### B. Phase 2C Traceability
| PRD Section | Phase 2C Source |
|-------------|-----------------|
| Dataset | Section "Dataset" |
| Reformulation Detection | Section "Proposed Model" pseudo-code |
| Analysis Protocol | Section "Training Protocol" |
| Success Criteria | Section "Evaluation" |
| Visualization | Section "Visualization Requirements" |

### C. Implementation Notes
- Experiment type: Data analysis (no model training)
- Execution environment: Standard Python scientific stack
- No GPU required
- Estimated runtime: <30 minutes

---

**PRD Status:** Draft v1.0
**Next Phase:** Architecture Design (Phase 3 Step 3)
