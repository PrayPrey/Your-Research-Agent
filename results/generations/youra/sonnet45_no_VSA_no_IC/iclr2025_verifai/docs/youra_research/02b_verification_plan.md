# Phase 2B: Verification Planning
# Mechanistic LLM Theorem Proving Baseline

**Generated**: 2026-08-20T03:42:15Z  
**Workflow**: Phase 2B Planning  
**Main Hypothesis ID**: H-MechanisticBaseline-v1  
**Archon Project ID**: 622e5a6a-846d-475f-bd6a-8c6080c60cbb

---

## Executive Summary

Phase 2B decomposed the main hypothesis into **5 sub-hypotheses** with clear dependency structure:
- **3 MUST_WORK gates** (H-E1 foundation, H-M1 core mechanism, H-C1 fairness control)
- **2 SHOULD_WORK gates** (H-M2, H-M3 secondary mechanisms)
- **DAG structure**: H-E1 → {H-M3, H-C1}; H-M1, H-M2 independent
- **Critical path**: H-M1 (2 weeks with pilot requirement)

---

## Main Hypothesis

**ID**: H-MechanisticBaseline-v1  
**Confidence**: 0.78

**Statement**:  
Under miniF2F Olympiad-level formal mathematics benchmark (Lean 4 subset, N≥50 problems), LLM-guided theorem proving (LeanCopilot) achieves significantly higher success rates (predicted: 65% vs 15%, Δ=50 percentage points) compared to pure automated provers (lean-auto), because LLMs exploit three distinct mechanisms:

1. **Natural language hint understanding** (contributing 60% of gap via linguistic pattern matching)
2. **Long-range proof search capability** (contributing 30% via context maintenance across 5-10 tactic steps)
3. **Mathlib corpus pattern matching** (contributing 10% via learned human proof tactic distributions)

**Controlled Variables**:
- Dataset: miniF2F Lean 4 subset (N≥50)
- Prover configurations: lean-auto (hammers), LeanCopilot (LLM-guided)
- Tactic budget: 10 evaluations/problem (equalized via H-E1 measurement)
- Timeout: 300s per problem
- Mathlib version: Lean 4 compatible

---

## Sub-Hypothesis Inventory

### H-E1: lean-auto Baseline Measurement (EXISTENCE)

**Statement**: Pure automated prover (lean-auto) achieves 10-25% baseline success on miniF2F Lean 4 subset

**Gate Type**: MUST_WORK (foundation for all comparisons)

**Prerequisites**: None (independent measurement)

**Status**: READY

**Risk Level**: LOW
- Infrastructure exists (lean-auto, miniF2F Lean 4)
- Straightforward measurement protocol
- Pilot: N=20 problems to verify compatibility

**Archon Task ID**: b1cf534c-c7ff-48e5-a432-1d260d9ec129

---

### H-M1: NL Hint Ablation (MECHANISM)

**Statement**: NL hint removal drops LLM success by 25-35 percentage points (tests 60% contribution claim)

**Gate Type**: MUST_WORK (core mechanism)

**Prerequisites**: None (independent ablation)

**Status**: READY

**Risk Level**: MEDIUM
- **Blocker risk**: NL comment removal may break Lean type-checking
- **Pilot required**: 10 problems to verify ablation feasibility
- **Fallback**: Pivot to informal Mathlib docs removal if comments are semantic

**Predicted Effect**:
- Baseline (with NL): 65%
- Ablated (no NL): 35%
- Delta: 30 percentage points

**Falsification**: IF Δ < 10%, reject 60% contribution claim

**Archon Task ID**: 100fc27f-e71c-43b4-abd4-fd896677e021

---

### H-M2: Proof Depth Filtering (MECHANISM)

**Statement**: Proof depth filtering (≤3 tactics) drops LLM success by 10-20 percentage points (tests 30% contribution)

**Gate Type**: SHOULD_WORK (secondary mechanism)

**Prerequisites**: None (post-hoc filtering)

**Status**: READY

**Risk Level**: LOW
- Post-hoc analysis (no infrastructure changes)
- Tactic count extraction from proof terms
- Fallback: Use proof script length (lines) as proxy

**Predicted Effect**:
- Full proofs: 65%
- Shallow only (≤3 tactics): 50%
- Delta: 15 percentage points

**Falsification**: IF Δ < 5% OR Δ > 30%, reject 30% contribution claim

**Archon Task ID**: 55701338-9bfa-4a75-be8d-e9200139418b

---

### H-M3: Random Mathlib Corpus Sampling (MECHANISM)

