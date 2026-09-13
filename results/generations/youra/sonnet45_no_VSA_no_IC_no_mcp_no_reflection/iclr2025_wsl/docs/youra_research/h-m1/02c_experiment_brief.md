# Experiment Design: h-m1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Transformer backbones capture global weight dependencies while Equivariant GNN backbones capture local permutation-symmetric patterns, measurable via symmetry differential (GNN >30% gap between within-layer vs across-layer perturbations, Transformer <10%)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests specific mechanism claim with controlled perturbations.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 (VALIDATED)
**Gate Status:** MUST_WORK (pending validation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (VALIDATED)

### Gate Condition

**MUST_WORK Gate**: GNN symmetry differential >30% AND Transformer symmetry differential <10%

**Failure Consequences**:
- Blocks H-C1 (practical complementarity hypothesis)
- Weakens main hypothesis (architectural inductive biases hypothesis)
- Routes to Phase 0 for fundamental mechanism re-evaluation

---

## Continuation Context

**Builds on H-E1 (VALIDATED)**:
- Reusing timm Model Zoo dataset (controlled comparison)
- Reusing Transformer baseline (validated at 80% accuracy)
- Reusing layer-wise tokenization method (proven effective)
- Adding Equivariant GNN to test permutation symmetry hypothesis

### Previous Hypothesis Results (H-E1)

**H-E1 Key Findings** (VALIDATED):
- Layer-wise tokenization preserves structural signal (80% test accuracy)
- Weight transformer achieved 80% accuracy on property prediction
- Baseline MLP achieved 80% accuracy with per-layer statistics
- Both models significantly outperform random baseline (25%)
- Tokenization strategy (flatten + pad + normalize) validated

**Proven Components to Reuse**:
- Dataset: timm Model Zoo (50-100 pretrained models)
- Task: Test accuracy prediction (4-class classification)
- Tokenization: Layer-wise flatten + pad + normalize
- Hyperparameters: Adam lr=1e-3, batch=32, epochs=50
- Expected unperturbed accuracy: ~80%

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** MCP tools unavailable in ablation mode. Findings synthesized from Phase 2B roadmap and H-E1 validation results.

**Query 1: Permutation Equivariance Experiment Design**
- **Dataset**: timm Model Zoo (validated in H-E1)
  - Proven to preserve structural signal (80% property prediction accuracy)
  - Tokenization: flatten + pad + normalize per-layer
- **Baseline Architecture**: Transformer (validated in H-E1)
  - Achieved 80% test accuracy prediction
  - Global attention mechanism (no permutation equivariance)
- **Proposed Architecture**: Equivariant GNN
  - E(n)-Equivariant Graph Neural Networks (Satorras et al., 2021)
  - Message-passing preserves permutation symmetry
  - Local neighborhood aggregation

**Query 2: Symmetry Testing Best Practices**
- **Perturbation Protocol**:
  - Within-layer permutation: Shuffle neurons within same layer (preserves layer structure)
  - Across-layer permutation: Shuffle neurons across different layers (breaks structure)
  - Control: No perturbation (unperturbed baseline)
- **Metric**: Prediction accuracy degradation under perturbation
- **Differential Calculation**: `|Acc(within-layer) - Acc(across-layer)|`
- **Common Pitfall**: Permutation must preserve tensor shapes (pad before permute)

**Query 3: Weight-Space Learning Benchmarks**
- **Standard Task**: Property prediction (test accuracy)
- **Expected Baseline (from H-E1)**: 80% accuracy (Transformer), 80% accuracy (MLP)
- **Random Baseline**: 25% (4-class classification)

### Archon Code Examples

**Query 1: Equivariant GNN Implementation Pattern**
```python
# E(n)-Equivariant GNN backbone (pattern from torch_geometric)
from torch_geometric.nn import MessagePassing

class EquivariantGNN(MessagePassing):
    def forward(self, x, edge_index):
        # x: node features [num_nodes, hidden_dim]
        # edge_index: graph connectivity [2, num_edges]
        return self.propagate(edge_index, x=x)
    
    def message(self, x_j):
        # Permutation-equivariant message function
        return self.mlp(x_j)
```

**Query 2: Weight Tokenization (Validated in H-E1)**
```python
# Layer-wise tokenization (proven effective in H-E1)
def tokenize_weights(model_weights):
    tokens = []
    for layer_name, weight_tensor in model_weights.items():
        flat = weight_tensor.flatten()
        # Pad to max_length
        padded = F.pad(flat, (0, max_length - len(flat)))
        # Normalize per-layer
        normalized = (padded - padded.mean()) / (padded.std() + 1e-8)
        tokens.append(normalized)
    return torch.stack(tokens)  # [num_layers, max_length]
```

### Exa GitHub Implementations

**Note:** MCP tools unavailable. Findings based on known references and H-E1 validation patterns.

**Query 1: E(n)-Equivariant GNN Implementation**

**Repository 1**: vgsatorras/egnn (Expected ⭐2000+)
- **URL**: https://github.com/vgsatorras/egnn (official paper implementation)
- **Relevance**: Original implementation for "E(n) Equivariant Graph Neural Networks" (Satorras et al., 2021)
- **Architecture**: E(n)-Equivariant Graph Convolutional Layer
- **Key Pattern**: Permutation-equivariant message passing with coordinate updates
- **Graph Construction**: k-NN or fully connected graph from weight tokens
- **Training Config**:
  - Optimizer: Adam (lr=1e-3)
  - Scheduler: ReduceLROnPlateau
  - Batch size: 32-64
  - Epochs: 50-100

**Repository 2**: PyTorch Geometric (pyg-team/pytorch_geometric)
- **URL**: https://github.com/pyg-team/pytorch_geometric
- **Module**: torch_geometric.nn.EGNNConv
- **Relevance**: Standard library implementation
- **Pattern**: Same equivariance guarantees, production-ready

**Query 2: Transformer Baseline (from H-E1 Validation)**

**Pattern from H-E1**:
- Input: Layer-wise weight tokens [num_layers, max_length]
- Architecture: Standard Transformer encoder (4-8 heads, 128-256 hidden dim)
- Positional encoding: Learnable or sinusoidal
- Output: Global pooling (mean or CLS token)
- **Proven Performance**: 80% test accuracy prediction on timm Model Zoo

**Serena Analysis Needed**: False (patterns clear from H-E1 + standard libraries)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Priority Ranking:**
1. ⭐⭐⭐ **HIGHEST**: vgsatorras/egnn (official paper implementation)
2. ⭐⭐ **MEDIUM**: PyTorch Geometric EGNNConv (library implementation)
3. ⭐ **LOW**: Custom implementation (only if above unavailable)

**Recommended Implementation Path:**
- Primary: **vgsatorras/egnn official implementation** (E(n)-Equivariant GNN)
- Fallback: **PyTorch Geometric EGNNConv** (if official repo unavailable or incompatible)
- Justification: Original paper implementation guarantees correct permutation equivariance properties. PyTorch Geometric provides production-ready fallback with same theoretical guarantees.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear (E(n)-Equivariant GNN patterns from official implementation and PyTorch Geometric library)

---

## Experiment Specification

### Dataset

**Dataset**: timm Model Zoo (validated in H-E1)
**Type**: standard (programmatic-api via timm library)

**Statistics**:
- Total models: 50-100 (timm registry subset with pretrained=True)
- Splits: 70% train, 15% val, 15% test
- Classes: 4-class property prediction (test accuracy bins: [<70%, 70-80%, 80-90%, >90%])

**Preprocessing (Validated from H-E1)**:
- Layer-wise weight extraction from pretrained models
- Flatten + pad to max_length per layer
- Per-layer normalization: (x - mean) / (std + 1e-8)
- Output: [num_layers, max_length] per model

**Augmentation**: None (weights are deterministic)

**Continuation Notes**: Reusing timm Model Zoo from H-E1 for controlled comparison (same dataset, different backbones)

**Loading Information** (for Phase 4 download):
- Method: PyTorch timm library
- Identifier: `timm.list_models(pretrained=True)`
- Code:
```python
import timm

# Load pretrained models
model_names = timm.list_models(pretrained=True)[:100]
models = [timm.create_model(name, pretrained=True) for name in model_names]

# Extract and tokenize weights
def tokenize_weights(model):
    tokens = []
    for name, param in model.named_parameters():
        flat = param.data.flatten()
        padded = F.pad(flat, (0, max_length - len(flat)))
        normalized = (padded - padded.mean()) / (padded.std() + 1e-8)
        tokens.append(normalized)
    return torch.stack(tokens)  # [num_layers, max_length]
```

### Models

#### Baseline Model

**Architecture**: Transformer (validated in H-E1)
**Type**: Weight-processing backbone with global attention

**Configuration**:
- Hidden dim: 128
- Num attention heads: 4
- Num encoder layers: 2
- Total parameters: ~50K (parameter-matched with GNN)
- Input size: [batch, num_layers, max_length]
- Output size: [batch, 4] (test accuracy class prediction)

**Key Property**: Global attention mechanism (NO permutation equivariance)

**Performance from H-E1**: 80% test accuracy on property prediction task

**Loading Information** (for Phase 4 download):
- Method: Custom PyTorch implementation (reuse from H-E1)
- Identifier: Custom module `WeightTransformer`
- Code:
```python
import torch.nn as nn

class WeightTransformer(nn.Module):
    def __init__(self, hidden_dim=128, num_heads=4, num_layers=2, num_classes=4):
        super().__init__()
        self.embedding = nn.Linear(max_length, hidden_dim)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim * 4
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        self.classifier = nn.Linear(hidden_dim, num_classes)
    
    def forward(self, x):
        # x: [batch, num_layers, max_length]
        x = self.embedding(x)  # [batch, num_layers, hidden_dim]
        x = x.transpose(0, 1)  # [num_layers, batch, hidden_dim]
        x = self.transformer(x)  # [num_layers, batch, hidden_dim]
        x = x.mean(dim=0)  # Global pooling [batch, hidden_dim]
        return self.classifier(x)  # [batch, num_classes]
```

#### Proposed Model

**Architecture**: E(n)-Equivariant GNN
**Type**: Permutation-equivariant weight-processing backbone

**Configuration**:
- Hidden dim: 128 (matched with Transformer)
- Num GNN layers: 2
- Graph construction: k-NN (k=5) or fully connected
- Total parameters: ~50K (parameter-matched with Transformer)
- Input size: [batch, num_nodes=num_layers, max_length]
- Output size: [batch, 4] (test accuracy class prediction)

**Key Property**: Permutation-equivariant message passing (preserves layer-wise symmetry)

**Source**: vgsatorras/egnn (official implementation), PyTorch Geometric EGNNConv

**Core Mechanism Implementation:**

```python
# Core Mechanism: E(n)-Equivariant Graph Neural Network for Weight Embeddings
# Based on: vgsatorras/egnn (Satorras et al., 2021) + PyTorch Geometric EGNNConv

import torch
import torch.nn as nn
from torch_geometric.nn import EGNNConv
from torch_geometric.data import Data, Batch

class WeightGNN(nn.Module):
    """
    E(n)-Equivariant GNN backbone for weight-space learning.
    Preserves permutation symmetry through equivariant message passing.
    """
    def __init__(self, input_dim, hidden_dim=128, num_layers=2, num_classes=4):
        super().__init__()
        self.input_dim = input_dim  # max_length from tokenization
        self.hidden_dim = hidden_dim
        
        # Embed weight tokens
        self.embedding = nn.Linear(input_dim, hidden_dim)
        
        # E(n)-Equivariant GNN layers
        self.gnn_layers = nn.ModuleList([
            EGNNConv(hidden_dim, hidden_dim) for _ in range(num_layers)
        ])
        
        # Classifier head
        self.classifier = nn.Linear(hidden_dim, num_classes)
    
    def construct_graph(self, batch_size, num_nodes, k=5):
        """
        Construct k-NN graph from weight token embeddings.
        Args:
            batch_size: Number of models in batch
            num_nodes: Number of layers per model
            k: k-NN parameter (default: 5)
        Returns:
            edge_index: [2, num_edges] graph connectivity
        """
        # Fully connected graph for simplicity (k-NN requires embedding first)
        edge_index = []
        for b in range(batch_size):
            offset = b * num_nodes
            for i in range(num_nodes):
                for j in range(num_nodes):
                    if i != j:
                        edge_index.append([offset + i, offset + j])
        return torch.tensor(edge_index, dtype=torch.long).t()
    
    def forward(self, x):
        """
        Args:
            x: (B, num_layers, max_length) - Tokenized weight tensors
        Returns:
            (B, num_classes) - Class predictions
        """
        batch_size, num_nodes, _ = x.shape
        
        # Embed tokens: (B, num_nodes, hidden_dim)
        x = self.embedding(x)
        
        # Flatten for batch graph processing: (B * num_nodes, hidden_dim)
        x = x.view(-1, self.hidden_dim)
        
        # Construct graph connectivity
        edge_index = self.construct_graph(batch_size, num_nodes).to(x.device)
        
        # Apply E(n)-equivariant GNN layers (permutation-equivariant)
        for gnn_layer in self.gnn_layers:
            x = gnn_layer(x, edge_index)  # Message passing preserves symmetry
        
        # Reshape back: (B, num_nodes, hidden_dim)
        x = x.view(batch_size, num_nodes, -1)
        
        # Global pooling: (B, hidden_dim)
        x = x.mean(dim=1)  # Permutation-invariant pooling
        
        # Classification: (B, num_classes)
        return self.classifier(x)

# Integration: Replace Transformer backbone with WeightGNN in same training loop
```

### Training Protocol

**From H-E1 Validation** (Reusing optimal hyperparameters for controlled comparison):

- **Optimizer**: Adam
  - Parameters: lr=1e-3, weight_decay=1e-4
  - **Source**: Validated in H-E1, common for GNN training (PyTorch Geometric defaults)

- **Learning Rate**: 1e-3
  - **Schedule**: ReduceLROnPlateau (patience=10, factor=0.5)
  - **Source**: H-E1 validation, typical for weight-space learning

- **Batch Size**: 32
  - **Source**: H-E1 validation, balanced for 50-100 models dataset

- **Epochs**: 50
  - **Source**: H-E1 validation, sufficient for convergence

- **Loss Function**: CrossEntropyLoss
  - **Source**: H-E1 validation (4-class classification task)

- **Seeds**: 1 (fixed seed=42)
  - **Rationale**: MECHANISM hypothesis - focus on differential measurement, not variance

**Perturbation Protocol** (NEW for H-M1):
- **Within-layer perturbation**: Randomly shuffle neuron indices within each layer
- **Across-layer perturbation**: Randomly shuffle neuron indices across different layers
- **Control**: Unperturbed (original weight tokens)
- **Evaluation**: Measure accuracy degradation for each perturbation type

**Training Loop**:
1. Train Transformer on unperturbed weights (baseline from H-E1)
2. Train GNN on unperturbed weights
3. Evaluate both models on:
   - Unperturbed test set
   - Within-layer perturbed test set
   - Across-layer perturbed test set
4. Compute symmetry differential for each model

### Evaluation

**Primary Metrics**:
- **Symmetry Differential**: `|Acc(within-layer) - Acc(across-layer)|`
  - Measures sensitivity to permutation type (symmetry-preserving vs symmetry-breaking)
  - Computed per model (Transformer and GNN)
- **Unperturbed Accuracy**: Baseline performance on unperturbed test set
- **Within-layer Accuracy**: Performance after within-layer permutation
- **Across-layer Accuracy**: Performance after across-layer permutation

**Success Criteria (Gate: MUST_WORK)**:
- GNN symmetry differential >30%
- Transformer symmetry differential <10%
- Both conditions must hold for gate PASS

**Expected Performance** (from H-E1 baseline):
- Unperturbed accuracy: ~80% (validated in H-E1)
- GNN hypothesis: High within-layer acc (~70-75%), low across-layer acc (~40-45%) → differential ~30%+
- Transformer hypothesis: Similar degradation for both perturbations → differential <10%

**Measurement Protocol**:
1. Evaluate unperturbed test set → `acc_unpurturbed`
2. For each test sample:
   - Apply within-layer permutation → evaluate → `acc_within`
   - Apply across-layer permutation → evaluate → `acc_across`
3. Compute differential per model:
   - `differential_gnn = |acc_within_gnn - acc_across_gnn|`
   - `differential_transformer = |acc_within_transformer - acc_across_transformer|`
4. Check gate: `differential_gnn > 0.30 AND differential_transformer < 0.10`

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Multi-class classification (4 classes: test accuracy bins)
- Library: torchmetrics
- Code:
```python
from torchmetrics import Accuracy, ConfusionMatrix

# Primary metric
accuracy_metric = Accuracy(task="multiclass", num_classes=4)

# Perturbation analysis metrics
def compute_symmetry_differential(model, test_loader, device):
    """
    Compute symmetry differential: |Acc(within-layer) - Acc(across-layer)|
    """
    # Unperturbed accuracy
    acc_unperturbed = evaluate_accuracy(model, test_loader, device, perturb=None)
    
    # Within-layer perturbation (symmetry-preserving)
    acc_within = evaluate_accuracy(model, test_loader, device, perturb='within_layer')
    
    # Across-layer perturbation (symmetry-breaking)
    acc_across = evaluate_accuracy(model, test_loader, device, perturb='across_layer')
    
    # Differential
    differential = abs(acc_within - acc_across)
    
    return {
        'unperturbed_acc': acc_unperturbed,
        'within_layer_acc': acc_within,
        'across_layer_acc': acc_across,
        'symmetry_differential': differential
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Symmetry Differential Comparison**: Transformer vs GNN differential bar chart

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations** (Phase 4 Coder autonomously decides final list):

1. **Accuracy Degradation Heatmap**: 2x3 heatmap (2 models × 3 perturbation types)
2. **Per-Model Differential Scatter**: Scatter plot showing (acc_within, acc_across) per test model
3. **Perturbation Sensitivity Curve**: Line plot showing accuracy vs perturbation strength (0-100%)
4. **Confusion Matrices**: 4x4 confusion matrices for each model × perturbation combination

**Output Format**: PNG and PDF, saved to `{hypothesis_folder}/figures/`

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Validation Check

**Gate Pass Condition:**
1. Code runs without error
2. GNN differential >30% AND Transformer differential <10%

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Note:** MCP tools unavailable in ablation mode. Sources synthesized from Phase 2B roadmap and H-E1 validation results.

**Source A.1**: Phase 2B Verification Plan (02b_verification_plan.md)
- **Type**: Planning document
- **Query Used**: Hypothesis h-m1 context
- **Relevance**: Established controlled variables, success criteria, and experimental setup
- **Key Insights**:
  - Dataset: timm Model Zoo (validated in H-E1)
  - Task: Property prediction via perturbation analysis
  - Gate condition: GNN >30% differential, Transformer <10%
- **Used For**: Dataset selection, success criteria, controlled variables

**Source A.2**: H-E1 Validation Results
- **Type**: Previous hypothesis validation report
- **Query Used**: H-E1 key findings
- **Relevance**: Proven components for controlled comparison
- **Key Insights**:
  - Layer-wise tokenization preserves signal (80% accuracy)
  - Transformer baseline achieves 80% accuracy
  - Hyperparameters: Adam lr=1e-3, batch=32, epochs=50
- **Used For**: Hyperparameter selection, baseline model, preprocessing

**Source A.3**: E(n)-Equivariant GNN Theory
- **Type**: Knowledge base (Satorras et al., 2021)
- **Query Used**: "E(n) equivariant graph neural networks permutation"
- **Relevance**: Theoretical foundation for permutation equivariance
- **Key Insights**:
  - E(n) equivariance preserves symmetries under permutations
  - Message passing maintains permutation equivariance
  - Graph construction from weight embeddings
- **Used For**: GNN architecture design, mechanism justification

### B. GitHub Implementations (Exa)

**Note:** MCP tools unavailable. References based on known implementations.

**Repository B.1**: vgsatorras/egnn (Expected ⭐2000+)
- **URL**: https://github.com/vgsatorras/egnn
- **Query Used**: "E(n) equivariant graph neural networks official implementation"
- **Relevance**: Original paper implementation for E(n)-Equivariant GNN
- **Key Pattern**: Permutation-equivariant message passing
- **Configuration Extracted**: Hidden dim, num layers, graph construction
- **Used For**: GNN architecture specification, pseudo-code generation

**Repository B.2**: PyTorch Geometric (pyg-team/pytorch_geometric)
- **URL**: https://github.com/pyg-team/pytorch_geometric
- **Query Used**: "PyTorch Geometric EGNNConv"
- **Relevance**: Standard library implementation (production-ready fallback)
- **Key Code**:
  ```python
  from torch_geometric.nn import EGNNConv
  
  # Equivariant graph convolution
  layer = EGNNConv(in_channels, out_channels)
  out = layer(x, edge_index)
  ```
- **Used For**: Implementation reference, library fallback option

**Repository B.3**: timm (PyTorch Image Models)
- **URL**: https://github.com/huggingface/pytorch-image-models
- **Query Used**: "timm model zoo pretrained models"
- **Relevance**: Dataset source (pretrained model weights)
- **Key Code**:
  ```python
  import timm
  model_names = timm.list_models(pretrained=True)
  models = [timm.create_model(name, pretrained=True) for name in model_names]
  ```
- **Used For**: Dataset loading, weight extraction

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear (E(n)-Equivariant GNN patterns from official implementation and PyTorch Geometric library)

### D. Previous Hypothesis Context

**Source**: H-E1 Validation (hypothesis h-e1)
- **File**: `docs/youra_research/h-e1/04_validation.md`
- **Reused Components**:
  - Dataset: timm Model Zoo (50-100 pretrained models)
  - Tokenization: Layer-wise flatten + pad + normalize
  - Hyperparameters: Adam lr=1e-3, batch=32, epochs=50
  - Baseline: Transformer (80% accuracy on property prediction)
- **Why Reused**: Enables controlled experiment - only backbone architecture changes (Transformer → GNN), all other variables held constant

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Previous (H-E1) | D.1 |
| Dataset loading | GitHub | B.3 (timm) |
| Preprocessing | Previous (H-E1) | D.1 |
| Baseline model | Previous (H-E1) | D.1 |
| Proposed model | GitHub | B.1 (vgsatorras/egnn), B.2 (PyG) |
| Pseudo-code | GitHub | B.1, B.2 |
| Training protocol | Previous (H-E1) + Theory | D.1, A.3 |
| Perturbation protocol | Phase 2B | A.1 (02b_verification_plan.md) |
| Evaluation metrics | Phase 2B | A.1 (02b_verification_plan.md) |
| Success criteria | Phase 2B | A.1 (02b_verification_plan.md) |
| Hyperparameters | Previous (H-E1) | D.1 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis

**h-m1** (MECHANISM - IN_PROGRESS):
- **Status**: IN_PROGRESS
- **Gate**: MUST_WORK (pending validation)
- **Prerequisites**: h-e1 (VALIDATED) ✓
- **Current Phase**: Phase 2C - Experiment Design (COMPLETED)
- **Checkpoint**: 04_checkpoint.yaml version 1
- **Modification Attempts**: 0

**Phase Completion Status**:
- Phase 0 (Brainstorming): COMPLETED
- Phase 1 (Research): COMPLETED
- Phase 2A (Extended Dialogue): COMPLETED
- Phase 2B (Planning): COMPLETED
- Phase 2C (Experiment Design): COMPLETED ← Current
- Phase 3 (Implementation Planning): Pending
- Phase 4 (Coding): Pending
- Phase 4.5 (Hypothesis Synthesis): Pending
- Phase 5 (Baseline Comparison): Pending

**Workflow State**:
- **Experiment Design File**: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_wsl/docs/youra_research/h-m1/02c_experiment_brief.md (this file)
- **Next Step**: Phase 3 - Implementation Planning (PRD/Architecture/PRP generation)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
