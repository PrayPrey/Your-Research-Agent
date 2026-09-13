# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-DualPlasticity-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under the condition of periodic alignment signal computation (every K epochs), if we apply alignment-weighted importance scoring to guide dynamic sparse training (grow/prune operations), then representational alignment metrics (debiased CKA) will increase by >10% compared to standard training, because alignment-promoting connections are selectively strengthened while alignment-hindering connections are pruned based on Hebbian-inspired dual-plasticity principles.

**Alternative Hypothesis (H0):**
There is no systematic relationship between alignment-weighted structural modifications and representational alignment; any observed alignment improvements are attributable to standard training dynamics or random variation rather than the proposed dual-plasticity mechanism.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Alignment weight (α) | Independent | Scalar controlling task vs alignment importance trade-off in scoring: Score = α × task_importance + (1-α) × alignment_correlation | [0.0, 1.0], default 0.5 |
| Pruning threshold | Independent | Percentile of lowest-importance connections removed per restructuring cycle | 10-30% per cycle |
| Alignment computation frequency (K) | Independent | Number of epochs between debiased CKA recomputation | K ∈ {5, 10, 20} epochs |
| Growth rate | Independent | Number/percentage of new connections added per restructuring cycle | 10-30% of pruned connections |
| Task accuracy | Dependent | Top-1 accuracy on validation set | CIFAR-10: 90-95%, ImageNet: 70-76% |
| Alignment metric (CKA) | Dependent | Debiased CKA between model layer representations and target representations | [0.0, 1.0], target >10% improvement |
| Alignment controllability | Dependent | Δ alignment per unit change in α (slope of alignment-α curve) | Positive monotonic relationship expected |
| Model architecture | Controlled | Neural network architecture | ResNet-18 (dev), ResNet-50 (scale) |
| Dataset | Controlled | Training/evaluation dataset | CIFAR-10 (dev), ImageNet-1k (scale) |
| Target representations | Controlled | Reference for alignment computation | Human similarity judgments (odd-one-out) or NSD fMRI |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Alignment Signal Computation
    ↓
Step 2: Connection Importance Scoring
    ↓
Step 3: Structural Modification (Grow/Prune)
    ↓
Step 4: Alignment Improvement
    ↓
