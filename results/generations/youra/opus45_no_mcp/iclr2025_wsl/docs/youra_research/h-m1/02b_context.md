# Phase 2B Context: H-M1

**Hypothesis ID:** H-M1
**Title:** Layer-wise Structure Advantage
**Type:** MECHANISM
**Gate:** MUST_WORK
**Prerequisites:** H-E1 (COMPLETED, PASS)

---

## Hypothesis Statement

Under Model Zoo benchmark, if we compare Layer-wise encoding vs Flatten+MLP, then Pearson correlation improves by Δr > 0.1, because per-layer statistics capture layer-specific functional patterns.

---

## Rationale

First causal chain step. Layer-wise processing preserves structural information that flat concatenation destroys. Validates basic structural awareness helps.

---

## Variables

- **Independent:** Embedding method (Flatten+MLP vs Layer-wise)
- **Dependent:** Pearson correlation with ground-truth accuracy
- **Controlled:** Dataset, train/test split, regressor architecture

---

## Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Model Zoos (CIFAR-10 Small) | 61,335 pretrained models with ground-truth accuracy labels, σ=15.62% |
| **Model** | Flatten+MLP vs Layer-wise encoder + MLP regressor | Each method produces embeddings for accuracy prediction |

**Dataset Details:**
- Source: Schurholt et al. 2022 (NeurIPS)
- DOI: 10.5281/zenodo.6620869
- File: dataset_cifar_small_hyp_fix.pt
- Splits: Train 42,650 / Val 9,340 / Test 9,345

---

## Verification Protocol

1. Implement Flatten+MLP baseline encoder
2. Implement Layer-wise encoder with mean aggregation
3. Train identical MLP regressors on embeddings
4. Compute Pearson r for both on test set (full standard split)
5. Run paired t-test across 5 random seeds

---

## Success Criteria

- **Primary:** Layer-wise r > Flatten+MLP r + 0.1 with p < 0.05
- **Secondary:** Consistent improvement across seeds

---

## Gate Condition

**Type:** MUST_WORK
**Condition:** Δr > 0.1 with p < 0.05
**Failure Response:** PIVOT to alternative layer aggregation strategies

---

## Dependencies

- **H-E1:** Model Zoo Dataset Validity
  - Status: COMPLETED
  - Result: PASS
  - Key Finding: σ(accuracy) = 15.62% > 10% threshold
  - N samples: 61,335 models verified

---

## Previous Hypothesis Results

### H-E1 Validation (Predecessor)

**Gate:** PASS
**Metrics:**
- σ(accuracy): 15.62% (threshold: 10%)
- N samples: 61,335
- Distribution: Multi-modal (Shapiro-Wilk p < 0.001)

**Proven Components:**
- Model Zoo data loading via Zenodo (DOI: 10.5281/zenodo.6620869)
- dataset_cifar_small_hyp_fix.pt format validated
- Train/Val/Test splits established

**Reusable Code:**
- `code/data.py` - Data loading from Zenodo with caching

---

## Source References

- Phase 2A: Causal Step 1, Prediction P1
- Phase 2B: 02b_verification_plan.md Section 2.2

---

*Generated for Phase 2C experiment design*
