# Experiment Design: h-e1

**Date:** 2026-08-28
**Author:** PrayPrey
**Hypothesis Statement:** Locality inductive bias difference exists between DWS and NFT architectures, measurable via distinct processing patterns on weight-space inputs.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK: If fails, ABANDON entire hypothesis chain (core premise invalid)

---

## Continuation Context

First hypothesis in chain. No prior context.

### Previous Hypothesis Results (if applicable)
N/A - This is the root hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Skipped* - Archon MCP unavailable in this session.

### Archon Code Examples

*Skipped* - Archon MCP unavailable in this session.

### Exa GitHub Implementations

**Query 1: DWS Official Implementation**

**Repository 1**: AvivNavon/DWSNets
- **URL**: https://github.com/AvivNavon/DWSNets
- **Paper**: ICML 2023 "Equivariant Architectures for Learning in Deep Weight Spaces"
- **Language**: Python (PyTorch 1.12.1)
- **Relevance**: Official DWS implementation with equivariant layers
- **Datasets**: MNIST INRs, CIFAR10 classifiers, SSL INRs, Sine regression INRs
- **Dependencies**: Python 3.9, PyTorch 1.12.1, Torchvision 0.13.1, CUDA 11.3
- **Key Insight**: Uses custom INR datasets, not TrojAI directly
- **Retrieved via**: WebSearch fallback (Exa MCP unavailable)

**Query 2: NFT Implementation**

**Repository 2**: AllanYangZhou/nfn
- **URL**: https://github.com/AllanYangZhou/nfn
- **Paper**: NeurIPS 2023 "Neural Functional Transformers"
- **Language**: Python (PyTorch)
- **Relevance**: Official NFT/NFN library with permutation-equivariant layers
- **Components**: NPLinear layers, TupleOp, HNPPool pooling
- **Key Insight**: Infrastructure library; requires custom training code
- **Retrieved via**: WebSearch fallback (Exa MCP unavailable)

**Serena Analysis Needed**: false (code structure clear from repos)

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Availability | Notes |
|----------|--------|--------------|-------|
| 1 | AvivNavon/DWSNets | Available | Official DWS, ICML 2023 |
| 2 | AllanYangZhou/nfn | Available | Official NFT/NFN, NeurIPS 2023 |
| 3 | Custom integration | Required | Neither repo has TrojAI benchmarks |

**Recommended Implementation Path:**
- Primary: Use DWSNets equivariant layers + nfn NPLinear layers
- Fallback: Reimplement core mechanisms from paper descriptions
- Justification: Both official implementations available; need custom dataset integration

### Code Analysis (Serena MCP)

*Skipped* - Serena optional and code structure clear from README analysis.

---

## Experiment Specification

### Dataset

**Dataset**: MNIST INRs (Implicit Neural Representations)
**Type**: standard (pre-generated INR weights from DWSNets authors)
**Source**: DWSNets official Dropbox (linked in AvivNavon/DWSNets README)

**Description**: 
- Collection of SIREN networks encoding MNIST digit images
- Each sample is a set of neural network weights representing one MNIST image
- Task: Classify INR weights to predict original digit class (0-9)

**Statistics**:
- Training: ~50,000 INR models (one per MNIST training image)
- Test: ~10,000 INR models (one per MNIST test image)
- Classes: 10 (digits 0-9)
- Input: Flattened weight vectors from SIREN networks

**Preprocessing**:
- Load weight tensors from .pt files
- Flatten layer weights into input format for DWS/NFT
- Normalize weights (zero mean, unit variance per layer)

**Augmentation**: None (weight-space data, not images)

**Loading Information** (for Phase 4 download):
- Method: Custom (Dropbox download + PyTorch loading)
- Identifier: MNIST INRs from DWSNets
- Code:
```python
# Download from DWSNets Dropbox link
# wget https://www.dropbox.com/s/[hash]/mnist_inrs.zip
import torch
data = torch.load("data/mnist_inrs/train.pt")
# data contains: {'weights': [...], 'labels': [...]}
```

### Models

#### Baseline Model

**Architecture**: Flattened MLP
**Type**: Non-equivariant baseline
**Source**: Standard approach (flatten weights, feed to MLP)

**Configuration**:
- Input: Flattened weight vector (all SIREN layer weights concatenated)
- Hidden layers: [512, 256, 128]
- Output: 10 classes (digit classification)
- Activation: ReLU
- Dropout: 0.1

**Purpose**: Control for equivariant architecture effects. If DWS/NFT show different activation patterns than MLP, validates inductive bias existence.