**Statement**: Random Mathlib tactic sampling achieves 18-25% success (Δ=5% above lean-auto, tests 10% corpus contribution)

**Gate Type**: SHOULD_WORK (control baseline for triangulation)

**Prerequisites**: [H-E1] (needs lean-auto baseline for comparison)

**Status**: NOT_STARTED (blocked by H-E1)

**Risk Level**: MEDIUM
- **Corpus bias acknowledged**: Random sampling from human-written proofs ≠ uniform distribution
- **Mitigation**: Used as THIRD baseline for triangulation, not sole comparison
- **Custom implementation required**: Random tactic sampler from Mathlib distribution

**Predicted Effect**:
- Random Mathlib: 20%
- lean-auto: 15%
- Delta: 5 percentage points (corpus contribution)

**Falsification**: IF Random < 15% OR > 30%, reject 10% contribution claim

**Archon Task ID**: 85926db5-cf33-4f0b-84d0-0e66b3edc48e

---

### H-C1: Tactic Budget Equalization (CONDITION)

**Statement**: Tactic evaluation budget equalization feasible (10 evaluations measured from lean-auto @ 300s timeout)

**Gate Type**: MUST_WORK (fairness control)

**Prerequisites**: [H-E1] (measures lean-auto tactic count)

**Status**: NOT_STARTED (blocked by H-E1)

**Risk Level**: MEDIUM
- **Variance risk**: If CV > 50%, use median instead of mean
- **Purpose**: Establishes fair comparison metric (tactic evaluations, not wall-clock time)
- **Confound control**: LLM inference latency ≠ search depth difference

**Measurement Protocol**:
1. Run lean-auto on 20 miniF2F problems @ 300s timeout
2. Log tactic evaluation count per problem
3. Compute mean ± std (or median if high variance)
4. Set LLM tactic budget = measured baseline

**Falsification**: IF variance too high (CV > 100%), tactic-count metric is unreliable

**Archon Task ID**: e89da7c1-f178-4f21-8356-f19cc50927d5

---

## Dependency Graph (DAG)

```
         H-E1 (lean-auto baseline)
          /  \
         /    \
        /      \
   H-M3        H-C1
(corpus)    (budget)

   H-M1        H-M2
(NL ablation) (depth)
[independent] [independent]
```

**Parallel Execution Tracks**:
- **Track 1**: H-E1 → H-M3, H-C1 (sequential dependency)
- **Track 2**: H-M1 (independent, requires pilot)
- **Track 3**: H-M2 (independent, post-hoc)

**Critical Path**: H-M1 (2 weeks: 1 week pilot + 1 week full ablation)

---

## Risk Analysis

### Critical Risks (MEDIUM)

**R1: NL Ablation Type-Checking Failure (H-M1)**
- **Probability**: 30%
- **Impact**: HIGH (blocks core mechanism test)
- **Mitigation**: 10-problem pilot BEFORE full experiment
- **Fallback**: Pivot to informal Mathlib docs removal

**R2: Corpus Bias Confound (H-M3)**
- **Probability**: 50%
- **Impact**: MEDIUM (weakens 10% contribution claim)
- **Mitigation**: Three-baseline triangulation (lean-auto, Random, LLM)
- **Acknowledged limitation**: Random sampling from human proofs has bias

**R3: Tactic Budget Variance (H-C1)**
- **Probability**: 40%
- **Impact**: MEDIUM (fairness metric unreliable)
- **Mitigation**: Use median if CV > 50%, report variance in caveat
- **Fallback**: Timeout scaling analysis (10s, 60s, 300s)

### Low Risks

**R4: Lean 4 Subset Size < 50**
- **Probability**: 20%
- **Impact**: MEDIUM (reduces to case study)
- **Mitigation**: Report as pilot, propose full Lean 4 port as future work

**R5: Metadata Unavailable for Stratification**
- **Probability**: 60%
- **Impact**: LOW (aggregate results still valid)
- **Mitigation**: Report aggregate results, acknowledge stratification limitation

---

## Timeline Estimation

### Phase 2C: Experiment Design (5 hypotheses)
- **Duration**: 1 week
- **Parallelization**: All 5 designs in parallel (independent)

### Phase 3: Implementation Planning (5 hypotheses)
- **Duration**: 1 week
- **Parallelization**: All 5 PRD/Architecture specs in parallel

