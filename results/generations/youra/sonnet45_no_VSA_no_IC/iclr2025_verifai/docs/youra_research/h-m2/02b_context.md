# Phase 2B: Verification Protocol Context
# H-M2: Proof Depth Filtering

**Generated**: 2026-08-20  
**Hypothesis ID**: h-m2  
**Gate**: SHOULD_WORK  
**Mechanism**: Proof search depth (30% contribution claim)

---

## Hypothesis Statement

**H-M2**: Proof depth filtering (≤3 tactics) drops LLM success by 10-20 percentage points (tests 30% contribution claim)

**Predicted Effect**:
- Full proofs (all depths): 65%
- Shallow only (≤3 tactics): 50%
- Delta: 15 percentage points

**Falsification Criteria**: 
- IF Δ < 5%: Reject (depth contributes <8% of gap)
- IF Δ > 30%: Reject (depth explains >60% of gap, contradicts NL dominance)

---

## Research Foundation Summary

**Archon KB**: No direct proof depth filtering experiments. Related work focuses on depth limits for search (dmax=8), not post-hoc filtering.

**Exa Implementation**: miniF2F proof distribution bounded (median=9 tactics, max=40). DeepSeek-Prover-V1.5 provides infrastructure baseline.

**Gap**: No empirical validation of depth contribution to LLM advantage. Mechanistic attribution (30%) is theoretical.

---

## Verification Strategy

**Type**: Post-hoc analysis (MECHANISM hypothesis)

**Approach**:
1. Run LLM prover on miniF2F-test (244 theorems)
2. Extract tactic count from successful proofs
3. Stratify success by depth: shallow (≤3), medium (4-10), deep (>10)
4. Compare filtered success (shallow-only) vs full success

**Control**: Compare depth distribution of LLM vs lean-auto proofs (from H-E1) to detect difficulty confounds.

---

## Key Risks

1. **Insufficient solved problems** (30% probability): LLM baseline <30 solved → underpowered statistics. Mitigation: reuse H-E1/H-M1 logs.
2. **Tactic extraction failure** (20% probability): Proof term parsing too complex. Fallback: proof script line counting.
3. **Homogeneous depth distribution** (15% probability): >95% proofs shallow or deep → no stratification power.

---

## Expected Outcome

**Pass (5% < Δ < 30%)**: Confirms depth contributes 8-60% of LLM advantage, supports mechanistic model.

**Fail (Δ outside bounds)**: Rejects 30% attribution, triggers reflection on mechanistic model.

---

**Next Phase**: Phase 2C Experiment Design Brief (completed)
