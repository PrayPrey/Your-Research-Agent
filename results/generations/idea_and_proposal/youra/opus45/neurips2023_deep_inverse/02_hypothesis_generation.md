# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-GAMDP-v1
**Confidence Level:** 0.80

**Main Hypothesis:**
Under the condition of medical imaging inverse problems with limited target modality data, if we decompose diffusion priors into a geometry-aware universal encoder trained on multi-modal data (MRI, CT, X-ray) plus lightweight modality-specific LoRA adapters (<5% parameters), then cross-modality transfer will achieve comparable reconstruction quality (PSNR within 1dB, SSIM within 0.02) to modality-specific baselines while requiring significantly less target modality training data, because geometric structural regularities (edges, boundaries, smoothness) are shared across medical imaging modalities and can be captured in a modality-agnostic latent space.

**Alternative Hypothesis (H0):**
There is no meaningful cross-modality transfer of geometric priors in diffusion models for medical imaging inverse problems - modality-specific training is always required to achieve competitive reconstruction quality, regardless of architectural decomposition.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Architecture Modularity | Independent | Binary: Modular (geometric encoder + adapters) vs Monolithic (single model per modality) | {Modular, Monolithic} |
| Geometric Latent Space Design | Independent | Encoder trained with geometry-preserving losses (edge preservation, boundary consistency, smoothness) on MRI+CT+X-ray | Latent dimension: 4-16 channels |
| Reconstruction Quality | Dependent | PSNR (dB) and SSIM measured on test set reconstructions vs ground truth | PSNR: 25-40 dB, SSIM: 0.80-0.98 |
| Transfer Efficiency | Dependent | Number of target modality samples required to match baseline quality (within 1dB PSNR) | 10%-100% of full dataset |
| Adapter Size | Controlled | Fixed at <5% of total model parameters (LoRA rank r=4-16) | 1-5% of base model |
| Base Architecture | Controlled | Latent diffusion model (Stable Diffusion-style UNet backbone) | Fixed architecture |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Multi-modal training data (MRI+CT+X-ray)
    ↓ [Forces encoder to learn only shared features]
Step 2: Geometry-preserving latent space
    ↓ [Diffusion learns universal structural prior]
Step 3: Universal prior + LoRA adapters
    ↓ [Adapters specialize modality-dependent components]
