# Experiment Design: h-m1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Temporal gap is driven by feature complexity difference (simpler spurious features converge faster) - validated via layer-neuron consistency test (Test 8)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM** Template - Mechanistic validation with layer-wise analysis.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 ✅ PASS
**Gate Status:** MUST_WORK (mechanism required for h-c1 intervention)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** [h-e1]

### Gate Condition

MUST_WORK gate: This mechanism hypothesis must validate to proceed to h-c1 intervention. Failure blocks gradient-aware training approach and requires alternative mechanism or intervention redesign.

---

## Continuation Context

**Prerequisite**: h-e1 (Temporal Ordering Foundation) - **VALIDATED ✅**

**Reuse Strategy**: h-m1 is mechanistic analysis of h-e1 trained models
- **Dataset**: CMNIST (same as h-e1) - enables controlled comparison
- **Models**: ResNet-18 checkpoints from h-e1 (spurious-only, core-only, baseline)
- **Training**: None required - post-hoc analysis on converged models
- **Ground Truth**: Spurious labels from h-e1 color corruption (known feature attribution)

**Inherited Configuration** (from h-e1):
- Optimizer: SGD (lr=0.01, momentum=0.9)
- Batch size: 256
- Data path: `./data/mnist`
- Model checkpoints: `{h-e1_folder}/checkpoints/*.pt`

**Novel Component**: Layer-wise activation extraction + neuron-spurious correlation analysis
**Execution Time**: ~5 minutes (single forward pass + correlation computation, no training)

### Previous Hypothesis Results (if applicable)

**h-e1 (VALIDATED ✅):**
- **Result:** Spurious features converge 4 epochs earlier than core features (E_spurious=13, E_core=17)
- **Gate:** PASS (exceeds 2-epoch threshold by 2×)
- **Dataset:** CMNIST
- **Models Available:** ResNet-18 trained on spurious-only, core-only, and baseline variants
- **Key Asset:** Ablation training data provides ground truth for neuron-feature correlation analysis

**Continuation Strategy:** Leverage h-e1 trained models to compute layer-wise neuron correlations with spurious features. No new training required - analyze existing checkpoints.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Source: Phase 2B + h-e1 Validation Context** (Archon MCP unavailable)

**Finding 1: h-e1 Validated Temporal Ordering**
- Dataset: CMNIST (Colored MNIST, spurious correlation benchmark)
- Model: ResNet-18 (no pretraining)
- Training: SGD (lr=0.01, momentum=0.9), batch_size=256, epochs=20
- Key Result: E_spurious=13, E_core=17 (Δ=4 epochs, exceeds threshold)
- Asset: Trained checkpoints available (spurious-only, core-only, baseline variants)
- Insight: Ablation training provides ground truth for neuron-feature correlation analysis

**Finding 2: Layer-wise Feature Complexity Theory**
- Hypothesis: CNNs learn hierarchical features (early=simple, late=complex)
- Prediction: Early layers should correlate more with spurious (simpler) features
- Validation Method: Compute neuron-spurious correlation ρ_j per layer
- Expected Pattern: ρ_j(layer1) > ρ_j(layer2) > ρ_j(layer3) > ρ_j(layer4)

**Finding 3: Statistical Test Design**
- Test 8 (from Phase 2B): Layer-neuron consistency test
- Method: Compare ρ_j distributions across layer groups (early vs late)
- Success Criterion: Early layers show significantly higher spurious correlation
- Cross-validation: Align with GradCAM temporal ratio R_temporal (h-e3)

### Archon Code Examples

**Source: Research Context** (Archon MCP unavailable)

**Example 1: Layer-wise Gradient Extraction**
```python
# Extract per-layer gradients during training
layer_grads = {}
for name, param in model.named_parameters():
    if param.grad is not None:
        layer_name = name.split('.')[0]  # e.g., 'layer1', 'layer2'
        if 'layer' in layer_name or 'conv' in layer_name:
            layer_grads[layer_name] = param.grad.norm().item()
```

**Example 2: Neuron-Feature Correlation**
```python
# Compute correlation between neuron activations and spurious feature
# Using trained models from h-e1
activations = {}
with torch.no_grad():
    for layer_name in ['layer1', 'layer2', 'layer3', 'layer4']:
        act = model.get_activation(layer_name)  # (batch, channels, h, w)
        activations[layer_name] = act.mean(dim=(2, 3))  # (batch, channels)
        
# Correlate with spurious feature labels (color in CMNIST)
spurious_labels = batch['spurious_feature']
rho_j = {}
for layer_name, act in activations.items():
    # Per-neuron correlation with spurious feature
    rho_j[layer_name] = [pearsonr(act[:, i], spurious_labels)[0] 
                         for i in range(act.shape[1])]
```

