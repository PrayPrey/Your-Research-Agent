# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-NF-Eval-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under condition [neural field evaluation across diverse applications (visual computing, robotics, scientific computing)], if [multi-dimensional metrics with application-aware thresholds and Pareto analysis are used], then [method rankings will correlate better with human preferences (r > 0.7) and enable principled trade-off decisions] because [thresholding filters perceptually negligible differences while Pareto analysis identifies non-dominated solutions across quality dimensions].

**Alternative Hypothesis (H0):**
Multi-dimensional evaluation with thresholds and Pareto analysis provides no improvement over single-metric (PSNR) evaluation in terms of human preference correlation or actionable trade-off decisions (r ≤ 0.55, no discrimination improvement).

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Evaluation Framework Type | Independent | Single-metric (PSNR) vs Multi-dimensional with Pareto (NF-Eval) | Binary: {PSNR-only, NF-Eval} |
| Application-Aware Thresholds | Independent | Domain-expert defined values per dimension | Visual: LPIPS<0.1, Physics: residual<1e-4, Robotics: latency<10ms |
| Dimension Weights | Independent | User-specified priority ranking for dimensions | Ordered list of 4 dimensions |
| Human Preference Correlation | Dependent | Spearman correlation between framework rankings and human preference study rankings | r ∈ [0, 1], target r > 0.70 |
| Trade-off Decision Quality | Dependent | Number of actionable method recommendations per use-case from Pareto frontier | 2-5 recommendations per application domain |
| Method Discrimination Power | Dependent | Percentage of method pairs with statistically significant quality difference | Target: >60% pairs discriminated |
| Benchmark Dataset | Controlled | Fixed test set across all evaluations | Mip-NeRF 360, ScanNet, PDE simulation benchmarks |
| Neural Field Implementations | Controlled | Fixed set of methods being compared | NeRF, Mip-NeRF, 3DGS, SIREN, Instant-NGP |
| Evaluation Hardware | Controlled | Fixed GPU/CPU configuration for efficiency metrics | NVIDIA RTX 3090, consistent settings |

### 1.3 Causal Mechanism

**3-Step Causal Chain:**

```
[Multi-dimensional metrics]
    → (Step 1) Comprehensive quality capture
        → [Application-aware thresholds]
            → (Step 2) Meaningful difference filtering
                → [Pareto frontier analysis]
                    → (Step 3) Principled trade-off decisions
                        → [Improved human correlation + actionable recommendations]
```

**Step 1: Multi-dimensional Metrics → Comprehensive Quality Capture**
- Mechanism: Single metrics (PSNR) miss important quality dimensions; multi-dimensional evaluation captures perceptual, physical, semantic, and efficiency aspects simultaneously
- Evidence: DreamSim study (2025) shows PSNR cannot differentiate minor vs substantial corruptions; PINNs review (2022) demonstrates physics requires PDE residual metrics independent of visual quality

**Step 2: Application-Aware Thresholds → Meaningful Difference Filtering**
- Mechanism: Thresholds below perceptual equivalence (JND-inspired) filter out negligible differences, reducing false comparisons
- Evidence: NerfBaselines (2024) shows tiny protocol differences artificially boost performance; psychophysics literature establishes threshold-based perception

**Step 3: Pareto Frontier Analysis → Principled Trade-off Decisions**
- Mechanism: Non-dominated sorting identifies methods that are optimal for specific dimension priorities, enabling actionable recommendations
- Evidence: Multi-objective optimization theory; no single neural field method dominates all quality dimensions

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Mip-NeRF (2021) | PSNR inadequate for multi-scale; 17-60% error reduction with proper multi-scale evaluation | Strong |
| Step1 → Step2 | DreamSim (2025) | PSNR/SSIM/LPIPS ineffective at differentiating corruption severity | Strong |
| Step2 → Step3 | NerfBaselines (2024) | Protocol sensitivity demonstrates need for principled thresholds | Strong |
| Step2 → Step3 | Psychophysics literature | JND thresholds correspond to perceptual equivalence | Medium |
| Step3 → Outcome | MOO Theory | Pareto optimality identifies best compromises across objectives | Strong |

**Key Tension:**
- **Tension:** Dimension correlation concern - if perceptual quality highly correlates with physical correctness (r > 0.85), multi-dimensional evaluation becomes redundant
- **Resolution:** Correlation analysis step merges redundant dimensions before Pareto computation; empirical validation on neural field benchmarks will determine actual correlation levels

### 1.4 Key Assumptions

1. **A1: Quality dimensions are separable and independently measurable**
   - Supporting evidence: Each dimension has established independent metrics (LPIPS for perceptual, PDE residual for physics, task accuracy for semantic, FLOPs for efficiency)
   - Consequence if violated: Framework reduces to effectively single-dimensional; mitigate via correlation analysis merging redundant dimensions

2. **A2: Domain experts can define meaningful thresholds**
   - Supporting evidence: Psychophysics JND literature; numerical analysis convergence criteria for physics
   - Consequence if violated: Thresholds become arbitrary; mitigate via empirical validation against human preference studies

