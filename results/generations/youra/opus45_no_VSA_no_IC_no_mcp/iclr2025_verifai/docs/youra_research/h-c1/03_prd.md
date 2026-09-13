# PRD: h-c1 Format × Model Scale Interaction Experiment

**Version:** 1.0
**Date:** 2026-08-28
**Hypothesis:** h-c1 (CONDITION)
**Gate:** SHOULD_WORK
**Prerequisite:** h-e1 (VALIDATED)

---

## 1. Executive Summary

This experiment tests whether structured error format benefits are inversely proportional to model scale. We predict significant Format × Model Scale interaction with effect sizes: CodeLlama-7B > CodeLlama-34B > GPT-4.

---

## 2. Problem Statement

h-e1 established that structured format improves repair success. h-c1 investigates whether this benefit varies by model capability—specifically testing if smaller models gain more from structured representation.

---

## 3. Goals

### Primary Goal
Demonstrate significant Format × Model Scale interaction effect (p < 0.05, η² > 0.01)

### Secondary Goals
1. Confirm monotonic effect ordering (7B > 34B > GPT-4)
2. Quantify simple effects per model with 95% CI
3. Generate publication-ready interaction plots

---

## 4. Scope

### In Scope
- 2×3 factorial experiment (Format × Model Scale)
- Full EvalPlus test sets (HumanEval+ 164, MBPP+ 378)
- Two-way ANOVA with interaction term
- Effect size analysis (η², Cohen's d)
- Planned contrasts for monotonic pattern

### Out of Scope
- Additional model scales beyond 7B/34B/GPT-4
- New error format variants
- Training or fine-tuning

---

## 5. Success Criteria

| Metric | Threshold |
|--------|-----------|
| Interaction p-value | < 0.05 |
| Interaction η² | > 0.01 |
| Effect ordering | Effect_7B > Effect_34B > Effect_GPT4 |

**Pass:** Significant interaction AND correct ordering

---

## 6. User Stories

### US-1: Data Collection Extension
As a researcher, I need to collect repair results across 3 model scales so that I can compare format effects.

**Acceptance Criteria:**
- Run repairs on CodeLlama-7B, CodeLlama-34B, GPT-4
- Both Raw and Structured format per model
- Cache all results for reproducibility

### US-2: Interaction Analysis
As a researcher, I need proper factorial ANOVA implementation so that I can test the interaction hypothesis.

**Acceptance Criteria:**
- Two-way ANOVA with Type III SS
- Handle unequal cell sizes
- Report F-statistics and p-values

### US-3: Effect Size Quantification
As a researcher, I need effect size metrics per model so that I can confirm the ordering pattern.

**Acceptance Criteria:**
- Compute simple effects (Structured - Raw) per model
- Calculate Cohen's d per contrast
- Generate 95% confidence intervals

### US-4: Visualization
As a researcher, I need interaction plots so that I can communicate findings.

**Acceptance Criteria:**
- Format × Scale interaction plot
- Error bars showing 95% CI
- Publication-ready formatting

---

## 7. Technical Requirements

### TR-1: Reuse h-e1 Infrastructure
- StructuredError parser and formatters
- Self-repair loop implementation
- Model inference wrappers
- EvalPlus dataset loading

### TR-2: New Statistical Module
- Two-way ANOVA implementation
- Effect size calculations
- Planned contrast testing
- Multiple comparison correction (BH-FDR)

### TR-3: Multi-Model Orchestration
- Sequential or parallel model runs
- Consistent prompt formatting
- API rate limiting for GPT-4

---

## 8. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| h-e1 infrastructure | VALIDATED | Reuse all components |
| scipy.stats | Available | For ANOVA |
| statsmodels | Available | For contrast analysis |
| matplotlib/seaborn | Available | For visualization |

---

## 9. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low GPT-4 failure count | Medium | Pool HumanEval+ and MBPP+ |
| Unequal cells | Low | Type III SS handles this |
| API costs | Medium | Cache aggressively |

---

## 10. Timeline

| Phase | Duration |
|-------|----------|
| Implementation | 1 day |
| Data collection | 2 days |
| Analysis | 0.5 day |
| **Total** | 3.5 days |

---

*Generated for h-c1 Phase 3*