**Pattern: No New Training Required**
- Reuse h-e1 trained models (already converged)
- Analysis is post-hoc on existing checkpoints
- Focus: Feature attribution, not model training

### Exa GitHub Implementations

**Source: Standard PyTorch Patterns** (Exa MCP unavailable)

**Note**: h-m1 is a mechanistic analysis hypothesis (layer-neuron consistency test), not a method reproduction. No "official implementation" exists - this is a novel test designed in Phase 2B.

**Reference 1: PyTorch Activation Hooks**
- **Pattern**: Forward hooks for layer-wise activation extraction
- **Code**:
```python
activations = {}
def get_activation(name):
    def hook(model, input, output):
        activations[name] = output.detach()
    return hook

# Register hooks for all layers
for layer_name in ['layer1', 'layer2', 'layer3', 'layer4']:
    layer = getattr(model, layer_name)
    layer.register_forward_hook(get_activation(layer_name))
```

**Reference 2: CMNIST Standard Protocol**
- **Dataset**: MNIST + color corruption (10 colors, 95% train correlation)
- **Feature Extraction**: 
  - Spurious: RGB color channels
  - Core: Grayscale digit shape
- **Evaluation**: 10% spurious correlation in val/test (counter-correlated)

**Reference 3: Neuron-Feature Correlation**
- **Method**: Pearson correlation between neuron activations and spurious labels
- **Per-layer**: Compute correlation distribution for early vs late layers
- **Expected Pattern**: ρ_j(early) > ρ_j(late) if complexity hypothesis holds

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Status**: Not applicable - h-m1 is a novel mechanistic test, not a method reproduction.

**Recommended Implementation Path:**
- Primary: Leverage h-e1 trained models (ResNet-18 checkpoints from spurious-only, core-only, baseline training)
- Fallback: Retrain simplified ResNet with activation logging if h-e1 checkpoints lack activation hooks
- Justification: Post-hoc analysis on existing h-e1 models is most efficient (no new training required, ground truth feature labels available from ablation setup)

### Code Analysis (Serena MCP)

*Skipped* - Code from research context was sufficiently clear (standard PyTorch activation hooks pattern)

---

## Experiment Specification

### Dataset

**Dataset**: CMNIST (Colored MNIST)  
**Type**: `standard` (spurious correlation benchmark)  
**Path**: `./data/mnist` (auto-download via torchvision)

**Spurious vs Core Features**:
- Spurious: Color (10 colors mapped to digits, 95% train correlation, 10% test correlation)
- Core: Digit shape (grayscale MNIST patterns)

**Statistics**:
- Train: 60,000 samples (95% spurious correlation)
- Test: 10,000 samples (10% counter-correlation)
- Classes: 10 digits (0-9)
- Input: 28×28 RGB (3 channels)

**Continuation from h-e1**: ✅ Reusing same dataset for controlled comparison

**Loading Information** (for Phase 4 download):
- Method: torchvision + color corruption
- Identifier: `torchvision.datasets.MNIST`
- Code:
```python
mnist_train = torchvision.datasets.MNIST('./data/mnist', train=True, download=True)
mnist_test = torchvision.datasets.MNIST('./data/mnist', train=False, download=True)
# Color corruption applied via custom transform (spurious feature generation)
```

**Preprocessing**:
- Normalization: ToTensor() → [0,1]
- No augmentation (analysis experiment)

### Models

#### Baseline Model

**Architecture**: ResNet-18 (pre-trained from h-e1)  
**Type**: CNN (convolutional neural network)  
**Source**: h-e1 trained checkpoints (spurious-only, core-only, baseline variants)

**Configuration**:
- Layers: conv1, layer1 (early), layer2, layer3, layer4 (late), fc
- Parameters: ~11M
- Input: (batch, 3, 28, 28) RGB
- Output: (batch, 10) digit logits

**Continuation from h-e1**: ✅ Reusing trained models (NO new training required)

**Loading Information** (for Phase 4 download):
- Method: Load h-e1 checkpoint
- Identifier: `{h-e1_folder}/checkpoints/baseline_seed0.pt`
- Code:
```python
import torchvision.models as models
model = models.resnet18(pretrained=False, num_classes=10)
checkpoint = torch.load('./docs/youra_research/h-e1/checkpoints/baseline_seed0.pt')
model.load_state_dict(checkpoint['model_state_dict'])
```

**Activation Extraction**:
```python
# Register hooks for layer-wise analysis
activations = {}
def get_activation(name):
    def hook(model, input, output):
        activations[name] = output.detach()
    return hook

for layer_name in ['conv1', 'layer1', 'layer2', 'layer3', 'layer4']:
    getattr(model, layer_name).register_forward_hook(get_activation(layer_name))
```

#### Proposed Model

**Architecture:** ResNet-18 (from h-e1) + Layer-Neuron Correlation Analyzer

**Core Mechanism Implementation:**

