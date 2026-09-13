# Hypothesis: h-m2

**Generated**: 2026-08-24T00:00:00Z  
**Type**: MECHANISM  
**Gate**: MUST_WORK  
**Prerequisites**: h-m1 (VALIDATED)

---

## Statement

Matched correction routing (entity-error → RAG) achieves higher success rates than mismatched routing (entity-error → COT) by ≥20 percentage points or ≥50% relative improvement, replicated across GPT-3.5 and Llama-2-7B.

---

## Rationale

Tests causal mechanism Step 3 (Correction Effectiveness). Proves routing framework has practical utility, not just diagnostic capability.

---

## Falsification Criteria

- Difference < 20 points AND relative improvement < 50% in either model
- OR opposite direction (COT > RAG for entity-errors)

---

## Experimental Design

### Dataset
- **Source**: TruthfulQA single-entity factual questions subset
- **Split**: Entity-error cases (identified by h-m1 entropy classifier)
- **Sample Size**: N=100 (50 entity-error cases per model)
- **Test Models**: GPT-3.5 and Llama-2-7B

### Success Criteria
**Gate Condition (MUST_WORK)**:
- Matched routing (entity-error → RAG) success rate - Mismatched routing (entity-error → COT) success rate ≥ 20 percentage points
- OR relative improvement ≥ 50%
- **Must replicate across BOTH GPT-3.5 AND Llama-2-7B**

**Falsification**:
- Difference < 20 points AND relative improvement < 50% in either model
- OR opposite direction (COT > RAG for entity-errors)

### Controlled Variables
- Dataset: TruthfulQA single-entity factual questions subset
- Models: GPT-3.5 and Llama-2-7B
- NER Tool: spaCy
- Retrieval Corpus: Wikipedia
- Correction Threshold: ≥20 percentage points or ≥50% relative improvement
- Significance Level: α = 0.05

---

## Continuation Context

**Prerequisites**: h-m1 (VALIDATED)

**Previous Results from h-m1**:
- Entropy classification accuracy: 86.7% on test set
- Optimal threshold: 0.32 (entropy < 0.32 → entity-error)
- Perfect entity-error precision: 10/10 correct (100%)
- Non-entity recall: 3/5 correct (60%)

**Continuation Logic**:
- h-m1 proves entropy-based classification can identify entity-error failures with 86.7% accuracy
- Now test whether routing entity-errors to RAG (matched) outperforms routing to COT (mismatched)
- Uses h-m1's entropy classifier (threshold 0.32) to identify entity-error cases for correction experiments

---

## Risk Analysis

**Moderate-Risk Hypothesis**: Correction success depends on RAG retrieval quality and COT baseline performance. Pilot experiment (N=20) grounds threshold expectations.

**Mitigation**: Multi-model testing (GPT-3.5 + Llama-2-7B) reduces architecture-specific risk.

---

## Phase 2A Mapping

**Maps to Phase 2A Prediction**: P2 (correction validation)

---

*This hypothesis file was auto-generated from Phase 2B context. Next: Phase 2C experiment design.*
