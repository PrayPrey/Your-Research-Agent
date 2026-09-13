# PRD: h-m3 Architecture × Task Interaction Experiment

**Hypothesis:** Task-dependent optimal bias manifests as performance difference: significant interaction effect between architecture type and property type (backdoor vs accuracy).

**Type:** MECHANISM | **Gate:** SHOULD_WORK | **Budget Tier:** FULL (30 tasks)

---

## Executive Summary

Validate that different weight-space architectures (DWS, NFT, MLP) exhibit task-dependent performance: DWS should excel at backdoor detection (local anomalies) while NFT should excel at accuracy prediction (global statistics). This tests the hypothesis that architectural inductive bias interacts with task type.

---

## Problem Statement

h-m2 was inconclusive due to dataset ceiling effect (all models achieved 1.0 AUC on synthetic data). h-m3 uses real-world datasets (TrojAI for backdoor, CNN-Zoo for accuracy) to test whether architectural bias interacts with task type, producing crossover performance.

---

## Functional Requirements

### FR-1: Backdoor Detection Dataset (TrojAI)
- Load TrojAI Object Detection Round models
- Target: 600 train, 200 test models
- Labels: Binary (clean/backdoored)
- Model types: ResNet50, DenseNet121, InceptionV3

### FR-2: Accuracy Prediction Dataset (CNN-Zoo)
- Load CNN Zoo CIFAR-10 models (Schürholt et al.)
- Target: 1000 train, 300 test models
- Labels: Continuous (test accuracy 0-100%)
- Model types: ResNet variants

### FR-3: Model Implementations
- **MLP Baseline**: Flattened weights → [512, 256, 128] → output
- **DWS**: Equivariant layers (locality bias)
- **NFT**: Transformer encoder (global attention)
- Match parameter counts within 10%

### FR-4: Training Protocol
- Optimizer: AdamW (lr=1e-4)
- Schedule: Cosine annealing
- Batch size: 32
- Epochs: 100
- Seeds: 3 (42, 123, 456)
- Loss (backdoor): BCEWithLogitsLoss
- Loss (accuracy): MSE

### FR-5: Evaluation Metrics
- Backdoor: ROC-AUC
- Accuracy prediction: RMSE, R²
- Expected baselines: MLP ~0.70 AUC, MLP R² ~0.6

### FR-6: Interaction Effect Analysis
- 2×3 factorial design: 2 tasks × 3 architectures
- Test for significant interaction effect
- Compare: DWS_AUC > NFT_AUC (backdoor) AND NFT_RMSE < DWS_RMSE (accuracy)

### FR-7: Visualization
- 2×2 bar chart: DWS vs NFT × Backdoor vs Accuracy
- Interaction plot: Architecture × Performance, lines for each task
- Training curves: Loss/metric over epochs for all 6 conditions
- Performance difference heatmap

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seeds for all random operations
- Deterministic data loading order
- Version-pinned dependencies

### NFR-2: Performance
- GPU training (CUDA)
- Target: <8 hours total training time (6 conditions × 3 seeds)

### NFR-3: Statistical Rigor
- 3 seeds minimum for interaction significance
- Report mean ± std for all metrics

---

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| DWS AUC > NFT AUC on backdoor | Required |
| NFT RMSE < DWS RMSE on accuracy | Required |
| Both equivariant > MLP on at least one task | Required |
| Significant interaction effect (p < 0.05) | Expected |

---

## Dependencies

- h-m2 validated code (DWS, NFT implementations, if available)
- TrojAI dataset access
- CNN-Zoo dataset access
- PyTorch, sklearn, torchmetrics

---

## Data Models

```python
@dataclass
class ExperimentConfig:
    tasks: List[str] = ["backdoor", "accuracy"]
    architectures: List[str] = ["mlp", "dws", "nft"]
    seeds: List[int] = [42, 123, 456]
    epochs: int = 100
    lr: float = 1e-4
    batch_size: int = 32

@dataclass
class ExperimentResult:
    task: str
    architecture: str
    seed: int
    metric_value: float  # AUC for backdoor, RMSE for accuracy
    train_time: float
```

---

## Ablation Variants

1. **Tokenization method**: Fixed-size chunks vs layer-aligned
2. **Hidden dimension**: 256 vs 512
3. **Number of layers**: 4 vs 6

---

*Generated: 2026-08-28 | Phase 3 Step 2*
