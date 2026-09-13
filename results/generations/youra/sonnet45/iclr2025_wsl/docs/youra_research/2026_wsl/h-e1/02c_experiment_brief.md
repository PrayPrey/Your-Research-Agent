# Experiment Design: h-e1

**Date:** 2026-03-19
**Author:** Anonymous
**Hypothesis Statement:** Under training on a heterogeneous 750-model zoo (CNNs, Transformers, MLPs), if a Compositional Architecture-Agnostic Weight Encoder (CAWE) is trained to predict generalization gap, then it achieves Spearman ρ > 0.7 (95% CI lower bound) on a 150-model held-out test set because the shared NFT backbone learns architecture-independent weight relationships from tokenized representations.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None (foundation hypothesis)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK - If fail: ABANDON → ROUTE_TO_PHASE_0 (entire approach invalidated)

---

## Continuation Context

This is the foundation hypothesis with no prerequisites. Success validates the core CAWE approach.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in verification sequence

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Neural Functional Transformer Experiment Design**
- Limited direct NFT references in knowledge base
- Related attention mechanism documentation found (PyTorch scaled_dot_product_attention)
- Key insight: Permutation-equivariant attention is core to transformer architectures

**Query 2: Architecture-Agnostic Weight Tokenization**
- Found model quantization and weight conversion patterns
- Insight: Weight transformation techniques (quantization) show feasibility of weight-space operations
- Adapter and LoRA patterns demonstrate weight-level modifications

**Query 3: Model Zoo Benchmarking**
- ModelScope model zoo framework found (github.com/modelscope/modelscope)
- Limited generalization gap prediction benchmarks in current knowledge base
- Insight: Model zoo infrastructure exists but specific weight-space learning applications are novel

### Archon Code Examples

**Query 1: Transformer Implementation Patterns**
- PyTorch scaled_dot_product_attention (canonical attention implementation)
  - Pattern: Demonstrates efficient attention computation with masking
  - Insight: Standard transformer attention can serve as NFT backbone reference

**Query 2: Weight Space Operations**
- Weight quantization examples (bitsandbytes int8)
  - Code shows weight loading, transformation, and state dict operations
  - Pattern: `model.load_state_dict()` → transform weights → use in forward pass
  - Insight: Weight-level operations are standard in PyTorch ecosystem

**Query 3: Token Embedding Operations**
- CLIP tokenizer configuration examples
  - Pattern: Tokenization pipelines with special tokens and encoding
  - Insight: Tokenization strategies are well-established for text, adaptable to weights

### Exa GitHub Implementations

**Query 1: Neural Functional Transformer Official Implementation**

**Repository 1**: AllanYangZhou/nfn (⭐171, MIT License)
- **URL**: https://github.com/AllanYangZhou/nfn
- **Relevance**: ⭐⭐⭐ HIGHEST - Official NFT implementation from paper authors (NeurIPS 2023)
- **Paper**: "Neural Functional Transformers" (Zhou et al., NeurIPS 2023)
- **Architecture**: Permutation-equivariant NF-Layers (NPLinear) with attention mechanism
- **Key Code Pattern**:
  ```python
  from nfn import layers
  from nfn.common import network_spec_from_wsfeat, state_dict_to_tensors

  # Convert weights to WeightSpaceFeatures
  wsfeat = state_dict_to_tensors(model.state_dict())
  network_spec = network_spec_from_wsfeat(wsfeat)

  # Build NFN with NPLinear layers
  nfn = nn.Sequential(
      layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
      layers.TupleOp(nn.ReLU()),
      layers.NPLinear(network_spec, nfn_channels, nfn_channels, io_embed=True)
  )
  ```
- **Installation**: `pip install nfn` (PyPI available)
- **Datasets Used**: MNIST MLPs, small CNNs (homogeneous single-architecture zoos)
- **Results**: +17% INR classification improvement over prior methods
- **Limitation**: Original paper tested on homogeneous zoos (single architecture family)

