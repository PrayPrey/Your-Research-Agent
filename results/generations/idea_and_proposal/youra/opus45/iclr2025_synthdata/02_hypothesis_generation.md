# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SGADM-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under standard supervised learning conditions with mixed synthetic-real data, if we dynamically adjust the synthetic-to-real mixing ratio based on real-time model state feedback signals (loss divergence, ECE, MMD), then we achieve superior downstream performance compared to fixed-ratio or static curriculum approaches, because closed-loop feedback prevents distribution drift that causes model collapse while maximizing diversity benefits of synthetic augmentation.

**Alternative Hypothesis (H0):**
There is no significant difference in downstream performance between SGADM's adaptive ratio adjustment and fixed-ratio or static curriculum approaches; the feedback mechanism does not provide meaningful collapse prevention or performance improvement.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Feedback controller policy | Independent | PID-style controller with EMA smoothing (α=0.9), gains k_p=0.1, k_i=0.01 | Controller output: ratio adjustment Δr ∈ [-0.1, +0.1] per epoch |
| Loss gap signal | Independent | L_synth - L_real on validation split, computed per epoch | Gap ∈ [-0.5, +2.0], threshold_high = 0.3 |
| ECE signal | Independent | Expected Calibration Error on real validation with temperature scaling, 15 bins | ECE ∈ [0.0, 0.3], threshold = 0.05 |
| MMD signal | Independent | Maximum Mean Discrepancy between synthetic/real feature representations using RBF kernel | MMD ∈ [0.0, 1.0], increasing indicates drift |
| Downstream task accuracy | Dependent | Test accuracy on held-out real data, measured at training end | Expected: 2-5% improvement over baselines |
| Model collapse indicators | Dependent | Tail-class accuracy degradation, feature diversity (FID), loss variance | Tail acc >15%, FID <50, variance stable |
| Model architecture | Controlled | Fixed architecture (e.g., ResNet-50, ViT-B) across conditions | Same for all experiments |
| Training budget | Controlled | Fixed total epochs and compute budget | 100-200 epochs standard |
| Synthetic data quality | Controlled | Same synthetic generator (e.g., Stable Diffusion) across conditions | FID <30 for generated data |

### 1.3 Causal Mechanism

**4-Step Causal Chain:**

```
[Feedback Signal Computation] → [Divergence Detection] → [Ratio Adjustment Decision] → [Training Distribution Modification] → [Performance Improvement]
```

**Step 1: Feedback Signal Computation → Divergence Detection**
- **Mechanism:** Loss gap, ECE, and MMD are computed each epoch to quantify the mismatch between model predictions on synthetic vs real data
- **Evidence:** ECE is the canonical calibration metric (Guo et al.); MMD captures feature space divergence (pytorch-fid)
- **Falsification:** Signals too noisy or lagged → Mitigation: EMA smoothing (α=0.9)

**Step 2: Divergence Detection → Ratio Adjustment Decision**
- **Mechanism:** PID controller translates divergence magnitude into ratio change direction and magnitude
- **Evidence:** Control theory principles; AutoMixAlign (ACL 2025) uses similar adaptive reweighting
- **Falsification:** Controller gains miscalibrated → Mitigation: Validated defaults (k_p=0.1, k_i=0.01)

**Step 3: Ratio Adjustment Decision → Training Distribution Modification**
- **Mechanism:** Reducing synthetic ratio when divergence high corrects distribution drift before collapse onset
- **Evidence:** Seddik (2024) proves collapse inevitable with pure synthetic; ratio reduction prevents threshold crossing
- **Falsification:** Adjustment too slow → Mitigation: Per-epoch updates, staged thresholds

**Step 4: Training Distribution Modification → Performance Improvement**
- **Mechanism:** Maintaining balanced distribution prevents tail degradation while synthetic diversity improves generalization
- **Evidence:** DisCL (ICCV 2025) achieves +4.02% all-class accuracy on ImageNet-LT
- **Falsification:** Synthetic quality too low → Mitigation: Quality controlled via same generator

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | ECE literature (Guo et al.) | ECE reliably indicates calibration drift | Strong |
| Step 2 → Step 3 | Control theory, AutoMixAlign | PID controllers enable stable adaptive systems | Strong |
| Step 3 → Step 4 | Seddik (2024), Kazdan (2024) | Ratio management prevents collapse | Strong |
| Step 4 → Outcome | DisCL (ICCV 2025) | Curriculum learning improves +4% accuracy | Strong |

