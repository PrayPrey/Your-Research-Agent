# Experiment Design: H-M3

**Date:** 2026-08-28
**Author:** PrayPrey
**Hypothesis Statement:** Task-dependent optimal bias manifests as performance difference: significant interaction effect between architecture type and property type (backdoor vs accuracy).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Testing interaction effect between architecture and task type.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m2 completed with LIMITATION_RECORDED)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2

### Gate Condition
SHOULD_WORK gate: If fails, document limitation and continue (no pipeline stop).

---

## Continuation Context

H-M2 completed with LIMITATION_RECORDED status:
- Dataset ceiling effect observed on synthetic MNIST-INR (all models achieved 1.0 AUC)
- Sample efficiency hypothesis remains plausible but requires harder dataset (TrojAI)
- H-M3 must use TrojAI dataset to avoid same ceiling effect

### Previous Hypothesis Results (if applicable)
H-M2 findings inform H-M3 design:
1. Synthetic datasets produce meaningless results (ceiling effect)
2. Must use real TrojAI dataset for backdoor detection
3. Must use real ModelZoo for accuracy prediction
4. Both tasks needed to test interaction effect

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Weight-Space Architecture Comparison**
- Deep Weight-Space Networks (DWSNets) leverage intrinsic permutation symmetries in MLPs
- DWS constructs layers equivariant to hidden neuron permutation group
- NFT uses attention mechanism for permutation equivariant weight-space layers
- Source: [ICML 2023 - Navon et al.](https://proceedings.mlr.press/v202/navon23a/navon23a.pdf)

**Query 2: Backdoor Detection Methods**
- Weight-space meta analysis extracts features from pre-trained DNN weights
- TrojAI uses AUC and cross-entropy (CE) as primary metrics
- CE threshold of ln(2)/2 ≈ 0.347 is TrojAI program detection goal
- Source: [TrojAI Documentation](https://pages.nist.gov/trojai/docs/overview.html)

**Query 3: Accuracy Prediction from Weights**
- Unterthiner et al. (2020) pioneered predicting neural network accuracy from weights
- Weight statistics perform well for property prediction
- Source: [arXiv:2002.11448](https://arxiv.org/pdf/2002.11448)

### Archon Code Examples

**DWS Implementation Pattern:**
```python
# From AvivNavon/DWSNets
class DWSLayer(nn.Module):
    """Equivariant layer for weight-space processing"""
    def __init__(self, in_channels, out_channels):
        # Constructs permutation-equivariant operations
        self.weight_processor = EquivariantConv(in_channels, out_channels)
    
    def forward(self, weights):
        # Process weights while preserving permutation symmetry
        return self.weight_processor(weights)
```

**NFT Implementation Pattern:**
```python
# From AllanYangZhou/nfn
class NFTLayer(nn.Module):
    """Neural Functional Transformer layer"""
    def __init__(self, dim, num_heads):
        self.attention = nn.MultiheadAttention(dim, num_heads)
    
    def forward(self, weight_tokens):
        # Global attention over weight tokens
        return self.attention(weight_tokens, weight_tokens, weight_tokens)
```

### Exa GitHub Implementations

**Repository 1**: [AvivNavon/DWSNets](https://github.com/AvivNavon/DWSNets) (⭐ Official)
- **URL**: https://github.com/AvivNavon/DWSNets
- **Relevance**: Official DWS implementation for weight-space learning
- **Architecture**: Permutation-equivariant layers with locality constraints
- **Training Config**:
  - Optimizer: Adam
  - Learning rate: 1e-4
  - Batch size: 64
  - Epochs: 100
- **Dataset**: INR datasets, can adapt to model zoos

**Repository 2**: [AllanYangZhou/nfn](https://github.com/AllanYangZhou/nfn) (⭐ Official)
- **URL**: https://github.com/AllanYangZhou/nfn
- **Relevance**: Official NFT implementation with attention-based weight processing
- **Architecture**: Transformer layers adapted for weight-space
- **Training Config**:
  - Optimizer: AdamW
  - Learning rate: 3e-4
  - Batch size: 32
  - Epochs: 100

**Serena Analysis Needed**: No (official implementations are well-documented)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Implementation | Status |
|----------|---------------|--------|
| 1 | AvivNavon/DWSNets (Official) | ✅ Available |
| 2 | AllanYangZhou/nfn (Official) | ✅ Available |
| 3 | Community implementations | Not needed |

**Recommended Implementation Path:**
- Primary: Use official DWSNets and nfn repositories directly
- Fallback: Adapt from Awesome-Weight-Space-Learning collection
- Justification: Official implementations ensure reproducibility; both are PyTorch-based and actively maintained

### Code Analysis (Serena MCP)

*Skipped - Official implementations are well-documented with clear APIs*

---

## Experiment Specification

### Dataset

**Task 1: Backdoor Detection (TrojAI)**

| Attribute | Value |
|-----------|-------|
| **Name** | TrojAI Object Detection Round |
| **Type** | standard |
| **Source** | NIST TrojAI Program |
| **URL** | https://pages.nist.gov/trojai/ |
| **Split** | Train: 600 models, Test: 200 models (typical round) |
| **Labels** | Binary (clean/backdoored) |
| **Model Types** | ResNet50, DenseNet121, InceptionV3 |

**Task 2: Accuracy Prediction (Model Zoo)**

| Attribute | Value |
|-----------|-------|
| **Name** | CNN Zoo (Unterthiner-style) |
| **Type** | standard |
| **Source** | Model Zoos Dataset (Schürholt et al.) |
| **URL** | https://github.com/model-zoos |
| **Split** | Train: 1000 models, Test: 300 models |
| **Labels** | Continuous (test accuracy 0-100%) |
| **Model Types** | ResNet variants trained on CIFAR-10 |

**Loading Information** (for Phase 4 download):
- Method: Custom download scripts + torch.load
- Identifier: `trojai-round-X` (select appropriate round), `cnn-zoo-cifar10`
- Code:
```python
# TrojAI models
import torch
model_weights = torch.load(f"trojai_models/{model_id}/model.pt")
label = pd.read_csv(f"trojai_models/{model_id}/ground_truth.csv")

# CNN Zoo models  
model_weights = torch.load(f"cnn_zoo/{model_id}/weights.pt")
accuracy = metadata[model_id]["test_accuracy"]
```

### Models

#### Baseline Model

**MLP Baseline (Flattened Weights)**

| Attribute | Value |
|-----------|-------|
| **Architecture** | 3-layer MLP |
| **Input** | Flattened weight vector |
| **Hidden** | [512, 256, 128] |
| **Output** | 1 (binary) or 1 (regression) |
| **Activation** | ReLU |
| **Source** | Standard baseline from TrojAI literature |

**Loading Information** (for Phase 4 download):
- Method: Custom implementation
- Identifier: N/A (implement from scratch)
- Code:
```python
class MLPBaseline(nn.Module):
    def __init__(self, input_dim, hidden_dims=[512, 256, 128]):
        super().__init__()
        layers = []
        prev_dim = input_dim
        for h in hidden_dims:
            layers.extend([nn.Linear(prev_dim, h), nn.ReLU()])
            prev_dim = h
        layers.append(nn.Linear(prev_dim, 1))
        self.net = nn.Sequential(*layers)
```

#### Proposed Model

**Architecture:** DWS and NFT (testing both against baseline)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Architecture × Task Interaction Test
# Based on: DWSNets (Navon 2023), NFT (Zhou 2023)

class WeightSpaceProcessor(nn.Module):
    """
    Abstract base for weight-space architectures.
    Subclasses: DWSProcessor (local bias), NFTProcessor (global attention)
    """
    def __init__(self, weight_dim, hidden_dim=256, num_layers=4):
        super().__init__()
        self.weight_dim = weight_dim
        self.hidden_dim = hidden_dim
        
    def forward(self, weights):
        """
        Args:
            weights: List of (weight, bias) tuples from target network
        Returns:
            prediction: (B, 1) - task output (backdoor prob or accuracy)
        """
        # Tokenize weights for processing
        tokens = self.tokenize(weights)  # (B, N_tokens, D)
        # Process through architecture-specific layers
        features = self.process(tokens)  # (B, hidden_dim)
        # Final prediction head
        return self.head(features)  # (B, 1)

class DWSProcessor(WeightSpaceProcessor):
    """Locality-biased: equivariant layers preserve weight structure"""
    def process(self, tokens):
        # Local operations respect layer boundaries
        return self.equivariant_layers(tokens)

class NFTProcessor(WeightSpaceProcessor):
    """Global attention: all weights attend to all weights"""
    def process(self, tokens):
        # Full attention across all weight tokens
        return self.transformer_layers(tokens)

# Integration: Both processors share same input/output interface
# Test: DWS on backdoor (local anomaly) vs NFT on accuracy (global stat)
```

### Training Protocol

| Parameter | Value | Source |
|-----------|-------|--------|
| **Optimizer** | AdamW | DWSNets, NFT papers |
| **Learning Rate** | 1e-4 | DWSNets default |
| **Schedule** | Cosine annealing | Common in transformer literature |
| **Batch Size** | 32 | NFT default (memory-constrained) |
| **Epochs** | 100 | Both papers |
| **Loss (Backdoor)** | Binary Cross-Entropy | Classification task |
| **Loss (Accuracy)** | MSE | Regression task |
| **Seeds** | 3 | For interaction effect significance |

### Evaluation

**Primary Metrics:**

| Task | Metric | Definition |
|------|--------|------------|
| Backdoor Detection | AUC-ROC | Area under ROC curve |
| Accuracy Prediction | RMSE | Root mean squared error |
| Accuracy Prediction | R² | Coefficient of determination |

**Success Criteria (Interaction Effect):**
1. DWS_AUC > NFT_AUC on backdoor detection (locality advantage)
2. NFT_RMSE < DWS_RMSE on accuracy prediction (global aggregation advantage)
3. Both > MLP_baseline on at least one task

**Expected Baseline Performance** (from research):
- MLP on TrojAI: ~0.70 AUC (estimated from TrojAI competition results)
- MLP on accuracy prediction: R² ~0.6 (Unterthiner 2020)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (backdoor), Regression (accuracy)
- Library: torchmetrics, sklearn.metrics
- Code:
```python
from torchmetrics import AUROC, MeanSquaredError, R2Score
from sklearn.metrics import roc_auc_score

# Backdoor metrics
auroc = AUROC(task="binary")
auc_score = auroc(predictions, labels)

# Accuracy prediction metrics
rmse = MeanSquaredError(squared=False)
r2 = R2Score()
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: 2×2 bar chart showing DWS vs NFT × Backdoor vs Accuracy

#### Additional Figures (LLM Autonomous)

1. **Interaction Plot**: Architecture (x-axis) × Performance (y-axis), lines for each task type
2. **Performance Difference Heatmap**: Architecture × Task matrix showing delta from baseline
3. **Training Curves**: Loss/metric over epochs for all 6 conditions (3 arch × 2 tasks)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- [ ] DWS implementation loads and processes weight inputs correctly
- [ ] NFT implementation loads and processes weight inputs correctly  
- [ ] Both architectures produce same output shape for same input
- [ ] Parameter counts are matched within 10%

### Activation Indicators
- **Log Message**: "Processing {N} weight tokens through {architecture_name}"
- **Tensor Shape Change**: Input (B, N_weights) → Tokens (B, N_tokens, D) → Output (B, 1)
- **Metric Delta Expected**: >0.05 AUC difference between architectures on each task

### Architecture Compatibility
- DWS: Requires weight tensor in layer-separated format
- NFT: Requires weight tensor tokenized into fixed-size chunks
- Both: Input/output interface must be identical for fair comparison

### Verification Code
```python
def verify_mechanism(dws_model, nft_model, sample_weights):
    """Verify both architectures process weights correctly"""
    # Check forward pass works
    dws_out = dws_model(sample_weights)
    nft_out = nft_model(sample_weights)
    
    # Verify output shapes match
    assert dws_out.shape == nft_out.shape, "Output shapes must match"
    
    # Verify outputs are different (architectures are distinct)
    assert not torch.allclose(dws_out, nft_out), "Architectures must produce different outputs"
    
    print("✓ Mechanism verification passed")
    return True
```

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on both tasks
2. Interaction effect observed: DWS > NFT on backdoor AND NFT > DWS on accuracy
3. Both equivariant architectures outperform MLP baseline on at least one task

---

## Appendix: Reference Implementations

| Source | URL | Usage |
|--------|-----|-------|
| DWSNets (Official) | https://github.com/AvivNavon/DWSNets | DWS architecture |
| NFN (Official) | https://github.com/AllanYangZhou/nfn | NFT architecture |
| TrojAI Program | https://pages.nist.gov/trojai/ | Backdoor detection dataset |
| Model Zoos | https://arxiv.org/pdf/2209.14764 | Accuracy prediction dataset |
| Unterthiner 2020 | https://arxiv.org/pdf/2002.11448 | Accuracy from weights baseline |
| Awesome Weight-Space Learning | https://github.com/Zehong-Wang/Awesome-Weight-Space-Learning | Reference collection |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- 2026-08-28: Experiment design started (IN_PROGRESS)
- 2026-08-28: Research completed (Archon KB, Exa GitHub)
- 2026-08-28: Experiment specification synthesized

---

*MCP Tools Used: WebSearch (Knowledge + Code)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
