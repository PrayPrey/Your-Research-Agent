# Phase 2B Context: H-C1

**Hypothesis ID:** h-c1  
**Type:** CONDITION  
**Gate:** MUST_WORK

---

## Hypothesis Statement

Pre-validation conditions are met: NER tool achieves ≥90% accuracy on entity identification, and Wikipedia achieves ≥90% coverage for entity-error test cases.

---

## Rationale

Validates measurement assumptions A1 (NER accuracy) and A2 (Wikipedia coverage) before pattern detection experiments. Foundation for all subsequent hypotheses.

---

## Falsification Criteria

If NER accuracy < 90% OR Wikipedia coverage < 90%, measurement validity compromised.

---

## Experimental Setup (from Phase 2B)

**Dataset:** TruthfulQA single-entity factual questions subset  
**Sample Size:** N=100 (50 entity-error, 50 non-entity-error per model)  
**Models:** GPT-3.5 and Llama-2-7B  
**NER Tool:** spaCy  
**Retrieval Corpus:** Wikipedia  
**Significance Level:** α = 0.05

---

## Success Criteria

- NER entity identification accuracy ≥ 90%
- Wikipedia coverage for entity-error test cases ≥ 90%

---

## Dependencies

**Prerequisites:** None (root condition)  
**Blocks:** h-e1, h-m1, h-m2 (all downstream hypotheses depend on this validation)

---

## Phase 2A Mapping

Maps to Assumption A1 (NER accuracy) and A2 (Wikipedia coverage) from Phase 2A synthesis.

---

*Generated: 2026-08-24*  
*Source: 02b_verification_plan.md*
