# Product Requirements Document (PRD): H-E2

**Date:** 2026-07-11  
**Hypothesis:** Common semantic primitives exist across verifiers (Frama-C, Dafny, Why3) that can be abstracted into universal repair categories  
**Version:** 1.0  
**Phase:** 3 - Implementation Planning  

---

## Executive Summary

**Objective:** Validate the existence of common semantic primitives across three formal verification tools (Frama-C, Dafny, Why3) by constructing a cross-verifier error taxonomy and measuring coverage of universal repair categories.

**Success Criteria:** 
- ≥80% of error categories from all three verifiers map to shared semantic primitives
- Abstraction layer design is implementation-ready
- Coverage validated individually for each verifier (Frama-C, Dafny, Why3)

**Gate:** MUST_WORK - Failure invalidates cross-verifier portability claims and blocks H-M3 (Semantic Normalization Transfer)

---

## Background & Motivation

### Problem Statement
Current formal verification tools (Frama-C, Dafny, Why3) produce tool-specific error messages with no semantic normalization layer. This prevents:
- Cross-verifier knowledge transfer for repair strategies
- Portable LLM-based repair systems
- Unified abstraction of proof obligations

### Research Question
Do formal verification tools share sufficient semantic primitives to enable a universal error taxonomy? Specifically:
- Can ≥80% of error categories be mapped to shared semantic primitives?
- Does the abstraction layer remain feasible for implementation?

### Hypothesis Context
- **Type:** Existence (Foundation Layer)
- **Prerequisites:** None (Wave 1 - executable in parallel with H-E1)
- **Enables:** H-M3 (requires semantic primitives from H-E2)
- **Timeline:** 7 weeks (Week 5-12 of overall pipeline)

---

## Requirements

### Functional Requirements

#### FR-1: Error Category Extraction
**Priority:** P0 (Critical)  
**Description:** Extract error categories from three verifiers through documentation parsing and empirical testing

**Acceptance Criteria:**
- Parse Frama-C WP documentation for VC (Verification Condition) types
- Parse Dafny error documentation for verification failure categories
- Parse Why3 Model_parser API for error model element types
- Run verifiers on benchmark programs to collect ≥100 error instances per tool
- Output: Structured error category catalog per verifier (JSON/YAML)

**Data Sources:**
- Frama-C WP VC API: https://frama-c.com/api/frama-c-wp/Wp/VC/index.html
- Dafny error docs: https://dafny.org/v3.12.0/HowToFAQ/Errors
- Why3 Model_parser API: https://why3.org/api/Model_parser.html
- Benchmark programs: Frama-C examples, Juliet Test Suite verified subset, Why3 gallery

#### FR-2: Semantic Primitive Identification
**Priority:** P0 (Critical)  
**Description:** Identify universal repair categories through bottom-up semantic clustering

**Acceptance Criteria:**
- Cluster error categories by semantic structure (proof obligation types)
- Produce candidate list of ≥6 universal semantic primitives
- Primitives must cover: preconditions, postconditions, invariants, bounds checks, arithmetic overflow, null safety, termination, type correctness
- Output: Taxonomy specification document (primitives with definitions)

**Proposed Primitives (from Phase 2C research):**
1. MISSING_PRECONDITION
2. POSTCONDITION_FAILURE
3. LOOP_INVARIANT_VIOLATION
4. BOUNDS_CHECK_FAILURE
5. ARITHMETIC_OVERFLOW
6. NULL_DEREFERENCE
7. TERMINATION_FAILURE
8. TYPE_MISMATCH

#### FR-3: Mapping Construction
**Priority:** P0 (Critical)  
**Description:** Create verifier-to-primitive mapping table with confidence scores

**Acceptance Criteria:**
- Map each verifier error category to ≥1 semantic primitive
- Assign confidence scores (0.0-1.0) based on semantic alignment
- Document tool-specific edge cases (categories that resist abstraction)
- Output: Mapping table (verifier × category → primitive + confidence score)

**Mapping Schema:**
```python
{
  "verifier": str,  # "frama-c" | "dafny" | "why3"
  "error_category": str,
  "semantic_primitive": str | None,
  "confidence_score": float,  # 0.0-1.0
  "notes": str  # Tool-specific edge case documentation
}
```

