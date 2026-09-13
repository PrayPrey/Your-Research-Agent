# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-EFA-v1
**Confidence Level:** 0.83

**Main Hypothesis:**
Under the condition of having 50-100 experimental design-outcome pairs available, if SE(3)-equivariant scalar injection adapters encode experimental feedback (success/failure, binding affinity, expression level) into frozen protein generative models (RFdiffusion, FrameFlow), then wet-lab success rates will improve by ≥2x compared to unconditional generation, because scalar invariants modulate equivariant feature magnitudes to bias generation toward experimentally validated design space regions without breaking geometric symmetries.

**Alternative Hypothesis (H0):**
SE(3)-equivariant scalar injection does not significantly improve wet-lab success rates compared to unconditional generation, either because: (a) experimental feedback cannot be meaningfully encoded as scalar invariants, (b) scalar injection disrupts rather than guides learned representations, or (c) the improvement is statistically indistinguishable from random variation.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| EFA Architecture | Independent | Scalar injection layers at IPA (Invariant Point Attention) modules in RFdiffusion/FrameFlow; parameterized by injection depth (1-4 layers) and scalar dimensionality (16-128) | Depth: 1-4 IPA layers; Dim: 16, 32, 64, 128 |
| Feedback Encoding | Independent | Binary success/failure labels + continuous metrics (binding affinity Kd, expression level, stability ΔTm) normalized to [0,1] range | Binary: {0,1}; Continuous: [0,1] normalized |
| Learning Strategy | Independent | Contrastive learning on (successful, failed) pairs + prototype-based conditioning with k prototypes | k = 5-10 prototypes; InfoNCE loss |
| Wet-lab Success Rate | Dependent | Percentage of generated designs passing functional assay (binding, activity, expression) out of total synthesized designs | Baseline: 5-20%; Target: ≥2x baseline |
| Sample Efficiency | Dependent | Number of experimental rounds required to achieve target success rate (e.g., 50% functional) | Baseline: 5-10 rounds; Target: 2-4 rounds |
| Design Diversity | Dependent | Sequence identity and structural RMSD distribution of generated designs | Seq ID: <50%; RMSD: >2Å from training |
| Base Generative Model | Controlled | Frozen RFdiffusion or FrameFlow with fixed weights | No fine-tuning during EFA training |
| Target Protein System | Controlled | Specific protein engineering task | PD-L1 binder, GFP variant, or GB1 fitness |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Experimental Feedback → Scalar Invariant Encoding
   ↓
Step 2: Scalar Encoding → Feature Magnitude Modulation (IPA layers)
   ↓
Step 3: Feature Modulation → Generation Bias (toward successful regions)
   ↓
Step 4: Generation Bias → Improved Wet-lab Success Rate
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | EGNN, GVP literature | Scalar-vector interactions preserve equivariance mathematically | Strong |
| Step 2 → Step 3 | ControlNet (Zhang et al.) | Adapter injection modulates generation without retraining | Strong |
| Step 3 → Step 4 | Calvanese et al. 2025 | Feedback integration improves success 6.7% → 63.7% | Strong |
| Overall mechanism | ProSpero 2025 | Frozen generative + learnable surrogate achieves high fitness | Strong |

**Key Tension:**
- **Tension:** Calvanese et al. uses likelihood-based reintegration (modifies sampling probability directly), while EFA uses conditioning-based approach (modifies feature representations). It is unclear which approach provides better sample efficiency.
- **Resolution:** This verification plan will directly compare EFA conditioning against likelihood reintegration as an ablation study.

### 1.4 Key Assumptions

1. **Pre-trained model steerability:** Pre-trained protein generative models capture sufficient structural diversity that can be steered by scalar conditioning signals without requiring weight updates.
   - *Consequence if violated:* EFA would require partial fine-tuning, increasing computational cost.

2. **Learnable failure patterns:** Experimental failure modes exhibit learnable patterns in sequence-structure space.
   - *Consequence if violated:* EFA would not outperform random conditioning; hypothesis rejected.

3. **Scalar sufficiency:** Scalar invariants are mathematically sufficient to encode relevant experimental feedback while preserving SE(3) equivariance.
   - *Consequence if violated:* Would require vector-valued feedback injection, increasing complexity.

4. **Data efficiency:** 50-100 experimental design-outcome pairs provide adequate signal for contrastive learning.
   - *Consequence if violated:* Would require 500-1000 experiments, limiting practical applicability.

### 1.5 Scope & Boundaries

**Applies to:**
- SE(3)-equivariant protein generative models (RFdiffusion, FrameFlow, Chroma)
- Protein engineering tasks with measurable experimental outcomes
- Batch-based wet-lab workflows (10-100 designs per round)

**Does NOT apply to:**
- Non-equivariant generative models
- Small molecule generation
- Single-shot design tasks without iterative feedback

**Known limitations:**
- Requires initial data or in-silico surrogate for cold-start
- Transfer across protein families not validated

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Wet-lab Success Rate Improvement):**
EFA-conditioned generation will achieve wet-lab success rate ≥2x higher than unconditional generation.

*Measurement:* Two-proportion z-test, p < 0.05, n ≥ 50 designs per condition
*Falsification:* Success rate ratio ≤ 1.2

**Secondary Predictions:**

**P2 (SE(3) Equivariance Preservation):**
Generated structures will maintain SE(3) equivariance metrics within 1% of unconditional generation.

**P3 (Sample Efficiency):**
EFA will achieve 50% success rate in ≤3 rounds vs. ≥6 rounds for unconditional + selection.

**P4 (Cold-start Performance):**
EFA with in-silico predictor feedback will outperform random baseline in round 0.

**Falsification Criteria:**

1. **Primary Failure:** Success rate ratio < 1.2x
2. **Mechanism Failure:** SE(3) equivariance error > 5%
3. **Efficiency Failure:** No improvement in sample efficiency
4. **Baseline Failure:** EFA performs worse than fine-tuning

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 50 designs per condition (power=0.80, α=0.05)
**Test:** Two-proportion z-test with Bonferroni correction
**Report:** Success rates with 95% CI, effect size (RR), p-values

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does SE(3)-equivariant scalar injection successfully condition frozen protein generative models without breaking geometric symmetries?"
- Verification: Architectural validation + equivariance error measurement
- Critical: MUST PASS for hypothesis to proceed

**SH2 (Mechanism) - Will decompose into 4 sub-hypotheses (H-M1 to H-M4):**
"Is the proposed 4-step causal mechanism the actual cause of improved wet-lab success rates?"
- H-M1: Feedback encoding captures discriminative patterns
- H-M2: Scalar injection modulates features as designed
- H-M3: Modulation biases generation toward successful regions
- H-M4: Biased generation translates to wet-lab improvement

**SH3 (Comparison):**
"Does EFA outperform baseline approaches (unconditional, likelihood reintegration, fine-tuning)?"
- Verification: Controlled comparison across ≥2 protein targets

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-EFA-v1)
- [x] Confidence level specified (0.83)
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified + resolution proposed
- [x] Assumptions list consequences if violated
- [x] 4 testable predictions (primary marked)
- [x] Falsification criteria defined
- [x] 3 baselines identified
- [x] SH1, SH2, SH3 defined

### Open Questions

1. **Data Availability:** Are paired experimental design-outcome datasets available for benchmarks (GB1, GFP, AAV)?

2. **Computational Resources:** What is the training time and GPU memory requirement for EFA adapters?

3. **Priority Verification Order:** Should SH1 be fully verified before wet-lab experiments, or can SH1 and SH2-M1 proceed in parallel?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
