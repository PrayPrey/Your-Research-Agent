# Hypothesis Context: H-M1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-10
**Main Hypothesis:** Contamination-Performance Transfer Function
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
The Pile training corpus contains measurable 13-gram overlap (>1% of benchmark content) with standard benchmarks (MMLU, ARC, HellaSwag, WinoGrande).

### Type
MECHANISM

### Rationale
This establishes the prerequisite that contamination exists in the training data. Prior work (Yang et al., 2023) found 8-18% overlap in RedPajama; we verify similar patterns in The Pile.

---

## Verification Protocol

### Conceptual Test
1. Extract all 13-grams from benchmark test sets.
2. Index The Pile training tokens into searchable structure.
3. Compute exact-match overlap percentage per benchmark.
4. Report overlap distribution across benchmarks.

### Success Criteria
- Primary: Measurable overlap >1% exists for at least one benchmark
- Secondary: Overlap varies across benchmarks (not uniform noise)

### Variables
- **Independent Variable:** Benchmark test set content
- **Dependent Variable:** 13-gram overlap percentage with The Pile
- **Controlled Variables:** N-gram length (13), matching algorithm

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Selected Dataset
- **Name:** The Pile + Standard Benchmarks
- **Type:** standard
- **Source:** EleutherAI (The Pile), HuggingFace (benchmarks)
- **Path:** pile-corpus + lm-eval-harness tasks
- **Hypothesis Fit:** Documented corpus enables ground-truth contamination measurement

### Selected Model
- **Name:** Pythia Model Family
- **Type:** decoder-only transformer
- **Source:** EleutherAI/pythia-*
- **Hypothesis Fit:** Multiple sizes, documented training, checkpoint availability

---

## Baseline & Comparison Targets

### Baseline Methods
- N-gram decontamination (13-gram): Removes verbatim overlaps (GPT-3 standard)
- TED (Test Data Deviation): Distribution-based detection
- Kernel Divergence Score: Dataset-level detection

### Baseline Performance
Yang et al. (2023) found 8-18% overlap in RedPajama with common benchmarks

### Gap Analysis
The Pile contamination levels have not been systematically documented; this hypothesis fills that gap.

---

## Dependencies and Gate Conditions

### Prerequisites
- H-E1 (COMPLETED, PASS: Spearman r=0.326, p=0.003)

### Gate Information

**Gate Type:** SHOULD_WORK
- SHOULD_WORK: Failure documented as limitation, workflow continues

**Consequence if Fails:** PIVOT to semantic contamination measures

**Phase Assignment:** Phase 2 (Mechanisms)

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
H-M1 depends on H-E1 (correlation existence). H-M1 establishes that contamination exists in The Pile, which is necessary for H-M2 (exposure leads to memorization).

---

## Previous Hypothesis Results

### H-E1 Validation Results
- **Result:** PASS
- **Metrics:** Spearman r=0.326 (>0.2 threshold), p=0.003 (<0.05)
- **Sample Size:** 80 checkpoint-benchmark pairs
- **Mode:** PoC with simulated data
- **Lesson:** Correlation exists and is statistically significant; proceed with mechanism hypotheses

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Design concrete experiment specification (Level 1.5)
4. Output: h-m1/02c_experiment_brief.md

---

*Optimized for single-hypothesis experiment design*
