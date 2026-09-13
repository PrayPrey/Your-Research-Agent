---
workflow: phase2b-planning
hypothesis_id: h-c1
parent_hypothesis: h-verifierteacher-v1
archon_project_id: 6b1361ed-02e6-4b99-ab72-78b79a4178ab
source: /workspace/TEST_verifai/docs/youra_research/02b_verification_plan.md
generated_at: 2026-07-11T05:18:00Z
---

# Phase 2B Context: H-C1 Hypothesis Specification

**Hypothesis ID**: h-c1  
**Type**: Control Condition  
**Gate**: MUST_WORK  
**Status**: NOT_STARTED  
**Archon Task ID**: e119be40-86f5-4403-89cf-91afc1017079

---

## Hypothesis Statement

**H-C1: Compute-Matched Control**

Under compute-matched budgets (equal tokens + verifier time), iterative feedback outperforms single-shot self-consistency sampling by ≥10pp in proof discharge rate

---

## Rationale & Importance

**Gate Type**: MUST_WORK  
**Rationale**: Critical control - ensures observed gains from feedback signal, not just more sampling  
**Prerequisites**: H-M1 (Information Gradient hypothesis)

This is a **critical control hypothesis** that validates whether the gains from iterative feedback are truly due to the **information content** of feedback rather than simply **more compute budget**. Without this control, critics could argue that any performance gain is just from spending more tokens/time, not from feedback quality.

---

## Success Criteria

1. **Primary**: Iterative feedback outperforms single-shot self-consistency by ≥10pp in proof discharge rate
2. **Budget Matching**: Token and verifier time budgets within ±10% tolerance
3. **Statistical Significance**: p < 0.05 (paired t-test or equivalent)

---

## Failure Conditions

1. Single-shot matches or exceeds iterative performance
2. Budget mismatch invalidates comparison
3. No significant difference (feedback has no value beyond compute)

---

## Experiment Sketch

Budget-constrained comparison with rigorous token + verifier time tracking:
- **Baseline 1 (Iterative)**: N iterations with feedback
- **Baseline 2 (Single-shot)**: N×M samples with self-consistency selection
- **Compute Matching**: Total tokens and verifier time equalized across baselines

---

## Dialectical Analysis

**Thesis**: Iterative feedback outperforms single-shot sampling under equal compute

**Antithesis**: More diverse samples may explore specification space better than sequential refinement

**Synthesis**: Iterative feedback provides guided search via verifier supervision, while single-shot is unguided exploration - both have value, but feedback should outperform when verifier signals are informative

**Resolution Strategy**: Compute-match rigorously (tokens + verifier time), report both strict and ±10% tolerance

---

## Dependency Graph Position

```
H-E1 → H-M1 → H-C1
```

**Prerequisites**:
- H-M1 (Information Gradient) must be VALIDATED before H-C1 can execute

**Parallel Opportunities**:
- H-C1 and H-C2 can execute in parallel (both depend only on H-M1)
- H-M3 is independent in its dependencies

**Wave Assignment**: Wave 3 (Integration phase)

---

## Timeline Estimate

- **Phase 3 (Planning)**: 2 weeks
- **Phase 4 (Implementation)**: 6 weeks
  - Dataset preparation: 2 weeks
  - Baseline 1 implementation: 2 weeks
  - Baseline 2 + evaluation: 2 weeks
- **Phase 5 (Baseline Adaptation)**: 1 week
- **Total**: 9 weeks

---

## Risk Factors

1. **Compute matching imperfection**: Token/time variance across programs
2. **Selection strategy sensitivity**: Best-of-N vs majority voting
3. **Temperature effects**: Sampling diversity vs individual quality
4. **Model stability**: Error introduction rate (per Liu & Meng 2024)

---

## References to Main Verification Plan

This context document is extracted from:
`/workspace/TEST_verifai/docs/youra_research/02b_verification_plan.md`

For full details on:
- All 7 sub-hypotheses
- Complete dependency graph
- Phase 2B methodology
- Archon project structure

Refer to the main verification plan document.

---

**END OF H-C1 PHASE 2B CONTEXT**
