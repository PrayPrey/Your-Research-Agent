# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-EITSD-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under the condition of multimodal models with separable modality inputs, if we apply Efficient Information-Theoretic Shapley Decomposition (E-ITSD) combining permutation-sampled Shapley values with I_broja Partial Information Decomposition and learned null embeddings for ablation, then we can produce interpretable metrics quantifying each modality's unique contribution, shared redundancy, and emergent synergy, because Shapley values provide axiomatic fair attribution (efficiency, symmetry, null player properties) while PID decomposes the information-theoretic structure of contributions.

**Alternative Hypothesis (H0):**
Modality contributions in multimodal representations cannot be meaningfully decomposed into unique, redundant, and synergistic components using E-ITSD, OR the decomposition provides no additional interpretability beyond existing methods (attention weights, gradient-based attribution, standard Shapley without PID).

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Ablation Strategy | Independent | Method for modality removal: (a) Zero ablation, (b) Mean embedding, (c) Learned null token | Categorical: 3 levels |
| Unique Contribution Score | Dependent | Information uniquely provided by modality i, computed via I_broja PID on Shapley marginals | [0.0, 1.0] normalized |
| Redundancy Score | Dependent | Shared/overlapping information across modalities, computed via I_broja | [0.0, 1.0] normalized |
| Synergy Score | Dependent | Emergent information from modality combination, computed via I_broja | [0.0, 1.0] normalized |
| Number of Modalities | Controlled | Fixed count of input modalities per experiment | 2-5 modalities |
| Model Architecture | Controlled | Fixed multimodal fusion architecture | Cross-attention or late fusion |
| Dataset | Controlled | MultiBench benchmark datasets | CMU-MOSEI, AV-MNIST, etc. |
| Permutation Sample Count | Controlled | Number of samples for Shapley approximation | 500 (default) |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Learned Null Ablation
    ↓ (enables valid counterfactuals)
Step 2: Permutation-based Shapley Computation
    ↓ (provides fair attribution values)
Step 3: PID Decomposition via I_broja
    ↓ (separates contribution types)