3. **A3: Pareto dominance is meaningful for neural field comparison**
   - Supporting evidence: Multi-objective optimization theory; DreamSim shows different metrics have different sensitivities (trade-offs exist)
   - Consequence if violated: One method dominates all; mitigate via primary dimension ranking for actionable output

4. **A4: Users can specify dimension weights based on application**
   - Supporting evidence: Different applications have different priorities (real-time robotics needs efficiency, offline rendering needs quality)
   - Consequence if violated: Generic rankings insufficient; mitigate via application-specific preset configurations

### 1.5 Scope & Boundaries

**Applies To:**
- Neural field architectures: NeRF variants, 3D Gaussian Splatting, SIREN, PINNs
- Standard benchmarks: Mip-NeRF 360, ScanNet, Tanks and Temples, PDE simulation datasets
- Applications: Visual computing (NVS, 3D reconstruction), robotics (SLAM), scientific computing (physics simulation)

**Does NOT Apply To:**
- Single-image quality assessment (no multi-view consistency)
- Non-neural field methods (traditional graphics pipelines)
- Architectures without spatial/temporal dimensions
- Real-time interactive evaluation (batch evaluation only)

**Known Limitations:**
- Threshold definition requires domain expertise
- Dimension correlation may reduce effective dimensionality
- Human preference study required for validation (resource-intensive)
- Initial focus on visual computing; physics/robotics domains require domain expert collaboration

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Human Preference Correlation)**:
NF-Eval method rankings will achieve Spearman correlation r > 0.70 with human preference study rankings, compared to PSNR-only baseline (r ≈ 0.40-0.50).

*Measurement*:
- Spearman ρ > 0.70 with p < 0.05
- Statistical test: Fisher's z-transformation for correlation comparison
- Sample size: n ≥ 30 human evaluators, m ≥ 50 scene pairs

*Basis*:
DreamSim study (2025) establishes PSNR/SSIM correlate poorly with human perception for NVS applications. Target represents "strong" correlation threshold in behavioral research.

*Success Criteria for Phase 2B*:
- Primary: r > 0.70 (p < 0.05)
- Falsification: r ≤ 0.55 triggers rejection

**Secondary Predictions:**

**P2 (Threshold Effectiveness)**:
Application-aware thresholds will group perceptually equivalent methods together, reducing false-positive comparisons by >40% compared to raw metric differences.

**P3 (Pareto Discrimination)**:
Pareto frontier analysis will identify 3-7 non-dominated methods per application domain, each optimal for specific dimension priorities.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Human preference correlation r ≤ 0.55
2. **Mechanism Failure - Dimension Redundancy**: All dimension pairs show r > 0.85
3. **Mechanism Failure - Threshold Invalidity**: Threshold-filtered "equivalent" pairs show <50% human agreement
4. **Practical Failure - No Discrimination**: Pareto frontier contains >80% of methods

### 1.7 SOTA Baseline (Optional)

*Not applicable - framework evaluation, not method performance comparison.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (correlation improvement): Δr = 0.25 (from ~0.45 to 0.70)
- Required human evaluators: n ≥ 30
- Required scene pairs: m ≥ 50
- Statistical power: 0.80

**Test Specification:**
- Method: Fisher's z-transformation for correlation comparison
- Significance level: α = 0.05 (one-tailed)
- Report format: Spearman ρ, 95% CI, Fisher's z, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does multi-dimensional evaluation capture quality aspects that single-metric (PSNR) evaluation misses?"
- Maps to: Primary prediction P1 (human correlation improvement)
- Verification type: Empirical (human preference study)
- Critical: MUST PASS for hypothesis to proceed

**SH2 (Mechanism):**
"Is the proposed 3-step mechanism the actual cause of improved evaluation quality?"
- Phase 2B decomposes into 3 sub-hypotheses:
  - **H-M1:** Multi-dimensional metrics → Comprehensive quality capture
  - **H-M2:** Application-aware thresholds → Meaningful difference filtering
  - **H-M3:** Pareto frontier → Principled trade-off decisions
- Verification type: Causal analysis via ablation studies

**SH3 (Comparison):**
"Does NF-Eval outperform existing evaluation approaches in actionable recommendations?"
- Maps to: Prediction P3 (Pareto discrimination)
- Verification type: Comparative empirical (user study on actionability)

**Total Phase 2B Sub-Hypotheses:** 5 (SH1 + 3×SH2 + SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-NF-Eval-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (3 steps, evidence table provided)
- [x] Causal chain length (N=3) determined and documented
- [x] Key tension identified (dimension correlation) and resolution proposed
- [x] Key assumptions list consequences if violated (4 assumptions)
- [x] At least 2 testable predictions exist (3 predictions with primary marked)
- [x] Falsification criteria defined (4 rejection conditions)
- [x] Baselines identified for comparison (PSNR-only, multi-metric display)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Human preference study design:** How many evaluators needed for statistical power? Which neural field methods and scenes should be included?

2. **Threshold validation methodology:** How to empirically validate that expert-defined thresholds correspond to perceptual equivalence?

3. **Implementation scope for Phase 2C:** Start with visual computing domain only, or include physics/robotics from the beginning?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
