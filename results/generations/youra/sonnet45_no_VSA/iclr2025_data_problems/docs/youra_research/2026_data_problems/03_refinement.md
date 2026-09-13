# Phase 2A Refinement Summary

**Hypothesis ID:** h-c1  
**Title:** Confidence-Calibrated Iteration Control for Agentic Code Generation  
**Version:** 1  
**Date:** 2026-07-10  
**Source Gap:** GAP-001 (Confidence-Calibrated Submit/Refine Decision Mechanisms)

---

## Core Hypothesis

**Calibrated confidence, implemented via temperature-scaled log-probability gating, enables adaptive iteration control that reduces execution attempts by 20-40% on code generation benchmarks while preserving pass@k accuracy.**

---

## Causal Mechanism

Temperature scaling post-processes model logits to produce calibrated confidence scores. These scores gate the agent's decision to:

1. **Submit code directly** (high confidence > 90th percentile)
2. **Self-critique before submission** (medium confidence 70-90th percentile)
3. **Request execution feedback** (low confidence < 70th percentile)

Thresholds are set via conformal calibration to bound false negative rates at predefined error levels (α=0.05, β=0.20).

---

## Testable Predictions

### Prediction 1: Monotonicity
**Statement:** Calibrated confidence bins exhibit monotonic relationship with empirical pass@1  
**Metric:** Spearman rank correlation ρ  
**Success Criteria:** ρ ≥ 0.7 with p < 0.05  
**Validation:** Bin MBPP validation problems by confidence deciles, measure pass rate per bin

### Prediction 2: Marginal Benefit Decreases with Confidence
**Statement:** Additional self-critique provides diminishing returns at higher confidence  
**Metric:** Regression coefficient β (confidence → Δpass@1 after critique)  
**Success Criteria:** β < 0 with p < 0.05  
**Validation:** Stratified analysis across confidence tertiles

### Prediction 3: Execution Reduction with Preserved Accuracy
**Statement:** Gated+Scaled condition reduces execution attempts while maintaining pass@k  
**Metric:** Execution attempts reduction, absolute Δpass@1  
**Success Criteria:** 20-40% execution reduction, Δpass@1 ≤ 2% absolute  
**Validation:** 2×2 factorial ablation on MBPP, generalization check on HumanEval

---

## Experimental Design

### 2×2 Factorial Ablation

| Condition | Temperature Scaling | Gating Policy | Purpose |
|-----------|---------------------|---------------|---------|
| Baseline | None | Fixed (N=1 critique) | Control |
| Scaled-only | Learned | Fixed (N=1 critique) | Calibration effect only |
| Gated-only | None | Confidence-based | Gating effect only |
| Treatment | Learned | Confidence-based | Combined effect |

### Data Split
- **Train:** 60% of MBPP (584 problems) - Model fine-tuning if needed
- **Calibration:** 20% of MBPP (195 problems) - Fit temperature parameter
- **Validation:** 20% of MBPP (195 problems) - Tune conformal thresholds
- **Test:** HumanEval (164 problems) - Generalization check (held-out)

### Metrics
1. **pass@1** - Primary accuracy metric
2. **Execution attempts** - Resource efficiency (primary impact claim)
3. **Wall-clock time** - Practical deployment consideration
4. **Cost-adjusted utility** - Expected value under cost ratios R=1× to 10×

---

## Validation Gates (Sequential)

### Gate 1: Monotonicity Validation ⚠️ CRITICAL
**Test:** Spearman rank correlation between confidence bins and empirical pass rate  
**Success:** ρ ≥ 0.7 with p < 0.05  
**Failure Action:** **STOP** - Calibration is not behaviorally meaningful

### Gate 2: Marginal Benefit Regression
**Test:** Regression Δpass ~ confidence + difficulty  
**Success:** Coefficient(confidence) < 0 with p < 0.05  
**Failure Action:** **STOP** - Gating is not justified over fixed schedule