**Repository 2**: Fsoft-AIC/Transformer-NFN (⭐N/A, ICLR 2025, MIT License)
- **URL**: https://github.com/Fsoft-AIC/Transformer-NFN
- **Relevance**: ⭐⭐ HIGH - Recent extension to transformer architectures
- **Paper**: "Equivariant Neural Functional Networks for Transformers" (ICLR 2025)
- **Datasets**: AG-News-Transformers, MNIST-Transformers (HuggingFace model zoos)
- **Key Insight**: Demonstrates NFN application to transformer weight spaces
- **Training Config**:
  - Command: `python nfn_transformer/main.py --enc_mode inv --classifier_nfn_channels 10,10 --transformers_nfn_channels 10`
  - Architecture-specific channels configuration

**Query 2: Weight Space Learning & Model Zoo**

**Repository 3**: Zehong-Wang/Awesome-Weight-Space-Learning (⭐Collection)
- **URL**: https://github.com/Zehong-Wang/Awesome-Weight-Space-Learning
- **Relevance**: ⭐⭐⭐ Survey resource - comprehensive weight space learning overview
- **Key References**:
  - Schürholt et al. "Towards Scalable and Versatile Weight Space Learning" (ICML 2024)
  - Unterthiner et al. "Predicting Neural Network Accuracy from Weights" (2021)
  - Model Zoo datasets: NeurIPS 2022 paper with diverse populations
- **Insight**: Active research area with ICLR 2025 workshop on weight space learning

**Repository 4**: HSG-AIML Model Zoo Research
- **Paper**: "Model Zoos: A Dataset of Diverse Populations of Neural Network Models" (NeurIPS 2022)
- **Architecture**: SANE encoder-decoder for weight tokenization
- **Key Pattern**: Tokenize weights → transformer encoder → task-specific heads
- **Multi-zoo Training**: Recent work (2026) on training across heterogeneous zoos

**Serena Analysis Needed**: ✅ YES
- Complex NFN layer implementation (NPLinear, TupleOp)
- Architecture-specific tokenization strategies
- Multi-zoo training modifications

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Priority Hierarchy:**
1. ⭐⭐⭐ Official NFT implementation (github.com/AllanYangZhou/nfn) - PyPI available
2. ⭐⭐ ICLR 2025 Transformer-NFN extension (github.com/Fsoft-AIC/Transformer-NFN)
3. ⭐ Custom implementation based on paper specifications

**Recommended Implementation Path:**
- Primary: Use `nfn` library from PyPI (`pip install nfn`) for NFT backbone
- Fallback: Custom NPLinear implementation based on paper equations if library issues arise
- Justification: Official library is maintained, peer-reviewed (NeurIPS 2023), and provides proven NFT layers. Custom tokenizers needed for architecture-agnostic extension (not in original library).

### Code Analysis (Serena MCP)

**Status**: *Limited* - Analyzed from GitHub documentation (external nfn library, not in local codebase)

**NFN Library Structure** (from github.com/AllanYangZhou/nfn):

**Core Components**:
- `WeightSpaceFeatures`: Data structure for weight tensors
- `NPLinear`: Permutation-equivariant linear layer (core NF-Layer)
- `TupleOp`: Element-wise operations on weight space features
- `network_spec`: Specification of input network architecture

**Core Mechanism**: NPLinear (Neural Parameter Linear Layer)
- **Purpose**: Permutation-equivariant transformation of weight-space features
- **Input**: WeightSpaceFeatures (weight tensors from source network)
- **Output**: Transformed weight-space features
- **Key Property**: Maintains equivariance to neuron permutations in weight space

