# Phase 2B: Verification Plan

**Generated:** 2026-08-28T22:30:00Z  
**Hypothesis ID:** H-LoRA-SSM-Transfer-v1  
**Main Hypothesis:** LoRA rank-8 on Mamba-130M input/output projections achieves ≥95% of GPT-2-117M LoRA accuracy on GLUE tasks

---

## Overview

This verification plan decomposes the main hypothesis into testable sub-hypotheses with clear dependencies and gate conditions. Phase 5 handles the final baseline comparison (DETERMINES_SUCCESS gate).

---

## Sub-Hypotheses

### H-E1: Checkpoint Verification (EXISTENCE)

**Statement:** Mamba-130M pretrained checkpoint exists, loads correctly, and produces non-random outputs on GLUE zero-shot evaluation.

**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Prerequisites:** None  
**Status:** READY

**Success Criteria:**
- Checkpoint downloads without errors
- Model loads into memory (<16GB GPU)
- Zero-shot accuracy on GLUE > random baseline (MNLI: >33%, QQP: >50%, SST-2: >50%)

**Failure Impact:** Blocks entire pipeline - no Mamba experiments possible without checkpoint.

**Mitigation:** If unavailable, identify alternative state-space model checkpoint or pivot to different architecture.

---

### H-M1: Mamba LoRA Mechanism (MECHANISM)

**Statement:** LoRA adaptation applied to Mamba input/output projections (frozen A,B,C matrices) produces statistically significant improvement over zero-shot baseline (p<0.05, 3 seeds).

**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Prerequisites:** [H-E1]  
**Status:** NOT_STARTED (awaiting H-E1)

**Success Criteria:**
- LoRA training converges without errors
- Adapted model accuracy > zero-shot baseline on all 3 GLUE tasks
- Paired t-test p-value < 0.05 (across 3 seeds)
- Trainable parameter count logged correctly

**Failure Impact:** If MUST_WORK fails → LoRA fundamentally incompatible with Mamba architecture → Route to Phase 0 for new hypothesis.

**Mitigation:** Test minimal LoRA wrapper first. Verify gradient flow through adapted layers.

---

### H-M2: GPT-2 LoRA Baseline (MECHANISM)

**Statement:** GPT-2 LoRA baseline establishes upper bound - GPT-2 LoRA significantly outperforms GPT-2 zero-shot (p<0.05, 3 seeds) on GLUE tasks.

**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Prerequisites:** None  
**Status:** READY

**Success Criteria:**
- GPT-2 LoRA training converges
- LoRA accuracy > zero-shot baseline on all 3 GLUE tasks
- Paired t-test p-value < 0.05 (across 3 seeds)
- Results align with published LoRA benchmarks

**Failure Impact:** If MUST_WORK fails → GPT-2 baseline unreliable → Cannot establish comparison target → Route to Phase 0.

**Mitigation:** Use standard HuggingFace PEFT library. Verify hyperparameters match literature.

---

### Phase 5: Baseline Comparison (DETERMINES_SUCCESS)

**Statement:** Mamba LoRA achieves ≥95% of GPT-2 LoRA average accuracy on GLUE tasks, with parameter count within 10% (ratio 0.9-1.1).

**Gate:** DETERMINES_SUCCESS  
**Prerequisites:** [H-M1, H-M2]  
**Handled by:** Phase 5 workflow

**Success Criteria (PASS):**
- Performance ratio: Mamba LoRA / GPT-2 LoRA ≥ 0.95
- Parameter ratio: 0.9 ≤ (Mamba params / GPT-2 params) ≤ 1.1
- Statistical significance maintained

**Partial Criteria (PARTIAL):**
- Performance ratio: 0.85 ≤ ratio < 0.95 → Mixed results, deeper analysis needed
- Performance ratio: ratio < 0.85 → Approach fundamentally inferior to baseline → Route to Phase 0

**Routing:**
- PASS → Phase 6 (paper writing)
- PARTIAL → Phase 0 (new hypothesis needed - architecture-specific adaptation required)

---

## Dependency Graph (DAG)

```
H-E1 (checkpoint) ──→ H-M1 (Mamba LoRA)
                              ↓
H-M2 (GPT-2 LoRA) ──────→ Phase 5 (comparison)
```

**Execution Order:**
1. Parallel: H-E1, H-M2 (independent foundation hypotheses)
2. Sequential: H-M1 (depends on H-E1)
3. Final: Phase 5 (depends on H-M1, H-M2)

---

## Risk Analysis

| Risk | Hypothesis | Likelihood | Impact | Mitigation |
|------|-----------|------------|--------|------------|
| Checkpoint unavailable | H-E1 | Medium | Critical | Verify before Phase 3; identify fallback SSM |
| LoRA incompatible with Mamba | H-M1 | Low | High | Test minimal wrapper; verify gradient flow |
| Zero-shot baseline collapse | H-E1, H-M1, H-M2 | Low | Medium | Verify pretrained quality first |
| Performance gap (Mamba < GPT-2) | Phase 5 | Medium | Expected | Guides future work on architecture-specific adaptation |

---

## Timeline Estimate

| Phase | Duration | Hypotheses | Notes |
|-------|----------|------------|-------|
| Phase 2C | 2 days | H-E1, H-M1, H-M2 | Experiment design per hypothesis |
| Phase 3 | 3 days | H-E1, H-M1, H-M2 | PRD/Architecture/PRP generation |
| Phase 4 | 5 days | H-E1, H-M1, H-M2 | PoC validation (MUST_WORK gates) |
| Phase 5 | 2 days | Baseline comparison | Full experimental runs, statistical analysis |

**Total:** 12 days (assumes no major blockers)

---

## Controlled Variables

From Phase 2A refinement:

**Dataset:** GLUE (MNLI, QQP, SST-2)  
**Models:** GPT-2-117M, Mamba-130M  
**Optimizer:** AdamW  
**Hyperparameters:**
- Learning rate: 3e-4
- Batch size: 32
- LoRA rank: 8
- LoRA alpha: 16
- LoRA dropout: 0.1
- Random seeds: [42, 1337, 2024]

**Adaptation Strategy:**
- GPT-2: LoRA on Q/K/V attention projections (frozen attention weights)
- Mamba: LoRA on input/output projections (frozen A,B,C state-space matrices)

---

## Success Thresholds

**Phase 4 (PoC Validation):**
- All MUST_WORK gates must pass (H-E1, H-M1, H-M2)
- Statistical significance p<0.05 for adapted > zero-shot

**Phase 5 (Baseline Comparison):**
- PASS: Mamba ≥95% of GPT-2 LoRA performance
- PARTIAL: 85% ≤ Mamba < 95% of GPT-2 → Further analysis needed
- FAIL: Mamba <85% of GPT-2 → Architecture fundamentally incompatible

---

## Next Steps

1. **Phase 2C:** Design experiments for H-E1, H-M1, H-M2
2. **Phase 3:** Generate PRD, Architecture, PRP documents; create Archon tasks
3. **Phase 4:** Execute PoC validation via Coder-Validator loop
4. **Phase 5:** Run full baseline comparison with statistical analysis

---

**Status:** READY FOR PHASE 2C  
**Sub-Hypotheses:** 3 (H-E1, H-M1, H-M2)  
**Phase 5 Gate:** DETERMINES_SUCCESS (baseline comparison)
