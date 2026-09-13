# Phase 2A Refinement Summary: Geometric Robustness Hypothesis

**Generated:** 2026-04-24T15:45:00Z  
**Workflow:** phase2a-dialogue v10.0.0  
**Gap:** GAP-1 - Loss Landscape Differences (Spurious vs Core)  
**Hypothesis ID:** H-GeometricRobustness-v1  
**Status:** VALIDATED (15 exchanges, unanimous consensus)

---

## Executive Summary

We propose that **curvature subspace orientation** (not scalar flatness) explains why standard ERM training fails on spurious correlation benchmarks. Solutions that rely on spurious features exhibit high alignment between minority-group gradients and Hessian outlier eigenspaces (defined via Marchenko-Pastur bulk edge). SGD's implicit bias toward flat directions creates directional flow away from these sharp, spurious-aligned regions toward flatter, core-feature-aligned regions—explaining the ROUTE_TO_0 observation that task-alignment dominates learning regardless of intrinsic feature properties.

**Confidence:** 80% | **Novelty:** First mechanistic link between loss landscape geometry and spurious correlations | **Feasibility:** All experiments use existing tools/benchmarks

---

## Core Hypothesis

> **If** we measure curvature subspace orientation via Marchenko-Pastur-defined Hessian outlier alignment A(w),  
> **Then** solutions with high minority-gradient alignment to this subspace will exhibit poor worst-group accuracy,  
> **Because** SGD dynamics preferentially flow along locally flat directions away from sharp, spurious-feature-aligned curvature concentrations.

**Null Hypothesis (H₀):** No systematic relationship between A(w) and worst-group accuracy exists. Geometric orientation does not predict distribution shift robustness.

---

## The Mechanism: Four Causal Steps