### Gate 3: Full Ablation Study
**Test:** 2×2 factorial on MBPP, generalization on HumanEval  
**Success:** 20-40% execution reduction, Δpass@1 ≤ 2%  
**Failure Action:** Report negative result, analyze failure modes

---

## Novelty

### Primary Contribution
**First integration of temperature scaling for intermediate control flow (not just final prediction) in agentic code generation.**

Previous work (UniCR, QaTS, ATS) calibrates final predictions. Agentic systems (CODESIM, OpenCodeInterpreter) use fixed iteration policies. This work demonstrates calibrated confidence as an **active control signal** for iteration depth.

### Secondary Contribution
**Meta-level: Calibrated confidence as general resource allocation principle for agentic systems.**

The calibration→gating→resource-allocation pattern applies beyond code generation:
- Theorem proving (proof synthesis vs. proof checking)
- Text2SQL (query planning vs. database execution)
- Multi-modal agents (action planning vs. UI interaction)
- Scientific discovery (hypothesis generation vs. wet-lab experiments)

### Bridging Paradigms
Combines **model-heavy** (CODESIM: simulation-driven planning, 95.1% HumanEval) with **execution-heavy** (OpenCodeInterpreter: iterate until tests pass, 83.2 avg) via confidence-based routing.

---

## Scope and Boundaries

### In Scope
- **Datasets:** MBPP (primary), HumanEval (generalization)
- **Models:** Open-weight (Code Llama 34B, StarCoder2 15B, DeepSeek-Coder-V2 16B)
- **Task:** Function-level code generation
- **Calibration:** Post-hoc temperature scaling

### Out of Scope (Future Work)
- API-only models (GPT-4, Claude) - No logit access
- Project-level code generation - Complexity beyond function-level
- Code editing tasks - Different task structure
- Meta-learned predictors - Additional complexity, risk of overfitting

---

## Baselines and Related Work

### Baselines
1. **OpenCodeInterpreter** - Execution-heavy, no confidence modeling, iterates until tests pass
2. **CODESIM** - Model-heavy simulation, 95.1% HumanEval, no calibration

### Calibration Methods
- **UniCR** - Temperature scaling + conformal risk control for final predictions
- **QaTS** - Quantile-adaptive temperature scaling (heterogeneous miscalibration)
- **ATS** - Adaptive temperature scaling (post-RLHF degradation)

### Agentic Code Generation
- **InterCode** - Standard RL environment for execution feedback
- **PerfCodeGen** - Runtime performance feedback (ACM Distinguished Paper)
- **AgentCoder** - Multi-agent collaboration (fixed iteration policies)

---

## Key Assumptions (All Testable)

1. **Calibrated log-probability (length-normalized) correlates monotonically with empirical code correctness**
   - **Test:** Gate 1 (monotonicity validation)
   
2. **Marginal benefit from self-critique decreases with initial confidence**
   - **Test:** Gate 2 (marginal benefit regression)
   
3. **Temperature fitted on round-0 generations generalizes to post-critique generations**
   - **Test:** Per-round ECE measurement without refitting

---

## Objections Addressed

### Prof. Rex: "Calibration may reduce ECE without predicting behaviorally relevant correctness"
**Resolution:** Monotonicity validation (Gate 1) explicitly tests whether calibrated confidence predicts empirical pass rate. If it doesn't, we stop.

### Prof. Vera: "Self-critique and calibration effects are entangled"
**Resolution:** 2×2 factorial design isolates calibration contribution. Scaled-only vs. Gated-only vs. Treatment conditions disentangle effects.

### Prof. Rex: "Execution savings may be trivial compared to inference cost"
**Resolution:** Cost-adjusted utility metric varies cost ratio R from 1× to 10×. Identifies win regions and real-world scenarios (formal verification, databases) where R is naturally high.

