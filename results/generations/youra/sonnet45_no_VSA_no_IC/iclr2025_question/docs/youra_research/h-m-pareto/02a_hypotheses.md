# Phase 2A: Hypothesis Generation — h-m-pareto

**Date:** 2026-08-20
**Research Question:** Do different UQ methods exhibit cost-performance trade-offs in selective prediction tasks?

---

## Competing Hypotheses

### Hypothesis 1 (h-m-pareto): Pareto Frontier Exists

**Statement:** Under the same conditions, if we construct the empirical Pareto frontier from (cost, AUROC) pairs for all 6 UQ methods, then at least 2 methods are Pareto-optimal (no method strictly dominates another with statistical significance p < 0.05), because different UQ mechanisms trade off calibration quality vs computational cost at different efficiency zones.

**Type:** Mechanism (SHOULD_WORK gate)

**Prerequisites:** h-m-integrated (validated — all UQ methods produce valid uncertainty rankings)

**Predictions:**
- H1: MC dropout k=5 achieves highest AUROC (≥ 0.70)
- H2: Temperature scaling competitive with MC k=5 (|AUROC difference| ≤ 0.05)
- H3: Cost-performance trade-off exists (|Pareto_set| ≥ 2)

**Mechanistic Reasoning:**
- MC dropout k=5: High cost (5× baseline) → high uncertainty quality (averaging k passes reduces variance)
- Temperature scaling: Low cost (1× post-hoc) → competitive calibration (logit rescaling without extra inference)
- Conformal prediction: Low cost (1× post-hoc) → different efficiency zone (set-valued predictions, not point estimates)

**Evidence Supporting:**
- retinal-selective-prediction benchmark: "Three different methods, three different wins"
- TS4CP paper: Non-monotonic trade-off between temperature and prediction set size
- MC dropout T=30: Best AURC (0.0756) vs softmax baseline (0.0793)

---

### Hypothesis 2 (h-m-universal-dominance): Universal Dominance

**Statement:** Under the same conditions, if we construct the empirical Pareto frontier from (cost, AUROC) pairs for all 6 UQ methods, then exactly 1 method is Pareto-optimal (one method universally dominates all others), because UQ quality scales monotonically with computational cost and no calibration shortcuts exist.

**Type:** Null/Alternative

**Predictions:**
- Only MC dropout k=10 is Pareto-optimal (highest cost → highest AUROC)
- Temperature scaling / conformal prediction strictly dominated (lower AUROC for same or higher cost)
- |Pareto_set| = 1

**Mechanistic Reasoning:**
- If uncertainty quality depends solely on averaging more forward passes, then MC dropout k=10 (highest k) should dominate all lower-cost methods
- Post-hoc calibration (temperature scaling / conformal) cannot match multi-pass averaging quality

**Evidence Supporting:**
- Ensemble methods often show monotonic performance improvement with more members
- MC dropout is asymptotically equivalent to Bayesian inference (more samples → better approximation)

**Evidence Against:**
- retinal-selective-prediction: MC dropout best AURC, but temperature scaling best ECE (different metrics favor different methods)
- TS4CP: Non-monotonic trend suggests diminishing returns exist

---

## Selected Hypothesis for Testing

**Primary:** h-m-pareto (Hypothesis 1)

**Rationale:**
- Prior evidence suggests no universal dominance (retinal benchmark shows different methods win on different metrics)
- Negative result (|Pareto_set| = 1) is scientifically valuable (would confirm UQ quality monotonic in cost)
- SHOULD_WORK gate: Non-blocking, both outcomes advance knowledge

---

## Dependent Variables

**Primary DV:** AUROC (Area Under ROC Curve)
**Measurement:** sklearn.metrics.roc_auc_score(y_true=correctness, y_score=uncertainty)
**Success Criterion:** AUROC ≥ 0.70 (per h-e1 baseline)

**Secondary DVs:**
- Spearman ρ: Correlation between uncertainty and incorrectness (validation > 0.2)
- FLOPs cost: Normalized to 1.0× baseline (MC k=1, temperature scaling, conformal = 1×; MC k=5 = 5×)
- Pareto set size: Number of non-dominated methods (success: ≥ 2)

---

## Independent Variables

**Primary IV:** UQ Method
**Levels:** 6 methods
1. Temperature scaling (1× cost)
2. Conformal prediction (1× cost)
3. MC dropout k=1 (1× cost, baseline)
4. MC dropout k=3 (3× cost)
5. MC dropout k=5 (5× cost)
6. MC dropout k=10 (10× cost)

**Controlled Variables:**
- Model: Llama-3.1-8B-Instruct (frozen, no fine-tuning)
- Dataset: TruthfulQA (817 questions)
- Calibration set: HaluEval (~10k samples for temperature / conformal only)
- Seeds: 3 (42, 123, 456) for AUROC variance estimation
- Precision: bfloat16

---

## Mechanism Under Test

**Pareto Dominance:**
- Method j dominates method i if:
  - cost_j ≤ cost_i AND
  - auroc_j > auroc_i (statistically significant via paired t-test, α=0.05)

**Construction:**
1. Compute (cost, AUROC) pairs for all 6 methods (n=3 seeds each)
2. For each method i, check if any method j dominates i
3. If no method dominates i, add i to Pareto set
4. Return Pareto set (expected size ≥ 2)

---

## Alternative Explanations

**If |Pareto_set| = 1 (h-m-pareto FAILS):**
1. **UQ quality monotonic in cost**: MC dropout k=10 dominates all others → suggests averaging is the only path to better uncertainty
2. **Calibration insufficient**: Temperature scaling / conformal fail to match MC dropout AUROC → post-hoc methods too weak
3. **Measurement noise**: Statistical power insufficient to detect trade-offs (α=0.05, n=3 seeds too low)

**If |Pareto_set| ≥ 2 (h-m-pareto CONFIRMED):**
1. **Different efficiency zones**: Temperature scaling competitive at low cost, MC k=5 better at high cost
2. **Diminishing returns**: MC k>5 shows marginal AUROC gains (not statistically significant)
3. **Trade-off validated**: Confirms prior retinal benchmark finding ("three different methods, three different wins")

---

*Next Phase: 02b_verification_plan.md — Design experimental protocol to test h-m-pareto*
