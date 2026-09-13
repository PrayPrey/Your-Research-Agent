# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CRP-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under controlled training conditions with intermediate checkpoints available, if lightweight linear probes are trained on circuit-specific activation patterns (attention head coherence for ICL, MLP activation geometry for arithmetic, key-value patterns for factual recall), then capability emergence can be predicted earlier than loss-threshold methods (Du et al. 2024) by directly monitoring the maturation of known capability-relevant circuits during training, because specific computational circuits responsible for capabilities mature at trackable rates before behavioral manifestation on benchmarks.

**Alternative Hypothesis (H0):**
Circuit-specific activation patterns do not contain sufficient information to predict capability emergence earlier than aggregate loss-based methods, either because (a) circuit maturation does not temporally precede benchmark performance improvement, or (b) the relationship between activation patterns and capabilities is too complex for linear probes to capture.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Circuit-specific activation patterns | Independent | Extract attention head patterns (induction head coherence scores) and MLP activations from capability-relevant layers using TransformerLens; focus on heads identified by prior mechanistic work | Continuous activation vectors; coherence scores 0-1 |
| Prediction lead time | Dependent | Training steps between probe prediction threshold (confidence > 0.8) and benchmark performance emergence (>random baseline + 2σ) | 0 to ~50% of training duration |
| Probe prediction accuracy | Dependent | AUC of probe classifier on held-out checkpoints | 0.5 (random) to 1.0 (perfect) |
| Model architecture | Controlled | GPT-style decoder-only transformer (Pythia 125M-7B, OLMo 1B-7B) | Fixed per experiment |
| Training data | Controlled | Standard pre-training corpus (The Pile for Pythia, Dolma for OLMo) | Fixed per model family |
| Target capability | Controlled | ICL, basic arithmetic, factual recall | 3 capabilities tested |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Training Progression → Circuit-specific activation pattern changes
    ↓
Step 2: Activation pattern maturation → Probe classification confidence increase
    ↓
Step 3: Probe threshold crossing → Capability emergence prediction
    ↓
Outcome: Earlier prediction than loss-threshold methods
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Olsson et al. 2022 | Induction heads develop at precisely the same point as ICL bump; causal relationship established | Strong |
| Step 1 → Step 2 | Hong & Hong 2025 | Vocabulary-based metrics reveal transitions invisible in loss curves | Strong |
| Step 2 → Step 3 | Belrose et al. 2023 (Tuned Lens) | Affine probes successfully decode hidden states into predictions layer-by-layer | Medium |
| Step 2 → Step 3 | Huang et al. 2024 | Circuit competition framework predicts four training dynamics regimes | Medium |
| Step 3 → Outcome | Du et al. 2024 | Loss thresholds correlate with emergence but cannot explain mechanism | Medium (baseline) |

**Key Tension:**
- **Tension:** Olsson et al. (2022) demonstrated clear circuit-capability correspondence for ICL, but it remains unclear whether this pattern generalizes to other capabilities (arithmetic, factual recall) which lack comparable mechanistic analysis.
- **Resolution:** This verification plan will test probes on multiple capabilities (ICL, arithmetic, recall) to determine generalization scope. ICL serves as positive control; other capabilities test generalization.

### 1.4 Key Assumptions

1. **Emergent capabilities correspond to identifiable computational circuits**
   - Evidence: Olsson 2022 established ICL ↔ induction heads
   - *Consequence if violated:* Probe targets would be undefined; methodology would require alternative feature extraction

2. **Circuit maturation temporally precedes behavioral manifestation**
   - Evidence: Hong 2025 showed vocabulary metrics detect transitions before loss
   - *Consequence if violated:* No prediction lead time would be achievable

3. **Linear probes have sufficient capacity to detect readiness signatures**
   - Evidence: Tuned Lens (Belrose 2023) uses affine probes successfully
   - *Consequence if violated:* Nonlinear probes would be required, increasing overfitting risk

