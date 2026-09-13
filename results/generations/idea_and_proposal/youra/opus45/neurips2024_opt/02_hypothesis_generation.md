# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ScaleOptSched-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under large-scale Transformer language model training (>100M parameters), if we track sharpness evolution (λ_max of the Hessian) and trigger optimizer transitions when sharpness stabilizes at the edge of stability, then training efficiency improves by 10-20% compared to fixed optimizer (Adam) because different optimizers are optimal at different training phases due to evolving loss landscape curvature.

**Alternative Hypothesis (H0):**
There is no relationship between optimizer transition timing based on sharpness evolution and training efficiency; a fixed optimizer (Adam) throughout training achieves equivalent or better compute efficiency regardless of loss landscape curvature phase.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Optimizer Type | Independent | Adam vs SGD vs Lion, with transition timing based on sharpness threshold (λ_max ≈ 2/η) | {Adam→SGD, Adam→Lion, Adam-only baseline} |
| Model Scale | Independent | Parameter count measured at initialization | 125M, 350M, 760M, 1B+ |
| Training Phase | Independent | Detected via sharpness regime: Early (λ_max decreasing), Mid (λ_max increasing), Late (λ_max ≈ 2/η plateau) | {early, mid, late} or continuous step count |
| Sharpness (λ_max) | Mediating | Critical sharpness measure: λ_c = 2·(L(θ+Δθ) - L(θ)) / ‖Δθ‖² (requires ~10 forward passes) | 0.1 to 100+ depending on scale and LR |
| Training Loss | Dependent | Cross-entropy loss on held-out validation set | Expected improvement: 2-5% lower final loss |
| Compute Efficiency | Dependent | Final validation loss achieved per FLOP (loss/FLOP curve area) | Expected improvement: 10-20% better efficiency |
| Architecture | Controlled | Fixed GPT-style Transformer (decoder-only, standard attention) | Fixed per experiment |
| Data Distribution | Controlled | Standard LM corpus (C4, OpenWebText, or equivalent) | Fixed per experiment |
| Learning Rate Schedule | Controlled | Cosine decay with warmup; base LR transferred via μP | Fixed per experiment |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Phase-Dependent Optimizer Optimality
    ↓
Step 2: Sharpness-Based Transition Detection
    ↓
Step 3: Late-Training SGD Benefits
    ↓
