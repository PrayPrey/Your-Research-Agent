# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - H-IGL)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-IGL-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under non-stationary implicit human feedback conditions where user preferences evolve over time, **if** we apply Homeostatic Interaction-Grounded Learning (H-IGL) with Bayesian Online Change-Point Detection (BOCPD) for drift monitoring and homeostatic regulation for decoder adaptation, **then** the agent will maintain effective policy performance (>80% baseline recovery within 100 episodes) **because** BOCPD provides principled detection of feedback-reward mapping shifts while homeostatic regulation controls the stability-plasticity trade-off during re-grounding.

**Alternative Hypothesis (H0):**
H-IGL provides no significant advantage over standard IGL in non-stationary implicit feedback settings. Specifically:
- H0a: BOCPD detection adds latency without improving adaptation timing
- H0b: Homeostatic regulation is no better than simple learning rate decay
- H0c: EWC regularization causes under-fitting on new preference structure

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| implicit_feedback_signal | Independent | Multimodal signals (EEG ErrPs, eye gaze, facial expressions) processed through pretrained encoder | Continuous vectors ∈ ℝ^d |
| change_point_threshold (τ) | Independent | BOCPD posterior threshold with sustained evidence window K | τ ∈ [0.5, 0.99], K=10 |
| homeostatic_time_constant | Independent | Exponential moving average parameter for decoder set-point | τ_h ∈ [0.9, 0.999] |
| EWC_importance_weight (λ) | Independent | Fisher information regularization strength | λ ∈ [100, 10000] |
| policy_performance | Dependent | Cumulative reward normalized by baseline IGL performance | [0%, 150%] of baseline |
| adaptation_latency | Dependent | Episodes from preference shift to 80% performance recovery | 10-200 episodes |
| false_positive_rate | Dependent | Proportion of change-point detections when no true shift occurred | <5% target |
| knowledge_retention | Dependent | Performance on held-out pre-shift evaluation set after adaptation | >70% target |
| preference_drift_rate | Controlled | Synthetic drift injection: gradual or abrupt | gradual: 0.1%/ep, abrupt: step |

### 1.3 Causal Mechanism

**4-Step Causal Chain:**

