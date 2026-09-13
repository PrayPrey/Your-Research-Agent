# Verification Plan: Constraint-Satisfiability Verification for DL Hypothesis Testability

**Date:** 2026-08-25
**Hypothesis ID:** H-ConstraintSatChecker-v1
**Confidence:** 0.80
**Total Hypotheses:** 6

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under constraint-driven deep learning research contexts (existing datasets/benchmarks only, no human evaluation), if a formal constraint-satisfiability verification system with an extensible knowledge base is used, then researchers can accurately classify hypotheses as testable/not-testable (>75% accuracy against experimental outcomes), because the system performs formal verification of (Dataset, Benchmark, Metric) triple existence and flags known confound patterns.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in testability classification accuracy between the constraint-satisfiability system and random classification (50% baseline), when validated against actual experimental outcomes.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Papers With Code Catalog (Jan 2026 snapshot) (standard) | Provides comprehensive inventory of existing datasets and benchmarks, which is the core resource the hypothesis claims to leverage |
| **Model** | Formal Constraint-Satisfiability Verifier | Hypothesis proposes a formal verification approach, not a learned model; the 'model' is the logical rule system that checks (D,B,M) existence |

**Dataset Details:**
- Source: https://paperswithcode.com/
- Path: Scraped and stored as structured KB (YAML/JSON)

**Model Details:**
- Type: symbolic reasoning system
- Source: Custom implementation (no pre-trained model required)

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Expert Judgment (3-person majority) | ~80-85% inter-rater reliability | Same 100 hypotheses | Circular: expert agreement is not ground truth. Experts may share biases. |
| Random Classification | 50% accuracy | Same 100 hypotheses | No reasoning; pure baseline |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Papers With Code catalog (Jan 2026) is sufficiently complete | Widely-used aggregator covering major DL benchmarks | System misses valid testability mappings (false negatives) |
| A2 | Experimental outcomes (p < 0.05) are valid ground truth | Statistical significance is objective measure | Validation metric unreliable |
| A3 | Confound patterns generalize cross-domain | Tokenizer-size (NLP) → resolution-architecture (vision) | Confound flagging domain-specific only |
| A4 | Non-experts learn (D,B,M) format in <10 min | YAML/JSON schema with examples | KB extensibility fails |
| A5 | 20 hypothesis sample has sufficient power | Effect size ~0.5, power ~0.80 at alpha=0.05 | Validation study underpowered |

### 1.6 Research Gap & Novelty

**Gap Addressed:** Automated Evaluation Methodology Taxonomy Gap (Gap 2)

**Key Innovation:** Post-hoc experimental validation of meta-research tools (not circular expert agreement). Three-fold innovation:

1. **Post-Hoc Experimental Validation**: Validates system predictions by running actual experiments (p < 0.05 results = ground truth). No prior work in meta-research tools uses this standard.
2. **Extensible Knowledge Base**: Users can add new (D,B,M) triples in <10 minutes, making the system self-improving.
3. **Cross-Domain Confound Pattern Detection**: Confounds from NLP transfer to vision.

**Differentiation:**
- Papers With Code: Static listing vs. formal verification with testability classification
- Expert reviews: Circular agreement vs. post-hoc experimental ground truth
- Meta-analyses: Retrospective synthesis vs. prospective testability prediction

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | MUST_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | Mechanism | MUST_WORK | H-M3 | NOT_STARTED |
| H-C1 | Condition | SHOULD_WORK | H-M4 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

**H-E1: Knowledge Base Constructability**

**Statement**: Under constraint-driven DL research contexts (existing datasets/benchmarks only), if Papers With Code catalog (Jan 2026) is scraped and structured, then a (Dataset, Benchmark, Metric) triple knowledge base covering >80% of well-known DL datasets/benchmarks can be constructed, because the catalog provides comprehensive metadata on dataset-benchmark-metric relationships.

**Rationale**: KB construction is the foundation of the entire system. If the KB cannot capture sufficient coverage of real DL resources, the system's testability classifications become unreliable (false negatives dominate).