**Integration Pattern**:
```python
# Step 1: Convert model weights to weight-space features
wsfeat = state_dict_to_tensors(model.state_dict())
network_spec = network_spec_from_wsfeat(wsfeat)

# Step 2: Build NFN encoder with NPLinear layers
nfn_encoder = nn.Sequential(
    layers.NPLinear(network_spec, in_channels=1, out_channels=32, io_embed=True),
    layers.TupleOp(nn.ReLU()),
    layers.NPLinear(network_spec, in_channels=32, out_channels=64, io_embed=True),
    layers.TupleOp(nn.ReLU()),
    layers.NPLinear(network_spec, in_channels=64, out_channels=128, io_embed=True)
)

# Step 3: Forward pass
encoded_weights = nfn_encoder(wsfeat)

# Step 4: Task-specific head (e.g., generalization gap prediction)
prediction_head = nn.Sequential(
    nn.Linear(128, 64),
    nn.ReLU(),
    nn.Linear(64, 1)  # Regression output
)
```

**Architecture-Specific Tokenization** (for CAWE):
Since NFN library expects specific network architectures, we need custom tokenizers:
- **CNN Tokenizer**: Extract conv kernels → flatten → project to D-dim tokens
- **Transformer Tokenizer**: Extract Q/K/V matrices → project to D-dim tokens
- **MLP Tokenizer**: Extract weight matrices → project to D-dim tokens
- All tokenizers output fixed D-dimensional tokens for NFT backbone

---

## Experiment Specification

### Dataset

**Dataset**: Heterogeneous Model Zoo (750 models)
**Type**: standard (3 sources)
**Composition**:
- ViT Model Zoo: 250 Vision Transformer models
- torchvision.models: 250 CNN models (ResNet, VGG, etc.)
- Unterthiner MNIST MLPs: 250 fully-connected models

**Statistics**:
- Total models: 750 (train: 600, test: 150)
- Stratified split: 200/200/200 per family (train), 50/50/50 per family (test)
- Each model includes: weights (.pt or .pth), generalization gap metadata

**Source & Access**:
- ViT: HuggingFace `timm` library or direct download
- CNNs: `torchvision.models` (pretrained=True)
- MLPs: Zenodo 5645138 (research dataset)

**Loading Information** (for Phase 4 download):
- Method: Multi-source (HuggingFace + torchvision + Zenodo)
- Identifier: Custom model zoo assembly
- Code:
  ```python
  # ViT models (250)
  import timm
  vit_models = [
      timm.create_model('vit_base_patch16_224', pretrained=True),
      timm.create_model('vit_large_patch16_224', pretrained=True),
      # ... 250 variants
  ]

  # CNN models (250)
  import torchvision.models as models
  cnn_models = [
      models.resnet18(pretrained=True),
      models.resnet50(pretrained=True),
      models.vgg16(pretrained=True),
      # ... 250 variants
  ]

  # MLP models (250)
  # Load from Zenodo 5645138 or generate MNIST-trained MLPs
  # Reference: Unterthiner et al. (2021) "Predicting NN Accuracy from Weights"
  ```

**Preprocessing**: Extract model weights via `.state_dict()`, compute generalization gap (train_acc - test_acc)

**Target Variable**: Generalization gap (continuous, regression task)

### Models

#### Baseline Model

**Architecture**: Flat-weight MLP (naive baseline)
**Type**: Simple feedforward network on concatenated weights
**Purpose**: Baseline comparison to show CAWE improvement (Δρ > 0.15 required)

**Configuration**:
- Input: Flattened weight vector (all model weights concatenated)
- Hidden layers: [512, 256, 128]
- Output: 1 (generalization gap prediction)
- Activation: ReLU
- Dropout: 0.2

**Loading Information** (for Phase 4 download):
- Method: Custom implementation (no pretrained)
- Identifier: N/A (simple MLP, implement from scratch)
- Code:
  ```python
  class FlatWeightMLP(nn.Module):
      def __init__(self, input_dim):
          super().__init__()
          self.fc = nn.Sequential(
              nn.Linear(input_dim, 512),
              nn.ReLU(),
              nn.Dropout(0.2),
              nn.Linear(512, 256),
              nn.ReLU(),
              nn.Dropout(0.2),
              nn.Linear(256, 128),
              nn.ReLU(),
              nn.Linear(128, 1)
          )

      def forward(self, x):
          return self.fc(x.flatten(1))
  ```

