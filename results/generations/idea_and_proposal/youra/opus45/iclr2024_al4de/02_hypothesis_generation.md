# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-AGANO-v1
**Confidence Level:** 0.88

**Main Hypothesis:**
Under conditions of PDEs with localized sharp gradients (boundary layers, shocks, discontinuities), if a learned complexity detector identifies high-gradient regions and a Gumbel-softmax soft mode allocator assigns more Fourier spectral modes to those regions, then the neural operator will achieve lower L2 relative error per FLOP compared to fixed-mode allocation, because adaptive resource allocation concentrates computational effort where solution complexity requires it, analogous to visual cortex saliency processing.

**Alternative Hypothesis (H0):**
There is no significant difference in accuracy-per-FLOP between fixed uniform mode allocation and saliency-guided adaptive mode allocation; the overhead from complexity detection negates any potential savings from adaptive allocation.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Mode allocation strategy | Independent | Binary: fixed uniform (baseline) vs. saliency-guided adaptive (AGANO) | {fixed, adaptive} |
| Complexity detector output | Independent | Per-region complexity scores from MobileNet-style CNN (2% FLOPs budget) | [0, 1] per spatial region |
| Gumbel-softmax temperature | Independent | Temperature schedule τ=5→0.1 over training epochs | τ ∈ [0.1, 5.0] |
| L2 relative error | Dependent | ‖u_pred - u_true‖₂ / ‖u_true‖₂ averaged over test set | 0.1% - 10% typical |
| FLOPs per inference | Dependent | Floating point operations per forward pass | 10⁸ - 10¹⁰ |
| Resolution capability | Dependent | Maximum effective resolution at fixed compute budget | 256×256 to 2048×2048 |
| PDE type | Controlled | Navier-Stokes, Darcy, Burgers, Reaction-Diffusion from PDEBench | 4 families |
| Domain resolution | Controlled | Grid sizes for evaluation | 256×256, 512×512 |
| Training data size | Controlled | Samples per PDE family | 1000 samples |
| Baseline FNO config | Controlled | Standard FNO with 12 fixed modes, 4 Fourier layers | Fixed architecture |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Complexity Detection
  ↓
Step 2: Saliency Map → Soft Mode Weights (Gumbel-softmax)
  ↓
Step 3: Soft Mode Weights → Adaptive Spectral Convolution
  ↓
Step 4: Adaptive Spectral Convolution → Improved Accuracy/FLOP
  ↓