**Variables** (from Phase 2A):
- Independent: KB extraction method (automated scraping)
- Dependent: Coverage percentage (% of well-known datasets/benchmarks captured)
- Controlled: Catalog snapshot date (Jan 2026), KB structure (YAML/JSON)

**Verification Protocol**:
1. Scrape Papers With Code catalog (Jan 2026 snapshot) and extract (D,B,M) triples
2. Compare extracted entries against ground-truth list of 50 well-known datasets (CIFAR-10, ImageNet, GLUE, etc.)
3. Measure coverage: (# entries found in KB) / 50

**Success Criteria** (PoC: Direction-based):
- Primary: Coverage >80% (40/50 well-known datasets present)
- Secondary: Metadata completeness (each entry has D, B, M fields populated)

**Failure Response**:
- IF <80%: EXPLORE catalog alternatives (HuggingFace Datasets, Google Dataset Search)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 1.3 Causal Mechanism Step 1, Section 1.4 Assumption A1

---

**H-M1: KB Extraction Coverage**

**Statement**: Under automated scraping conditions, if KB extraction logic is applied to Papers With Code catalog, then >80% of well-known datasets/benchmarks are captured in the KB, because the catalog's structured format enables reliable automated extraction.

**Rationale**: This is the first causal step. If extraction fails, downstream verification logic has no data to work with.

**Variables**:
- Independent: Extraction logic implementation
- Dependent: Coverage percentage
- Controlled: Catalog snapshot, ground-truth list

**Verification Protocol**:
1. Implement extraction logic (parse HTML/API from Papers With Code)
2. Run extraction on Jan 2026 snapshot
3. Count (D,B,M) triples extracted vs ground-truth list

**Success Criteria**:
- Primary: Extraction captures >80% of ground-truth entries

**Failure Response**:
- IF fails: PIVOT to manual KB curation or alternative catalog sources

**Dependencies**: H-E1

**Source**: Phase 2A Causal Mechanism Step 1

---

**H-M2: Formal Verification Precision**

**Statement**: Under formal constraint-satisfiability verification, if a hypothesis H is evaluated against the KB, then the system produces <25% false positives (marks untestable as testable), because the ∃ (D,B,M) verification logic correctly distinguishes measurable interventions from non-measurable ones.

**Rationale**: Precision is critical. High false positive rate means researchers receive "testable" labels for untestable hypotheses, wasting experimental effort.

**Variables**:
- Independent: Verification logic (∃ (D,B,M) check)
- Dependent: False positive rate
- Controlled: Test set of labeled hypotheses (ground truth: expert-labeled)

**Verification Protocol**:
1. Create test set: 20 hypotheses (10 expert-labeled testable, 10 untestable)
2. Run formal verification on all 20
3. Measure false positives: (# untestable marked testable) / 10

**Success Criteria**:
- Primary: False positive rate <25% (≤2 out of 10 untestable mislabeled)

**Failure Response**:
- IF fails: EXPLORE stricter verification conditions or manual review step

**Dependencies**: H-M1

**Source**: Phase 2A Causal Mechanism Step 2

---

**H-M3: Confound Flagging Precision**

**Statement**: Under confound pattern detection, if the system flags hypotheses with known confounds from literature, then precision >40% is achieved on labeled confound cases, because cross-domain confound patterns (tokenizer-size, resolution-architecture) generalize across DL subfields.

**Rationale**: Confound flagging prevents "technically correct but pragmatically useless" outputs. Low precision creates noise (false alarms reduce trust).

**Variables**:
- Independent: Confound database (NLP/vision patterns)
- Dependent: Flagging precision
- Controlled: Labeled confound test set (15 known-confounded, 15 unconfounded)

**Verification Protocol**:
1. Populate confound database with literature patterns (tokenizer-size ↔ BLEU, resolution ↔ accuracy)
2. Run confound flagging on 30 labeled hypotheses
3. Measure precision: (true positives) / (true positives + false positives)

**Success Criteria**:
- Primary: Precision >40%

**Failure Response**:
- IF fails: PIVOT to domain-specific confound databases (skip cross-domain transfer claim)

**Dependencies**: H-M2

**Source**: Phase 2A Causal Mechanism Step 3

---

**H-M4: Post-Hoc Validation Accuracy**

**Statement**: Under post-hoc experimental validation, if a sample of system-classified "testable" hypotheses are actually tested, then ≥65% yield p < 0.05 results (ground truth confirmation), because the system's (D,B,M) existence checks correctly predict experimental feasibility.

**Rationale**: This is the ultimate ground truth test. If <65% of "testable" classifications result in successful experiments, the system's predictions don't match reality.

**Variables**:
- Independent: System classifications ("testable" vs "not testable")
- Dependent: Experimental success rate (p < 0.05 results)
- Controlled: Random sample size (20 hypotheses)

**Verification Protocol**:
1. System classifies 100 hypotheses as testable/not-testable
2. Randomly sample 20 hypotheses from "testable" group
3. Actually run experiments for each (simplified PoC experiments, not full-scale)
4. Measure: (# experiments with p < 0.05) / 20

**Success Criteria**:
- Primary: Success rate ≥65% (13/20 hypotheses yield significant results)

**Failure Response**:
- IF fails: ABANDON post-hoc validation claim, revert to expert agreement baseline

**Dependencies**: H-M3

**Source**: Phase 2A Causal Mechanism Step 4

---

**H-C1: Benchmark Infrastructure Boundary**

**Statement**: Under domain boundary conditions, if a hypothesis is from a domain without established benchmark infrastructure (novel modalities, emerging applications), then the system correctly classifies it as "not testable" (or flags domain limitation), because the KB contains no matching (D,B,M) triples for that domain.

**Rationale**: Scope boundaries are critical for system usability. If the system fails to detect out-of-scope domains, users receive misleading classifications.

**Variables**:
- Independent: Domain type (benchmark-rich vs benchmark-poor)
- Dependent: Classification accuracy on boundary cases
- Controlled: Test set of 10 boundary hypotheses (5 novel modality, 5 emerging app)

**Verification Protocol**:
1. Curate 10 boundary hypotheses from domains known to lack benchmarks (e.g., olfactory AI, quantum ML)
2. Run system classification
3. Verify: system marks as "not testable" or flags "domain outside scope"

**Success Criteria**:
- Primary: ≥8/10 boundary cases correctly flagged

**Failure Response**:
- IF fails: EXPLORE domain detection heuristics (keyword matching, metadata analysis)

**Dependencies**: H-M4

**Source**: Phase 2A Section 1.5 Scope & Boundaries

<!--
Each hypothesis follows this format:

#### {H-ID}: {Title}

**Type:** {EXISTENCE|MECHANISM|CONDITION|COMPARISON}
**Statement:** {Full Under-If-Then-Because statement}

**Variables:**
- IV: {independent variable}
- DV: {dependent variable}
- CV: {controlled variables}

**Success Criteria:**
- {quantitative threshold 1}
- {quantitative threshold 2}

**Gate:**
- Type: {MUST_WORK|SHOULD_WORK|DETERMINES_SUCCESS}
- If Fail: {consequence}

**Prerequisites:** {list or "None"}

**Verification Protocol:** (100-150 words)
{step-by-step protocol}

---
-->

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | KB coverage >80% | STOP - reassess approach |
| H-M1 | MUST_WORK | Extraction >80% | PIVOT to manual curation |
| H-M2 | MUST_WORK | False positive <25% | EXPLORE stricter logic |
| H-M3 | SHOULD_WORK | Confound precision >40% | Document limitation |
| H-M4 | MUST_WORK | Post-hoc success ≥65% | ABANDON post-hoc claim |
| H-C1 | SHOULD_WORK | Boundary flagging ≥80% | Narrow scope |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 2C: Design | H-E1, H-M1-4, H-C1 | 6 sessions × 8-12 min |
| Phase 3: Planning | 6 implementation plans | 6 sessions × 10-15 min |
| Phase 4: Coding | 6 PoC validations | 6 sessions × 15-25 min |

**Total Duration:** ~3-4 hours (sequential execution)

---
