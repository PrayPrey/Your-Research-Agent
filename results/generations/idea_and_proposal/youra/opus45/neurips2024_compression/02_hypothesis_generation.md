# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-EUR-JDMC-v1
**Confidence Level:** 0.80

**Main Hypothesis:**
Under CNN-based image compression models with standard datasets (ImageNet, COCO), if hyperprior entropy models are applied to jointly compress neural network weights and data representations with unified rate-distortion optimization, then total bitrate will be 10-20% lower than independent sequential optimization because data latents and weights share mutual information that can be exploited for improved joint entropy coding.

**Alternative Hypothesis (H0):**
Joint compression of data and model weights using shared entropy models provides no significant bitrate advantage (≤5% improvement) over independent sequential optimization, because the mutual information between data latents and weights is negligible or cannot be practically exploited.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Entropy model architecture | Independent | Hyperprior depth (2-4 layers), channels (64-256), conditioning structure | Config parameters |
| Lambda trade-off weights (λ₁, λ₂) | Independent | Grid search for reconstruction/task balance | [0.001, 0.01, 0.1, 1.0] |
| Quantization bit-width | Independent | Bits per weight parameter | INT4 (4 bits), INT8 (8 bits) |
| Total bitrate | Dependent | R_data + R_model measured via actual compressed size | 10-20% reduction vs baseline |
| Reconstruction quality | Dependent | PSNR (dB), LPIPS on validation set | PSNR: 25-40 dB, LPIPS: 0.01-0.2 |
| Task accuracy | Dependent | Top-1 accuracy on ImageNet classification | 70-80% (within 1% of uncompressed) |
| Dataset | Controlled | ImageNet (1.2M images), COCO (118K images) | Fixed |
| Base model architecture | Controlled | ResNet-50 encoder in CompressAI framework | Fixed |
| Training procedure | Controlled | 300 epochs, Adam optimizer, cosine LR schedule | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
[Hyperprior applied to weights]
        ↓ (Link 1)
[Weight entropy estimation improves]
        ↓ (Link 2)
[Joint entropy coding exploits I(z;W) correlation]
        ↓ (Link 3)