#### Proposed Model (CAWE)

**Architecture:** Neural Functional Transformer (NFT) with Architecture-Specific Tokenizers
**Integration**: Compositional design - tokenizers → shared token space → NFT backbone → regression head

**Core Mechanism Implementation:**

```python
# Core Mechanism: Compositional Architecture-Agnostic Weight Encoder (CAWE)
# Based on: github.com/AllanYangZhou/nfn (NFT paper, NeurIPS 2023)

import torch
import torch.nn as nn
from nfn import layers
from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat

class ArchitectureSpecificTokenizer(nn.Module):
    """Project architecture-specific weights to D-dimensional tokens"""
    def __init__(self, arch_type, token_dim=128):
        super().__init__()
        self.arch_type = arch_type  # 'cnn' | 'transformer' | 'mlp'
        self.token_dim = token_dim

        if arch_type == 'cnn':
            # CNN: Extract conv kernels, flatten, project
            self.proj = nn.Linear(variable_size, token_dim)
        elif arch_type == 'transformer':
            # Transformer: Extract Q/K/V matrices, project
            self.proj = nn.Linear(variable_size, token_dim)
        else:  # mlp
            # MLP: Extract weight matrices, project
            self.proj = nn.Linear(variable_size, token_dim)

    def forward(self, weights):
        # weights: state_dict from source model
        # Extract relevant parameters, flatten, project to D-dim
        tokens = self.proj(extracted_weights)
        return tokens  # (num_layers, token_dim)

class CAWE(nn.Module):
    """Compositional Architecture-Agnostic Weight Encoder"""
    def __init__(self, token_dim=128, nft_channels=64):
        super().__init__()
        # Architecture-specific tokenizers
        self.tokenizers = nn.ModuleDict({
            'cnn': ArchitectureSpecificTokenizer('cnn', token_dim),
            'transformer': ArchitectureSpecificTokenizer('transformer', token_dim),
            'mlp': ArchitectureSpecificTokenizer('mlp', token_dim)
        })

        # Shared NFT backbone (from nfn library)
        # Processes tokens with permutation-equivariant attention
        self.nft_encoder = nn.Sequential(
            layers.NPLinear(network_spec, token_dim, nft_channels, io_embed=True),
            layers.TupleOp(nn.ReLU()),
            layers.NPLinear(network_spec, nft_channels, nft_channels*2, io_embed=True),
            layers.TupleOp(nn.ReLU()),
            layers.NPLinear(network_spec, nft_channels*2, nft_channels*2, io_embed=True)
        )

        # Regression head for generalization gap prediction
        self.prediction_head = nn.Sequential(
            nn.Linear(nft_channels*2, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 1)  # Generalization gap (continuous)
        )

    def forward(self, weights, arch_family):
        # Step 1: Architecture-specific tokenization
        tokens = self.tokenizers[arch_family](weights)

        # Step 2: NFT backbone (shared processing)
        encoded = self.nft_encoder(tokens)

        # Step 3: Pool encoded features
        pooled = encoded.mean(dim=0)  # Global average pooling

        # Step 4: Predict generalization gap
        gap_pred = self.prediction_head(pooled)
        return gap_pred
```

### Training Protocol

**Optimizer**: AdamW
- Parameters: lr=1e-4, betas=(0.9, 0.999), weight_decay=1e-2
- Source: Standard for transformer architectures, NFT paper default

**Learning Rate**: 1e-4 (fixed)
- Schedule: None (PoC uses fixed LR)
- Source: NFT paper baseline

**Batch Size**: 32
- Source: Phase 2B specification, NFT paper default

**Epochs**: 100
- Early stopping: patience=10 on validation Spearman ρ
- Source: Phase 2B specification

