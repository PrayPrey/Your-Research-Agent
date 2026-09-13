# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-TCBM-v1
**Confidence Level:** 0.84

**Main Hypothesis:**
Under clinical time series classification/prediction tasks (C), if we constrain temporal representations to pass through hierarchical clinical concepts (beat→segment→episode) with a hybrid residual pathway (X), then the model will achieve interpretability significantly higher than attention-based methods while maintaining accuracy within 3% of black-box transformers (Y), because the concept bottleneck forces representations to align with human-understandable clinical patterns while the residual pathway preserves predictive capacity for patterns not captured by predefined concepts (Z).

**Alternative Hypothesis (H0):**
There is no meaningful difference in interpretability between concept-constrained temporal representations and attention-based explanations, OR the accuracy degradation from concept bottleneck constraints exceeds 3% compared to black-box transformers.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Concept alignment loss weight (λ_concept) | Independent | Weight in joint loss: λ_concept × L_concept + λ_task × L_task | [0.1, 1.0], default 0.5 |
| Multi-scale concept hierarchy | Independent | Three-level: beat (1s), segment (5min), episode (1hr+) | 3 scales fixed |
| Residual pathway ratio | Independent | Fraction of representation for learned residual concept | [0.1, 0.3], default 0.2 |
| Downstream task accuracy | Dependent | AUROC/AUPRC on held-out test set (sklearn metrics) | Target: ≥97% of black-box |
| Interpretability score | Dependent | Concept intervention accuracy + clinician ratings (1-5 Likert) | Target: >3.5/5 rating |
| Dataset | Controlled | MIMIC-IV (ICU vitals) or PTB-XL (ECG) | Fixed preprocessing |
| Base architecture | Controlled | Temporal transformer: hidden=256, 4 layers, standard PE | Fixed architecture |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Temporal Encoder → Multi-Scale Concept Extraction
        ↓
Step 2: Multi-Scale Concept Extraction → Concept Bottleneck Layer
        ↓
Step 3: Concept Bottleneck Layer → Hybrid Representation
        ↓