**Key Tension:**
- **Tension:** Seddik (2024) suggests fixed maximal synthetic ratios are sufficient, but DisCL (2024) shows adaptive curricula outperform fixed approaches by 2-4%
- **Resolution:** This verification plan tests whether SGADM's closed-loop feedback provides additional benefit beyond DisCL's static curriculum

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|--------------------|-----------------------|
| A1 | Feedback signals are reliable proxies for collapse risk | ECE correlates with miscalibration; MMD tracks distribution shift | Controller makes incorrect decisions; performance degrades |
| A2 | Synthetic data quality remains consistent | Controlled via same generator | Variable quality introduces confounding |
| A3 | Model state provides sufficient information | Implicit in feedback signal design | Need additional signals |
| A4 | Real validation data is available | Standard ML practice | Cannot compute ECE; rely on loss gap and MMD only |
| A5 | Controller overhead is negligible (<5%) | Signal computation is lightweight | Training time increases; practical adoption limited |

### 1.5 Scope & Boundaries

**Applies to:**
- Supervised learning tasks with synthetic data augmentation
- Any modality with computable feedback signals (images, text, tabular)
- Standard deep learning architectures (CNNs, Transformers)
- Scenarios where some real data is available as anchor

**Does NOT apply to:**
- Pure synthetic data generation without real data anchor
- Online/streaming learning scenarios
- Tasks where ECE/MMD computation is undefined
- Extremely small datasets where validation split is infeasible

**Known Limitations:**
- Controller hyperparameters may require task-specific tuning
- Feedback lag may miss very rapid collapse dynamics
- Multi-modality validation needed to confirm generalization claims

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Downstream Accuracy vs Baselines):**
SGADM will achieve downstream test accuracy ≥2% higher than fixed-ratio baselines and ≥1% higher than DisCL static curriculum on standard benchmarks (ImageNet-LT, iWildCam).

*Measurement:*
- Test accuracy improvement with p < 0.05 (paired t-test)
- n ≥ 20 runs with different random seeds

*Success Criteria:*
- Primary: Accuracy improvement ≥2% over fixed-ratio (p < 0.05)
- Secondary: Accuracy improvement ≥1% over DisCL (p < 0.10)

**Secondary Predictions:**

**P2 (Collapse Prevention):**
SGADM will maintain tail-class accuracy >15% throughout training, while fixed-ratio baselines will show degradation below 10% when synthetic ratio is suboptimal.

**P3 (Feedback Signal Correlation):**
When loss gap exceeds threshold_high (0.3), reducing synthetic ratio will correlate with subsequent ECE reduction within 5 epochs (r > 0.5).

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** SGADM accuracy ≤ fixed-ratio baseline accuracy
2. **Mechanism Failure:** No correlation between feedback signals and collapse indicators
3. **Comparative Failure:** SGADM accuracy < DisCL accuracy
4. **Overhead Failure:** Controller overhead >15% training time

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 20 runs per condition
**Statistical Test:** Paired t-test, α = 0.05 (one-tailed)
**Effect Size:** Cohen's d ~0.6 (medium-large)
**Report Format:** Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does SGADM's adaptive ratio control produce measurably different training dynamics compared to fixed-ratio approaches?"
- Maps to: Primary prediction P1
- Verification type: Empirical
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the closed-loop feedback the actual cause of improved performance?"
- Maps to: Causal mechanism (4 sub-hypotheses H-M1 through H-M4)
  - H-M1: Feedback signals detect divergence reliably
  - H-M2: Controller translates signals to appropriate ratio changes
  - H-M3: Ratio changes prevent collapse threshold crossing
  - H-M4: Balanced distribution yields performance improvement
- Verification type: Causal analysis with ablations
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does SGADM outperform DisCL and other baselines on standard benchmarks?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total Sub-Hypotheses in Phase 2B:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-SGADM-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence (9 variables)
- [x] Causal mechanism has evidence at each step (4 steps)
- [x] Causal chain length (N=4) determined
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated (5 assumptions)
- [x] At least 2 testable predictions exist (3 predictions)
- [x] Falsification criteria are defined (4 criteria)
- [x] Baselines are identified for comparison (4 baselines)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** ~500 GPU-hours on A100 for full verification
2. **Data Availability:** iWildCam dataset accessibility? Synthetic generators available?
3. **Priority Order:** SH1 (existence) first as gating condition

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
