# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-AML-v1
**Confidence Level:** 0.72

**Main Hypothesis:**
Under diffusion model inference on discrete pattern sets, if noise schedule variance is modulated via parameter λ ∈ [0,1], then the memory-generation trade-off shifts predictably (retrieval at low λ, novelty at high λ) because noise variance controls attractor basin depth and trajectory exploration in the diffusion-AM energy landscape.

**Alternative Hypothesis (H0):**
Noise schedule variance modulation via λ has no systematic effect on the memory-generation trade-off; outputs are determined by factors independent of inference-time noise scaling (e.g., training data distribution, model architecture, or random seed).

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| λ (lambda) | Independent | User-specified scalar ∈ [0,1] applied as multiplier to base noise schedule σ(t) | 0.0, 0.2, 0.4, 0.6, 0.8, 1.0 |
| Retrieval Accuracy | Dependent | Cosine similarity > 0.95 between generated sample and nearest training pattern | 0-100% of samples meeting threshold |
| Generation Novelty | Dependent | Minimum L2 distance to training set > 0.7 of maximum pairwise distance | 0-100% of samples meeting threshold |
| Trade-off Monotonicity | Dependent | Pearson correlation coefficient between λ and novelty score | r ∈ [-1, 1], target r > 0.9 |
| Training Data Size (N) | Controlled | Fixed at N=1000 discrete patterns | N=1000 (MNIST digits) |
| Base Noise Schedule | Controlled | Standard DDPM linear schedule σ_base(t) | Fixed implementation |
| Model Architecture | Controlled | Standard U-Net diffusion model | No modifications |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
[λ Parameter] → [Noise Variance σ(t)] → [Trajectory Dynamics] → [Memory/Generation Outcome]
```

**Step 1: λ → Noise Variance**
- Mechanism: σ_controlled(t) = λ · σ_base(t) directly scales the noise schedule
- At λ=0: Zero effective noise (deterministic trajectory)
- At λ=1: Full base noise schedule (standard diffusion)

**Step 2: Noise Variance → Trajectory Dynamics**
- Mechanism: Lower noise restricts denoising trajectories to attractor basins
- High noise enables exploration across multiple basins
- Based on Hess & Morris (2025) bifurcation theory for diffusion-AM systems

**Step 3: Trajectory Dynamics → Outcome**
- Mechanism: Trajectories converging to single attractors yield memory retrieval
- Exploratory trajectories through multiple basins yield novel interpolations
- Pham et al. (2025) demonstrates this phase transition exists empirically

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| λ → σ(t) | Mathematical definition | Direct scaling relationship | Strong |
| σ(t) → Trajectory | Hess & Morris (2025) | Bifurcation theory characterizes noise-induced transitions | Strong |
| Trajectory → Outcome | Pham et al. (2025) | Phase transitions between memorization and generalization | Strong |

**Key Tension:**
- **Tension:** Ambrogioni (2023) establishes equivalence for discrete patterns, but Pham et al. (2025) shows spurious states at boundaries may complicate control.
- **Resolution:** Two-stage approach tests simple baseline first; Stage 2 trajectory-aware enhancement addresses boundary complexity if needed.

### 1.4 Key Assumptions

1. **A1: Diffusion latent space embeds training patterns as attractors**
   - Evidence: Ambrogioni (2023) proves diffusion energy ≡ Hopfield energy asymptotically
   - Consequence if violated: No attractor structure to modulate; hypothesis fails completely

2. **A2: Noise variance modulation induces regime shifts without retraining**
   - Evidence: Inspired by Chen et al. (2024) attractor control in memristive networks
   - Consequence if violated: Requires training-time intervention; practical value diminishes

3. **A3: Memory-generation boundary exhibits predictable phase transition**
   - Evidence: Pham et al. (2025) demonstrates phase transitions exist in diffusion models
   - Consequence if violated: Non-monotonic or discontinuous trade-off; λ parameter unreliable

4. **A4: Attractor distance can be computed efficiently via k-NN approximation**
   - Evidence: Standard technique with O(log N) complexity for approximate nearest neighbor
   - Consequence if violated: Stage 2 computationally infeasible; limited to Stage 1 only

### 1.5 Scope & Boundaries

**Applies to:**
- Diffusion models trained on discrete pattern sets (MNIST, CIFAR discrete subsets)
- Inference-time modification only (no retraining required)
- Standard DDPM-style noise schedules
- Datasets with N ≤ 10,000 patterns for efficient distance computation

**Does NOT apply to:**
- Continuous distribution training (ImageNet full, natural images) without validation
- Non-diffusion generative models (VAEs, GANs, flow-based)
- Real-time applications requiring <10ms inference
- Text-to-image models with text conditioning

**Known Limitations:**
- Cross-domain analogy from dynamical systems is inspirational, not proven
- Computational overhead for Stage 2 (trajectory-aware) unknown
- Generalization from discrete patterns to continuous distributions requires separate validation

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Retrieval at Low λ):**
If λ ≤ 0.2, then retrieval accuracy ≥ 90% (where retrieval = cosine similarity > 0.95 to nearest training pattern)

*Measurement:*
- Generate 1000 samples at λ = 0.1, 0.2
- Compute cosine similarity to nearest training pattern for each
- Report % of samples exceeding 0.95 threshold
- Statistical test: One-sample t-test against 90% threshold, p < 0.05

*Basis:*
Low noise restricts trajectories to attractor basins, converging to memorized patterns (Ambrogioni 2023, Pham et al. 2025)

**Secondary Predictions:**

**P2 (Novelty at High λ):**
If λ ≥ 0.8, then generation novelty ≥ 80% (where novelty = min L2 distance > 0.7 of max pairwise distance)

**P3 (Monotonic Trade-off):**
If λ varies from 0 to 1, then trade-off is monotonic (Pearson r > 0.9 between λ and novelty score)

**P4 (Stage 2 Efficiency - Conditional):**
If Stage 1 achieves < 80% of targets AND Stage 2 is implemented, then inference overhead < 50%

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** Retrieval accuracy at λ ≤ 0.2 is < 70% (statistically worse than expected)

2. **Mechanism Failure:** No monotonic relationship exists (r < 0.5) between λ and novelty

3. **Baseline Failure:** Performance at λ = 1.0 differs significantly from standard diffusion (implementation error)

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - This hypothesis proposes absolute performance thresholds, not SOTA comparison.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (expected): Large (d > 0.8) based on theoretical phase transition
- Required runs: n ≥ 20 per λ value (6 values × 20 runs = 120 total)
- Statistical power: 0.8

**Test Specification:**
- Primary tests: One-sample t-tests against thresholds
- Correlation test: Pearson correlation with bootstrapped confidence intervals
- Significance level: α = 0.05 (one-tailed for directional predictions)
- Report format: Mean ± Std Dev, 95% CI, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does inference-time noise variance modulation affect output characteristics in diffusion models trained on discrete patterns?"
- Maps to: P1, P2 (existence of effect)
- Verification type: Empirical
- Critical: MUST PASS for hypothesis to proceed

**SH2 (Mechanism):**
"Is noise variance modulation the causal mechanism for memory-generation trade-off shift?"
- Maps to: Causal chain (λ → σ(t) → trajectory → outcome)
- Will decompose into N=3 sub-hypotheses in Phase 2B:
  - H-M1: λ → σ(t) scaling functions correctly
  - H-M2: σ(t) → trajectory dynamics (bifurcation behavior)
  - H-M3: trajectory → outcome correlation
- Verification type: Causal analysis
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does our approach provide meaningful control absent in standard diffusion?"
- Maps to: P3 (monotonic control), comparison to λ=1.0 baseline
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 2 + 3 = 5 (SH1, H-M1, H-M2, H-M3, SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-AML-v1
- [x] Confidence level specified: 0.72
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table complete)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (4 total, P1 marked primary)
- [x] Falsification criteria are defined
- [x] Baselines are identified for comparison
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** What GPU memory and compute time needed for 120+ generation runs with varying λ? Estimate: 2-4 GPU hours on single A100.

2. **Data Preparation:** Is MNIST 1000-pattern subset sufficient or should we also test CIFAR-10 subset for robustness?

3. **Priority Verification Order:** Recommend SH1 (existence) first, then SH2 (mechanism), finally SH3 (comparison) - sequential dependency structure.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
