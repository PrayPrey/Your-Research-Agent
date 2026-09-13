# Product Requirements Document (PRD): h-c1

**Date:** 2026-08-24  
**Hypothesis ID:** h-c1  
**Type:** CONDITION  
**Author:** Phase 3 Pipeline  
**Status:** Implementation Planning

---

## Overview

### Purpose

Validate pre-conditions for entity-error detection research by measuring:
1. NER tool accuracy (≥90% F1) on entity identification
2. Wikipedia coverage (≥90%) for entity-error test cases

### Success Criteria

**MUST_WORK Gate:**
- NER F1 ≥ 0.90 AND Wikipedia coverage ≥ 0.90 → PASS
- Either metric < 0.90 → FAIL (blocks h-e1, h-m1, h-m2)

### Context

Root CONDITION hypothesis. No prerequisites. Validates measurement assumptions A1 (NER accuracy) and A2 (Wikipedia coverage) from Phase 2A before downstream experiments.

---

## Functional Requirements

### FR-1: Data Preparation

**FR-1.1:** Load TruthfulQA generation split from HuggingFace  
**FR-1.2:** Filter for single-entity factual questions (N=100)  
**FR-1.3:** Create gold entity annotations (span, type) for NER validation  
**FR-1.4:** Split into entity-error (N=50) and non-entity-error (N=50) subsets  
**FR-1.5:** Extract correct entities from entity-error cases for Wikipedia lookup

**Output:** `data/truthfulqa_entity_subset/` with:
- `entity_errors.json` (50 samples with gold annotations)
- `non_entity_errors.json` (50 samples)
- `gold_annotations.jsonl` (100 samples, spaCy-compatible format)

### FR-2: NER Validation

**FR-2.1:** Load spaCy `en_core_web_lg` pre-trained model  
**FR-2.2:** Run NER on 100 gold-annotated samples  
**FR-2.3:** Score predictions against gold labels using `spacy.scorer.Scorer`  
**FR-2.4:** Extract entity-level F1 score (`ents_f`)

**Output:** NER F1 score (float, 0.0-1.0)

### FR-3: Wikipedia Coverage Validation

**FR-3.1:** Extract entities from 50 entity-error samples  
**FR-3.2:** Query Wikipedia API for each entity  
**FR-3.3:** Check page existence + non-stub filter (>100 chars content)  
**FR-3.4:** Calculate coverage percentage

**Output:** Wikipedia coverage (float, 0.0-1.0)

### FR-4: Gate Evaluation

**FR-4.1:** Compare NER F1 against threshold (0.90)  
**FR-4.2:** Compare Wikipedia coverage against threshold (0.90)  
**FR-4.3:** Determine gate status (PASS/FAIL)  
**FR-4.4:** Log detailed metrics breakdown

**Output:** Gate result (PASS/FAIL) with supporting metrics

### FR-5: Reporting

**FR-5.1:** Generate validation report (`04_validation.md`)  
**FR-5.2:** Create required figure: Target vs Actual metrics bar chart  
**FR-5.3:** Create additional figures:
- NER confusion matrix by entity type
- Coverage by entity type (PERSON/ORG/GPE)
- Per-sample NER F1 distribution histogram

**Output:** `figures/` folder with 4 plots + validation report

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Deterministic evaluation (no random seeds)
- Version-pinned dependencies (spaCy 3.x, wikipediaapi)

### NFR-2: Performance
- Wikipedia API queries: max 10 concurrent threads (rate limit compliance)
- Total runtime: <5 minutes for 100 samples

### NFR-3: Error Handling
- Wikipedia API failures: log entity + retry once, skip if persistent fail
- NER scorer errors: fail early with clear diagnostic

---

## Technical Constraints

### TC-1: Environment
- Python 3.8+
- spaCy model download: `python -m spacy download en_core_web_lg`
- Dependencies: `spacy`, `wikipediaapi`, `datasets` (HuggingFace)

### TC-2: Data Format
- Gold annotations: spaCy-compatible format `{"entities": [(start, end, label)]}`
- Entity extraction: plain string list for Wikipedia lookup

### TC-3: Metrics Libraries
- NER F1: `spacy.scorer.Scorer` (official implementation)
- Wikipedia coverage: custom (no external library)

---

## Edge Cases

### EC-1: Ambiguous Entity Names
- **Issue:** "Jordan" (person vs. country)  
- **Mitigation:** Use context from question text; prioritize exact Wikipedia title match

### EC-2: Wikipedia API Throttling
- **Issue:** Rate limit exceeded for rapid queries  
- **Mitigation:** ThreadPoolExecutor capped at 10 workers, exponential backoff on 429 errors

### EC-3: Missing Gold Annotations
- **Issue:** Subset creation may leave gaps in entity labels  
- **Mitigation:** Manual annotation required before validation; fail if annotations incomplete

---

## Success Metrics

| Metric | Threshold | Expected Baseline |
|--------|-----------|-------------------|
| NER F1 | ≥ 0.90 | 0.85-0.90 (spaCy lg) |
| Wikipedia Coverage | ≥ 0.90 | 0.90-0.98 (common entities) |

**Gate Logic:**
```python
gate_pass = (ner_f1 >= 0.90) and (coverage >= 0.90)
```

---

## Dependencies

**No prerequisite hypotheses** (root CONDITION)

**External Dependencies:**
- spaCy `en_core_web_lg` model (~800MB download)
- Wikipedia API access (internet connection required)
- TruthfulQA dataset (HuggingFace Datasets library)

---

## Deliverables

1. **Code:** `h-c1/code/validate_preconditions.py` (main script)
2. **Data:** `data/truthfulqa_entity_subset/` (100 annotated samples)
3. **Figures:** `h-c1/figures/` (4 visualization files)
4. **Report:** `h-c1/04_validation.md` (gate result + metrics)

---

## Out of Scope

- Training custom NER models (use pre-trained only)
- Wikipedia dump offline processing (API-based only)
- Dataset expansion beyond N=100
- Multi-entity questions (single-entity only)

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| NER F1 < 0.90 on TruthfulQA entities | Blocks all downstream hypotheses | Use domain-specific NER model if pre-trained fails |
| Wikipedia coverage < 0.90 for entity-errors | Invalidates retrieval assumption | Expand to alternative knowledge corpora (DBpedia, Wikidata) |
| Manual annotation bottleneck | Delays validation | Pre-labeled subset or automated weak supervision |

---

*PRD for CONDITION hypothesis h-c1*  
*No training required — pure validation experiment*  
*Next: Phase 3 Architecture Design*
