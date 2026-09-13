# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-IRM-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under continual few-shot learning conditions, if the Immune Repertoire Memory (IRM) framework with clonal selection gates and checkpoint validation is applied, then certified robustness will be maintained across sequential task updates (≥90% retention after 10 updates) because the immunologically-inspired repertoire management preserves robustness certificates through affinity-based selection and two-stage validation.

**Alternative Hypothesis (H0):**
There is no relationship between IRM's immunologically-inspired mechanisms (clonal selection, checkpoint validation) and certified robustness retention during continual learning; any observed robustness maintenance is attributable to the base certification method alone or random chance.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| IRM Mechanism Parameters (τ, ε, K) | Independent | Affinity threshold τ (cosine similarity 0.5-0.9), degradation bound ε (0.01-0.1), pruning threshold K (3-10 updates) | τ ∈ [0.5, 0.9], ε ∈ [0.01, 0.1], K ∈ {3, 5, 10} |
| Certified Robustness Retention | Dependent | Ratio of certified radius after N updates to initial certified radius, measured via randomized smoothing | Target: ≥90% after 10 updates |
| Clean Accuracy | Dependent | Classification accuracy on clean test samples after continual updates | Baseline ±3% |
| Base Model Architecture | Controlled | Fixed embedding model (CLIP ViT-L/14 or DINO v2) | Fixed per experiment |
| Dataset Sequence | Controlled | Fixed task sequence order in continual learning benchmark | Continual-miniImageNet-R |
| Smoothing Noise Level (σ) | Controlled | Gaussian noise σ for randomized smoothing certification | σ ∈ {0.25, 0.5, 1.0} |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Memory Repertoire Bank (Certified Prototype Storage)
    ↓ [stores embedding + certificate]
Step 2: Clonal Selection Gate (Affinity-based Filtering)
    ↓ [filters by τ AND robustness constraint]
Step 3: Immune Checkpoint Validation (Two-stage Verification)
    ↓ [conservative bound + efficient re-certification]
Step 4: Consolidation with Apoptosis (Capacity-Managed Update)
    ↓ [prunes low-utility, organizes hierarchically]
→ Certified Robustness Maintained
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | FCert (Wang 2024) | First certified defense for few-shot classification with formal guarantees against data poisoning | Strong |
| Step2 → Step3 | Smoothed Embeddings (Pautov 2022) | Extends randomized smoothing to embedding spaces with L2 robustness certificates | Strong |
| Step3 → Step4 | Seferis (2024) | 100× sample efficiency for re-certification enables practical checkpoint validation | Medium |
| Step4 → Outcome | CH-HNN (Shi 2025) | Bio-inspired continual learning prevents catastrophic forgetting; validates cross-domain approach | Medium |

**Key Tension:**
- **Tension:** FCert provides certified robustness but assumes static models; CH-HNN enables continual learning but lacks formal robustness guarantees.
- **Resolution:** IRM bridges this gap by applying immunological repertoire management principles to maintain FCert-style certificates during CH-HNN-style continual updates. This verification plan tests whether the two-stage checkpoint validation successfully preserves certificates across updates.

### 1.4 Key Assumptions

1. **Prototype Certification Compatibility**
   - Assumption: Prototype-based few-shot learning can be extended with robustness certificates via randomized smoothing
   - Evidence: Smoothed Embeddings (Pautov 2022) demonstrates this for static few-shot models
   - **If Violated:** IRM cannot establish initial certificates; must find alternative certification method or restrict to uncertified prototypes

2. **Robustness Decomposability**
   - Assumption: Robustness properties are partially decomposable across class prototypes
   - Evidence: Randomized smoothing certificates are computed per-sample; ensemble methods (EsbRS) compose certificates
   - **If Violated:** Cannot track per-prototype certificates; must use global model-level certification only

3. **Re-certification Efficiency**
   - Assumption: Efficient re-certification (Seferis 2024 method) applies to prototype embedding updates
   - Evidence: Seferis achieves ~20% radius reduction for 100× faster certification
   - **If Violated:** Checkpoint validation becomes computationally infeasible; must use conservative bound propagation only (potentially unbounded degradation)

### 1.5 Scope & Boundaries

**Applies To:**
- Prototype-based few-shot learning with embedding models (CLIP, DINO v2, ResNet)
- Continual learning scenarios with sequential task arrival
- L2-bounded adversarial perturbations
- Class counts up to 500 (with hierarchical scaling)

