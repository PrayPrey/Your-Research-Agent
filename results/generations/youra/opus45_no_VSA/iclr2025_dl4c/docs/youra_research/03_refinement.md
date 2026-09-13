# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-08T03:06:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-2
- **Gap Title**: Limited Hybrid Approach Studies (Training + Test-Time Combined)
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met — SPECIFIC core claim, MECHANISM defined via I(F;E), PREDICTIONS with statistical tests, NOVELTY established, FEASIBILITY confirmed, OBJECTIONS addressed

### Key Insights

1. RL training may teach "execution feedback comprehension" as a transferable skill, but the mechanism requires precise operationalization as "feedback-conditioned edit policy"
2. Superadditivity requires RL to improve edit directionality without collapsing exploration diversity — the entropy-directionality tradeoff is empirical
3. Feedback→edit mutual information I(F;E) is the cleanest mechanistic probe for structural policy coupling

### Breakthrough Moments

- **Exchange 3**: Prof. Rex identified that RL could reduce diversity, creating subadditivity risk
- **Exchange 5**: Dr. Ally refined hypothesis from vague "comprehension" to measurable "feedback-conditioned edit policy"
- **Exchange 8**: Prof. Rex proposed difference-in-differences for causal mechanism isolation
- **Exchange 12**: Prof. Rex crystallized feedback→edit alignment as policy-level evidence

---

## Final Hypothesis

### Title
Superadditive Gains from Hybrid RL Training and Test-Time Refinement in Code Generation

### Hypothesis ID
H-HybridRL-Refine-v1

### Core Claim

**Under** conditions where RL training includes structurally diverse execution feedback (H(Schema|ErrorClass) > threshold),

**If** we apply both RL training and K-step test-time refinement to code generation models,

**Then** we observe:
1. Superadditive accuracy gains (Training×Refinement interaction > 0 on logit scale)
2. Differential sensitivity to semantic feedback structure (difference-in-differences > 0)
3. Increased feedback→edit mutual information

**Because** RL training induces a feedback-conditioned edit policy that transfers to inference-time refinement.

### Mechanism

1. RL training optimizes p(edit | code, feedback) under diverse feedback distributions
2. Diversity forces abstraction over feedback structure rather than surface memorization
3. Abstraction manifests as increased I(F;E) — structural coupling between feedback spans and edit locations
4. At inference, structural coupling compounds: each refinement step is more directed → superadditive pass@k

---

## Predictions

| ID | Statement | Test Method | Success Criterion |
|----|-----------|-------------|-------------------|
| **P1** (Primary) | Training × Refinement interaction > 0 | Logit-scale GLMM | Interaction coef > 0, p < 0.05, OR ≥ 1.2 |
| **P2** | RL shows greater semantic sensitivity | Difference-in-differences | [(A-C)_RL - (A-C)_CE] > 0, p < 0.05 |
| **P3** | RL increases feedback→edit coupling | I(F;E) comparison | I(F;E)_RL > I(F;E)_CE, p < 0.05 |

---

## Novelty

**Key Innovation**: Feedback→edit mutual information I(F;E) as mechanistic probe for structural policy coupling

**Differentiation**:
- vs. CodeRL: First to combine with test-time refinement
- vs. Self-Refine: First to test on RL-trained models
- vs. S*: Studies training-inference interaction, not just test-time scaling
- vs. "Rethinking Fine-Tuning": Provides empirical mechanism evidence via I(F;E)

---

## Experimental Design

**Datasets**: HumanEval+ (164 problems), MBPP+ (500+ problems)

**Model**: CodeT5+-base (220M parameters)

**Factorial Design**: 2×2×2
- Training: CE vs RL
- Inference: single-shot vs K=3 refinement
- Training diversity: low vs high (for RL only)

**Baselines**:
- CE single-shot
- CE + Self-Refine
- RL single-shot (CodeRL protocol)

---

## Limitations

1. Results may not transfer to models with fundamentally different architectures
2. Training diversity effects may saturate at high diversity levels
3. Feedback perturbation quality depends on template design
4. Scope limited to function-level Python code generation

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met after 15 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

*Phase: 2A-Dialogue*
*Ready for: Phase 2B - Research Planning*
