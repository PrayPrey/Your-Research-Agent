# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-TrustNeuroDG-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under conditions of multi-site medical imaging with domain shift, if Neural Response Normalization (NeuRN) layers are inserted into CNN architectures, then domain-invariant features will be extracted achieving higher target domain accuracy (≥5% improvement), calibrated uncertainty (ECE ≤0.10), and improved explanation faithfulness (≥10% over Grad-CAM), because NeuRN mimics the excitatory-inhibitory balance mechanism of the visual cortex that biologically achieves invariant representations through population diversity.

**Alternative Hypothesis (H0):**
NeuRN layer insertion does not improve domain generalization performance over standard DG algorithms, and any observed improvements are due to increased model capacity or regularization effects rather than the proposed domain-class separation mechanism.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| NeuRN layer insertion | Independent | Binary: with/without NeuRN layers after each convolutional block | {0, 1} |
| Diversity regularization strength (λ) | Independent | Continuous weight controlling orthogonality loss | λ ∈ [0.01, 1.0] |
| Hierarchical layer positions | Independent | Which CNN layers receive NeuRN insertion | {conv2, conv3, conv4, all} |
| Target domain accuracy | Dependent | AUROC on held-out target domain (different hospital/equipment) | [0.5, 1.0], target ≥0.85 |
| Uncertainty calibration (ECE) | Dependent | Expected Calibration Error via reliability diagrams | [0, 1], target ≤0.10 |
| Explanation faithfulness | Dependent | Deletion/insertion AUC for NeuRN activation maps | [0, 1], target ≥0.10 improvement |
| Base architecture | Controlled | Fixed ResNet-50 backbone pretrained on ImageNet | ResNet-50 |
| Training protocol | Controlled | Standard DomainBed training with leave-one-domain-out | Fixed hyperparameters |

### 1.3 Causal Mechanism

**4-Step Causal Chain:**

```
Step 1: NeuRN Layer Application
    ↓
Step 2: Domain-Class Feature Separation
    ↓
Step 3: Diversity-Based Uncertainty Estimation
    ↓
Step 4: Hierarchical Interpretable Activations
    ↓
OUTCOME: Multi-dimensional Trustworthy DG (Accuracy + UQ + XAI)
```

**Step 1 → Step 2:** NeuRN layer separates domain statistics from class features
- Mechanism: y = (x - μ_domain) * γ_class + β_class
- Evidence: Qazi et al. (2025) demonstrated this formula explicitly decouples domain from class information

**Step 2 → Step 3:** Domain-suppressed features enable generalization + diversity enables UQ
- Mechanism: Population diversity across channels provides uncertainty estimates
- Evidence: Lee et al. (2025) showed V4 achieves superior invariant decoding due to greater diversity

**Step 3 → Step 4:** Hierarchical activations provide interpretability
- Mechanism: NeuRN activation patterns reveal domain-invariant (high activation) vs domain-specific (suppressed) features
- Evidence: Biological visual cortex hierarchy (V1→V2→V4) provides increasing invariance

**Step 4 → Outcome:** Combined DG + UQ + XAI for clinical trustworthiness
- Evidence: Addresses all 3 gaps identified in Phase 1 research

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Qazi et al. (2025) | NeuRN improves DG on PACS/Office-Home | Strong |
| Step2 → Step3 | Lee et al. (2025) | V4 diversity enables robust invariant decoding | Medium |
| Step3 → Step4 | Biological analogy | Cortical hierarchy provides increasing abstraction | Medium |
| Step4 → Outcome | Integration design | Novel contribution connecting 3 gaps | Theoretical |

**Key Tension:**
- Tension: Korevaar et al. (2023) suggests ALL DG algorithms fail to achieve domain invariance, yet Qazi et al. (2025) claims NeuRN succeeds on natural images.
- Resolution: This verification plan tests whether NeuRN's biological mechanism transfers to medical imaging where the domain-class relationship may differ from natural images.

### 1.4 Key Assumptions

1. **Domain labels available during training**
   - Standard DG assumption; required for leave-one-domain-out protocol
   - Consequence if violated: Cannot separate source/target domains; need unsupervised DG approach

2. **NeuRN mechanism transfers from natural to medical images**
   - Qazi et al. (2025) validated on PACS/Office-Home; medical imaging untested
   - Consequence if violated: Core hypothesis fails; need domain-specific adaptation

3. **Population diversity correlates with prediction uncertainty**
   - Based on V4 cortical diversity principle from Lee et al. (2025)
   - Consequence if violated: UQ component fails; need alternative uncertainty method

4. **Hierarchical NeuRN activations are clinically interpretable**
   - Assumes activation patterns correspond to clinically meaningful features
   - Consequence if violated: XAI component fails; need clinician validation study

### 1.5 Scope & Boundaries

**Applies to:**
- Medical imaging classification tasks (chest X-ray, retinal OCT, CT)
- Multi-site/multi-equipment domain shift scenarios
- Settings with available domain labels during training