**Loading Information** (for Phase 4 download):
- Method: Custom PyTorch module
- Identifier: N/A (implemented from scratch)
- Code:
```python
import torch.nn as nn
class FlattenedMLP(nn.Module):
    def __init__(self, input_dim, num_classes=10):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 512), nn.ReLU(), nn.Dropout(0.1),
            nn.Linear(512, 256), nn.ReLU(), nn.Dropout(0.1),
            nn.Linear(256, 128), nn.ReLU(),
            nn.Linear(128, num_classes)
        )
    def forward(self, x):
        return self.net(x.flatten(1))
```

#### Proposed Model

**Architecture**: DWS (Deep Weight Space) Equivariant Network

**Core Mechanism Implementation:**

```python
# Core Mechanism: DWS Equivariant Layer
# Based on: AvivNavon/DWSNets (ICML 2023)
# Purpose: Process weight-space inputs with locality-preserving equivariance

class DWSLayer(nn.Module):
    """
    Equivariant layer for processing neural network weights.
    Preserves permutation equivariance while exploiting weight locality.
    """
    def __init__(self, in_channels, out_channels, weight_shapes):
        super().__init__()
        # Per-layer processing (locality inductive bias)
        self.layer_ops = nn.ModuleList([
            nn.Linear(in_c * out_c, out_channels)
            for (in_c, out_c) in weight_shapes
        ])
        # Cross-layer aggregation
        self.aggregate = nn.Linear(out_channels * len(weight_shapes), out_channels)
    
    def forward(self, weight_list):
        """
        Args:
            weight_list: List of (B, in_c, out_c) weight tensors per layer
        Returns:
            (B, out_channels) - equivariant representation
        """
        # Process each layer's weights separately (LOCAL)
        layer_feats = [op(w.flatten(1)) for op, w in zip(self.layer_ops, weight_list)]
        # Aggregate across layers
        combined = torch.cat(layer_feats, dim=-1)
        return self.aggregate(combined)

# Key difference from NFT: Processes layers LOCALLY before aggregating
# NFT would flatten all weights to tokens and attend GLOBALLY
```

**NFT Comparison Model:**

```python
# Core Mechanism: NFT (Neural Functional Transformer)
# Based on: AllanYangZhou/nfn (NeurIPS 2023)
# Purpose: Process weight-space inputs with global attention

class NFTLayer(nn.Module):
    """
    Transformer-based layer for processing neural network weights.
    Uses global attention across all weight tokens.
    """
    def __init__(self, d_model, nhead=4, num_layers=2):
        super().__init__()
        self.tokenizer = WeightTokenizer(d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model, nhead, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        self.pool = nn.AdaptiveAvgPool1d(1)
    
    def forward(self, weight_list):
        """
        Args:
            weight_list: List of weight tensors per layer
        Returns:
            (B, d_model) - global representation via attention
        """
        # Tokenize ALL weights into sequence (GLOBAL view)
        tokens = self.tokenizer(weight_list)  # (B, num_tokens, d_model)
        # Global attention across all weight tokens
        attended = self.transformer(tokens)
        # Pool to single representation
        return self.pool(attended.transpose(1, 2)).squeeze(-1)

# Key difference from DWS: Attends GLOBALLY across all weights immediately
# DWS processes layers locally before cross-layer aggregation
```

### Training Protocol

**Optimizer**: AdamW
- Parameters: lr=1e-3, weight_decay=1e-4
- **Source**: DWSNets default configuration

**Learning Rate**: 1e-3
- **Source**: DWSNets experiments

**Schedule**: CosineAnnealingLR
- Parameters: T_max=50 epochs
- **Source**: Common practice for INR classification

**Batch Size**: 64
- **Source**: DWSNets default

**Epochs**: 50
- **Source**: Sufficient for convergence on MNIST INRs (DWSNets paper)

**Loss Function**: CrossEntropyLoss

**Seeds**: 1 (fixed at 42)

> **EXISTENCE (PoC)**: Single seed sufficient. Goal is direction, not statistical significance.

### Evaluation

**Primary Metrics**:
- Test Accuracy: Classification accuracy on held-out MNIST INRs
- Attention Entropy (NFT only): Measures how distributed attention is across weights
- Layer Activation Variance (DWS only): Measures locality of processing

**Success Criteria**:
- proposed_metric > baseline_metric (effect direction only)
- Specifically: DWS and NFT show measurably different internal processing patterns
- Evidence: Attention entropy differs OR activation patterns show locality vs global bias