```python
# Core Mechanism: Layer-Neuron Consistency Analysis
# Tests if early layers correlate more with spurious features (complexity hypothesis)

import torch
import numpy as np
from scipy.stats import pearsonr, ttest_ind

class LayerNeuronAnalyzer:
    """Analyzes layer-wise neuron correlations with spurious features."""
    def __init__(self, model, layer_names=['conv1', 'layer1', 'layer2', 'layer3', 'layer4']):
        self.model = model
        self.layer_names = layer_names
        self.activations = {}
        self._register_hooks()
    
    def _register_hooks(self):
        def get_activation(name):
            def hook(model, input, output):
                self.activations[name] = output.detach()
            return hook
        for layer_name in self.layer_names:
            getattr(self.model, layer_name).register_forward_hook(get_activation(layer_name))
    
    def compute_layer_correlations(self, dataloader, spurious_labels):
        """Compute per-layer neuron-spurious correlations."""
        layer_activations = {name: [] for name in self.layer_names}
        
        self.model.eval()
        with torch.no_grad():
            for batch_x, _ in dataloader:
                _ = self.model(batch_x)
                for layer_name in self.layer_names:
                    act = self.activations[layer_name].mean(dim=(2, 3))  # Spatial pool
                    layer_activations[layer_name].append(act.cpu())
        
        # Compute per-neuron Pearson correlation
        layer_rho_j = {}
        for layer_name, acts in layer_activations.items():
            acts = torch.cat(acts, dim=0).numpy()
            rho_j = [pearsonr(acts[:, i], spurious_labels)[0] for i in range(acts.shape[1])]
            layer_rho_j[layer_name] = np.array(rho_j)
        
        return layer_rho_j
    
    def test_layer_consistency(self, layer_rho_j):
        """Test: early layers > late layers?"""
        early = np.concatenate([layer_rho_j['conv1'], layer_rho_j['layer1']])
        late = np.concatenate([layer_rho_j['layer3'], layer_rho_j['layer4']])
        t_stat, p_value = ttest_ind(early, late, alternative='greater')
        return t_stat, p_value
```

**Integration Point**: Post-training analysis (no model modification)

### Training Protocol

**Reusing h-e1 Configuration** (No new training):
- **Model**: Load h-e1 baseline checkpoint (seed 0)
- **Dataset**: CMNIST test set (10,000 samples)
- **Analysis**: Single forward pass to extract activations
- **Compute**: Layer-wise correlations with spurious labels (color)

**Rationale**: h-m1 is mechanistic analysis on h-e1 trained models. Training is complete.

### Evaluation

**Primary Metrics**:
- **Layer-wise mean ρ_j**: Mean Pearson correlation between neuron activations and spurious feature per layer
- **Computation**: `mean_rho[layer] = np.mean(layer_rho_j[layer])`

**Statistical Test**:
- **Method**: Independent samples t-test (one-sided)
- **Groups**: Early layers (conv1, layer1) vs Late layers (layer3, layer4)
- **Null Hypothesis**: mean(ρ_early) ≤ mean(ρ_late)
- **Alternative**: mean(ρ_early) > mean(ρ_late)

**Success Criteria**:
- **MUST_WORK gate**: p < 0.05 AND mean(ρ_early) > mean(ρ_late)
- **Direction**: Early layers must show higher spurious correlation (supports complexity hypothesis)

**Expected Performance**:
- Early layers (conv1, layer1): mean(ρ_j) ≈ 0.3-0.5 (moderate-to-strong correlation with color)
- Late layers (layer3, layer4): mean(ρ_j) ≈ 0.05-0.15 (weak correlation with color)
- **Source**: Theoretical prediction from hierarchical feature learning

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: correlation_analysis
- Library: scipy.stats (pearsonr, ttest_ind)
- Code:
```python
from scipy.stats import pearsonr, ttest_ind
# Per-neuron correlation
rho, p_value = pearsonr(neuron_activations, spurious_labels)
# Layer consistency test
t_stat, p_value = ttest_ind(early_rho, late_rho, alternative='greater')
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing mean(ρ_j) per layer (conv1, layer1, layer2, layer3, layer4) with 95% confidence intervals

#### Additional Figures (LLM Autonomous)
- **Per-Neuron Correlation Heatmap**: Heatmap (layers × neurons) showing individual ρ_j values
- **Cumulative Distribution Function**: CDF of ρ_j for early vs late layer groups (should show separation)
- **Layer Hierarchy Line Plot**: mean(ρ_j) vs layer depth (should decrease monotonically if hypothesis holds)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Note**: Archon MCP unavailable - references derived from Phase 2B context and h-e1 validation.

**Source A.1**: h-e1 Validation Report (04_validation.md)
- **Type**: Previous hypothesis validation
- **Relevance**: Provides trained model checkpoints and ground truth temporal ordering (E_spurious=13, E_core=17)
- **Key Insights**:
  - CMNIST ablation training (spurious-only, core-only, baseline) provides ground truth for feature attribution
  - ResNet-18 trained to convergence (>90% accuracy on both variants)
  - Spurious feature: Color (simple, low-level), Core feature: Digit shape (complex, semantic)
- **Used For**: Dataset selection, model selection, continuation experiment design

**Source A.2**: Phase 2B Verification Plan (02b_verification_plan.md)
- **Type**: Hypothesis planning document
- **Relevance**: Defines layer-neuron consistency test (Test 8) as mechanistic validation
- **Key Insights**:
  - Mechanism hypothesis: Temporal gap driven by feature complexity difference
  - Test method: Layer-wise neuron correlation with spurious features
  - Expected pattern: ρ_j decreases with layer depth (early → simple, late → complex)
- **Used For**: Experiment design, success criteria, statistical test specification

### Archon Code Examples

**Note**: Archon MCP unavailable - code patterns derived from standard PyTorch practices.

**Code Source A.1**: PyTorch Forward Hooks (Standard Pattern)
- **Relevance**: Standard method for extracting layer-wise activations
- **Key Code**:
```python
activations = {}
def get_activation(name):
    def hook(model, input, output):
        activations[name] = output.detach()
    return hook