[Feedback Loop → Step 1]
```

**Detailed Mechanism:**

1. **Step 1 → Step 2 (Alignment Signal → Importance Scores):**
   Computing layer-wise debiased CKA between model and target representations produces per-connection alignment correlation values. These are combined with task gradients using alignment-weighted importance scoring.

2. **Step 2 → Step 3 (Importance Scores → Structural Decisions):**
   Using importance formula: `Score = α × task_importance + (1-α) × alignment_correlation`, connections below threshold are marked for pruning while high-alignment neuron pairs become growth candidates.

3. **Step 3 → Step 4 (Structural Modification → Topology Change):**
   Top-KAST's differentiable grow/prune operations execute structural changes: remove lowest-importance connections, add connections between high-alignment neurons using gradient-based or random regrowth strategies.

4. **Step 4 → Outcome (Topology Change → Alignment Improvement):**
   Iterative restructuring progressively shapes the network to favor alignment-promoting pathways, measured by increased debiased CKA with target representations across training.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Murphy et al. (2024) | Debiased CKA detects stimuli-driven alignment in low-data regimes | Strong |
| Step 2 → Step 3 | Top-KAST (Jayakumar 2021) | Differentiable importance scoring enables gradient-based grow/prune | Strong |
| Step 3 → Step 4 | RigL (Evci 2019) | Dynamic sparse training maintains task performance while modifying topology | Strong |
| Step 4 → Outcome | Muttenthaler (2022) | Training objective modifications can improve human alignment | Medium |

**Key Tension:**
- **Tension:** Murphy et al. (2024) shows debiased CKA is necessary for reliable alignment measurement, but existing CKA implementations in sparse training literature use biased CKA which can produce spurious similarity scores.
- **Resolution:** This verification plan explicitly uses debiased CKA (mean-centered, per Murphy et al.) for all alignment computations, ensuring measurement reliability.

### 1.4 Key Assumptions

| # | Assumption | Evidence | Consequence if Violated |
|---|------------|----------|------------------------|
| A1 | Debiased CKA is a reliable indicator of true representational alignment | Murphy et al. (2024) validated on THINGS fMRI/MEG | If violated: Importance scores become noise; structural decisions are random; no systematic alignment improvement |
| A2 | Periodic computation (every K epochs) captures sufficient alignment dynamics | Bridging Critical Gaps (2025) shows alignment crystallizes early | If violated: Miss critical alignment changes; suboptimal structural decisions; reduced controllability |
| A3 | Top-KAST framework can be extended with custom importance scoring | Top-KAST uses modular scoring function | If violated: Implementation blocked; need alternative sparse training framework |
| A4 | Target representations are available and representative | NSD, THINGS datasets publicly available | If violated: Cannot compute alignment signal; hypothesis untestable |
| A5 | Task and alignment objectives are not perfectly antagonistic | Muttenthaler (2022) found training objectives improve alignment | If violated: No valid α trade-off exists; Pareto front is empty |

### 1.5 Scope & Boundaries

**Applies to:**
- Vision models (CNNs, particularly ResNet family)
- Scenarios with available alignment targets (human similarity judgments, brain data)
- Supervised learning settings with classification objectives
- Models with 1M-50M parameters (validated range)

**Does NOT apply to:**
- Language models (different alignment measurement needed)
- Real-time adaptation scenarios (periodic computation incompatible)
- Domains without established alignment targets
- Very large models (>100M params) without further scaling validation

**Known Limitations:**
- Requires pre-defined target representations (not self-supervised)
- α parameter tuning needed per application domain
- Computational overhead: ~10-15% additional training time for CKA computation
- Interpretability analysis requires additional tooling

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Alignment Improvement):**
Our approach (Dual-Plasticity Alignment Networks with α=0.5) will achieve debiased CKA alignment >10% higher than standard training baseline.

*Measurement:*
- Debiased CKA improvement > 10% with p < 0.05
- Statistical test: Paired t-test, n ≥ 20 runs (same random seeds)

*Basis:*
Domain standard for alignment improvement research (Muttenthaler 2022 showed 5-15% improvements with loss modifications alone; structural modifications should enable larger effects).

*Success Criteria for Phase 2B:*
- Primary: Δ CKA > 10% (p < 0.05)
- Falsification: Δ CKA ≤ 2% triggers rejection (within noise)

**Secondary Predictions:**

**P2 (Controllability):**
Varying α from 0 to 1 will produce a monotonic Pareto front between task accuracy and alignment, with controllable trade-off (correlation > 0.8 between α and alignment).

**P3 (Mechanism Validation):**
Pruned connections will show statistically lower alignment correlation than retained connections (p < 0.01), confirming the mechanism operates as designed.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Δ CKA ≤ 2% (within noise range, no meaningful improvement)

2. **Mechanism Failure**: Pruned vs retained connections show no alignment correlation difference (p > 0.05)

3. **Controllability Failure**: α-alignment relationship is non-monotonic or correlation < 0.5

4. **Baseline Failure**: Task accuracy drops >5% below standard training (catastrophic forgetting)

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - This is a novel intervention framework, not targeting specific SOTA benchmarks.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.8 (large, based on expected >10% improvement)
- Required runs: n ≥ 20
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds across conditions)
- Significance level: α = 0.05 (one-tailed for improvement)
- Multiple comparison correction: Bonferroni for secondary predictions
- Report format: Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does dual-plasticity training produce measurable alignment improvement (>10% debiased CKA increase) compared to standard training?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical comparison
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is alignment-weighted importance scoring the actual cause of improved alignment, operating through the 4-step causal chain?"
- Maps to: Causal mechanism (N=4 steps)
  - SH2.1: Alignment signal → Importance scores
  - SH2.2: Importance scores → Structural decisions
  - SH2.3: Structural decisions → Topology modification
  - SH2.4: Topology modification → Alignment improvement
- Verification type: Causal analysis with ablations
- Critical: Determines explanatory power
- **Note:** Phase 2B will decompose into 4 sub-hypotheses (H-M1 through H-M4)

**SH3 (Comparison):**
"Does dual-plasticity outperform loss-based alignment methods (Muttenthaler) in controllability and/or alignment magnitude?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical
- Critical: Determines practical value vs existing methods

**Total sub-hypotheses in Phase 2B:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-DualPlasticity-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps, evidence table provided)
- [x] Causal chain length (N=4) determined and documented
- [x] Key tension identified (biased vs debiased CKA) and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (P1 primary, P2/P3 secondary)
- [x] Falsification criteria are defined (4 conditions)
- [x] Baselines are identified: Standard training, Muttenthaler loss, RE-CONTROL
- [x] SH1, SH2, SH3 are clear starting points for Phase 2B

### Open Questions

1. **Resource Requirements:**
   - Compute: ~100 GPU-hours for full ImageNet validation (n=20 runs on ResNet-50)

2. **Data Availability:**
   - Human similarity judgments: THINGS dataset available
   - fMRI data: Natural Scenes Dataset (NSD) requires application
   - Priority: Start with THINGS (easier access)

3. **Technical Feasibility:**
   - Top-KAST integration: Verify custom importance function injection
   - Debiased CKA implementation: Requires custom implementation

4. **Verification Priority Order:**
   - Recommend: SH1 (existence) → SH2.1-2.4 (mechanism chain) → SH3 (comparison)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
