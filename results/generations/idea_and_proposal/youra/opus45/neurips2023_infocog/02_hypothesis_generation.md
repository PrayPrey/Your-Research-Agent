# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CBN-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of high-dimensional (>1000D), non-stationary, bi-modal cognitive data with limited samples (100-5000), if temporal-aware encoders and bridge matching are applied, then MI estimation error will be reduced to ≤10% (vs >30% for baseline methods) because the encoders preserve temporal causality while bridge matching enables efficient transport between marginal and joint distributions in a lower-dimensional latent space.

**Alternative Hypothesis (H0):**
Temporal-aware encoders and bridge matching do not significantly improve MI estimation accuracy compared to direct neural estimation methods (MINE, CLUB, MIGE) on high-dimensional, non-stationary cognitive data. Any observed improvements are due to chance or confounding factors rather than the proposed mechanism.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Data dimensionality | Independent | Number of features in neural/behavioral recordings | 100D - 2000D |
| Sample size | Independent | Number of time points or trials available | 100 - 5000 |
| Non-stationarity level | Independent | Drift rate in data distribution (sliding window variance) | Low/Medium/High |
| MI estimation error | Dependent | \|Estimated MI - True MI\| / True MI × 100% | Target: ≤10% |
| Computational cost | Dependent | GPU hours for training + inference time | <10 GPU-hours |
| Sample efficiency | Dependent | Minimum samples for <15% error | Target: 500 samples |
| Encoder architecture | Controlled | Fixed GRU/Transformer configuration | Fixed per experiment |
| Bridge architecture | Controlled | Fixed MLP configuration | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Raw Bi-Modal Data → Temporal-Aware Encoders → Latent Trajectories
Step 2: Latent Trajectories → Bridge Matching Network → Transported Representations
Step 3: Transported Representations → MI Estimator → Estimated Mutual Information
Step 4: Estimated MI → Thermodynamic Validation → Validated MI Estimates
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Latent MI (NeurIPS 2024) | MI approximation works if data admits low-dimensional representations | Strong |
| Step 2 → Step 3 | InfoBridge (2025) | Bridge matching provides unbiased MI estimation via domain transfer | Strong |
| Step 3 → Step 4 | Normalizing Flows MI (2024) | Transformation-based MI achieves <20% error on high-D benchmarks | Strong |
| Step 4 → Outcome | Karbowski (2023) | Thermodynamic bounds can validate information-theoretic estimates | Medium |

**Key Tension:**
InfoBridge (2025) demonstrates bridge matching for unimodal distributions, while our hypothesis extends to bi-modal cognitive data. Resolution: Derive new theoretical bounds for bi-modal case (core contribution).

### 1.4 Key Assumptions

1. **Temporal Structure:** Cognitive data exhibits temporal structure capturable by recurrent/attention architectures
   - *Consequence if violated:* Encoders learn noise; estimation error increases

2. **Temporal Alignment:** Bi-modal data can be temporally aligned at millisecond resolution
   - *Consequence if violated:* MI estimates biased by misalignment

3. **Bridge Extension:** Bridge matching extends to bi-modal with similar guarantees
   - *Consequence if violated:* Bi-modal bridge does not preserve MI

4. **Thermodynamic Applicability:** Fisher information bounds apply to cognitive distributions
   - *Consequence if violated:* Validation fails to detect errors

5. **Self-Supervised Learning:** Pre-training provides useful representations
   - *Consequence if violated:* Increased labeled data requirements

### 1.5 Scope & Boundaries

**Applies to:** High-dimensional (>100D) cognitive time series, bi-modal (neural+behavioral), non-stationary, limited samples (100-5000)

**Does NOT apply to:** Static data, >2 modalities, <50 samples, unaligned modalities

**Limitations:** Bi-modal only, requires temporal alignment, ~2-3x MINE training time

### 1.6 Testable Predictions

**P1 (Primary - MI Error vs SOTA ~25% ± 8%):**
CBN achieves MI estimation error ≤10% on 1000D+ bi-modal cognitive data.
- *Success:* Error ≤ 10% (p < 0.05)
- *Falsification:* Error > 20%

**P2 (Sample Efficiency):**
CBN achieves ≤15% error with 500 samples (MINE/CLUB require >2000).

**P3 (Non-Stationarity Robustness):**
Under strong drift, CBN degrades ≤5% (MINE/CLUB >20%).

**P4 (Thermodynamic Validation):**
≥90% CBN estimates satisfy bounds (vs <70% for MINE/CLUB).

**Falsification Criteria:**
1. Error > 20% (worse than SOTA)
2. Ablation shows temporal encoder provides no improvement
3. No advantage on ANY dimension
4. Bi-modal bridge provably does not preserve MI

### 1.7 SOTA Baseline

| Method | Error (%) | Year |
|--------|-----------|------|
| MINE | 32.5 ± 8.2 | 2018 |
| CLUB | 28.3 ± 7.5 | 2020 |
| MIGE | 24.1 ± 6.8 | 2020 |
| NF-MI | 18.5 ± 5.2 | 2024 |
| InfoBridge | 12.3 ± 4.1 | 2025 |

**SOTA Mean:** 23.1% | **Target:** ≤10% | **Falsification:** >20%

### 1.8 Statistical Verification Design

- **Effect size:** d = 1.875 (large)
- **Required runs:** n ≥ 25
- **Test:** Paired t-test, α = 0.05 (one-tailed)
- **Report:** Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does CBN achieve lower MI estimation error than baselines on high-dimensional bi-modal data?"
- Maps to: P1
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the 4-step mechanism the actual cause of improved MI estimation?"
- Decomposes to 4 sub-hypotheses (H-M1 to H-M4)
- Tests each causal link

**SH3 (Comparison):**
"Does CBN outperform across multiple dimensions (error, efficiency, robustness, validation)?"
- Maps to: P2, P3, P4

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-CBN-v1
- [x] Confidence: 0.82
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism with N=4 steps and evidence
- [x] Key tension identified with resolution
- [x] Assumptions with consequences
- [x] 4 testable predictions (P1 primary)
- [x] Falsification criteria defined
- [x] Baselines identified
- [x] SH1, SH2, SH3 ready

### Open Questions

1. **Data:** Which public datasets provide bi-modal cognitive recordings?
2. **Resources:** GPU requirements (~50-100 hours estimated)
3. **Priority:** Theory-first or parallel empirical work?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
