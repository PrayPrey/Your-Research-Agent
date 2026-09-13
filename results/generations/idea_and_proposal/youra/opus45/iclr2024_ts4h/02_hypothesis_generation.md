# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SENTINEL-ADAPT-v1
**Confidence Level:** 0.83

**Main Hypothesis:**
Under healthcare deployment conditions with distribution shift, if an immunology-inspired framework (SENTINEL-ADAPT) with batched drift detection (KS-test, MMD), Reptile-style meta-learning adaptation, and experience replay is applied, then deployed ML models will maintain AUROC within 5% of original performance because: (1) sentinel-based drift detection enables early shift identification via statistical monitoring, (2) lightweight meta-learning enables rapid adaptation with limited samples using first-order gradient updates, and (3) experience replay with distribution-tagged exemplars prevents catastrophic forgetting of the original distribution.

**Alternative Hypothesis (H0):**
There is no significant relationship between the SENTINEL-ADAPT framework's components and model performance maintenance under distribution shift. Specifically: (a) drift detection does not enable earlier identification than periodic retraining schedules, (b) meta-learning adaptation provides no advantage over full model retraining, or (c) experience replay does not prevent performance degradation on original distributions.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Drift detection sensitivity threshold | Independent | KS-test and MMD p-value threshold on batched feature embeddings | 0.01-0.05 (configurable) |
| Adaptation rate | Independent | Reptile-style gradient step size, updates per detected shift event | 0.001-0.01 |
| Monitoring frequency | Independent | Batch interval for drift detection execution | Hourly, Daily, or Event-triggered |
| AUROC under shift | Dependent | Area under ROC curve on shifted test set | Target: ≥95% of original (within 5% degradation) |
| Adaptation latency | Dependent | Hours from shift detection to performance recovery | Target: ≤24 hours |
| Forgetting rate | Dependent | AUROC delta on original distribution after adaptation | Target: ≤3% degradation |
| Memory buffer size | Controlled | Fixed exemplar count with distribution provenance tags | 10,000 samples |
| Base model architecture | Controlled | Foundation model architecture (STraTS-based or similar) | Fixed per experiment |
| Dataset | Controlled | MIMIC-III/IV with temporal splits simulating distribution shift | Fixed per experiment |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
[Sentinel Module] → [Shift Detection] → [Adaptation Trigger] → [Model Update] → [Performance Maintenance]
```

**Step 1: Sentinel Module → Shift Detection**
- **Mechanism:** Continuous statistical monitoring (KS-test, MMD) on batched feature embeddings identifies when incoming data distribution deviates significantly from training distribution
- **Evidence:** Exa papers (Nature Communications 2024) demonstrate effectiveness of statistical drift detection; Schrouff et al. 2022 provides causal framing for distribution shift diagnosis
- **Falsification Point:** If distribution shift is gradual and falls below statistical detection threshold, shift goes undetected → Silent performance degradation

**Step 2: Shift Detection → Adaptation Trigger**
- **Mechanism:** Detected shift signals activate the meta-learning adaptation engine only when statistically significant drift is confirmed (p < threshold), preventing unnecessary updates
- **Evidence:** Unsupervised Prediction Alignment (Roschewitz et al. 2023) shows automatic recalibration can be triggered without ground truth labels
- **Falsification Point:** If threshold is too sensitive (false positives) or too lax (false negatives), adaptation is triggered inappropriately → Unnecessary adaptation or missed shifts

**Step 3: Adaptation Trigger → Model Update**
- **Mechanism:** Reptile-style first-order gradient updates with rate limits allow the model to learn from new distribution while validation gates prevent harmful updates
- **Evidence:** Gen-P-Tuning 2024 demonstrates lightweight adaptation for frozen models; Reptile meta-learning literature shows effectiveness with limited samples
- **Falsification Point:** If new distribution requires fundamentally different model architecture rather than parameter updates → Adaptation fails to improve performance

**Step 4: Model Update → Performance Maintenance**
- **Mechanism:** Updated model parameters combined with experience replay buffer samples maintain performance on both old and new distributions
- **Evidence:** Critical Care FM 2024 harmonized dataset approach; continual learning literature on replay buffers
- **Falsification Point:** If experience replay buffer is too small or poorly sampled → Catastrophic forgetting occurs

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Sentinel → Detection | Kore et al. 2024 (Nature Comms), Roschewitz et al. 2023 | Statistical drift detection (KS-test, MMD) effectively identifies distribution shift in medical imaging | Strong |
| Detection → Trigger | Schrouff et al. 2022 | Causal framing enables principled shift diagnosis; threshold selection affects false positive/negative rates | Strong |
| Trigger → Update | Gen-P-Tuning 2024, Reptile literature | First-order meta-learning enables adaptation with <100 samples | Medium |
| Update → Performance | Critical Care FM 2024 | Harmonized datasets enable cross-hospital transfer learning; distribution shift challenges addressed | Medium |

**Key Tension:**
- **Tension:** Roschewitz et al. 2023 shows automatic recalibration preserves sensitivity/specificity without labels, BUT Kore et al. 2024 demonstrates drift detection on imaging data may not directly transfer to time series embeddings
- **Resolution:** This verification plan tests whether statistical tests on time series feature embeddings (not raw pixels) maintain detection effectiveness, with comparison to image-based methods as ablation

### 1.4 Key Assumptions

1. **Distribution shift in healthcare is detectable through statistical monitoring**
   - Supporting Evidence: Schrouff et al. 2022 causal framing; Exa drift detection papers showing KS-test and MMD effectiveness
   - **Consequence if Violated:** Framework cannot trigger adaptation proactively; falls back to reactive monitoring (performance degradation before detection)

2. **Reptile-style meta-learning can adapt with limited samples (<100 per shift)**
   - Supporting Evidence: Gen-P-Tuning 2024 lightweight adaptation for frozen models; meta-learning literature
   - **Consequence if Violated:** Adaptation requires full retraining (computational cost increase 10-100x); deployment advantage lost

3. **Experience replay with 10K samples prevents catastrophic forgetting**
   - Supporting Evidence: Continual learning literature; Critical Care FM 2024 harmonized dataset design
   - **Consequence if Violated:** Adapted model loses performance on original distribution; requires maintaining multiple model versions

4. **Interpretability via SHAP can be maintained during adaptation**
   - Supporting Evidence: SHAP is model-agnostic; explainability frameworks work with fine-tuned models
   - **Consequence if Violated:** Compliance layer cannot provide explanations; limits clinical deployment scope

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Healthcare time series data: ICU vitals, lab values, temporal EHR features
- Deployment scenarios with gradual or sudden distribution shift
- Research validation context (not FDA/EMA-approved clinical deployment)
- Foundation models amenable to gradient-based fine-tuning (STraTS, Medformer, HyMaTE-style)

**Where Hypothesis Does NOT Apply:**
- Real-time sub-second clinical alerts (batched monitoring adds latency)
- Regulatory-approved clinical decision support systems (requires additional validation)
- Streaming data without sufficient batch accumulation (minimum ~100 samples)
- Non-gradient-based models (rule-based systems, decision trees)

**Known Limitations:**
- Batched monitoring reduces real-time responsiveness (minimum 1-hour delay in detection)
- Simplified Reptile meta-learning may not capture all shift types (concept drift vs. covariate shift)
- Research scope limits immediate clinical deployment claims
- MIMIC dataset may not represent all healthcare settings (academic medical centers bias)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Performance Under Shift - Absolute Target):**
SENTINEL-ADAPT will maintain AUROC ≥ 95% of pre-shift performance (within 5% degradation) when evaluated on temporally-shifted MIMIC test sets, compared to static models that degrade >15% under the same conditions.

*Measurement:*
- AUROC on shifted test set ÷ AUROC on original test set ≥ 0.95
- Statistical test: Paired t-test across 5 random seeds, p < 0.05
- Sample size: n ≥ 25 runs (moderate effect size)

*Basis:*
Domain standard for healthcare ML deployment; 5% threshold based on clinical significance thresholds in literature

*Success Criteria for Phase 2B:*
- Primary: AUROC retention ≥ 95% with p < 0.05
- Falsification: AUROC retention < 85% OR no significant difference from static baseline triggers rejection

**Secondary Predictions:**

**P2 (Adaptation Latency):**
If distribution shift is detected, performance recovery (return to within 5% of original AUROC) will occur within 24 hours of shift detection.

*Measurement:* Hours from detection event to performance threshold achievement
*Basis:* Clinical relevance - daily review cycles in ICU settings

**P3 (Forgetting Prevention):**
After adaptation to new distribution, performance on original distribution will remain within 3% of pre-adaptation AUROC.

*Measurement:* AUROC_original_after_adaptation ÷ AUROC_original_before_adaptation ≥ 0.97
*Basis:* Experience replay design; catastrophic forgetting literature thresholds

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure:** AUROC retention < 85% under distribution shift
   - Interpretation: Framework provides no meaningful protection against shift

2. **Mechanism Failure:** Drift detection accuracy < 70% (precision + recall / 2)
   - Interpretation: Sentinel module cannot reliably identify shifts

3. **Forgetting Failure:** Original distribution AUROC drops > 10% after adaptation
   - Interpretation: Experience replay fails to prevent catastrophic forgetting

4. **Latency Failure:** Recovery takes > 72 hours consistently across shift types
   - Interpretation: Adaptation is too slow for clinical relevance

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - Absolute Performance Mode*

This hypothesis targets deployment robustness under distribution shift rather than SOTA accuracy improvement.

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): Estimated 0.6-0.8 (medium-large)
- Required runs: n ≥ 25 per condition
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds across conditions)
- Significance level: α = 0.05 (two-tailed for main comparisons)
- Multiple comparison correction: Bonferroni for P1-P3

**Report Format:**
- Mean ± Std Dev for all metrics
- 95% Confidence Interval
- Cohen's d effect size
- p-value with multiple comparison adjustment

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence - 1 hypothesis):**
"Does SENTINEL-ADAPT maintain model performance (AUROC ≥95% retention) under simulated distribution shift in MIMIC temporal splits?"
- Maps to: Primary prediction P1
- Verification type: Empirical
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism - 4 hypotheses: H-M1 through H-M4):**
"Is each component of the four-step causal mechanism operating as proposed?"

- **H-M1:** Does the Sentinel Module reliably detect distribution shift via statistical tests?
- **H-M2:** Does the detection-to-trigger threshold appropriately balance false positives/negatives?
- **H-M3:** Does Reptile-style adaptation improve performance on shifted data with <100 samples?
- **H-M4:** Does experience replay maintain original distribution performance within 3%?

- Maps to: Causal mechanism (4 steps)
- Verification type: Causal analysis / ablation studies
- Critical: Determines explanatory power

**SH3 (Comparison - 1 hypothesis):**
"Does SENTINEL-ADAPT outperform baseline deployment strategies (static, periodic retraining) on performance retention, adaptation latency, and forgetting metrics?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-SENTINEL-ADAPT-v1
- [x] Confidence level specified: 0.83
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (4 steps, evidence_for_links table)
- [x] Causal chain length (N=4) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 predictions, primary marked)
- [x] Falsification criteria are defined (4 failure conditions)
- [x] Baselines are identified for comparison (static, periodic retraining, simple online)
- [x] SH1, SH2, SH3 are clear starting points

**All 13 items verified ✓**

### Open Questions

1. **Data Availability:** Can MIMIC temporal splits adequately simulate realistic distribution shifts (COVID-era vs. pre-COVID, hospital policy changes)? May need additional validation datasets.

2. **Computational Resources:** What is the overhead of continuous drift detection? Need to measure latency and memory impact for practical deployment feasibility.

3. **Priority Verification Order:** Recommend starting with SH1 (existence) → SH2-H-M1 (detection works) → SH2-H-M3 (adaptation works) → remaining components. This validates critical path first.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