### Phase 4: Coding & PoC Validation
- **H-E1**: 1 week (infrastructure setup + measurement)
- **H-M1**: 2 weeks (1 week pilot + 1 week full ablation) **[CRITICAL PATH]**
- **H-M2**: 3 days (post-hoc filtering implementation)
- **H-M3**: 1 week (blocked by H-E1, custom sampler)
- **H-C1**: 3 days (blocked by H-E1, tactic budget measurement)
- **Total**: 3 weeks (with parallelization)

### Phase 5: Baseline Comparison
- **Duration**: 3 days (statistical analysis, report generation)

### Phase 6: Paper Writing
- **Duration**: 1 week

**Total Pipeline**: 6-7 weeks

---

## Dialectical Analysis

### Thesis
LLMs outperform automated theorem provers via three independent, additive mechanisms:
1. Natural language understanding (60%)
2. Long-range proof search (30%)
3. Mathlib corpus pattern matching (10%)

### Antithesis
Performance gap is NOT due to NL/depth/corpus mechanisms, but rather:
- **Alternative explanation 1**: Generic search heuristics unrelated to NL understanding
- **Alternative explanation 2**: Difficulty confound (LLMs only excel on easier problems)
- **Alternative explanation 3**: Corpus patterns explain ENTIRE gap (not just 10%)

### Synthesis (Falsification Framework)
Controlled ablation study with three-baseline triangulation:

**Global Null**: IF all prover configs achieve ±5% success within difficulty strata, THEN reject entire attribution framework (difficulty alone determines outcome)

**Per-Mechanism Falsification**:
- **NL hypothesis**: Rejected if LLM-no-NL ablation Δ < 10%
- **Depth hypothesis**: Rejected if LLM-shallow Δ < 5% OR Δ > 30%
- **Corpus hypothesis**: Rejected if Random-Mathlib < 15% OR > 30%

**Stratification Test** (if metadata available):
- **NL contribution**: Highest on AMC (informal language), lowest on IMO (formal)
- **Depth contribution**: Highest on IMO (complex proofs), lowest on AMC
- IF no stratum variation, THEN mechanisms are domain-agnostic (weaker claim)

---

## Phase 2C Readiness

**Status**: READY to proceed

**Next Actions**:
1. Begin Phase 2C with H-E1 (READY, no prerequisites)
2. Begin Phase 2C with H-M1 (READY, independent)
3. Begin Phase 2C with H-M2 (READY, independent)
4. H-M3, H-C1 await H-E1 completion (automatic unblocking in hypothesis loop)

**Archon Pipeline**:
- Project ID: 622e5a6a-846d-475f-bd6a-8c6080c60cbb
- 11 phase tasks created (Phase 0 → Phase 6.5.1)
- 5 hypothesis parent tasks created (H-E1 → H-C1)
- All tasks linked via `feature` field for grouping

---

## Appendix: Mechanistic Dissection Table

| Config | Tool | NL Hints | Depth | Corpus | Predicted Success | Δ vs lean-auto | Tests Mechanism |
|--------|------|----------|-------|--------|-------------------|----------------|-----------------|
| **Baseline-Hammer** | lean-auto | N/A | All | Deterministic | 15% | — | Foundation |
| **SOTA-LLM** | LeanCopilot | Yes | All | Learned | 65% | +50% | Full LLM |
| **Ablation-NL** | LeanCopilot | No | All | Learned | 35% | +20% | Tests NL (60% claim) |
| **Ablation-Depth** | LeanCopilot | Yes | ≤3 | Learned | 50% | +35% | Tests depth (30% claim) |
| **Control-Corpus** | Random Mathlib | N/A | All | Random human | 20% | +5% | Tests corpus (10% claim) |

**Attribution Logic**:
- NL contribution = SOTA - Ablation-NL = 65% - 35% = 30% (predicted)
- Depth contribution = SOTA - Ablation-Depth = 65% - 50% = 15% (predicted)
- Corpus contribution = Control - Baseline = 20% - 15% = 5% (predicted)
- Total gap explained = 30% + 15% + 5% = 50% (matches SOTA - Baseline)

---

## References

- **Phase 2A Output**: `03_refinement.yaml` (main hypothesis definition)
- **Synthesis Evidence**: `02_synthesis.yaml` (mechanistic decomposition rationale)
- **Persona Verdicts**: `01_round_table/final_opinions.yaml` (consensus assessment)
- **Verification State**: Managed by harness (ablation mode, not in this file)
- **Archon Project**: https://archon.local/projects/622e5a6a-846d-475f-bd6a-8c6080c60cbb

---

**Phase 2B Complete**  
**Next Phase**: Phase 2C Experiment Design (3 READY hypotheses: H-E1, H-M1, H-M2)
