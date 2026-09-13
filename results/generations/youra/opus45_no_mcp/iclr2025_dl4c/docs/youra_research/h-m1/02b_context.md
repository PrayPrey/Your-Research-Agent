# Hypothesis Context: H-M1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-19
**Main Hypothesis:** Error-Type-Gated Fine-Grained Execution Feedback
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under RLTF's fine-grained reward scheme, if an error occurs, then reward penalties are applied specifically to tokens at the error line location via traceback parsing.

### Type
MECHANISM

### Rationale
This validates the first causal step - that fine-grained feedback actually localizes credit to specific tokens. Without this, gating would have no mechanism to operate on.

---

## Verification Protocol

### Conceptual Test
1. Generate failing code samples that produce errors with tracebacks
2. Apply RLTF fine-grained reward calculation
3. Compute gradients and measure concentration at error-line tokens
4. Verify >80% of penalty gradient concentrates within ±2 lines of traceback location
5. Document any systematic localization failures

### Success Criteria
- Primary: Gradient concentration at error-line > gradient_other_lines
- Secondary: >80% penalty within ±2 lines

### Variables (if applicable)
- **Independent Variable:** error occurrence with traceback
- **Dependent Variable:** gradient distribution across tokens
- **Controlled Variables:** reward scheme (RLTF Eq 4-5), model architecture

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** APPS
- **Type:** standard
- **Source:** https://github.com/hendrycks/apps
- **Path:** datasets/apps/
- **Hypothesis Fit:** Standard code RL benchmark with error tracebacks

### Selected Model
- **Name:** CodeT5-large
- **Type:** encoder-decoder
- **Source:** Salesforce/codet5-large
- **Hypothesis Fit:** Same as RLTF baseline; 770M parameters

---

## Baseline & Comparison Targets

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| RLTF combined (coarse+fine+adaptive) | ~35% pass@1 | APPS |
| CodeRL | ~30% pass@1 | APPS |

### Baseline Performance
RLTF combined achieves ~35% pass@1 on APPS

### Gap Analysis
H-M1 tests mechanism, not performance improvement. Success = gradient concentration at error lines.

---

## Dependencies and Gate Conditions

### Prerequisites
- H-E1: Error-Type Gating Improves Sample Efficiency (VALIDATED, PASS)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:** STOP, localization broken

**Phase Assignment:** Phase 2 (Mechanisms)

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
H-M1 is the first mechanism hypothesis. It validates that fine-grained feedback actually targets error-line tokens - the foundation for understanding why gating works. H-E1 (existence) already proved the efficiency improvement exists; H-M1 explains the first causal step.

### Previous Hypothesis Results (H-E1)
- **Status:** PASS
- **Key Findings:**
  - Error-type gating mechanism correctly classifies U_line vs U_ignore errors
  - Gating activation rate: ~13% (within expected 10-15% range)
  - Fine-gated condition showed improvement over fine-always
  - Unit tests confirm correct error classification and reward computation

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