**Loss Function**: Mean Squared Error (MSE)
- Target: Generalization gap (regression)
- Source: Standard for regression tasks

**Seeds**: 42 (single seed for PoC)

**Training Data**: 600 models (200 CNN, 200 Transformer, 200 MLP) - stratified split

### Evaluation

**Primary Metric**: Spearman ρ (rank correlation)
- Measures: Correlation between predicted and actual generalization gap
- Success: ρ > 0.7 (95% CI lower bound)
- Source: Phase 2B success criteria

**Secondary Metric**: Per-architecture Spearman ρ
- CNN subset: ρ_cnn
- Transformer subset: ρ_transformer
- MLP subset: ρ_mlp
- Success: All three ρ > 0.65

**Baseline Comparison**: Δρ = ρ_CAWE - ρ_baseline
- Success: Δρ > 0.15 (CAWE significantly outperforms flat-weight MLP)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Regression (generalization gap prediction)
- Library: scipy.stats
- Code:
  ```python
  from scipy.stats import spearmanr
  import numpy as np

  # Compute Spearman correlation
  rho, p_value = spearmanr(y_true, y_pred)

  # Bootstrap 95% CI
  bootstrap_rhos = []
  for _ in range(1000):
      indices = np.random.choice(len(y_true), len(y_true), replace=True)
      rho_boot, _ = spearmanr(y_true[indices], y_pred[indices])
      bootstrap_rhos.append(rho_boot)
  ci_lower = np.percentile(bootstrap_rhos, 2.5)
  ci_upper = np.percentile(bootstrap_rhos, 97.5)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Spearman ρ comparison (CAWE vs Baseline) with 95% CI error bars

#### Additional Figures (LLM Autonomous)
- **Per-architecture Performance**: Bar chart showing ρ for CNN/Transformer/MLP subsets
- **Prediction Scatter**: Scatter plot of predicted vs actual generalization gap (150 test models)
- **Architecture Clustering**: t-SNE projection of CAWE embeddings colored by architecture family

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### Primary References

**1. Neural Functional Transformers (NeurIPS 2023)**
- Authors: Allan Zhou, Kaien Yang, Yiding Jiang, Kaylee Burns, et al.
- Paper: https://arxiv.org/abs/2305.13546
- Code: https://github.com/AllanYangZhou/nfn
- PyPI: `pip install nfn`
- Key Contribution: Permutation-equivariant attention for weight spaces

**2. Weight Space Learning Survey (2026)**
- Repository: https://github.com/Zehong-Wang/Awesome-Weight-Space-Learning
- Key Papers:
  - Schürholt et al. "Towards Scalable and Versatile Weight Space Learning" (ICML 2024)
  - Unterthiner et al. "Predicting Neural Network Accuracy from Weights" (2021)

**3. Model Zoo Datasets**
- ViT Models: HuggingFace `timm` library
- CNN Models: torchvision.models
- Unterthiner MNIST MLPs: Zenodo 5645138

### Implementation Code Examples

**NFT Layer Usage**:
```python
from nfn import layers
from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat

# Convert model weights
wsfeat = state_dict_to_tensors(model.state_dict())
network_spec = network_spec_from_wsfeat(wsfeat)

# Build NFN
nfn = nn.Sequential(
    layers.NPLinear(network_spec, 1, 32, io_embed=True),
    layers.TupleOp(nn.ReLU()),
    layers.NPLinear(network_spec, 32, 64, io_embed=True)
)
```

**Model Loading**:
```python
# ViT
import timm
vit = timm.create_model('vit_base_patch16_224', pretrained=True)

# CNN
import torchvision.models as models
resnet = models.resnet50(pretrained=True)

# Extract weights
weights = model.state_dict()
```

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-19T05:53:38Z

### Workflow History for This Hypothesis
- 2026-03-19T05:52:58Z: Hypothesis set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- 2026-03-19T05:53:38Z: Phase 2C started (Experiment design workflow initiated)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