Outcome: Interpretable Unique/Redundant/Synergy Scores
```

**Step 1 → Step 2:** Learned null embeddings create valid counterfactual representations by maintaining in-distribution model behavior during ablation. This enables meaningful Shapley marginal computations without distribution shift artifacts.

**Step 2 → Step 3:** Permutation sampling approximates exact Shapley values with bounded variance. These values quantify WHO contributes HOW MUCH, providing the input for information-theoretic decomposition.

**Step 3 → Outcome:** I_broja PID measure decomposes the Shapley-attributed contributions into unique, redundant, and synergistic components, answering HOW each modality contributes (uniquely vs. shared vs. emergently).

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | MM-SHAP (Morais & Fuentes, 2025) | Successfully applied Shapley ablation to Audio LLMs; null strategies validated | Strong |
| Step 2 → Step 3 | SHAPE (Hu et al., 2022) | Shapley-based perceptual scores measure modality contribution and cooperation | Strong |
| Step 3 → Outcome | MultiSHAP (Wang & Wang, 2025) | Shapley Interaction Index captures cross-modal synergistic and suppressive effects | Strong |
| Overall | Verdinelli & Wasserman (2023) | Shapley axioms valid but correlation requires extension (supports PID addition) | Medium |

**Key Tension:**
- **Tension:** Verdinelli & Wasserman (2023) note that Shapley values do not eliminate feature correlation effects, potentially obscuring interpretability. However, MM-SHAP (2025) and MultiSHAP (2025) successfully apply Shapley to multimodal settings.
- **Resolution:** E-ITSD addresses this by adding PID decomposition layer, which explicitly separates shared (redundant) information from unique contributions, thus handling the correlation concern at the information-theoretic level.

### 1.4 Key Assumptions

1. **Decomposability Assumption:** Modality contributions can be meaningfully decomposed into unique, redundant, and synergistic components.
   - Evidence: SHAPE (2022) demonstrates this decomposition is informative for understanding fusion behavior
   - Consequence if violated: E-ITSD scores would be uninterpretable or inconsistent across experiments

2. **Sampling Convergence Assumption:** Shapley permutation sampling converges with 500 samples to stable attribution values (variance < 5% of mean).
   - Evidence: KernelSHAP literature establishes convergence bounds; MM-SHAP used similar sample counts
   - Consequence if violated: Results would be non-reproducible; would need to increase sample count

3. **Null Embedding Validity Assumption:** Learned null embeddings approximate true modality absence without distribution shift.
   - Evidence: MM-SHAP (2025) validated this approach for Audio LLMs
   - Consequence if violated: Shapley marginals would reflect distribution artifacts rather than modality contribution

4. **PID Measure Consistency Assumption:** I_broja measure provides consistent PID decomposition across different multimodal settings.
   - Evidence: I_broja is the most commonly used bivariate PID measure in neuroscience
   - Consequence if violated: Results would be sensitive to PID measure choice; would need to test multiple measures

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Multimodal models with separable modality inputs (separate encoders per modality)
- Models with 2-5 modalities (vision, language, audio, etc.)
- Any fusion strategy (early, late, cross-attention) where modality-specific representations are accessible
- Post-hoc analysis (model already trained)

**Where Hypothesis Does NOT Apply:**
- Models with pre-fused modality inputs (e.g., RGB-D images treated as single input)
- Single-modality models
- Models where modality boundaries are unclear (e.g., multimodal tokens in unified embedding space)
- Real-time inference scenarios (computational overhead of Shapley sampling)

**Known Limitations:**
- Computational cost: O(M! / sampling) where M = number of modalities
- PID measure choice (I_broja) may not be optimal for all domains
- Interpretation requires domain expertise to understand unique/redundant/synergy semantics
- Cannot explain internal attention patterns (complementary to attention-based methods)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Attribution Decomposition Validity):**
E-ITSD produces a valid decomposition where Unique + Redundancy + Synergy = Total Contribution for each modality, with coefficient of variation < 10% across 20 repeated runs.

*Measurement*:
- Decomposition sum error < 5% of total
- CV of scores across runs < 10%
- Statistical test: Paired comparison with bootstrap CI

*Basis*:
Domain standard for attribution method validity (SHAP, Integrated Gradients literature)

*Success Criteria for Phase 2B*:
- Primary: Decomposition validates mathematically (sum constraint holds)
- Falsification: Scores do not sum to total OR high variance (CV > 20%)

**Secondary Predictions:**

**P2 (Interpretability Correlation):**
E-ITSD synergy scores correlate (Spearman ρ > 0.5) with cross-modal attention weights on datasets where cross-modal reasoning is essential (VQA, multimodal sentiment).

*Measurement*: Spearman correlation, p < 0.05, n ≥ 100 samples
*Basis*: If synergy captures emergent cross-modal effects, it should correlate with model's attention to cross-modal interactions

**P3 (Diagnostic Utility):**
E-ITSD can identify modality dominance: when one modality's Unique score > 0.7 × Total, the model exhibits modality collapse (verified by single-modality ablation performance drop < 10%).

*Measurement*: Threshold-based classification, validated against ablation ground truth
*Basis*: MLA (2023) documented modality dominance problem; E-ITSD should detect it

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Decomposition Failure**: Unique + Redundancy + Synergy ≠ Total (error > 10%)
2. **Convergence Failure**: Shapley values do not stabilize within 500 samples (CV > 25%)
3. **Null Baseline Failure**: Learned null embeddings produce Shapley values statistically indistinguishable from random ablation
4. **Interpretability Failure**: E-ITSD scores show no correlation with any behavioral measure

### 1.7 SOTA Baseline (Optional)

*Not applicable - This hypothesis targets interpretability metrics, not performance improvement over SOTA.*

**Comparison Methods:** MM-SHAP, Attention-based attribution, Gradient-based attribution, SHAPE scores

### 1.8 Statistical Verification Design

**Sample Size**: n ≥ 20 runs with different random seeds
**Statistical Tests**:
- One-sample t-test for decomposition validity
- Spearman correlation for interpretability
- Coefficient of Variation analysis for convergence
**Significance Level**: α = 0.05
**Report Format**: Mean ± Std Dev, 95% CI via bootstrap, Effect sizes

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does E-ITSD produce a mathematically valid decomposition where Unique + Redundancy + Synergy = Total Contribution for each modality?"
- Maps to: Primary prediction P1
- Verification type: Empirical (mathematical validation)
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Does the E-ITSD causal mechanism operate as proposed through learned null ablation → Shapley computation → PID decomposition?"
- Maps to: Causal mechanism (N=3 steps, will decompose into H-M1, H-M2, H-M3)
  - H-M1: Learned null embeddings produce valid counterfactuals
  - H-M2: Permutation sampling converges to stable Shapley values
  - H-M3: I_broja PID produces interpretable decomposition
- Verification type: Causal analysis
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does E-ITSD provide interpretability advantages over existing methods (MM-SHAP, attention, gradients)?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 2 + 3 = 5 (SH1, H-M1, H-M2, H-M3, SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-EITSD-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated (4 assumptions)
- [x] At least 2 testable predictions exist (3 predictions, P1 primary)
- [x] Falsification criteria are defined (4 criteria)
- [x] Baselines are identified for comparison
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** What computational resources are needed for 500-sample Shapley computation on MultiBench datasets? Estimate GPU hours per dataset.

2. **PID Implementation:** Which PID implementation library should be used? (Options: dit, pypid, custom implementation) Need to verify I_broja availability.

3. **Priority Verification Order:** Should we verify SH1 (mathematical validity) first, or H-M1 (null embedding validity) first? Recommendation: SH1 first as it's the foundation.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
