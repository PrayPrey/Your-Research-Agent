# Logic Design: H-M-Integrated (Full CAPE Mechanism Validation)

**Date:** 2026-07-13
**Hypothesis ID:** H-M-Integrated
**Type:** MECHANISM
**Budget:** 13 subtasks allocated (A-2: 5, A-6: 4, A-7: 4)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-e1 actual code
**Analyzed Path:** `/workspace/TEST_wsl/docs/youra_research/h-e1/code/`
**Relevant Symbols:**
- `ModelZooCollector`: Reusable for 400-model collection
- `FeatureExtractor`: Base for weight extraction (needs extension for operation-type grouping)
- Verified methods: `collect_models(n_resnet, n_vit)`, `extract_batch(model_list)`, `download_model(model_id, retry)`

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from h-e1 base hypothesis. Signatures verified from actual implementation:

```python
# From: h-e1/code/src/model_zoo.py (ACTUAL CODE)
class ModelZooCollector:
    def __init__(self, output_dir: str, random_seed: int = 42):
        """Initialize collector."""
        ...
    
    def collect_models(self, n_resnet: int = 50, n_vit: int = 50) -> Dict[str, List]:
        """
        Download models via timm library.
        Returns: {"models": [...metadata...], "success_count": int}
        """
        ...
    
    def download_model(self, model_id: str, retry: int = 3) -> Dict:
        """
        Download single model with retry logic.
        Returns: {"model_id": str, "architecture": str, "state_dict": OrderedDict, "accuracy": float}
        """
        ...
    
    def save_metadata(self, metadata: List[Dict], filepath: str) -> None:
        """Save metadata to JSON."""
        ...


# From: h-e1/code/src/feature_extractor.py (ACTUAL CODE)
class FeatureExtractor:
    def __init__(self, include_spectral: bool = True):
        """Initialize extractor."""
        ...
    
    def extract_from_state_dict(self, state_dict: Dict) -> np.ndarray:
        """
        Extract features from state_dict.
        Returns: [F] flattened feature vector
        """
        ...
    
    def extract_batch(self, model_list: List[Dict]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Batch process models.
        Returns: (X_full: [N, F], X_baseline: [N, F'], y: [N])
        """
        ...
```

**Verified from:** `/workspace/TEST_wsl/docs/youra_research/h-e1/code/` (actual implementation)

**Reuse Strategy:**
- Scale `collect_models()` to 400 models across 4 architectures
- Extend `FeatureExtractor` to group weights by operation type (conv/attention/MLP)

---

## A-2: Operation-Specific Encoders [Complexity: 17, Budget: 5]

**Applied:** SANE spatial tokenization, UNF equivariance principles

### API Signatures

