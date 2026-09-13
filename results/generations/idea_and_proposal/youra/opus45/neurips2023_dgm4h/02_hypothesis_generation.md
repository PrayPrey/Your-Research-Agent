# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-VA-CCVF-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under the condition of medical generative AI evaluation for chest X-ray synthesis, if we implement VLM-augmented cognitive-calibrated validation (combining VLM difficulty stratification, multi-expert annotation with active learning, and asymmetric hardness-aware metrics), then AI performance assessment accuracy will correlate more strongly with deployment outcomes than single ground-truth approaches, because expert disagreement patterns contain meaningful clinical signal about case difficulty that current benchmarks ignore.

**Alternative Hypothesis (H0):**
There is no significant improvement in deployment outcome prediction when using VLM-augmented cognitive-calibrated validation compared to traditional single ground-truth evaluation approaches. Expert disagreement is annotation noise rather than meaningful clinical signal.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| VLM difficulty stratification | Independent | VLM-estimated case difficulty score (0-1 scale) computed using Med-PaLM or BiomedCLIP on chest X-ray images before expert annotation | 0.0-1.0 continuous score |
| Multi-expert annotation protocol | Independent | Active learning-guided annotation with 5+ experts per high-disagreement case, 1-2 experts per low-disagreement case, targeting 80% annotation cost reduction | Binary: AL-guided vs. uniform annotation |
| Asymmetric hardness-aware metrics | Independent | HaPrecision, HaRecall, and Brittleness Gap (B-Gap) computed from calibrated expert consensus | HaPrecision: 0-1, HaRecall: 0-1, B-Gap: 0-100% |
| AI performance assessment accuracy | Dependent | Correlation between validation framework predictions and actual deployment failure rate (measured 6+ months post-deployment) | Pearson r: 0.0-1.0 |
| Deployment risk prediction | Dependent | Precision/recall of identifying AI systems that fail in clinical deployment | Precision: 0-1, Recall: 0-1 |
| Clinical domain | Controlled | Chest X-ray generation initially, single imaging modality | Fixed: CXR |
| Expert panel composition | Controlled | Board-certified radiologists with 5+ years experience | Fixed: 5+ years, board-certified |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
VLM Difficulty Stratification → Reduced Annotation Cost → Calibrated Expert Consensus → Asymmetric Metrics → Deployment Risk Prediction
```

**Step 1: VLM Difficulty Stratification → Reduced Annotation Cost**
- VLM pre-screening identifies easy cases requiring minimal expert effort
- Active learning focuses 80% of multi-expert annotation on high-disagreement cases
- Evidence: VLM neuroradiology study (2025) shows 35% VLM vs 86.2% expert accuracy gap validates difficulty detection

**Step 2: Stratified Multi-Expert Annotation → Calibrated Expert Consensus**
- Cognitive diagnostic modeling applied to expert response patterns
- Extracts latent difficulty factors and creates probability distributions
- Evidence: Zheng et al. (2026) demonstrated non-parametric CDM for 41 LLMs across 22 medical subdomains

**Step 3: Calibrated Consensus → Asymmetric Hardness-Aware Metrics**
- HaPrecision/HaRecall weight failures by case difficulty
- B-Gap quantifies brittleness by comparing easy vs hard case performance
- Evidence: HaME (2025) showed B-Gap better identifies brittle AI systems

**Step 4: Asymmetric Metrics → Deployment Risk Prediction**
- Dual-track reporting provides both absolute thresholds (regulatory) and relative metrics (deployment risk)
- Evidence: RWE-LLM (2025) showed output testing > input validation with 6,234 clinicians

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | VLM medical imaging review (2025) | VLMs can assess image quality and difficulty | Medium |
| Step 2 → Step 3 | Zheng et al. (2026) Nature Scientific Reports | Cognitive diagnostic models reveal mastery patterns | Strong |
| Step 3 → Step 4 | HaME (2025) IEEE BIBM | B-Gap predicts deployment brittleness | Strong |
| Step 4 → Outcome | RWE-LLM (2025), AgentClinic (2024) | Output-based validation superior | Medium |

**Key Tension:**
- Tension: Zheng et al. (2026) demonstrates cognitive diagnostic modeling works for MCQ/classification, but VA-CCVF applies it to generative AI evaluation
- Resolution: This verification plan tests whether cognitive calibration transfers from classification to generation tasks by validating on chest X-ray quality assessment

### 1.4 Key Assumptions

1. **Expert disagreement reflects clinical ambiguity, not noise**
   - Evidence: Croskerry (2023) dual-process theory; MEDFAIR (2022) shows 30% fairness gap
   - Consequence if violated: Calibration approach collapses; expert disagreement becomes uninformative

2. **VLMs can reliably estimate case difficulty for chest X-rays**
   - Evidence: VLM neuroradiology study (2025) shows 35% VLM vs 86.2% expert accuracy gap
   - Consequence if violated: Stratification fails; must fall back to uniform multi-expert annotation

3. **Non-parametric cognitive diagnostic models transfer to medical AI evaluation**
   - Evidence: Zheng et al. (2026) applied CDM to 41 LLMs across 22 medical subdomains
   - Consequence if violated: Must develop domain-specific modeling approach

4. **Asymmetric cost functions improve deployment decision quality**
   - Evidence: HaME (2025) showed B-Gap better identifies brittle AI systems
   - Consequence if violated: Traditional aggregate metrics sufficient; framework adds complexity without benefit

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Medical generative AI systems producing synthetic chest X-ray images
- Validation scenarios requiring multi-expert annotation infrastructure
- Regulatory submission preparation (FDA 510(k), CE marking)

**Where Hypothesis Does NOT Apply:**
- Real-time clinical decision support (latency constraints)
- Natural language generation without structured ground truth
- Low-resource settings without VLM inference access

**Known Limitations:**
- VLM difficulty estimation requires validation per imaging modality
- Multi-expert annotation requires radiologist collaboration (minimum 5 experts)
- Regulatory acceptance of relative metrics uncertain
- Initial scope limited to chest X-ray

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Deployment Risk Prediction vs. Single Ground-Truth)**:
VA-CCVF will achieve higher correlation with deployment outcomes (Pearson r > 0.70) compared to single ground-truth validation approaches (expected r ≈ 0.40-0.50).

*Measurement*: Correlation coefficient between VA-CCVF risk scores and actual 6-month deployment failure rates
*Statistical test*: Fisher's z-test for correlation comparison, p < 0.05
*Sample size*: Minimum n = 20 AI systems evaluated, 5+ deployment sites

*Success Criteria*: r(VA-CCVF, deployment) > 0.70 (p < 0.05)
*Falsification*: r(VA-CCVF, deployment) ≤ 0.50 triggers rejection

**Secondary Predictions:**

**P2 (Annotation Cost Reduction)**:
VLM-guided active learning will reduce multi-expert annotation cost by ≥80% while maintaining calibration quality (expert consensus entropy within 10% of full annotation).

**P3 (Brittleness Detection)**:
B-Gap will identify AI systems with deployment failures (sensitivity ≥ 0.85) better than aggregate accuracy alone (expected sensitivity ≈ 0.50).

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:
1. **Primary Failure**: r(VA-CCVF, deployment) ≤ 0.50 (no improvement over baseline)
2. **Mechanism Failure**: VLM difficulty estimates do not correlate with expert disagreement (r < 0.30)
3. **Transfer Failure**: Cognitive diagnostic modeling cannot be applied to image quality assessment
4. **Cost Failure**: Annotation cost reduction < 50% while maintaining calibration quality

### 1.7 SOTA Baseline (Optional)

**Mode: Absolute Performance Mode** (No direct SOTA numerical comparison)

Baselines for comparison:
- GMAI-MMBench: Single ground-truth, classification-focused
- FID/KID: Image quality metrics without clinical calibration
- Traditional inter-rater reliability (Fleiss' Kappa): Treats disagreement as noise

### 1.8 Statistical Verification Design

**Sample Size**: n ≥ 20 AI systems, 5+ deployment sites each
**Effect Size**: Cohen's d ≈ 0.8 (large effect for correlation difference)
**Statistical Power**: 0.80
**Test**: Fisher's z-transformation for correlation comparison
**Significance**: α = 0.05 (one-tailed, superiority)
**Multiple Testing**: Bonferroni correction for 3 primary predictions

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does VLM difficulty stratification correlate with expert disagreement patterns in chest X-ray quality assessment?"
- Maps to: Causal Link 1 (VLM stratification → annotation cost)
- Verification type: Empirical correlation study
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is cognitive-calibrated expert consensus the actual mechanism improving deployment prediction?"
- Maps to: Causal chain (4 sub-hypotheses H-M1 through H-M4)
  - H-M1: VLM difficulty → Expert disagreement correlation
  - H-M2: Active learning → Annotation efficiency
  - H-M3: Cognitive diagnostic modeling → Calibrated consensus
  - H-M4: Asymmetric metrics → Deployment risk accuracy
- Verification type: Causal analysis with ablation studies
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does VA-CCVF outperform single ground-truth validation in deployment outcome prediction?"
- Maps to: Primary prediction (P1)
- Verification type: Comparative empirical study
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 6 (SH1: 1, SH2: 4, SH3: 1)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-VA-CCVF-v1)
- [x] Confidence level specified (0.82)
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps, evidence table completed)
- [x] Causal chain length (N=4) determined and documented
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 predictions, primary marked)
- [x] Falsification criteria are defined (4 criteria)
- [x] Baselines are identified for comparison
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Data Availability:** Access to chest X-ray datasets with multi-expert annotations (MIMIC-CXR with additional labels)? May require new annotation study.

2. **VLM Selection:** Which medical VLM (Med-PaLM, BiomedCLIP, RadFM) provides best difficulty estimation? Requires pilot comparison.

3. **Regulatory Engagement:** Should FDA/CE guidance be sought early for dual-track reporting acceptance?

4. **Priority Order:** Recommend starting with SH1 (VLM-expert correlation) as critical gate before full framework implementation.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