Step 4: Hybrid Representation → Clinical Outcome + Interpretation
```

**Step 1: Temporal Encoder → Multi-Scale Concept Extraction**
- Mechanism: Transformer with positional encoding extracts features at beat/segment/episode scales
- Evidence: Standard temporal transformer architecture; validated in time series literature
- Falsification: Ablation showing single-scale performs equally (multi-scale adds no value)

**Step 2: Multi-Scale Concept Extraction → Concept Bottleneck Layer**
- Mechanism: Extracted features projected to predefined clinical concepts via concept alignment loss
- Evidence: AnyCBM (2024) demonstrates concept projection with minimal loss; arXiv:2410.06070 shows CBM works for time series
- Falsification: Random concepts achieve same downstream performance (concept alignment meaningless)

**Step 3: Concept Bottleneck Layer → Hybrid Representation**
- Mechanism: Clinical concepts combine with residual pathway for patterns not covered by predefined concepts
- Evidence: AnyCBM (2024) residual pathway design preserves capacity; maintains performance when concepts incomplete
- Falsification: Residual pathway captures >50% of predictive information (concepts become irrelevant)

**Step 4: Hybrid Representation → Clinical Outcome + Interpretation**
- Mechanism: Concept-based representation enables both accurate prediction AND clinically meaningful explanation
- Evidence: CBM literature shows concept activations map to human reasoning; HITS (2025) validates temporal interpretability
- Falsification: Clinician ratings <3/5 or inter-rater κ <0.4 (concepts not clinically meaningful)

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Deep FCM (2021, 94 citations) | Hierarchical temporal structures capture time series patterns | Strong |
| Step2 → Step3 | AnyCBM (2024, 6 citations) | Concept projection maintains performance with residual pathway | Strong |
| Step3 → Step4 | arXiv:2410.06070 (2024) | CBM for time series transformers achieves interpretability without performance loss | Strong |
| Step4 → Outcome | HITS (2025), VLG-CBM (NeurIPS 2024) | Concept-based explanations rated higher than attention visualization | Medium |

**Key Tension:**
- **Tension:** arXiv:2410.06070 uses Centered Kernel Alignment for concept training, while AnyCBM uses post-hoc concept projection. These represent different training paradigms.
- **Resolution:** This verification plan tests both approaches: (1) joint training with concept alignment loss (primary) and (2) post-hoc concept projection (ablation) to determine which achieves better interpretability-performance tradeoff for clinical time series.

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|---------------------|-------------------------|
| A1 | Clinical concepts for ECG and ICU vitals can be defined from clinical guidelines | ICD-10, SNOMED-CT ontologies; PTB-XL expert annotations | Need to develop concept generation methodology; may require LLM-assisted concept extraction |
| A2 | Temporal transformer can learn concept-aligned representations with appropriate supervision | arXiv:2410.06070 demonstrates this for forecasting; AnyCBM shows it for classification | May need alternative encoder architecture (e.g., S4, Mamba) or different alignment loss |
| A3 | Performance-interpretability tradeoff is manageable (<3% accuracy drop) | AnyCBM reports <2% drop; CBM-TS paper reports "mostly unaffected" performance | May need to increase residual pathway ratio or relax concept constraints |
| A4 | Clinicians can reliably rate explanation quality (κ > 0.6) | Standard practice in medical AI evaluation; prior CBM studies | Need clearer rating guidelines or objective interpretability metrics |

### 1.5 Scope & Boundaries

**Applies to:**
- Clinical time series with definable temporal concepts (ECG, ICU vitals, wearable health data)
- Classification and prediction tasks where interpretability is valued (diagnosis, risk prediction)
- Domains with existing clinical ontologies or expert knowledge

**Does NOT apply to:**
- Time series without clinical concept vocabulary (financial, weather)
- Real-time inference requiring <10ms latency (concept layer adds overhead)
- Tasks where interpretability is not a requirement

**Known Limitations:**
- Concept completeness depends on expert knowledge availability
- LLM-generated concepts require clinical validation
- Multi-scale hierarchy design may need domain-specific tuning
- Evaluation requires clinical expert involvement (time/cost)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Interpretability vs Attention Baselines):**
T-CBM-MHR will achieve clinician interpretability ratings significantly higher (p < 0.05) than attention-based explanations on the same clinical time series tasks.

*Measurement:*
- Clinician ratings: T-CBM concepts > 3.5/5 AND T-CBM - Attention > 0.5 points (p < 0.05)
- Concept intervention accuracy: >70% (when correct concept is intervened, prediction changes appropriately)
- Statistical test: Paired t-test, n ≥ 20 clinician evaluations

*Basis:*
CBM literature consistently shows concept explanations rated higher than feature attribution methods. Target based on domain standard for "clinically meaningful" interpretation (>3.5/5).

*Success Criteria for Phase 2B:*
- Primary: Clinician rating difference > 0.5 points (p < 0.05)
- Falsification: Clinician ratings ≤ 3.0/5 OR no significant difference from attention

**Secondary Predictions:**

**P2 (Performance Preservation):**
T-CBM-MHR will maintain downstream task accuracy within 3% of black-box transformer baseline.

*Measurement:*
- AUROC(T-CBM) ≥ 0.97 × AUROC(black-box)
- Statistical test: Paired t-test, n ≥ 5 random seeds

**P3 (Multi-Scale Concept Value):**
Multi-scale concept hierarchy will outperform single-scale concept design on both interpretability and accuracy.

*Measurement:*
- Ablation: 3-scale vs 1-scale concept design
- Both metrics should favor multi-scale (p < 0.05)

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** Clinician interpretability ratings ≤ 3.0/5 OR no significant difference from attention-based explanations

2. **Performance Failure:** AUROC drop > 5% compared to black-box transformer

3. **Mechanism Failure:** Residual pathway captures >50% of predictive information

4. **Intervention Failure:** Concept intervention accuracy < 50%

### 1.7 SOTA Baseline (Optional)

**Mode:** Absolute Performance (Interpretability-focused, not SOTA comparison)

**Reference Baselines for Interpretability:**
- HITS (2025): Hierarchical MIL-based interpretability
- Attention visualization: Standard transformer attention weights
- Post-hoc SHAP: Feature attribution for time series

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Primary outcome: Clinician rating difference
- Effect size (Cohen's d): 0.8 (large effect for interpretability)
- Required evaluations: n ≥ 20 clinician ratings
- Statistical power: 0.8

**Test Specification:**
- Interpretability: Paired t-test (same cases rated by same clinicians)
- Accuracy: Paired t-test across random seeds
- Significance level: α = 0.05
- Report format: Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does the T-CBM-MHR architecture produce clinically meaningful concept activations when trained on clinical time series (ECG/ICU vitals)?"
- Maps to: Primary prediction P1
- Verification type: Empirical (concept activation analysis + clinician evaluation)
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism (encoder→concepts→hybrid→prediction) the actual cause of improved interpretability?"
- Maps to: Causal mechanism (4 sub-hypotheses: H-M1 through H-M4)
- Verification type: Ablation studies for each causal link
- Critical: Determines explanatory power

**Phase 2B will decompose SH2 into 4 sub-hypotheses:**
- H-M1: Multi-scale encoding improves concept extraction (vs single-scale)
- H-M2: Concept alignment loss improves concept prediction (vs no alignment)
- H-M3: Residual pathway preserves accuracy (vs pure concept bottleneck)
- H-M4: Concept activations are clinically interpretable (vs random concepts)

**SH3 (Comparison):**
"Does T-CBM-MHR provide better interpretability than attention-based explanation methods while maintaining comparable accuracy?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical (head-to-head evaluation)
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-TCBM-v1
- [x] Confidence level specified: 0.84
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps, evidence table complete)
- [x] Causal chain length determined: N=4
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (P1 primary, P2/P3 secondary)
- [x] Falsification criteria defined (4 criteria)
- [x] Baselines identified for comparison (HITS, attention, SHAP)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:**
   - Compute: Single GPU training feasible? (Estimated: 1x A100, ~24hrs/experiment)
   - Clinician evaluation: How many clinicians needed? (Minimum 3 for κ calculation)

2. **Data Availability:**
   - MIMIC-IV access: PhysioNet credentialed access required
   - PTB-XL: Publicly available, can start immediately
   - Concept labels: Need to define or extract from guidelines

3. **Priority Verification Order:**
   - Recommended: SH1 (Existence) → H-M4 (Interpretability) → H-M3 (Performance) → H-M1/H-M2 (Ablations) → SH3 (Comparison)
   - Rationale: Validate core interpretability claim first before full mechanism analysis

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
