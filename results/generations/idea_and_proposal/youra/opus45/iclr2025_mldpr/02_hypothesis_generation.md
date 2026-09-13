# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-VLB-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under conditions where benchmark datasets experience sustained high model submission rates, if epoch versioning with automated saturation detection is implemented, then benchmark relevance will be maintained (measured by performance variance staying above threshold) while preserving cross-temporal comparability (measured by rank correlation > 0.7 across epochs), because performance variance compression signals dataset staleness that can be proactively addressed through epoch transitions.

**Alternative Hypothesis (H0):**
Epoch versioning with automated saturation detection does not meaningfully maintain benchmark relevance or cross-temporal comparability; performance variance compression is not a reliable indicator of benchmark saturation, OR epoch transitions do not restore benchmark discriminative power.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Epoch transition frequency | Independent | Quarterly benchmark snapshots with semantic versioning (v1.0, v1.1, v2.0) | 3-6 months between major epochs |
| Saturation threshold | Independent | Variance compression ratio: trigger transition when top-k model performance variance drops below 0.5× baseline variance | Threshold: 0.3-0.7× baseline |
| Benchmark relevance | Dependent | Performance variance of top-k models remaining above threshold; distribution alignment with real-world data | Variance > 0.5× baseline; alignment score > 0.8 |
| Cross-temporal comparison validity | Dependent | Spearman rank correlation coefficient across epochs | r > 0.7 (target), r > 0.5 (minimum) |
| Dataset domain | Controlled | Fixed to tabular data initially (following TabArena), then vision/NLP | Tabular classification |
| Evaluation metrics | Controlled | Standard classification metrics: accuracy, F1, AUC-ROC | Fixed per epoch |
| Model submission format | Controlled | Standardized API interface for model predictions | Unified submission format |

### 1.3 Causal Mechanism

**Causal Chain (N=2):**

```
[Variance Monitoring] → [Saturation Detection] → [Epoch Transition + Restored Variance]
        Step 1                  Step 2                      Outcome
```

**Step 1: Variance Monitoring → Saturation Detection**
- **Mechanism:** Continuous monitoring of top-k model performance variance identifies when variance compression indicates saturation
- **Evidence:** Bouthillier et al. (2021) demonstrated variance measurement methodology; Koch et al. (2021) documented increasing concentration on fewer datasets
- **Falsification:** If variance compression does not reliably indicate saturation (e.g., due to genuine capability convergence or metric noise)

**Step 2: Saturation Detection → Epoch Transition + Restored Variance**
- **Mechanism:** Triggered epoch transition introduces fresh data, breaking dataset-specific overfitting and restoring performance variance
- **Evidence:** TabArena (2025) demonstrates continuous maintenance protocols maintain benchmark utility
- **Falsification:** If epoch transitions do not restore variance (e.g., new data too similar, or models learned domain-general patterns)

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Bouthillier et al. (2021), Madaan et al. (2024) | Variance metrics capture meaningful performance differences; seed variance and monotonicity measurable | Strong |
| Step 2 → Outcome | TabArena (2025), Koch et al. (2021) | Living benchmarks with maintenance protocols preserve utility; concentration problem is addressable | Medium |

**Key Tension:**
- **Tension:** Koch et al. (2021) shows concentration is increasing despite awareness, suggesting structural incentives favor familiar datasets. TabArena (2025) shows living benchmarks are technically feasible but requires sustained maintenance effort.
- **Resolution:** This verification plan tests whether automated saturation detection can reduce the maintenance burden while achieving comparable results to manual curation, making living benchmarks more sustainable.

### 1.4 Key Assumptions

1. **Benchmark saturation is measurable via performance variance compression**
   - Supporting evidence: Bouthillier et al. (2021) - variance from data sampling, initialization, and hyperparameters is measurable; Madaan et al. (2024) - seed variance and monotonicity metrics validated
   - Consequence if violated: Cannot automate saturation detection; would require manual expert judgment for epoch transitions

2. **Fresh data samples can be sourced continuously from existing pipelines**
   - Supporting evidence: TabArena (2025) demonstrates continuous data ingestion with quality checks
   - Consequence if violated: Epoch transitions become infeasible; framework degrades to static benchmark with manual updates

3. **Epoch versioning enables reproducibility without blocking evolution**
   - Supporting evidence: Git branching/tagging model in software engineering; TabArena's public leaderboard with versioned results
   - Consequence if violated: Historical comparison becomes invalid; community loses trust in benchmark

4. **Dual scoring captures both relevance and consistency trade-offs**
   - Supporting evidence: Cross-domain analogy from software CI/CD (continuous testing + release tagging)
   - Consequence if violated: Single-metric optimization continues; no improvement over current benchmarking practices

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Classification benchmarks (binary, multi-class)
- Tabular data domain (primary validation target, following TabArena)
- Vision and NLP domains (secondary extension targets)
- Benchmarks with sustained submission activity (>50 submissions/epoch)
- Repository-integrated benchmarks (OpenML, HuggingFace)

**Where Hypothesis Does NOT Apply:**
- Generative model evaluation (different metrics, no clear "saturation" signal)
- Real-time streaming benchmarks (continuous evaluation, no epoch concept)
- Low-activity benchmarks (<10 submissions/epoch, insufficient variance data)
- Benchmarks with proprietary/restricted data (cannot implement fresh data ingestion)