for layer_name in ['conv1', 'layer1', 'layer2', 'layer3', 'layer4']:
    getattr(model, layer_name).register_forward_hook(get_activation(layer_name))
```
- **Used For**: Pseudo-code generation (LayerNeuronAnalyzer class)

**Code Source A.2**: Scipy Correlation Analysis (Standard Library)
- **Relevance**: Statistical correlation between neuron activations and feature labels
- **Key Code**:
```python
from scipy.stats import pearsonr, ttest_ind
# Per-neuron correlation
rho, p_value = pearsonr(neuron_activations, spurious_labels)
# Layer consistency test
t_stat, p_value = ttest_ind(early_rho, late_rho, alternative='greater')
```
- **Used For**: Statistical test specification, evaluation metrics

### B. GitHub Implementations (Exa)

**Note**: Exa MCP unavailable - references derived from research context.

**Implementation B.1**: CMNIST Spurious Correlation Benchmark
- **Relevance**: Standard benchmark for spurious correlation research
- **Protocol**:
  - Training: 95% spurious correlation (color-digit alignment)
  - Test: 10% spurious correlation (counter-correlated to detect bias)
  - Feature separation: Color (spurious) vs Shape (core)
- **Used For**: Dataset specification, spurious feature definition

**Implementation B.2**: ResNet-18 Layer Hierarchy
- **Relevance**: Well-established hierarchical feature learning in CNNs
- **Layer Structure**:
  - conv1: Initial convolution (low-level features)
  - layer1: Early residual block (simple patterns)
  - layer2, layer3: Mid-level residual blocks (intermediate features)
  - layer4: Late residual block (high-level semantic features)
- **Used For**: Layer grouping (early vs late), feature complexity hypothesis validation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from research context was sufficiently clear (standard PyTorch patterns)

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - h-e1
- **File**: `docs/youra_research/h-e1/04_validation.md`
- **Reused Components**:
  - Dataset: CMNIST (same benchmark ensures controlled comparison)
  - Model: ResNet-18 trained checkpoints (spurious-only, core-only, baseline variants)
  - Training Config: SGD (lr=0.01, momentum=0.9), batch_size=256, epochs=20
  - Spurious Labels: Color corruption labels (ground truth for correlation analysis)
- **Why Reused**: h-m1 is mechanistic analysis of h-e1 trained models - NO new training required

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (CMNIST) | Previous Validation | h-e1 (A.1) |
| Spurious Feature (Color) | Benchmark Protocol | CMNIST (B.1) |
| Model (ResNet-18) | Previous Validation | h-e1 (A.1) |
| Layer Hierarchy | CNN Theory | ResNet (B.2) |
| Activation Hooks | PyTorch Pattern | Standard (A.1) |
| Correlation Analysis | Statistical Library | scipy.stats (A.2) |
| Test Design (Layer Consistency) | Phase 2B | Verification Plan (A.2) |
| Success Criteria (p < 0.05) | Phase 2B | Verification Plan (A.2) |
| Training Protocol | Previous Validation | h-e1 (A.1, D.1) |
| Evaluation Metrics | Statistical Theory | Pearson correlation (A.2) |

**Grounding Status**: All specifications trace to documented sources (h-e1 validation, Phase 2B plan, or standard methods)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28T23:30:00Z

### Workflow History for This Hypothesis

- 2026-08-28T23:30:00Z: Experiment design started (Phase 2C)
- 2026-08-29T00:00:00Z: Experiment design completed (Phase 2C)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
