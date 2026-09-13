# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-PC-Alignment-v1
**Confidence Level:** 0.75

**Main Hypothesis:**
Under standard ImageNet training conditions with ResNet-50 architecture, if neural networks are trained with predictive coding (PC) objectives (prediction error minimization across hierarchical layers), then they will exhibit greater representational alignment with biological visual systems (measured by debiased CKA and RSA on brain-score benchmarks) compared to standard supervised learning, because predictive coding implements the same computational principle (hierarchical predictive processing) that biological visual systems use for efficient sensory encoding.

**Alternative Hypothesis (H0):**
Training neural networks with predictive coding objectives does not produce greater representational alignment with biological visual systems compared to standard supervised learning; any observed differences are attributable to architectural modifications (lateral connections) rather than the PC training objective itself.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Training Paradigm | Independent | Four conditions: (1) Baseline (standard supervised), (2) Architecture Control (lateral connections + supervised), (3) PC-Full (lateral + PC objective α=0.5), (4) PC-Parametric (lateral + PC, α∈[0,0.25,0.5,0.75,1.0]) | 4 discrete levels |
| Representational Alignment | Dependent | Debiased CKA and RSA scores against brain-score benchmarks (macaque V1-IT, NSD human fMRI, Allen mouse V1) | 0.0-1.0 (higher = more aligned) |
| Alpha Parameter (α) | Controlled/Manipulated | Balance between predictive (α=0) and contrastive (α=1) PC components | [0, 0.25, 0.5, 0.75, 1.0] |
| Architecture | Controlled | ResNet-50 with lateral connections and precision weighting (Qi et al., 2025) | Fixed across PC conditions |
| Dataset | Controlled | ImageNet-1K for training | Fixed |
| Random Seeds | Controlled | Multiple seeds for reproducibility | 5 seeds minimum |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: PC Training Objective
    ↓ (induces)
Step 2: Hierarchical Prediction Error Minimization
    ↓ (creates)
Step 3: Shared Computational Structure with Biological Systems
    ↓ (manifests as)
