# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-10
**Main Hypothesis:** Contamination-Performance Transfer Function
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
A statistically significant positive correlation (Spearman r > 0.2) exists between cumulative 13-gram benchmark overlap percentage and benchmark score inflation residual across Pythia model checkpoints.

### Type
EXISTENCE

### Rationale
This existence hypothesis validates the fundamental premise that contamination produces measurable performance inflation. Without demonstrating this correlation, the entire transfer function approach lacks empirical foundation.

---

## Verification Protocol

### Conceptual Test
1. Extract 13-grams from MMLU/ARC/HellaSwag/WinoGrande test sets (full standard test splits, ~15K+ samples total).
2. Compute cumulative overlap for each of 72 Pythia checkpoints (6 sizes × 12 checkpoints).
3. Evaluate all checkpoints using lm-eval-harness with standard settings.
4. Fit capability regression using WikiText-103 perplexity, compute inflation residuals.
5. Calculate Spearman correlation between contamination and inflation.

### Success Criteria
- Primary: Spearman r > 0.5 with p < 0.05
- Secondary: r > 0.2 establishes existence (minimum threshold)

### Variables (if applicable)
- **Independent Variable:** Cumulative 13-gram benchmark overlap (%)
- **Dependent Variable:** Benchmark score inflation residual (observed - predicted)
- **Controlled Variables:** Model architecture (Pythia), corpus (The Pile), evaluation protocol

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** The Pile + Standard Benchmarks (MMLU, ARC, HellaSwag, WinoGrande)
- **Type:** standard
- **Source:** EleutherAI (The Pile), HuggingFace (benchmarks)
- **Path:** pile-corpus + lm-eval-harness tasks
- **Hypothesis Fit:** Documented corpus enables ground-truth contamination measurement

### Selected Model
- **Name:** Pythia Model Family
- **Type:** decoder-only transformer
- **Source:** EleutherAI/pythia-*
- **Sizes:** 410M, 1B, 1.4B, 2.8B, 6.9B, 12B (6 sizes × 12 checkpoints = 72 data points)
- **Hypothesis Fit:** Multiple sizes, documented training, checkpoint availability

---

## Baseline & Comparison Targets

> **Note:** For EXISTENCE hypothesis, baseline context provides expected effect sizes.

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| N-gram decontamination (13-gram) | Removes verbatim overlaps | GPT-3 training, various benchmarks |
| TED (Test Data Deviation) | Distribution-based detection | Multiple LLM benchmarks |
| Kernel Divergence Score | Dataset-level detection | LLM benchmarks |

### Baseline Performance
Prior work (Yang et al., 2023): 8-18% overlap in RedPajama

### Gap Analysis
Existing methods detect contamination presence but do not quantify performance impact. No contamination-to-inflation transfer function exists.

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:** ABANDON (no correlation means no transfer function possible)

**Phase Assignment:** Phase 1: Foundation

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the foundation. All mechanism hypotheses (H-M1 through H-M4) depend on H-E1 passing.

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

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
1. Search for implementation patterns (Archon, Exa MCP)
2. Design concrete experiment specification (Level 1.5)
3. Output: h-e1/02c_experiment_brief.md

---

*Optimized for single-hypothesis experiment design*