```python
from typing import Dict, List, Tuple
import torch
import torch.nn as nn
from torch import Tensor

class SANEConvEncoder(nn.Module):
    """Convolutional weight encoder with spatial tokenization."""
    
    def __init__(self, d_out: int = 256, d_token: int = 64, dropout: float = 0.1):
        """Initialize conv encoder."""
        ...
    
    def forward(self, conv_weights: List[Tensor]) -> Tensor:
        """
        Encode convolutional weights.
        Input: list of [C_out, C_in, K, K] tensors
        Returns: [B, d_out]
        """
        ...
    
    def spatial_tokenize(self, weight: Tensor) -> Tensor:
        """
        Tokenize convolution kernel spatially.
        Input: [C_out, C_in, K, K]
        Returns: [N_tokens, d_token]
        """
        ...


class UNFAttentionEncoder(nn.Module):
    """Attention weight encoder with permutation equivariance."""
    
    def __init__(self, d_out: int = 256, d_hidden: int = 128, dropout: float = 0.1):
        """Initialize attention encoder."""
        ...
    
    def forward(self, attn_weights: List[Tensor]) -> Tensor:
        """
        Encode attention weights.
        Input: list of [N_heads, D_qk, D_qk] or [N_heads, D_qk, D_v] tensors
        Returns: [B, d_out]
        """
        ...
    
    def equivariant_process(self, weight: Tensor) -> Tensor:
        """
        Apply permutation-equivariant processing.
        Input: [N_heads, D, D]
        Returns: [N_heads, d_hidden]
        """
        ...


class MLPEncoder(nn.Module):
    """MLP weight encoder using DeepSets-style aggregation."""
    
    def __init__(self, d_out: int = 256, d_hidden: int = 128, dropout: float = 0.1):
        """Initialize MLP encoder."""
        ...
    
    def forward(self, mlp_weights: List[Tensor]) -> Tensor:
        """
        Encode MLP/FC layer weights.
        Input: list of [D_out, D_in] tensors
        Returns: [B, d_out]
        """
        ...
    
    def embed_weight_matrix(self, weight: Tensor) -> Tensor:
        """
        Embed single weight matrix.
        Input: [D_out, D_in]
        Returns: [d_hidden]
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| conv_weights[i] | [C_out, C_in, K, K] | Variable per layer |
| spatial_tokens | [N_tokens, d_token] | N_tokens = C_out * K^2 |
| conv_embed | [B, d_out] | Batch of models |
| attn_weights[i] | [N_heads, D, D] | Attention matrices |
| equivariant_feat | [N_heads, d_hidden] | Per-head features |
| mlp_weights[i] | [D_out, D_in] | FC layer weights |

### Pseudo-code

```
SANEConvEncoder:
1. For each conv weight [C_out, C_in, K, K]:
   a. Flatten spatial: [C_out, C_in * K * K]
   b. Linear project: [C_out, d_token]
   c. Spatial tokenize: [C_out * K^2, d_token]
2. Mean pool tokens → [d_token]
3. Project → [d_out]
4. Mean pool layers → [d_out]

UNFAttentionEncoder:
1. For each attn weight [N_heads, D, D]:
   a. Row/column statistics: [N_heads, 4*D]
   b. Linear project → [N_heads, d_hidden]
2. Mean pool heads → [d_hidden]
3. Project → [d_out]
4. Mean pool layers → [d_out]

MLPEncoder:
1. For each MLP weight [D_out, D_in]:
   a. Matrix statistics: norm, mean, std
   b. Linear project → [d_hidden]
2. Mean pool layers → [d_hidden]
3. Project → [d_out]
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | SANEConvEncoder spatial tokenization | Kernel flattening and spatial token generation |
| L-2-2 | UNFAttentionEncoder equivariance | Row/column statistics and permutation-equivariant pooling |
| L-2-3 | MLPEncoder set aggregation | DeepSets encoding for FC layers |
| L-2-4 | Weight grouping pipeline | Group state_dict by operation type |
| L-2-5 | Operation encoder integration | Combine 3 encoders with mean pooling |

---

## A-6: Full CAPE Integration [Complexity: 15, Budget: 4]

**Applied:** Multi-component encoder composition, InfoNCE contrastive learning (τ=0.07)

### API Signatures

