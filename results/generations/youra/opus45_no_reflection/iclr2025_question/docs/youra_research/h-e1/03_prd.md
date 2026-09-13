# Product Requirements Document: H-E1

**Hypothesis:** Middle-layer hidden states encode sufficient signal for correctness prediction with AUROC > 0.60
**Type:** EXISTENCE (Proof-of-Concept)
**Date:** 2026-08-18
**Author:** Anonymous

---

## Executive Summary

Validate whether middle-layer hidden states from Llama-3-8B-Instruct contain predictive signal for factual correctness. Train linear probe on layer 19 hidden states, evaluate AUROC against random baseline. Gate condition: AUROC > 0.60.

---

## Problem Statement

LLMs generate factually incorrect responses without indicating uncertainty. Output-level signals (token entropy, sequence probability) may miss internal correctness representations. This experiment tests whether hidden states encode correctness signal exploitable by simple linear probe.

---

## Functional Requirements

### FR-1: Dataset Preparation
- **FR-1.1**: Load TriviaQA (rc config) from HuggingFace datasets
- **FR-1.2**: Sample 95,000 training examples, 17,000 validation examples
- **FR-1.3**: Format as QA prompts for Llama-3-8B-Instruct
- **FR-1.4**: Generate answers with greedy decoding
- **FR-1.5**: Label correctness via exact match with ground truth aliases

### FR-2: Hidden State Extraction
- **FR-2.1**: Load Llama-3-8B-Instruct with bfloat16 precision
- **FR-2.2**: Register forward hook on layer 19 (60% depth)
- **FR-2.3**: Extract last-token hidden state (shape: [batch, 4096])
- **FR-2.4**: Store hidden states with correctness labels

### FR-3: Linear Probe Training
- **FR-3.1**: Implement LinearProbe(4096 → 1) with sigmoid output
- **FR-3.2**: Train with Adam optimizer (lr=1e-3)
- **FR-3.3**: Use Binary Cross-Entropy loss
- **FR-3.4**: Train for 10 epochs with batch size 256

### FR-4: Evaluation
- **FR-4.1**: Compute AUROC on validation set
- **FR-4.2**: Generate ROC curve (FPR vs TPR)
- **FR-4.3**: Plot training loss curve
- **FR-4.4**: Compute random baseline (0.50 expected)

### FR-5: Visualization
- **FR-5.1**: Gate metrics bar chart (Probe AUROC vs 0.50 baseline)
- **FR-5.2**: ROC curve with AUROC annotation
- **FR-5.3**: Training loss vs epoch plot
- **FR-5.4**: Save all figures to `figures/` subdirectory

---

## Non-Functional Requirements

### NFR-1: Performance
- Inference: Process full validation set in <4 hours on single A100
- Training: Linear probe converges in <5 minutes

### NFR-2: Reproducibility
- Fixed random seed (42)
- Deterministic operations where possible
- Log all hyperparameters

### NFR-3: Resource Constraints
- GPU memory: <40GB (single A100)
- Disk: <50GB for cached hidden states

---

## Success Criteria

| Metric | Target | Justification |
|--------|--------|---------------|
| **Primary: AUROC** | > 0.60 | MUST_WORK gate condition |
| **Secondary: Random Baseline** | 0.50 | Sanity check |
| **Code Execution** | No errors | PoC completeness |

---

## Gate Decision Logic

```
IF probe_auroc > 0.60:
    PASS → Proceed to H-M1 (hidden state extraction mechanism)
ELSE:
    FAIL → ABANDON research direction (hidden states lack signal)
```

---

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| transformers | >=4.40.0 | Model loading |
| datasets | >=2.18.0 | TriviaQA loading |
| torch | >=2.0.0 | Training |
| scikit-learn | >=1.3.0 | AUROC computation |
| matplotlib | >=3.8.0 | Visualization |

---

## Out of Scope

- Multiple layer comparison (H-M2)
- Baseline comparisons (H-M4)
- MLP/attention probes (future work)
- Cross-model generalization

---

## References

- Phase 2C: 02c_experiment_brief.md
- venator: Linear probe achieving 0.999 AUROC on classification
- Alain & Bengio 2016: Linear classifier probes
