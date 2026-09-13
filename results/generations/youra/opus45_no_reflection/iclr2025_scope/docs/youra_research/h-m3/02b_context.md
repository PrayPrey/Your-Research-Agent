# Phase 2B Context: H-M3

**Hypothesis ID:** H-M3
**Type:** MECHANISM
**Statement:** Token-level achieves superior F1 retention at extrapolated lengths with significant interaction effect

## Gate Condition
- **Type:** MUST_WORK
- **Pass Condition:** Interaction term (Objective × Length) significant at p<0.05
- **Fail Action:** Document as negative result

## Prerequisites
- H-M2: VALIDATED (CAB drift slope 5x lower than MOHAWK)

## Previous Hypothesis Results

### H-M2 Validation (Prerequisite)
- **mohawk_slope:** 0.00452495
- **cab_slope:** 0.00090506
- **slope_ratio:** 5.0
- **cab_drift_ratio:** 1.34
- **gate_pass:** true
- **note:** CAB drift slope 5x lower than MOHAWK - token-level distillation more stable across lengths

## Experimental Setup (from Phase 2B)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | LongBench (standard) | Standard long-context NLU benchmark with single-doc QA tasks supporting 4K-32K evaluation |
| **Model** | Phi-Mamba | Standard target architecture from MOHAWK with modifications enabling fair objective comparison |

### Dataset Details
- Source: THUDM/LongBench (HuggingFace)
- Path: huggingface:THUDM/LongBench

### Model Details
- Type: Modified Mamba-2 (SSM)
- Source: goombalab/phi-mamba + wph6/CAB (custom integration)

## Verification Protocol
1. Train 6 models: 2 objectives × 3 lengths (1.5B tokens each)
2. Evaluate each on LongBench single-doc QA at matching length
3. Compute F1 retention ratios
4. Run 2×3 ANOVA with interaction term
5. Test predictions P1 (4K), P2 (16K), P3 (32K)

## Success Criteria (PoC)
- **Primary:** Interaction term (Objective × Length) significant at p<0.05
- **Secondary:** P2 and P3 effect sizes match predictions (≥3 and ≥5 F1 points)

## Variables
- **Independent:** Distillation objective × Sequence length (2×3 factorial)
- **Dependent:** F1 retention ratio (student F1 / teacher F1)
- **Controlled:** Training budget (1.5B tokens), architecture, data

## Continuation Context
Building on H-M2's finding that CAB drift slope is 5x lower than MOHAWK, H-M3 tests whether this representation stability translates to downstream F1 performance advantage at extrapolated lengths.