```
Step 1: Signal Processing
   Implicit feedback (EEG/gaze/expression) → Pretrained decoder → Probabilistic reward components

Step 2: Change-Point Detection
   Reward distribution history → BOCPD run-length posterior → P(change-point|history)

Step 3: Adaptation Control
   BOCPD signal + Homeostatic regulator → Controlled decoder adaptation rate

Step 4: Knowledge-Preserving Update
   EWC-regularized decoder update → Policy re-grounding → Maintained performance
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Kim et al. 2025 (RLIHF) | EEG-based ErrP decoder successfully provides reward signal for robotic control | Strong |
| Step 2 → Step 3 | Alami et al. 2023 (R-BOCPD) | Near-optimal detection delay and false-alarm bounds proven for non-stationary MDPs | Strong |
| Step 3 → Step 4 | Man et al. 2022 (Homeostatic NNs) | Biological homeostatic mechanisms successfully applied to concept drift in NNs | Medium |
| Step 4 → Outcome | Kirkpatrick et al. 2017 (EWC) | EWC prevents catastrophic forgetting with ~3% performance loss on old tasks | Strong |

**Key Tension:**
- **Tension:** BOCPD requires sustained evidence (K=10 timesteps) for robust detection, but this introduces ~10-episode detection latency. Meanwhile, rapid preference shifts may require faster response.
- **Resolution:** This verification plan tests the trade-off between K values (5, 10, 15) to determine optimal balance between false-positive rate and detection latency for the implicit feedback domain.

### 1.4 Key Assumptions

1. **IGL Conditional Independence (Local):** P(feedback|context,action,reward) = P(feedback|reward) holds between change-points
   - *Consequence if violated:* Reward decoder learns spurious context-feedback correlations, causing policy failure even without preference drift

2. **Detectable Drift:** Preference drift produces measurable changes in P(feedback|reward) distribution
   - *Consequence if violated:* BOCPD never detects drift, system degrades to standard IGL behavior under non-stationarity

3. **Drift Speed Bound:** Preference changes occur slower than BOCPD minimum detection latency (~10 episodes with K=10)
   - *Consequence if violated:* System perpetually lags behind true preference state, causing oscillating behavior

4. **Meaningful Homeostatic Set-Points:** Decoder parameter set-points can be meaningfully defined and tracked
   - *Consequence if violated:* Homeostatic regulation has no stable reference, may cause parameter drift

### 1.5 Scope & Boundaries

**Where H-IGL Applies:**
- Sequential decision-making with implicit human feedback (EEG, gaze, expression, gesture)
- Online learning scenarios where preferences may evolve
- Single-user or slow-varying population preference settings
- Environments with episodic structure for performance measurement

**Where H-IGL Does NOT Apply:**
- ❌ Explicit preference settings (use NS-DPO or LCPO instead)
- ❌ Offline-only learning (use FORL or offline RLHF methods)
- ❌ Multi-user settings with rapidly switching users (requires identity-conditioned approach)
- ❌ Preference shifts faster than 10 episodes (violates drift speed assumption)

**Known Limitations:**
- Requires ~100 episodes minimum for homeostatic set-point calibration
- BOCPD memory scales O(T) with trajectory length (use sliding window for long deployments)
- EWC Fisher information computation adds ~10% computational overhead
- Hyperparameters (τ, K, τ_h, λ) require tuning or Bayesian optimization

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Adaptation Under Drift):**
If preference drift occurs (abrupt or gradual), H-IGL will recover >80% of baseline IGL performance within 100 episodes, whereas standard IGL performance will degrade to <50% without recovery.

*Measurement:*
- Performance metric: Cumulative reward ratio vs. stationary baseline
- Statistical test: Paired t-test between H-IGL and IGL, n ≥ 20 runs
- Significance level: p < 0.05

*Falsification:*
- H-IGL fails to reach 80% recovery within 200 episodes
- H-IGL performance statistically indistinguishable from IGL under drift

**Secondary Predictions:**

**P2 (False Positive Control):**
If preferences are stationary, H-IGL false positive re-grounding rate will be <5% (≤1 false detection per 20 episodes).

**P3 (Comparative Advantage):**
If comparing with sliding-window IGL and context-reset IGL baselines, H-IGL will achieve >15% higher cumulative reward under drift scenarios.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure:** H-IGL recovery rate ≤60% within 200 episodes (substantial failure)
2. **False Positive Failure:** False positive rate >10% under stationary conditions
3. **No Comparative Advantage:** H-IGL underperforms sliding-window IGL baseline
4. **Mechanism Failure:** BOCPD does not detect drift OR homeostatic regulation degrades performance

### 1.7 SOTA Baseline (N/A)

*Not targeting SOTA comparison. Comparison will be against ablation baselines.*

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 20 runs per condition
**Statistical Test:** Paired t-test, α = 0.05 (one-tailed)
**Report Format:** Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does preference drift detection via BOCPD work for implicit feedback signals?"
- Maps to: Primary prediction P1 (detection component)
- Verification: Empirical test with synthetic drift injection
- Critical: MUST PASS - if BOCPD fails, entire mechanism fails

**SH2 (Mechanism):**
"Is the BOCPD + Homeostatic + EWC integration the actual cause of maintained performance?"
- Maps to: Causal mechanism (4 sub-hypotheses: H-M1 through H-M4)
  - H-M1: Signal → Decoder → Reward (Step 1)
  - H-M2: Reward history → BOCPD detection (Step 2)
  - H-M3: BOCPD + Homeostatic → Controlled adaptation (Step 3)
  - H-M4: EWC → Knowledge retention (Step 4)
- Verification: Ablation studies removing each component
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does H-IGL outperform baseline approaches (IGL, sliding-window, context-reset)?"
- Maps to: Secondary prediction P3
- Verification: Comparative empirical evaluation
- Critical: Determines practical value

**Total Sub-Hypotheses for Phase 2B:** 6 (SH1 + H-M1~H-M4 + SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-IGL-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined: 3 specific counter-claims
- [x] All variables have operationalization from evidence (9 variables)
- [x] Causal mechanism has evidence at each step (N=4 steps, evidence table provided)
- [x] Causal chain length determined: N=4
- [x] Key tension identified: Detection latency vs. false positives (K parameter trade-off)
- [x] Key assumptions list consequences if violated (4 assumptions)
- [x] At least 2 testable predictions exist: P1 (primary), P2, P3
- [x] Falsification criteria defined: 4 specific failure conditions
- [x] Baselines identified: IGL, sliding-window IGL, context-reset IGL
- [x] SH1, SH2, SH3 are clear starting points

**Readiness Status:** ✅ READY FOR PHASE 2B

### Open Questions for Phase 2B

1. **Data Availability:** Which implicit feedback datasets support synthetic drift injection? RLIHF's EEG data may require modification; alternatively, generate fully synthetic implicit feedback.

2. **Compute Requirements:** BOCPD with sliding window W=100 adds O(W) memory per episode. Estimate total GPU memory for 500-episode experiments with n=20 seeds.

3. **Priority Verification Order:** Recommend SH1 (existence) first, then H-M1→H-M4 (mechanism ablations), finally SH3 (comparison) - allows early termination if SH1 fails.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
