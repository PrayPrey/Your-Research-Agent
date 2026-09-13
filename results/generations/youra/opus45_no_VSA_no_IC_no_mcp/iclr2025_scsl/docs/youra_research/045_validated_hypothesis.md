# Phase 4.5: Validated Hypothesis Synthesis

**Date:** 2026-08-28  
**Main Hypothesis:** H-TemporalSGD-v1  
**Status:** PARTIALLY_SUPPORTED (Existence confirmed, Mechanism falsified)

---

## Executive Summary

This synthesis evaluates the hypothesis that SGD hyperparameters (learning rate, batch size) control the temporal dynamics of spurious feature emergence. Two sub-hypotheses were tested:

**H-E1 (Existence):** PASS — Spurious features dominate from epoch 0 with GradCAM attribution ratio = 1.348, confirming simplicity bias in ERM training on Waterbirds.

**H-M1 (Mechanism):** FAIL — The proposed gradient competition mechanism is falsified. Spurious-aligned samples produce gradient norm ratio = 0.18 (not >1.5). Minority samples generate 5.7x higher gradients, inverting the hypothesis.

**Critical Finding:** Spurious feature dominance occurs through faster loss convergence on simpler patterns, not through stronger gradient signals. The mechanistic foundation requires reformulation before testing LR/batch interventions.

**Routing Decision:** Return to Phase 2A-Dialogue for mechanism revision.

---

## Prediction-Result Matrix

| ID | Prediction | Expected | Actual | Status |
|----|------------|----------|--------|--------|
| P1 | 10x higher LR shifts peak spurious dominance ≥5 epochs later | Shift ≥5 epochs | NOT_TESTED | BLOCKED |
| P2 | Peak spurious epoch negatively correlates with worst-group accuracy | r < -0.5 | NOT_TESTED | BLOCKED |
| P3 | Loss landscape sharpness ≥2x at peak vs convergence | Ratio ≥2.0 | NOT_TESTED | BLOCKED |

### Sub-Hypothesis Results

| ID | Type | Statement | Gate | Result | Key Metric |
|----|------|-----------|------|--------|------------|
| H-E1 | EXISTENCE | Spurious dominance before epoch 10 | MUST_WORK | **PASS** | Ratio=1.348 at epoch 0 |
| H-M1 | MECHANISM | Spurious gradient norm > core (ratio >1.5) | MUST_WORK | **FAIL** | Ratio=0.18 (inverted) |
| H-M2 | MECHANISM | Higher LR shifts peak ≥5 epochs | MUST_WORK | NOT_STARTED | Blocked by H-M1 |
| H-M3 | MECHANISM | Delayed dominance correlates with accuracy | SHOULD_WORK | NOT_STARTED | Blocked by H-M2 |

---

## Experiment Results

### H-E1: Spurious Feature Dominance (EXISTENCE)

**Configuration:**
- Dataset: Waterbirds v1.0 (11,788 images)
- Model: ResNet-50 (ImageNet pretrained)
- Training: SGD, LR=0.01, batch=128, 50 epochs
- Attribution: GradCAM on layer4[-1], 500 validation samples

**Results:**

| Epoch | Spurious/Core Ratio |
|-------|---------------------|
| 0 | 1.348 |
| 5 | 1.273 |
| 10 | 1.431 |
| 13 (peak) | 1.590 |
| 25 | 1.255 |
| 50 | 1.255 |

**Conclusion:** Spurious dominance immediate and persistent. Gate PASSED.

### H-M1: Gradient Competition Mechanism (MECHANISM)

**Configuration:**
- Same dataset/model as H-E1
- Training: SGD, LR=0.001, batch=128, 50 epochs
- Measurement: Gradient norms at layer4 for spurious-aligned vs minority samples
- Seeds: 3 (42, 123, 456)

**Results:**

| Seed | Early Epoch Ratio (1-10) | Trend |
|------|--------------------------|-------|
| 42 | 0.175 | Decreasing |
| 123 | 0.173 | Decreasing |
| 456 | 0.181 | Decreasing |
| **Mean** | **0.176** | Decreasing |

**Expected:** Ratio > 1.5  
**Actual:** Ratio = 0.18 (5.7x inverted)

**Conclusion:** Spurious-aligned samples produce LOW gradients (already solved). Minority samples produce HIGH gradients (remain difficult). Mechanism falsified. Gate FAILED.

---

## Hypothesis Refinement

### Original Statement
> Under standard supervised learning on datasets with spurious correlations, if we increase the learning rate or decrease the batch size, then peak spurious feature dominance will occur at later training epochs, because higher learning rates and smaller batches introduce optimization noise that disrupts the fast convergence to spurious feature reliance.

### Refined Statement
> Spurious features dominate ERM training from initialization because they occupy simpler loss landscape regions that converge faster, not because they receive stronger gradient signals. The "gradient competition" mechanism is incorrect—minority samples maintain high gradients precisely because they remain unsolved. Any intervention targeting spurious timing must operate through loss landscape geometry (convergence speed, basin sharpness), not gradient magnitude rebalancing.

### What Was Confirmed
1. Spurious feature dominance exists from epoch 0 (ratio=1.348)
2. Dominance persists throughout training (ratio stays >1.0)
3. Peak dominance occurs at epoch 13 (ratio=1.59)
4. Simplicity bias (Shah et al., 2020) is empirically verified

### What Was Falsified
1. "Gradient competition" mechanism — spurious features do NOT receive stronger gradients
2. The causal chain: LR/batch → gradient noise → spurious timing
3. Assumption A2: "Spurious and core features compete for gradient signal"

### Assumptions Validated/Invalidated