### Step 1: Spurious Features → Sharp Curvature
Spurious correlations create concentrated curvature in specific Hessian eigenspace subspaces (Sagun et al.'s Gauss-Newton decomposition shows Hessian outliers align with data structure).

**Falsifier:** If spurious and core solutions show indistinguishable eigenvalue spectra.

### Step 2: Sharp Directions → Minority Gradient Alignment
These sharp directions align with minority-group gradient directions (high A(w)), because minority groups expose spurious correlations.

**Falsifier:** If minority gradients project equally onto top eigenspaces in ERM and DRO solutions.

### Step 3: SGD Implicit Bias → Directional Flow
SGD preferentially follows locally flat directions to minimize curvature-induced gradient variance (well-known flatness bias; Garipov shows abundance of low-loss flat directions).

**Falsifier:** If SGD trajectories show no directional bias or early A(w) doesn't predict final robustness.

### Step 4: Low A(w) → Better Robustness
Solutions converging to regions with lower A(w) exhibit better worst-group accuracy through functional coupling within mode-connected manifolds.

**Falsifier:** If FGE samples show geometric variation without phenotype variation, or linear interpolation shows no monotonic coupling.

---

## Key Variables

### Independent Variable
- **Training Method:** ERM vs group-DRO vs FGE-sampled (manipulated via loss function)

### Dependent Variables (Primary)
- **Curvature Subspace Alignment A(w):** ||P_S_out g_minority||² / ||g_minority||²  
  where S_out = eigenvectors above Marchenko-Pastur bulk edge
- **Worst-Group Accuracy:** Min accuracy across subgroups [0,100]%

### Controlled Variables
- Batch size: {32, 128, 512} (verify orientation stability)
- Architecture: ResNet-50 (consistency)
- Random seed: 20 independent runs (statistical power)

---

## Five Testable Predictions

### P1: Endpoint Geometric Signature ⭐
**Statement:** ERM solutions exhibit significantly higher A(w) than group-DRO solutions.

**Test:** Train 20 seeds each ERM/DRO on Waterbirds; compute A(w) at convergence; two-sample t-test.

**Success:** p<0.01, Cohen's d>0.8, stable across 3 batch sizes.

**Falsification:** Distributions overlap (d<0.5) or effect disappears under batch variation.

---

### P2: Functional Geometric Coupling (FGE) ⭐
**Statement:** Along FGE-sampled paths, curvature alignment and worst-group accuracy covary.

**Test:** FGE training with M=20 checkpoints; compute Spearman ρ(A(w), WGA).

**Success:** ρ>0.6, p<0.01.

**Falsification:** ρ<0.3 or p>0.05 (geometry doesn't functionally encode robustness).

---

### P3: Early-Epoch Predictive Power ⭐
**Statement:** Early-epoch A(w) predicts final worst-group accuracy beyond scalar flatness.

**Test:** At 10% training, measure A(w) and λ_max; regress final WGA on both; test incremental R².

**Success:** A(w) significant (p<0.01), incremental R²>10% beyond λ_max+loss.

**Falsification:** A(w) becomes non-significant when λ_max is controlled.

---

### P4: Label Noise Robustness
**Statement:** Geometry-robustness correlation survives 10% minority label noise.

**Test:** Repeat E1 with random 10% label flips in minority group.

**Success:** Effect size >50% of clean-data effect.

**Falsification:** Correlation collapses to near-zero.

---

### P5: Linear Interpolation Monotonicity
**Statement:** Linear interpolation shows monotonic A(w)-WGA coupling without path optimization.

**Test:** Sample θ(t)=(1-t)θ_ERM + tθ_DRO, t∈[0,1]; compute Spearman ρ(A(w)(θ(t)), WGA(θ(t))).

**Success:** ρ>0.7.

**Falsification:** Non-monotonic or ρ<0.4.

---

## Critical Assumptions (A1-A5)

**A1 (Marchenko-Pastur Validity):** MP bulk edge accurately identifies signal vs noise threshold in over-parameterized networks.  
*Consequence if violated:* Subspace definition becomes arbitrary, alignment metric unstable.

**A2 (Minority Gradient Informativeness):** Minority-group gradients reliably indicate spurious-vs-core feature directions.  
*Consequence if violated:* Alignment metric overfits subgroup sampling noise.

**A3 (Orientation Stability):** Curvature orientation is more stable than magnitude across batch sizes and parameterizations.  
*Consequence if violated:* Geometric signature collapses under hyperparameter variation.

**A4 (SGD Implicit Bias):** SGD implicit bias toward flat directions creates directional flow in optimization dynamics.  
*Consequence if violated:* No mechanism linking local geometry to trajectory preference.

**A5 (Mode Connectivity Compatibility):** Mode connectivity doesn't preclude functional variation within connected components.  
*Consequence if violated:* FGE test would show geometric variation without phenotype shifts.

---

## Scope & Boundaries

### ✅ Applies To
- Supervised classification with spurious correlations
- Over-parameterized DNNs (M≥N regime)
- Benchmarks with ground-truth subgroup labels (Waterbirds, CelebA, Colored MNIST)
- SGD-based optimization (including Adam, momentum variants)

### ❌ Does NOT Apply To
- Under-parameterized models (M<<N, MP assumptions break)
- Unsupervised/self-supervised learning (no minority gradients)
- Tasks without distribution shift structure
- Non-gradient-based optimization (evolutionary algorithms, MCMC)

### ⚠️ Known Limitations
- Requires group labels for validation (though not training)
- Hessian computation: O(N·M) per eigenvalue (tractable but non-trivial)
- MP edge estimation sensitive to tail behavior
- Parameterization invariance not guaranteed; requires symmetry controls

---

## Experimental Setup

### Datasets
- **Waterbirds** (primary): 4,795 training images, background-class spurious correlation
- **CelebA** (cross-validation): Gender-attribute spurious correlations, 162,770 training images
- **Colored MNIST** (controlled validation): Color-digit spurious correlation, tunable strength

### Architecture
- **ResNet-50** (standard, enables reproducibility via Li et al. filter normalization)

### Training Methods
1. **Standard ERM:** Cross-entropy loss, SGD, standard augmentation
2. **Group-DRO:** Robust reweighting (requires group labels)
3. **Fast Geometric Ensembling (FGE):** Cyclical learning rate (Garipov et al. 2018)

### Computational Requirements
- Hessian-vector products via power iteration (pytorch-hessian-eigenthings)
- 20 seeds × 3 batch sizes × 3 methods = 180 training runs
- **Estimated:** ~50 GPU-hours per dataset (ResNet-50 on V100)

---

## What Makes This Novel

### Preserved Novelty
**First application of loss landscape geometric analysis** (Hessian subspace orientation) **to spurious correlation problem.**

### Key Innovation
Marchenko-Pastur-defined curvature subspace alignment as mechanistic explanation for task-aligned feature dominance, with 5 falsifiable predictions.

### Differentiation from Prior Work

| Prior Work | Our Contribution |
|------------|------------------|
| **SAM (Foret 2020)** - seeks flat minima | We target **orientation** relative to subgroup gradients, not scalar flatness. SAM is feature-agnostic; we're distribution-shift-aware. |
| **Group-DRO (Sagawa 2020)** - robust optimization | We explain **WHY ERM fails** via geometric mechanism; enable **label-free diagnostics** via A(w) monitoring. DRO is solution; we provide foundation. |
| **Sagun/Li/Garipov (2017-2018)** - loss landscape analysis | They study architecture/optimization effects. We apply their tools to **spurious correlation domain**—novel synthesis, not novel methods. |

---

## Discussion Evolution (15 Exchanges)

### Iteration 1: Vague Claim
*"Loss landscape differences between spurious and core solutions"*

**Critique:** Prof. Vera: "What constitutes spurious vs core region?" Dr. Sage: "Mode connectivity contradicts geometric distinction."

### Iteration 2: Eigenvalue Magnitude
*"Hessian eigenvalue magnitude distinguishes solutions"*

**Critique:** Prof. Rex: "Magnitude depends on parameterization—arbitrary threshold." Prof. Pax: "How does this explain ROUTE_TO_0?"

### Iteration 3: Breakthrough - Orientation via MP Subspace
*"Curvature ORIENTATION via Marchenko-Pastur subspace alignment"*

**Progress:** Dr. Nova: "Now intrinsic and testable." Dr. Ally: "Need explicit minority gradient operationalization."

### Iteration 4: Causal Mechanism
*"4-step chain: Gauss-Newton structure → minority alignment → SGD bias → robustness"*

**Progress:** Prof. Vera: "Each step now independently falsifiable."

### Iteration 5: Final Refinement
*"5 predictions with quantitative criteria; FGE test resolves mode connectivity tension"*

**Consensus:** All personas: **"VALIDATED—ready for Phase 2B."**

---

## Major Objections Resolved

### 🔴 "Mode connectivity contradicts geometric distinction"
**Resolution:** Distinct regions within connected manifold—FGE samples test functional coupling without requiring disconnected components.

### 🔴 "Marchenko-Pastur threshold arbitrary in neural networks"
**Resolution:** Random matrix theory validated for over-parameterized regime (Sagun et al.); experiments test edge stability across architectures.

### 🔴 "Just rediscovering scalar flatness?"
**Resolution:** Explicit control experiments (P3) test incremental predictive power of orientation beyond λ_max.

### 🔴 "Requires group labels (impractical)"
**Resolution:** Only for validation, not training. A(w) enables label-free early diagnostics.

---

## Phase 2B Readiness

### Status: ✅ READY

**SH1 (Existence):** Loss landscape tools (pytorch-hessian-eigenthings, pytorch_loss_landscape) and spurious benchmarks (Waterbirds, CelebA) exist and are accessible.

**SH2 (Mechanism):** Curvature subspace orientation (MP-defined A(w)) must systematically differ between ERM and DRO; must predict early-epoch robustness; must couple functionally via FGE.

**SH3 (Comparison):** Compare against scalar flatness (λ_max), Group-DRO (requires labels), SAM (feature-agnostic flatness).

### Open Questions for Phase 2B
1. Does MP edge estimation remain stable under non-Gaussian initialization or heavy-tailed activations?
2. How does parameterization invariance affect alignment metric stability?
3. Can we extend to self-supervised learning where minority gradients are not well-defined?

---

## Final Persona Verdicts

🔭 **Dr. Nova (Novelty):** STRONG - Genuine paradigm synthesis bridging loss landscapes and spurious correlations  
🔬 **Prof. Vera (Falsifiability):** STRONG - Precise, with 5 independent falsification opportunities  
🎯 **Dr. Sage (Significance):** STRONG - Addresses documented gap, enables label-free diagnostics  
⚙️ **Prof. Pax (Feasibility):** STRONG - All experiments technically sound and computationally tractable  
🛡️ **Dr. Ally (Synthesis):** Unified framework achieved through iterative refinement  
🔍 **Prof. Rex (Critique):** Rigorous and feasible; remaining concerns have mitigations

**Unanimous Consensus:** VALIDATED - Ready for Phase 2B experimental verification.

---

## What Success Unlocks

If experiments succeed (E1+E2+E3):

1. **Diagnostic Tool:** Monitor A(w) during training for label-free robustness assessment
2. **Optimization Target:** Design loss functions that penalize high A(w) (geometry-aware robustification)
3. **Architecture Guidance:** Choose architectures that naturally produce low A(w)
4. **Theory Building:** Geometric structure becomes organizing principle for understanding spurious correlations

**If experiments fail:** We rule out geometric explanations and redirect research toward alternative mechanisms. Either outcome advances the field.

---

## References to Established Work

- **Li et al. (2018):** Filter normalization for loss landscape visualization
- **Sagun et al. (2017):** Hessian eigenvalue analysis, Gauss-Newton decomposition, Marchenko-Pastur theory
- **Garipov et al. (2018):** Mode connectivity, Fast Geometric Ensembling (FGE), Bezier curves
- **Sagawa et al. (2020):** Group-DRO, Waterbirds/CelebA benchmarks
- **Foret et al. (2020):** Sharpness-Aware Minimization (SAM)

---

**Next Step:** Phase 2B experimental validation (step-01 through step-11) to test all 5 predictions.