Outcome: Efficient cross-modality transfer with reduced data requirements
```

**Detailed Mechanism:**

1. **Link 1 (Data → Latent Space):** Training on diverse medical imaging modalities forces the geometric encoder to learn representations that are invariant to modality-specific characteristics. Features that only appear in one modality are averaged out; only shared geometric regularities (edges, boundaries, anatomical structures) persist.

2. **Link 2 (Latent Space → Universal Prior):** The diffusion model trained in this geometric latent space learns a score function ∇_z log p(z) that captures universal structural regularities without encoding modality-specific noise patterns or textures.

3. **Link 3 (Universal Prior → Reconstruction):** When adapting to a new modality, LoRA adapters inject modality-specific knowledge (texture patterns, noise characteristics, acquisition physics) while the frozen universal prior provides structural guidance.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | MARBLE (Nature Methods 2025) | Geometric manifold learning transfers across dynamical systems | Medium |
| Step 1 → Step 2 | IP-Adapter (Archon KB) | Adapter-based conditioning preserves structure while changing style | Strong |
| Step 2 → Step 3 | Neural Operators (Kacmaz 2025) | Resolution-invariant representations combine with diffusion for generalization | Medium |
| Step 3 → Outcome | LoRA (Hu et al. 2022) | <1% parameters sufficient for task adaptation in large models | Strong |

**Key Tension:**
- **Tension:** MARBLE paper operates on neural time-series dynamics, not medical imaging. The transfer of geometric manifold learning principles to cross-modality imaging is theoretically motivated but not directly validated.
- **Resolution:** This verification plan tests whether geometric latent spaces trained on multi-modal medical imaging data exhibit the hypothesized modality-invariant properties through explicit feature similarity analysis across modalities.

### 1.4 Key Assumptions

1. **Shared Geometric Regularities:** Mid-level geometric features (edges, boundaries, smoothness priors) are partially shared across MRI, CT, and X-ray imaging modalities despite different physical acquisition mechanisms.
   - *Consequence if violated:* Multi-modal pre-training would not improve over single-modality training; no transfer benefit.

2. **Geometric Latent Separability:** A geometric latent space can capture modality-invariant structural features while being agnostic to modality-specific characteristics.
   - *Consequence if violated:* Latent space would encode modality-specific information, reducing transfer effectiveness.

3. **Adapter Sufficiency:** LoRA-style lightweight adapters (<5% parameters) are sufficient to specialize universal priors for modality-specific reconstruction.
   - *Consequence if violated:* Full fine-tuning would be required, eliminating efficiency benefits.

4. **Multi-modal Pre-training Benefit:** Training on multiple modalities improves generalization to new modalities compared to single-modality training.
   - *Consequence if violated:* No advantage over training separate models per modality.

### 1.5 Scope & Boundaries

**Where hypothesis applies:**
- Medical imaging modalities with structural anatomical content (MRI, CT, X-ray, ultrasound)
- Inverse problems with known forward models (compressed sensing MRI, sparse-view CT, image denoising)
- Scenarios with limited target modality training data (<1000 samples)
- Resolution range: 128×128 to 512×512 pixels

**Where it does NOT apply:**
- Fundamentally different imaging modalities (natural images, satellite imagery, microscopy) without validation
- Inverse problems with unknown or highly complex forward models
- Real-time inference requirements (diffusion models are computationally expensive)
- Modalities without structural anatomical content (functional MRI activation maps)

**Known limitations:**
- Transfer efficiency gains are empirically quantified, not theoretically guaranteed
- Geometric encoder design requires domain expertise for loss function selection
- Adapter rank selection may require hyperparameter tuning per modality

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Transfer Efficiency):**
When adapting GAMDP (pre-trained on MRI+CT) to X-ray reconstruction, the model will achieve PSNR within 1dB of a modality-specific baseline while using ≤50% of the target modality training data.

*Measurement:*
- PSNR and SSIM on held-out X-ray test set
- Baseline: Modality-specific diffusion model trained on 100% X-ray data
- Transfer: GAMDP + LoRA adapter trained on 10%, 25%, 50% X-ray data
- Statistical test: Paired t-test, n ≥ 20 random seeds, p < 0.05

*Success Criteria for Phase 2B:*
- Primary: PSNR(GAMDP@50%) ≥ PSNR(Baseline@100%) - 1dB with p < 0.05
- Falsification: PSNR(GAMDP@50%) < PSNR(Baseline@100%) - 3dB triggers rejection

**Secondary Predictions:**

**P2 (Geometric Feature Similarity):**
Features in the geometric latent space will show higher cosine similarity across modalities (MRI vs CT vs X-ray) compared to features from a standard VAE latent space.

*Expected:* GAMDP similarity > VAE similarity by >0.1

**P3 (Adapter Efficiency):**
LoRA adapters with <5% of base model parameters will achieve reconstruction quality within 0.5dB PSNR of full fine-tuning.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** PSNR(GAMDP@50% data) < PSNR(Baseline@100% data) - 3dB
2. **Mechanism Failure:** Cross-modality latent feature similarity for GAMDP ≤ standard VAE
3. **Efficiency Failure:** LoRA adapters require >20% of base model parameters to match full fine-tuning

### 1.7 SOTA Baseline (Optional)

*Not applicable - This hypothesis targets transfer efficiency rather than absolute SOTA performance.*

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 20 runs (5 seeds × 4 test variations)
**Statistical Test:** Paired t-test, α = 0.05 (one-tailed)
**Report Format:** Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does cross-modality transfer of geometric priors exist in diffusion models for medical imaging inverse problems?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed geometric latent space + adapter mechanism the actual cause of transfer efficiency?"
- Decomposition for Phase 2B:
  - H-M1: Multi-modal training → Geometry-preserving latent space
  - H-M2: Geometry-preserving latent → Universal diffusion prior
  - H-M3: Universal prior + LoRA adapters → Modality-specific reconstruction
- Verification type: Causal analysis with ablations

**SH3 (Comparison):**
"Does GAMDP provide efficiency advantages over modality-specific baselines?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical

**Total sub-hypotheses in Phase 2B:** 2 + 3 = **5 sub-hypotheses**

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-GAMDP-v1
- [x] Confidence level specified: 0.80
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps)
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (primary marked)
- [x] Falsification criteria defined with quantitative thresholds
- [x] Baselines identified (HFS-SDE, MCG, SMRD)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Dataset Availability:** Are paired multi-modal medical imaging datasets available, or will we need unpaired data with domain adaptation?

2. **Geometric Loss Design:** What specific geometry-preserving losses for the encoder? (edge detection, boundary consistency, gradient magnitude)

3. **Adapter Placement Strategy:** At which UNet layers should LoRA adapters be placed?

4. **Verification Priority:** Recommend SH1 first as the critical gate.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
