# Product Requirements Document: H-M3

**Hypothesis:** Attribution approximation methods make different assumptions about curvature (EK-FAC: Kronecker, TracIn: gradient-only, TRAK: random projection)

**Date:** 2026-08-18
**Author:** Anonymous
**Type:** MECHANISM (INCREMENTAL from H-M2)
**Gate:** SHOULD_WORK

---

## 1. Executive Summary

This experiment validates that different attribution approximation methods (EK-FAC, TracIn, TRAK) exhibit architecture-dependent performance due to their underlying mathematical assumptions about curvature structure. Building on H-M2's confirmation of Hessian curvature divergence (90.93% difference), we test whether:
- EK-FAC performs better on GPT-2 (Kronecker assumption fits causal structure)
- TracIn performs better on BERT (benefits from dense bidirectional gradients)
- TRAK shows architecture invariance (random projection theory)

**Success Criterion:** >10% relative difference in mislabeled detection AUC across architectures for at least one method.

---

## 2. Problem Statement

H-M2 established that BERT and GPT-2 exhibit fundamentally different Hessian curvature patterns (GPT-2 has 11x higher top eigenvalue). This curvature difference should affect how well each attribution method's mathematical assumptions hold:

1. **EK-FAC** assumes Kronecker-factored curvature (G ≈ A ⊗ B). Causal attention's block structure may better satisfy this assumption.
2. **TracIn** uses first-order gradient dot products only. Dense bidirectional gradients in BERT may provide stronger signal.
3. **TRAK** uses random Johnson-Lindenstrauss projections. Theory predicts architecture invariance.

**Key Question:** Do approximation assumptions create measurable performance differences across architectures?

---

## 3. Functional Requirements

### FR-1: Model Fine-tuning Pipeline
- Fine-tune BERT-base-uncased on SST-2 with 5% mislabeled training data
- Fine-tune GPT-2 on SST-2 with identical mislabeled indices
- Save checkpoints at epochs 1, 2, 3 for TracIn
- Record mislabeled indices as ground truth

### FR-2: EK-FAC Attribution (kronfluence)
- Integrate kronfluence library for EK-FAC influence computation
- Fit Kronecker factors on both BERT and GPT-2
- Compute pairwise influence scores for validation queries
- Measure mislabeled detection AUC

### FR-3: TracIn Attribution (simple-influence / captum)
- Implement TracIn using gradient checkpoints
- Compute gradient dot-products across checkpoints
- Aggregate scores with learning rate weighting
- Measure mislabeled detection AUC

### FR-4: TRAK Attribution (traker)
- Integrate traker library for TRAK computation
- Use default projection dimension (2048)
- Compute scores with multiple random seeds (0-4)
- Measure cross-seed rank correlation and AUC

### FR-5: Comparative Analysis
- Compare mislabeled detection AUC across methods × architectures (6 combinations)
- Compute relative AUC differences per method
- Generate gate metrics comparison figure

### FR-6: Ablation Studies
- **Ablation A1:** Projection dimension sensitivity (TRAK: 1024, 2048, 4096)
- **Ablation A2:** Number of checkpoints (TracIn: 1, 2, 3 epochs)
- **Ablation A3:** EK-FAC strategy comparison (identity, diagonal, kfac, ekfac)

---

## 4. Data Specification

### Primary Dataset: SST-2

| Split | Samples | Usage |
|-------|---------|-------|
| Train | 67,349 | Attribution source |
| Validation | 872 | Query examples |
| Mislabeled | ~3,367 (5%) | Detection target |

**Source:** HuggingFace datasets (glue/sst2)
**Preprocessing:**
- Tokenization: Model-specific (bert-base-uncased, gpt2)
- Max sequence length: 128 tokens
- Padding: Right-side to max_length

### Mislabeled Injection Protocol
- Random selection of 5% training indices
- Flip binary labels (0→1, 1→0)
- Store indices in `mislabeled_indices.json`

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds for all experiments
- Checkpoint versioning with timestamps
- Full configuration logging

### NFR-2: Scalability
- Full SST-2 training set (67,349 samples)
- Full validation set (872 queries)
- No arbitrary sample limits

### NFR-3: Library Compatibility
- kronfluence >= 0.1.0
- traker[fast] >= 0.3.0
- captum >= 0.6.0
- simple-influence (latest)

---

## 6. Success Criteria

### Gate Metrics (SHOULD_WORK)

| Metric | Expected Outcome |
|--------|------------------|
| EK-FAC AUC (GPT-2 vs BERT) | GPT-2 > BERT (Kronecker fits causal) |
| TracIn AUC (BERT vs GPT-2) | BERT ≥ GPT-2 (denser gradients) |
| TRAK AUC difference | |diff| < 5% (architecture invariant) |
| Any method shows >10% diff | **GATE PASS** |

### Validation Metrics

| Metric | Target |
|--------|--------|
| Mislabeled detection AUC | Report per method/arch |
| Cross-seed correlation (TRAK) | > 0.9 |
| Checkpoint count (TracIn) | 3 |

---

## 7. Dependencies

### 7.1 Python Packages (requirements.txt)

```
torch>=2.0.0
transformers>=4.30.0
datasets>=2.0.0
kronfluence>=0.1.0
traker[fast]>=0.3.0
captum>=0.6.0
scikit-learn>=1.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
```

### 7.2 External Repositories (Reference)

| Repository | Purpose |
|------------|---------|
| github.com/pomonam/kronfluence | EK-FAC implementation |
| github.com/MadryLab/trak | TRAK implementation |
| github.com/pomonam/simple-influence | Unified influence interface |

### 7.3 Base Hypothesis Code (H-M2)

- Import Hessian analysis utilities if needed
- Reuse model loading/tokenization from h-m2/code/

---

## 8. Out of Scope

- Custom CUDA kernel optimization
- Multi-GPU distributed training
- Real-time attribution serving
- Non-classification tasks

---

## Appendix: Phase 2C Reference

Source: `h-m3/02c_experiment_brief.md`
Prerequisite: H-M2 (Hessian Curvature Divergence - PASSED with 90.93% diff)