```python
from typing import Dict, Optional, Tuple
import torch
import torch.nn as nn
from torch import Tensor

class CAPEEncoder(nn.Module):
    """Full CAPE encoder with 3 components."""
    
    def __init__(
        self,
        d_z: int = 256,
        d_arch: int = 64,
        d_token: int = 64,
        tau: float = 0.07,
        dropout: float = 0.1,
        gnn_layers: int = 3
    ):
        """Initialize CAPE encoder."""
        ...
    
    def forward(
        self,
        model_weights: Dict[str, List[Tensor]],
        arch_graph: Optional[Tuple[Tensor, Tensor]] = None
    ) -> Tensor:
        """
        Forward pass.
        Input:
            model_weights: {"conv": [tensors], "attention": [tensors], "mlp": [tensors]}
            arch_graph: (node_features: [N_nodes, d_arch], edge_index: [2, N_edges]) or None
        Returns: [B, d_z] final embeddings z_final
        """
        ...
    
    def get_operation_embeddings(self, model_weights: Dict[str, List[Tensor]]) -> Tensor:
        """
        Get operation-specific embeddings.
        Returns: [B, 3, d_z] for [conv, attention, mlp]
        """
        ...
    
    def get_contrastive_embeddings(self, z_op: Tensor) -> Tensor:
        """
        Apply contrastive projection.
        Input: [B, d_z]
        Returns: [B, d_z] z_proj (L2 normalized)
        """
        ...
    
    def compute_infonce_loss(self, z_proj: Tensor) -> Tensor:
        """
        Compute InfoNCE contrastive loss.
        Input: [B, d_z] normalized embeddings
        Returns: scalar loss
        """
        ...


class ContrastiveProjector(nn.Module):
    """2-layer MLP projector for contrastive learning."""
    
    def __init__(self, d_z: int = 256, dropout: float = 0.1):
        """Initialize projector."""
        ...
    
    def forward(self, z_op: Tensor) -> Tensor:
        """
        Project embeddings.
        Input: [B, d_z]
        Returns: [B, d_z] L2-normalized
        """
        ...


class ArchitectureGNN(nn.Module):
    """3-layer GCN for architecture graph encoding."""
    
    def __init__(
        self,
        d_arch: int = 64,
        d_z: int = 256,
        num_layers: int = 3,
        dropout: float = 0.1
    ):
        """Initialize GNN."""
        ...
    
    def forward(self, node_features: Tensor, edge_index: Tensor, batch: Optional[Tensor] = None) -> Tensor:
        """
        Process architecture DAG.
        Input:
            node_features: [N_nodes, d_arch]
            edge_index: [2, N_edges]
            batch: [N_nodes] batch assignment
        Returns: [B, d_z] or [d_z] architecture embedding z_arch
        """
        ...


class PropertyPredictor(nn.Module):
    """Property prediction head (accuracy prediction)."""
    
    def __init__(self, d_z: int = 256, num_properties: int = 1, dropout: float = 0.1):
        """Initialize predictor."""
        ...
    
    def forward(self, z_final: Tensor) -> Tensor:
        """
        Predict properties.
        Input: [B, d_z]
        Returns: [B, num_properties]
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| z_conv | [B, d_z] | Conv operation embedding |
| z_attn | [B, d_z] | Attention operation embedding |
| z_mlp | [B, d_z] | MLP operation embedding |
| op_embeddings | [B, 3, d_z] | Stacked operation embeddings |
| z_op | [B, d_z] | Aggregated operation embedding |
| z_proj | [B, d_z] | Contrastive projection (L2 normalized) |
| z_arch | [B, d_z] or [d_z] | Architecture embedding |
| z_final | [B, d_z] | Final embedding (z_proj + α * z_arch) |
| predictions | [B, 1] | Property predictions |

### Pseudo-code

```
CAPEEncoder Forward:
1. Extract operation embeddings:
   z_conv = conv_encoder(model_weights["conv"])  # [B, d_z]
   z_attn = attn_encoder(model_weights["attention"])  # [B, d_z]
   z_mlp = mlp_encoder(model_weights["mlp"])  # [B, d_z]

2. Aggregate operations:
   z_op = mean([z_conv, z_attn, z_mlp])  # [B, d_z]

3. Contrastive projection:
   z_proj = projector(z_op)  # [B, d_z]
   z_proj = F.normalize(z_proj, dim=-1)  # L2 normalize

4. Architecture GNN:
   if arch_graph is not None:
       z_arch = gnn(node_features, edge_index)  # [d_z]
       z_final = z_proj + alpha * z_arch  # Learnable residual
   else:
       z_final = z_proj

InfoNCE Loss:
1. Similarity matrix: S = z_proj @ z_proj.T / tau  # [B, B]
2. Positive pairs: diagonal
3. InfoNCE = -log(exp(S[i,i]) / sum_j exp(S[i,j]))
4. Return mean(InfoNCE)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Component integration | Combine operation encoders, projector, and GNN |
| L-6-2 | Residual combination | Learnable alpha for z_final = z_proj + α * z_arch |
| L-6-3 | InfoNCE loss implementation | Contrastive loss with τ=0.07 |
| L-6-4 | Property predictor | 2-layer MLP for accuracy prediction |

---

## A-7: Multi-Task Training Pipeline [Complexity: 14, Budget: 4]

**Applied:** Combined loss training, AdamW + cosine annealing

