# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-PWGD-ST-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under molecular graph generation conditions using score-based diffusion, if precision heads are integrated into the GDSS architecture with a staged training protocol, then generated molecules will have calibrated uncertainty estimates that correlate with chemical validity (AUROC > 0.8), because precision-weighted score functions enable heteroscedastic uncertainty propagation through the reverse SDE, similar to Bayesian predictive coding's precision-weighted prediction errors.

**Alternative Hypothesis (H0):**
Precision heads integrated into GDSS do not produce meaningful uncertainty estimates; uncertainty scores are uncorrelated with molecular validity (AUROC ≈ 0.5), and the added architectural complexity provides no benefit over post-hoc uncertainty quantification methods.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Precision head architecture | Independent | Equivariant MPNN layers sharing backbone with score network, outputting inverse variance per node/edge | 2-4 layers, 64-256 hidden dim |
| Training protocol | Independent | Three-stage: (1) base GDSS, (2) frozen score + precision heads, (3) joint fine-tuning | Stage 1: 100 epochs, Stage 2: 50 epochs, Stage 3: 50 epochs |
| Loss weights (λ_gen, λ_cal) | Independent | Hyperparameters balancing score matching and calibration objectives | λ_gen ∈ [0.5, 1.0], λ_cal ∈ [0.1, 0.5] |
| Calibration quality (ECE) | Dependent | Expected Calibration Error measured via SmoothECE on validity predictions | ECE < 0.05 (well-calibrated) |
| Generation quality | Dependent | Validity, uniqueness, novelty metrics on QM9/ZINC benchmarks | Validity > 95%, within 5% of baseline GDSS |
| AUROC for quality detection | Dependent | Area under ROC for predicting invalid molecules from uncertainty scores | AUROC > 0.8 |
| Dataset | Controlled | QM9 (134k molecules) and ZINC250k benchmarks | Fixed |
| Base architecture | Controlled | GDSS with standard MPNN score network (Jo et al. 2022) | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
[Precision Heads Learn Uncertainty] → [Precision Modulates SDE] → [Uncertainty-Quality Correlation] → [Calibrated Molecular Generation]
```

**Step 1: Precision Heads Learn Score Uncertainty**
- Precision heads learn to estimate inverse variance from MPNN hidden representations
- High-uncertainty regions correspond to ambiguous molecular configurations
- Evidence: BPC (Tschantz 2025) demonstrates local Bayesian updates preserve uncertainty through layers

**Step 2: Precision-Modulated Noise Injection in Reverse SDE**
- Modified SDE: dx = [f(x,t) - g²(t)·Λ(x,t)·s_θ(x,t)]dt + g(t)·Λ^{-1/2}(x,t)·dw̄
- Evidence: Analogous to precision-weighted prediction errors in predictive coding

**Step 3: Uncertainty Propagation Through Denoising**
- Uncertainty accumulates through trajectory; final uncertainty reflects generation confidence
- Evidence: Score-based models track trajectory; uncertainty propagation standard in Bayesian filtering

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Tschantz et al. (2025) BPC | Local Bayesian updates work in deep networks | Strong |
| Step2 → Step3 | Jo et al. (2022) GDSS | Joint node-edge SDE system captures dependencies | Strong |
| Step3 → Outcome | Gawlikowski et al. (2021) | Heteroscedastic UQ correlates with prediction errors | Medium |

**Key Tension:**
- **Tension:** Jazbec et al. (2025) achieves generative uncertainty via post-hoc Laplace without modifying training
- **Resolution:** Test whether end-to-end precision learning provides better calibration than post-hoc methods

### 1.4 Key Assumptions

1. **Precision can be meaningfully estimated from hidden representations**
   - Evidence: BPC (Tschantz 2025)
   - Consequence if violated: AUROC ≈ 0.5, uncertainty uninformative

2. **Heteroscedastic formulation transfers from regression to score matching**
   - Evidence: Gawlikowski (2021) UQ survey
   - Consequence if violated: Training diverges or precision meaningless

3. **Equivariant precision heads preserve permutation invariance**
   - Evidence: GDSS architecture properties
   - Consequence if violated: Invalid molecular generation

4. **Staged training prevents precision-score optimization conflict**
   - Evidence: Multi-stage training literature
   - Consequence if violated: Generation quality degrades

### 1.5 Scope & Boundaries

**Applies to:** Graph-structured molecular data (QM9, ZINC); score-based diffusion with MPNN

**Does NOT apply to:** Continuous image/audio diffusion; very large graphs (>100 atoms); non-diffusion generative models

**Known limitations:** ~30-50% compute overhead; hyperparameter sensitivity for loss weights

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (AUROC for Quality Detection)**:
PWGD-ST will achieve AUROC > 0.8 for predicting invalid molecules from uncertainty scores.

*Measurement*: Generate 10,000 molecules, compute uncertainty per molecule, evaluate AUROC vs validity
*Success Criteria*: AUROC > 0.8 (p < 0.05)
*Falsification*: AUROC ≤ 0.6 triggers rejection

**Secondary Predictions:**

**P2 (Calibration Quality)**: ECE < 0.05 on validity confidence (SmoothECE metric)

**P3 (Generation Quality Preservation)**: Validity within 5% of baseline GDSS

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:
1. AUROC ≤ 0.6 for validity prediction
2. ECE > 0.15 (severely miscalibrated)
3. Validity > 10% below baseline GDSS
4. Precision values constant or random across samples

### 1.8 Statistical Verification Design

**Sample Size:** 10,000 molecules per condition
**Statistical Test:** Bootstrap 95% CI (10,000 resamples)
**Significance Level:** α = 0.05 (one-tailed)
**Report Format:** AUROC with 95% CI, ECE, generation metrics

**Ablation Studies:**
1. Staged vs end-to-end training
2. Precision head depth (2, 3, 4 layers)
3. Loss weight sensitivity

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Do precision heads produce non-trivial uncertainty estimates that vary across generated molecules?"
- Verification: Measure variance of precision outputs
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is precision-weighted score propagation the actual cause of calibrated uncertainty?"
- Will decompose into N=3 sub-hypotheses:
  - H-M1: Precision heads learn score uncertainty
  - H-M2: Precision modulation affects sample quality distribution
  - H-M3: Accumulated uncertainty correlates with validity
- Verification: Ablation studies

**SH3 (Comparison):**
"Does PWGD-ST outperform post-hoc Laplace (Jazbec et al.) on calibration?"
- Verification: Comparative empirical

**Total sub-hypotheses:** 5 (SH1 + 3×SH2 + SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-PWGD-ST-v1
- [x] Confidence level: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized (8 variables)
- [x] Causal mechanism with evidence (N=3 steps)
- [x] Key tension identified with resolution
- [x] Key assumptions with consequences (4)
- [x] Testable predictions with primary (3)
- [x] Falsification criteria defined (4)
- [x] Baselines identified (GDSS, Jazbec, MC Dropout)
- [x] SH1, SH2, SH3 clear

### Open Questions

1. **Resource requirements:** GPU memory ~1.3-1.5x baseline GDSS
2. **Data availability:** QM9/ZINC publicly available; verify preprocessing compatibility
3. **Technical feasibility:** Custom SDE solver modifications for precision-modulated noise

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
