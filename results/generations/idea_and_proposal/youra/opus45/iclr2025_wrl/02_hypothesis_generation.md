# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CBF-Diffusion-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under contact-rich robot manipulation with definable safety constraints, if Control Barrier Function (CBF) constraints are integrated during diffusion policy training via Lagrangian relaxation, then the learned policy will achieve comparable task success rates while significantly reducing safety violations compared to inference-time CBF methods, because training-time integration shapes the action distribution to inherently avoid unsafe regions rather than filtering them post-hoc.

**Alternative Hypothesis (H0):**
Training-time CBF integration provides no significant advantage over inference-time CBF filtering (CoBL-Diffusion) in terms of safety-performance trade-off, or the gradient conflict between task and safety objectives prevents convergence to a viable policy.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| CBF integration method | Independent | training-time (Lagrangian) vs inference-time (CoBL-Diffusion) vs post-hoc (SRL-VIC) | 3 levels |
| Lagrangian weight λ | Independent | Learned via dual gradient ascent with learning rate α_λ | [0.01, 10.0] |
| Training phase schedule | Independent | Phase 1: frozen pretrained CBF, Phase 2: joint fine-tuning | 2 phases |
| Task success rate | Dependent | Percentage of episodes achieving goal within time limit on CALVIN benchmark | [0%, 100%], target ≥82% |
| Safety violation rate | Dependent | Count of CBF constraint violations (h(s,a) < 0) per episode | [0, ∞), target <2% |
| Inference latency | Dependent | Wall-clock time per action in milliseconds | [10ms, 100ms], target no increase |
| Robot embodiment | Controlled | Fixed to Franka Panda arm | Fixed |
| Task domain | Controlled | Contact-rich manipulation tasks from CALVIN benchmark | Fixed |
| CBF architecture | Controlled | 3-layer MLP with ReLU activations | Fixed |
| Diffusion architecture | Controlled | Diffusion Policy (Chi et al., 2023) with DDPM scheduler | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: CBF Loss Integration
    L_safety = max(0, -h(s,a)) provides gradient signal penalizing unsafe actions
    ↓
Step 2: Lagrangian Balancing
    λ dynamically balances L_task and L_safety, preventing mode collapse
    ↓
Step 3: Phased Training Stability
    Frozen CBF → Joint fine-tuning ensures stable learning dynamics
    ↓
Step 4: Distribution Shaping
    Action distribution shifts to have lower density in unsafe regions
    ↓
[OUTCOME]: Inherently safe policy without inference-time overhead
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | CoBL-Diffusion (2024) | CBF gradients successfully guide diffusion denoising | Strong |
| Step2 → Step3 | APPO (Dai et al., 2023) | Augmented Lagrangian ensures stable convergence in constrained RL | Strong |
| Step3 → Step4 | Neural Barrier Certificate (Yang et al., 2023) | Phased training with frozen safety component works | Medium |
| Step4 → Outcome | Diffusion Policy (Chi et al., 2023) | Diffusion models shape action distributions effectively | Strong |

**Key Tension:**
- **Tension:** CoBL-Diffusion applies CBF at inference time (post-hoc filtering), while our approach applies at training time (distribution shaping). The question is whether training-time integration yields genuinely different learned distributions.
- **Resolution:** Test whether the action distribution itself changes (measured via KL divergence from vanilla policy in unsafe regions).

### 1.4 Key Assumptions

1. **Neural CBF Accuracy:** Neural CBF can accurately represent the safe set for contact-rich manipulation tasks
   - Evidence: Yang et al. (2023) demonstrated neural barrier certificates achieve near-zero violations
   - Consequence if violated: Safety constraint would be meaningless; need hand-crafted CBF instead

2. **CBF Gradient Informativeness:** CBF gradients are informative during early training
   - Evidence: CoBL-Diffusion successfully uses CBF gradients at inference
   - Consequence if violated: Training would fail to incorporate safety; need curriculum learning

3. **Lagrangian Convergence:** Lagrangian relaxation converges to balanced task-safety solution
   - Evidence: APPO, CVaR-CPO literature demonstrates stable Lagrangian optimization
   - Consequence if violated: Policy oscillates between unsafe-high-performance and safe-low-performance