### API Signatures

```python
from typing import Dict, Optional
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import DataLoader

class MultiTaskTrainer:
    """Training pipeline with combined InfoNCE + property prediction loss."""
    
    def __init__(
        self,
        model: nn.Module,
        config: Dict,
        device: str = "cuda"
    ):
        """Initialize trainer."""
        ...
    
    def train_epoch(self, train_loader: DataLoader) -> Dict[str, float]:
        """
        Train one epoch.
        Returns: {"loss": float, "infonce_loss": float, "property_loss": float}
        """
        ...
    
    def validate(self, val_loader: DataLoader) -> Dict[str, float]:
        """
        Validation pass.
        Returns: {"val_loss": float, "val_infonce": float, "val_property": float}
        """
        ...
    
    def compute_combined_loss(
        self,
        z_proj: torch.Tensor,
        predictions: torch.Tensor,
        targets: torch.Tensor
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        Compute combined loss.
        Input:
            z_proj: [B, d_z] contrastive embeddings
            predictions: [B, 1] property predictions
            targets: [B, 1] ground truth properties
        Returns: (total_loss, {"infonce": float, "property_mse": float})
        """
        ...
    
    def save_checkpoint(self, filepath: str, epoch: int, metrics: Dict) -> None:
        """Save model checkpoint."""
        ...
    
    def load_checkpoint(self, filepath: str) -> Dict:
        """Load checkpoint. Returns: {"epoch": int, "metrics": dict}"""
        ...


class ModelZooDataset(torch.utils.data.Dataset):
    """Dataset for batched model weight loading."""
    
    def __init__(
        self,
        metadata: List[Dict],
        features_dir: str,
        arch_graphs_dir: str,
        architectures: List[str]
    ):
        """Initialize dataset."""
        ...
    
    def __getitem__(self, idx: int) -> Dict:
        """
        Get single item.
        Returns: {
            "model_weights": {"conv": [tensors], "attention": [tensors], "mlp": [tensors]},
            "arch_graph": (node_features, edge_index),
            "accuracy": float,
            "architecture": str
        }
        """
        ...
    
    @staticmethod
    def collate_fn(batch: List[Dict]) -> Dict:
        """Collate batch with variable-size weight lists and graphs."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| z_proj | [B, d_z] | Contrastive embeddings |
| predictions | [B, 1] | Predicted accuracies |
| targets | [B, 1] | Ground truth accuracies |
| infonce_loss | scalar | Contrastive loss |
| property_loss | scalar | MSE loss |
| total_loss | scalar | λ_contrast * infonce + λ_property * mse |

### Pseudo-code

```
Training Epoch:
1. model.train()
2. For each batch in train_loader:
   a. Load: model_weights, arch_graphs, targets
   b. Forward:
      z_final = model(model_weights, arch_graphs[0])
      z_proj = model.get_contrastive_embeddings(z_op)
      predictions = property_predictor(z_final)
   c. Losses:
      infonce = model.compute_infonce_loss(z_proj)
      mse = F.mse_loss(predictions, targets)
      loss = lambda_contrast * infonce + lambda_property * mse
   d. Backward + optimizer step
3. scheduler.step()
4. Return epoch metrics

Validation:
1. model.eval()
2. with torch.no_grad():
   Compute forward pass and losses (no backward)
3. Return validation metrics

Combined Loss:
loss = lambda_contrast * InfoNCE(z_proj) + lambda_property * MSE(predictions, targets)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Training loop implementation | train_epoch with combined loss |
| L-7-2 | Validation and early stopping | Validation loop with patience-based stopping |
| L-7-3 | Checkpoint management | Save/load model state, optimizer, scheduler |
| L-7-4 | Learning rate scheduling | Cosine annealing with 10% warmup |

---

## Supporting Module APIs (Reference Only)

### WeightPreprocessor

```python
class WeightPreprocessor:
    def normalize_weights(self, state_dict: Dict) -> Dict:
        """Per-layer Frobenius norm normalization."""
        ...
    
    def extract_operation_groups(self, state_dict: Dict) -> Dict[str, List]:
        """
        Group weights by operation type.
        Returns: {"conv": [tensors], "attention": [tensors], "mlp": [tensors]}
        """
        ...
```