**Known Limitations:**
- Saturation threshold (0.5× baseline) is heuristic; may need domain-specific tuning
- Epoch transition timing may trigger too early (false positive) or too late (delayed response)
- Requires sustained data curation infrastructure investment
- Cross-temporal rank correlation assumes model quality is relatively stable across epochs

### 1.6 Testable Predictions

**Primary Prediction (P1):**
**P1 (Variance Restoration)**:
If VLB epoch versioning with automated saturation detection is implemented, then:
- Top-k model performance variance will remain above the saturation threshold (>0.5× baseline variance) post-transition

*Measurement*:
- Performance variance of top-10 models calculated per epoch
- Variance restoration: post-transition variance > 0.5× pre-saturation baseline variance
- Statistical test: Paired t-test comparing pre-transition (saturated) vs post-transition variance, p < 0.05

*Basis*:
Domain standard for ML benchmarking; variance compression documented as saturation indicator by Bouthillier et al. (2021)

*Success Criteria for Phase 2B*:
- Primary: Post-transition variance > 0.5× baseline (p < 0.05)
- Falsification: Post-transition variance ≤ 0.3× baseline triggers rejection

**Secondary Predictions:**

**P2 (Cross-Temporal Validity)**:
If dual scoring (current epoch + historical consistency) is implemented, then model rankings on epoch E_n will correlate with rankings on E_(n+k) with Spearman r > 0.7

*Measurement*: Spearman rank correlation between epoch rankings
*Success Criteria*: r > 0.7 for k=1 (adjacent epochs), r > 0.5 for k=2-3

**P3 (Saturation Detection Accuracy)**:
If automated saturation detection triggers an epoch transition, then post-transition variance will increase

*Measurement*: Compare variance 30 days before vs 30 days after triggered transition
*Success Criteria*: Variance increase > 20% with p < 0.05

**Falsification Criteria:**

The hypothesis will be **REJECTED** if:

1. **Primary Failure**: Post-transition variance ≤ 0.3× baseline variance
   (Epoch transitions do not restore benchmark discriminative power)

2. **Mechanism Failure**: Variance compression does not correlate with expert-judged saturation (r < 0.3)
   (Automated detection is not a valid saturation signal)

3. **Comparison Failure**: Cross-temporal rank correlation r < 0.5 for adjacent epochs
   (Dual scoring does not preserve meaningful model comparisons)

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - This is framework/methodology research, not performance improvement research.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): Expected ~0.6 (medium) for variance restoration
- Required epochs: Minimum 4 epochs (2 pre-transition, 2 post-transition)
- Required models per epoch: Minimum 50 unique model submissions
- Statistical power: 0.8

**Test Specification:**
- Primary test: Paired t-test for variance restoration (pre vs post transition)
- Secondary test: Spearman correlation for cross-temporal rank validity
- Significance level: α = 0.05 (one-tailed for directional hypotheses)
- Report format: Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does performance variance compression occur in saturated benchmarks, and can it be reliably detected through automated monitoring?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical analysis of existing benchmark data
- Critical: MUST PASS for Phase 2B to proceed
- **Count:** 1 sub-hypothesis

**SH2 (Mechanism):**
"Is the proposed causal mechanism (variance monitoring → saturation detection → epoch transition → variance restoration) the actual cause of maintained benchmark relevance?"
- Maps to: Causal mechanism (N=2 steps)
  - H-M1: Variance compression reliably indicates saturation
  - H-M2: Epoch transitions restore benchmark discriminative power
- Verification type: Causal analysis with controlled experiments
- Critical: Determines explanatory power
- **Count:** 2 sub-hypotheses (based on N=2 causal chain)

**SH3 (Comparison):**
"Does the VLB dual scoring protocol outperform single-epoch scoring in maintaining cross-temporal model comparability?"
- Maps to: Secondary prediction (P2)
- Verification type: Comparative empirical analysis
- Critical: Determines practical value
- **Count:** 1 sub-hypothesis

**Total sub-hypotheses in Phase 2B:** 2 + 2 = 4 (SH1 + SH2×2 + SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-VLB-v1
- [x] Confidence level specified: 0.78
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence (7 variables specified)
- [x] Causal mechanism has evidence at each step (N=2 steps, evidence table provided)
- [x] Causal chain length (N=2) determined and documented
- [x] Key tension identified (structural incentives vs technical feasibility) and resolution proposed
- [x] Key assumptions list consequences if violated (4 assumptions)
- [x] At least 2 testable predictions exist (3 predictions: P1 primary, P2, P3)
- [x] Falsification criteria are defined (3 conditions)
- [x] Baselines are identified for comparison (Open Graph Benchmark, static benchmarks)
- [x] SH1, SH2, SH3 are clear starting points for Phase 2B decomposition

### Open Questions

1. **Data Availability:** Can we access sufficient historical benchmark submission data (performance records, timestamps) from TabArena or OpenML to validate variance compression patterns? If not, need to simulate or collect prospectively.

2. **Threshold Calibration:** The 0.5× baseline variance threshold is heuristic. Phase 2B should include sensitivity analysis to determine optimal threshold values across different dataset characteristics.

3. **Priority Verification Order:** Recommend verifying SH1 (existence of measurable saturation) first, as SH2 and SH3 depend on this foundation. If SH1 fails, the entire hypothesis framework requires revision.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