**Does NOT apply to:**
- Segmentation tasks (without architecture modification)
- Single-site deployments (no domain shift)
- Domains without labeled source data
- Temporal concept shift (equipment updates over time)

**Known Limitations:**
- UQ via diversity is approximate, not full Bayesian inference
- XAI interpretability requires clinician validation
- Performance on very large domain gaps (e.g., X-ray to CT) untested

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Target Domain Accuracy vs DomainBed Baselines):**
TrustNeuroDG will achieve target domain AUROC ≥5% higher than the best DomainBed baseline (CORAL, DANN, IRM, or GroupDRO) on multi-site medical imaging benchmarks.

*Measurement:*
- AUROC improvement > 5% with p < 0.05
- Statistical test: Paired t-test across 3+ datasets, n ≥ 25 runs per configuration
- Effect size: Cohen's d > 0.5

*Basis:*
Qazi et al. (2025) showed significant improvements on PACS and Office-Home. Medical imaging DG methods typically show 2-5% variance across sites (Matta et al. 2024 systematic review).

*Success Criteria for Phase 2B:*
- Primary: AUROC improvement ≥ 5% (p < 0.05)
- Falsification: AUROC improvement < 0% (no better than baseline)

**Secondary Predictions:**

**P2 (Uncertainty Calibration):**
TrustNeuroDG with diversity-based UQ will achieve Expected Calibration Error (ECE) ≤ 0.10 on out-of-distribution target domain samples, outperforming standard softmax confidence.

**P3 (Explanation Faithfulness):**
TrustNeuroDG hierarchical activation maps will achieve ≥10% higher deletion/insertion AUC than Grad-CAM baseline on the same model.

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** Target domain AUROC improvement < 0% compared to best DomainBed baseline
2. **Mechanism Failure:** Ablation study shows NeuRN layer removal does not decrease performance
3. **Multi-dimensional Failure:** Improvements on DG come at cost of UQ (ECE > 0.15) or XAI (faithfulness < Grad-CAM)

### 1.7 SOTA Baseline (Domain Standards)

**Performance Context:**
- Medical imaging DG methods show high variance (±10-15%) across sites
- DomainBed algorithms achieve 70-85% accuracy depending on domain gap
- Korevaar et al. (2023): No DG method consistently outperforms ERM baseline

**Target Thresholds:**
- Meaningful improvement: ≥5% over best baseline
- Statistical significance: p < 0.05, Cohen's d > 0.5

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size target: Cohen's d ≥ 0.5 (medium)
- Required runs: n ≥ 25 per configuration
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds across methods)
- Significance level: α = 0.05 (two-tailed)
- Multiple comparison correction: Bonferroni for 3 primary metrics

**Report Format:**
- Mean ± Std Dev, 95% Confidence Interval
- Cohen's d effect size, p-value with correction

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does NeuRN layer insertion improve target domain accuracy on multi-site medical imaging datasets compared to baseline architectures without NeuRN?"
- Maps to: Primary prediction P1
- Verification type: Empirical comparative
- Critical: MUST PASS for hypothesis to proceed

**SH2 (Mechanism):**
"Is the NeuRN domain-class separation mechanism the actual cause of improved generalization, uncertainty calibration, and explainability?"
- Maps to: Causal mechanism (4 steps)
- Will decompose into 4 sub-hypotheses in Phase 2B:
  - H-M1: NeuRN separates domain from class features (Step 1→2)
  - H-M2: Separation enables target domain generalization (Step 2→3)
  - H-M3: Population diversity provides calibrated uncertainty (Step 3→4)
  - H-M4: Hierarchical activations provide interpretable features (Step 4→Outcome)
- Verification type: Ablation studies and mechanism analysis
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does TrustNeuroDG outperform DomainBed baselines on multi-dimensional trustworthiness metrics (DG + UQ + XAI)?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical across all 3 dimensions
- Critical: Determines practical value over existing methods

**Total Sub-Hypotheses:** 2 + 4 = 6 (SH1 + H-M1 through H-M4 + SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-TrustNeuroDG-v1
- [x] Confidence level specified: 0.78
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has 4 steps with evidence table
- [x] Causal chain length (N=4) determined and documented
- [x] Key tension identified with resolution strategy
- [x] Key assumptions list consequences if violated
- [x] 3 testable predictions (P1 primary, P2/P3 secondary)
- [x] Falsification criteria defined with quantitative thresholds
- [x] Baselines identified: DomainBed (CORAL, DANN, IRM, GroupDRO, ERM)
- [x] SH1, SH2, SH3 are clear starting points for Phase 2B

### Open Questions

1. **Dataset Access:** Need to verify access to MIMIC-CXR, ChestX-ray14, and CheXpert for multi-site evaluation
2. **Compute Requirements:** Multi-site training with 25+ runs per configuration requires significant GPU time
3. **Clinician Validation:** XAI interpretability (P3) requires clinician study design
4. **Verification Priority:** Recommended order: SH1 (existence) → SH2 (mechanism) → SH3 (comparison)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