### Prof. Pax: "Logit access unavailable in production APIs"
**Resolution:** Scoped to open-weight models as proof-of-concept. API integration via alternative confidence proxies (self-consistency, entropy) is future work.

### Prof. Pax: "Dataset too small for robust per-round calibration"
**Resolution:** MBPP primary (974 problems vs. HumanEval 164). Pool rounds 1-2-3 into "post-critique" if per-round calibration is noisy.

### Prof. Rex: "Heuristic thresholds (0.9, 0.7, 0.5) are arbitrary"
**Resolution:** Conformal quantiles derived from calibration set with pre-registered error rates (α=0.05, β=0.20). No tuning on test data.

---

## Must-Work Gate

**Monotonicity Validation:** Calibrated confidence bins must exhibit monotonic relationship with empirical correctness (Spearman ρ ≥ 0.7).

**Rationale:** If confidence doesn't predict correctness, calibration is decorative, not functional. The entire approach depends on confidence being a valid behavioral signal.

---

## Determines-Success Gate

**Execution Reduction with Preserved Accuracy:** Gated+Scaled condition must reduce execution attempts by 20-40% while maintaining pass@1 within 2% absolute difference of baseline.

**Rationale:** The impact claim is resource efficiency. If we can't demonstrate execution savings, the practical value proposition collapses.

---

## Established Facts from Discussion

1. ✅ Temperature scaling reduces ECE (58.3% on h-e1, validated methodology)
2. ✅ Multi-turn refinement outperforms single-shot (CODESIM 95.1%, OpenCodeInterpreter 83.2)
3. ✅ Model-based self-critique reduces tool calls (Structural Verification: 2× fewer)
4. ✅ Execution feedback is lightweight (test pass/fail, no profiling)
5. ✅ HumanEval approaching saturation (95.1% SOTA), MBPP more headroom

---

## Phase 2B Readiness

**Hypothesis Type:** EMPIRICAL (A/B test + ablation study)

**Feasibility Validated:**
- ✅ Mechanism valid (temperature scaling mathematically sound)
- ✅ Logit access via open-weight models
- ✅ Dataset sufficient (MBPP 974, HumanEval 164)
- ✅ Existing benchmarks (no new data collection)
- ✅ No human evaluation required (automated test execution)

**Next Phase Inputs:**
- Experimental design: 2×2 factorial with three-way data split
- Validation sequence: Monotonicity → Marginal benefit → Full ablation
- Success criteria: 20-40% execution reduction, Δpass@1 ≤ 2%
- Metrics: pass@1, execution attempts, wall-clock time, cost-adjusted utility

**Risk Mitigation:**
- Gate 1 stops study if monotonicity fails
- Per-round ECE checks calibration drift
- Cost-adjusted utility identifies realistic win regions

---

## Discussion Convergence Summary

**Exchanges:** 7  
**Personas:** 6 (Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex)

**Convergence Criteria Met:**
- ✅ SPECIFIC: Clear core claim stated
- ✅ MECHANISM: How it works explained
- ✅ PREDICTIONS: 3 testable predictions with success criteria
- ✅ NOVELTY: Intermediate control flow via calibration (first)
- ✅ FEASIBILITY: Mechanism valid, datasets available, models accessible
- ✅ OBJECTIONS: All major criticisms addressed with concrete resolutions

**Consensus Points:**
- Temperature scaling is validated (58.3% ECE reduction on h-e1)
- 2×2 factorial necessary to isolate effects
- Monotonicity validation is critical gate
- MBPP primary, HumanEval generalization
- Open-weight models required (logit access)

---

**Status:** ✅ READY FOR PHASE 2B (Verification Protocol Design)

**Next Steps:**
1. Phase 2B: Design detailed experimental protocol
2. Phase 2C: Specify implementation requirements
3. Phase 3: Create implementation plan (PRD, Architecture, PRP)
4. Phase 4: Implement and validate hypothesis