[Outcome]: Lower L2 relative error at equal or reduced FLOPs
```

**Step 1 - Complexity Detection:**
MobileNet-style depthwise separable CNN (3 layers, 2% FLOPs budget) takes coarse solution estimate as input and outputs per-region complexity scores indicating local gradient magnitudes.

**Step 2 - Saliency to Mode Weights:**
Gumbel-softmax transformation converts continuous complexity scores to differentiable mode allocation weights. Temperature annealing (τ=5→0.1) ensures convergence to near-discrete selection during training.

**Step 3 - Adaptive Spectral Convolution:**
Mode weights modulate Fourier spectral convolution - more modes (up to 32) allocated to high-complexity regions, fewer modes (down to 4) in smooth regions. V-cycle architecture transfers information across scales.

**Step 4 - Efficiency Gain:**
Concentrating spectral modes where needed reduces error in critical regions (boundary layers, shocks) while saving computation in smooth regions, achieving higher accuracy per FLOP.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | MSVMamba (Shi 2024) | Hierarchy-in-hierarchy multi-scale processing is effective for complexity detection | Strong |
| Step2 → Step3 | Gumbel-softmax (Jang 2017) | Standard technique for differentiable discrete selection, widely validated | Strong |
| Step3 → Step4 | Geo-FNO (Li 2022) | FNO can be extended with learned geometric components; 2x more accurate | Strong |
| Step4 → Outcome | M2NO (Li 2024) | Multigrid-neural operator integration achieves significant speedups | Medium |

**Key Tension:**
- **Tension:** FNO literature (Li 2020) achieves SOTA with fixed 12-mode truncation, suggesting fixed allocation may be sufficient. However, recent benchmarking (Current 2026) shows "significant limitations of present architectures" for high-frequency components critical to turbulent flows.
- **Resolution:** This verification plan tests whether adaptive allocation specifically benefits PDEs with localized sharp gradients, where fixed truncation is known to struggle.

### 1.4 Key Assumptions

| # | Assumption | Evidence | Consequence if Violated |
|---|------------|----------|------------------------|
| A1 | PDE solutions exhibit spectral sparsity - smooth regions have few significant Fourier modes | FNO (Li 2020) uses only 12 modes and achieves SOTA on standard benchmarks | If PDE solutions are spectrally dense everywhere, adaptive allocation provides no benefit over uniform allocation |
| A2 | Gradient magnitude is a reliable proxy for solution complexity requiring more spectral modes | Numerical analysis theory; high gradients = high frequency content | If complexity is not correlated with gradients (e.g., internal wave patterns), detector will misallocate modes |
| A3 | Gumbel-softmax soft allocation approximates discrete allocation at low temperatures (τ<0.5) | Jang et al. 2017; widely validated in discrete latent variable models | If soft allocation remains "fuzzy," efficiency gains from mode reduction will be minimal |
| A4 | Complexity detector overhead (2% FLOPs) is negligible compared to spectral convolution savings | MobileNet efficiency; depthwise separable convolutions | If overhead exceeds 10% FLOPs, net efficiency gain disappears for moderate complexity PDEs |

### 1.5 Scope & Boundaries

**Applies To:**
- Elliptic, parabolic, hyperbolic PDEs with localized sharp gradients
- Navier-Stokes equations with localized turbulence
- 2D and 3D domains with boundary layers, discontinuities

**Does NOT Apply To:**
- PDEs with uniformly distributed high-frequency content (fully-developed turbulence at all scales)
- Very low-resolution domains (64×64) where mode count is already minimal
- Real-time inference scenarios where detector latency is critical

**Known Limitations:**
- Complexity detector adds 2% FLOPs overhead
- Multi-task training increases total training time 2-3x
- Temperature schedule requires tuning for convergence stability

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Accuracy per FLOP improvement):**
AGANO will achieve ≥30% reduction in L2 relative error compared to FNO baseline at equal FLOPs, OR achieve equal L2 relative error with ≥50% fewer FLOPs, on PDEs with localized sharp gradients.

*Measurement:* L2 relative error, FLOPs via PyTorch profiler, paired t-test n≥20, p<0.05
*Falsification:* <10% improvement in accuracy/FLOP triggers WEAK SUPPORT

**Secondary Predictions:**

**P2 (Complexity detector localization):** >90% IoU in localizing high-gradient regions vs ground-truth gradient maps

**P3 (Mode allocation convergence):** Entropy <0.5 bits per region at τ≤0.5, demonstrating near-discrete allocation

**P4 (Cross-PDE generalization):** >80% of single-PDE performance when evaluated on held-out PDE configurations

**Falsification Criteria:**
REJECT if ANY occur:
1. **Primary Failure:** <10% improvement in accuracy/FLOP across ALL tested PDEs
2. **Mechanism Failure:** Complexity detector <70% IoU in gradient localization
3. **Convergence Failure:** Entropy >1.5 bits at τ≤0.3
4. **Overhead Failure:** Detector + allocation overhead >15% of total FLOPs

### 1.7 SOTA Baseline (Optional)

**Mode: Absolute Performance Validation**

| Method | Source | Performance Context |
|--------|--------|-------------------|
| FNO (fixed 12 modes) | Li et al. 2020 | ~1% L2 error on Navier-Stokes |
| Geo-FNO | Li et al. 2022 | 2x more accurate than FNO |
| U-FNO | Wen et al. 2021 | Multi-scale via U-Net skip connections |

### 1.8 Statistical Verification Design

**Sample Size:** n≥20 per configuration (effect size d=0.8, power=0.8)
**Configurations:** 2 models × 4 PDEs × 2 resolutions = 16
**Total runs:** 320 experiments

**Tests:** Paired t-test (primary), ANOVA (multi-factor), Cohen's d + 95% CI
**Format:** Mean ± Std Dev [95% CI], Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does saliency-guided adaptive mode allocation achieve measurably different accuracy/FLOP than fixed mode allocation on PDEs with localized sharp gradients?"
- Maps to: Primary prediction P1
- Verification type: Empirical comparison
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism the actual cause of any observed improvement?"
- Maps to: Causal mechanism with N=4 steps
- Will decompose into 4 sub-hypotheses:
  - H-M1: Complexity detector accurately localizes high-gradient regions
  - H-M2: Gumbel-softmax converges to near-discrete allocation
  - H-M3: Adaptive spectral convolution is computationally efficient
  - H-M4: Concentrated computation improves accuracy in critical regions
- Verification type: Ablation studies and component analysis

**SH3 (Comparison):**
"Does AGANO outperform existing neural operator baselines (FNO, Geo-FNO, U-FNO) on multi-scale PDE benchmarks?"
- Maps to: Secondary predictions P2-P4
- Verification type: Comparative empirical evaluation

**Total sub-hypotheses in Phase 2B:** 2 + 4 = 6 (SH1: 1, SH2: 4, SH3: 1)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-AGANO-v1
- [x] Confidence level specified: 0.88
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization (8 variables)
- [x] Causal mechanism has evidence at each step (N=4)
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated (4 assumptions)
- [x] At least 2 testable predictions: 4 predictions (P1-P4)
- [x] Falsification criteria defined (4 conditions)
- [x] Baselines identified (FNO, Geo-FNO, U-FNO)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** ~32GB GPU, ~48 hours training for multi-task 512×512
2. **Data Availability:** PDEBench for Navier-Stokes, Darcy, Burgers; verify Reaction-Diffusion
3. **Priority Order:** SH1 (gate) → SH2-H-M1 (detector) → remaining mechanism → SH3

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
