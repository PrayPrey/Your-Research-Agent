# Phase 2B Context: Hypothesis h-e1

**Generated:** 2026-05-11
**Source:** 02b_verification_plan.md (Auto-extracted)

---

## Hypothesis Information

### Statement
Under conditions where Constitutional AI or system-prompted LLMs are evaluated across multiple compliance strength levels (λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0}), if base model capability is held frozen while policy-layer rules are varied, then base capability metrics (MMLU, HumanEval) will remain invariant (ICC > 0.95, ANOVA p > 0.05), because the architectural separation between base weights and policy layer allows compliance modulation without capability degradation.

### Type
EXISTENCE

### Gate
- **Type:** MUST_WORK
- **Condition:** (ICC > 0.95) AND (ANOVA p > 0.05) AND (Cohen's f < 0.10)
- **If Fail:** ABORT entire chain → Route to Phase 0 for architecture re-selection

### Prerequisites
None (foundational validation)

---

## Experimental Setup (From Phase 2B Section 1.3)

### Dataset
- **Primary:** MMLU (full 57-subject test, ~14k questions)
- **Secondary:** HumanEval (164 coding problems)
- **Type:** standard
- **Purpose:** Base capability measurement across compliance conditions

### Model
- **Primary:** Constitutional AI (Claude) or GPT-4 with system prompts
- **Architecture Feature:** Policy-layer separation from base weights
- **Key Requirement:** Frozen base weights, modulated policy layer

---

## Variables

### Independent Variable (IV)
Policy-layer compliance strength (λ parameter: 0.2, 0.4, 0.6, 0.8, 1.0)

### Dependent Variables (DV)
- MMLU accuracy (across 57 subjects)
- HumanEval pass@1

### Controlled Variables (CV)
- Model architecture (frozen base weights)
- Evaluation prompts (identical across conditions)
- Temperature (fixed at 0.0 for deterministic evaluation)

---

## Success Criteria

1. **ICC (Intraclass Correlation Coefficient) > 0.95** across all λ conditions
2. **One-way ANOVA p > 0.05** (no significant variation in MMLU/HumanEval)
3. **Cohen's f < 0.10** (negligible effect of λ on capability)

---

## Verification Protocol

1. Select Constitutional AI (Claude) or GPT-4 with system prompts architecture
2. Implement 5 compliance conditions (λ = 0.2, 0.4, 0.6, 0.8, 1.0) via rule strength or prompt intensity modulation
3. Freeze base model weights (no fine-tuning between conditions)
4. Evaluate each condition on MMLU (full 57-subject test, ~14k questions) and HumanEval (164 coding problems)
5. Compute ICC (two-way mixed effects, absolute agreement) across conditions
6. Perform one-way ANOVA with Bonferroni correction (α = 0.05)
7. Calculate Cohen's f effect size to quantify practical significance
8. Pass Gate: (ICC > 0.95) AND (ANOVA p > 0.05) AND (Cohen's f < 0.10)

---

## Baseline & Comparison Targets (From Phase 2B Section 1.4)

### Baseline Methods
| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| Standard RLHF alignment | Improves AI task accuracy but HOR effects unmeasured | Various (HHH, TruthfulQA, etc.) | Unidirectional evaluation. Doesn't measure human oversight retention or temporal dynamics. |
| Constitutional AI | Provides value alignment through constitutional rules | Anthropic internal benchmarks | Evaluates AI alignment quality, not bidirectional stability. No HOR measurement or temporal dynamics model. |

---

## Dependencies

**Blocks:** h-m1, h-m2, h-m3, h-m4
**Blocked By:** None

---

*Auto-generated from 02b_verification_plan.md Section 2.2 (H-E1 specification)*