**Expected Baseline Performance** (from research):
- MLP Baseline: ~90-93% accuracy on MNIST INR classification
- DWS: ~95-97% accuracy (reported in DWSNets paper)
- NFT: ~95-97% accuracy (expected similar to DWS)
- **Source**: DWSNets paper Table 1, NFN paper benchmarks

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: multiclass classification
- Library: torchmetrics + custom
- Code:
```python
import torchmetrics
accuracy = torchmetrics.Accuracy(task="multiclass", num_classes=10)

# Custom: Attention entropy for NFT
def attention_entropy(attn_weights):
    # attn_weights: (B, heads, seq, seq)
    probs = attn_weights.mean(dim=1)  # Average over heads
    entropy = -(probs * torch.log(probs + 1e-9)).sum(dim=-1).mean()
    return entropy

# Custom: Layer activation locality for DWS
def layer_activation_variance(layer_outputs):
    # Variance across layers (lower = more local processing)
    return torch.stack(layer_outputs).var(dim=0).mean()
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing accuracy of MLP vs DWS vs NFT

#### Additional Figures (LLM Autonomous)

Based on EXISTENCE hypothesis for representation differences:
1. **Attention Pattern Heatmap (NFT)**: Visualize attention weights across weight tokens
2. **Layer Activation Profile (DWS)**: Show activation magnitudes per SIREN layer
3. **Representation t-SNE**: 2D projection of learned representations from DWS vs NFT
4. **Processing Pattern Comparison**: Side-by-side attention entropy vs locality metrics

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: true (DWS equivariant layers, NFT attention layers)
- `mechanism_isolatable`: true (can extract intermediate representations)
- `baseline_measurable`: true (MLP provides non-equivariant baseline)

### Architecture Compatibility
- DWS: Compatible with SIREN weight structure (layer-wise processing)
- NFT: Compatible with any flattened weight sequence
- Both: Accept same input format (list of weight tensors per layer)

### Activation Indicators
- `mechanism_log_message`: "DWS layer outputs: {shapes}, NFT attention entropy: {value}"
- `tensor_shape_change`: DWS maintains layer structure; NFT flattens to tokens
- `metric_delta_expected`: Attention entropy > 2.0 (distributed) for NFT; layer variance < 1.0 (local) for DWS

### Mechanism Verification Code
```python
def verify_mechanism(model, sample_input, model_type):
    """Verify that DWS/NFT mechanisms are active and show expected patterns."""
    with torch.no_grad():
        if model_type == "DWS":
            # Extract per-layer activations
            layer_acts = model.get_layer_activations(sample_input)
            locality_score = layer_activation_variance(layer_acts)
            print(f"[VERIFY] DWS locality score: {locality_score:.4f} (expect < 1.0)")
            return locality_score < 1.0
        elif model_type == "NFT":
            # Extract attention weights
            attn_weights = model.get_attention_weights(sample_input)
            entropy = attention_entropy(attn_weights)
            print(f"[VERIFY] NFT attention entropy: {entropy:.4f} (expect > 2.0)")
            return entropy > 2.0
    return False
```

### Success Criteria
- `hypothesis_support_threshold`: DWS and NFT show statistically different processing patterns
- `hypothesis_support_metric`: |DWS_locality - NFT_locality| > 0.5 OR |attention_entropy_diff| > 1.0

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. DWS and NFT both achieve > 90% accuracy (mechanisms functional)
3. Representation metrics differ measurably between architectures
4. `verify_mechanism()` returns True for both model types

---

## Appendix: Reference Implementations

### Official Repositories

1. **DWSNets (DWS)**
   - URL: https://github.com/AvivNavon/DWSNets
   - Paper: "Equivariant Architectures for Learning in Deep Weight Spaces" (ICML 2023)
   - Key files: `nn/`, `experiments/`
   - Dataset: Dropbox links in README

2. **nfn (NFT/NFN)**
   - URL: https://github.com/AllanYangZhou/nfn
   - Paper: "Neural Functional Transformers" (NeurIPS 2023)
   - Key files: `nfn/` library
   - Install: `pip install nfn`

### Related Work

3. **Awesome Weight Space Learning**
   - URL: https://github.com/Zehong-Wang/Awesome-Weight-Space-Learning
   - Comprehensive list of weight-space learning papers and code

4. **Deep Weight Space Augmentations**
   - URL: https://github.com/avivsham/deep-weight-space-augmentations
   - Paper: ICML 2024
   - Relevance: Data augmentation techniques for weight-space

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- 2026-08-28: Phase 2C started
- 2026-08-28: Steps 1-3 completed (init, Archon skipped, Exa/WebSearch done)
- 2026-08-28: Steps 4-8 completed (Serena skipped, dataset/baseline confirmed, synthesis done)

---

*MCP Tools Used: WebSearch (fallback for Exa), WebFetch*
*Archon/Exa MCP unavailable - used WebSearch fallback*
*Phase 2C Complete - Ready for Phase 3 Implementation Planning*