**Does NOT Apply To:**
- End-to-end fine-tuning approaches
- Non-prototype few-shot methods (gradient-based meta-learning)
- Non-L2 threat models (L∞, semantic perturbations)
- Real-time requirements (<10ms inference)

**Known Limitations:**
- ~10× overhead for periodic re-certification (every K updates)
- Hierarchical scaling introduces clustering approximations for >100 classes
- Requires access to support samples for certificate computation

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Certified Robustness Retention vs Baseline):**
IRM will maintain ≥90% of initial certified radius after 10 continual task updates, while naive continual few-shot learning (no IRM) will degrade to ≤50% certified radius.

*Measurement*:
- Certified Radius Retention Ratio (CRRR) = R_N / R_0 where R is certified radius
- Target: CRRR ≥ 0.90 after N=10 updates with p < 0.05
- Statistical test: Paired t-test vs naive baseline, n ≥ 25 runs

*Basis*:
FCert achieves ~0.7 certified accuracy on static miniImageNet. IRM checkpoint validation bounds degradation to ε per update, so after 10 updates: max degradation = 10ε ≈ 10% for ε=0.01.

*Success Criteria for Phase 2B*:
- Primary: CRRR ≥ 0.90 (p < 0.05)
- Falsification: CRRR ≤ 0.70 triggers rejection

**Secondary Predictions:**

**P2 (Mechanism Validation - Checkpoint Effectiveness):**
Two-stage checkpoint validation will catch ≥95% of robustness-degrading prototype updates in stage 1 (conservative bound propagation), requiring full re-certification for ≤5% of updates.

**P3 (Clean Accuracy Preservation):**
IRM will maintain clean accuracy within ±3% of static FCert baseline while providing continual learning capability.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: CRRR ≤ 0.70 after 10 updates
   (= significantly worse than 10ε bound, checkpoint validation ineffective)

2. **Mechanism Failure**: Checkpoint stage 1 catches <80% of degrading updates
   (= two-stage validation provides no benefit over full re-certification)

3. **Accuracy Collapse**: Clean accuracy drops >10% relative to static baseline
   (= IRM imposes unacceptable accuracy penalty)

### 1.7 SOTA Baseline (Optional)

**Mode:** Absolute Performance Validation (No direct SOTA comparison available)

| Method | Certified Robustness | Continual Learning | Limitation |
|--------|---------------------|-------------------|------------|
| FCert (Wang 2024) | ✅ | ❌ | Static model only |
| CH-HNN (Shi 2025) | ❌ | ✅ | No robustness guarantees |
| AFSL (Agrawal 2025) | ❌ (empirical) | ❌ | Not certified |
| Naive Continual | ❌ | ✅ | Unbounded degradation |

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): Target d ≥ 0.8 (large effect)
- Required runs: n ≥ 25 per condition
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds)
- Significance level: α = 0.05 (one-tailed)
- Report format: Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does certified robustness retention (CRRR ≥ 0.90) exist under IRM management during continual few-shot learning?"
- Maps to: Primary prediction P1
- Verification type: Empirical measurement
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the four-component IRM mechanism (repertoire bank, clonal selection, checkpoint validation, apoptosis pruning) the actual cause of robustness retention?"
- Maps to: Causal mechanism (4 steps)
- Verification type: Ablation studies
- **Note:** Phase 2B will decompose into 4 sub-hypotheses (H-M1 through H-M4)

**SH3 (Comparison):**
"Does IRM outperform naive continual FSL and match static FCert accuracy?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical

**Total Sub-Hypotheses for Phase 2B:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-IRM-v1
- [x] Confidence level: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized with evidence
- [x] Causal mechanism with 4 steps and evidence table
- [x] Key tension and resolution identified
- [x] Assumptions with violation consequences
- [x] 3 testable predictions (P1 primary)
- [x] Falsification criteria with thresholds
- [x] Baselines identified
- [x] SH1, SH2, SH3 starting points clear

### Open Questions

1. **Resource Requirements:** Compute budget for randomized smoothing across 500+ prototypes? (~10-100 GPU-hours)
2. **Data Availability:** Continual-miniImageNet-R benchmark construction needed?
3. **Priority Order:** SH1 first, or parallel SH2 ablations?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
