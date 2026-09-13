# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SL-VGG-v1
**Confidence Level:** 0.80

**Main Hypothesis:**
Under compounding-error formal domains (theorem proving in Lean 4, verified code generation with Z3), if step-level verification feedback is provided during LLM generation, then verification correctness rate will exceed claim-level approaches by ≥5% because early error detection prevents error propagation and provides denser training signals.

**Alternative Hypothesis (H0):**
Step-level verification feedback provides no significant improvement over claim-level feedback in compounding-error formal domains, or the overhead of step-level verification negates any correctness benefits.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Feedback Integration Mode | Independent | Step-level (per tactic/statement) vs claim-level (post-hoc) vs grammar-only feedback | {step, claim, grammar} |
| Verification Correctness Rate | Dependent | Percentage of generated proofs/code verified correct by Lean 4 type checker or Z3 SMT solver | 0-100% (target: 75-85%) |
| Generation Efficiency | Dependent | Total generation time including verification overhead, measured in seconds per proof/program | <2x unconstrained baseline |
| Error Recovery Rate | Dependent | Percentage of initially failed generations that succeed after feedback-guided correction | ≥70% (vs ≤50% claim-level) |
| Base LLM Architecture | Controlled | Fixed transformer architecture (e.g., 7B parameter decoder-only) | Fixed |
| Verification Backend | Controlled | Lean 4 for theorem proving, Z3 for code verification | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Step-Level Verification → Feedback Encoding
  After each tactic/statement, verification module checks partial validity
  and generates 3-part feedback signal (validity bit + error type embedding + correction hints)
        ↓
Step 2: Feedback Encoding → Generation Conditioning
  Feedback embeddings are incorporated via cross-attention in modified decoder,
  conditioning next token generation on verification state
        ↓
Step 3: Generation Conditioning → Improved Correctness
  Dense verification rewards enable RL fine-tuning with step-level signals,
  leading to earlier error detection and reduced error propagation
        ↓
  Outcome: Higher verification rate with acceptable efficiency
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Grammar-Constrained Decoding (Park et al. 2025) | ~50μs mask computation proves efficient real-time verification feasible | Strong |
| Step2 → Step3 | CRANE (Banerjee et al. 2025) | Reasoning-augmented constrained decoding improves 10% on symbolic benchmarks | Strong |
| Step3 → Outcome | Seed-Prover (Chen et al. 2025) | Iterative refinement with Lean feedback achieves 78.1% on IMO formalized | Strong |

**Key Tension:**
- **Tension:** Seed-Prover uses whole-proof refinement (claim-level) and achieves saturation on miniF2F, while CRANE shows grammar constraints can hurt reasoning. SL-VGG claims step-level is better than both.
- **Resolution:** SL-VGG targets compounding-error domains specifically where early detection matters most. Evaluation on CLEVER benchmark (verified code) will test whether step-level granularity provides genuine advantage over claim-level in error-compounding scenarios.

### 1.4 Key Assumptions

1. **Efficient incremental verification** (<50ms per step)
   - Evidence: Z3 incremental solving, Lean 4 tactic checking support partial query caching
   - If violated: Step-level feedback becomes impractical; fall back to claim-level approach

2. **Learnable feedback encoding**
   - Evidence: Seed-Prover learns from Lean feedback; CRANE learns grammar constraints
   - If violated: LLM cannot generalize correction behavior; need alternative encoding scheme

3. **Partial verification provides useful guidance**
   - Evidence: Grammar-constrained decoding prunes invalid tokens before completion
   - If violated: Partial checks give false positives; require full proof for meaningful guidance

4. **Overhead offset by reduced regeneration**
   - Evidence: VERGE's iterative refinement averages 2.3 cycles; step-level may reduce this
   - If violated: Total time exceeds claim-level; efficiency claim fails despite correctness gains

### 1.5 Scope & Boundaries

**Applies to:**
- Theorem proving in Lean 4 (tactic-by-tactic verification)
- Verified code generation with Z3 (incremental SMT solving)
- Domains where errors compound (proof steps, dependent assertions)

**Does NOT apply to:**
- Simple structured output (JSON, SQL) - grammar constraints sufficient
- Domains without incremental verification support
- Natural language generation - no formal verification possible

**Known limitations:**
- Dependency on incremental verifier support (Lean 4, Z3 only initially)
- Narrower than universal FM-LLM framework
- Requires RL training infrastructure for dense step-level rewards

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Correctness vs SOTA 70% ± 10%):**
SL-VGG will achieve verification correctness rate > 75% on miniF2F-Lean with p < 0.05

*Measurement:*
- Correctness rate > 75% with paired t-test, n ≥ 25 runs
- Statistical test: Paired t-test (same random seeds)

*Basis:*
SOTA methods achieve 70% ± 10% (miniF2F-v2 best performance).
Our target represents 0.5σ improvement.

*Success Criteria for Phase 2B:*
- Primary: Correctness > 75% (p < 0.05)
- Falsification: Correctness ≤ 60% triggers rejection

**Secondary Predictions:**

**P2 (Error Recovery - Mechanism Validation):**
Step-level feedback will achieve error recovery rate ≥ 70% compared to ≤ 50% for claim-level approaches.

**P3 (Efficiency - Robustness):**
Total generation time will not exceed 2x unconstrained baseline when verification latency ≤ generation latency per step.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:
1. **Primary Failure:** Verification correctness rate ≤ 60%
2. **Mechanism Failure:** Error recovery rate < 50%
3. **Efficiency Failure:** Total generation time > 3x unconstrained baseline

### 1.7 SOTA Baseline

| Method | Benchmark | Performance | Year |
|--------|-----------|-------------|------|
| Seed-Prover | miniF2F | ~100% (saturated) | 2025 |
| miniF2F-v2 (SoTA) | miniF2F | 70% | 2025 |
| VERGE | Reasoning benchmarks | +18.7% improvement | 2026 |
| CRANE | GSM-symbolic, FOLIO | +10% over baselines | 2025 |

**SOTA Statistics:** Mean 70% ± 10%, Medium Performance Tier

### 1.8 Statistical Verification Design

- Effect size (Cohen's d): 0.5
- Required runs: n ≥ 25
- Statistical power: 0.8
- Test: Paired t-test, α = 0.05 (one-tailed)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does step-level verification feedback improve verification correctness rate under compounding-error formal domains?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the 3-step causal chain the actual cause of improved outcomes?"
- Phase 2B decomposes into: H-M1, H-M2, H-M3 (3 sub-hypotheses)
- Verification type: Causal analysis (ablation)

**SH3 (Comparison):**
"Does SL-VGG outperform VERGE (claim-level) and CRANE (grammar-level)?"
- Maps to: P2, P3
- Verification type: Comparative empirical

**Total: 5 sub-hypotheses** (1 + 3 + 1)

### Readiness Checklist

- [x] Hypothesis in scientific format
- [x] ID: H-SL-VGG-v1, Confidence: 0.80
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism (N=3) with evidence
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] Predictions (P1 primary, P2/P3 secondary)
- [x] Falsification criteria
- [x] Baselines: VERGE, CRANE
- [x] SH1/SH2/SH3 ready

### Open Questions

1. **Resources:** 8x A100 GPUs, 1 week for RL fine-tuning?
2. **Data:** LeanDojo for Lean 4 tactic feedback?
3. **Priority:** SH1 first or parallel with SH2?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