Outcome: Measurable Representational Alignment
```

**Step 1 → Step 2:** PC training objective induces hierarchical prediction error minimization
- The PC loss function L_PC = (1-α) * L_predictive + α * L_contrastive explicitly minimizes prediction errors between adjacent layers
- Precision weighting (Qi et al., 2025) balances errors across the deep hierarchy
- Evidence: Gütlin & Auksztulewicz (2025) demonstrated PC-trained ANNs exhibit brain-like mismatch responses

**Step 2 → Step 3:** Hierarchical prediction error minimization creates shared computational structure
- Both biological visual systems (Ali et al., 2021) and PC-trained ANNs minimize prediction errors across hierarchies
- This computational equivalence should produce similar internal representations
- Evidence: Khosla et al. (2024) showed training regime affects privileged representational axes

**Step 3 → Outcome:** Shared computational structure manifests as measurable alignment
- If both systems solve the same computational problem similarly, their representations should be geometrically similar
- Debiased CKA/RSA (Williams 2024, Murphy et al. 2024) can measure this similarity
- Evidence: Brain-score benchmarks successfully rank models by brain-likeness

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Qi et al. (2025) | Precision-weighted PC enables deep network training | Strong |
| Step1 → Step2 | Gütlin & Auksztulewicz (2025) | PC objectives create predictive/contrastive responses | Strong |
| Step2 → Step3 | Ali et al. (2021) | PC emerges from energy efficiency in biological systems | Medium |
| Step2 → Step3 | Khosla et al. (2024) | Training creates privileged representational axes | Medium |
| Step3 → Outcome | Williams (2024) | RSA/CKA equivalence for alignment measurement | Strong |
| Step3 → Outcome | Murphy et al. (2024) | Debiased CKA necessary for valid comparisons | Strong |

**Key Tension:**
- **Tension:** Ali et al. (2021) shows PC *emerges* from energy efficiency optimization in biological systems, but we are *explicitly imposing* PC objectives on ANNs. This raises the question: does explicitly training with PC capture the same computational properties as PC that naturally emerges?
- **Resolution:** This verification plan tests whether explicit PC training produces alignment improvements. If PC-trained networks show significantly higher alignment than both Baseline AND Architecture Control conditions, it supports the principle-based intervention approach regardless of whether PC emerges naturally or is explicitly trained.

### 1.4 Key Assumptions

1. **Biological PC Implementation:** Biological visual systems implement predictive processing as a core computational strategy
   - Evidence: Ali et al. (2021), Gütlin & Auksztulewicz (2025)
   - **If violated:** The theoretical basis for principle-based alignment collapses; alignment improvements (if any) would be coincidental rather than principled

2. **ANN PC Fidelity:** Simplified PC objectives in ANNs capture essential computational properties of biological PC
   - Evidence: Gütlin & Auksztulewicz (2025) brain-like responses
   - **If violated:** PC training may not induce the desired computational structure; need more biologically detailed implementations

3. **Metric Validity:** CKA and RSA (with mean-centering) are valid measures of representational alignment
   - Evidence: Williams (2024), Murphy et al. (2024)
   - **If violated:** Alignment conclusions are measurement artifacts; need alternative metrics (e.g., model stitching)

4. **Benchmark Representativeness:** Brain-score benchmarks (macaque V1-IT, human fMRI, mouse V1) are representative of ventral stream visual processing
   - Evidence: Established use in brain-model comparison literature
   - **If violated:** Results may not generalize to other brain regions or species

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Vision domain with natural images (ImageNet)
- Feedforward-dominant architectures with lateral connections (ResNet-50 based)
- Ventral stream visual processing (V1-IT hierarchy)
- Static image processing (not video/temporal)

**Where It Does NOT Apply:**
- Other modalities (language, audio, multimodal)
- Non-natural image distributions (medical imaging, synthetic data)
- Recurrent architectures with explicit temporal dynamics
- Behavioral alignment (response patterns, decision-making)
- Dorsal stream / action-related visual processing

**Known Limitations:**
- HIGH implementation difficulty (lateral connections, precision weighting)
- ~2x computational cost compared to standard training
- PC optimization at ImageNet scale is unproven
- Behavioral alignment relationship unexplored (future work)
- Multi-benchmark evaluation requires significant resources

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Alignment Improvement):**
PC-trained networks (PC-Full condition) will achieve significantly higher representational alignment scores than both Baseline and Architecture Control conditions on brain-score benchmarks.

*Measurement*:
- Debiased CKA and RSA scores on macaque V1-IT (primary)
- Paired comparisons: PC-Full vs Baseline, PC-Full vs Architecture Control
- Statistical test: Paired t-test across random seeds, p < 0.05

*Success Criteria*:
- PC-Full > Baseline with effect size Cohen's d > 0.5
- PC-Full > Architecture Control with p < 0.05 (isolates PC effect from architecture)

**Secondary Predictions:**

**P2 (Architecture Control):**
Architecture Control (lateral connections + standard supervised) will NOT show significant alignment improvement over Baseline, demonstrating that lateral connections alone do not drive alignment.

**P3 (Dose-Response):**
Alignment scores will show systematic relationship with α parameter, demonstrating controllable intervention.
- Expected: Significant correlation (r > 0.5) indicating dose-response relationship

**P4 (Cross-Species Generalization):**
Alignment improvements will generalize across macaque, human, and mouse benchmarks, supporting computational principle explanation over species-specific effects.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure:** PC-Full condition does NOT show significant improvement over Baseline (p > 0.05) on any benchmark

2. **Architecture Confound:** Architecture Control shows equivalent or greater alignment than PC-Full

3. **Mechanism Failure:** No dose-response relationship between α and alignment (r < 0.3)

4. **Generalization Failure:** Alignment improvement observed on only one species/benchmark

### 1.7 SOTA Baseline (Optional)

*Not applicable - Novel intervention method, not benchmark competition.*

**Reference Baseline:** Standard ResNet-50 brain-score (V1-IT): ~0.45-0.55

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 15 independent training runs per condition (5 seeds × 3 benchmarks)
**Effect Size Target:** Cohen's d ≥ 0.5 (medium effect)
**Statistical Power:** 0.8
**Significance Level:** α = 0.05

**Experimental Design:**
- 4 conditions × 5 random seeds = 20 trained models minimum
- PC-Parametric adds 5 α levels × 5 seeds = 25 additional models
- Total: 45 trained models

**Statistical Tests:**
1. Paired t-test (PC-Full vs Baseline, PC-Full vs Architecture Control)
2. Pearson correlation (α vs alignment scores)
3. Repeated measures ANOVA (condition × benchmark)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does predictive coding training produce any measurable change in brain-AI representational alignment compared to standard supervised learning?"
- Maps to: Primary prediction P1
- Verification type: Empirical comparison (PC-Full vs Baseline)
- Critical: MUST PASS for verification to proceed

**SH2 (Mechanism):**
"Is the PC training objective (not architectural modifications) the actual cause of alignment improvement?"
- Maps to: Causal mechanism (3 steps)
- Will decompose into 3 sub-hypotheses in Phase 2B:
  - H-M1: PC objective → Hierarchical error minimization
  - H-M2: Error minimization → Computational structure
  - H-M3: Computational structure → Measurable alignment
- Verification type: Ablation analysis (PC-Full vs Architecture Control)
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does the PC intervention provide controllable modulation of alignment through the α parameter?"
- Maps to: Secondary predictions P3 (dose-response)
- Verification type: Parametric analysis
- Critical: Determines practical utility as intervention method

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-PC-Alignment-v1
- [x] Confidence level specified: 0.75
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table provided)
- [x] Causal chain length (N=3) determined and documented
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (4 predictions with primary marked)
- [x] Falsification criteria are defined (4 criteria)
- [x] Baselines are identified for comparison (Baseline, Architecture Control)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Computational Resources:** What GPU resources and training time are required for 45 model training runs at ImageNet scale with ~2x compute overhead?

2. **Data Access:** Are brain-score benchmarks (macaque V1-IT, NSD human fMRI, Allen mouse V1) freely accessible, or do they require institutional access/agreements?

3. **Implementation Complexity:** Should precision weighting hyperparameters be treated as fixed (from Qi et al.) or as additional parameters to optimize?

4. **Verification Priority:** Should SH1 (existence) be verified first as a go/no-go gate before investing in mechanism (SH2) and comparison (SH3) verification?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
