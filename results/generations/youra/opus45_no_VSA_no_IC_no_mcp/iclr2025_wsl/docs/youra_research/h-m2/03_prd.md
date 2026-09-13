# PRD: h-m2 Sample Efficiency Experiment

**Hypothesis:** Locality bias reduces sample complexity for local patterns: DWS should match or exceed NFT on backdoor detection with same training data.

**Type:** MECHANISM | **Gate:** SHOULD_WORK | **Budget Tier:** FULL (30 tasks)

---

## Executive Summary

Validate that DWS locality inductive bias provides sample efficiency advantage over NFT for backdoor detection. Train both architectures on 25%, 50%, 100% of TrojAI data and compare ROC-AUC curves.

---

## Problem Statement

h-m1 confirmed DWS encodes stronger locality bias (CoV 1.44 vs NFT 1.35). This experiment tests whether that bias translates to practical sample efficiency gains on backdoor detection.

---

## Functional Requirements

### FR-1: Dataset Pipeline
- Load TrojAI Round 10 CNN models (1000+ backdoored/clean)
- Split: 70% train, 15% val, 15% test
- Subsample training: 25%, 50%, 100%

### FR-2: Model Implementations
- **MLP Baseline**: Flattened weights → [512, 256, 128] → binary
- **DWS**: Equivariant layers (reuse h-m1 implementation)
- **NFT**: Transformer encoder (reuse h-m1 implementation)

### FR-3: Training Protocol
- Optimizer: AdamW (lr=1e-4, weight_decay=0.01)
- Epochs: 100 per model
- Loss: BCEWithLogitsLoss
- 3 seeds per configuration (42, 123, 456)

### FR-4: Evaluation
- Metric: ROC-AUC on held-out test set
- Compute mean ± std across seeds
- Sample efficiency curves: AUC vs data fraction

### FR-5: Visualization
- Learning curves (AUC vs fraction)
- Bar chart at 25% data
- Gap closure plot (DWS-NFT difference)

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seeds for all random operations
- Deterministic data loading order

### NFR-2: Performance
- GPU training (CUDA)
- Target: <4 hours total training time

---

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| DWS AUC > NFT AUC at 25% data | Required |
| DWS-NFT gap narrows at 100% data | Expected |
| Both > MLP baseline | Required |

---

## Dependencies

- h-m1 validated code (DWS, NFT implementations)
- TrojAI dataset access
- PyTorch, sklearn

---

## Data Models

```python
@dataclass
class ExperimentConfig:
    fractions: List[float] = [0.25, 0.50, 1.0]
    seeds: List[int] = [42, 123, 456]
    epochs: int = 100
    lr: float = 1e-4
    batch_size: int = 32

@dataclass
class ExperimentResult:
    model: str
    fraction: float
    seed: int
    auc: float
    train_time: float
```

---

*Generated: 2026-08-28 | Phase 3 Step 2*