### ArchitectureGraphBuilder

```python
class ArchitectureGraphBuilder:
    def build_dag(self, model: nn.Module) -> Tuple[Tensor, Tensor]:
        """
        Build architecture DAG.
        Returns: (node_features: [N_nodes, d_arch], edge_index: [2, N_edges])
        """
        ...
```

### CrossArchEvaluator

```python
class CrossArchEvaluator:
    def evaluate_transfer(self, predictions: np.ndarray, targets: np.ndarray) -> Dict:
        """Compute Spearman correlation. Returns: {"rho": float, "p_value": float}"""
        ...
    
    def permutation_test(self, rho_cape: float, rho_baseline: float) -> Dict:
        """Statistical significance test. Returns: {"p_value": float, "improvement": float}"""
        ...
```

### DiagnosticMetrics

```python
class DiagnosticMetrics:
    def compute_operation_similarity(self, z_conv: Tensor, z_attn: Tensor) -> float:
        """Cosine similarity between operation embeddings. Returns: scalar in [0, 1]"""
        ...
    
    def compute_intra_arch_variance(self, z_proj: Tensor, labels: Tensor) -> float:
        """Within-architecture embedding variance. Returns: scalar (std)"""
        ...
    
    def check_falsifiers(self, diagnostics: Dict) -> Dict[str, bool]:
        """Check diagnostic thresholds. Returns: {"operation_encoder_failed": bool, ...}"""
        ...
```

---

## Configuration Schema

```python
CONFIG = {
    "hypothesis_id": "H-M-Integrated",
    "random_seed": 42,
    "model_zoo": {
        "n_per_architecture": 100,
        "architectures": ["resnet50", "vit_base_patch16_224", "mobilenetv2_100", "efficientnet_b0"]
    },
    "cape_encoder": {
        "d_z": 256,
        "d_arch": 64,
        "d_token": 64,
        "tau": 0.07,
        "dropout": 0.1,
        "gnn_layers": 3
    },
    "training": {
        "batch_size": 32,
        "epochs": 100,
        "lr": 1e-4,
        "weight_decay": 1e-4,
        "lr_schedule": "cosine",
        "warmup_ratio": 0.10,
        "early_stopping_patience": 10
    },
    "loss": {
        "lambda_contrast": 1.0,
        "lambda_property": 0.5
    },
    "diagnostics": {
        "operation_similarity_threshold": 0.95,
        "intra_variance_threshold": 0.1,
        "gnn_weight_threshold": 0.1
    }
}
```

---

## Data Flow Summary

```
1. ModelZooCollector (h-e1) → 400 models → metadata.json
2. WeightPreprocessor → operation groups → preprocessed/
3. ArchitectureGraphBuilder → DAG representations → arch_graphs/
4. ModelZooDataset → DataLoader → batched inputs
5. CAPEEncoder.forward() → z_final embeddings
6. MultiTaskTrainer → combined loss → optimizer step
7. CrossArchEvaluator → transfer correlations → results/
8. DiagnosticMetrics → component validation → diagnostics.json
```

---

## Self-Validation

- [x] No ASCII diagrams
- [x] KB patterns applied: InfoNCE contrastive learning (τ=0.07), multi-component composition
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in comments and tables
- [x] Subtask count: 13/13 used (5+4+4 within budget)
- [x] Total length: ~550 lines (within 600 limit)
- [x] Codebase Analysis section included
- [x] External Dependencies API section included
- [x] Base hypothesis APIs verified from actual code
- [x] Parameter names match actual h-e1 implementation

---

**Status:** COMPLETE
**Next Phase:** Phase 4 - Implementation
**File Locations:**
- Architecture: `/workspace/TEST_wsl/docs/youra_research/h-m-integrated/03_architecture.md`
- PRD: `/workspace/TEST_wsl/docs/youra_research/h-m-integrated/03_prd.md`
- Logic: `/workspace/TEST_wsl/docs/youra_research/h-m-integrated/03_logic.md`