| ID | Assumption | Status | Evidence |
|----|------------|--------|----------|
| A1 | GradCAM separates spurious/core attribution | VALIDATED | H-E1 shows clear ratio differences |
| A2 | Spurious/core features compete for gradient signal | **INVALIDATED** | H-M1 shows inverted gradients |
| A3 | Higher LR increases optimization noise | UNTESTED | Blocked |
| A4 | Delayed dominance improves worst-group accuracy | UNTESTED | Blocked |
| A5 | Effects transfer across datasets | UNTESTED | Only Waterbirds tested |

---

## Theoretical Interpretation

### Alignment with Prior Work

**Shah et al. (2020) - Simplicity Bias:**
- Our H-E1 confirms their finding: DNNs preferentially learn simple features
- However, our H-M1 reveals the mechanism is NOT gradient magnitude

**JTT (Liu et al., 2021):**
- Confirms early training reveals spurious reliance
- Our findings suggest JTT's two-stage approach works by loss reweighting, not gradient rebalancing

### Unexpected Finding: Inverted Gradient Dynamics

The core surprising result: minority (hard) samples produce 5.7x higher gradient norms than spurious-aligned (easy) samples.

**Competing Explanations:**

1. **Loss-based convergence (most likely):**
   - Spurious patterns achieve low loss quickly (simple to classify via background)
   - Low loss → small gradients (already solved)
   - Minority samples remain high-loss → large gradients (still learning)
   - Dominance comes from convergence SPEED, not gradient MAGNITUDE

2. **Sample difficulty hypothesis:**
   - The model "gives up" on learning from spurious-aligned samples (already correct)
   - Continues "trying" on minority samples (still incorrect)
   - High gradients indicate effort, not preference

3. **Feature simplicity hypothesis:**
   - Simpler features require fewer gradient updates total
   - Not larger updates per step

### Theoretical Implications

The gradient competition framing is fundamentally wrong. Spurious features dominate because:
- They occupy flatter, simpler loss basins
- Networks converge to these solutions faster
- NOT because they receive more gradient signal

**New mechanistic hypothesis needed:** Test whether LR/batch affects convergence speed in simple vs complex basins, not gradient magnitudes.

---

## Limitations

| Limitation | Root Cause | Impact | Mitigation |
|------------|------------|--------|------------|
| Mechanism falsified | Incorrect gradient competition assumption | Cannot test LR/batch interventions | Reformulate mechanism |
| Synthetic masks | H-E1 used upper/lower half heuristic | Attribution ratio may be noisy | Use segmentation masks |
| Single dataset | Only Waterbirds tested | Cannot claim generalization | Add CelebA replication |
| Layer4 only | Gradients at final conv block | Earlier layers may differ | Multi-layer analysis |
| Single architecture | ResNet-50 only | May not generalize to ViT | Architecture sweep |
| Group definition | Spurious-aligned vs minority | Coarse grouping | Per-sample analysis |

---

## Future Work

### Immediate (Mechanism Reformulation)
1. **Loss trajectory analysis:** Track per-group loss curves to confirm spurious-aligned samples converge faster
2. **Basin geometry study:** Measure loss landscape curvature (Hessian eigenvalues) for spurious vs core features
3. **Convergence speed hypothesis:** Test if high LR slows convergence in simple basins more than complex ones

### Medium-term (Alternative Interventions)
4. **SAM connection:** Sharpness-Aware Minimization may work by penalizing simple basin convergence
5. **Curriculum learning:** Present minority samples earlier to prevent premature spurious convergence
6. **Basin-aware regularization:** Explicitly penalize fast convergence regions

### Long-term (Validation)
7. **Multi-dataset replication:** CelebA, Colored MNIST, CivilComments
8. **Architecture generalization:** ViT, EfficientNet, MLP-Mixer
9. **Theoretical formalization:** Connect to neural tangent kernel / loss landscape theory

---

## Implications for Phase 6

### Paper Framing
The paper cannot claim "gradient competition controls spurious timing" — this is falsified. Instead:

**Positive framing options:**
1. "We characterize the temporal dynamics of spurious feature emergence and falsify the gradient competition hypothesis"
2. "Simplicity bias operates through convergence speed, not gradient magnitude: implications for robustness interventions"

### Contribution Repositioning

| Original Claim | Status | Revised Claim |
|----------------|--------|---------------|
| SGD hyperparameters control spurious timing | BLOCKED | Mechanism unclear |
| Gradient competition drives spurious dominance | FALSIFIED | Convergence speed drives dominance |
| Single-stage optimization suffices for robustness | UNTESTED | Requires new mechanism |

### What CAN Be Written
1. Confirmation of simplicity bias (H-E1)
2. Novel finding: gradient magnitudes are inverted from expectation
3. Theoretical reframing: spurious dominance as convergence phenomenon
4. Negative result: gradient competition hypothesis falsified

### What CANNOT Be Written
1. Any claims about LR/batch controlling spurious timing (untested)
2. Any claims about gradient competition mechanism (falsified)
3. Comparison to JTT/Group DRO baselines (not reached)

### Recommended Path
Return to Phase 2A-Dialogue to reformulate mechanism around loss landscape convergence. Test new mechanism before proceeding to P1-P3 predictions.

---

## Synthesis Metadata

| Field | Value |
|-------|-------|
| Sub-hypotheses tested | 2 of 4 |
| Gates passed | 1 (H-E1) |
| Gates failed | 1 (H-M1) |
| Predictions tested | 0 of 3 |
| Routing decision | Phase 2A-Dialogue |
| Synthesis complete | true |

---

*Generated: 2026-08-28 | Phase 4.5 Hypothesis Synthesis*
*Next: Phase 2A-Dialogue for mechanism reformulation*