#### FR-4: Coverage Computation
**Priority:** P0 (Critical)  
**Description:** Compute cross-verifier taxonomy coverage and validate success criteria

**Acceptance Criteria:**
- Implement coverage metric: (mapped categories / total categories) × 100%
- Compute per-verifier coverage breakdown
- Compute aggregate coverage across all verifiers
- Generate coverage report with threshold comparison
- Output: Coverage metrics JSON + visualization

**Success Thresholds:**
- Aggregate coverage ≥80% (MUST_WORK gate)
- Per-verifier coverage ≥80% (all three must pass)

### Non-Functional Requirements

#### NFR-1: Reproducibility
**Priority:** P0 (Critical)  
- All data extraction scripts must be deterministic
- Verifier versions must be pinned (Frama-C 28.1, Dafny 4.9.0, Why3 1.7.2)
- Benchmark program selection must be documented
- Random seed (if any clustering algorithms use randomness) must be fixed

#### NFR-2: Validation Rigor
**Priority:** P0 (Critical)  
- Taxonomy must be reviewed by formal methods expert (qualitative validation)
- Empirical validation on ≥500 total error instances across all verifiers
- Edge cases documented with justification for mapping decisions

#### NFR-3: Extensibility
**Priority:** P1 (High)  
- Taxonomy structure must support future verifier additions
- Mapping schema must allow multi-primitive assignments
- Confidence scoring must support threshold-based filtering

---

## Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Taxonomy Construction Pipeline             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Error Category Extraction (FR-1)                   │
│  ├─ Documentation Parser (Frama-C, Dafny, Why3 docs)        │
│  ├─ Empirical Runner (verifiers on benchmark programs)      │
│  └─ Output: error_categories.json                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Semantic Primitive Identification (FR-2)           │
│  ├─ Semantic Clustering (proof obligation grouping)         │
│  ├─ Primitive Definition (taxonomy specification)           │
│  └─ Output: semantic_primitives.yaml                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Mapping Construction (FR-3)                        │
│  ├─ Mapping Rules Engine (error → primitive logic)          │
│  ├─ Confidence Scoring (semantic alignment heuristics)      │
│  └─ Output: taxonomy_mapping.json                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Coverage Computation & Validation (FR-4)           │
│  ├─ Coverage Metrics (aggregate + per-verifier)             │
│  ├─ Threshold Validation (≥80% gate check)                  │
│  ├─ Visualization (heatmap, bar charts)                     │
│  └─ Output: coverage_report.json + figures/                 │
└─────────────────────────────────────────────────────────────┘
```

### Data Pipeline

**Inputs:**
- Verifier documentation (web scraping + manual curation)
- Benchmark programs (git clone):
  - Frama-C examples repository
  - Juliet Test Suite verified subset
  - Why3 gallery examples

**Outputs:**
- `error_categories.json` - Verifier-specific error catalog
- `semantic_primitives.yaml` - Universal repair categories taxonomy
- `taxonomy_mapping.json` - Verifier-to-primitive mappings
- `coverage_report.json` - Metrics with gate validation
- `figures/` - Visualizations (heatmap, coverage bars, frequency distribution)

### Technology Stack

**Core Technologies:**
- Python 3.10+
- Verifier toolchains:
  - Frama-C 28.1 (WP plugin)
  - Dafny 4.9.0
  - Why3 1.7.2 + Alt-Ergo/Z3 SMT solvers

**Libraries:**
- Data processing: pandas, pyyaml, json
- Visualization: matplotlib, seaborn
- Documentation parsing: BeautifulSoup, requests
- Subprocess management: subprocess (for verifier execution)

---

## Success Metrics & Validation

### Primary Metrics

**M1: Aggregate Coverage Percentage** (Gate Metric)
- **Definition:** (# mapped categories across all verifiers / total # categories) × 100%
- **Target:** ≥80%
- **Failure Threshold:** <60% → MUST_WORK gate fails

**M2: Per-Verifier Coverage**
- **Definition:** Coverage computed individually for Frama-C, Dafny, Why3
- **Target:** All three ≥80%
- **Purpose:** Ensure abstraction is not biased toward one verifier

**M3: Abstraction Layer Feasibility**
- **Definition:** Binary assessment of implementation readiness
- **Target:** Design document with clear API specification produced
- **Method:** Qualitative review by formal methods expert

### Secondary Metrics

**M4: Unmapped Category Analysis**
- **Purpose:** Identify error types that resist abstraction
- **Method:** Count + categorization of categories with confidence <0.5

**M5: Primitive Frequency Distribution**
- **Purpose:** Identify common vs. rare semantic categories
- **Method:** Histogram of error counts per primitive

### Validation Protocol

1. **Empirical Validation:** Run verifiers on ≥500 benchmark programs, collect error instances
2. **Expert Review:** Taxonomy reviewed by formal methods researcher
3. **Gate Validation:** Automated threshold check (coverage ≥80%)
4. **Baseline Comparison:** Compare to 0% baseline (no abstraction layer)

---

## Deliverables

### Code Artifacts
1. `taxonomy_builder.py` - Main pipeline orchestrator
2. `extractors/` - Documentation parsers + verifier runners
3. `clustering/` - Semantic primitive identification logic
4. `mapping/` - Verifier-to-primitive mapping engine
5. `evaluation/` - Coverage computation + visualization

### Documentation
1. `README.md` - Setup instructions, usage guide
2. `TAXONOMY.md` - Semantic primitives specification
3. `MAPPINGS.md` - Verifier-specific mapping rules
4. `04_validation.md` - Experimental results + gate validation

### Outputs
1. `data/error_categories.json` - Extracted error catalog
2. `data/semantic_primitives.yaml` - Taxonomy specification
3. `data/taxonomy_mapping.json` - Mapping table
4. `results/coverage_report.json` - Metrics
5. `figures/` - Visualizations (heatmap, coverage bars, unmapped analysis)

---

## Risks & Mitigation

### R1: Coverage Below 80% Threshold
**Likelihood:** Medium  
**Impact:** Critical (MUST_WORK gate fails)  
**Mitigation:**
- Expand semantic primitive set during Phase 2 if initial coverage low
- Allow multi-primitive assignments (one error → multiple primitives)
- Document tool-specific edge cases as acceptable unmapped categories

### R2: Verifier Installation Complexity
**Likelihood:** High  
**Impact:** Medium (delays Phase 4 execution)  
**Mitigation:**
- Use Docker containers with pre-installed verifiers
- Pin exact verifier versions in requirements
- Provide installation scripts for Ubuntu/Debian

### R3: Documentation Parsing Failures
**Likelihood:** Low  
**Impact:** Medium (incomplete error catalog)  
**Mitigation:**
- Fallback to manual curation if web scraping fails
- Supplement documentation with empirical error collection
- Maintain backup local copies of documentation snapshots

---

## Timeline & Dependencies

### Phase Breakdown
- **Week 5-6:** Error category extraction (FR-1)
- **Week 7-8:** Semantic primitive identification (FR-2)
- **Week 9-10:** Mapping construction (FR-3)
- **Week 11:** Coverage computation + validation (FR-4)
- **Week 12:** Expert review + documentation finalization

### Dependencies
- **Prerequisite:** Phase 2C experiment design (COMPLETED)
- **Enables:** H-M3 (Semantic Normalization Transfer) - requires taxonomy from H-E2
- **Parallel:** H-E1 (independent, can execute concurrently)

---

## Appendix: Reference Resources

**Official Documentation:**
1. Frama-C WP VC API: https://frama-c.com/api/frama-c-wp/Wp/VC/index.html
2. Dafny Error Docs: https://dafny.org/v3.12.0/HowToFAQ/Errors
3. Why3 Model_parser: https://why3.org/api/Model_parser.html

**Academic References:**
1. joscoh/why3-semantics (Coq formalization): https://github.com/joscoh/why3-semantics
2. FormalRx Error Taxonomy: https://arxiv.org/html/2607.04655
3. Translation Validation Papers: Dafny→Boogie, Viper→Boogie, witness validation

**Benchmark Programs:**
1. Frama-C examples repository
2. Juliet Test Suite (NIST verified subset)
3. Why3 gallery examples

---

**Status:** DRAFT  
**Next Step:** Architecture design (03_architecture.md)  
**Owner:** Phase 3 Implementation Planning Agent  