4. **Phased Training Stability:** Phased training prevents CBF-policy co-adaptation instability
   - Evidence: Standard practice in safe RL
   - Consequence if violated: Both CBF and policy may degrade; need full separation

### 1.5 Scope & Boundaries

**Where hypothesis applies:**
- Contact-rich robot manipulation with definable geometric safety constraints
- Tasks where CBF can be learned from demonstration data with collision labels
- Continuous action spaces (e.g., robotic arms)

**Where hypothesis does NOT apply:**
- Tasks with context-dependent safety requirements (e.g., social navigation)
- High-dimensional action spaces where CBF becomes intractable
- Domains without clear safe/unsafe boundaries

**Known limitations:**
- Requires training CBF first (additional overhead)
- Lagrangian hyperparameter α_λ requires tuning

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Safety Violation Rate vs SOTA ~5-10%):**
Our training-time CBF approach will achieve safety violation rate <2% while maintaining task success ≥82%

*Measurement:*
- Safety violation rate: Count of h(s,a) < 0 per episode, averaged over 100 rollouts
- Statistical test: Two-sample t-test, p < 0.05

*Success Criteria:*
- Primary: Safety violation rate <2% with task success ≥82%
- Falsification: Safety violation rate >15% OR task success <75%

**Secondary Predictions:**

**P2 (Inference Latency Advantage):**
Our approach achieves equivalent inference latency to vanilla Diffusion Policy (no CBF overhead), while CoBL-Diffusion incurs 20-50% overhead

**P3 (Distribution Shift Evidence):**
Learned action distribution shows measurably lower density in unsafe regions (KL divergence test)

**Falsification Criteria:**

The hypothesis will be **REJECTED** if:
1. Safety violation rate >15% (worse than post-hoc filtering)
2. Task success rate <75% (significant degradation)
3. No measurable distribution shift in unsafe regions
4. CoBL-Diffusion achieves equivalent trade-off

### 1.7 SOTA Baseline

| Method | Safety Approach | Violation Rate | Task Success | Inference Overhead |
|--------|-----------------|----------------|--------------|-------------------|
| Vanilla Diffusion Policy | None | ~15-20% | ~85% | Baseline |
| CoBL-Diffusion | Inference-time CBF | ~5-10% | ~80% | +30-50% |
| **Ours (Target)** | Training-time CBF | <2% | ≥82% | 0% |

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 25 per condition (Cohen's d = 0.8, power = 0.8)
**Tests:** Two-sample t-test (safety), Paired t-test (task success)
**Significance:** α = 0.05 (one-tailed for safety improvement)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does CBF-conditioned diffusion training produce policies with lower safety violation rates than vanilla diffusion policy under contact-rich manipulation?"

**SH2 (Mechanism):**
"Is the Lagrangian CBF-conditioning mechanism the actual cause of improved safety?"

Decomposes into N=4 sub-hypotheses:
- H-M1: CBF gradient signal → Penalizes unsafe actions during training
- H-M2: Lagrangian λ → Balances task and safety without mode collapse
- H-M3: Phased training → Enables stable learning dynamics
- H-M4: Distribution shaping → Reduces density in unsafe regions

**SH3 (Comparison):**
"Does training-time CBF integration outperform inference-time (CoBL-Diffusion) on the safety-performance Pareto frontier?"

**Total sub-hypotheses: 2 + 4 = 6**

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-CBF-Diffusion-v1
- [x] Confidence: 0.85
- [x] H0 defined
- [x] All variables operationalized
- [x] Causal mechanism (N=4) with evidence
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] 3 testable predictions (primary marked)
- [x] Falsification criteria (4 conditions)
- [x] Baselines: CoBL-Diffusion, SRL-VIC
- [x] SH1/SH2/SH3 defined

### Open Questions

1. **Resources:** ~56 GPU hours total (48 training + 8 CBF pretraining)
2. **Data:** CALVIN dataset (public); safety labels from collision detection
3. **Priority:** SH1 → SH2 (H-M1, H-M2) → SH3

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