Outcome: Improved Training Efficiency
```

**Step 1 → Step 2:** Training begins in high-curvature regime where Adam's per-parameter adaptivity efficiently navigates the sharp loss landscape, leading to rapid initial loss decrease. As training progresses, sharpness tracking (λ_max monitoring via critical sharpness) detects the transition to the edge of stability plateau, providing a trigger signal for optimizer switch.

**Step 2 → Step 3:** The detected sharpness plateau indicates the model has reached a region where Adam's adaptive learning rates provide diminishing returns. Transitioning to SGD at this point leverages SGD's implicit regularization properties and its natural operation at the 2/η sharpness boundary.

**Step 3 → Outcome:** SGD's implicit regularization helps escape sharp minima and find flatter solutions with better generalization. Combined with the efficiency gains from optimal phase-matched optimization, overall training efficiency improves by 10-20%.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Kalra & Barkeshli (2023) "Phase diagram of early training dynamics" | Four distinct training regimes identified: early transient, saturation, progressive sharpening, edge of stability | Strong |
| Step 1 → Step 2 | Kalra et al. (2026) "Scalable Measure of Loss Landscape Curvature" | Critical sharpness (λ_c) requires only ~10 forward passes, demonstrated at 7B scale | Strong |
| Step 2 → Step 3 | Kalra et al. (2023) "Universal Sharpness Dynamics" | Edge of stability mechanism explained; period-doubling route to chaos at high LR | Strong |
| Step 2 → Step 3 | Noci et al. (2024) "Super Consistency of NN Landscapes" | μP maintains consistent sharpness dynamics across scales, enabling transfer | Medium |
| Step 3 → Outcome | Kaplan et al. (2020) "Scaling Laws for Neural Language Models" | Larger models more sample-efficient; optimization interacts with scaling | Medium |

**Key Tension:**
Noci et al. (2024) show that under μP, sharpness dynamics remain consistent across scales, suggesting hyperparameter transfer is possible. However, this work focuses on learning rate transfer with a fixed optimizer (Adam), not dynamic optimizer scheduling. The tension is whether the consistency that enables LR transfer also implies that optimizer transitions are unnecessary.

**Resolution:** This verification plan tests whether the consistent sharpness dynamics under μP actually create predictable transition points that can be exploited for optimizer scheduling, rather than eliminating the need for such transitions. The hypothesis is that consistent dynamics make transitions MORE predictable, not less valuable.

### 1.4 Key Assumptions

1. **Edge of stability generalizes to Transformers at scale**
   - Supporting Evidence: Kalra et al. (2023) demonstrated in deep networks; Kalra et al. (2026) validated critical sharpness at 7B scale on OLMo-2 models
   - Consequence if violated: If Transformers don't exhibit clear edge of stability behavior, transition timing becomes arbitrary and benefits disappear

2. **Sharpness is computationally tractable to track (<5% overhead)**
   - Supporting Evidence: Critical sharpness (λ_c) requires only ~10 forward passes per measurement (Kalra et al. 2026)
   - Consequence if violated: If tracking overhead exceeds efficiency gains, the approach becomes impractical

3. **Different optimizers have genuinely different optimal operating regimes**
   - Supporting Evidence: Adam excels in high-curvature early training (Reddi et al. 2018); SGD provides implicit regularization at edge of stability (Cohen et al. 2021)
   - Consequence if violated: If optimizers perform equivalently across all regimes, transitions provide no benefit

4. **Optimizer transition overhead is negligible**
   - Supporting Evidence: Optimizer state re-initialization or momentum transfer takes negligible time compared to training
   - Consequence if violated: If transitions cause training instability or require lengthy re-warmup, efficiency gains are negated

### 1.5 Scope & Boundaries

**Applies to:**
- Transformer-based language models (decoder-only, encoder-decoder)
- Model scales from 125M to multi-billion parameters
- Standard autoregressive language modeling objective (cross-entropy)
- SGD-family and Adam-family optimizers
- Training from scratch or continued pre-training

**Does NOT apply to:**
- Reinforcement learning from human feedback (RLHF) - different optimization landscape
- Fine-tuning on small datasets - insufficient training duration for phase transitions
- Very small models (<100M parameters) - overhead may dominate benefits
- Non-Transformer architectures - sharpness dynamics may differ
- Optimizers with fundamentally different mechanics (e.g., second-order methods)

**Known Limitations:**
- Sharpness tracking adds computational overhead (~5% per measurement point)
- Optimal transition points may require initial calibration experiments
- Benefits most pronounced at scales >1B parameters where training cost justifies overhead
- Transition protocol (hard switch vs. gradual interpolation) requires empirical validation

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Efficiency Improvement):** If sharpness-triggered optimizer scheduling is applied (Adam → SGD at edge of stability), then compute efficiency (final loss per FLOP) improves by ≥10% compared to Adam-only baseline.

*Measurement:* Compare loss/FLOP curves; efficiency = ∫(baseline_loss - scheduled_loss) dFLOP
*TRUE if:* Scheduled training achieves target loss with ≤90% of baseline FLOPs
*FALSE if:* Scheduled training requires ≥95% of baseline FLOPs or shows higher final loss

**Secondary Predictions:**
**P2 (Scale-Dependent Transition Point):** As model scale increases, the optimal transition point (in training steps) shifts earlier in relative terms (earlier fraction of total training).

*Measurement:* Record transition step / total steps ratio across scales
*TRUE if:* Transition ratio decreases monotonically with scale (125M→1B)
*FALSE if:* No consistent relationship between scale and transition timing

**P3 (Sharpness Signature Reliability):** The edge of stability plateau (λ_max ≈ 2/η ± 10%) provides a reliable transition signal with <5% false positive rate.

*Measurement:* Track sharpness evolution; measure stability of plateau detection
*TRUE if:* Plateau detected consistently across random seeds and scales
*FALSE if:* Plateau timing varies >20% across seeds or is undetectable at some scales

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:
1. **Primary Failure:** Compute efficiency improvement < 5% (no meaningful benefit)
2. **Mechanism Failure:** Sharpness does not show detectable edge of stability plateau at Transformer scale
3. **Comparative Failure:** Adam-only baseline achieves equivalent or better final loss with same compute

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - this is a methodology contribution, not SOTA comparison mode.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): ~0.8 (large effect expected based on 10-20% improvement claim)
- Required runs: n ≥ 5 random seeds per configuration (power = 0.8, α = 0.05)
- Scale points: 4 (125M, 350M, 760M, 1B)
- Total experiments: 5 seeds × 4 scales × 2 conditions = 40 training runs

**Test Specification:**
- Method: Paired t-test comparing scheduled vs. baseline at matched compute
- Significance level: α = 0.05 (one-tailed, testing improvement)
- Report format: Mean difference, 95% CI, Cohen's d, p-value

**Reproducibility Requirements:**
- Fixed random seeds for initialization and data sampling
- μP parameterization for hyperparameter transfer
- Critical sharpness measurement protocol standardized

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does the edge of stability phenomenon (sharpness plateau at λ_max ≈ 2/η) reliably occur during large-scale Transformer training across different scales and random seeds?"
- Maps to: Primary prediction P3 (Sharpness Signature Reliability)
- Verification type: Empirical observation
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is sharpness-based optimizer transition the actual cause of improved training efficiency, operating through the proposed 3-step causal mechanism?"
- Maps to: Causal mechanism (Step 1 → Step 2 → Step 3 → Outcome)
- Phase 2B will decompose into 3 sub-hypotheses:
  - H-M1: Adam provides efficiency advantage in high-curvature early phase
  - H-M2: Sharpness plateau is a reliable and detectable transition signal
  - H-M3: SGD provides efficiency advantage after edge of stability
- Verification type: Causal analysis with ablations
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does sharpness-triggered optimizer scheduling outperform fixed-optimizer baselines in compute efficiency?"
- Maps to: Primary prediction P1 (Efficiency Improvement)
- Verification type: Comparative empirical
- Critical: Determines practical value

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-ScaleOptSched-v1
- [x] Confidence level specified: 0.78
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps)
- [x] Evidence for links table provided
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 provided, primary marked)
- [x] Falsification criteria are defined
- [x] Baselines are identified for comparison
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Compute Resources:** What GPU hours are required for 40 training runs (5 seeds × 4 scales × 2 conditions)? Estimate: ~2000 A100-hours for full validation.

2. **Critical Sharpness Implementation:** Is there an existing open-source implementation of critical sharpness (λ_c) measurement, or must we implement from Kalra et al. (2026)?

3. **Transition Protocol:** Should optimizer transition be a hard switch or gradual interpolation (e.g., linear blend of Adam and SGD over N steps)? This requires ablation study.

4. **Priority Verification Order:** Recommend SH1 (Existence) first - if edge of stability is not reliably detectable at scale, entire hypothesis fails. Then SH2 (Mechanism) to validate causal chain. Finally SH3 (Comparison) for practical validation.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