[Total bitrate reduced 10-20%]
```

**Step 1: Hyperprior Transfer to Weights**
- Hyperprior entropy models capture layer-wise and channel correlations in weight tensors
- Evidence: CompressAI hyperprior implementation, Ballé et al. foundational work

**Step 2: Correlation Exploitation**
- I(z;W) > 0 implies H(z,W) < H(z) + H(W), enabling joint coding gain
- Evidence: IB Analysis of DNNs (2023), Rate-Distortion theory

**Step 3: Joint Rate-Distortion Optimization**
- Unified loss: L = R_data(z) + R_model(W) + λ₁·D_recon + λ₂·D_task
- Evidence: Radio (2025), RD for Model Compression (2018)

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | CompressAI hyperprior, Ballé papers | Hyperprior captures spatial/channel correlations effectively | Strong |
| Step2 → Step3 | IB Analysis of DNNs (2023), Information theory | Mutual information enables joint coding gain | Medium |
| Step3 → Outcome | Radio (2025), RD for Model Compression (2018) | RD optimization yields optimal compression-accuracy tradeoff | Strong |

**Key Tension:**
- **Tension:** Radio (2025) targets LLMs (transformers), while CompressAI targets CNNs. Architecture transferability unverified.
- **Resolution:** Scope to CNN-based image compression first; validate before extending.

### 1.4 Key Assumptions

| Assumption | Evidence | Consequence if Violated |
|------------|----------|------------------------|
| **A1:** I(z; W) > 0 and exploitable | IB theory (Tishby 2015) | If I(z;W) ≈ 0, joint coding provides no benefit |
| **A2:** Hyperprior transfers to weight tensors | Similar tensor structures | If fails, need architecture-specific entropy model |
| **A3:** Multi-objective training converges | GradNorm literature | If diverges, need curriculum learning |
| **A4:** 8-GPU node sufficient | CompressAI benchmarks | If insufficient, use gradient accumulation |

### 1.5 Scope & Boundaries

**Applies to:**
- CNN-based image compression models (ResNet, EfficientNet encoders)
- Image/video data with learned compression
- Standard quantization bit-widths (INT4, INT8)

**Does NOT apply to:**
- Large Language Models (Radio addresses separately)
- Non-visual data initially
- Extremely deep networks (>200 layers) without validation

**Known Limitations:**
- Requires retraining for each base architecture
- Joint optimization adds ~30% training overhead

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Bitrate Reduction vs Sequential Baseline):**
Our approach will achieve >10% total bitrate reduction compared to sequential optimization (TorchAO INT4 + CompressAI hyperprior independently).

*Measurement*: Total bitrate reduction > 10% with p < 0.05
*Statistical test*: Paired t-test, n ≥ 20 runs
*Falsification*: Bitrate reduction ≤ 5% triggers rejection

**Secondary Predictions:**

**P2 (Joint Entropy Improvement):**
Hyperprior entropy model for weights will reduce bits-per-parameter by >5% compared to factorized prior.

**P3 (Correlation Exploitation):**
Mutual information I(z; W) > 0.1 nats will correlate with joint coding gain.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Bitrate reduction ≤ 5%
2. **Mechanism Failure**: Hyperprior provides no entropy improvement for weights
3. **Correlation Failure**: I(z; W) < 0.05 nats
4. **Convergence Failure**: Multi-objective training diverges

### 1.7 SOTA Baseline

| Method | Configuration | Baseline |
|--------|---------------|----------|
| Sequential Optimization | TorchAO INT4 + CompressAI (independent) | 1.0× (reference) |
| CompressAI (data only) | Hyperprior, λ=0.01 | ~0.5 bpp |
| TorchAO INT4 (model only) | INT4 quantization | ~2 bits/param |

### 1.8 Statistical Verification Design

**Sample Size**: n ≥ 20 runs
**Effect Size**: Cohen's d = 0.8 (large)
**Test**: Paired t-test, α = 0.05 (one-tailed)
**Report**: Mean difference, 95% CI, Cohen's d, p-value

**Ablation Design:**
- A1: With/without weight hyperprior
- A2: Joint vs. sequential training
- A3: Shared vs. separate entropy backends

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does hyperprior entropy modeling improve weight compression efficiency compared to factorized priors?"
- Maps to: P2
- Verification: Empirical
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the proposed 3-step causal mechanism the actual cause of bitrate reduction?"
- Phase 2B decomposes into 3 sub-hypotheses:
  - H-M1: Hyperprior improves weight entropy estimation
  - H-M2: I(z;W) > 0 enables joint coding gain
  - H-M3: Joint RD optimization converges to Pareto-optimal solutions
- Verification: Causal analysis with ablations

**SH3 (Comparison):**
"Does our joint framework achieve >10% bitrate reduction vs sequential optimization?"
- Maps to: P1
- Verification: Comparative empirical
- Critical: Determines practical value

**Total sub-hypotheses:** 5 (SH1 + 3×SH2 + SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-EUR-JDMC-v1
- [x] Confidence: 0.80
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism (N=3) with evidence
- [x] Key tension identified
- [x] Assumptions with consequences
- [x] Testable predictions (P1 primary, P2/P3 secondary)
- [x] Falsification criteria defined
- [x] Baselines: CompressAI + TorchAO
- [x] SH1/SH2/SH3 clear

### Open Questions

1. **Compute:** Is 8-GPU A100 sufficient for 2-week training?
2. **MI Estimator:** MINE vs InfoNCE for I(z;W) estimation?
3. **Architecture:** ResNet-50 first, or parallel EfficientNet?
4. **Priority:** Verify SH1 before SH2, or parallel?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