4. **Public checkpoints provide sufficient temporal resolution**
   - Evidence: Pythia has 143 checkpoints; OLMo provides intermediate saves
   - *Consequence if violated:* Custom training runs would be required

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Transformer-based autoregressive language models (GPT architecture)
- Models with publicly available intermediate training checkpoints
- Well-characterized capabilities with known or discoverable circuit associations
- Model sizes from 125M to 7B parameters

**Where Hypothesis Does NOT Apply:**
- Encoder-only or encoder-decoder architectures without modification
- Capabilities without identifiable circuit associations
- Closed-source models without checkpoint access
- Real-time training prediction (requires periodic checkpoint evaluation)

**Known Limitations:**
- Requires prior mechanistic interpretability work to identify target circuits
- Prediction granularity limited by checkpoint frequency
- May not generalize to capabilities arising from distributed representations

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Prediction Lead Time)**:
Capability Readiness Probes will predict capability emergence with measurable lead time compared to loss-threshold methods.

*Measurement*:
- Lead time = (checkpoint at loss-threshold detection) - (checkpoint at probe threshold crossing)
- Success: Lead time > 0 with p < 0.05 (paired comparison across capabilities)
- Statistical test: Wilcoxon signed-rank test, n ≥ 15 capability × model combinations

*Success Criteria for Phase 2B*:
- Primary: Mean lead time > 5% of total training duration with p < 0.05
- Falsification: Lead time ≤ 0 in majority of cases (probes no better than loss)

**Secondary Predictions:**

**P2 (Probe Classification Accuracy)**:
Probes trained on circuit-specific activations will achieve AUC > 0.8 on held-out checkpoints for distinguishing pre-emergence from post-emergence states.

**P3 (Cross-Model Transfer)**:
Probes trained on Pythia models will transfer to OLMo models with AUC > 0.7 after minimal fine-tuning (≤10% of training data).

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure**: Lead time ≤ 0 in >50% of capability × model combinations
2. **Mechanism Failure**: Probe AUC ≤ 0.65 on held-out checkpoints
3. **Generalization Failure**: Probes work only for ICL but fail for arithmetic and recall

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): Estimated 0.6-0.8
- Required comparisons: n ≥ 15 (3 capabilities × 5+ model sizes)
- Statistical power: 0.8

**Test Specification:**
- Primary comparison: Wilcoxon signed-rank test (paired, non-parametric)
- Classification performance: AUC with 5-fold cross-validation
- Significance level: α = 0.05

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Can linear probes trained on circuit-specific activation patterns distinguish pre-emergence from post-emergence model states with AUC > 0.8?"
- Maps to: Primary prediction (P1, P2)
- Verification type: Empirical classification
- Critical: MUST PASS for hypothesis to be viable

**SH2 (Mechanism):**
"Does probe confidence increase monotonically as circuits mature during training, reflecting the underlying causal mechanism?"
- Maps to: Causal mechanism (3 steps)
- Phase 2B will decompose into 3 sub-hypotheses:
  - H-M1: Training progression causes detectable activation pattern changes
  - H-M2: Activation maturation causes probe confidence increase
  - H-M3: Probe threshold crossing precedes benchmark emergence
- Verification type: Causal/correlational analysis
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Do Capability Readiness Probes predict emergence earlier than loss-threshold methods (Du et al. 2024)?"
- Maps to: Secondary predictions (comparison)
- Verification type: Comparative empirical
- Critical: Determines practical value over existing methods

**Total sub-hypotheses in Phase 2B:** 5 (SH1 + 3 mechanism sub-hypotheses + SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-CRP-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (3 steps, evidence_for_links table)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (P1 primary, P2, P3)
- [x] Falsification criteria are defined (3 failure modes)
- [x] Baselines identified for comparison (Du et al. 2024)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** What is the computational cost of extracting circuit-specific activations from all Pythia/OLMo checkpoints?

2. **Circuit Identification for Non-ICL Capabilities:** Which specific circuits should be targeted for arithmetic and factual recall?

3. **Probe Calibration:** How should the prediction threshold be calibrated?

4. **Priority Verification Order:** Recommend starting with ICL (best-understood circuits) as positive control.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
